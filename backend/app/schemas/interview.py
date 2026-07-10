from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.ai_contracts import CoachEvaluation

VALID_TYPES = {"technical", "behavioral", "system_design", "hr"}


class StartInterviewRequest(BaseModel):
    session_type: str = "technical"
    topic: str = "General"
    company: str | None = None
    difficulty: str = "medium"

    @field_validator("session_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"session_type must be one of {sorted(VALID_TYPES)}")
        return v

    @field_validator("difficulty")
    @classmethod
    def valid_difficulty(cls, v: str) -> str:
        return v if v in {"easy", "medium", "hard"} else "medium"


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=4000)
    voice_metrics: dict | None = None  # {wpm, filler_count, duration_s} from browser voice mode


class TurnOut(BaseModel):
    turn_index: int
    question: str
    answer: str | None = None
    coach: CoachEvaluation | None = None
    difficulty_at_turn: str

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: int
    session_type: str
    topic: str
    company: str | None
    difficulty: str
    status: str
    started_at: datetime
    ended_at: datetime | None

    model_config = {"from_attributes": True}


class SessionDetailOut(SessionOut):
    turns: list[TurnOut] = []


class AnswerResponse(BaseModel):
    coach: CoachEvaluation
    next_question: str
    difficulty: str
    turn_index: int
    xp_awarded: int


class ReportOut(BaseModel):
    id: int
    session_id: int
    overall: int
    communication: int
    confidence: int
    technical_accuracy: int
    problem_solving: int
    hiring_recommendation: str
    summary: str
    strengths: list[str]
    improvements: list[str]
    created_at: datetime
    session_type: str | None = None
    topic: str | None = None
    company: str | None = None
