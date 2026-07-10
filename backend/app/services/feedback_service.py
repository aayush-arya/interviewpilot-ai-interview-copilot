"""End-of-session report synthesis, anchored to per-turn coach scores."""
import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.prompts import REPORT_SYSTEM
from app.ai.provider import AIProvider, call_structured
from app.models import FeedbackReport, InterviewSession, User
from app.repositories.interviews import ReportRepository
from app.schemas.ai_contracts import SessionReport
from app.services.gamification_service import GamificationService


class FeedbackService:
    def __init__(self, db: Session, ai: AIProvider):
        self.db = db
        self.ai = ai
        self.repo = ReportRepository(db)

    def generate_report(self, user: User, session: InterviewSession) -> FeedbackReport:
        existing = self.repo.get_by_session(session.id, user.id)
        if existing:
            return existing
        answered = [t for t in session.turns if t.answer is not None]
        if not answered:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "No answers to evaluate")

        transcript_lines = []
        for t in answered:
            coach = json.loads(t.coach_json or "{}")
            transcript_lines.append(
                f"Q{t.turn_index + 1} ({t.difficulty_at_turn}): {t.question}\n"
                f"A: {t.answer}\ncoach_score: {coach.get('score', '?')}"
            )
        transcript = "\n\n".join(transcript_lines)

        report_data: SessionReport = call_structured(
            self.ai,
            SessionReport,
            system=REPORT_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"Interview type: {session.session_type}, topic: {session.topic}, "
                    f"company: {session.company or 'generic'}\n\n<transcript>\n{transcript}\n</transcript>",
                }
            ],
            chain="report",
            max_tokens=1200,
        )
        report = self.repo.create(
            session_id=session.id,
            user_id=user.id,
            overall=report_data.overall,
            communication=report_data.communication,
            confidence=report_data.confidence,
            technical_accuracy=report_data.technical_accuracy,
            problem_solving=report_data.problem_solving,
            hiring_recommendation=report_data.hiring_recommendation,
            summary=report_data.summary,
            strengths_json=json.dumps(report_data.strengths),
            improvements_json=json.dumps(report_data.improvements),
        )
        GamificationService(self.db).award(
            user, "interview_completed", {"session_id": session.id, "overall": report.overall}
        )
        return report
