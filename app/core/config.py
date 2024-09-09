from typing import ClassVar

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: ClassVar[str] = "Rate Sync"
    TMDB_API_KEY: str
    OMDB_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
