import pytest
from datetime import date
from backend.app.agents.profile_agent import StudentProfile
from backend.app.scorer.models import ScholarshipRecord
from backend.app.scorer.scorer import score_all
from backend.app.api.scorer_router import _load_catalogue

# ---------------------------------------------------------------------------
# Test Profiles setup helper
# ---------------------------------------------------------------------------

def get_base_profile_data():
    return {
        "full_name": "Test Student",
        "date_of_birth": "2000-01-01",
        "gender": "other",
        "nationality": "Any",
        "home_country": "AnyCountry",
        "home_city": "AnyCity",
        "residence_country": "US",
        "residence_state": "CA",
        "residence_city": "Stanford",
        "visa_type": "F-1",
        "enrollment_status": "full_time",
        "first_generation_student": False,
        "degree_level": "masters",
        "field_of_study": "Computer Science",
        "major": "Computer Science",
        "minor": None,
        "university_name": "Stanford University",
        "university_city": "Stanford",
        "university_state": "CA",
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
        "research_papers": ["Test Paper"],
        "citations_count": 10,
        "conference_presentations": 1,
        "patents": 0,
        "academic_awards": [],
        "previous_scholarships": [],
        "leadership_roles": [],
        "volunteer_hours": 0,
        "sports_achievements": [],
        "artistic_achievements": [],
        "entrepreneurship_experience": True,
        "financial_need_level": "medium",
        "family_income_bracket": "medium",
        "current_funding_sources": [],
        "dependents": 0
    }

# 1. Indian F-1 master’s student in Computer Science with strong GPA
def get_indian_f1_cs_masters():
    data = get_base_profile_data()
    data.update({
        "full_name": "Priya Sharma",
        "nationality": "IN",
        "home_country": "India",
        "home_city": "Mumbai",
        "gender": "female",
        "gpa": 3.9,
        "toefl": 112.0
    })
    return StudentProfile(**data)

# 2. International undergraduate student with financial need
def get_undergrad_french_f1():
    data = get_base_profile_data()
    data.update({
        "full_name": "Jean-Luc",
        "nationality": "FR",
        "home_country": "France",
        "home_city": "Paris",
        "degree_level": "undergrad",
        "gpa": 3.7,
        "financial_need_level": "high",
        "published_research": False,
        "research_papers": None,
        "citations_count": None
    })
    return StudentProfile(**data)

# 3. Woman graduate student eligible for women-focused fellowships
def get_woman_grad_kenya_f1():
    data = get_base_profile_data()
    data.update({
        "full_name": "Sarah",
        "nationality": "KE",
        "home_country": "Kenya",
        "home_city": "Nairobi",
        "gender": "female",
        "degree_level": "masters",
        "gpa": 3.8
    })
    return StudentProfile(**data)

# 4. PhD/postdoc research-focused student
def get_phd_sociology_egypt_j1():
    data = get_base_profile_data()
    data.update({
        "full_name": "Fatima",
        "nationality": "EG",
        "home_country": "Egypt",
        "home_city": "Cairo",
        "visa_type": "J-1",
        "gender": "female",
        "degree_level": "phd",
        "field_of_study": "Sociology",
        "major": "Sociology",
        "gpa": 3.95,
        "published_research": True,
        "research_papers": ["Gender dynamics in developing economies"],
        "citations_count": 25
    })
    return StudentProfile(**data)

# 5. Low-match / Ineligible profile (US Citizen, part-time/non-matching degree or major)
def get_ineligible_us_citizen():
    data = get_base_profile_data()
    data.update({
        "full_name": "John Smith",
        "nationality": "US",
        "home_country": "United States",
        "visa_type": "US_CITIZEN",
        "enrollment_status": "part_time",
        "gpa": 2.2
    })
    return StudentProfile(**data)


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

def test_catalogue_loads_real_scholarships():
    catalogue = _load_catalogue()
    ids = [s.id for s in catalogue]
    assert "fulbright_foreign_student" in ids
    assert "aauw_international_fellowships" in ids
    assert "mpower_global_citizen" in ids
    assert "clark_university_presidents" in ids
    assert "campbell_fellowship_sar" in ids

def test_matching_indian_f1_cs_masters():
    profile = get_indian_f1_cs_masters()
    catalogue = _load_catalogue()
    results = score_all(profile.to_feature_vector(), catalogue)
    
    matched_ids = [r.scholarship_id for r in results]
    
    # Priya Sharma is F-1, so she should be excluded from Fulbright (requires J-1)
    assert "fulbright_foreign_student" not in matched_ids
    
    # Should match AAUW (female) and MPOWER
    assert "aauw_international_fellowships" in matched_ids
    assert "mpower_global_citizen" in matched_ids
    
    # Check that MPOWER has correct action checklist populated from outputs
    mpower_res = next(r for r in results if r.scholarship_id == "mpower_global_citizen")
    assert "Essay answering program prompts" in mpower_res.action_checklist
    assert "Proof of Enrollment or Acceptance Letter" in mpower_res.action_checklist

def test_matching_undergrad_french_f1():
    profile = get_undergrad_french_f1()
    catalogue = _load_catalogue()
    results = score_all(profile.to_feature_vector(), catalogue)
    
    matched_ids = [r.scholarship_id for r in results]
    assert "clark_university_presidents" in matched_ids
    assert "mpower_global_citizen" in matched_ids
    
    # Graduate ones must be excluded
    assert "fulbright_foreign_student" not in matched_ids
    assert "aauw_international_fellowships" not in matched_ids

def test_matching_woman_grad_kenya_f1():
    profile = get_woman_grad_kenya_f1()
    catalogue = _load_catalogue()
    results = score_all(profile.to_feature_vector(), catalogue)
    
    matched_ids = [r.scholarship_id for r in results]
    assert "aauw_international_fellowships" in matched_ids
    assert "mpower_global_citizen" in matched_ids

def test_matching_phd_sociology_egypt_j1():
    profile = get_phd_sociology_egypt_j1()
    catalogue = _load_catalogue()
    results = score_all(profile.to_feature_vector(), catalogue)
    
    matched_ids = [r.scholarship_id for r in results]
    # Campbell fellowship requires PhD/Postdoc + Social Science (Sociology is mapped) + Female + Published Research
    assert "campbell_fellowship_sar" in matched_ids
    # Fulbright is J-1 and Egypt/any is allowed
    assert "fulbright_foreign_student" in matched_ids
    assert "aauw_international_fellowships" in matched_ids

def test_matching_ineligible_us_citizen():
    profile = get_ineligible_us_citizen()
    catalogue = _load_catalogue()
    results = score_all(profile.to_feature_vector(), catalogue)
    
    matched_ids = [r.scholarship_id for r in results]
    # US citizens or part-time are filtered out of all our seeded international scholarships
    # Let's verify that none of the real ones match
    real_ids = {"fulbright_foreign_student", "aauw_international_fellowships", "mpower_global_citizen", "clark_university_presidents", "campbell_fellowship_sar"}
    assert not any(rid in matched_ids for rid in real_ids)
