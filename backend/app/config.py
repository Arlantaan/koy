from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    admin_password: str = "changeme"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/koya"
    cors_origins: list[str] = ["http://localhost", "http://localhost:3000", "http://localhost:5173", "https://koya.living"]
    debug: bool = False
    jwt_secret: str = "changeme-jwt-secret-please-change"
    google_client_id: str = ""
    upload_dir: str = "/var/www/koya/uploads"
    resend_api_key: str = ""
    email_from: str = "Koya Restaurant <comedine@koya.living>"


settings = Settings()
