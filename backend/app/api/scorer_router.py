"""
scorer_router.py — Scoring API endpoints.

Endpoints:
  POST /score/all                       — score all scholarships for a profile
  POST /score/single                    — score one scholarship by ID for a profile
  GET  /score/cached/{profile_id}       — return last cached scoring result

No business logic lives here. Scoring is delegated to scorer.py.
Scholarship loading is delegated to load_scholarships.py.
Cache is an MVP in-memory dict keyed by profile_id.

Per AI_RULES.md § 6: routes must not contain business logic.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.scorer.models import ScholarshipRecord, ScoringResult
from backend.app.scorer.scorer import score_all, score_one
from backend.app.db import database
from scripts.load_scholarships import load_scholarships

router = APIRouter(prefix="/score", tags=["scorer"])

# ---------------------------------------------------------------------------
# MVP in-memory scoring cache  {profile_id -> list[ScoringResult]}
# ---------------------------------------------------------------------------
_score_cache: dict[str, list[ScoringResult]] = {}


# ---------------------------------------------------------------------------
# Lazy-loaded scholarship catalogue
# ---------------------------------------------------------------------------

def _load_catalogue() -> list[ScholarshipRecord]:
    """Load all scholarship JSON files and return as ScholarshipRecord objects.

    Uses the same loader used in Phase 3. Path is resolved relative to this
    file so it works regardless of the working directory.
    """
    data_dir = Path(__file__).parents[3] / "data" / "scholarships"
    raw_list: list[dict[str, Any]] = load_scholarships(str(data_dir))
    return [ScholarshipRecord(**raw) for raw in raw_list]


def _find_scholarship(scholarship_id: str, catalogue: list[ScholarshipRecord]) -> ScholarshipRecord | None:
    """Return the first scholarship whose id matches, or None."""
    for s in catalogue:
        if s.id == scholarship_id:
            return s
    return None


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ScoreAllRequest(BaseModel):
    """Request body for POST /score/all."""
    profile_id: str


class ScoreSingleRequest(BaseModel):
    """Request body for POST /score/single."""
    profile_id: str
    scholarship_id: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/all", response_model=list[ScoringResult])
def score_all_endpoint(request: ScoreAllRequest) -> list[ScoringResult]:
    """Score all scholarships for a given student profile.

    1. Look up the stored profile.
    2. Load the full scholarship catalogue.
    3. Run hard pre-filters + M/T scoring via score_all().
    4. Cache and return the ranked results.

    Args:
        request: Contains profile_id.

    Returns:
        Sorted list of ScoringResult objects (score >= 40.0, max 20).

    Raises:
        HTTPException 404 if the profile is not found.
    """
    profile = database.get_profile(request.profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    catalogue = _load_catalogue()
    profile_vector = profile.to_feature_vector()
    results = score_all(profile_vector, catalogue)

    _score_cache[request.profile_id] = results
    return results


@router.post("/single", response_model=ScoringResult)
def score_single_endpoint(request: ScoreSingleRequest) -> ScoringResult:
    """Score one specific scholarship for a given student profile.

    Does NOT apply hard pre-filters — returns the raw M/T score for
    the requested scholarship regardless of deadline/citizenship/etc.

    Args:
        request: Contains profile_id and scholarship_id.

    Returns:
        A single ScoringResult.

    Raises:
        HTTPException 404 if the profile or scholarship is not found.
    """
    profile = database.get_profile(request.profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    catalogue = _load_catalogue()
    scholarship = _find_scholarship(request.scholarship_id, catalogue)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    profile_vector = profile.to_feature_vector()
    result = score_one(profile_vector, scholarship)
    return result


@router.get("/cached/{profile_id}", response_model=list[ScoringResult])
def get_cached_score(profile_id: str) -> list[ScoringResult]:
    """Return the last cached scoring result for a profile.

    The cache is populated when POST /score/all is called.

    Args:
        profile_id: UUID of the profile.

    Returns:
        The previously cached list of ScoringResult objects.

    Raises:
        HTTPException 404 if no cached result exists for this profile.
    """
    cached = _score_cache.get(profile_id)
    if cached is None:
        raise HTTPException(status_code=404, detail="Cached score not found")
    return cached


def clear_cache() -> None:
    """Remove all cached scores.

    Used only by tests to reset state between test runs.
    """
    _score_cache.clear()
