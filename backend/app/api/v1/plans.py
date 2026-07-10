import json
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider, get_ai_provider
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.models import InterviewPlan, User
from app.repositories.content import PlanRepository
from app.schemas.ai_contracts import InterviewRoadmap
from app.schemas.resume import PlanOut
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


def _to_out(plan: InterviewPlan, user: User) -> PlanOut:
    days_left = None
    if user.interview_deadline:
        days_left = max(0, (user.interview_deadline - date.today()).days)
    return PlanOut(
        id=plan.id,
        resume_id=plan.resume_id,
        roadmap=InterviewRoadmap.model_validate(json.loads(plan.roadmap_json)),
        created_at=plan.created_at,
        days_until_deadline=days_left,
    )


@router.post(
    "/generate",
    response_model=PlanOut,
    dependencies=[Depends(rate_limit("plan", limit=5, window_s=300))],
)
def generate(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    return _to_out(PlanService(db, ai).generate(user), user)


@router.get("/latest", response_model=PlanOut | None)
def latest(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = PlanRepository(db).latest_for_user(user.id)
    return _to_out(plan, user) if plan else None
