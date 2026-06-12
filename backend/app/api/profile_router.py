"""
profile_router.py — Profile API endpoints.

Endpoints:
  POST   /profile                         — create profile
  GET    /profile/{profile_id}            — get profile
  PATCH  /profile/{profile_id}            — update profile fields
  DELETE /profile/{profile_id}            — delete profile
  GET    /profile/{profile_id}/completeness — return completeness score

No business logic lives here. All logic is delegated to profile_agent.py
and database.py per AI_RULES.md § 6.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from backend.app.agents.profile_agent import StudentProfile
from backend.app.db import database

router = APIRouter(prefix="/profile", tags=["profile"])


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class CreateProfileResponse(BaseModel):
    """Response body for POST /profile."""
    profile_id: str
    completeness: float
    message: str


class CompletenessResponse(BaseModel):
    """Response body for GET /profile/{profile_id}/completeness."""
    profile_id: str
    completeness: float


class DeleteResponse(BaseModel):
    """Response body for DELETE /profile/{profile_id}."""
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/", response_model=CreateProfileResponse, status_code=201)
def create_profile(profile: StudentProfile) -> CreateProfileResponse:
    """Create and store a new student profile.

    Args:
        profile: Validated StudentProfile from request body.

    Returns:
        profile_id, completeness score, and a success message.
    """
    profile_id = database.save_profile(profile)
    return CreateProfileResponse(
        profile_id=profile_id,
        completeness=profile.completeness_score(),
        message="Profile created successfully",
    )


@router.get("/{profile_id}", response_model=StudentProfile)
def get_profile(profile_id: str) -> StudentProfile:
    """Retrieve a stored profile by its ID.

    Args:
        profile_id: UUID assigned at creation.

    Returns:
        The full StudentProfile.

    Raises:
        HTTPException 404 if the profile does not exist.
    """
    profile = database.get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=StudentProfile)
def update_profile(profile_id: str, updates: dict[str, Any]) -> StudentProfile:
    """Apply a partial update to a stored profile.

    Only the provided fields are changed. Pydantic re-validates the result.

    Args:
        profile_id: UUID of the profile to update.
        updates: Partial field dict from request body.

    Returns:
        The updated StudentProfile.

    Raises:
        HTTPException 404 if the profile does not exist.
        HTTPException 422 if the updated values fail validation.
    """
    existing = database.get_profile(profile_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    try:
        updated = database.update_profile(profile_id, updates)
    except (ValueError, ValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated


@router.delete("/{profile_id}", response_model=DeleteResponse)
def delete_profile(profile_id: str) -> DeleteResponse:
    """Delete a stored profile.

    Args:
        profile_id: UUID of the profile to delete.

    Returns:
        Success message.

    Raises:
        HTTPException 404 if the profile does not exist.
    """
    deleted = database.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
    return DeleteResponse(message="Profile deleted")


@router.get("/{profile_id}/completeness", response_model=CompletenessResponse)
def get_completeness(profile_id: str) -> CompletenessResponse:
    """Return the completeness score for a stored profile.

    Args:
        profile_id: UUID of the profile.

    Returns:
        profile_id and completeness percentage (0.0–100.0).

    Raises:
        HTTPException 404 if the profile does not exist.
    """
    profile = database.get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return CompletenessResponse(
        profile_id=profile_id,
        completeness=profile.completeness_score(),
    )
