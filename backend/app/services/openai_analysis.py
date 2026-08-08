from __future__ import annotations

import json
from typing import Any

from openai import OpenAI, OpenAIError

from app.config import settings
from app.schemas.analysis import AnalysisResult


class AIAnalysisError(Exception):
    pass


def _parse_response_text(response: Any) -> str:
    if hasattr(response, "output_text") and response.output_text is not None:
        return response.output_text

    try:
        output_list = response.output
    except AttributeError as exc:
        raise AIAnalysisError("OpenAI response missing output") from exc

    if not output_list:
        raise AIAnalysisError("OpenAI response output is empty")

    first_item = output_list[0]
    if hasattr(first_item, "content") and first_item.content:
        for content_item in first_item.content:
            if getattr(content_item, "type", None) == "output_text":
                return getattr(content_item, "text", "")

    if isinstance(first_item, dict):
        for content_item in first_item.get("content", []):
            if content_item.get("type") == "output_text":
                return content_item.get("text", "")

    raise AIAnalysisError("Unable to parse text from OpenAI response")


def _build_prompt(cv_text: str, job_description: str) -> str:
    return (
        "You are an AI career analysis assistant."
        "\n\n"
        "Analyze the candidate profile and the job description, then return only valid JSON matching exactly the schema below."
        "\n\n"
        "Schema:\n"
        "{\n"
        "  \"match_score\": integer between 0 and 100,\n"
        "  \"recommendation\": \"APPLY\", \"MAYBE\", or \"SKIP\",\n"
        "  \"matching_skills\": array of strings,\n"
        "  \"missing_skills\": array of strings,\n"
        "  \"weak_skills\": array of strings,\n"
        "  \"experience_gaps\": array of strings,\n"
        "  \"strengths\": array of strings,\n"
        "  \"reasoning\": array of strings,\n"
        "  \"learning_recommendations\": array of strings,\n"
        "  \"profile_summary\": array of strings,\n"
        "  \"technologies\": array of strings,\n"
        "  \"experience_years\": integer,\n"
        "  \"education\": array of strings\n"
        "}\n\n"
        "Include the following analysis points:\n"
        "- required skills from the job description,\n"
        "- preferred skills from the job description,\n"
        "- years of experience and how the candidate compares,\n"
        "- responsibilities and project experience,\n"
        "- technologies and domain experience,\n"
        "- transferable skills that increase fit,\n"
        "- an explainable match score and recommendation.\n\n"
        "Respond only with the JSON object and no additional text.\n\n"
        "Candidate profile:\n" + cv_text + "\n\n"
        "Job description:\n" + job_description + "\n"
    )


def analyze_profile_with_ai(cv_text: str, job_description: str) -> AnalysisResult:
    if not settings.openai_api_key:
        raise AIAnalysisError("OpenAI API key not configured")

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        _strict_response_validation=True,
    )

    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=_build_prompt(cv_text, job_description),
            temperature=0.0,
        )
    except OpenAIError as exc:
        raise AIAnalysisError("OpenAI API request failed") from exc

    response_text = _parse_response_text(response)

    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise AIAnalysisError("OpenAI response was not valid JSON") from exc

    try:
        return AnalysisResult.model_validate(payload)
    except Exception as exc:
        raise AIAnalysisError("OpenAI response failed schema validation") from exc
