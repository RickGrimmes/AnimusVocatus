from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    PORT: int = 8000
    DEBUG: bool = True

    # Base de Datos
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vocatus_animus"

    # Seguridad y Tokens
    SECRET_KEY: str = "insecure_dev_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    GUEST_TOKEN_EXPIRE_HOURS: int = 24
    HOST_TOKEN_EXPIRE_DAYS: int = 7

    # Cloudflare R2
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "vocatus-animus-media"
    R2_ENDPOINT_URL: str = ""
    R2_PUBLIC_DOMAIN: str = ""

    # Correo Transaccional (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Vocatus & Animus <noreply@tudominio.com>"

    # Frontend y CORS
    FRONTEND_URL: str = "http://localhost:4321"
    ADMIN_URL: str = "http://localhost:4321/admin"

    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parent.parent.parent.parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
