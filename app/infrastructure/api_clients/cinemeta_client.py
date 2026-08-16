# app/infrastructure/api_clients/cinemeta_client.py

import httpx
from typing import Any
from urllib.parse import quote

from app.core.config import settings
from app.domain.repositories.movie_api_client import MovieAPIClient


class CinemetaClient(MovieAPIClient):
    BASE_URL = "https://v3-cinemeta.strem.io"

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.CINEMETA_BASE_URL or self.BASE_URL

    async def _get_json(self, path: str) -> dict[str, Any]:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(f"{self.base_url}{path}", timeout=10.0)
            response.raise_for_status()
            return response.json()

    async def _search(self, movie_title: str) -> list[dict[str, Any]]:
        data = await self._get_json(f"/catalog/movie/top/search={quote(movie_title)}.json")
        return data.get("metas", [])

    async def get_movie_rating(self, movie_title: str) -> dict[str, Any]:
        try:
            metas = await self._search(movie_title)
            if not metas:
                return {"error": "Movie not found"}
            meta = await self._get_json(f"/meta/movie/{metas[0]['imdb_id']}.json")
            meta = meta.get("meta", {})
            return {
                "title": meta.get("name"),
                "rating": self._to_float(meta.get("imdbRating")),
                "year": self._to_int(meta.get("releaseInfo")),
            }
        except Exception as e:
            return {"error": str(e)}

    async def find_movie(self, movie_title: str) -> list[dict[str, Any]] | dict[str, str]:
        try:
            metas = await self._search(movie_title)
            if not metas:
                return {"error": "Movie not found"}
            return [
                {
                    "title": meta.get("name"),
                    "overview": meta.get("description", ""),
                    "poster_path": meta.get("poster"),
                }
                for meta in metas
            ]
        except Exception as e:
            return {"error": str(e)}

    async def find_more_populars(self) -> list[dict[str, Any]] | dict[str, str]:
        try:
            data = await self._get_json("/catalog/movie/top.json")
            metas = data.get("metas", [])
            if not metas:
                return {"error": "Movie not found"}
            return [
                {
                    "title": meta.get("name"),
                    "overview": meta.get("description", ""),
                    "poster_path": meta.get("poster"),
                }
                for meta in metas
            ]
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None