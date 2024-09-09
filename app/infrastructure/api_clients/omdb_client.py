# app/infrastructure/api_clients/omdb_client.py

import requests
from app.core.config import settings
from app.domain.repositories.movie_api_client import MovieAPIClient


class OMDBClient(MovieAPIClient):
    def __init__(self):
        self.api_key = settings.OMDB_API_KEY
        self.base_url = "http://www.omdbapi.com/"

    async def get_movie_rating(self, movie_title: str) -> list[dict] | dict[str, str] | dict[str, str]:
        try:
            response = requests.get(self.base_url, params={
                't': movie_title,
                'apikey': self.api_key
            })
            data = response.json()
            if data.get('Response') == 'True':
                other_ratings = self.get_ratings(data, data.get('Title'))
                other_ratings.append({'imdb':{
                    'title': data.get('Title'),
                    'rating': data.get('imdbRating'),
                    'vote_count': data.get('imdbVotes'),
                    'year': data.get('Year'),
                    "source_name": 'IMDB'
                }})
                return other_ratings
            return {"error": "Movie not found"}
        except Exception as e:
            return {"error": str(e)}

    def get_ratings(self, data: dict, movie_title: str) -> list[dict]:
        source_mapping = {
            "Internet Movie Database": "imdb",
            "Rotten Tomatoes": "rotten_tomatoes",
            "Metacritic": "metacritic"
        }

        return [
            {
                source_mapping.get(rating['Source'], rating['Source']): {
                    "movie_title": movie_title,
                    "rating": rating['Value'],
                    "source_name":rating['Source']
                }
            }
            for rating in data.get('Ratings', [])
            if source_mapping.get(rating['Source'], rating['Source']) != "imdb"
        ]
