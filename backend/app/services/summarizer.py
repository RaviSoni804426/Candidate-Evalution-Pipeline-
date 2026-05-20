from __future__ import annotations

from typing import Any

import httpx

from ..config import get_settings


def _fallback_summary(profile: dict[str, Any], evaluation: dict[str, Any], job_role: str | None) -> str:
    skills = profile.get("skills") or evaluation.get("matched_skills") or []
    skill_text = ", ".join(skills[:6]) if skills else "relevant technical experience"
    recommendation = evaluation.get("recommendation", "Needs review")
    role_text = job_role or "the role"

    parts = [
        f"Candidate shows {skill_text} aligned to {role_text}.",
        f"Estimated experience: {evaluation.get('experience_years', 0)} years.",
        f"Overall recommendation: {recommendation}.",
    ]
    return " ".join(parts)


async def _groq_summary(profile: dict[str, Any], evaluation: dict[str, Any], job_role: str | None, resume_text: str) -> str:
    settings = get_settings()
    if not settings.groq_api_key:
        return _fallback_summary(profile, evaluation, job_role)

    prompt = f"""
You are helping a recruiter. Write a concise, factual 2-3 sentence summary for this candidate.

Job role: {job_role or 'Unspecified'}
Candidate name: {profile.get('name', 'Candidate')}
Matched skills: {', '.join(evaluation.get('matched_skills', [])) or 'None'}
Estimated experience: {evaluation.get('experience_years', 0)} years
Final score: {evaluation.get('score', 0)}
Recommendation: {evaluation.get('recommendation', 'Needs review')}

Resume text:
{resume_text[:6000]}

Keep it short, recruiter-friendly, and avoid overclaiming.
""".strip()

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": "You write concise recruiting summaries."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(base_url=settings.groq_base_url, timeout=30.0) as client:
        response = await client.post("/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices") or []
        if choices:
            return choices[0]["message"]["content"].strip()

    return _fallback_summary(profile, evaluation, job_role)


async def generate_summary(profile: dict[str, Any], evaluation: dict[str, Any], job_role: str | None, resume_text: str) -> str:
    try:
        return await _groq_summary(profile, evaluation, job_role, resume_text)
    except Exception:
        return _fallback_summary(profile, evaluation, job_role)
