import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from backend.app.main import app
from scripts.load_scholarships import load_scholarships
from backend.app.scorer.scorer import score_all
from backend.app.db.database import clear_all

client = TestClient(app)

def test_empty_scholarship_dataset():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Load from empty directory
        scholarships = load_scholarships(temp_dir)
        assert len(scholarships) == 0
        
        # Scoring with empty catalogue should return empty list
        vector = {"nationality": "IN", "gpa": 3.8, "degree_level": "masters"}
        # Ensure score_all handles empty list cleanly
        results = score_all(vector, scholarships)
        assert results == []

def test_invalid_scholarship_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "invalid.json")
        with open(file_path, "w") as f:
            f.write('{"name": "Missing Required Fields"}')
        
        with pytest.raises(ValueError) as excinfo:
            load_scholarships(temp_dir)
        
        assert "Missing required fields" in str(excinfo.value)

def test_scoring_profile_no_cached_result():
    # If a profile hasn't been scored, /score/cached/{id} returns 404
    # First create profile
    payload = {
        "full_name": "No Cache User",
        "date_of_birth": "2000-01-01",
        "nationality": "US",
        "home_country": "USA",
        "visa_type": "F-1",
        "enrollment_status": "full_time",
        "degree_level": "undergrad",
        "field_of_study": "Art",
        "major": "Fine Arts",
        "university_name": "NYU",
        "university_state": "NY",
        "gpa": 3.0,
        "gpa_scale": 4.0,
        "expected_graduation_year": 2026,
        "published_research": False,
        "conference_presentations": 0,
        "patents": 0,
        "entrepreneurship_experience": False,
        "financial_need_level": "low"
    }
    create_res = client.post("/profile/", json=payload)
    assert create_res.status_code == 201
    profile_id = create_res.json()["profile_id"]

    # Try retrieving cached score
    cache_res = client.get(f"/score/cached/{profile_id}")
    assert cache_res.status_code == 404
    assert "not found" in cache_res.json()["detail"].lower()

def test_invalid_profile_payload():
    # Submit profile missing required fields
    payload = {"full_name": "Incomplete User"}
    res = client.post("/profile/", json=payload)
    assert res.status_code == 422
    assert "detail" in res.json()
