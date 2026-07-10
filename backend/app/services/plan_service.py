"""30-day roadmap generation, deadline-aware."""
import json
from datetime import date

from sqlalchemy.orm import Session

from app.ai.prompts import PLAN_SYSTEM
from app.ai.provider import AIProvider, call_structured
from app.models import InterviewPlan, User
from app.repositories.content import PlanRepository, ResumeRepository
from app.schemas.ai_contracts import InterviewRoadmap
from app.services.gamification_service import GamificationService


class PlanService:
    def __init__(self, db: Session, ai: AIProvider):
        self.db = db
        self.ai = ai
        self.repo = PlanRepository(db)

    def generate(self, user: User) -> InterviewPlan:
        resume = ResumeRepository(self.db).latest_for_user(user.id)
        digest = ""
        weak_signals = ""
        if resume:
            analysis = json.loads(resume.analysis_json or "{}")
            digest = analysis.get("digest", "")
            weak_signals = ", ".join(
                analysis.get("missing_skills", []) + analysis.get("keyword_gaps", [])
            )

        days_available = 30
        if user.interview_deadline:
            remaining = (user.interview_deadline - date.today()).days
            if remaining > 0:
                days_available = max(7, min(60, remaining))

        prompt = (
            f"target_role: {user.target_role or 'Software Engineer'}\n"
            f"target_company: {user.target_company or 'top tech company'}\n"
            f"days_available: {days_available}\n"
            f"known_weak_areas: {weak_signals or 'unknown'}\n"
            f"<resume_digest>{digest or 'No resume uploaded yet.'}</resume_digest>"
        )
        roadmap: InterviewRoadmap = call_structured(
            self.ai,
            InterviewRoadmap,
            system=PLAN_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
            chain="plan",
            max_tokens=4000,
            deep=True,
        )
        plan = self.repo.create(
            user_id=user.id,
            resume_id=resume.id if resume else None,
            roadmap_json=roadmap.model_dump_json(),
        )
        GamificationService(self.db).award(user, "plan_generated", {"plan_id": plan.id})
        return plan
