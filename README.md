# InterviewPilot — AI Interview Copilot

A production-grade SaaS application for technical interview preparation. Practice mock interviews (technical, behavioral, system design, HR), get your resume analyzed and rewritten, solve coding problems in an embedded editor with real execution, and receive senior-engineer-level feedback — all powered by the Claude API with adaptive difficulty, session memory, and company-specific interview styles.

![stack](https://img.shields.io/badge/FastAPI-Python%203.11-009688) ![stack](https://img.shields.io/badge/React%2018-TypeScript-3178C6) ![stack](https://img.shields.io/badge/Claude-API-D97757)

## Feature Overview

| Area | What you get |
|---|---|
| **Auth** | Email/password + JWT (access/refresh), Google & GitHub OAuth (env-gated), forgot/reset password, protected routes |
| **Dashboard** | Readiness %, streak, XP/level, weak & strong areas, score trend, recent feedback, recommended topics |
| **Resume Analyzer** | PDF upload → ATS/Recruiter/Technical/Communication/Confidence scores, issue detection, improved resume, cover letter, LinkedIn summary |
| **Interview Plan** | 30-day roadmap, skill-gap analysis, daily/weekly goals, deadline countdown — generated from your resume |
| **AI Mock Interview** | One-question-at-a-time interviewer, follow-ups, adaptive difficulty, challenges wrong answers, never reveals answers early. 20+ tracks (Java → System Design) |
| **Voice Mode** | Browser speech-to-text + text-to-speech, filler-word detection, speaking-pace metrics |
| **Coding Round** | Monaco editor, run Python/JavaScript against visible + hidden test cases, Claude senior-reviewer code review with complexity analysis |
| **AI Coach & Feedback** | Per-answer coaching (good/weak/how FAANG evaluates/ideal answer) + end-of-session report with hiring recommendation |
| **Company Modes** | Google, Amazon, Microsoft, Goldman Sachs, startups, service-based… each with tuned style & difficulty |
| **Analytics** | Score trends, topic mastery, practice frequency, success prediction |
| **Gamification** | XP, levels, badges, daily streaks |
| **Admin** | User/usage analytics, question management (role-gated) |

## Quick Start (local, no Docker)

**Backend** (Python 3.11+):
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt
copy .env.example .env                             # add ANTHROPIC_API_KEY for real AI
python -m app.seed                                 # creates demo data + demo@user.com / Demo@1234
uvicorn app.main:app --reload --port 8002
```

**Frontend** (Node 18+):
```bash
cd frontend
npm install
npm run dev            # http://localhost:5175
```

> **No Claude API key?** The app still fully works — the AI layer falls back to a deterministic `MockAIProvider` so every screen and flow is demoable offline. Set `ANTHROPIC_API_KEY` in `backend/.env` to switch to real Claude.

**Demo login:** `demo@user.com` / `Demo@1234` (created by the seeder). Admin: `admin@user.com` / `Admin@1234`.

## Quick Start (Docker)

```bash
docker compose up --build
# frontend: http://localhost:5175  backend: http://localhost:8002/docs
```

Runs PostgreSQL + Redis + backend + frontend (nginx). Without Docker the backend defaults to SQLite so nothing else is required.

## Documentation

| Doc | Contents |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, clean-architecture layers, component hierarchy, user flows |
| [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Full ER model and table reference |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Every REST endpoint (also live at `/docs` via OpenAPI) |
| [docs/AI_WORKFLOWS.md](docs/AI_WORKFLOWS.md) | Prompt engineering strategy, chains, adaptive difficulty, memory, evaluation |
| [docs/SECURITY.md](docs/SECURITY.md) | Auth design, threat model, code-execution sandboxing |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Docker, AWS, nginx, CI/CD pipeline |
| [docs/TESTING.md](docs/TESTING.md) | Testing strategy & how to run tests |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Future enhancements |

## Repository Layout

```
interview-copilot/
├── backend/            FastAPI app (clean architecture: api → services → repositories → models)
│   ├── app/
│   │   ├── api/v1/     Routers (thin controllers)
│   │   ├── core/       Config, security, dependencies
│   │   ├── db/         Engine/session
│   │   ├── models/     SQLAlchemy ORM
│   │   ├── schemas/    Pydantic DTOs
│   │   ├── repositories/  Data access (repository pattern)
│   │   ├── services/   Business logic
│   │   └── ai/         Provider abstraction, prompts, chains
│   └── tests/
├── frontend/           React 18 + TS + Vite + Tailwind + Redux Toolkit + React Query
│   └── src/
│       ├── api/        Axios client + typed React Query hooks
│       ├── components/ UI kit, layout, charts
│       ├── features/   Voice engine, theme
│       ├── pages/      Route screens
│       └── store/      Redux slices
├── docs/
├── .github/workflows/  CI pipeline
└── docker-compose.yml
```
