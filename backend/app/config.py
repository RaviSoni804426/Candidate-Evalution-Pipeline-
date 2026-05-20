from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Candidate Evaluation Pipeline"
    database_url: str = "sqlite:///./candidate_evaluation.db"
    storage_dir: Path = Path("backend/storage")
    api_cors_origins: str = "http://localhost:5173"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    (settings.storage_dir / "resumes").mkdir(parents=True, exist_ok=True)
    return settings
