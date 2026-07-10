# API Reference

Base URL: `/api/v1`. Auth: `Authorization: Bearer <access_token>` unless noted. Interactive OpenAPI docs: `http://localhost:8002/docs`.

## Auth (public, rate-limited 10/min)
| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/auth/register` | `{email, password, full_name}` | 201 UserOut · 409 duplicate · 422 weak password |
| POST | `/auth/login` | `{email, password}` | `{access_token, refresh_token}` · 401 |
| POST | `/auth/refresh` | `{refresh_token}` | new token pair · 401 |
| POST | `/auth/forgot-password` | `{email}` | 202 always (no enumeration) |
| POST | `/auth/reset-password` | `{token, new_password}` | 200 · 400 invalid/expired |
| GET | `/auth/oauth/{google\|github}/url` | — | `{url}` · 501 if not configured |
| GET | `/auth/oauth/{provider}/callback?code=` | — | redirect to `FRONTEND_URL/oauth-complete#tokens` |

## Users
| GET | `/users/me` | current profile (UserOut: xp, level, streak, targets) |
|---|---|---|
| PATCH | `/users/me` | update `full_name, target_role, target_company, interview_deadline` |
| GET | `/users/leaderboard` | top-20 by XP with `is_me` flag |

## Resumes (rate-limited 5/5min)
| POST | `/resumes/analyze` | multipart `file` (PDF ≤5 MB) → scores, analysis (issues/gaps), improved resume, cover letter, LinkedIn summary. 413/415/422 on bad input |
|---|---|---|
| GET | `/resumes/latest` | latest ResumeOut or null |

## Plans
| POST | `/plans/generate` | builds roadmap from resume digest + targets + deadline → PlanOut |
|---|---|---|
| GET | `/plans/latest` | latest PlanOut or null |

## Interviews (AI endpoints rate-limited 30/min)
| GET | `/interviews/catalog` | `{tracks[], companies[]}` |
|---|---|---|
| POST | `/interviews` | `{session_type: technical\|behavioral\|system_design\|hr, topic, company?, difficulty}` → 201 SessionDetailOut with first question |
| GET | `/interviews` | session list |
| GET | `/interviews/{id}` | session detail with full transcript + per-turn coach |
| POST | `/interviews/{id}/answer` | `{answer, voice_metrics?}` → `{coach, next_question, difficulty, xp_awarded}` · 409 already answered / not active |
| POST | `/interviews/{id}/finish` | completes session → ReportOut · 422 if no answers |
| GET | `/interviews/reports/all` | all feedback reports (annotated with topic/company) |

## Coding (run/submit rate-limited 20/min)
| GET | `/coding/problems` | problem summaries |
|---|---|---|
| GET | `/coding/problems/{id}` | detail: description, starter code per language, visible tests |
| POST | `/coding/run` | `{language: python\|javascript\|java\|cpp, code, stdin}` → `{stdout, stderr, exit_code, timed_out, runtime_ms}` |
| POST | `/coding/problems/{id}/submit` | `{language, code}` → SubmissionOut: per-test results (hidden inputs redacted), AI CodeReview, XP |

## Analytics
| GET | `/dashboard` | readiness %, streak, XP/level, weak/strong areas, recommendations, score trend, recent feedback, badges, deadline countdown |
|---|---|---|
| GET | `/analytics` | score/confidence trends, practice frequency, topic mastery, success prediction |

## Admin (role=admin)
| GET | `/admin/stats` | users, sessions by type, submissions, avg score, event counts |
|---|---|---|
| GET | `/admin/users` | user list |

## Health
`GET /health` (liveness) · `GET /health/ready` (DB ping readiness).

### Error shape
All errors: `{"detail": "message"}` (or Pydantic validation arrays for 422). 429 on rate-limit.
