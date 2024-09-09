# app/domain/repositories/movie_repository.py

from abc import ABC, abstractmethod

class MovieRepository(ABC):
    @abstractmethod
    async def get_movie(self, movie_id: str):
        pass

    @abstractmethod
    async def save_movie(self, movie_data: dict):
        pass
