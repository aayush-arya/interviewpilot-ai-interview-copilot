from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.session import get_db
from app.models import CodingSubmission, FeedbackReport, InterviewSession
from app.repositories.content import EventRepository
from app.repositories.users import UserRepository
from app.schemas.auth import UserOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    sessions_by_type = dict(
        db.execute(
            select(InterviewSession.session_type, func.count(InterviewSession.id)).group_by(
                InterviewSession.session_type
            )
        ).all()
    )
    avg_score = db.scalar(select(func.avg(FeedbackReport.overall))) or 0
    return {
        "total_users": UserRepository(db).count(),
        "total_sessions": db.scalar(select(func.count(InterviewSession.id))) or 0,
        "sessions_by_type": sessions_by_type,
        "total_submissions": db.scalar(select(func.count(CodingSubmission.id))) or 0,
        "average_interview_score": round(float(avg_score), 1),
        "ai_events_by_kind": EventRepository(db).count_by_kind(),
    }


@router.get("/users", response_model=list[UserOut])
def users(db: Session = Depends(get_db)):
    return UserRepository(db).list_all()
