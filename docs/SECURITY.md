# Security Architecture

## Authentication & sessions
- **Passwords**: bcrypt (passlib), min-length + complexity validated in schema. Never logged.
- **JWT**: short-lived access token (30 min) + refresh token (14 days), HS256, distinct `type` claims so a refresh token can't be used as access. Secret from env; app refuses to start with the placeholder secret when `ENV=production`.
- **OAuth (Google/GitHub)**: standard code flow server-side; endpoints return 501 unless client id/secret env vars are set. On first OAuth login an account is provisioned with `provider` set and no password.
- **Forgot password**: single-use, hashed, 30-min-expiry token stored server-side; response is identical whether the email exists or not (no user enumeration). Token delivery via SMTP if configured, else logged to server console (dev).
- **Route protection**: `get_current_user` dependency; `require_admin` for admin routes. Frontend mirrors with `ProtectedRoute` + role check, but authorization is enforced server-side only.

## Code execution sandboxing (`app/services/runner.py`)
Threat: arbitrary user code execution is the product feature.
Current controls (single-tenant / self-hosted appropriate):
- Each run executes in a fresh temp directory, wiped afterwards.
- Hard wall-clock timeout (default 5 s) → process kill (whole tree on Windows via `taskkill /T`).
- Output capped (64 KB) to prevent memory exhaustion via stdout flooding.
- Environment stripped to a minimal allowlist (no inherited secrets, no `ANTHROPIC_API_KEY`).
- Python runs with `-I` (isolated mode: no site-packages, no env hooks).

**Multi-tenant production upgrade path (required before public hosting):** run each submission in an ephemeral container (`docker run --rm --network=none --memory=128m --cpus=0.5 --pids-limit=64 --read-only`) or delegate to Judge0/Firecracker. The `CodeRunner` interface is the seam; swap the implementation without touching services.

## API hardening
- Rate limiting middleware: fixed-window per user/IP (Redis-backed when available, in-memory fallback) — strictest on auth (10/min) and AI endpoints (30/min).
- CORS locked to configured origins.
- Upload constraints: PDF only (magic-bytes check, not just extension), 5 MB cap, filename never used for storage paths (UUID names).
- SQL injection: SQLAlchemy bound parameters everywhere; no raw SQL.
- Secrets only via environment; `.env` git-ignored; `.env.example` documents every variable.

## Prompt-injection surface
Resume text and interview answers are untrusted input embedded in prompts. Mitigations: user content is delimited in tagged blocks (`<resume>…</resume>`), system prompts instruct the model to treat content as data, and AI outputs are parsed into strict schemas — free-text model output is rendered as text (React escapes by default), never `dangerouslySetInnerHTML`, and markdown rendering strips raw HTML.

## Transport & headers
Behind nginx: TLS termination, HSTS, `X-Content-Type-Options`, `X-Frame-Options: DENY`, gzip. FastAPI adds security headers middleware for non-proxied deployments.
