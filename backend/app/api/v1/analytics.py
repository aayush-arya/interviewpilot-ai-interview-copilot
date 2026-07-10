from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.analytics import AnalyticsOut, DashboardOut
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService(db).dashboard(user)


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService(db).analytics(user)
