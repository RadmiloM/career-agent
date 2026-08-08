from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint
from typing import List, Literal


class AnalysisResult(BaseModel):
    match_score: conint(ge=0, le=100)
    recommendation: Literal["APPLY", "MAYBE", "SKIP"]
    matching_skills: List[str]
    missing_skills: List[str]
    weak_skills: List[str]
    experience_gaps: List[str]
    strengths: List[str]
    reasoning: List[str]
    learning_recommendations: List[str]
    profile_summary: List[str]
    technologies: List[str]
    experience_years: int
    education: List[str]

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
