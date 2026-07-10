import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.companies import COMPANIES, company_blurb
from app.ai.prompts import TRACKS
from app.ai.provider import AIProvider, get_ai_provider
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.models import FeedbackReport, User
from app.repositories.interviews import InterviewRepository, ReportRepository
from app.schemas.ai_contracts import CoachEvaluation
from app.schemas.interview import (
    AnswerRequest,
    AnswerResponse,
    ReportOut,
    SessionDetailOut,
    SessionOut,
    StartInterviewRequest,
    TurnOut,
)
from app.services.feedback_service import FeedbackService
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["interviews"])
ai_guard = Depends(rate_limit("interview", limit=30, window_s=60))


@router.get("/catalog")
def catalog():
    return {
        "tracks": TRACKS,
        "companies": [{"name": name, "blurb": company_blurb(name)} for name in COMPANIES],
    }


@router.post("", response_model=SessionDetailOut, status_code=201, dependencies=[ai_guard])
def start(
    payload: StartInterviewRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    session, _ = InterviewService(db, ai).start(user, payload)
    return _detail(session)


@router.get("", response_model=list[SessionOut])
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InterviewRepository(db).list_sessions(user.id)


@router.get("/{session_id}", response_model=SessionDetailOut)
def get_session(
    session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    session = InterviewRepository(db).get_session(session_id, user.id)
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview session not found")
    return _detail(session)


@router.post("/{session_id}/answer", response_model=AnswerResponse, dependencies=[ai_guard])
def answer(
    session_id: int,
    payload: AnswerRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    return InterviewService(db, ai).answer(user, session_id, payload)


@router.post("/{session_id}/finish", response_model=ReportOut, dependencies=[ai_guard])
def finish(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    session = InterviewService(db, ai).finish(user, session_id)
    if session.status == "abandoned":
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Session had no answers; marked abandoned"
        )
    report = FeedbackService(db, ai).generate_report(user, session)
    return _report_out(report, session.session_type, session.topic, session.company)


def _detail(session) -> SessionDetailOut:
    return SessionDetailOut(
        id=session.id,
        session_type=session.session_type,
        topic=session.topic,
        company=session.company,
        difficulty=session.difficulty,
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        turns=[
            TurnOut(
                turn_index=t.turn_index,
                question=t.question,
                answer=t.answer,
                coach=CoachEvaluation.model_validate_json(t.coach_json) if t.coach_json else None,
                difficulty_at_turn=t.difficulty_at_turn,
            )
            for t in session.turns
        ],
    )


def _report_out(report: FeedbackReport, session_type=None, topic=None, company=None) -> ReportOut:
    return ReportOut(
        id=report.id,
        session_id=report.session_id,
        overall=report.overall,
        communication=report.communication,
        confidence=report.confidence,
        technical_accuracy=report.technical_accuracy,
        problem_solving=report.problem_solving,
        hiring_recommendation=report.hiring_recommendation,
        summary=report.summary,
        strengths=json.loads(report.strengths_json),
        improvements=json.loads(report.improvements_json),
        created_at=report.created_at,
        session_type=session_type,
        topic=topic,
        company=company,
    )


@router.get("/reports/all", response_model=list[ReportOut])
def all_reports(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reports = ReportRepository(db).list_for_user(user.id)
    sessions = {s.id: s for s in InterviewRepository(db).list_sessions(user.id, limit=200)}
    return [
        _report_out(
            r,
            getattr(sessions.get(r.session_id), "session_type", None),
            getattr(sessions.get(r.session_id), "topic", None),
            getattr(sessions.get(r.session_id), "company", None),
        )
        for r in reports
    ]
