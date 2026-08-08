import pytest

from app.config import settings
from app.services.openai_analysis import AIAnalysisError, analyze_profile_with_ai


class DummyResponse:
    def __init__(self, text: str) -> None:
        self.output = [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": text,
                    }
                ]
            }
        ]


class DummyOpenAIClient:
    def __init__(self, *args, **kwargs) -> None:
        self.responses = self

    def create(self, *args, **kwargs) -> DummyResponse:
        return DummyResponse(
            "{\"match_score\": 80, \"recommendation\": \"APPLY\", \"matching_skills\": [\"python\", \"fastapi\"], \"missing_skills\": [\"kubernetes\"], \"weak_skills\": [], \"experience_gaps\": [\"cloud deployment depth\"], \"strengths\": [\"strong backend experience\"], \"reasoning\": [\"The candidate has core backend skills\"], \"learning_recommendations\": [\"Learn Kubernetes\"], \"profile_summary\": [\"Experienced Python backend engineer\"], \"technologies\": [\"Python\", \"FastAPI\"], \"experience_years\": 5, \"education\": [\"Bachelor's degree\"]}"
        )


def test_analyze_profile_with_ai_parses_valid_json(monkeypatch) -> None:
    monkeypatch.setattr("app.services.openai_analysis.OpenAI", DummyOpenAIClient)
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(settings, "openai_model", "gpt-4o-mini")
    monkeypatch.setattr(settings, "openai_base_url", None)

    result = analyze_profile_with_ai(
        cv_text="Experienced backend engineer with Python, FastAPI, and PostgreSQL.",
        job_description="Looking for a backend software engineer with Python and cloud experience.",
    )

    assert result.match_score == 80
    assert result.recommendation == "APPLY"
    assert result.matching_skills == ["python", "fastapi"]
    assert result.missing_skills == ["kubernetes"]
    assert result.weak_skills == []
    assert result.experience_gaps == ["cloud deployment depth"]
    assert result.strengths == ["strong backend experience"]
    assert result.reasoning == ["The candidate has core backend skills"]
    assert result.learning_recommendations == ["Learn Kubernetes"]
    assert result.profile_summary == ["Experienced Python backend engineer"]
    assert result.technologies == ["Python", "FastAPI"]
    assert result.experience_years == 5
    assert result.education == ["Bachelor's degree"]


def test_analyze_profile_with_ai_rejects_invalid_json(monkeypatch) -> None:
    class InvalidResponse:
        def __init__(self) -> None:
            self.output = [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "not-json",
                        }
                    ]
                }
            ]

    class InvalidOpenAIClient:
        def __init__(self, *args, **kwargs) -> None:
            self.responses = self

        def create(self, *args, **kwargs) -> InvalidResponse:
            return InvalidResponse()

    monkeypatch.setattr("app.services.openai_analysis.OpenAI", InvalidOpenAIClient)
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(settings, "openai_model", "gpt-4o-mini")
    monkeypatch.setattr(settings, "openai_base_url", None)

    with pytest.raises(AIAnalysisError, match="not valid JSON"):
        analyze_profile_with_ai(
            cv_text="Experienced backend engineer with Python.",
            job_description="Backend engineer role with Python.",
        )
