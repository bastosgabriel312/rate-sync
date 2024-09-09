# app/infrastructure/api_clients/tmdb_client.py

from tmdbv3api import TMDb, Movie, Search
from app.core.config import settings
from app.domain.repositories.movie_api_client import MovieAPIClient
from typing import Dict, Any, List


class TMDBClient(MovieAPIClient):
    def __init__(self):
        self.tmdb = TMDb()
        self.tmdb.api_key = settings.TMDB_API_KEY
        self.search = Search()
        self.movie = Movie()

    async def get_movie_rating(self, movie_title: str) -> Dict[str, Any]:
        try:
            search = self.search.movies(movie_title)
            if search:
                movie = search[0]
                return {
                    'title': movie.title,
                    'rating': movie.vote_average,
                    'vote_count': movie.vote_count
                }
            return {"error": "Movie not found"}
        except Exception as e:
            return {"error": str(e)}

    async def find_movie(self, movie_title: str) -> list[Any] | dict[str, str] | dict[str, str]:
        try:
            search = self.search.movies(movie_title)
            if search:
                movies_search = [{'title': movie.title, 'overview': movie.overview, 'poster_path': movie.poster_path}
                                 for movie in search]
                return movies_search
            return {"error": "Movie not found"}
        except Exception as e:
            return {"error": str(e)}

    async def find_more_populars(self) -> list[dict[str, Any]] | dict[str, str] | dict[str, str]:
        try:
            popular = self.movie.popular()
            populars = []
            for p in popular:
                populars.append(
                    {'title': p.title,
                     'overview': p.overview,
                     'poster_path': p.poster_path
                     })
            return populars
        except Exception as e:
            return {"error": str(e)}
