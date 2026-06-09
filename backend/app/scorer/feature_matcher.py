from pydantic import BaseModel
from backend.app.scorer.models import ScholarshipFeature

class FeatureMatchResult(BaseModel):
    feature_id: str
    feature_type: str
    matched: bool
    required: bool
    reason: str

def match_feature(student_features: dict, feature: ScholarshipFeature) -> FeatureMatchResult:
    f_type = feature.type
    f_id = feature.id
    f_req = feature.required
    f_student_field = feature.student_field

    if f_type == "output":
        return FeatureMatchResult(
            feature_id=f_id,
            feature_type=f_type,
            matched=False,
            required=f_req,
            reason=f"Action required: this item ({feature.label}) must be prepared by the student."
        )

    # For other types, check if student field is specified
    if not f_student_field:
        return FeatureMatchResult(
            feature_id=f_id,
            feature_type=f_type,
            matched=False,
            required=f_req,
            reason="Feature configuration error: student_field is missing."
        )

    student_value = student_features.get(f_student_field)
    if student_value is None:
        return FeatureMatchResult(
            feature_id=f_id,
            feature_type=f_type,
            matched=False,
            required=f_req,
            reason=f"Missing student information for {f_student_field}."
        )

    if f_type == "enum":
        allowed_values = feature.values or []
        # Case insensitive exact membership check for strings
        allowed_lower = [str(v).lower() if isinstance(v, str) else v for v in allowed_values]
        student_val_match = str(student_value).lower() if isinstance(student_value, str) else student_value
        
        if student_val_match in allowed_lower:
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=True,
                required=f_req,
                reason=f"Student {f_student_field} ({student_value}) matches allowed values."
            )
        else:
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=False,
                required=f_req,
                reason=f"Student {f_student_field} ({student_value}) is not in allowed values."
            )

    elif f_type == "threshold":
        # threshold only supports min for MVP based on rules
        min_val = feature.min
        if min_val is None:
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=False,
                required=f_req,
                reason="Feature configuration error: threshold feature missing min."
            )
        
        try:
            val_float = float(student_value)
            min_float = float(min_val)
        except (ValueError, TypeError):
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=False,
                required=f_req,
                reason="Invalid numeric type for threshold comparison."
            )

        if val_float >= min_float:
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=True,
                required=f_req,
                reason=f"Student {f_student_field} {val_float} >= minimum {min_float}."
            )
        else:
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=False,
                required=f_req,
                reason=f"Student {f_student_field} {val_float} < minimum {min_float}."
            )

    elif f_type == "boolean":
        if bool(student_value):
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=True,
                required=f_req,
                reason=f"Student {f_student_field} requirement met."
            )
        else:
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=False,
                required=f_req,
                reason=f"Student {f_student_field} requirement not met."
            )

    elif f_type == "range":
        min_val = feature.min
        max_val = feature.max
        try:
            val_float = float(student_value)
        except (ValueError, TypeError):
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=False,
                required=f_req,
                reason="Invalid numeric type for range comparison."
            )

        if min_val is not None and max_val is not None:
            if float(min_val) <= val_float <= float(max_val):
                return FeatureMatchResult(
                    feature_id=f_id,
                    feature_type=f_type,
                    matched=True,
                    required=f_req,
                    reason=f"Student {f_student_field} {val_float} is within {min_val} and {max_val}."
                )
            else:
                return FeatureMatchResult(
                    feature_id=f_id,
                    feature_type=f_type,
                    matched=False,
                    required=f_req,
                    reason=f"Student {f_student_field} {val_float} is outside {min_val} and {max_val}."
                )
        elif min_val is not None:
            if val_float >= float(min_val):
                return FeatureMatchResult(
                    feature_id=f_id,
                    feature_type=f_type,
                    matched=True,
                    required=f_req,
                    reason=f"Student {f_student_field} {val_float} >= minimum {min_val}."
                )
            else:
                return FeatureMatchResult(
                    feature_id=f_id,
                    feature_type=f_type,
                    matched=False,
                    required=f_req,
                    reason=f"Student {f_student_field} {val_float} < minimum {min_val}."
                )
        elif max_val is not None:
            if val_float <= float(max_val):
                return FeatureMatchResult(
                    feature_id=f_id,
                    feature_type=f_type,
                    matched=True,
                    required=f_req,
                    reason=f"Student {f_student_field} {val_float} <= maximum {max_val}."
                )
            else:
                return FeatureMatchResult(
                    feature_id=f_id,
                    feature_type=f_type,
                    matched=False,
                    required=f_req,
                    reason=f"Student {f_student_field} {val_float} > maximum {max_val}."
                )
        else:
            return FeatureMatchResult(
                feature_id=f_id,
                feature_type=f_type,
                matched=False,
                required=f_req,
                reason="Feature configuration error: range feature missing both min and max."
            )

    else:
        raise ValueError(f"Unsupported feature type: {f_type}")
