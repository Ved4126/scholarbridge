from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel
from backend.app.scorer.models import ScholarshipRecord

class PreFilterResult(BaseModel):
    passed: bool
    failed_filters: list[str]
    reasons: list[str]

def apply_prefilters(
    student_features: dict,
    scholarship: ScholarshipRecord,
    evaluation_date: date | None = None
) -> PreFilterResult:
    if evaluation_date is None:
        evaluation_date = date.today()

    failed_filters = []
    reasons = []

    # 1. Deadline Filter
    deadline_str = scholarship.deadline
    if not deadline_str or not deadline_str.strip():
        failed_filters.append("deadline")
        reasons.append("Scholarship deadline is missing")
    else:
        try:
            if "T" in deadline_str:
                deadline_date = datetime.fromisoformat(deadline_str).date()
            else:
                deadline_date = datetime.strptime(deadline_str.strip(), "%Y-%m-%d").date()
            
            if deadline_date < evaluation_date:
                failed_filters.append("deadline")
                reasons.append(f"Scholarship deadline {deadline_str} has expired")
            elif (deadline_date - evaluation_date).days <= 14:
                failed_filters.append("deadline")
                reasons.append(f"Scholarship deadline {deadline_str} is within 14 days")
        except ValueError:
            failed_filters.append("deadline")
            reasons.append(f"Scholarship deadline {deadline_str} has invalid date format")

    # 2. Citizenship Filter
    # Open / empty list or list containing "any" (case-insensitive) passes.
    eligible_nats = [n.strip().lower() for n in scholarship.eligible_nationalities if n]
    if eligible_nats and "any" not in eligible_nats:
        student_nationalities = []
        nat = student_features.get("nationality")
        if nat and isinstance(nat, str) and nat.strip():
            student_nationalities.append(nat.strip().lower())
        
        dual_nat = student_features.get("dual_citizenship")
        if dual_nat and isinstance(dual_nat, str) and dual_nat.strip():
            for dn in dual_nat.split(","):
                dn_clean = dn.strip().lower()
                if dn_clean and dn_clean not in student_nationalities:
                    student_nationalities.append(dn_clean)
        
        matched = False
        for sn in student_nationalities:
            if sn in eligible_nats:
                matched = True
                break
        if not matched:
            failed_filters.append("citizenship")
            student_nat_val = student_features.get("nationality") or "None"
            reasons.append(f"Student nationality {student_nat_val} is not eligible")

    # 3. Degree Level Filter
    eligible_degrees = [d.strip().lower() for d in scholarship.degree_levels if d]
    if eligible_degrees:
        student_degree = student_features.get("degree_level")
        if not student_degree or not isinstance(student_degree, str) or student_degree.strip().lower() not in eligible_degrees:
            failed_filters.append("degree")
            student_degree_val = student_degree or "None"
            reasons.append(f"Student degree level {student_degree_val} is not eligible")

    # 4. Visa Restriction Filter
    eligible_visas = [v.strip().lower() for v in scholarship.eligible_visa_types if v]
    if eligible_visas and "any" not in eligible_visas:
        student_visa = student_features.get("visa_type")
        if not student_visa or not isinstance(student_visa, str) or student_visa.strip().lower() not in eligible_visas:
            failed_filters.append("visa")
            student_visa_val = student_visa or "None"
            reasons.append(f"Student visa type {student_visa_val} is not eligible")

    passed = len(failed_filters) == 0
    return PreFilterResult(
        passed=passed,
        failed_filters=failed_filters,
        reasons=reasons
    )
