"""Resume analysis pipeline: PDF → text → analyst chain → writer chain → digest."""
import io
import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.prompts import (
    RESUME_ANALYST_SYSTEM,
    RESUME_WRITER_SYSTEM,
    resume_digest_prompt,
)
from app.ai.provider import AIProvider, call_structured
from app.models import Resume, User
from app.repositories.content import ResumeRepository
from app.schemas.ai_contracts import ResumeAnalysis, ResumeDocs
from app.services.gamification_service import GamificationService

PDF_MAGIC = b"%PDF"


class ResumeService:
    def __init__(self, db: Session, ai: AIProvider):
        self.db = db
        self.ai = ai
        self.repo = ResumeRepository(db)

    def analyze_upload(self, user: User, filename: str, content: bytes) -> Resume:
        raw_text = self._extract_pdf_text(content)
        if len(raw_text.strip()) < 100:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Could not extract enough text from this PDF (is it a scanned image?)",
            )

        target = f"Target role: {user.target_role or 'Software Engineer'}"
        analysis: ResumeAnalysis = call_structured(
            self.ai,
            ResumeAnalysis,
            system=RESUME_ANALYST_SYSTEM,
            messages=[{"role": "user", "content": f"{target}\n<resume>\n{raw_text[:15000]}\n</resume>"}],
            chain="resume_analysis",
            max_tokens=2000,
            deep=True,
        )
        docs: ResumeDocs = call_structured(
            self.ai,
            ResumeDocs,
            system=RESUME_WRITER_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"{target}\n<resume>\n{raw_text[:15000]}\n</resume>\n"
                    f"<analyst_issues>\n{analysis.model_dump_json()}\n</analyst_issues>",
                }
            ],
            chain="resume_docs",
            max_tokens=2500,
            deep=True,
        )
        digest = self.ai.complete(
            system="You summarize resumes for interviewers.",
            messages=[{"role": "user", "content": resume_digest_prompt(raw_text)}],
            chain="resume_digest",
            max_tokens=300,
        ).strip()

        analysis_payload = analysis.model_dump()
        analysis_payload["digest"] = digest

        resume = self.repo.create(
            user_id=user.id,
            filename=filename,
            raw_text=raw_text,
            ats_score=analysis.ats_score,
            recruiter_score=analysis.recruiter_score,
            technical_score=analysis.technical_score,
            communication_score=analysis.communication_score,
            confidence_score=analysis.confidence_score,
            analysis_json=json.dumps(analysis_payload),
            improved_resume=docs.improved_resume,
            cover_letter=docs.cover_letter,
            linkedin_summary=docs.linkedin_summary,
        )
        GamificationService(self.db).award(user, "resume_analyzed", {"resume_id": resume.id})
        return resume

    @staticmethod
    def _extract_pdf_text(content: bytes) -> str:
        if not content.startswith(PDF_MAGIC):
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "File is not a PDF")
        from pypdf import PdfReader

        try:
            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:  # pypdf raises many exception types
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, f"Failed to read PDF: {e}"
            ) from e
