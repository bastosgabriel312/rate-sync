# tests/test_use_cases.py

from typing import Any

import pytest

from app.domain.use_cases.find_movie import FindMovie
from app.domain.use_cases.get_movie_ratings import GetMovieRatings
from app.core.cache import TTLCache


class FakeCinemeta:
    async def get_movie_rating(self, movie_title: str) -> dict[str, Any]:
        return {"title": movie_title, "rating": 8.5, "year": 2020}


class FakeOMDB:
    async def get_movie_rating(self, movie_title: str) -> list[dict] | dict[str, str]:
        return [{"imdb": {"title": movie_title, "rating": 8.2, "year": "2020"}}]


class FakeLetterboxd:
    async def get_movie_rating(self, movie_title: str) -> dict[str, Any]:
        return {"title": movie_title, "rating": 7.9, "year": 2020}


class FailingLetterboxd:
    async def get_movie_rating(self, movie_title: str) -> dict[str, Any]:
        raise RuntimeError("scraper offline")


class CountingCinemeta:
    def __init__(self):
        self.calls = 0

    async def find_movie(self, movie_title: str) -> list[dict[str, Any]] | dict[str, str]:
        self.calls += 1
        return [{"title": movie_title}]


async def test_get_movie_ratings_aggregates_all_sources():
    use_case = GetMovieRatings(FakeCinemeta(), FakeOMDB(), FakeLetterboxd(), cache=TTLCache())
    result = await use_case.execute("Inception")
    assert set(result.keys()) == {"cinemeta", "omdb", "letterboxd"}
    assert result["cinemeta"]["rating"] == 8.5
    assert result["omdb"][0]["imdb"]["rating"] == 8.2
    assert result["letterboxd"]["rating"] == 7.9


async def test_get_movie_ratings_isolates_provider_failure():
    use_case = GetMovieRatings(FakeCinemeta(), FakeOMDB(), FailingLetterboxd(), cache=TTLCache())
    result = await use_case.execute("Inception")
    assert result["cinemeta"]["rating"] == 8.5
    assert result["letterboxd"]["error"] == "scraper offline"


async def test_get_movie_ratings_uses_cache():
    cache = TTLCache()
    cinemeta = FakeCinemeta()
    use_case = GetMovieRatings(cinemeta, FakeOMDB(), FakeLetterboxd(), cache=cache)
    first = await use_case.execute("Inception")
    second = await use_case.execute("Inception")
    assert first == second
    assert cache.get("ratings:Inception") is not None


async def test_find_movie_uses_cache():
    cache = TTLCache()
    client = CountingCinemeta()
    use_case = FindMovie(client, cache=cache)
    first = await use_case.execute("Inception")
    second = await use_case.execute("Inception")
    assert first == second
    assert client.calls == 1