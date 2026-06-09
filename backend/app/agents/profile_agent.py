from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

class StudentProfile(BaseModel):
    # Personal
    full_name: str = Field(min_length=1)
    date_of_birth: date
    gender: str | None = None
    nationality: str = Field(min_length=1)
    dual_citizenship: str | None = None
    home_country: str
    home_city: str | None = None
    visa_type: str = Field(min_length=1)
    enrollment_status: Literal["full_time", "part_time"]

    # Academic
    degree_level: Literal["undergrad", "masters", "phd", "postdoc"]
    field_of_study: str
    major: str
    minor: str | None = None
    university_name: str
    university_state: str
    gpa: float = Field(ge=0.0)
    gpa_scale: float = Field(gt=0.0)
    gre: float | None = Field(None, ge=0)
    gmat: float | None = Field(None, ge=0)
    toefl: float | None = Field(None, ge=0)
    ielts: float | None = Field(None, ge=0)
    sat: float | None = Field(None, ge=0)
    act: float | None = Field(None, ge=0)
    expected_graduation_year: int = Field(gt=1900, lt=2100)
    previous_degrees: list[str] | None = None

    # Merit
    published_research: bool
    research_papers: list[str] | None = None
    conference_presentations: int = Field(ge=0)
    patents: int = Field(ge=0)
    academic_awards: list[str] = Field(default_factory=list)
    previous_scholarships: list[str] = Field(default_factory=list)

    # Extracurricular
    leadership_roles: list[str] = Field(default_factory=list)
    volunteer_hours: int | None = Field(None, ge=0)
    sports_achievements: list[str] = Field(default_factory=list)
    artistic_achievements: list[str] = Field(default_factory=list)
    entrepreneurship_experience: bool

    # Financial
    financial_need_level: Literal["low", "medium", "high"]
    family_income_bracket: str | None = None
    current_funding_sources: list[str] = Field(default_factory=list)
    dependents: int | None = Field(None, ge=0)

    # Goals
    career_goals: str | None = None
    intended_industry: str | None = None
    willing_to_return_home_country: bool | None = None
    languages: list[str] = Field(default_factory=list)
    preferred_scholarship_types: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_gpa(self) -> 'StudentProfile':
        if self.gpa > self.gpa_scale:
            raise ValueError(f"gpa ({self.gpa}) cannot be greater than gpa_scale ({self.gpa_scale})")
        return self

    def to_feature_vector(self) -> dict[str, object]:
        return {
            "nationality": self.nationality,
            "dual_citizenship": self.dual_citizenship,
            "visa_type": self.visa_type,
            "degree_level": self.degree_level,
            "enrollment_status": self.enrollment_status,
            "field_of_study": self.field_of_study,
            "major": self.major,
            "university_name": self.university_name,
            "university_state": self.university_state,
            "gpa": self.gpa,
            "gpa_scale": self.gpa_scale,
            "gre": self.gre,
            "gmat": self.gmat,
            "toefl": self.toefl,
            "ielts": self.ielts,
            "sat": self.sat,
            "act": self.act,
            "published_research": self.published_research,
            "conference_presentations": self.conference_presentations,
            "patents": self.patents,
            "has_leadership": len(self.leadership_roles) > 0,
            "volunteer_hours": self.volunteer_hours,
            "entrepreneurship_experience": self.entrepreneurship_experience,
            "financial_need_level": self.financial_need_level,
            "dependents": self.dependents,
            "willing_to_return_home_country": self.willing_to_return_home_country,
            "languages": self.languages,
            "preferred_scholarship_types": self.preferred_scholarship_types
        }

    def completeness_score(self) -> float:
        # Check an arbitrary but comprehensive set of fields for completeness.
        fields_to_check = [
            self.full_name, self.date_of_birth, self.gender, self.nationality, 
            self.home_country, self.home_city, self.visa_type, self.enrollment_status,
            self.degree_level, self.field_of_study, self.major, self.university_name,
            self.university_state, self.gpa, self.gpa_scale, self.expected_graduation_year,
            self.financial_need_level, self.family_income_bracket, self.career_goals,
            self.intended_industry
        ]
        
        filled = sum(1 for field in fields_to_check if field is not None and field != "" and field != [])
        return round((filled / len(fields_to_check)) * 100, 1)
