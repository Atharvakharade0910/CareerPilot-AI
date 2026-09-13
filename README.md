# CareerPilot AI

**From resume to opportunity — intelligently.**

A Next.js + FastAPI + PostgreSQL career workspace with an evidence-first profile, live Arbeitnow job discovery, persistent saved jobs, Gemini-assisted coaching, local OCR for scanned PDFs, and scheduled mock interviews.

## Try the running application

- App: http://localhost:3010
- Demo workspace: http://localhost:3010/demo
- Register: http://localhost:3010/sign-up
- API documentation: http://127.0.0.1:8010/docs
- API readiness: http://127.0.0.1:8010/api/health

Create your own account; no shared credentials are provided. New accounts have zero jobs and applications. The demo candidate and companies are fictional and never populate a real account.

## Implemented

- Editorial emerald/ivory visual system, self-hosted Geist, responsive sidebar, mobile drawer, light/dark workspace, reduced-motion support, keyboard command palette, Radix dialogs and shadcn button.
- Sign up, sign in, server-side logout and a truthful recovery-unavailable screen.
- Argon2 password hashes; opaque, hashed, revocable 7-day sessions in HttpOnly cookies; origin checks; process-local authentication throttling.
- Five-step onboarding: personal information, PDF/DOCX resume upload, roles, preferences and evidence review.
- Local resume extraction with exact source snippets, categories, confidence, warnings and canonical skill names. DOCX tables are included.
- Reject/accept extracted facts; correct source facts by editing and re-uploading the master resume. No unsupported rewriting or inference of years of experience.
- Private originals, authenticated downloads, immutable resume versions, account-scoped facts and activity logs.
- Profile completeness calculated from four completed setup steps. It is not a hiring score.
- PostgreSQL UUID models, typed API schemas and OpenAPI documentation.

## What the demo means

The `/demo` pages are an interactive product preview. Job filters, job-analysis dialogs, a per-page sample shortlist, theme switching and navigation work. Scores, trends, jobs, readiness and skill frequencies are illustrative fixtures. They are **not live job-market evidence or computed personal matches**. The sample shortlist lasts only while the current workspace component is mounted.

## Local setup

Requires Node.js 20.9+, Python 3.12+, and PostgreSQL. Install dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
# Install the Gemini, OCR, and monitoring dependencies declared by the application.
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit DATABASE_URL with your private database credentials.
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

For the production frontend: `npm run build`, then `npm run start`.

This workspace currently uses an isolated PostgreSQL 18 cluster under the parent workspace's `work/pgdata`, listening only on 127.0.0.1:55432. It does not use or modify the pre-existing PostgreSQL service on 5432. Its generated password is only in the ignored backend `.env`. The database is outside the deliverable folder. To move the project, provision PostgreSQL and configure `.env`; do not expect the local cluster to move with it.

`Start-Local.ps1` starts this configured workspace with hidden processes and verifies ownership of occupied service ports. `Stop-Local.ps1` stops only matching CareerPilot backend/frontend processes. The isolated PostgreSQL cluster can remain available across app restarts.

## Database with Docker

Docker Compose is provided as an alternative. Docker's engine was stopped during development; this deployment route has not been executed.

```powershell
$env:POSTGRES_PASSWORD = 'choose-a-private-password'
docker compose up -d db
# Set the same password in backend/.env, then run Alembic.
```

## Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest ../tests -q
cd ../frontend
npm run typecheck
npm run build
npx playwright test
```

## Daily maintenance checklist

Before opening a pull request or deploying a new build, verify the working tree is clean, run the backend and frontend checks above, and confirm that `backend/.env` is present only on the local machine. Use `Start-Local.ps1` for a local smoke test and `Stop-Local.ps1` when finished. Never paste API keys, database passwords, private resumes, or generated `private/` storage into an issue, commit, or support message.

Backend tests use the configured PostgreSQL database and remove only their own test users and files. Browser tests require the services running; they create a `browser-*` account and are intended for a development/test database. The browser configuration uses installed Edge on Windows, otherwise Playwright Chromium (`npx playwright install chromium`).

See [architecture](docs/ARCHITECTURE.md), [phase roadmap](docs/ROADMAP.md), and [verification](docs/VERIFICATION.md).

## Current boundaries

The core opportunity loop is implemented with curated PostgreSQL jobs plus a keyless Arbeitnow feed, persistent imports, deterministic `weighted-v1` matching, saved jobs and applications. Gemini is available through the backend provider boundary and falls back locally when unavailable. Scanned PDFs use local OCR when Tesseract is installed. Resume review remains mandatory; extraction confidence is not proficiency.

Before public deployment: use HTTPS and secure cookies, a least-privilege database role, private storage ACLs, an external rate limiter, transactional email recovery, isolated document-parsing workers with resource budgets and malware scanning, monitoring, backups and retention controls. The current setup is an interview-ready local foundation, not a publicly hardened production service.
## Gemini and mock interviews

CareerPilot supports Gemini through the official `google-genai` SDK. Set `GEMINI_API_KEY` only in the backend environment; never commit it. The default model is configurable with `GEMINI_MODEL` and currently defaults to `gemini-3.7-flash`. Without a key, the assistant and mock interview evaluator use an honest deterministic local fallback.

Mock interviews are persisted in PostgreSQL and exposed at `/api/mock-interviews`: schedule a future session, start it, answer each question, and complete with per-answer feedback and a score. The local reminder loop is intentionally lightweight; production deployments should run the reminder worker as a separate durable process.
