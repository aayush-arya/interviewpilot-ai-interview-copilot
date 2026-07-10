# Database Schema

SQLAlchemy ORM. Dev: SQLite (auto `create_all`). Prod: PostgreSQL (Alembic migrations — `alembic revision --autogenerate`).

```
users ──< resumes ──< interview_plans
  │
  ├──< interview_sessions ──< interview_turns
  │            └──── 1:1 ──── feedback_reports
  ├──< coding_submissions >── coding_problems
  ├──< activity_events
  ├──< user_badges >── badges
  └──< password_reset_tokens
```

## users
| column | type | notes |
|---|---|---|
| id | int PK | |
| email | str unique idx | |
| hashed_password | str nullable | null for OAuth-only accounts |
| full_name | str | |
| avatar_url | str nullable | |
| provider | str | `local` / `google` / `github` |
| role | str | `user` / `admin` |
| xp | int | gamification |
| level | int | derived, denormalized for leaderboard queries |
| streak_count | int | consecutive active days |
| last_active_date | date nullable | streak bookkeeping |
| target_role | str nullable | e.g. "Backend Engineer" |
| target_company | str nullable | |
| interview_deadline | date nullable | drives countdown |
| created_at | datetime | |

## resumes
id · user_id FK · filename · raw_text (extracted PDF text) · ats_score · recruiter_score · technical_score · communication_score · confidence_score (all int 0-100) · analysis_json (issues, missing skills, keyword gaps, grammar) · improved_resume · cover_letter · linkedin_summary (text, AI-generated) · created_at

## interview_plans
id · user_id FK · resume_id FK nullable · roadmap_json (`{days:[{day,topic,goals[]}], weekly_goals[], skill_gaps[], priority_topics[]}`) · created_at

## interview_sessions
id · user_id FK · session_type (`technical|behavioral|system_design|hr|coding`) · topic · company nullable · difficulty (`easy|medium|hard`, mutates adaptively) · status (`active|completed|abandoned`) · resume_context (compact digest injected into prompts) · started_at · ended_at

## interview_turns
id · session_id FK · turn_index · question · answer nullable · coach_json (`{score, good, weak, faang_view, ideal_answer}`) · difficulty_at_turn · created_at

## feedback_reports
id · session_id FK unique · user_id FK (denorm for feed queries) · overall · communication · confidence · technical_accuracy · problem_solving · scores 0-100 · hiring_recommendation (`strong_hire|hire|lean_hire|no_hire`) · summary · strengths_json · improvements_json · created_at

## coding_problems
id · title · slug unique · description (markdown) · difficulty · topic · starter_code_json (per language) · visible_tests_json / hidden_tests_json (`[{input, expected}]` — stdin/stdout contract) · time_limit_ms

## coding_submissions
id · user_id FK · problem_id FK · language · code · status (`passed|failed|error|timeout`) · passed_count · total_count · results_json · review_json (Claude review: quality, complexity, edge cases, suggestions) · runtime_ms · created_at

## activity_events
Append-only event log powering analytics, streaks, and XP history.
id · user_id FK · kind (`interview_completed|coding_submitted|resume_analyzed|login|plan_generated`) · xp_awarded · meta_json · created_at

## badges / user_badges
badges: id · code unique · name · description · icon · rule_key
user_badges: user_id FK + badge_id FK (composite PK) · awarded_at

## password_reset_tokens
id · user_id FK · token (hashed) · expires_at · used (bool)

### Indexing strategy
- `activity_events (user_id, created_at)` — dashboard/analytics range scans
- `interview_sessions (user_id, status)` — active-session lookup
- `feedback_reports (user_id, created_at)` — recent-feedback feed
- `users (xp desc)` — leaderboard
