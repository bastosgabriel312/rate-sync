# app/domain/use_cases/find_movie.py

from typing import Dict, Any, List
from app.infrastructure.api_clients.tmdb_client import TMDBClient


class FindMovie:
    def __init__(self, tmdb_client: TMDBClient):
        self.tmdb_client = tmdb_client

    async def execute(self, movie_title:str) -> list[dict[str, Any]] | dict[str, str]:
        movie = await self.tmdb_client.find_movie(movie_title)
        return movie
