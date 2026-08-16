# app/domain/use_cases/find_movie.py

from typing import Any

from app.core.cache import shared_cache
from app.core.config import settings
from app.infrastructure.api_clients.cinemeta_client import CinemetaClient


class FindMovie:
    def __init__(self, cinemeta_client: CinemetaClient, cache=None):
        self.cinemeta_client = cinemeta_client
        self._cache = cache if cache is not None else shared_cache

    async def execute(self, movie_title: str) -> list[dict[str, Any]] | dict[str, str]:
        cache_key = f"search:{movie_title}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        movie = await self.cinemeta_client.find_movie(movie_title)
        self._cache.set(cache_key, movie, ttl=settings.SEARCH_CACHE_TTL_SECONDS)
        return movie