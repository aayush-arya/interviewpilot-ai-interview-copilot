from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.analytics import LeaderboardEntry
from app.schemas.auth import UpdateProfileRequest, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    return UserRepository(db).save(user)


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    top = UserRepository(db).leaderboard(limit=20)
    return [
        LeaderboardEntry(
            rank=i + 1,
            full_name=u.full_name or u.email.split("@")[0],
            level=u.level,
            xp=u.xp,
            streak_count=u.streak_count,
            is_me=u.id == user.id,
        )
        for i, u in enumerate(top)
    ]
