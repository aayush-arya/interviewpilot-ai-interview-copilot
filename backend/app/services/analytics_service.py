"""Dashboard + analytics aggregations over reports, submissions and events."""
import json
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.ai.prompts import TRACKS
from app.models import User
from app.repositories.content import BadgeRepository, CodingRepository, EventRepository, ResumeRepository
from app.repositories.interviews import InterviewRepository, ReportRepository
from app.schemas.analytics import AnalyticsOut, DashboardOut, TopicMastery, TrendPoint
from app.services.gamification_service import total_xp_for_level


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.reports = ReportRepository(db)
        self.interviews = InterviewRepository(db)
        self.coding = CodingRepository(db)
        self.events = EventRepository(db)

    def dashboard(self, user: User) -> DashboardOut:
        reports = self.reports.list_for_user(user.id, limit=100)
        sessions = {s.id: s for s in self.interviews.list_sessions(user.id, limit=200)}
        resume = ResumeRepository(self.db).latest_for_user(user.id)
        mastery = self._topic_mastery(reports, sessions)
        weak = sorted(mastery, key=lambda m: m.average_score)[:3]
        strong = sorted(mastery, key=lambda m: -m.average_score)[:3]
        problems_solved = self.coding.count_passed(user.id)
        sessions_completed = self.interviews.count_completed(user.id)

        days_left = None
        if user.interview_deadline:
            days_left = max(0, (user.interview_deadline - date.today()).days)

        return DashboardOut(
            readiness_percent=self._readiness(user, reports, resume, problems_solved),
            streak_count=user.streak_count,
            xp=user.xp,
            level=user.level,
            next_level_xp=total_xp_for_level(user.level + 1),
            resume_score=resume.ats_score if resume else None,
            sessions_completed=sessions_completed,
            problems_solved=problems_solved,
            weak_areas=weak,
            strong_areas=strong,
            recommended_topics=self._recommendations(weak, resume),
            score_trend=self._trend([(r.created_at.date(), r.overall) for r in reports]),
            recent_feedback=[
                {
                    "session_id": r.session_id,
                    "overall": r.overall,
                    "recommendation": r.hiring_recommendation,
                    "summary": r.summary[:200],
                    "topic": getattr(sessions.get(r.session_id), "topic", ""),
                    "created_at": r.created_at.isoformat(),
                }
                for r in reports[:5]
            ],
            badges=[
                {"code": b.code, "name": b.name, "icon": b.icon, "description": b.description}
                for b in BadgeRepository(self.db).user_badges(user.id)
            ],
            days_until_deadline=days_left,
        )

    def analytics(self, user: User) -> AnalyticsOut:
        reports = self.reports.list_for_user(user.id, limit=200)
        sessions = {s.id: s for s in self.interviews.list_sessions(user.id, limit=300)}
        submissions = self.coding.list_submissions(user.id, limit=300)
        events = self.events.for_user(user.id, limit=500)

        practice_by_day: dict[date, int] = defaultdict(int)
        for e in events:
            if e.kind in ("interview_completed", "coding_submitted", "interview_answer"):
                practice_by_day[e.created_at.date()] += 1

        avg = sum(r.overall for r in reports) / len(reports) if reports else 0.0
        return AnalyticsOut(
            score_trend=self._trend([(r.created_at.date(), r.overall) for r in reports]),
            confidence_trend=self._trend([(r.created_at.date(), r.confidence) for r in reports]),
            practice_frequency=[
                TrendPoint(date=d, value=v) for d, v in sorted(practice_by_day.items())
            ][-30:],
            topic_mastery=self._topic_mastery(reports, sessions),
            success_prediction=self._readiness_from_scores(
                [r.overall for r in reports], len(submissions)
            ),
            total_sessions=len([s for s in sessions.values() if s.status == "completed"]),
            total_submissions=len(submissions),
            average_score=round(avg, 1),
        )

    # --- internals ----------------------------------------------------------
    @staticmethod
    def _trend(points: list[tuple[date, int]]) -> list[TrendPoint]:
        by_day: dict[date, list[int]] = defaultdict(list)
        for d, v in points:
            by_day[d].append(v)
        return [
            TrendPoint(date=d, value=round(sum(vs) / len(vs), 1))
            for d, vs in sorted(by_day.items())
        ][-30:]

    @staticmethod
    def _topic_mastery(reports, sessions) -> list[TopicMastery]:
        by_topic: dict[str, list[int]] = defaultdict(list)
        for r in reports:
            session = sessions.get(r.session_id)
            if session:
                by_topic[session.topic].append(r.overall)
        return [
            TopicMastery(topic=t, average_score=round(sum(v) / len(v), 1), sessions=len(v))
            for t, v in sorted(by_topic.items())
        ]

    def _readiness(self, user, reports, resume, problems_solved: int) -> int:
        return self._readiness_from_scores(
            [r.overall for r in reports],
            problems_solved,
            resume_score=resume.ats_score if resume else None,
            streak=user.streak_count,
        )

    @staticmethod
    def _readiness_from_scores(
        scores: list[int], activity_count: int, resume_score: int | None = None, streak: int = 0
    ) -> int:
        """Weighted readiness: recent performance 60%, volume 20%, resume 15%, streak 5%."""
        recent = scores[:5]
        performance = sum(recent) / len(recent) if recent else 0
        volume = min(activity_count / 20, 1.0) * 100
        resume_part = resume_score if resume_score is not None else 40
        streak_part = min(streak / 7, 1.0) * 100
        readiness = 0.6 * performance + 0.2 * volume + 0.15 * resume_part + 0.05 * streak_part
        return int(round(readiness))

    @staticmethod
    def _recommendations(weak: list[TopicMastery], resume) -> list[str]:
        recs = [w.topic for w in weak]
        if resume:
            analysis = json.loads(resume.analysis_json or "{}")
            recs += [s for s in analysis.get("missing_skills", []) if s in TRACKS]
        if not recs:
            recs = ["Data Structures & Algorithms", "System Design", "Behavioral"]
        seen: set[str] = set()
        return [r for r in recs if not (r in seen or seen.add(r))][:5]
