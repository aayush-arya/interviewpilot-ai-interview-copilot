# Deployment

## Local / self-hosted (Docker Compose)
`docker compose up --build` starts:
- **db**: PostgreSQL 16 (volume-persisted)
- **redis**: Redis 7 (rate limiting + cache)
- **backend**: FastAPI under uvicorn, waits for db healthcheck, runs seed on first boot
- **frontend**: multi-stage build → static bundle served by nginx, `/api` proxied to backend

## AWS reference architecture
```
Route53 → CloudFront (SPA from S3)  ──┐
Route53 → ALB (api.domain.com, TLS) ──┤
                                      ▼
                    ECS Fargate service (backend image from ECR)
                    ├── RDS PostgreSQL (multi-AZ)
                    ├── ElastiCache Redis
                    ├── S3 bucket (resume uploads — enable S3StorageAdapter via env)
                    └── Secrets Manager → task env (ANTHROPIC_API_KEY, SECRET_KEY, DB URL)
CloudWatch: container logs, ALB 5xx alarm, p95 latency alarm, AI-cost log metric filter
```
Scaling: backend is stateless (JWT, DB-backed sessions) → horizontal scale behind ALB. AI latency dominates; set target-tracking on ALB request count, not CPU.

## CI/CD (GitHub Actions — `.github/workflows/ci.yml`)
1. **backend job**: ruff lint → pytest (mock AI provider, SQLite) — no secrets needed.
2. **frontend job**: npm ci → tsc --noEmit → vite build.
3. **docker job** (main branch only): build both images, push to registry with git-SHA tags.
4. Deploy step (commented template): `aws ecs update-service --force-new-deployment` after image push; SPA sync via `aws s3 sync && cloudfront create-invalidation`.

Rollback = redeploy previous SHA tag. DB migrations run as a one-off ECS task before service update (`alembic upgrade head`).

## Monitoring
- `/api/v1/health` (liveness: process up) and `/api/v1/health/ready` (readiness: DB ping) for orchestrator probes.
- Structured JSON logs (uvicorn access + app loggers) → CloudWatch / Loki.
- AI usage: every provider call logs chain name, latency, input/output tokens → dashboardable cost tracking.
- Admin dashboard surfaces the same usage counters in-app.
