from app.services.analysis import analyze_profile_against_job


def test_returns_structured_result_with_recommendation() -> None:
    cv_text = """
    Senior Python developer with 6 years of experience in FastAPI, Docker, PostgreSQL,
    and cloud deployment. Built internal tools and APIs for fintech startups.
    """
    job_description = """
    We are hiring a backend engineer with strong Python, FastAPI, SQL, and cloud experience.
    Experience with Kubernetes and distributed systems is preferred.
    """

    result = analyze_profile_against_job(cv_text=cv_text, job_description=job_description)

    assert result.match_score >= 50
    assert result.recommendation in {"APPLY", "MAYBE", "SKIP"}
    assert result.matching_skills
    assert result.missing_skills
    assert result.reasoning
    assert result.learning_recommendations
