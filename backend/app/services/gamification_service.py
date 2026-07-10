"""XP, levels, streaks and badges.

Level curve: level N requires 100 * N * (N - 1) / 2 total XP
(level 2 at 100, level 3 at 300, level 4 at 600 ...).
"""
import json
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import User
from app.repositories.content import BadgeRepository, CodingRepository, EventRepository
from app.repositories.interviews import InterviewRepository
from app.repositories.users import UserRepository

XP_RULES = {
    "login": 5,
    "resume_analyzed": 40,
    "plan_generated": 25,
    "interview_answer": 10,
    "interview_completed": 60,
    "coding_submitted": 20,
    "coding_passed": 50,
}

BADGE_DEFS = [
    ("first_interview", "Ice Breaker", "Complete your first mock interview", "🎤"),
    ("five_interviews", "Regular", "Complete 5 mock interviews", "🔁"),
    ("first_code_pass", "Green Tests", "Pass all tests on a coding problem", "✅"),
    ("streak_7", "On Fire", "Practice 7 days in a row", "🔥"),
    ("resume_pro", "Polished", "Analyze your resume", "📄"),
    ("level_5", "Climber", "Reach level 5", "⛰️"),
]


def total_xp_for_level(level: int) -> int:
    return 100 * level * (level - 1) // 2


def level_for_xp(xp: int) -> int:
    level = 1
    while total_xp_for_level(level + 1) <= xp:
        level += 1
    return level


class GamificationService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.events = EventRepository(db)
        self.badges = BadgeRepository(db)

    def award(self, user: User, kind: str, meta: dict | None = None) -> int:
        """Log an event, add XP, update level/streak, and evaluate badges."""
        xp = XP_RULES.get(kind, 0)
        self.events.log(user.id, kind, xp, json.dumps(meta or {}))
        user.xp += xp
        user.level = level_for_xp(user.xp)
        self._touch_streak(user)
        self.users.save(user)
        self._evaluate_badges(user)
        return xp

    def _touch_streak(self, user: User) -> None:
        today = date.today()
        if user.last_active_date == today:
            return
        if user.last_active_date == today - timedelta(days=1):
            user.streak_count += 1
        else:
            user.streak_count = 1
        user.last_active_date = today

    def _evaluate_badges(self, user: User) -> None:
        interviews = InterviewRepository(self.db).count_completed(user.id)
        passed = CodingRepository(self.db).count_passed(user.id)
        kinds = self.events.count_by_kind()  # global; fine-grained check below uses user data

        checks = {
            "first_interview": interviews >= 1,
            "five_interviews": interviews >= 5,
            "first_code_pass": passed >= 1,
            "streak_7": user.streak_count >= 7,
            "resume_pro": any(
                e.kind == "resume_analyzed" for e in self.events.for_user(user.id, limit=100)
            ),
            "level_5": user.level >= 5,
        }
        _ = kinds
        for code, earned in checks.items():
            if earned:
                badge = self.badges.get_by_code(code)
                if badge:
                    self.badges.award(user.id, badge)
