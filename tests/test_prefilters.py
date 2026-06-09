from __future__ import annotations
from datetime import date
import pytest
from backend.app.scorer.prefilters import apply_prefilters, PreFilterResult
from backend.app.scorer.models import ScholarshipRecord, FeatureManifest

# Reference evaluation date: 2026-06-09
EVAL_DATE = date(2026, 6, 9)

def make_test_scholarship(
    deadline: str | None = "2026-06-25",
    eligible_nationalities: list[str] | None = None,
    degree_levels: list[str] | None = None,
    eligible_visa_types: list[str] | None = None
) -> ScholarshipRecord:
    return ScholarshipRecord(
        id="test-id",
        scholarship_name="Test Scholarship",
        org_name="Test Org",
        source_url="https://example.com",
        country="US",
        source_type="private",
        deadline=deadline,
        degree_levels=degree_levels or [],
        eligible_nationalities=eligible_nationalities or [],
        eligible_visa_types=eligible_visa_types or [],
        description="Test description",
        eligibility_text="Test eligibility text",
        feature_manifest=FeatureManifest(total_features=0, features=[]),
        last_verified="2026-06-09",
        created_at="2026-06-09",
        updated_at="2026-06-09"
    )

# --- DEADLINE FILTER TESTS ---

def test_deadline_future_passes():
    # 16 days in future
    scholarship = make_test_scholarship(deadline="2026-06-25")
    res = apply_prefilters({"nationality": "IN"}, scholarship, EVAL_DATE)
    assert res.passed is True
    assert "deadline" not in res.failed_filters

def test_deadline_expired_fails():
    # Yesterday
    scholarship = make_test_scholarship(deadline="2026-06-08")
    res = apply_prefilters({"nationality": "IN"}, scholarship, EVAL_DATE)
    assert res.passed is False
    assert "deadline" in res.failed_filters
    assert len(res.reasons) == 1
    assert "has expired" in res.reasons[0]

def test_deadline_within_14_days_fails():
    # 5 days in future
    scholarship = make_test_scholarship(deadline="2026-06-14")
    res = apply_prefilters({"nationality": "IN"}, scholarship, EVAL_DATE)
    assert res.passed is False
    assert "deadline" in res.failed_filters
    assert len(res.reasons) == 1
    assert "within 14 days" in res.reasons[0]

def test_deadline_missing_fails():
    # Missing / None
    scholarship1 = make_test_scholarship(deadline=None)
    res1 = apply_prefilters({"nationality": "IN"}, scholarship1, EVAL_DATE)
    assert res1.passed is False
    assert "deadline" in res1.failed_filters
    assert "missing" in res1.reasons[0]

    # Empty string
    scholarship2 = make_test_scholarship(deadline=" ")
    res2 = apply_prefilters({"nationality": "IN"}, scholarship2, EVAL_DATE)
    assert res2.passed is False
    assert "deadline" in res2.failed_filters
    assert "missing" in res2.reasons[0]

# --- CITIZENSHIP FILTER TESTS ---

def test_citizenship_eligible_passes():
    scholarship = make_test_scholarship(eligible_nationalities=["IN", "PK"])
    
    # Matching first
    res1 = apply_prefilters({"nationality": "IN"}, scholarship, EVAL_DATE)
    assert res1.passed is True

    # Matching second, case-insensitive
    res2 = apply_prefilters({"nationality": "pk"}, scholarship, EVAL_DATE)
    assert res2.passed is True

    # Matching dual citizenship
    res3 = apply_prefilters({"nationality": "US", "dual_citizenship": "IN"}, scholarship, EVAL_DATE)
    assert res3.passed is True

def test_citizenship_ineligible_fails():
    scholarship = make_test_scholarship(eligible_nationalities=["IN", "PK"])
    res = apply_prefilters({"nationality": "US"}, scholarship, EVAL_DATE)
    assert res.passed is False
    assert "citizenship" in res.failed_filters
    assert "nationality" in res.reasons[0]

