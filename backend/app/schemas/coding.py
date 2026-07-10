from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.ai_contracts import CodeReview

SUPPORTED_LANGUAGES = {"python", "javascript", "java", "cpp"}


class ProblemSummary(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: str
    topic: str

    model_config = {"from_attributes": True}


class ProblemDetail(ProblemSummary):
    description: str
    starter_code: dict[str, str]
    visible_tests: list[dict]
    time_limit_ms: int


class RunCodeRequest(BaseModel):
    language: str
    code: str = Field(min_length=1, max_length=50_000)
    stdin: str = Field(default="", max_length=10_000)

    @field_validator("language")
    @classmethod
    def valid_lang(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"language must be one of {sorted(SUPPORTED_LANGUAGES)}")
        return v


class RunCodeResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    runtime_ms: int


class SubmitCodeRequest(BaseModel):
    language: str
    code: str = Field(min_length=1, max_length=50_000)

    @field_validator("language")
    @classmethod
    def valid_lang(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"language must be one of {sorted(SUPPORTED_LANGUAGES)}")
        return v


class TestResult(BaseModel):
    index: int
    hidden: bool
    passed: bool
    input: str | None = None       # null for hidden tests
    expected: str | None = None
    actual: str | None = None
    error: str | None = None


class SubmissionOut(BaseModel):
    id: int
    problem_id: int
    language: str
    status: str
    passed_count: int
    total_count: int
    results: list[TestResult]
    review: CodeReview | None
    runtime_ms: int
    xp_awarded: int = 0
    created_at: datetime
