from typing import ClassVar

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: ClassVar[str] = "Rate Sync"
    OMDB_API_KEY: str
    CINEMETA_BASE_URL: str = "https://v3-cinemeta.strem.io"
    SEARCH_CACHE_TTL_SECONDS: int = 3600
    RATINGS_CACHE_TTL_SECONDS: int = 900
    CORS_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://localhost:8100",
        "https://ratesync.vercel.app",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
