# app/domain/use_cases/get_movie_ratings.py

from typing import Dict, Any

from app.api.v1.schemas import MovieReviewSource
from app.domain.repositories.movie_api_client import MovieAPIClient

class GetMovieRatings:
    def __init__(self, tmdb_client: MovieAPIClient, omdb_client: MovieAPIClient, letterboxd_client: MovieAPIClient):
        self.tmdb_client = tmdb_client
        self.omdb_client = omdb_client
        self.letterboxd_client = letterboxd_client

    async def execute(self, movie_title: str) -> dict[str:MovieReviewSource]:
        tmdb_rating = await self.tmdb_client.get_movie_rating(movie_title)
        omdb_rating = await self.omdb_client.get_movie_rating(movie_title)
        letterboxd_rating = await self.letterboxd_client.get_movie_rating(movie_title)

        return {
            "tmdb": tmdb_rating,
            "omdb": omdb_rating,
            "letterboxd": letterboxd_rating
        }
