from datetime import datetime

from pydantic import BaseModel

from app.schemas.ai_contracts import InterviewRoadmap, ResumeAnalysis


class ResumeOut(BaseModel):
    id: int
    filename: str
    ats_score: int
    recruiter_score: int
    technical_score: int
    communication_score: int
    confidence_score: int
    analysis: ResumeAnalysis | None = None
    improved_resume: str
    cover_letter: str
    linkedin_summary: str
    created_at: datetime


class PlanOut(BaseModel):
    id: int
    resume_id: int | None
    roadmap: InterviewRoadmap
    created_at: datetime
    days_until_deadline: int | None = None
