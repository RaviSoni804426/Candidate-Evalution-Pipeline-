from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .models import CandidateStatus


class JobDescriptionCreate(BaseModel):
    role: str = Field(min_length=2, max_length=200)
    skills_required: list[str] = Field(default_factory=list)
    experience_required: str | None = None
    description: str | None = None


class JobDescriptionRead(JobDescriptionCreate):
    id: UUID
    created_at: datetime


class CandidateRead(BaseModel):
    id: UUID
    name: str
    email: str | None = None
    job_title: str | None = None
    resume_filename: str | None = None
    resume_url: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: float = 0.0
    score: float = 0.0
    technical_score: float = 0.0
    experience_score: float = 0.0
    project_score: float = 0.0
    education_score: float = 0.0
    summary: str | None = None
    status: CandidateStatus
    created_at: datetime
    updated_at: datetime


class EvaluationResponse(BaseModel):
    candidate: CandidateRead
    job_description: JobDescriptionRead | None = None
    extracted_text: str
    match_breakdown: dict[str, float]


class BulkEvaluationResponse(BaseModel):
    job_description: JobDescriptionRead | None = None
    candidates: list[CandidateRead]
    uploaded_count: int


class UploadResumeResponse(BaseModel):
    extracted_text: str
    profile: dict[str, object]


class CandidateRankingResponse(BaseModel):
    candidates: list[CandidateRead]


class ShortlistRequest(BaseModel):
    candidate_id: UUID
    status: Literal["shortlisted", "rejected", "hold"]
    note: str | None = None


class ActionResponse(BaseModel):
    candidate_id: UUID
    status: str
    message: str


class DashboardMetrics(BaseModel):
    total_candidates: int
    shortlisted_count: int
    rejected_count: int
    hold_count: int
    average_score: float
    processed_resumes: int
    shortlist_rate: float


class SeedDataResponse(BaseModel):
    seeded_candidates: int
    seeded_job_descriptions: int
