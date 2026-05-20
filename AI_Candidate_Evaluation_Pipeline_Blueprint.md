# AI Candidate Evaluation Pipeline

## 1. Product Overview

AI Candidate Evaluation Pipeline is an AI-powered recruitment screening system that helps recruiters evaluate resumes, rank candidates, generate concise candidate summaries, and reduce manual screening effort.

### Primary Goals
- Automate resume screening
- Rank candidates against a job description
- Generate AI-based candidate summaries
- Reduce recruiter workload
- Improve hiring speed and consistency

### Target Users
- Recruiters
- Hiring managers
- Talent acquisition teams

---

## 2. Problem Statement

Recruiters spend significant time manually screening resumes, which are often unstructured, inconsistent, and difficult to compare. This leads to slow hiring cycles, inconsistent evaluations, recruiter fatigue, and missed qualified candidates.

This product solves that by automating screening and scoring through an AI evaluation pipeline.

---

## 3. Product Vision

Build a smart hiring assistant that:
- Reads resumes in common formats
- Matches candidates against a job description
- Scores each candidate consistently
- Generates AI summaries and insights
- Supports shortlisting decisions in a recruiter dashboard

---

## 4. Core Features

### 4.1 Resume Upload
Candidates can upload resumes in PDF or DOCX format.

Functionalities:
- Drag-and-drop upload
- Resume parsing
- Candidate profile extraction

### 4.2 Job Description Input
Recruiters can paste:
- Job description
- Required skills
- Experience requirements

### 4.3 AI Resume Evaluation
The system evaluates resumes using:
- Skills match
- Experience match
- Education relevance
- Keyword match
- Project relevance
- Communication indicators

### 4.4 Candidate Scoring
The system generates:
- Match percentage
- Technical score
- Experience score
- Final recommendation

Example ranking output:

| Candidate | Score |
| --- | --- |
| Ravi Kumar | 89% |
| Aman Singh | 76% |
| Rahul Jain | 58% |

### 4.5 AI Summary Generation
The system generates a short recruiter-friendly summary such as:

> Candidate has strong Python and SQL experience with relevant AI projects and internship exposure. Recommended for technical round.

### 4.6 Candidate Dashboard
Recruiters can:
- Filter candidates
- Sort by score
- View resume insights
- Download reports

### 4.7 Shortlisting Workflow
Recruiters can take actions on each candidate:
- Shortlist
- Reject
- Hold

---

## 5. End-to-End Workflow

1. Recruiter uploads a job description
2. Candidate uploads a resume
3. Resume is parsed
4. AI matches candidate profile to the job description
5. Candidate is scored
6. AI summary is generated
7. Candidates are ranked in the dashboard
8. Recruiter makes a decision

---

## 6. Suggested Tech Stack

### Frontend
- React.js
- Tailwind CSS
- Vercel deployment

### Backend
- FastAPI

### AI / NLP Layer
- Groq API
- Sentence Transformers
- spaCy

### Database
- PostgreSQL
- Supabase for managed deployment

### Resume Parsing
- PyPDF2
- pdfplumber
- python-docx

### Deployment
- Frontend: Vercel
- Backend: Render
- Database: Supabase

---

## 7. Recommended UI Pages

### 7.1 Landing Page
- Product introduction
- Value proposition
- Upload CTA

### 7.2 Recruiter Dashboard
- Candidate rankings
- Filters
- Scorecards

### 7.3 Resume Upload Page
- Upload resume
- Upload job description

### 7.4 Candidate Insights Page
- AI summary
- Skills match
- Experience analysis

---

## 8. Database Design

### Candidate Table
| Field | Description |
| --- | --- |
| Candidate ID | Unique identifier |
| Name | Candidate name |
| Email | Candidate email |
| Resume URL | Stored resume location |
| Skills | Extracted skills |
| Experience | Parsed experience summary |
| Score | Final evaluation score |
| Status | Shortlisted, rejected, or hold |

### Job Description Table
| Field | Description |
| --- | --- |
| JD ID | Unique identifier |
| Role | Job title |
| Skills Required | Required skills list |
| Experience Required | Required experience |

---

## 9. AI Evaluation Logic

### Scoring Weights
| Parameter | Weight |
| --- | --- |
| Skills Match | 40% |
| Experience | 25% |
| Projects | 20% |
| Education | 15% |

### Final Score
Final Score = Weighted Score across all evaluation dimensions.

Example calculation:
- Skills Match: 90 x 0.40
- Experience: 80 x 0.25
- Projects: 85 x 0.20
- Education: 70 x 0.15

Final Score = sum of weighted values

---

## 10. Deployment Architecture

Frontend on Vercel sends requests to the backend API on Render. The backend handles parsing, AI evaluation, and candidate ranking. Processed results are stored in Supabase.

Flow:

Frontend (Vercel)
-> Backend API (Render)
-> AI Processing Layer
-> Database (Supabase)

---

## 11. APIs Required

### Resume Upload API
`POST /upload-resume`

Purpose:
- Accept and store candidate resume files
- Trigger resume parsing

### Candidate Evaluation API
`POST /evaluate-candidate`

Purpose:
- Evaluate a candidate against a job description
- Return score, summary, and match breakdown

### Get Rankings API
`GET /candidate-rankings`

Purpose:
- Return candidates sorted by score
- Support filtering and pagination

### Shortlist API
`POST /shortlist-candidate`

Purpose:
- Update candidate status to shortlisted, rejected, or hold

---

## 12. Product Metrics

Track the following metrics:
- Time saved in screening
- Average evaluation speed
- Candidate shortlist rate
- Recruiter usage
- Resume processing count

---

## 13. Suggested MVP Scope

### MVP Includes
- Resume upload
- Job description input
- Resume parsing
- AI scoring
- Candidate summary generation
- Recruiter dashboard
- Candidate shortlisting actions

### Post-MVP Enhancements
- Email notifications
- Interview scheduling integration
- ATS integrations
- Team collaboration features
- Advanced analytics and hiring funnel reports

---

## 14. Risks and Considerations

### Technical Risks
- Poor resume parsing quality on messy PDFs
- Inconsistent scoring due to weak evaluation logic
- Model hallucination in summaries

### Product Risks
- Bias in ranking logic
- Over-reliance on AI scoring
- Recruiter distrust if explanations are unclear

### Mitigation
- Use transparent scoring breakdowns
- Show why a candidate scored highly or poorly
- Keep human review in the loop
- Add validation and testing for parsing and ranking

---

## 15. Execution Roadmap

### Phase 1: Discovery and Design
- Define user stories
- Finalize evaluation criteria
- Design wireframes

### Phase 2: Core Platform
- Build upload flow
- Build job description input
- Implement parsing and storage

### Phase 3: AI Evaluation
- Implement scoring engine
- Generate candidate summaries
- Rank candidates

### Phase 4: Recruiter Experience
- Build dashboard
- Add filters and shortlist workflow
- Add export/reporting features

### Phase 5: Launch and Improve
- Monitor product metrics
- Improve parsing accuracy
- Refine scoring weights

---

## 16. Success Criteria

The project is successful if it:
- Reduces manual screening time
- Improves recruiter throughput
- Produces reliable candidate rankings
- Generates useful summaries
- Supports fast shortlisting decisions

---

## 17. Next Steps

1. Confirm whether this should be built as a prototype, MVP, or production system.
2. Break this blueprint into user stories and sprint tasks.
3. Define the API contract and database schema in more detail.
4. Start implementing the frontend and backend scaffolding.
