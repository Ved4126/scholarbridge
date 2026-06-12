"""
test_scorer.py — Phase 6 Tests: M/T Scorer

Tests for:
  - score_one(): M/T formula, gap_analysis, action_checklist, edge cases
  - score_all(): pre-filter integration, sorting, threshold, max results
  - compute_match_label(): all four score bands
  - T=0 edge case
  - Missing age does not block scoring
  - Output-only scholarships
"""
from __future__ import annotations

from datetime import date

import pytest

from backend.app.scorer.models import (
    FeatureManifest,
    FeatureMatchDetail,
    ScholarshipFeature,
    ScholarshipRecord,
    ScoringResult,
)
from backend.app.scorer.scorer import compute_match_label, score_all, score_one

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FUTURE_DEADLINE = "2099-12-31"
PAST_DEADLINE = "2020-01-01"
EVAL_DATE = date(2026, 6, 9)


def make_scholarship(
    features: list[dict],
    deadline: str = FUTURE_DEADLINE,
    eligible_nationalities: list[str] | None = None,
    degree_levels: list[str] | None = None,
    eligible_visa_types: list[str] | None = None,
    scholarship_id: str = "test-scholarship",
    scholarship_name: str = "Test Scholarship",
    org_name: str = "Test Org",
) -> ScholarshipRecord:
    """Build a ScholarshipRecord from a list of raw feature dicts."""
    feature_objects = [ScholarshipFeature(**f) for f in features]
    manifest = FeatureManifest(total_features=len(feature_objects), features=feature_objects)
    return ScholarshipRecord(
        id=scholarship_id,
        scholarship_name=scholarship_name,
        org_name=org_name,
        source_url="https://example.com/test",
        country="US",
        source_type="test",
        deadline=deadline,
        degree_levels=degree_levels or [],
        eligible_nationalities=eligible_nationalities or [],
        eligible_visa_types=eligible_visa_types or [],
        fields_of_study=[],
        description="Test",
        eligibility_text="Test",
        feature_manifest=manifest,
        last_verified="2026-06-09T00:00:00Z",
        created_at="2026-06-09T00:00:00Z",
        updated_at="2026-06-09T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# 1. Known profile + known scholarship gives exact expected score
# ---------------------------------------------------------------------------

def test_known_profile_known_scholarship_exact_score():
    """A scholarship with 5 features where the profile matches 3 non-output ones
    and 1 is output should give: M=3, T=5, score = (3/5)*100 = 60.0."""
    features = [
        {"id": "nationality", "label": "Nationality", "type": "enum",
         "student_field": "nationality", "values": ["IN", "PK"], "required": True},
        {"id": "degree", "label": "Degree Level", "type": "enum",
         "student_field": "degree_level", "values": ["masters"], "required": True},
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.0, "required": True},
        {"id": "research", "label": "Research", "type": "boolean",
         "student_field": "published_research", "required": False},
        {"id": "essay", "label": "Personal Statement", "type": "output", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {
        "nationality": "IN",
        "degree_level": "masters",
        "gpa": 3.5,
        "published_research": False,  # unmatched
    }
    result = score_one(profile_vector, scholarship)
    # M=3 (nationality, degree, gpa matched), T=5
    assert result.score == 60.0
    assert result.match_label == "Possible Match"
    assert result.scholarship_id == "test-scholarship"
    assert result.name == "Test Scholarship"
    assert result.org_name == "Test Org"


# ---------------------------------------------------------------------------
# 2. All matched non-output features gives correct score
# ---------------------------------------------------------------------------

def test_all_non_output_features_matched():
    """All non-output features matched → M = number of non-output features,
    T = total features, score is correct."""
    features = [
        {"id": "nationality", "label": "Nationality", "type": "enum",
         "student_field": "nationality", "values": ["IN"], "required": True},
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.0, "required": True},
        {"id": "essay", "label": "Essay", "type": "output", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"nationality": "IN", "gpa": 3.8}
    result = score_one(profile_vector, scholarship)
    # M=2, T=3 → 66.7
    assert result.score == 66.7
    assert result.match_label == "Possible Match"
    assert len(result.gap_analysis) == 0


# ---------------------------------------------------------------------------
# 3. No matched features gives 0.0
# ---------------------------------------------------------------------------

def test_no_matched_features_gives_zero():
    """Profile matches nothing → score is 0.0."""
    features = [
        {"id": "nationality", "label": "Nationality", "type": "enum",
         "student_field": "nationality", "values": ["IN"], "required": True},
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.8, "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"nationality": "US", "gpa": 2.0}
    result = score_one(profile_vector, scholarship)
    assert result.score == 0.0
    assert result.match_label == "Below Threshold"
    assert len(result.gap_analysis) == 2


# ---------------------------------------------------------------------------
# 4. Scholarship with only output features → score 0.0, action_checklist
#    populated, gap_analysis empty
# ---------------------------------------------------------------------------

def test_only_output_features_score_zero_action_checklist_populated():
    """When all features are output-type: T > 0, M = 0, score = 0.0,
    gap_analysis is empty, action_checklist is fully populated."""
    features = [
        {"id": "essay", "label": "Write personal statement", "type": "output", "required": True},
        {"id": "rec", "label": "Obtain 2 recommendation letters", "type": "output", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"nationality": "IN", "gpa": 4.0}

    result = score_one(profile_vector, scholarship)

    assert result.score == 0.0
    assert result.match_label == "Below Threshold"
    assert len(result.gap_analysis) == 0
    assert len(result.action_checklist) == 2
    assert "Write personal statement" in result.action_checklist
    assert "Obtain 2 recommendation letters" in result.action_checklist


# ---------------------------------------------------------------------------
# 5. Gap analysis contains exactly unmatched non-output features
# ---------------------------------------------------------------------------

def test_gap_analysis_contains_only_unmatched_non_output():
    """gap_analysis must not contain output features and must contain all
    unmatched non-output features."""
    features = [
        {"id": "nationality", "label": "Nationality", "type": "enum",
         "student_field": "nationality", "values": ["IN"], "required": True},
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.8, "required": True},  # will NOT match
        {"id": "essay", "label": "Essay", "type": "output", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"nationality": "IN", "gpa": 3.0}  # nationality matches, gpa doesn't

    result = score_one(profile_vector, scholarship)

    assert len(result.gap_analysis) == 1
    assert result.gap_analysis[0].field == "gpa"
    assert result.gap_analysis[0].label == "GPA"
    # essay must NOT be in gap_analysis
    gap_fields = [g.field for g in result.gap_analysis]
    assert "essay" not in gap_fields


# ---------------------------------------------------------------------------
# 6. Action checklist contains exactly output-type feature descriptions
# ---------------------------------------------------------------------------

def test_action_checklist_contains_exactly_output_labels():
    """action_checklist should contain exactly the labels of all output-type
    features — nothing else."""
    features = [
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.0, "required": True},
        {"id": "essay", "label": "Write essay (500 words)", "type": "output", "required": True},
        {"id": "rec", "label": "Get 3 recommendation letters", "type": "output", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"gpa": 3.9}

    result = score_one(profile_vector, scholarship)

    assert len(result.action_checklist) == 2
    assert "Write essay (500 words)" in result.action_checklist
    assert "Get 3 recommendation letters" in result.action_checklist
    # Non-output labels must NOT appear in action_checklist
    assert "GPA" not in result.action_checklist


# ---------------------------------------------------------------------------
# 7. score_all() applies hard pre-filters correctly
# ---------------------------------------------------------------------------

def test_score_all_applies_hard_prefilters():
    """Scholarship failing a pre-filter should not appear in score_all results."""
    features = [
        {"id": "nationality", "label": "Nationality", "type": "enum",
         "student_field": "nationality", "values": ["IN"], "required": True},
    ]
    # This scholarship requires IN nationality but the profile is US — filtered by citizenship
    rejected = make_scholarship(
        features,
        deadline=FUTURE_DEADLINE,
        eligible_nationalities=["CN"],  # student is IN — will fail citizenship filter
        scholarship_id="rejected-scholarship",
    )
    accepted = make_scholarship(
        [{"id": "nationality", "label": "Nationality", "type": "enum",
          "student_field": "nationality", "values": ["IN"], "required": True}],
        deadline=FUTURE_DEADLINE,
        eligible_nationalities=[],  # open to all
        scholarship_id="accepted-scholarship",
    )
    profile_vector = {"nationality": "IN", "degree_level": "masters", "visa_type": "F-1"}

    results = score_all(profile_vector, [rejected, accepted], eval_date=EVAL_DATE)

    ids = [r.scholarship_id for r in results]
    assert "rejected-scholarship" not in ids
    assert "accepted-scholarship" in ids


# ---------------------------------------------------------------------------
# 8. Expired scholarship is excluded
# ---------------------------------------------------------------------------

def test_score_all_excludes_expired_scholarship():
    """Scholarship with a past deadline must not appear in score_all results."""
    features = [
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 2.0, "required": True},
    ]
    # Far-future deadline; deadline filter sets a 14-day minimum, so use 30 days out
    future_deadline = "2099-12-31"
    expired = make_scholarship(features, deadline=PAST_DEADLINE, scholarship_id="expired-s")
    active = make_scholarship(features, deadline=future_deadline, scholarship_id="active-s")
    profile_vector = {"gpa": 3.5}

    results = score_all(profile_vector, [expired, active], eval_date=EVAL_DATE)

    ids = [r.scholarship_id for r in results]
    assert "expired-s" not in ids
    assert "active-s" in ids


# ---------------------------------------------------------------------------
# 9. Results are sorted by score descending
# ---------------------------------------------------------------------------

def test_score_all_sorted_by_score_descending():
    """score_all() results must come back sorted highest score first."""
    # Scholarship A: only 1 feature, profile matches → 100.0
    s_a = make_scholarship(
        [{"id": "gpa", "label": "GPA", "type": "threshold",
          "student_field": "gpa", "min": 2.0, "required": True}],
        scholarship_id="high-scorer",
    )
    # Scholarship B: 2 features, profile matches only 1 → 50.0
    s_b = make_scholarship(
        [
            {"id": "gpa", "label": "GPA", "type": "threshold",
             "student_field": "gpa", "min": 2.0, "required": True},
            {"id": "research", "label": "Research", "type": "boolean",
             "student_field": "published_research", "required": True},
        ],
        scholarship_id="mid-scorer",
    )
    profile_vector = {"gpa": 3.5, "published_research": False}

    results = score_all(profile_vector, [s_b, s_a], eval_date=EVAL_DATE)

    assert len(results) >= 2
    assert results[0].score >= results[1].score
    assert results[0].scholarship_id == "high-scorer"


# ---------------------------------------------------------------------------
# 10. Results below 40.0 are excluded
# ---------------------------------------------------------------------------

def test_score_all_excludes_below_40():
    """Scholarships scoring < 40.0 must not appear in score_all() results."""
    # 4 features, profile matches 0 → score 0.0 (below 40)
    s_low = make_scholarship(
        [
            {"id": "nat", "label": "Nationality", "type": "enum",
             "student_field": "nationality", "values": ["IN"], "required": True},
            {"id": "gpa", "label": "GPA", "type": "threshold",
             "student_field": "gpa", "min": 3.9, "required": True},
            {"id": "research", "label": "Research", "type": "boolean",
             "student_field": "published_research", "required": True},
            {"id": "leadership", "label": "Leadership", "type": "boolean",
             "student_field": "has_leadership", "required": True},
        ],
        scholarship_id="low-scorer",
    )
    # 1 feature, matches → score 100.0 (above 40)
    s_high = make_scholarship(
        [{"id": "gpa", "label": "GPA", "type": "threshold",
          "student_field": "gpa", "min": 2.0, "required": True}],
        scholarship_id="good-scorer",
    )
    profile_vector = {
        "nationality": "US",
        "gpa": 2.5,
        "published_research": False,
        "has_leadership": False,
    }

    results = score_all(profile_vector, [s_low, s_high], eval_date=EVAL_DATE)

    ids = [r.scholarship_id for r in results]
    assert "low-scorer" not in ids
    assert "good-scorer" in ids


# ---------------------------------------------------------------------------
# 11. Maximum 20 results are returned
# ---------------------------------------------------------------------------

def test_score_all_returns_maximum_20_results():
    """score_all() must cap results at 20 even when more qualify."""
    # Build 25 identical scholarships that all score 100.0
    scholarships = []
    for i in range(25):
        s = make_scholarship(
            [{"id": "gpa", "label": "GPA", "type": "threshold",
              "student_field": "gpa", "min": 2.0, "required": True}],
            scholarship_id=f"scholarship-{i}",
        )
        scholarships.append(s)

    profile_vector = {"gpa": 3.5}
    results = score_all(profile_vector, scholarships, eval_date=EVAL_DATE)

    assert len(results) == 20


# ---------------------------------------------------------------------------
# 12. T = 0 returns 0.0 without division-by-zero error
# ---------------------------------------------------------------------------

def test_t_equals_zero_returns_zero_without_error():
    """Empty feature manifest: T=0 must return score 0.0 with no exception."""
    scholarship = make_scholarship(features=[])
    profile_vector = {"gpa": 4.0, "nationality": "IN"}
    result = score_one(profile_vector, scholarship)
    assert result.score == 0.0
    assert result.match_label == "Below Threshold"
    assert len(result.gap_analysis) == 0
    assert len(result.action_checklist) == 0


# ---------------------------------------------------------------------------
# 13. Match labels are correct for all bands
# ---------------------------------------------------------------------------

def test_compute_match_label_strong_match():
    assert compute_match_label(90.0) == "Strong Match"
    assert compute_match_label(100.0) == "Strong Match"
    assert compute_match_label(95.5) == "Strong Match"


def test_compute_match_label_good_match():
    assert compute_match_label(70.0) == "Good Match"
    assert compute_match_label(89.9) == "Good Match"
    assert compute_match_label(78.4) == "Good Match"


def test_compute_match_label_possible_match():
    assert compute_match_label(40.0) == "Possible Match"
    assert compute_match_label(69.9) == "Possible Match"
    assert compute_match_label(55.0) == "Possible Match"


def test_compute_match_label_below_threshold():
    assert compute_match_label(39.9) == "Below Threshold"
    assert compute_match_label(0.0) == "Below Threshold"
    assert compute_match_label(20.0) == "Below Threshold"


# ---------------------------------------------------------------------------
# 14. Missing age does not block scoring; age range feature becomes unmatched
# ---------------------------------------------------------------------------

def test_missing_age_does_not_block_scoring():
    """If the scholarship has an age range feature but the profile has no age,
    the scholarship is still scored (age becomes an unmatched feature)."""
    features = [
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.0, "required": True},
        {"id": "age", "label": "Age", "type": "range",
         "student_field": "age", "min": 18, "max": 30, "required": False},
    ]
    scholarship = make_scholarship(features)
    # No 'age' key in profile vector — simulates a student who didn't provide age
    profile_vector = {"gpa": 3.5}

    result = score_one(profile_vector, scholarship)

    # Scholarship is still scored: M=1 (gpa), T=2 → 50.0
    assert result.score == 50.0
    assert result.match_label == "Possible Match"

    # Age appears in gap_analysis as unmatched
    gap_fields = [g.field for g in result.gap_analysis]
    assert "age" in gap_fields


def test_missing_age_scholarship_still_appears_in_score_all():
    """score_all() must not filter out a scholarship just because age is missing."""
    features = [
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.0, "required": True},
        {"id": "age", "label": "Age", "type": "range",
         "student_field": "age", "min": 18, "max": 30, "required": False},
    ]
    scholarship = make_scholarship(features, scholarship_id="age-scholarship")
    profile_vector = {"gpa": 3.5}  # no age field

    results = score_all(profile_vector, [scholarship], eval_date=EVAL_DATE)

    ids = [r.scholarship_id for r in results]
    assert "age-scholarship" in ids


# ---------------------------------------------------------------------------
# 15. ScoringResult model completeness
# ---------------------------------------------------------------------------

def test_scoring_result_includes_all_required_fields():
    """ScoringResult must include all fields specified in PRD.md § 4.6."""
    features = [
        {"id": "gpa", "label": "GPA", "type": "threshold",
         "student_field": "gpa", "min": 3.0, "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"gpa": 3.5}

    result = score_one(profile_vector, scholarship)

    assert hasattr(result, "scholarship_id")
    assert hasattr(result, "name")
    assert hasattr(result, "org_name")
    assert hasattr(result, "score")
    assert hasattr(result, "match_label")
    assert hasattr(result, "deadline")
    assert hasattr(result, "source_url")
    assert hasattr(result, "gap_analysis")
    assert hasattr(result, "action_checklist")


# ---------------------------------------------------------------------------
# 16. score_all() returns empty list if all scholarships fail pre-filters
# ---------------------------------------------------------------------------

def test_score_all_returns_empty_list_when_all_filtered():
    """When all scholarships fail the pre-filter, score_all returns []."""
    expired_scholarship = make_scholarship(
        [{"id": "gpa", "label": "GPA", "type": "threshold",
          "student_field": "gpa", "min": 2.0, "required": True}],
        deadline=PAST_DEADLINE,
    )
    profile_vector = {"gpa": 3.5}

    results = score_all(profile_vector, [expired_scholarship], eval_date=EVAL_DATE)

    assert results == []


# ---------------------------------------------------------------------------
# 17. Output features do NOT appear in gap_analysis even when profile is empty
# ---------------------------------------------------------------------------

def test_output_features_never_in_gap_analysis():
    """Output-type features must never appear in gap_analysis, regardless of
    whether the profile provides a matching value."""
    features = [
        {"id": "essay", "label": "Essay", "type": "output", "required": True},
        {"id": "rec", "label": "Reference Letter", "type": "output", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {}  # empty profile

    result = score_one(profile_vector, scholarship)

    assert len(result.gap_analysis) == 0


# ---------------------------------------------------------------------------
# 18. Score rounding — explicit verification at 1 decimal place
# ---------------------------------------------------------------------------

def test_rounding_two_of_three_features():
    """Canonical repeating decimal: M=2, T=3 → 66.666... rounds to 66.7."""
    features = [
        {"id": "f1", "label": "F1", "type": "boolean",
         "student_field": "f1", "required": True},
        {"id": "f2", "label": "F2", "type": "boolean",
         "student_field": "f2", "required": True},
        {"id": "f3", "label": "F3", "type": "boolean",
         "student_field": "f3", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"f1": True, "f2": True, "f3": False}

    result = score_one(profile_vector, scholarship)

    # Raw: (2/3)*100 = 66.666... → rounded to 66.7
    assert result.score == 66.7
    assert result.match_label == "Possible Match"


def test_rounding_one_of_three_features():
    """M=1, T=3 → 33.333... rounds to 33.3."""
    features = [
        {"id": "f1", "label": "F1", "type": "boolean",
         "student_field": "f1", "required": True},
        {"id": "f2", "label": "F2", "type": "boolean",
         "student_field": "f2", "required": True},
        {"id": "f3", "label": "F3", "type": "boolean",
         "student_field": "f3", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {"f1": True, "f2": False, "f3": False}

    result = score_one(profile_vector, scholarship)

    # Raw: (1/3)*100 = 33.333... → rounded to 33.3
    assert result.score == 33.3
    assert result.match_label == "Below Threshold"


def test_rounding_one_of_six_features():
    """M=1, T=6 → 16.666... rounds to 16.7."""
    features = [
        {"id": f"f{i}", "label": f"F{i}", "type": "boolean",
         "student_field": f"f{i}", "required": True}
        for i in range(6)
    ]
    scholarship = make_scholarship(features)
    profile_vector = {f"f{i}": (i == 0) for i in range(6)}

    result = score_one(profile_vector, scholarship)

    # Raw: (1/6)*100 = 16.666... → rounded to 16.7
    assert result.score == 16.7
    assert result.match_label == "Below Threshold"


def test_rounding_five_of_six_features():
    """M=5, T=6 → 83.333... rounds to 83.3."""
    features = [
        {"id": f"f{i}", "label": f"F{i}", "type": "boolean",
         "student_field": f"f{i}", "required": True}
        for i in range(6)
    ]
    scholarship = make_scholarship(features)
    profile_vector = {f"f{i}": (i != 5) for i in range(6)}

    result = score_one(profile_vector, scholarship)

    # Raw: (5/6)*100 = 83.333... → rounded to 83.3
    assert result.score == 83.3
    assert result.match_label == "Good Match"


def test_rounding_clean_score_unchanged():
    """Scores that are already clean (M/T produces a terminating decimal)
    must not be altered by rounding."""
    features = [
        {"id": "f1", "label": "F1", "type": "boolean",
         "student_field": "f1", "required": True},
        {"id": "f2", "label": "F2", "type": "boolean",
         "student_field": "f2", "required": True},
        {"id": "f3", "label": "F3", "type": "boolean",
         "student_field": "f3", "required": True},
        {"id": "f4", "label": "F4", "type": "boolean",
         "student_field": "f4", "required": True},
    ]
    scholarship = make_scholarship(features)
    profile_vector = {f"f{i+1}": True for i in range(4)}

    result = score_one(profile_vector, scholarship)

    # (4/4)*100 = 100.0 exactly
    assert result.score == 100.0
    assert result.match_label == "Strong Match"


def test_rounding_at_band_boundary_after_round():
    """Match labels are assigned on the rounded score, not the raw float.
    9 of 10 features matched → exactly 90.0 → Strong Match."""
    features = [
        {"id": f"f{i}", "label": f"F{i}", "type": "boolean",
         "student_field": f"f{i}", "required": True}
        for i in range(10)
    ]
    scholarship_all = make_scholarship(features, scholarship_id="s-all")
    scholarship_nine = make_scholarship(features, scholarship_id="s-nine")

    # All 10 match → 100.0
    result_all = score_one({f"f{i}": True for i in range(10)}, scholarship_all)
    assert result_all.score == 100.0
    assert result_all.match_label == "Strong Match"

    # 9 of 10 match → exactly 90.0 → Strong Match
    result_nine = score_one({f"f{i}": (i != 9) for i in range(10)}, scholarship_nine)
    assert result_nine.score == 90.0
    assert result_nine.match_label == "Strong Match"

