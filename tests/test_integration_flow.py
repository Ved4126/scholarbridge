from fastapi.testclient import TestClient
from backend.app.main import app
import pytest

client = TestClient(app)

def test_full_integration_flow():
    # 1. Create profile
    payload = {
        "full_name": "Integration Test User",
        "date_of_birth": "1998-05-15",
        "nationality": "NG",
        "home_country": "Nigeria",
        "visa_type": "F-1",
        "enrollment_status": "full_time",
        "degree_level": "phd",
        "field_of_study": "Engineering",
        "major": "Mechanical Engineering",
        "university_name": "MIT",
        "university_state": "MA",
        "gpa": 3.9,
        "gpa_scale": 4.0,
        "expected_graduation_year": 2028,
        "published_research": True,
        "conference_presentations": 2,
        "patents": 0,
        "entrepreneurship_experience": False,
        "financial_need_level": "medium"
    }
    create_res = client.post("/profile/", json=payload)
    assert create_res.status_code == 201, create_res.text
    profile_id = create_res.json()["profile_id"]

    # 2. Score all scholarships
    score_res = client.post("/score/all", json={"profile_id": profile_id})
    assert score_res.status_code == 200, score_res.text
    assert isinstance(score_res.json(), list)

    # 3. Retrieve cached score
    cached_res = client.get(f"/score/cached/{profile_id}")
    assert cached_res.status_code == 200, cached_res.text
    assert isinstance(cached_res.json(), list)

    # 4. Get profile completeness
    comp_res = client.get(f"/profile/{profile_id}/completeness")
    assert comp_res.status_code == 200, comp_res.text
    assert "completeness" in comp_res.json()

    # 5. Delete profile
    del_res = client.delete(f"/profile/{profile_id}")
    assert del_res.status_code == 200, del_res.text

    # 6. Confirm deleted profile returns 404
    get_res = client.get(f"/profile/{profile_id}")
    assert get_res.status_code == 404
    
    # 7. Check cached score is also deleted/inaccessible (not strictly required if cache persists, but PRD implies clean slate)
    cached_res_after = client.get(f"/score/cached/{profile_id}")
    assert cached_res_after.status_code == 404
