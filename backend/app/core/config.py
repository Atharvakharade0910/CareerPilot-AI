from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://careerpilot:careerpilot@127.0.0.1:55432/careerpilot"
    )
    frontend_origin: str = "http://localhost:3010"
    storage_dir: Path = Path("./private/resumes")
    secure_cookies: bool = False
    environment: str = "development"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.7-flash"
    sentry_dsn: str | None = None
    auth_rate_limit_per_minute: int = 30
    adzuna_app_id: str | None = None
    adzuna_app_key: SecretStr | None = None
    adzuna_country: str = "in"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
