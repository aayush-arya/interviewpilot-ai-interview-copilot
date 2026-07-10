import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.models import User
from app.repositories.users import ResetTokenRepository, UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair
from app.services.gamification_service import GamificationService

logger = logging.getLogger("auth")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.reset_tokens = ResetTokenRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        if self.users.get_by_email(payload.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email exists")
        return self.users.create(
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            provider="local",
        )

    def login(self, payload: LoginRequest) -> TokenPair:
        user = self.users.get_by_email(payload.email)
        if not user or not user.hashed_password or not verify_password(
            payload.password, user.hashed_password
        ):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
        GamificationService(self.db).award(user, "login")
        return self._issue_tokens(user)

    def oauth_login(self, email: str, full_name: str, provider: str, avatar_url: str | None) -> TokenPair:
        user = self.users.get_by_email(email)
        if user is None:
            user = self.users.create(
                email=email.lower(), full_name=full_name, provider=provider, avatar_url=avatar_url
            )
        GamificationService(self.db).award(user, "login")
        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenPair:
        from app.core.security import decode_token

        user_id = decode_token(refresh_token, "refresh")
        user = self.users.get(user_id) if user_id else None
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
        return self._issue_tokens(user)

    def forgot_password(self, email: str) -> None:
        """Always succeeds from the caller's perspective (no user enumeration)."""
        user = self.users.get_by_email(email)
        if not user:
            return
        raw, token_hash = generate_reset_token()
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=get_settings().RESET_TOKEN_EXPIRE_MINUTES
        )
        self.reset_tokens.create(user.id, token_hash, expires)
        reset_link = f"{get_settings().FRONTEND_URL}/reset-password?token={raw}"
        self._send_reset_email(user.email, reset_link)

    def reset_password(self, raw_token: str, new_password: str) -> None:
        token = self.reset_tokens.get_valid(hash_reset_token(raw_token))
        if not token:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")
        user = self.users.get(token.user_id)
        if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")
        user.hashed_password = hash_password(new_password)
        self.users.save(user)
        self.reset_tokens.mark_used(token)

    def _issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    @staticmethod
    def _send_reset_email(to_email: str, reset_link: str) -> None:
        settings = get_settings()
        if not settings.SMTP_HOST:
            logger.warning("SMTP not configured. Password reset link for %s: %s", to_email, reset_link)
            return
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["Subject"] = "Reset your InterviewPilot password"
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        msg.set_content(
            f"Click the link to reset your password (valid 30 minutes):\n{reset_link}\n\n"
            "If you didn't request this, ignore this email."
        )
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            smtp.starttls()
            if settings.SMTP_USER:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
