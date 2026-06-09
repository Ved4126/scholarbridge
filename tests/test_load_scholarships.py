import os
import json
import pytest
from pathlib import Path
from scripts.load_scholarships import load_scholarships

@pytest.fixture
def temp_data_dir(tmp_path):
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"type": "object"}')
    return tmp_path

def create_mock_scholarship(path: Path, filename: str, overrides: dict = None) -> None:
    data = {
        "id": "test_id",
        "scholarship_name": "Test Scholarship",
        "org_name": "Test Org",
        "source_url": "https://example.com",
        "country": "US",
        "source_type": "university",
        "award_amount": 1000,
        "currency": "USD",
        "deadline": "2026-12-31",
        "award_year": 2026,
        "degree_levels": ["undergrad"],
        "eligible_nationalities": ["US"],
        "eligible_visa_types": ["any"],
        "fields_of_study": ["any"],
        "description": "Test",
        "eligibility_text": "Test",
        "feature_manifest": {
            "total_features": 1,
            "features": [
                {
                    "id": "test_feature",
                    "label": "Test Label",
                    "type": "boolean",
                    "required": True,
                    "student_field": "test_bool"
                }
            ]
        },
        "last_verified": "2026-06-09T00:00:00Z",
        "created_at": "2026-06-09T00:00:00Z",
        "updated_at": "2026-06-09T00:00:00Z"
    }
    if overrides:
        data.update(overrides)
        
    file_path = path / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def test_load_scholarships_valid(temp_data_dir):
    us_dir = temp_data_dir / "us"
    us_dir.mkdir()
    create_mock_scholarship(us_dir, "test1.json")
    
    loaded = load_scholarships(str(temp_data_dir))
    assert len(loaded) == 1
    assert loaded[0]["id"] == "test_id"

def test_missing_required_field_raises_error(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "test_missing.json")
    
    file_path = temp_data_dir / "test_missing.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    del data["org_name"]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    with pytest.raises(ValueError, match="Missing required fields"):
        load_scholarships(str(temp_data_dir))

def test_missing_total_features(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "bad1.json", {
        "feature_manifest": {"features": []}
    })
    with pytest.raises(ValueError, match="Missing 'total_features'"):
        load_scholarships(str(temp_data_dir))

def test_missing_features(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "bad2.json", {
        "feature_manifest": {"total_features": 0}
    })
    with pytest.raises(ValueError, match="Missing 'features'"):
        load_scholarships(str(temp_data_dir))

def test_features_not_a_list(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "bad3.json", {
        "feature_manifest": {"total_features": 1, "features": {}}
    })
    with pytest.raises(ValueError, match="'features' must be a list"):
        load_scholarships(str(temp_data_dir))

def test_feature_missing_required_field(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "bad4.json", {
        "feature_manifest": {
            "total_features": 1,
            "features": [
                {"id": "only_id"}
            ]
        }
    })
    with pytest.raises(ValueError, match="Feature missing"):
        load_scholarships(str(temp_data_dir))

def test_invalid_feature_type(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "bad5.json", {
        "feature_manifest": {
            "total_features": 1,
            "features": [
                {"id": "1", "label": "L", "type": "unknown_type", "required": True}
            ]
        }
    })
    with pytest.raises(ValueError, match="Invalid feature type"):
        load_scholarships(str(temp_data_dir))

def test_score_test_feature_raises_error(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "bad6.json", {
        "feature_manifest": {
            "total_features": 1,
            "features": [
                {"id": "2", "label": "S", "type": "score_test", "required": False}
            ]
        }
    })
    with pytest.raises(ValueError, match="Found forbidden feature type 'score_test'"):
        load_scholarships(str(temp_data_dir))

def test_total_features_mismatch(temp_data_dir):
    create_mock_scholarship(temp_data_dir, "bad7.json", {
        "feature_manifest": {
            "total_features": 5,
            "features": [
                {"id": "1", "label": "L", "type": "boolean", "student_field": "x", "required": True}
            ]
        }
    })
    with pytest.raises(ValueError, match="'total_features' does not match"):
        load_scholarships(str(temp_data_dir))

def test_recursive_loading(temp_data_dir):
    dir1 = temp_data_dir / "us"
    dir1.mkdir()
    dir2 = temp_data_dir / "india"
    dir2.mkdir()
    
    create_mock_scholarship(dir1, "test1.json")
    create_mock_scholarship(dir2, "test2.json")
    
    loaded = load_scholarships(str(temp_data_dir))
    assert len(loaded) == 2
