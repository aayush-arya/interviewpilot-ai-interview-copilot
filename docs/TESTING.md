# Testing Strategy

## Layers
| Layer | Tooling | What's covered |
|---|---|---|
| Unit | pytest | security helpers, adaptive-difficulty logic, XP/level math, JSON extractor |
| Service/API integration | pytest + FastAPI TestClient + SQLite in-memory + MockAIProvider | full flows: register→login→refresh, resume analyze, interview start→answer→finish→report, coding run/submit, forgot/reset password, admin gating |
| AI contract | pytest | MockAIProvider responses validate against the same Pydantic schemas used to parse real Claude output — catches contract drift |
| Code runner | pytest | pass/fail/timeout/output-cap behavior with real subprocesses |
| Frontend | tsc --noEmit + vite build in CI | type safety + build integrity |

## Running
```bash
cd backend
pytest -q                 # whole suite, no network, no API key needed
pytest tests/test_interview_flow.py -q
```
Tests override `get_db` with a per-test in-memory SQLite and override `get_ai_provider` with the mock — deterministic and fast (<10 s suite).

## Conventions
- Every new endpoint ships with at least one happy-path and one auth-failure test.
- Anything parsing AI output must have a malformed-input test (`extract_json` cases).
- No test may hit the network; CI has no `ANTHROPIC_API_KEY` by design.
