"""
Application configuration.

Every setting the app needs is read from environment variables (or a .env file)
once, and exposed as a typed `Settings` object.

Why this matters:
- Secrets (DB password, API keys) never live in code.
- The same code runs locally, in Docker, and in the cloud just by changing env vars.
- Pydantic validates types, so a typo like POSTGRES_PORT=abc fails loudly at
  startup instead of silently at the first query.
"""

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # unrelated env vars (PATH, HOME, ...) are fine
    )

    # --- App ---
    app_name: str = "Personal AI Agent"
    app_env: str = Field(default="development", description="development | test | production")
    debug: bool = False

    # --- Database (individual parts, assembled into a URL below) ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "personal_agent"
    postgres_user: str = "agent"
    postgres_password: str = "agent"

    # --- CORS: which browser origin may call this API ---
    frontend_origin: str = "http://localhost:5173"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """SQLAlchemy connection string using the psycopg (v3) driver."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Build Settings once and reuse it for the whole process."""
    return Settings()
