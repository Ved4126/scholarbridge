"""
test_profile_router.py — Integration tests for the Profile API.

Tests:
  - POST /profile   creates a profile and returns a profile_id
  - GET  /profile/{id}    returns the full profile
  - GET  /profile/{bad-id} returns 404
  - PATCH /profile/{id}  updates selected fields
  - DELETE /profile/{id}  removes the profile
  - GET  /profile/{deleted-id}  returns 404
  - GET  /profile/{id}/completeness  returns completeness score
  - GET  /health  returns status ok

State is isolated per test via database.clear_all() in setup/teardown.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db import database

client = TestClient(app)

# ---------------------------------------------------------------------------
# A complete, valid StudentProfile payload for all tests.
# ---------------------------------------------------------------------------
VALID_PROFILE = {
    "full_name": "Priya Sharma",
    "date_of_birth": "1998-03-15",
    "gender": "female",
    "nationality": "IN",
    "home_country": "IN",
    "home_city": "Mumbai",
    "residence_country": "US",
    "residence_state": "MA",
    "residence_city": "Cambridge",
    "visa_type": "F-1",
    "enrollment_status": "full_time",
    "first_generation_student": True,
    "degree_level": "masters",
    "field_of_study": "Computer Science",
    "major": "Computer Science",
    "minor": None,
    "university_name": "MIT",
    "university_city": "Cambridge",
    "university_state": "MA",
    "university_country": "US",
    "gpa": 3.8,
    "gpa_scale": 4.0,
    "gre": None,
    "gmat": None,
    "toefl": 110.0,
    "ielts": None,
    "sat": None,
    "act": None,
    "expected_graduation_year": 2026,
    "published_research": True,
    "research_papers": ["Neural Scaling Laws (2024)"],
    "citations_count": 10,
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
}


@pytest.fixture(autouse=True)
def reset_db():
    """Clear the in-memory profile store before and after every test."""
    database.clear_all()
    yield
    database.clear_all()


# ---------------------------------------------------------------------------
# 1. POST /profile — creates a profile and returns a profile_id
# ---------------------------------------------------------------------------

def test_create_profile_returns_profile_id():
    """POST /profile must return HTTP 201 with a non-empty profile_id."""
    response = client.post("/profile/", json=VALID_PROFILE)
    assert response.status_code == 201
    body = response.json()
    assert "profile_id" in body
    assert len(body["profile_id"]) > 0
    assert "completeness" in body
    assert body["message"] == "Profile created successfully"


# ---------------------------------------------------------------------------
# 2. GET /profile/{id} — returns the full profile
# ---------------------------------------------------------------------------

def test_get_profile_returns_full_profile():
    """GET /profile/{id} must return the profile that was just created."""
    create_resp = client.post("/profile/", json=VALID_PROFILE)
    profile_id = create_resp.json()["profile_id"]

    get_resp = client.get(f"/profile/{profile_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["full_name"] == "Priya Sharma"
    assert body["nationality"] == "IN"
    assert body["degree_level"] == "masters"


# ---------------------------------------------------------------------------
# 3. GET /profile/{bad-id} — returns 404
# ---------------------------------------------------------------------------

def test_get_nonexistent_profile_returns_404():
    """GET for an unknown profile_id must return 404 with the correct detail."""
    response = client.get("/profile/does-not-exist-0000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


# ---------------------------------------------------------------------------
# 4. PATCH /profile/{id} — updates selected fields
# ---------------------------------------------------------------------------

def test_patch_profile_updates_selected_fields():
    """PATCH /profile/{id} with a partial payload must update only those fields."""
    create_resp = client.post("/profile/", json=VALID_PROFILE)
    profile_id = create_resp.json()["profile_id"]

    patch_resp = client.patch(
        f"/profile/{profile_id}",
        json={"gpa": 3.9, "home_city": "Pune"},
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["gpa"] == 3.9
    assert body["home_city"] == "Pune"
    # Other fields must not change
    assert body["full_name"] == "Priya Sharma"


# ---------------------------------------------------------------------------
# 5. DELETE /profile/{id} — removes the profile
# ---------------------------------------------------------------------------

def test_delete_profile_returns_success():
    """DELETE /profile/{id} must return 200 with a success message."""
    create_resp = client.post("/profile/", json=VALID_PROFILE)
    profile_id = create_resp.json()["profile_id"]

    del_resp = client.delete(f"/profile/{profile_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Profile deleted"


# ---------------------------------------------------------------------------
# 6. GET /profile/{deleted-id} — returns 404 after delete
# ---------------------------------------------------------------------------

def test_get_deleted_profile_returns_404():
    """After deletion, GET on the same profile_id must return 404."""
    create_resp = client.post("/profile/", json=VALID_PROFILE)
    profile_id = create_resp.json()["profile_id"]

    client.delete(f"/profile/{profile_id}")
    get_resp = client.get(f"/profile/{profile_id}")
    assert get_resp.status_code == 404
    assert get_resp.json()["detail"] == "Profile not found"


# ---------------------------------------------------------------------------
# 7. GET /profile/{id}/completeness — returns completeness score
# ---------------------------------------------------------------------------

def test_completeness_endpoint_returns_score():
    """GET /profile/{id}/completeness must return a numeric completeness value."""
    create_resp = client.post("/profile/", json=VALID_PROFILE)
    profile_id = create_resp.json()["profile_id"]

    comp_resp = client.get(f"/profile/{profile_id}/completeness")
    assert comp_resp.status_code == 200
    body = comp_resp.json()
    assert body["profile_id"] == profile_id
    assert isinstance(body["completeness"], float)
    assert 0.0 <= body["completeness"] <= 100.0


def test_completeness_endpoint_404_for_missing_profile():
    """GET /profile/{id}/completeness on unknown id must return 404."""
    response = client.get("/profile/nonexistent-id/completeness")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


# ---------------------------------------------------------------------------
# 8. GET /health — health endpoint still works after router registration
# ---------------------------------------------------------------------------

def test_health_endpoint_returns_ok():
    """GET /health must return status=ok and version=0.1.0."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
