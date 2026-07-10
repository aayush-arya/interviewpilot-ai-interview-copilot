from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PasswordResetToken, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email.lower()))

    def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def leaderboard(self, limit: int = 20) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.xp.desc()).limit(limit)))

    def list_all(self, limit: int = 200) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.created_at.desc()).limit(limit)))

    def count(self) -> int:
        from sqlalchemy import func

        return self.db.scalar(select(func.count(User.id))) or 0


class ResetTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, token_hash: str, expires_at: datetime) -> PasswordResetToken:
        token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(token)
        self.db.commit()
        return token

    def get_valid(self, token_hash: str) -> PasswordResetToken | None:
        token = self.db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used.is_(False),
            )
        )
        if token is None:
            return None
        expires = token.expires_at
        if expires.tzinfo is None:  # SQLite drops tzinfo
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            return None
        return token

    def mark_used(self, token: PasswordResetToken) -> None:
        token.used = True
        self.db.commit()
