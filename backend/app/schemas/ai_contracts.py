"""Pydantic contracts for every structured AI response.

Both ClaudeProvider output parsing and MockAIProvider generation validate
against these models, so the mock can never drift from the real contract.
"""
from pydantic import BaseModel, Field, field_validator


def _clamp(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, v))


class ResumeAnalysis(BaseModel):
    ats_score: int
    recruiter_score: int
    technical_score: int
    communication_score: int
    confidence_score: int
    missing_skills: list[str] = []
    weak_descriptions: list[str] = []
    grammar_issues: list[str] = []
    ats_issues: list[str] = []
    keyword_gaps: list[str] = []
    experience_gaps: list[str] = []
    improvement_suggestions: list[str] = []
    summary: str = ""

    @field_validator(
        "ats_score", "recruiter_score", "technical_score", "communication_score", "confidence_score"
    )
    @classmethod
    def clamp_scores(cls, v: int) -> int:
        return _clamp(v)


class ResumeDocs(BaseModel):
    improved_resume: str
    cover_letter: str
    linkedin_summary: str


class PlanDay(BaseModel):
    day: int
    topic: str
    goals: list[str] = []


class InterviewRoadmap(BaseModel):
    days: list[PlanDay]
    weekly_goals: list[str] = []
    skill_gaps: list[str] = []
    priority_topics: list[str] = []


class CoachEvaluation(BaseModel):
    score: int = Field(description="0-10")
    good: str
    weak: str
    faang_view: str
    ideal_answer: str
    key_points: list[str] = Field(
        default=[], description="Every point a full-marks answer must contain"
    )

    @field_validator("score")
    @classmethod
    def clamp_score(cls, v: int) -> int:
        return _clamp(v, 0, 10)


class SessionReport(BaseModel):
    overall: int
    communication: int
    confidence: int
    technical_accuracy: int
    problem_solving: int
    hiring_recommendation: str  # strong_hire|hire|lean_hire|no_hire
    summary: str
    strengths: list[str] = []
    improvements: list[str] = []

    @field_validator("overall", "communication", "confidence", "technical_accuracy", "problem_solving")
    @classmethod
    def clamp_scores(cls, v: int) -> int:
        return _clamp(v)

    @field_validator("hiring_recommendation")
    @classmethod
    def valid_reco(cls, v: str) -> str:
        allowed = {"strong_hire", "hire", "lean_hire", "no_hire"}
        return v if v in allowed else "lean_hire"


class CodeReview(BaseModel):
    verdict: str  # excellent|good|needs_work|poor
    time_complexity: str
    space_complexity: str
    correctness_notes: str
    edge_cases_missed: list[str] = []
    quality_issues: list[str] = []
    optimizations: list[str] = []
    score: int = 0

    @field_validator("score")
    @classmethod
    def clamp_score(cls, v: int) -> int:
        return _clamp(v)
