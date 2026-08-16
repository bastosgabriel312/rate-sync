# app/domain/repositories/movie_api_client.py

from abc import ABC, abstractmethod
from typing import Any


class MovieAPIClient(ABC):
    @abstractmethod
    async def get_movie_rating(self, movie_title: str) -> Any:
        """
        Recupera a avaliação de um filme a partir de seu título.
        Args:
            movie_title (str): Título do filme.
        Returns:
            dict: Dados da avaliação do filme.
        """
        pass