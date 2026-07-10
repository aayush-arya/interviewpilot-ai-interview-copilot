"""Mock-interview engine: start → answer loop (coach + adaptive difficulty +
follow-up generation with full conversation memory) → finish."""
import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.prompts import COACH_SYSTEM, interviewer_system
from app.ai.provider import AIProvider, call_structured
from app.models import InterviewSession, User
from app.repositories.content import ResumeRepository
from app.repositories.interviews import InterviewRepository
from app.schemas.ai_contracts import CoachEvaluation
from app.schemas.interview import AnswerRequest, AnswerResponse, StartInterviewRequest
from app.services.gamification_service import GamificationService

DIFFICULTY_LADDER = ["easy", "medium", "hard"]
MAX_TRANSCRIPT_MESSAGES = 40


class InterviewService:
    def __init__(self, db: Session, ai: AIProvider):
        self.db = db
        self.ai = ai
        self.repo = InterviewRepository(db)

    def start(self, user: User, payload: StartInterviewRequest) -> tuple[InterviewSession, str]:
        resume = ResumeRepository(self.db).latest_for_user(user.id)
        resume_digest = ""
        if resume:
            analysis = json.loads(resume.analysis_json or "{}")
            resume_digest = analysis.get("digest", "")

        session = self.repo.create_session(
            user_id=user.id,
            session_type=payload.session_type,
            topic=payload.topic,
            company=payload.company,
            difficulty=payload.difficulty,
            resume_context=resume_digest,
        )
        first_question = self.ai.complete(
            system=self._system_prompt(session),
            messages=[{"role": "user", "content": "I'm ready. Please ask your first question."}],
            chain="interviewer",
            max_tokens=300,
        ).strip()
        self.repo.add_turn(
            session, turn_index=0, question=first_question, difficulty_at_turn=session.difficulty
        )
        return session, first_question

    def answer(self, user: User, session_id: int, payload: AnswerRequest) -> AnswerResponse:
        session = self._get_active(user, session_id)
        current_turn = session.turns[-1]
        if current_turn.answer is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "This question was already answered")

        coach = self._evaluate(session, current_turn.question, payload)
        current_turn.answer = payload.answer
        current_turn.coach_json = coach.model_dump_json()
        self.repo.save(current_turn)

        self._adapt_difficulty(session)

        next_question = self.ai.complete(
            system=self._system_prompt(session),
            messages=self._transcript_messages(session),
            chain="interviewer",
            max_tokens=300,
        ).strip()
        next_turn = self.repo.add_turn(
            session,
            turn_index=current_turn.turn_index + 1,
            question=next_question,
            difficulty_at_turn=session.difficulty,
        )
        xp = GamificationService(self.db).award(
            user, "interview_answer", {"session_id": session.id, "score": coach.score}
        )
        return AnswerResponse(
            coach=coach,
            next_question=next_question,
            difficulty=session.difficulty,
            turn_index=next_turn.turn_index,
            xp_awarded=xp,
        )

    def finish(self, user: User, session_id: int) -> InterviewSession:
        session = self._get_active(user, session_id)
        answered = [t for t in session.turns if t.answer is not None]
        if not answered:
            session.status = "abandoned"
        else:
            session.status = "completed"
        session.ended_at = datetime.now(timezone.utc)
        self.repo.save(session)
        return session

    # --- internals ----------------------------------------------------------
    def _get_active(self, user: User, session_id: int) -> InterviewSession:
        session = self.repo.get_session(session_id, user.id)
        if not session:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview session not found")
        if session.status != "active":
            raise HTTPException(status.HTTP_409_CONFLICT, "Interview session is not active")
        return session

    def _system_prompt(self, session: InterviewSession) -> str:
        return interviewer_system(
            session.session_type,
            session.topic,
            session.company,
            session.difficulty,
            session.resume_context,
        )

    def _evaluate(self, session, question: str, payload: AnswerRequest) -> CoachEvaluation:
        voice_note = ""
        if payload.voice_metrics:
            vm = payload.voice_metrics
            voice_note = (
                f"\n<voice_metrics>pace: {vm.get('wpm', '?')} wpm, "
                f"filler words: {vm.get('filler_count', '?')}, "
                f"duration: {vm.get('duration_s', '?')}s</voice_metrics>"
            )
        return call_structured(
            self.ai,
            CoachEvaluation,
            system=COACH_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"<question>{question}</question>\n"
                    f"<answer>{payload.answer}</answer>{voice_note}",
                }
            ],
            chain="coach",
            max_tokens=700,
        )

    def _adapt_difficulty(self, session: InterviewSession) -> None:
        scores = [
            json.loads(t.coach_json)["score"] for t in session.turns if t.coach_json
        ][-2:]
        if not scores:
            return
        avg = sum(scores) / len(scores)
        idx = DIFFICULTY_LADDER.index(session.difficulty)
        if avg >= 7.5 and idx < 2:
            session.difficulty = DIFFICULTY_LADDER[idx + 1]
        elif avg <= 4 and idx > 0:
            session.difficulty = DIFFICULTY_LADDER[idx - 1]
        self.repo.save(session)

    def _transcript_messages(self, session: InterviewSession) -> list[dict]:
        messages: list[dict] = [
            {"role": "user", "content": "I'm ready. Please ask your first question."}
        ]
        for turn in session.turns:
            messages.append({"role": "assistant", "content": turn.question})
            if turn.answer is not None:
                messages.append({"role": "user", "content": turn.answer})
        # Cap replay length; keep the first exchange (topic anchor) + most recent turns.
        if len(messages) > MAX_TRANSCRIPT_MESSAGES:
            messages = messages[:3] + messages[-(MAX_TRANSCRIPT_MESSAGES - 3):]
        # Transcript must end with a user message for the next assistant turn.
        if messages[-1]["role"] == "assistant":
            messages.append({"role": "user", "content": "(continue)"})
        return messages
