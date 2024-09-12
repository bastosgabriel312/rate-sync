# app/infrastructure/api_clients/letterboxd_client.py

import re
import unicodedata

from app.domain.repositories.movie_api_client import MovieAPIClient
from letterboxdpy.movie import Movie


class LetterBoxdClient(MovieAPIClient):
    def __init__(self):
        """LetterBoxdCLient started"""

    async def get_movie_rating(self, movie_title: str) -> dict[str:any]:
        try:
            movie_request = Movie(self.sanitize(movie_title))
            if movie_request:
                return {
                    'title': movie_request.title,
                    'rating': movie_request.rating,
                    'year': movie_request.year
                }
            return {"error": "Movie not found"}
        except Exception as e:
            print(e)
            return {"error": str(e)}

    def sanitize(self, title: str) -> str:
        title = unicodedata.normalize('NFKD', title)
        title = title.encode('ascii', 'ignore').decode('ascii')
        title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        title = title.replace(' ', '-').lower().replace('--','-')
        return title