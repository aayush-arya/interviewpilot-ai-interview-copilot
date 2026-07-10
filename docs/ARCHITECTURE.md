# Architecture

## 1. System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│  Browser (React SPA)                                               │
│  React Query cache · Redux (auth/ui) · Web Speech API (voice)      │
└──────────────┬─────────────────────────────────────────────────────┘
               │ HTTPS (JWT Bearer)
┌──────────────▼─────────────────────────────────────────────────────┐
│  nginx (static SPA + /api reverse proxy)                           │
└──────────────┬─────────────────────────────────────────────────────┘
┌──────────────▼─────────────────────────────────────────────────────┐
│  FastAPI  /api/v1                                                  │
│  ┌──────────┐ ┌───────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ Routers  │→│ Services  │→│ Repositories │→│ SQLAlchemy ORM   │  │
│  └──────────┘ └─────┬─────┘ └──────────────┘ └────────┬─────────┘  │
│                     │                                 │            │
│              ┌──────▼──────┐                   ┌──────▼─────────┐  │
│              │ AI Provider │                   │ PostgreSQL /   │  │
│              │ (Claude/    │                   │ SQLite (dev)   │  │
│              │  Mock)      │                   └────────────────┘  │
│              └──────┬──────┘   ┌────────────┐  ┌────────────────┐  │
│                     │          │ Code Runner│  │ Redis (cache/  │  │
│              Claude API        │ (sandboxed │  │ rate limits,   │  │
│                                │ subprocess)│  │ optional)      │  │
│                                └────────────┘  └────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## 2. Clean Architecture Layers

Dependencies point inward only. Outer layers depend on inner abstractions, never the reverse.

| Layer | Location | Responsibility | Depends on |
|---|---|---|---|
| **API (interface)** | `app/api/v1/*` | HTTP concerns: routing, status codes, DTO validation | Services, Schemas |
| **Services (use-cases)** | `app/services/*` | Business rules: interview flow, scoring, gamification | Repositories, AI abstraction |
| **Repositories (data access)** | `app/repositories/*` | Query encapsulation; the only layer that touches the ORM session | Models |
| **Domain models** | `app/models/*` | Entities and relationships | Nothing above |
| **Infrastructure** | `app/ai/*`, `app/core/*`, `app/db/*` | Claude client, config, security, engine | External services |

**SOLID in practice**
- *SRP*: each service owns one aggregate (e.g. `InterviewService` never touches resumes).
- *OCP/DIP*: `AIProvider` is an abstract base; `ClaudeProvider` and `MockAIProvider` are drop-in implementations selected by DI (`get_ai_provider`). Services receive it as a constructor argument — no service imports the Anthropic SDK.
- *LSP*: `MockAIProvider` honors the same contract (JSON-mode responses validated by the same schemas), which is what makes offline demo mode and deterministic tests possible.
- *ISP*: repositories expose narrow, intent-named methods (`get_recent_reports`, `top_weak_topics`) instead of a generic query surface.

## 3. AI Mock-Interview Flow (the core loop)

```
POST /interviews            → InterviewService.start()
   builds system prompt from: track + company style + difficulty + resume summary
   Claude generates Q1 → stored as InterviewTurn(index=0)

POST /interviews/{id}/answer → InterviewService.answer()
   1. COACH CHAIN   : evaluate answer → {score, good, weak, faang_view, ideal_answer}
   2. ADAPTIVE STEP : rolling avg of last 2 scores → raise/lower difficulty
   3. INTERVIEWER   : full transcript replayed as conversation memory →
                      follow-up question (challenges wrong answers, never reveals solutions)
   4. GAMIFICATION  : XP award, streak update

POST /interviews/{id}/finish → FeedbackService.generate_report()
   whole transcript + per-turn coach scores → synthesis chain →
   FeedbackReport {overall, communication, confidence, technical accuracy,
                   problem solving, hiring recommendation, strengths, improvements}
```

Conversation memory = the persisted transcript replayed into the Claude `messages` array each turn; resume-awareness = a compact resume digest injected into the interviewer system prompt when available.

## 4. Component Hierarchy (frontend)

```
App
├── Providers (Redux → QueryClient → Router → ThemeProvider)
├── Public: Landing, Login, Register, ForgotPassword, ResetPassword
└── ProtectedRoute → AppShell (Sidebar + Topbar + <Outlet/>)
    ├── DashboardPage      StatCard·ReadinessRing·TrendChart·WeakAreas·RecentFeedback
    ├── ResumePage         UploadDropzone·ScoreBars·IssueList·GeneratedDocs tabs
    ├── PlanPage           CountdownBanner·RoadmapTimeline·WeeklyGoals
    ├── InterviewSetupPage TrackGrid·CompanyPicker·DifficultySelector
    ├── InterviewRoomPage  ChatThread·CoachPanel·VoiceControls(useVoice)
    ├── CodingPage         ProblemList → CodingRoomPage(MonacoEditor·TestResults·AIReview)
    ├── FeedbackPage       ReportList → FeedbackDetail(ScoreRadar·Recommendation)
    ├── AnalyticsPage      TrendChart·TopicMastery·PracticeHeatline·Prediction
    ├── CompaniesPage      CompanyCards → launches company-tuned setup
    ├── SettingsPage       Profile·TargetRole·Deadline·Theme
    └── AdminPage          UsersTable·UsageStats (role-gated)
```

## 5. Key User Flows

**New user:** Register → upload resume → analyzer scores it → "Generate my plan" → 30-day roadmap → dashboard recommends first interview → mock interview → feedback report → analytics update → streak/XP awarded.

**Daily practice:** Login (streak++) → dashboard shows weakest topic → one mock or coding round → coach feedback per answer → report → readiness % recomputed.

## 6. Design Decisions & Trade-offs

| Decision | Rationale |
|---|---|
| Turn-based REST instead of WebSocket streaming for interview turns | Simpler failure semantics, resumable sessions, trivially testable. Streaming is an additive upgrade (documented in ROADMAP). |
| SQLite default / PostgreSQL in Docker & prod | Zero-friction local dev; SQLAlchemy makes the swap a URL change. |
| Voice in the browser (Web Speech API) | Zero server cost/latency; STT+TTS quality is good in Chromium. Server-side Whisper is a roadmap item. |
| `MockAIProvider` fallback | App is fully demoable and CI-testable without API keys or spend. |
| Code runner = sandboxed subprocess (timeout, temp cwd, no network flag) | Right-sized for a single-tenant deployment; SECURITY.md documents the Docker-per-run / Judge0 upgrade path for multi-tenant prod. |
| Question retrieval: seeded bank + AI generation, ChromaDB interface stubbed behind `QuestionSource` | RAG adds ops burden; the abstraction point exists so a vector store can be added without touching services. |
