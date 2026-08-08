from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.openai_analysis import AIAnalysisError, analyze_profile_with_ai

ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"]
ALLOWED_ORIGIN_REGEX = r"http://(localhost|127\.0\.0\.1)(:\d+)?$"


class AnalyzeRequest(BaseModel):
    cv_text: str = Field(min_length=1, max_length=20000)
    job_description: str = Field(min_length=1, max_length=20000)


class AnalyzeResponse(BaseModel):
    match_score: int
    recommendation: str
    matching_skills: list[str]
    missing_skills: list[str]
    weak_skills: list[str]
    experience_gaps: list[str]
    strengths: list[str]
    reasoning: list[str]
    learning_recommendations: list[str]
    profile_summary: list[str]
    technologies: list[str]
    experience_years: int
    education: list[str]


app = FastAPI(title="Career Agent MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = analyze_profile_with_ai(
            cv_text=request.cv_text,
            job_description=request.job_description,
        )
    except AIAnalysisError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail="Analysis failed") from exc

    return AnalyzeResponse(
        match_score=result.match_score,
        recommendation=result.recommendation,
        matching_skills=result.matching_skills,
        missing_skills=result.missing_skills,
        weak_skills=result.weak_skills,
        experience_gaps=result.experience_gaps,
        strengths=result.strengths,
        reasoning=result.reasoning,
        learning_recommendations=result.learning_recommendations,
        profile_summary=result.profile_summary,
        technologies=result.technologies,
        experience_years=result.experience_years,
        education=result.education,
    )
