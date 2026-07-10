from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    ActivityEvent,
    Badge,
    CodingProblem,
    CodingSubmission,
    InterviewPlan,
    Resume,
    UserBadge,
)


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Resume:
        resume = Resume(**kwargs)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def latest_for_user(self, user_id: int) -> Resume | None:
        return self.db.scalar(
            select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        )

    def get(self, resume_id: int, user_id: int) -> Resume | None:
        return self.db.scalar(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )

    def save(self, resume: Resume) -> None:
        self.db.add(resume)
        self.db.commit()


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> InterviewPlan:
        plan = InterviewPlan(**kwargs)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def latest_for_user(self, user_id: int) -> InterviewPlan | None:
        return self.db.scalar(
            select(InterviewPlan)
            .where(InterviewPlan.user_id == user_id)
            .order_by(InterviewPlan.created_at.desc())
        )


class CodingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_problems(self) -> list[CodingProblem]:
        return list(self.db.scalars(select(CodingProblem).order_by(CodingProblem.id)))

    def get_problem(self, problem_id: int) -> CodingProblem | None:
        return self.db.get(CodingProblem, problem_id)

    def create_submission(self, **kwargs) -> CodingSubmission:
        submission = CodingSubmission(**kwargs)
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def list_submissions(self, user_id: int, limit: int = 50) -> list[CodingSubmission]:
        return list(
            self.db.scalars(
                select(CodingSubmission)
                .where(CodingSubmission.user_id == user_id)
                .order_by(CodingSubmission.created_at.desc())
                .limit(limit)
            )
        )

    def count_passed(self, user_id: int) -> int:
        return (
            self.db.scalar(
                select(func.count(func.distinct(CodingSubmission.problem_id))).where(
                    CodingSubmission.user_id == user_id, CodingSubmission.status == "passed"
                )
            )
            or 0
        )


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_id: int, kind: str, xp: int = 0, meta: str = "{}") -> ActivityEvent:
        event = ActivityEvent(user_id=user_id, kind=kind, xp_awarded=xp, meta_json=meta)
        self.db.add(event)
        self.db.commit()
        return event

    def for_user(self, user_id: int, limit: int = 500) -> list[ActivityEvent]:
        return list(
            self.db.scalars(
                select(ActivityEvent)
                .where(ActivityEvent.user_id == user_id)
                .order_by(ActivityEvent.created_at.desc())
                .limit(limit)
            )
        )

    def count_by_kind(self) -> dict[str, int]:
        rows = self.db.execute(
            select(ActivityEvent.kind, func.count(ActivityEvent.id)).group_by(ActivityEvent.kind)
        ).all()
        return {kind: count for kind, count in rows}


class BadgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self) -> list[Badge]:
        return list(self.db.scalars(select(Badge)))

    def get_by_code(self, code: str) -> Badge | None:
        return self.db.scalar(select(Badge).where(Badge.code == code))

    def user_badges(self, user_id: int) -> list[Badge]:
        return list(
            self.db.scalars(
                select(Badge).join(UserBadge, UserBadge.badge_id == Badge.id).where(
                    UserBadge.user_id == user_id
                )
            )
        )

    def award(self, user_id: int, badge: Badge) -> bool:
        """Award badge if not already held. Returns True if newly awarded."""
        existing = self.db.get(UserBadge, {"user_id": user_id, "badge_id": badge.id})
        if existing:
            return False
        self.db.add(UserBadge(user_id=user_id, badge_id=badge.id))
        self.db.commit()
        return True
