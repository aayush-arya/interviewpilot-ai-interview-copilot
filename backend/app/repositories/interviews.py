from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import FeedbackReport, InterviewSession, InterviewTurn


class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, **kwargs) -> InterviewSession:
        session = InterviewSession(**kwargs)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int, user_id: int) -> InterviewSession | None:
        return self.db.scalar(
            select(InterviewSession)
            .options(selectinload(InterviewSession.turns))
            .where(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
        )

    def list_sessions(self, user_id: int, limit: int = 50) -> list[InterviewSession]:
        return list(
            self.db.scalars(
                select(InterviewSession)
                .where(InterviewSession.user_id == user_id)
                .order_by(InterviewSession.started_at.desc())
                .limit(limit)
            )
        )

    def add_turn(self, session: InterviewSession, **kwargs) -> InterviewTurn:
        turn = InterviewTurn(session_id=session.id, **kwargs)
        self.db.add(turn)
        self.db.commit()
        self.db.refresh(turn)
        return turn

    def save(self, obj) -> None:
        self.db.add(obj)
        self.db.commit()

    def count_completed(self, user_id: int) -> int:
        return (
            self.db.scalar(
                select(func.count(InterviewSession.id)).where(
                    InterviewSession.user_id == user_id,
                    InterviewSession.status == "completed",
                )
            )
            or 0
        )


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> FeedbackReport:
        report = FeedbackReport(**kwargs)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_session(self, session_id: int, user_id: int) -> FeedbackReport | None:
        return self.db.scalar(
            select(FeedbackReport).where(
                FeedbackReport.session_id == session_id, FeedbackReport.user_id == user_id
            )
        )

    def list_for_user(self, user_id: int, limit: int = 50) -> list[FeedbackReport]:
        return list(
            self.db.scalars(
                select(FeedbackReport)
                .where(FeedbackReport.user_id == user_id)
                .order_by(FeedbackReport.created_at.desc())
                .limit(limit)
            )
        )
