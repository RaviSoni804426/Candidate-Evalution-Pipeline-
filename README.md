---
title: AI Candidate Evaluation Pipeline
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
# AI Candidate Evaluation Pipeline

End-to-end AI recruitment screening product with a FastAPI backend and a React frontend.

## What it does

- Upload and parse PDF or DOCX resumes
- Capture job description requirements
- Score candidates with transparent heuristics
- Generate recruiter-friendly summaries
- Rank candidates in a dashboard
- Support shortlist, reject, and hold actions

## Project Structure

- `backend/` FastAPI API, data model, parsing, scoring, and summary generation
- `frontend/` React app and dashboard UI
- `AI_Candidate_Evaluation_Pipeline_Blueprint.md` product blueprint

## Local Development

### Backend

1. Create a Python virtual environment.
2. Install dependencies from `backend/requirements.txt`.
3. Run the API:

```bash
uvicorn app.main:app --reload --app-dir backend
```

The backend listens on `http://localhost:8000`.

### Frontend

1. Install dependencies in `frontend/`.
2. Start the UI:

```bash
npm run dev
```

The frontend listens on `http://localhost:5173`.

### API Base URL

If the frontend needs a different backend URL, set `VITE_API_BASE_URL` in `frontend/.env`.

## Environment Variables

- `DATABASE_URL` - defaults to SQLite for local development
- `GROQ_API_KEY` - optional, enables LLM-backed summary generation if available
- `API_CORS_ORIGINS` - comma-separated allowed frontend origins
- `STORAGE_DIR` - local upload storage directory

## Docker + Hugging Face Deployment

This repository is set up to run as a single Docker container that serves both the FastAPI backend and the built React UI.

### 1. Build and test locally

```bash
docker build -t ai-candidate-evaluation-pipeline .
docker run --rm -p 7860:7860 -e PORT=7860 ai-candidate-evaluation-pipeline
```

Open `http://localhost:7860` and confirm the dashboard loads. The health endpoint should still respond at `http://localhost:7860/health`.

### 2. Push to Hugging Face Spaces

1. Create a new Hugging Face Space.
2. Choose `Docker` as the Space SDK.
3. Push this repository to the Space git remote.
4. Add any required secrets in the Space settings, such as `GROQ_API_KEY` or `DATABASE_URL`.
5. Wait for the Space build to finish, then open the Space URL.

### 3. Environment variables for deployment

- `DATABASE_URL` - use a managed PostgreSQL URL if you want persistent data.
- `API_CORS_ORIGINS` - usually not needed for same-origin Docker Spaces, but keep it if you reuse the backend elsewhere.
- `GROQ_API_KEY` - optional, enables AI-backed summaries.
- `STORAGE_DIR` - set a writable path if you want upload persistence across restarts.

### 4. Alternative deploy targets

If you do not want Hugging Face, the same Docker image can be deployed on Render, Fly.io, Railway, or any host that supports container deployments.

### 5. Final checks

1. Open the deployed app.
2. Save a job description.
3. Bulk upload resumes.
4. Verify rankings and resume links work.

## Notes

- The backend seeds a few demo candidates and a sample job description on first run so the dashboard is usable immediately.
- The AI summary layer falls back to a deterministic heuristic summary if no external LLM key is configured.