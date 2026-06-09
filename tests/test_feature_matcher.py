import pytest
from backend.app.scorer.feature_matcher import match_feature
from backend.app.scorer.models import ScholarshipFeature

# ENUM tests
def test_enum_exact_match():
    feature = ScholarshipFeature(id="n1", label="Nationality", type="enum", student_field="nationality", values=["IN", "PK", "BD"], required=True)
    res = match_feature({"nationality": "IN"}, feature)
    assert res.matched is True

def test_enum_no_match():
    feature = ScholarshipFeature(id="n1", label="Nationality", type="enum", student_field="nationality", values=["IN", "PK", "BD"], required=True)
    res = match_feature({"nationality": "US"}, feature)
    assert res.matched is False

def test_enum_missing_field():
    feature = ScholarshipFeature(id="n1", label="Nationality", type="enum", student_field="nationality", values=["IN"], required=True)
    res = match_feature({"other": "IN"}, feature)
    assert res.matched is False
    assert "Missing student information" in res.reason

def test_enum_case_insensitive_match():
    feature = ScholarshipFeature(id="n1", label="Nationality", type="enum", student_field="nationality", values=["IN"], required=True)
    res = match_feature({"nationality": "in"}, feature)
    assert res.matched is True
    
    feature2 = ScholarshipFeature(id="n1", label="Nationality", type="enum", student_field="nationality", values=["in"], required=True)
    res2 = match_feature({"nationality": "IN"}, feature2)
    assert res2.matched is True

# THRESHOLD tests
def test_threshold_passes():
    feature = ScholarshipFeature(id="gpa", label="GPA", type="threshold", student_field="gpa", min=3.5, required=True)
    res = match_feature({"gpa": 3.8}, feature)
    assert res.matched is True

def test_threshold_fails():
    feature = ScholarshipFeature(id="gpa", label="GPA", type="threshold", student_field="gpa", min=3.5, required=True)
    res = match_feature({"gpa": 3.0}, feature)
    assert res.matched is False

def test_threshold_missing_field():
    feature = ScholarshipFeature(id="gpa", label="GPA", type="threshold", student_field="gpa", min=3.5, required=True)
    res = match_feature({}, feature)
    assert res.matched is False
    assert "Missing" in res.reason

def test_threshold_invalid_type():
    feature = ScholarshipFeature(id="gpa", label="GPA", type="threshold", student_field="gpa", min=3.5, required=True)
    res = match_feature({"gpa": "A+"}, feature)
    assert res.matched is False
    assert "Invalid numeric" in res.reason

# BOOLEAN tests
def test_boolean_true():
    feature = ScholarshipFeature(id="b1", label="Published", type="boolean", student_field="published_research", required=True)
    res = match_feature({"published_research": True}, feature)
    assert res.matched is True

def test_boolean_false():
    feature = ScholarshipFeature(id="b1", label="Published", type="boolean", student_field="published_research", required=True)
    res = match_feature({"published_research": False}, feature)
    assert res.matched is False

def test_boolean_missing_field():
    feature = ScholarshipFeature(id="b1", label="Published", type="boolean", student_field="published_research", required=True)
    res = match_feature({}, feature)
    assert res.matched is False

# OUTPUT tests
def test_output_always_unmatched():
    feature = ScholarshipFeature(id="essay", label="Essay", type="output", required=True)
    res = match_feature({"essay": "Done"}, feature)
    assert res.matched is False
    assert "must be prepared by the student" in res.reason

# RANGE tests
def test_range_within_range():
    feature = ScholarshipFeature(id="age", label="Age", type="range", student_field="age", min=18, max=35, required=True)
    res = match_feature({"age": 24}, feature)
    assert res.matched is True

def test_range_below_range():
    feature = ScholarshipFeature(id="age", label="Age", type="range", student_field="age", min=18, max=35, required=True)
    res = match_feature({"age": 16}, feature)
    assert res.matched is False

def test_range_above_range():
    feature = ScholarshipFeature(id="age", label="Age", type="range", student_field="age", min=18, max=35, required=True)
    res = match_feature({"age": 40}, feature)
    assert res.matched is False

def test_range_min_only():
    feature = ScholarshipFeature(id="age", label="Age", type="range", student_field="age", min=18, required=True)
    res = match_feature({"age": 20}, feature)
    assert res.matched is True
    res2 = match_feature({"age": 15}, feature)
    assert res2.matched is False

def test_range_max_only():
    feature = ScholarshipFeature(id="age", label="Age", type="range", student_field="age", max=35, required=True)
    res = match_feature({"age": 20}, feature)
    assert res.matched is True
    res2 = match_feature({"age": 40}, feature)
    assert res2.matched is False

def test_range_missing_field():
    feature = ScholarshipFeature(id="age", label="Age", type="range", student_field="age", min=18, max=35, required=True)
    res = match_feature({}, feature)
    assert res.matched is False

# GENERAL
def test_unsupported_type():
    # Hack the type to test the ValueError
    feature = ScholarshipFeature(id="err", label="Err", type="output", required=True)
    feature.type = "unsupported"
    with pytest.raises(ValueError, match="Unsupported feature type"):
        match_feature({"err": 1}, feature)

def test_missing_student_field_in_config():
    feature = ScholarshipFeature(id="err", label="Err", type="boolean", required=True)
    # Valid ScholarshipFeature since student_field is Optional
    res = match_feature({"err": 1}, feature)
    assert res.matched is False
    assert "configuration error" in res.reason
