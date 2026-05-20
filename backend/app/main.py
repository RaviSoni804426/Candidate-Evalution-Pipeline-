from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, SessionLocal, engine, get_db
from .models import Candidate, CandidateAction, CandidateStatus, JobDescription
from .schemas import (
    ActionResponse,
    BulkEvaluationResponse,
    CandidateRankingResponse,
    CandidateRead,
    DashboardMetrics,
    EvaluationResponse,
    JobDescriptionCreate,
    JobDescriptionRead,
    SeedDataResponse,
    ShortlistRequest,
    UploadResumeResponse,
)
from .services.resume_parser import extract_profile, extract_text_from_path, save_upload
from .services.scoring import score_candidate
from .services.summarizer import generate_summary

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_dir = settings.storage_dir / "resumes"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.storage_dir), name="uploads")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    seed_demo_data()


def serialize_candidate(candidate: Candidate) -> CandidateRead:
    return CandidateRead.model_validate(candidate, from_attributes=True)


def serialize_job(job: JobDescription) -> JobDescriptionRead:
    return JobDescriptionRead.model_validate(job, from_attributes=True)


def _ensure_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item.strip() for item in value if item.strip()]
    if not value.strip():
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [part.strip() for part in value.split(",") if part.strip()]


def _candidate_query(db: Session):
    return select(Candidate).order_by(Candidate.score.desc(), Candidate.created_at.desc())


def _get_latest_job(db: Session) -> JobDescription | None:
    return db.execute(select(JobDescription).order_by(JobDescription.created_at.desc())).scalars().first()


def _candidate_to_response(candidate: Candidate) -> CandidateRead:
    return CandidateRead.model_validate(candidate, from_attributes=True)


def _job_to_response(job: JobDescription) -> JobDescriptionRead:
    return JobDescriptionRead.model_validate(job, from_attributes=True)


def _create_job(db: Session, job_role: str, skills_required: str | list[str] | None, experience_required: str | None, description: str | None) -> JobDescription:
    job = JobDescription(
        id=str(uuid.uuid4()),
        role=job_role,
        skills_required=_ensure_list(skills_required),
        experience_required=experience_required or None,
        description=description,
    )
    db.add(job)
    db.flush()
    return job


