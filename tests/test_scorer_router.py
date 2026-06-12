"""
test_scorer_router.py — Integration tests for the Scorer API.

Tests:
  - POST /score/all with valid profile returns ranked results
  - Results include required fields: score, match_label, deadline, source_url,
    gap_analysis, action_checklist
  - POST /score/single with valid scholarship ID returns one result
  - POST /score/single with invalid scholarship ID returns 404
  - GET /score/cached/{profile_id} after scoring returns cached result
  - GET /score/cached/{profile_id} without cache returns 404
  - POST /score/all with unknown profile_id returns 404
  - POST /score/single with unknown profile_id returns 404

State is isolated per test via database.clear_all() and scorer_router.clear_cache().
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db import database
from backend.app.api import scorer_router as scorer_router_module

client = TestClient(app)

# ---------------------------------------------------------------------------
# Shared valid profile payload (same one used in profile router tests)
# ---------------------------------------------------------------------------
VALID_PROFILE = {
    "full_name": "Priya Sharma",
    "date_of_birth": "1998-03-15",
    "gender": "female",
    "nationality": "IN",
    "dual_citizenship": None,
    "home_country": "IN",
    "home_city": "Mumbai",
    "visa_type": "F-1",
    "enrollment_status": "full_time",
    "first_generation_student": True,
    "degree_level": "masters",
    "field_of_study": "Computer Science",
    "major": "Machine Learning",
    "minor": None,
    "university_name": "MIT",
    "university_state": "MA",
    "gpa": 3.8,
    "gpa_scale": 4.0,
    "gre": None,
    "gmat": None,
    "toefl": 110.0,
    "ielts": None,
    "sat": None,
    "act": None,
    "expected_graduation_year": 2026,
    "previous_degrees": None,
    "published_research": True,
    "research_papers": ["Neural Scaling Laws (2024)"],
    "conference_presentations": 1,
    "patents": 0,
    "academic_awards": ["Dean's List 2023"],
    "previous_scholarships": [],
    "leadership_roles": ["Graduate Student Council President"],
    "volunteer_hours": 120,
    "sports_achievements": [],
    "artistic_achievements": [],
    "entrepreneurship_experience": True,
    "financial_need_level": "medium",
    "family_income_bracket": "40k-80k",
    "current_funding_sources": ["TA stipend"],
    "dependents": 0,
    "career_goals": "AI research in healthcare",
    "intended_industry": "Healthcare AI",
    "willing_to_return_home_country": True,
    "languages": ["English", "Hindi"],
    "preferred_scholarship_types": ["merit-based"],
}

# The ID from the fixture scholarship JSON in data/scholarships/international/
FIXTURE_SCHOLARSHIP_ID = "test_scholarship"


@pytest.fixture(autouse=True)
def reset_state():
    """Clear the in-memory profile store and score cache before each test."""
    database.clear_all()
    scorer_router_module.clear_cache()
    yield
    database.clear_all()
    scorer_router_module.clear_cache()


def _create_profile() -> str:
    """Helper: create a profile and return its ID."""
    resp = client.post("/profile/", json=VALID_PROFILE)
    assert resp.status_code == 201
    return resp.json()["profile_id"]


# ---------------------------------------------------------------------------
# 1. POST /score/all — returns ranked results for a valid profile
# ---------------------------------------------------------------------------

def test_score_all_returns_list():
    """POST /score/all must return a list (may be empty if no scholarships qualify)."""
    profile_id = _create_profile()
    response = client.post("/score/all", json={"profile_id": profile_id})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# 2. Results include all required fields
# ---------------------------------------------------------------------------

def test_score_all_results_have_required_fields():
    """Each ScoringResult in /score/all must include all PRD-required fields."""
    profile_id = _create_profile()
    response = client.post("/score/all", json={"profile_id": profile_id})
    assert response.status_code == 200
    results = response.json()

    # The fixture scholarship should qualify (far-future deadline, open nationality)
    assert len(results) >= 1, "Expected at least the fixture scholarship to appear"

    for result in results:
        assert "scholarship_id" in result
        assert "name" in result
        assert "org_name" in result
        assert "score" in result
        assert "match_label" in result
        assert "deadline" in result
        assert "source_url" in result
        assert "gap_analysis" in result
        assert "action_checklist" in result


# ---------------------------------------------------------------------------
# 3. Results are sorted by score descending
# ---------------------------------------------------------------------------

def test_score_all_results_sorted_descending():
    """Scores in /score/all results must be in descending order."""
    profile_id = _create_profile()
    response = client.post("/score/all", json={"profile_id": profile_id})
    assert response.status_code == 200
    results = response.json()

    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# 4. Scores are all >= 40.0
# ---------------------------------------------------------------------------

def test_score_all_no_result_below_40():
    """No result in /score/all should have score < 40.0."""
    profile_id = _create_profile()
    response = client.post("/score/all", json={"profile_id": profile_id})
    assert response.status_code == 200
    for result in response.json():
        assert result["score"] >= 40.0


# ---------------------------------------------------------------------------
# 5. POST /score/single with a valid scholarship ID returns one result
# ---------------------------------------------------------------------------

def test_score_single_returns_one_result():
    """POST /score/single with a known scholarship_id must return a ScoringResult."""
    profile_id = _create_profile()
    response = client.post(
        "/score/single",
        json={"profile_id": profile_id, "scholarship_id": FIXTURE_SCHOLARSHIP_ID},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["scholarship_id"] == FIXTURE_SCHOLARSHIP_ID
    assert "score" in body
    assert "match_label" in body
    assert "gap_analysis" in body
    assert "action_checklist" in body


# ---------------------------------------------------------------------------
# 6. POST /score/single with an invalid scholarship ID returns 404
# ---------------------------------------------------------------------------

def test_score_single_invalid_scholarship_id_returns_404():
    """POST /score/single with an unknown scholarship_id must return 404."""
    profile_id = _create_profile()
    response = client.post(
        "/score/single",
        json={"profile_id": profile_id, "scholarship_id": "nonexistent-scholarship"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Scholarship not found"


# ---------------------------------------------------------------------------
# 7. GET /score/cached/{profile_id} after scoring returns cached result
# ---------------------------------------------------------------------------

def test_get_cached_score_returns_previous_result():
    """GET /score/cached/{id} after POST /score/all must return the cached list."""
    profile_id = _create_profile()
    # Run score/all to populate the cache
    client.post("/score/all", json={"profile_id": profile_id})

    cached_resp = client.get(f"/score/cached/{profile_id}")
    assert cached_resp.status_code == 200
    cached = cached_resp.json()
    assert isinstance(cached, list)


# ---------------------------------------------------------------------------
# 8. GET /score/cached/{profile_id} without prior scoring returns 404
# ---------------------------------------------------------------------------

def test_get_cached_score_without_prior_scoring_returns_404():
    """GET /score/cached/{id} with no prior /score/all call must return 404."""
    profile_id = _create_profile()
    response = client.get(f"/score/cached/{profile_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Cached score not found"


# ---------------------------------------------------------------------------
# 9. POST /score/all with unknown profile_id returns 404
# ---------------------------------------------------------------------------

def test_score_all_unknown_profile_id_returns_404():
    """POST /score/all with an unknown profile_id must return 404."""
    response = client.post("/score/all", json={"profile_id": "unknown-id-xyz"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


# ---------------------------------------------------------------------------
# 10. POST /score/single with unknown profile_id returns 404
# ---------------------------------------------------------------------------

def test_score_single_unknown_profile_id_returns_404():
    """POST /score/single with an unknown profile_id must return 404."""
    response = client.post(
        "/score/single",
        json={"profile_id": "unknown-profile", "scholarship_id": FIXTURE_SCHOLARSHIP_ID},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"
