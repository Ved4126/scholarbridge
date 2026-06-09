"""
scorer.py — Phase 6: M/T Scorer

Implements the full deterministic scoring pipeline:
  - score_one(profile_vector, scholarship, eval_date) -> ScoringResult
  - score_all(profile_vector, scholarships, eval_date) -> list[ScoringResult]
  - compute_match_label(score) -> str

Rules enforced here:
  - output-type features always contribute 0 to M but always count toward T.
  - Unmatched non-output features go to gap_analysis.
  - All output-type feature labels go to action_checklist.
  - score_test is NOT implemented (deferred per AI_RULES.md).
  - Age is NOT a hard pre-filter; it is a range feature in the manifest.
  - Hard pre-filters (deadline, citizenship, degree, visa) run via apply_prefilters()
    before scoring in score_all().
  - Results below 40.0 are excluded from score_all output.
  - Results are sorted by score descending.
  - Maximum 20 results are returned by score_all.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from backend.app.scorer.feature_matcher import match_feature
from backend.app.scorer.models import (
    FeatureMatchDetail,
    ScholarshipFeature,
    ScholarshipRecord,
    ScoringResult,
)
from backend.app.scorer.prefilters import apply_prefilters


def _build_requirement_summary(feature: ScholarshipFeature) -> str:
    """Build a human-readable requirement string for gap analysis.

    Args:
        feature: The ScholarshipFeature being described.

    Returns:
        A short string such as '>= 3.5', 'in [IN, PK]', or 'must be True'.
    """
    f_type = feature.type
    if f_type == "enum":
        values = feature.values or []
        return f"in {values}"
    if f_type == "threshold":
        return f">= {feature.min}"
    if f_type == "boolean":
        return "must be True"
    if f_type == "range":
        if feature.min is not None and feature.max is not None:
            return f"{feature.min} – {feature.max}"
        if feature.min is not None:
            return f">= {feature.min}"
        if feature.max is not None:
            return f"<= {feature.max}"
        return "valid range required"
    # output type — should not appear in gap_analysis, but handle defensively
    return "action required"


def compute_match_label(score: float) -> str:
    """Return the human-readable match label for a given eligibility score.

    Score bands (per PRD.md § 4.5):
      90.0 – 100.0 → 'Strong Match'
      70.0 –  89.9 → 'Good Match'
      40.0 –  69.9 → 'Possible Match'
      below 40.0   → 'Below Threshold'

    Args:
        score: Eligibility score in the range 0.0 – 100.0.

    Returns:
        One of the four label strings above.
    """
    if score >= 90.0:
        return "Strong Match"
    if score >= 70.0:
        return "Good Match"
    if score >= 40.0:
        return "Possible Match"
    return "Below Threshold"


def score_one(
    profile_vector: dict[str, Any],
    scholarship: ScholarshipRecord,
) -> ScoringResult:
    """Score a single scholarship against a student's feature vector.

    Applies the M/T formula:
      Score = (M / T) × 100  (rounded to 1 decimal place)
      Returns 0.0 if T == 0 (no features in manifest).

    output-type features:
      - Always contribute 0 to M.
      - Always count toward T.
      - Their labels are added to action_checklist.

    Non-output features that are unmatched:
      - Contribute 0 to M.
      - Their details are added to gap_analysis.

    score_test features are not implemented (deferred) — this function
    expects the loader to have already excluded them.

    Args:
        profile_vector: Flat dict produced by StudentProfile.to_feature_vector().
        scholarship: Loaded and validated ScholarshipRecord.

    Returns:
        A ScoringResult populated with score, match_label, gap_analysis,
        and action_checklist.
    """
    features: list[ScholarshipFeature] = scholarship.feature_manifest.features
    T: int = len(features)
    M: int = 0
    gap_analysis: list[FeatureMatchDetail] = []
    action_checklist: list[str] = []

    for feature in features:
        if feature.type == "output":
            # Output features never contribute to M.
            # Collect the label as an action item.
            action_checklist.append(feature.label)
            # M += 0 implicitly
            continue

        result = match_feature(profile_vector, feature)

        if result.matched:
            M += 1
        else:
            # Unmatched non-output feature → add to gap_analysis.
            student_val = profile_vector.get(feature.student_field) if feature.student_field else None
            gap_analysis.append(
                FeatureMatchDetail(
                    field=feature.student_field or feature.id,
                    label=feature.label,
                    requirement=_build_requirement_summary(feature),
                    student_value=student_val,
                )
            )

    score = round((M / T) * 100, 1) if T > 0 else 0.0
    match_label = compute_match_label(score)

    return ScoringResult(
        scholarship_id=scholarship.id,
        name=scholarship.scholarship_name,
        org_name=scholarship.org_name,
        score=score,
        match_label=match_label,
        deadline=scholarship.deadline,
        source_url=scholarship.source_url,
        gap_analysis=gap_analysis,
        action_checklist=action_checklist,
    )


def score_all(
    profile_vector: dict[str, Any],
    scholarships: list[ScholarshipRecord],
    eval_date: date | None = None,
) -> list[ScoringResult]:
    """Score all scholarships against a student profile after applying hard pre-filters.

    Pipeline:
      1. For each scholarship, run apply_prefilters(). Skip if it fails.
      2. Score each passing scholarship via score_one().
      3. Exclude results with score < 40.0.
      4. Sort remaining results by score descending.
      5. Return the top 20 results.

    Args:
        profile_vector: Flat dict produced by StudentProfile.to_feature_vector().
        scholarships: List of loaded ScholarshipRecord objects.
        eval_date: Optional reference date for deadline checking (defaults to today).

    Returns:
        Sorted list of up to 20 ScoringResult objects, all with score >= 40.0.
    """
    if eval_date is None:
        eval_date = date.today()

    results: list[ScoringResult] = []

    for scholarship in scholarships:
        prefilter_result = apply_prefilters(profile_vector, scholarship, eval_date)
        if not prefilter_result.passed:
            continue

        result = score_one(profile_vector, scholarship)

        if result.score < 40.0:
            continue

        results.append(result)

    # Sort by score descending, then return top 20.
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:20]
