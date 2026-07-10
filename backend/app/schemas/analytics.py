from datetime import date

from pydantic import BaseModel


class TrendPoint(BaseModel):
    date: date
    value: float


class TopicMastery(BaseModel):
    topic: str
    average_score: float
    sessions: int


class DashboardOut(BaseModel):
    readiness_percent: int
    streak_count: int
    xp: int
    level: int
    next_level_xp: int
    resume_score: int | None
    sessions_completed: int
    problems_solved: int
    weak_areas: list[TopicMastery]
    strong_areas: list[TopicMastery]
    recommended_topics: list[str]
    score_trend: list[TrendPoint]
    recent_feedback: list[dict]
    badges: list[dict]
    days_until_deadline: int | None


class AnalyticsOut(BaseModel):
    score_trend: list[TrendPoint]
    confidence_trend: list[TrendPoint]
    practice_frequency: list[TrendPoint]
    topic_mastery: list[TopicMastery]
    success_prediction: int
    total_sessions: int
    total_submissions: int
    average_score: float


class LeaderboardEntry(BaseModel):
    rank: int
    full_name: str
    level: int
    xp: int
    streak_count: int
    is_me: bool = False
