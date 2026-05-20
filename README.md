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

## Go Live Steps

### 1. Prepare the backend for production
1. Create a PostgreSQL database on Supabase, Neon, or Render.
2. Set `DATABASE_URL` to the hosted Postgres connection string.
3. Set `API_CORS_ORIGINS` to your deployed frontend URL, for example `https://your-app.vercel.app`.
4. Set `GROQ_API_KEY` if you want AI summaries powered by Groq in production.
5. Set `STORAGE_DIR` to a writable path on the host, or switch to object storage later if you want persistent file storage.

### 2. Deploy the backend
1. Push the repo to GitHub.
2. Deploy the `backend/` app on Render, Railway, Fly.io, or a similar Python host.
3. Use this start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
```

4. Confirm the backend health endpoint returns `{"status":"ok"}`.

### 3. Deploy the frontend
1. Deploy `frontend/` on Vercel.
2. Set `VITE_API_BASE_URL` to your live backend URL, for example `https://your-backend.onrender.com`.
3. Build command: `npm run build`
4. Output directory: `dist`

### 4. Final checks before sharing
1. Open the live frontend URL.
2. Save a job description.
3. Bulk upload multiple resumes.
4. Verify the ranking table shows scores beside each candidate.
5. Verify resume files open correctly from the live backend.

### 5. Recommended production split
- Frontend: Vercel
- Backend: Render or Railway
- Database: Supabase or Neon PostgreSQL
- Resume storage: cloud storage if you need persistence across restarts

### One-Click Deployment

**Backend (Render):**
1. Push your repo to GitHub.
2. Go to [render.com](https://render.com) and create a new Blueprint deployment.
3. Connect your GitHub repo and point to the `render.yaml` in the root.
4. Render will auto-create the PostgreSQL database and deploy the backend.
5. After deployment, copy the live backend URL and use it for `VITE_API_BASE_URL` on Vercel.

**Frontend (Vercel):**
1. Go to [vercel.com](https://vercel.com) and create a new project.
2. Import your GitHub repo.
3. Set the root directory to `frontend/`.
4. Add environment variable `VITE_API_BASE_URL` with your live Render backend URL.
5. Deploy. Vercel will use settings from `vercel.json` automatically.

## Notes
- The backend seeds a few demo candidates and a sample job description on first run so the dashboard is usable immediately.
- The AI summary layer falls back to a deterministic heuristic summary if no external LLM key is configured.
