# app/domain/use_cases/get_movie_ratings.py

import asyncio
from typing import Any

from app.core.cache import shared_cache
from app.core.config import settings
from app.domain.repositories.movie_api_client import MovieAPIClient

class GetMovieRatings:
    def __init__(self, cinemeta_client: MovieAPIClient, omdb_client: MovieAPIClient, letterboxd_client: MovieAPIClient, cache=None):
        self.cinemeta_client = cinemeta_client
        self.omdb_client = omdb_client
        self.letterboxd_client = letterboxd_client
        self._cache = cache if cache is not None else shared_cache

    async def execute(self, movie_title: str) -> dict[str, Any]:
        cache_key = f"ratings:{movie_title}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        cinemeta_rating, omdb_rating, letterboxd_rating = await asyncio.gather(
            self.cinemeta_client.get_movie_rating(movie_title),
            self.omdb_client.get_movie_rating(movie_title),
            self.letterboxd_client.get_movie_rating(movie_title),
            return_exceptions=True,
        )

        ratings = {
            "cinemeta": self._safe_result(cinemeta_rating),
            "omdb": self._safe_result(omdb_rating),
            "letterboxd": self._safe_result(letterboxd_rating),
        }

        self._cache.set(cache_key, ratings, ttl=settings.RATINGS_CACHE_TTL_SECONDS)
        return ratings

    @staticmethod
    def _safe_result(result: Any) -> Any:
        if isinstance(result, BaseException):
            return {"error": str(result)}
        return result