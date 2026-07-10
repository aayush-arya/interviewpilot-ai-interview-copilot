import logging

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1 import admin, analytics, auth, coding, interviews, plans, resumes, users
from app.core.config import get_settings
from app.db.session import Base, SessionLocal, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

app = FastAPI(
    title="InterviewPilot API",
    version="1.0.0",
    description="AI Interview Copilot — mock interviews, resume analysis, coding rounds, feedback.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


api = APIRouter(prefix="/api/v1")
for router in (auth.router, users.router, resumes.router, plans.router,
               interviews.router, coding.router, analytics.router, admin.router):
    api.include_router(router)


@api.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@api.get("/health/ready", tags=["health"])
def ready():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ready"}


app.include_router(api)


@app.on_event("startup")
def startup():
    # Dev convenience; production uses Alembic (docs/DEPLOYMENT.md).
    import app.models  # noqa: F401  register all tables

    Base.metadata.create_all(bind=engine)
