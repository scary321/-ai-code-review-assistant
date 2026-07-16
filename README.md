# Codestand — AI Code Review Assistant

A full-stack code review tool: upload a Python file or zipped project, and it
runs static analysis (pylint), security scanning (bandit), complexity checks
(radon), and an AI review pass (OpenAI) — then scores the submission,
summarizes it, and generates a downloadable PDF report.

Built exactly to the stack and structure specified in the project brief.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite) |
| Styling | Tailwind CSS |
| Backend | Flask |
| API Framework | Flask Blueprints |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Authentication | Flask-JWT-Extended |
| Password Hashing | Bcrypt |
| AI Integration | OpenAI API |
| Static Analysis | Pylint, Bandit, Radon |
| File Upload | Flask + Werkzeug |
| PDF Reports | ReportLab |
| Deployment | Render (backend) / Vercel (frontend) |

## Project Structure

```
ai-code-review/
├── backend/
│   ├── app.py                  # Flask app factory + entrypoint
│   ├── config.py               # Env-driven configuration
│   ├── extensions.py           # db / bcrypt / jwt / cors singletons
│   ├── requirements.txt
│   ├── render.yaml             # Render deployment blueprint
│   ├── models/
│   │   ├── user.py
│   │   ├── project.py
│   │   └── review.py           # Review + ReviewFinding
│   ├── routes/
│   │   ├── auth.py             # register / login / me
│   │   ├── upload.py           # project upload + listing
│   │   ├── review.py           # trigger + fetch reviews
│   │   └── report.py           # PDF generation + download
│   ├── services/
│   │   ├── openai_service.py       # AI review pass
│   │   ├── pylint_service.py       # style/correctness analysis
│   │   ├── bandit_service.py       # security analysis
│   │   ├── radon_service.py        # complexity/maintainability
│   │   └── documentation_service.py # AI-written review summary
│   ├── utils/
│   │   ├── file_utils.py       # safe upload/zip handling
│   │   └── scoring.py          # weighted score formula
│   ├── uploads/                # uploaded project files (gitignored)
│   └── reports/                # generated PDFs (gitignored)
│
└── frontend/
    ├── src/
    │   ├── components/         # Navbar, ScoreGauge, FindingRow, UploadPanel...
    │   ├── pages/               # Login, Register, Dashboard, ProjectDetail
    │   ├── services/api.js      # fetch wrapper for the Flask API
    │   ├── hooks/useAuth.jsx    # auth context (JWT in localStorage)
    │   └── assets/
    ├── vercel.json
    └── tailwind.config.js
```

## Database Design

**users** — id, name, email, password_hash, created_at
**projects** — id, user_id, project_name, upload_type, created_at
**reviews** — id, project_id, review_score, summary, created_at
**review_findings** — id, review_id, severity, issue, explanation, suggestion, file_name, line_number

(`storage_path` was added to `projects` — the on-disk folder holding the
uploaded files — since the analysis pipeline needs to locate them.)

## How a review works

1. User uploads a `.py` file or a `.zip` (only `.py` files are extracted, with
   Zip-Slip protection).
2. `POST /api/review/<project_id>/run` walks every `.py` file and runs, per file:
   - **pylint** → style/correctness issues
   - **bandit** → security issues (hardcoded secrets, `shell=True`, weak hashes, etc.)
   - **radon** → cyclomatic complexity + maintainability index
   - **OpenAI** → design smells, logic bugs, and issues static tools miss
3. All findings are normalized to one shape (`severity`, `issue`, `explanation`,
   `suggestion`, `file_name`, `line_number`, `source`) and stored.
4. A weighted, damped scoring formula (`utils/scoring.py`) converts findings
   into a 0–100 score so a handful of critical issues hurts more than dozens
   of minor style nits, without ever zeroing out.
5. An AI-written (or rule-based fallback) summary is generated and stored
   alongside the score.
6. The PDF report (ReportLab) renders the score, summary, and a findings
   table, downloadable from the project page.

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ running locally (or a connection string to a hosted instance)
- An OpenAI API key (optional — the app degrades gracefully without one; you
  just lose the AI-review findings and get a rule-based summary instead)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

createdb ai_code_review                                # or use an existing Postgres DB

cp .env.example .env
# edit .env: set DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY, OPENAI_API_KEY

python app.py                                          # runs on http://localhost:5000
```

Tables are created automatically on first run via `db.create_all()`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env      # set VITE_API_URL if your backend isn't on localhost:5000
npm run dev                # runs on http://localhost:5173
```

Open `http://localhost:5173`, register an account, and upload a `.py` file to
try the full pipeline.

## Deployment

### Backend → Render
`backend/render.yaml` is a full Render Blueprint: it provisions a free
Postgres instance and a web service running
`gunicorn app:app --bind 0.0.0.0:$PORT`. In the Render dashboard:
1. New → Blueprint → point at this repo.
2. Set `CORS_ORIGINS` to your deployed Vercel URL and `OPENAI_API_KEY` (both
   marked `sync: false` in the blueprint so Render prompts for them).
3. Deploy — `SECRET_KEY`/`JWT_SECRET_KEY` are auto-generated.

### Frontend → Vercel
1. New Project → import the `frontend/` directory.
2. Framework preset: Vite.
3. Set `VITE_API_URL` to your Render backend URL.
4. Deploy — `vercel.json` handles SPA routing so React Router refreshes don't 404.

## API Reference

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create account, returns JWT |
| POST | `/api/auth/login` | Returns JWT |
| GET | `/api/auth/me` | Current user (requires auth) |
| POST | `/api/upload` | Upload a `.py`/`.zip`, creates a project |
| GET | `/api/upload` | List the current user's projects |
| POST | `/api/review/<project_id>/run` | Run the full analysis pipeline |
| GET | `/api/review/<project_id>` | List past reviews for a project |
| GET | `/api/review/detail/<review_id>` | Full review + findings |
| POST | `/api/report/<review_id>/generate` | Build the PDF |
| GET | `/api/report/<review_id>/download` | Download the PDF |

All routes except register/login/health require `Authorization: Bearer <token>`.

## Notes on what was verified

The backend pipeline was tested end-to-end in a local run (register → login →
upload a deliberately messy sample file → run review → generate + download
PDF): pylint, bandit, and radon all fired correctly against real code, the
scoring formula produced a sane 0–100 result, and the PDF rendered as a valid
document. The frontend was built and compiled cleanly with Vite.
PostgreSQL itself wasn't available in the build sandbox, so the smoke test
ran against SQLite via `DATABASE_URL` — the code path is identical for
Postgres since both go through the same SQLAlchemy engine; just point
`DATABASE_URL` at your Postgres instance to use it for real.
