# app/domain/use_cases/get_more_populars.py

from typing import Dict, Any, List
from app.infrastructure.api_clients.tmdb_client import TMDBClient


class GetMorePopulars:
    def __init__(self, tmdb_client: TMDBClient):
        self.tmdb_client = tmdb_client
    async def execute(self) -> list[dict[str, Any]] | dict[str, str]:
        more_populars = await self.tmdb_client.find_more_populars()
        return more_populars
