from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class MatchResult:
    match_score: int
    recommendation: str
    matching_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    weak_skills: List[str] = field(default_factory=list)
    experience_gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    learning_recommendations: List[str] = field(default_factory=list)
    profile_summary: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    experience_years: int = 0
    education: List[str] = field(default_factory=list)


SKILL_KEYWORDS = {
    "python": {"python", "django", "flask", "fastapi"},
    "sql": {"sql", "postgres", "postgresql", "database", "mysql"},
    "cloud": {"cloud", "aws", "azure", "gcp", "docker", "kubernetes"},
    "backend": {"backend", "api", "microservices", "server", "engineering"},
    "testing": {"testing", "pytest", "unittest", "tdd"},
    "devops": {"devops", "ci", "cd", "deployment", "infrastructure"},
}

EXPERIENCE_CUES = {
    "senior": 2,
    "lead": 2,
    "years": 1,
    "year": 1,
    "experience": 1,
    "built": 1,
    "developed": 1,
    "designed": 1,
    "implemented": 1,
}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _extract_keywords(text: str) -> set[str]:
    normalized = _normalize(text)
    if not normalized:
        return set()
    return {token for token in normalized.split() if len(token) >= 3}


def _find_matching_skills(cv_text: str, job_text: str) -> tuple[list[str], list[str], list[str]]:
    cv_keywords = _extract_keywords(cv_text)
    job_keywords = _extract_keywords(job_text)

    matching: list[str] = []
    missing: list[str] = []
    weak: list[str] = []

    for skill, aliases in SKILL_KEYWORDS.items():
        if aliases & cv_keywords:
            matching.append(skill)
        elif skill in job_keywords or aliases & job_keywords:
            missing.append(skill)

    for skill in missing:
        if skill in {"cloud", "devops"}:
            weak.append(skill)

    return sorted(set(matching)), sorted(set(missing)), sorted(set(weak))


def _estimate_experience(text: str) -> int:
    normalized = _normalize(text)
    if not normalized:
        return 0

    score = 0
    for cue, weight in EXPERIENCE_CUES.items():
        if cue in normalized:
            score += weight

    years_matches = re.findall(r"\b(\d+)\s+years?\b", normalized)
    if years_matches:
        score += min(3, int(years_matches[0]) // 2)

    return min(score, 6)


def _extract_profile_details(text: str) -> tuple[list[str], int, list[str]]:
    normalized = _normalize(text)
    if not normalized:
        return [], 0, []

    technologies = []
    if "fastapi" in normalized:
        technologies.append("FastAPI")
    if "docker" in normalized:
        technologies.append("Docker")
    if "postgres" in normalized or "postgresql" in normalized:
        technologies.append("PostgreSQL")
    if "python" in normalized:
        technologies.append("Python")
    if "aws" in normalized or "azure" in normalized:
        technologies.append("Cloud")

    experience_years = 0
    years_matches = re.findall(r"\b(\d+)\s+years?\b", normalized)
    if years_matches:
        experience_years = int(years_matches[0])

    education = []
    if "bachelor" in normalized or "master" in normalized:
        if "bachelor" in normalized:
            education.append("Bachelor's degree")
        if "master" in normalized:
            education.append("Master's degree")

    return technologies, experience_years, education


def analyze_profile_against_job(cv_text: str, job_description: str) -> MatchResult:
    matching_skills, missing_skills, weak_skills = _find_matching_skills(cv_text, job_description)
    candidate_experience = _estimate_experience(cv_text)
    technologies, experience_years, education = _extract_profile_details(cv_text)
    job_experience = 3

    score = 45
    score += min(25, len(matching_skills) * 6)
    score += min(15, max(0, candidate_experience - job_experience) * 3)

    if not missing_skills:
        score += 10
    elif len(missing_skills) <= 2:
        score += 5

    if candidate_experience >= job_experience:
        score += 5

    score = max(0, min(score, 95))

    recommendation = "APPLY"
    if score < 60:
        recommendation = "SKIP"
    elif score < 75:
        recommendation = "MAYBE"

    strengths = []
    if "python" in matching_skills:
        strengths.append("Strong Python-related experience")
    if "backend" in matching_skills:
        strengths.append("Backend engineering experience is evident")
    if "sql" in matching_skills:
        strengths.append("Database experience is present")

    reasoning = [
        "The profile shows overlap with several core job capabilities.",
        "The candidate appears to have practical backend experience and relevant tooling exposure.",
        "The main risks are around skills the description emphasizes more strongly than the current profile.",
    ]

    learning_recommendations = []
    if "cloud" in missing_skills or "devops" in missing_skills:
        learning_recommendations.append("Strengthen cloud and deployment knowledge")
    if "testing" in missing_skills:
        learning_recommendations.append("Practice automated testing and CI workflows")
    if "sql" in missing_skills:
        learning_recommendations.append("Deepen database design and query skills")

    if not learning_recommendations:
        learning_recommendations.append("Continue building depth in the strongest matched areas")

    profile_summary = []
    if "python" in matching_skills:
        profile_summary.append("Python-focused backend experience")
    if "sql" in matching_skills:
        profile_summary.append("Database and query experience")
    if candidate_experience >= 3:
        profile_summary.append(f"Estimated experience signal: {candidate_experience} / 6")

    return MatchResult(
        match_score=score,
        recommendation=recommendation,
        matching_skills=matching_skills[:8],
        missing_skills=missing_skills[:8],
        weak_skills=weak_skills[:8],
        experience_gaps=[
            "Additional evidence for cloud, deployment, or distributed systems would strengthen the profile"
        ],
        strengths=strengths,
        reasoning=reasoning,
        learning_recommendations=learning_recommendations,
        profile_summary=profile_summary,
        technologies=technologies,
        experience_years=experience_years,
        education=education,
    )