async def _build_candidate_from_resume(
    upload: UploadFile,
    job: JobDescription,
    db: Session,
    candidate_name: str | None = None,
    candidate_email: str | None = None,
) -> tuple[Candidate, str, dict[str, float | list[str] | str]]:
    destination = uploads_dir / f"{uuid.uuid4()}-{upload.filename}"
    saved_path = await save_upload(upload, destination)
    resume_text = extract_text_from_path(saved_path)
    profile = extract_profile(resume_text, fallback_name=candidate_name or Path(upload.filename).stem.replace("_", " ").title())
    if candidate_email:
        profile["email"] = candidate_email

    evaluation = score_candidate(resume_text, job.skills_required, job.experience_required)
    summary = await generate_summary(profile, evaluation, job.role, resume_text)

    candidate = Candidate(
        id=str(uuid.uuid4()),
        name=str(profile["name"]),
        email=profile.get("email"),
        job_title=job.role,
        resume_filename=upload.filename,
        resume_url=f"/uploads/resumes/{saved_path.name}",
        resume_text=resume_text,
        skills=profile.get("skills", []),
        experience_years=float(profile.get("experience_years", 0.0)),
        score=float(evaluation["score"]),
        technical_score=float(evaluation["technical_score"]),
        experience_score=float(evaluation["experience_score"]),
        project_score=float(evaluation["project_score"]),
        education_score=float(evaluation["education_score"]),
        summary=summary,
        status=CandidateStatus.new.value,
    )
    db.add(candidate)
    return candidate, resume_text, evaluation


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        demo_resumes = {
            "demo-ravi.txt": "Ravi Kumar\nravi@example.com\nPython SQL machine learning projects. 3 years experience at analytics startup. B.Tech from University.\n",
            "demo-aman.txt": "Aman Singh\naman@example.com\nExcel SQL reporting stakeholder communication. 2 years experience in operations analytics.\n",
            "demo-rahul.txt": "Rahul Jain\nrahul@example.com\nJavaScript React coursework and college projects. Fresh graduate with team collaboration experience.\n",
        }

        for filename, content in demo_resumes.items():
            demo_path = uploads_dir / filename
            if not demo_path.exists():
                demo_path.write_text(content, encoding="utf-8")

        if db.execute(select(func.count()).select_from(JobDescription)).scalar_one() == 0:
            job = JobDescription(
                id=str(uuid.uuid4()),
                role="AI Product Analyst",
                skills_required=["python", "sql", "machine learning", "communication"],
                experience_required="2+ years",
                description="Screen and evaluate candidates for product and AI roles.",
            )
            db.add(job)

        if db.execute(select(func.count()).select_from(Candidate)).scalar_one() == 0:
            demo_candidates = [
                Candidate(
                    id=str(uuid.uuid4()),
                    name="Ravi Kumar",
                    email="ravi@example.com",
                    job_title="Data Analyst",
                    resume_filename="demo-ravi.txt",
                    resume_url="/uploads/resumes/demo-ravi.txt",
                    resume_text="Python SQL machine learning projects. 3 years experience at analytics startup. B.Tech from University.",
                    skills=["python", "sql", "machine learning"],
                    experience_years=3.0,
                    score=89.0,
                    technical_score=92.0,
                    experience_score=85.0,
                    project_score=90.0,
                    education_score=88.0,
                    summary="Strong Python and SQL candidate with relevant ML projects and solid internship exposure.",
                    status=CandidateStatus.shortlisted.value,
                ),
                Candidate(
                    id=str(uuid.uuid4()),
                    name="Aman Singh",
                    email="aman@example.com",
                    job_title="Business Analyst",
                    resume_filename="demo-aman.txt",
                    resume_url="/uploads/resumes/demo-aman.txt",
                    resume_text="Excel, SQL, reporting, stakeholder communication. 2 years experience in operations analytics.",
                    skills=["sql", "excel", "communication"],
                    experience_years=2.0,
                    score=76.0,
                    technical_score=74.0,
                    experience_score=72.0,
                    project_score=78.0,
                    education_score=80.0,
                    summary="Solid analytics exposure with reporting experience and good stakeholder communication.",
                    status=CandidateStatus.hold.value,
                ),
                Candidate(
                    id=str(uuid.uuid4()),
                    name="Rahul Jain",
                    email="rahul@example.com",
                    job_title="Junior Developer",
                    resume_filename="demo-rahul.txt",
                    resume_url="/uploads/resumes/demo-rahul.txt",
                    resume_text="JavaScript React coursework and college projects. Fresh graduate with team collaboration experience.",
                    skills=["javascript", "react"],
                    experience_years=0.5,
                    score=58.0,
                    technical_score=60.0,
                    experience_score=35.0,
                    project_score=62.0,
                    education_score=78.0,
                    summary="Early-career profile with basic React exposure and strong academic projects.",
                    status=CandidateStatus.new.value,
                ),
            ]
            db.add_all(demo_candidates)

        db.commit()
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/candidate-rankings", response_model=CandidateRankingResponse)
def get_candidate_rankings(db: Session = Depends(get_db)) -> CandidateRankingResponse:
    candidates = db.execute(_candidate_query(db)).scalars().all()
    return CandidateRankingResponse(candidates=[_candidate_to_response(candidate) for candidate in candidates])


