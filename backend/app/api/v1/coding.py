import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider, get_ai_provider
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.models import User
from app.repositories.content import CodingRepository
from app.schemas.coding import (
    ProblemDetail,
    ProblemSummary,
    RunCodeRequest,
    RunCodeResponse,
    SubmitCodeRequest,
    SubmissionOut,
)
from app.services.coding_service import CodingService

router = APIRouter(prefix="/coding", tags=["coding"])
run_guard = Depends(rate_limit("code_run", limit=20, window_s=60))


@router.get("/problems", response_model=list[ProblemSummary])
def list_problems(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CodingRepository(db).list_problems()


@router.get("/problems/{problem_id}", response_model=ProblemDetail)
def get_problem(
    problem_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    problem = CodingRepository(db).get_problem(problem_id)
    if not problem:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    return ProblemDetail(
        id=problem.id,
        title=problem.title,
        slug=problem.slug,
        difficulty=problem.difficulty,
        topic=problem.topic,
        description=problem.description,
        starter_code=json.loads(problem.starter_code_json),
        visible_tests=json.loads(problem.visible_tests_json),
        time_limit_ms=problem.time_limit_ms,
    )


@router.post("/run", response_model=RunCodeResponse, dependencies=[run_guard])
def run_code(
    payload: RunCodeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    return CodingService(db, ai).run_adhoc(payload)


@router.post("/problems/{problem_id}/submit", response_model=SubmissionOut, dependencies=[run_guard])
def submit(
    problem_id: int,
    payload: SubmitCodeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    return CodingService(db, ai).submit(user, problem_id, payload)
