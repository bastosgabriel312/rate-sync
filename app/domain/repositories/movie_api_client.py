# app/domain/repositories/movie_api_client.py

from abc import ABC, abstractmethod
from typing import Dict


class MovieAPIClient(ABC):
    @abstractmethod
    async def get_movie_rating(self, movie_id: str) -> Dict[str, any]:
        """
        Recupera a avaliação de um filme a partir de um ID de filme.
        Args:
            movie_id (str): ID do filme.
        Returns:
            dict: Dados da avaliação do filme.
        """
        pass
