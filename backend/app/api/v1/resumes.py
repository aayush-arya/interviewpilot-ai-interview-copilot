import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider, get_ai_provider
from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.models import Resume, User
from app.repositories.content import ResumeRepository
from app.schemas.ai_contracts import ResumeAnalysis
from app.schemas.resume import ResumeOut
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _to_out(resume: Resume) -> ResumeOut:
    analysis_data = json.loads(resume.analysis_json or "{}")
    analysis_data.pop("digest", None)
    analysis = ResumeAnalysis.model_validate(analysis_data) if analysis_data else None
    return ResumeOut(
        id=resume.id,
        filename=resume.filename,
        ats_score=resume.ats_score,
        recruiter_score=resume.recruiter_score,
        technical_score=resume.technical_score,
        communication_score=resume.communication_score,
        confidence_score=resume.confidence_score,
        analysis=analysis,
        improved_resume=resume.improved_resume,
        cover_letter=resume.cover_letter,
        linkedin_summary=resume.linkedin_summary,
        created_at=resume.created_at,
    )


@router.post(
    "/analyze",
    response_model=ResumeOut,
    dependencies=[Depends(rate_limit("resume", limit=5, window_s=300))],
)
async def analyze(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
):
    content = await file.read()
    if len(content) > get_settings().MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "PDF larger than 5 MB")
    resume = ResumeService(db, ai).analyze_upload(user, file.filename or "resume.pdf", content)
    return _to_out(resume)


@router.get("/latest", response_model=ResumeOut | None)
def latest(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = ResumeRepository(db).latest_for_user(user.id)
    return _to_out(resume) if resume else None
