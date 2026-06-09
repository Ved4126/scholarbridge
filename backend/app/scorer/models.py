from typing import Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class ScholarshipFeature(BaseModel):
    id: str
    label: str
    type: Literal["enum", "threshold", "boolean", "output", "range"]
    required: bool
    student_field: str | None = None
    values: list[Any] | None = None
    min: float | None = None
    max: float | None = None
    weight: float | None = None

class FeatureManifest(BaseModel):
    total_features: int
    features: list[ScholarshipFeature]

class ScholarshipRecord(BaseModel):
    id: str
    scholarship_name: str
    org_name: str
    source_url: str
    country: str
    source_type: str
    award_amount: float | None = None
    currency: str | None = None
    deadline: str | None = None
    award_year: str | int | None = None
    degree_levels: list[str] = Field(default_factory=list)
    eligible_nationalities: list[str] = Field(default_factory=list)
    eligible_visa_types: list[str] = Field(default_factory=list)
    fields_of_study: list[str] = Field(default_factory=list)
    description: str
    eligibility_text: str
    feature_manifest: FeatureManifest
    last_verified: str | datetime
    created_at: str | datetime
    updated_at: str | datetime
