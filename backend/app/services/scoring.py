from __future__ import annotations

import math
import re
from collections.abc import Iterable

TECH_TERMS = {
    "python",
    "sql",
    "java",
    "javascript",
    "typescript",
    "react",
    "fastapi",
    "django",
    "flask",
    "pandas",
    "numpy",
    "machine learning",
    "nlp",
    "aws",
    "docker",
    "kubernetes",
    "postgresql",
    "mysql",
    "power bi",
    "excel",
    "data analysis",
    "rest api",
    "api",
}

PROJECT_TERMS = {"built", "developed", "designed", "implemented", "created", "deployed", "led"}
EDUCATION_TERMS = {"bachelor", "master", "b.tech", "btech", "m.tech", "mba", "phd", "degree", "university", "college"}
COMMUNICATION_TERMS = {"communicated", "presented", "stakeholder", "collaborated", "team", "led", "client"}


def _normalize_terms(terms: Iterable[str]) -> list[str]:
    normalized = []
    for term in terms:
        cleaned = term.strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return list(dict.fromkeys(normalized))


def _match_terms(text: str, terms: Iterable[str]) -> list[str]:
    lower_text = text.lower()
    matches = []
    for term in _normalize_terms(terms):
        pattern = rf"\b{re.escape(term)}\b"
        if re.search(pattern, lower_text):
            matches.append(term)
    return matches


def estimate_experience_years(text: str) -> float:
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"(?:experience|worked|professional experience).{0,40}?(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]
    candidates = [0.0]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL):
            try:
                candidates.append(float(match))
            except ValueError:
                continue
    return max(candidates)


def _bounded(value: float) -> float:
    return max(0.0, min(100.0, round(value, 2)))


def score_candidate(resume_text: str, required_skills: list[str], experience_required: str | None = None) -> dict[str, float | list[str] | str]:
    skills = _normalize_terms(required_skills)
    matched_skills = _match_terms(resume_text, skills or TECH_TERMS)

    if skills:
        skills_score = (len(matched_skills) / len(skills)) * 100.0
    else:
        skills_score = 55.0 if matched_skills else 30.0

    experience_years = estimate_experience_years(resume_text)
    if experience_required:
        required_match = re.search(r"(\d+(?:\.\d+)?)", experience_required)
        required_years = float(required_match.group(1)) if required_match else 0.0
        if required_years <= 0:
            experience_score = min(100.0, experience_years * 12.0)
        else:
            experience_score = min(100.0, (experience_years / required_years) * 100.0)
    else:
        experience_score = min(100.0, experience_years * 14.0)

    project_hits = len(_match_terms(resume_text, PROJECT_TERMS))
    project_score = _bounded(30.0 + project_hits * 18.0 + len(matched_skills) * 2.0)

    education_hits = len(_match_terms(resume_text, EDUCATION_TERMS))
    education_score = _bounded(35.0 + education_hits * 12.5)

    communication_hits = len(_match_terms(resume_text, COMMUNICATION_TERMS))

    final_score = (
        skills_score * 0.40
        + experience_score * 0.25
        + project_score * 0.20
        + education_score * 0.15
    )

    recommendation = "Strong match" if final_score >= 80 else "Potential fit" if final_score >= 65 else "Needs review"

    return {
        "score": _bounded(final_score),
        "technical_score": _bounded(skills_score),
        "experience_score": _bounded(experience_score),
        "project_score": _bounded(project_score),
        "education_score": _bounded(education_score),
        "communication_score": _bounded(40.0 + communication_hits * 15.0),
        "matched_skills": matched_skills,
        "recommendation": recommendation,
        "experience_years": round(experience_years, 2),
    }