def test_citizenship_any_passes():
    scholarship = make_test_scholarship(eligible_nationalities=["Any"])
    res = apply_prefilters({"nationality": "US"}, scholarship, EVAL_DATE)
    assert res.passed is True

    scholarship_lower = make_test_scholarship(eligible_nationalities=["any"])
    res2 = apply_prefilters({"nationality": "CA"}, scholarship_lower, EVAL_DATE)
    assert res2.passed is True

def test_citizenship_empty_passes():
    # If eligible nationalities is empty, any nationality should pass
    scholarship = make_test_scholarship(eligible_nationalities=[])
    res = apply_prefilters({"nationality": "US"}, scholarship, EVAL_DATE)
    assert res.passed is True

# --- DEGREE LEVEL FILTER TESTS ---

def test_degree_eligible_passes():
    scholarship = make_test_scholarship(degree_levels=["masters", "phd"])
    
    res1 = apply_prefilters({"degree_level": "masters"}, scholarship, EVAL_DATE)
    assert res1.passed is True

    # Case-insensitive
    res2 = apply_prefilters({"degree_level": "PHD"}, scholarship, EVAL_DATE)
    assert res2.passed is True

def test_degree_ineligible_fails():
    scholarship = make_test_scholarship(degree_levels=["masters", "phd"])
    res = apply_prefilters({"degree_level": "undergrad"}, scholarship, EVAL_DATE)
    assert res.passed is False
    assert "degree" in res.failed_filters
    assert "degree level" in res.reasons[0]

def test_degree_empty_passes():
    scholarship = make_test_scholarship(degree_levels=[])
    res = apply_prefilters({"degree_level": "undergrad"}, scholarship, EVAL_DATE)
    assert res.passed is True

# --- VISA RESTRICTION FILTER TESTS ---

def test_visa_eligible_passes():
    scholarship = make_test_scholarship(eligible_visa_types=["F-1", "J-1"])
    
    res1 = apply_prefilters({"visa_type": "F-1"}, scholarship, EVAL_DATE)
    assert res1.passed is True

    # Case-insensitive
    res2 = apply_prefilters({"visa_type": "j-1"}, scholarship, EVAL_DATE)
    assert res2.passed is True

def test_visa_ineligible_fails():
    scholarship = make_test_scholarship(eligible_visa_types=["F-1"])
    res = apply_prefilters({"visa_type": "J-1"}, scholarship, EVAL_DATE)
    assert res.passed is False
    assert "visa" in res.failed_filters
    assert "visa type" in res.reasons[0]

def test_visa_any_passes():
    scholarship = make_test_scholarship(eligible_visa_types=["any"])
    res = apply_prefilters({"visa_type": "H1B"}, scholarship, EVAL_DATE)
    assert res.passed is True

def test_visa_empty_passes():
    scholarship = make_test_scholarship(eligible_visa_types=[])
    res = apply_prefilters({"visa_type": "F-1"}, scholarship, EVAL_DATE)
    assert res.passed is True

# --- GENERAL COMBINED TESTS ---

def test_all_filters_pass():
    scholarship = make_test_scholarship(
        deadline="2026-06-25",
        eligible_nationalities=["IN", "PK"],
        degree_levels=["masters"],
        eligible_visa_types=["F-1"]
    )
    student = {
        "nationality": "IN",
        "degree_level": "masters",
        "visa_type": "F-1"
    }
    res = apply_prefilters(student, scholarship, EVAL_DATE)
    assert res.passed is True
    assert len(res.failed_filters) == 0
    assert len(res.reasons) == 0

def test_multiple_failures_collected():
    scholarship = make_test_scholarship(
        deadline="2026-06-08", # expired (fail 1)
        eligible_nationalities=["IN"], # mismatch (fail 2)
        degree_levels=["masters"], # mismatch (fail 3)
        eligible_visa_types=["F-1"] # mismatch (fail 4)
    )
    student = {
        "nationality": "US",
        "degree_level": "phd",
        "visa_type": "J-1"
    }
    res = apply_prefilters(student, scholarship, EVAL_DATE)
    assert res.passed is False
    assert set(res.failed_filters) == {"deadline", "citizenship", "degree", "visa"}
    assert len(res.reasons) == 4
