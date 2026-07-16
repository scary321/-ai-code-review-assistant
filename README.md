# Codestand — AI Code Review Assistant



##### 🔗 \*\*Live demo:\*\* https://ai-code-review-assistant-jet.vercel.app

##### 🔗 \*\*Backend API:\*\* https://ai-code-review-backend-ycow.onrender.com



> Note: the backend is on Render's free tier, which spins down after 15 minutes of inactivity. The first request after idling may take 30–60 seconds to wake up — that's expected, not a bug.



A full-stack code review tool: upload a Python file or zipped project, and it
runs static analysis (pylint), security scanning (bandit), complexity checks
(radon), and an AI review pass (OpenAI) — then scores the submission,
summarizes it, and generates a downloadable PDF report.

Built exactly to the stack and structure specified in the project brief.

## Tech Stack

|Layer|Technology|
|-|-|
|Frontend|React (Vite)|
|Styling|Tailwind CSS|
|Backend|Flask|
|API Framework|Flask Blueprints|
|ORM|SQLAlchemy|
|Database|PostgreSQL|
|Authentication|Flask-JWT-Extended|
|Password Hashing|Bcrypt|
|AI Integration|OpenAI API|
|Static Analysis|Pylint, Bandit, Radon|
|File Upload|Flask + Werkzeug|
|PDF Reports|ReportLab|
|Deployment|Render (backend) / Vercel (frontend)|

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
│   │   ├── openai\\\_service.py       # AI review pass
│   │   ├── pylint\\\_service.py       # style/correctness analysis
│   │   ├── bandit\\\_service.py       # security analysis
│   │   ├── radon\\\_service.py        # complexity/maintainability
│   │   └── documentation\\\_service.py # AI-written review summary
│   ├── utils/
│   │   ├── file\\\_utils.py       # safe upload/zip handling
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

**users** — id, name, email, password\_hash, created\_at
**projects** — id, user\_id, project\_name, upload\_type, created\_at
**reviews** — id, project\_id, review\_score, summary, created\_at
**review\_findings** — id, review\_id, severity, issue, explanation, suggestion, file\_name, line\_number

(`storage\\\_path` was added to `projects` — the on-disk folder holding the
uploaded files — since the analysis pipeline needs to locate them.)

## How a review works

1. User uploads a `.py` file or a `.zip` (only `.py` files are extracted, with
Zip-Slip protection).
2. `POST /api/review/<project\\\_id>/run` walks every `.py` file and runs, per file:

   * **pylint** → style/correctness issues
   * **bandit** → security issues (hardcoded secrets, `shell=True`, weak hashes, etc.)
   * **radon** → cyclomatic complexity + maintainability index
   * **OpenAI** → design smells, logic bugs, and issues static tools miss
3. All findings are normalized to one shape (`severity`, `issue`, `explanation`,
`suggestion`, `file\\\_name`, `line\\\_number`, `source`) and stored.
4. A weighted, damped scoring formula (`utils/scoring.py`) converts findings
into a 0–100 score so a handful of critical issues hurts more than dozens
of minor style nits, without ever zeroing out.
5. An AI-written (or rule-based fallback) summary is generated and stored
alongside the score.
6. The PDF report (ReportLab) renders the score, summary, and a findings
table, downloadable from the project page.

## Local Setup



> The app is already live at the link above — local setup below is only needed if you want to run it yourself, modify the code, or use your own OpenAI/Groq key instead of the demo instance's.



### Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL 14+ running locally (or a connection string to a hosted instance)
* An OpenAI API key (optional — the app degrades gracefully without one; you
just lose the AI-review findings and get a rule-based summary instead)

### Backend

```bash
cd backend
python -m venv venv \\\&\\\& source venv/bin/activate      # Windows: venv\\\\Scripts\\\\activate
pip install -r requirements.txt

createdb ai\\\_code\\\_review                                # or use an existing Postgres DB

cp .env.example .env
# edit .env: set DATABASE\\\_URL, JWT\\\_SECRET\\\_KEY, SECRET\\\_KEY, OPENAI\\\_API\\\_KEY

python app.py                                          # runs on http://localhost:5000
```

Tables are created automatically on first run via `db.create\\\_all()`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env      # set VITE\\\_API\\\_URL if your backend isn't on localhost:5000
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
2. Set `CORS\\\_ORIGINS` to your deployed Vercel URL and `OPENAI\\\_API\\\_KEY` (both
marked `sync: false` in the blueprint so Render prompts for them).
3. Deploy — `SECRET\\\_KEY`/`JWT\\\_SECRET\\\_KEY` are auto-generated.

### Frontend → Vercel

1. New Project → import the `frontend/` directory.
2. Framework preset: Vite.
3. Set `VITE\\\_API\\\_URL` to your Render backend URL.
4. Deploy — `vercel.json` handles SPA routing so React Router refreshes don't 404.

## API Reference

|Method|Route|Purpose|
|-|-|-|
|POST|`/api/auth/register`|Create account, returns JWT|
|POST|`/api/auth/login`|Returns JWT|
|GET|`/api/auth/me`|Current user (requires auth)|
|POST|`/api/upload`|Upload a `.py`/`.zip`, creates a project|
|GET|`/api/upload`|List the current user's projects|
|POST|`/api/review/<project\\\_id>/run`|Run the full analysis pipeline|
|GET|`/api/review/<project\\\_id>`|List past reviews for a project|
|GET|`/api/review/detail/<review\\\_id>`|Full review + findings|
|POST|`/api/report/<review\\\_id>/generate`|Build the PDF|
|GET|`/api/report/<review\\\_id>/download`|Download the PDF|

All routes except register/login/health require `Authorization: Bearer <token>`.

## Notes on what was verified

The backend pipeline was tested end-to-end in a local run (register → login →
upload a deliberately messy sample file → run review → generate + download
PDF): pylint, bandit, and radon all fired correctly against real code, the
scoring formula produced a sane 0–100 result, and the PDF rendered as a valid
document. The frontend was built and compiled cleanly with Vite.
PostgreSQL itself wasn't available in the build sandbox, so the smoke test
ran against SQLite via `DATABASE\\\_URL` — the code path is identical for
Postgres since both go through the same SQLAlchemy engine; just point
`DATABASE\\\_URL` at your Postgres instance to use it for real.

