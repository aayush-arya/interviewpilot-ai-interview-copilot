from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPair,
    UserOut,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
auth_guard = Depends(rate_limit("auth", limit=10, window_s=60))


@router.post("/register", response_model=UserOut, status_code=201, dependencies=[auth_guard])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenPair, dependencies=[auth_guard])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(payload.refresh_token)


@router.post("/forgot-password", status_code=202, dependencies=[auth_guard])
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).forgot_password(payload.email)
    return {"detail": "If that email exists, a reset link has been sent"}


@router.post("/reset-password", dependencies=[auth_guard])
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).reset_password(payload.token, payload.new_password)
    return {"detail": "Password updated"}


# --- OAuth (Google / GitHub) — active when client credentials are configured ---
@router.get("/oauth/{provider}/url")
def oauth_url(provider: str):
    settings = get_settings()
    if provider == "google":
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Google OAuth not configured")
        return {
            "url": "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.OAUTH_REDIRECT_BASE}/api/v1/auth/oauth/google/callback"
            "&response_type=code&scope=openid%20email%20profile"
        }
    if provider == "github":
        if not settings.GITHUB_CLIENT_ID:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "GitHub OAuth not configured")
        return {
            "url": "https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}&scope=user:email"
        }
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown provider")


@router.get("/oauth/{provider}/callback")
def oauth_callback(provider: str, code: str, db: Session = Depends(get_db)):
    import httpx

    settings = get_settings()
    if provider == "google":
        if not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Google OAuth not configured")
        token_response = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.OAUTH_REDIRECT_BASE}/api/v1/auth/oauth/google/callback",
                "grant_type": "authorization_code",
            },
            timeout=15,
        ).json()
        userinfo = httpx.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_response.get('access_token', '')}"},
            timeout=15,
        ).json()
        email, name = userinfo.get("email"), userinfo.get("name", "")
        avatar = userinfo.get("picture")
    elif provider == "github":
        if not settings.GITHUB_CLIENT_SECRET:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "GitHub OAuth not configured")
        token_response = httpx.post(
            "https://github.com/login/oauth/access_token",
            data={
                "code": code,
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
            },
            headers={"Accept": "application/json"},
            timeout=15,
        ).json()
        gh_headers = {"Authorization": f"Bearer {token_response.get('access_token', '')}"}
        profile = httpx.get("https://api.github.com/user", headers=gh_headers, timeout=15).json()
        emails = httpx.get("https://api.github.com/user/emails", headers=gh_headers, timeout=15).json()
        primary = next((e["email"] for e in emails if isinstance(e, dict) and e.get("primary")), None)
        email = primary or profile.get("email")
        name = profile.get("name") or profile.get("login", "")
        avatar = profile.get("avatar_url")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown provider")

    if not email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Could not obtain email from provider")

    tokens = AuthService(db).oauth_login(email, name, provider, avatar)
    from fastapi.responses import RedirectResponse

    return RedirectResponse(
        f"{settings.FRONTEND_URL}/oauth-complete"
        f"#access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
    )
