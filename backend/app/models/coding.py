from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.user import utcnow


class CodingProblem(Base):
    __tablename__ = "coding_problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)  # markdown
    difficulty: Mapped[str] = mapped_column(String(10), default="medium")
    topic: Mapped[str] = mapped_column(String(60), default="arrays")
    starter_code_json: Mapped[str] = mapped_column(Text, default="{}")  # {lang: code}
    visible_tests_json: Mapped[str] = mapped_column(Text, default="[]")  # [{input, expected}]
    hidden_tests_json: Mapped[str] = mapped_column(Text, default="[]")
    time_limit_ms: Mapped[int] = mapped_column(Integer, default=5000)


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("coding_problems.id"), index=True)
    language: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(10), default="error")  # passed|failed|error|timeout
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    results_json: Mapped[str] = mapped_column(Text, default="[]")
    review_json: Mapped[str] = mapped_column(Text, default="{}")
    runtime_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