@app.get("/dashboard-metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)) -> DashboardMetrics:
    total_candidates = db.execute(select(func.count()).select_from(Candidate)).scalar_one()
    shortlisted_count = db.execute(select(func.count()).select_from(Candidate).where(Candidate.status == CandidateStatus.shortlisted.value)).scalar_one()
    rejected_count = db.execute(select(func.count()).select_from(Candidate).where(Candidate.status == CandidateStatus.rejected.value)).scalar_one()
    hold_count = db.execute(select(func.count()).select_from(Candidate).where(Candidate.status == CandidateStatus.hold.value)).scalar_one()
    avg_score = db.execute(select(func.coalesce(func.avg(Candidate.score), 0.0))).scalar_one()
    processed_resumes = db.execute(select(func.count()).select_from(Candidate).where(Candidate.resume_filename.is_not(None))).scalar_one()
    shortlist_rate = (shortlisted_count / total_candidates * 100.0) if total_candidates else 0.0
    return DashboardMetrics(
        total_candidates=total_candidates,
        shortlisted_count=shortlisted_count,
        rejected_count=rejected_count,
        hold_count=hold_count,
        average_score=round(float(avg_score or 0.0), 2),
        processed_resumes=processed_resumes,
        shortlist_rate=round(shortlist_rate, 2),
    )


@app.get("/job-descriptions/latest", response_model=JobDescriptionRead | None)
def get_latest_job_description(db: Session = Depends(get_db)):
    job = _get_latest_job(db)
    return _job_to_response(job) if job else None


@app.post("/job-descriptions", response_model=JobDescriptionRead)
def create_job_description(payload: JobDescriptionCreate, db: Session = Depends(get_db)) -> JobDescriptionRead:
    job = _create_job(db, payload.role, payload.skills_required, payload.experience_required, payload.description)
    db.commit()
    db.refresh(job)
    return _job_to_response(job)


@app.post("/upload-resume", response_model=UploadResumeResponse)
async def upload_resume(resume: UploadFile = File(...)) -> UploadResumeResponse:
    destination = uploads_dir / f"{uuid.uuid4()}-{resume.filename}"
    saved_path = await save_upload(resume, destination)
    extracted_text = extract_text_from_path(saved_path)
    profile = extract_profile(extracted_text, fallback_name=Path(resume.filename).stem.replace("_", " ").title())
    return UploadResumeResponse(extracted_text=extracted_text, profile=profile)


@app.post("/evaluate-candidate", response_model=EvaluationResponse)
async def evaluate_candidate(
    resume: UploadFile = File(...),
    job_role: str = Form(...),
    skills_required: str = Form(""),
    experience_required: str = Form(""),
    candidate_name: str | None = Form(None),
    candidate_email: str | None = Form(None),
    db: Session = Depends(get_db),
) -> EvaluationResponse:
    job = _create_job(db, job_role, skills_required, experience_required or None, None)
    candidate, resume_text, evaluation = await _build_candidate_from_resume(resume, job, db, candidate_name, candidate_email)
    db.commit()
    db.refresh(candidate)
    db.refresh(job)

    return EvaluationResponse(
        candidate=_candidate_to_response(candidate),
        job_description=_job_to_response(job),
        extracted_text=resume_text,
        match_breakdown={
            "final_score": float(evaluation["score"]),
            "technical_score": float(evaluation["technical_score"]),
            "experience_score": float(evaluation["experience_score"]),
            "project_score": float(evaluation["project_score"]),
            "education_score": float(evaluation["education_score"]),
            "communication_score": float(evaluation["communication_score"]),
        },
    )


@app.post("/bulk-evaluate-candidates", response_model=BulkEvaluationResponse)
async def bulk_evaluate_candidates(
    resumes: list[UploadFile] = File(...),
    job_role: str = Form(...),
    skills_required: str = Form(""),
    experience_required: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
) -> BulkEvaluationResponse:
    if not resumes:
        raise HTTPException(status_code=400, detail="At least one resume file is required")

    job = _create_job(db, job_role, skills_required, experience_required or None, description or None)
    candidates: list[Candidate] = []

    for resume in resumes:
      candidate, _, _ = await _build_candidate_from_resume(resume, job, db)
      candidates.append(candidate)

    db.commit()
    for candidate in candidates:
        db.refresh(candidate)
    db.refresh(job)

    ranked_candidates = sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
    return BulkEvaluationResponse(
        job_description=_job_to_response(job),
        candidates=[_candidate_to_response(candidate) for candidate in ranked_candidates],
        uploaded_count=len(ranked_candidates),
    )


@app.post("/shortlist-candidate", response_model=ActionResponse)
def shortlist_candidate(payload: ShortlistRequest, db: Session = Depends(get_db)) -> ActionResponse:
    candidate = db.get(Candidate, str(payload.candidate_id))
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.status = payload.status
    db.add(
        CandidateAction(
            candidate_id=candidate.id,
            action=payload.status,
            note=payload.note,
        )
    )
    db.commit()
    return ActionResponse(candidate_id=payload.candidate_id, status=payload.status, message="Candidate status updated")


@app.get("/dashboard")
def dashboard_snapshot(db: Session = Depends(get_db)) -> JSONResponse:
    candidates = db.execute(_candidate_query(db)).scalars().all()
    latest_job = _get_latest_job(db)
    metrics = get_dashboard_metrics(db)
    return JSONResponse(
        {
            "metrics": metrics.model_dump(mode="json"),
            "latest_job": jsonable_encoder(_job_to_response(latest_job)) if latest_job else None,
            "candidates": [jsonable_encoder(serialize_candidate(candidate)) for candidate in candidates],
        }
    )
