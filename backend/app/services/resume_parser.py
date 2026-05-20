from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from docx import Document
from pypdf import PdfReader


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
NAME_HINT_RE = re.compile(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})$")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}")
YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", re.IGNORECASE)
SKILL_CANDIDATES = [
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
    "git",
    "linux",
    "rest api",
    "api",
    "postgresql",
    "mysql",
    "excel",
    "power bi",
    "communication",
    "leadership",
    "problem solving",
]


def _read_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _read_docx(file_path: Path) -> str:
    document = Document(str(file_path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_text_from_path(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(file_path)
    if suffix in {".doc", ".docx"}:
        return _read_docx(file_path)
    return file_path.read_text(encoding="utf-8", errors="ignore")


async def save_upload(upload: UploadFile, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = await upload.read()
    destination.write_bytes(content)
    await upload.close()
    return destination


def extract_profile(text: str, fallback_name: str | None = None) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)

    name = fallback_name or "Candidate"
    for line in lines[:8]:
        if NAME_HINT_RE.match(line) and not EMAIL_RE.search(line):
            name = line
            break

    if name == "Candidate" and email:
        name = email.group(0).split("@")[0].replace(".", " ").replace("_", " ").title()

    experience_years = 0.0
    for match in YEARS_RE.findall(text):
        experience_years = max(experience_years, float(match))

    lower_text = text.lower()
    skills = [skill for skill in SKILL_CANDIDATES if skill in lower_text]

    project_lines = [line for line in lines if any(keyword in line.lower() for keyword in ["project", "built", "developed", "designed", "implemented"])]
    education_lines = [line for line in lines if any(keyword in line.lower() for keyword in ["bachelor", "master", "b.tech", "btech", "m.tech", "mba", "phd", "degree", "university", "college"])]

    return {
        "name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "skills": skills,
        "experience_years": experience_years,
        "project_snippets": project_lines[:5],
        "education_snippets": education_lines[:5],
        "text_length": len(text),
    }
