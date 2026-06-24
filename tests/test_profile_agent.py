import pytest
from datetime import date
from pydantic import ValidationError
from backend.app.agents.profile_agent import StudentProfile

def get_valid_profile_data():
    return {
        "full_name": "Jane Doe",
        "date_of_birth": "2000-01-01",
        "nationality": "IN",
        "home_country": "India",
        "visa_type": "F-1",
        "enrollment_status": "full_time",
        "degree_level": "masters",
        "field_of_study": "Computer Science",
        "major": "AI",
        "university_name": "Stanford University",
        "university_state": "CA",
        "gpa": 3.8,
        "gpa_scale": 4.0,
        "expected_graduation_year": 2026,
        "published_research": True,
        "conference_presentations": 1,
        "patents": 0,
        "entrepreneurship_experience": False,
        "financial_need_level": "high",
        "languages": ["English", "Hindi"],
        "leadership_roles": ["President of CS Club"]
    }

def test_valid_profile():
    data = get_valid_profile_data()
    profile = StudentProfile(**data)
    assert profile.full_name == "Jane Doe"
    assert profile.gpa == 3.8

def test_empty_full_name():
    data = get_valid_profile_data()
    data["full_name"] = ""
    with pytest.raises(ValidationError):
        StudentProfile(**data)

def test_invalid_degree_level():
    data = get_valid_profile_data()
    data["degree_level"] = "high_school"
    with pytest.raises(ValidationError):
        StudentProfile(**data)

def test_negative_volunteer_hours():
    data = get_valid_profile_data()
    data["volunteer_hours"] = -5
    with pytest.raises(ValidationError):
        StudentProfile(**data)

def test_gpa_greater_than_scale():
    data = get_valid_profile_data()
    data["gpa"] = 4.2
    data["gpa_scale"] = 4.0
    with pytest.raises(ValidationError):
        StudentProfile(**data)

def test_to_feature_vector():
    data = get_valid_profile_data()
    profile = StudentProfile(**data)
    vector = profile.to_feature_vector()
    
    assert vector["nationality"] == "IN"
    assert vector["degree_level"] == "masters"
    assert vector["gpa"] == 3.8
    assert vector["has_leadership"] is True
    assert vector["published_research"] is True
    assert "financial_need_level" in vector

def test_completeness_score():
    data = get_valid_profile_data()
    profile = StudentProfile(**data)
    score = profile.completeness_score()
    
    assert 0 <= score <= 100
    
    data["gender"] = "Female"
    data["home_city"] = "Mumbai"
    data["family_income_bracket"] = "<30k"
    data["residence_country"] = "US"
    data["residence_city"] = "Stanford"
    data["university_city"] = "Stanford"
    data["university_country"] = "US"
    
    complete_profile = StudentProfile(**data)
    assert complete_profile.completeness_score() == 100.0

def test_list_defaults_not_shared():
    # Prove list defaults are not shared between instances
    data = get_valid_profile_data()
    profile_a = StudentProfile(**data)
    profile_b = StudentProfile(**data)
    
    profile_a.academic_awards.append("National Science Award")
    assert len(profile_a.academic_awards) == 1
    assert len(profile_b.academic_awards) == 0
