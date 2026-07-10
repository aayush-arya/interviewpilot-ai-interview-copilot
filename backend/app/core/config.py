from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    DATABASE_URL: str = "sqlite:///./interview_copilot.db"
    CORS_ORIGINS: str = "http://localhost:5175,http://localhost:5173"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    ANTHROPIC_API_KEY: str = ""
    AI_MODEL: str = "claude-sonnet-4-6"
    AI_MODEL_DEEP: str = "claude-sonnet-4-6"

    REDIS_URL: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@interviewpilot.dev"

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_BASE: str = "http://localhost:8002"
    FRONTEND_URL: str = "http://localhost:5175"

    MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024
    CODE_TIMEOUT_SECONDS: float = 5.0

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def validate_production(self) -> None:
        if self.ENV == "production" and self.SECRET_KEY == "change-me-in-production":
            raise RuntimeError("SECRET_KEY must be set in production")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
