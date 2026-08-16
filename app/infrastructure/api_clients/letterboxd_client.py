# app/infrastructure/api_clients/letterboxd_client.py

import asyncio
import json
import re
import unicodedata
from typing import Any

import requests

from app.domain.repositories.movie_api_client import MovieAPIClient


class LetterBoxdClient(MovieAPIClient):
    def __init__(self):
        self.base_url = "https://letterboxd.com/film/"

    async def get_movie_rating(self, movie_title: str) -> dict[str, Any]:
        try:
            return await asyncio.to_thread(self._fetch_movie_rating, movie_title)
        except Exception as exc:
            try:
                from app.core.monitor import incr
                incr('letterboxd.failures')
            except Exception:
                pass
            return {"error": str(exc)}

    def _fetch_movie_rating(self, movie_title: str) -> dict[str, Any]:
        slug = self.sanitize(movie_title)
        if not slug:
            return {"error": "Movie title missing"}

        url = f"{self.base_url}{slug}/"
        response = requests.get(
            url,
            headers=self._build_headers(),
            timeout=20,
            allow_redirects=True,
        )
        response.raise_for_status()

        return self._parse_rating(response.text, movie_title)

    def _build_headers(self) -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://letterboxd.com/",
        }

    def _parse_rating(self, html: str, movie_title: str) -> dict[str, Any]:
        for script in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S):
            try:
                payload = json.loads(script)
            except json.JSONDecodeError:
                continue

            rating_data = self._extract_rating_data(payload, movie_title)
            if rating_data is not None:
                return rating_data

        title_match = re.search(r'<meta name="production:name" content="([^"]+)"', html)
        year_match = re.search(r'<meta name="production:name-and-year" content="[^"]*\((\d{4})\)"', html)
        rating_match = re.search(r'"ratingValue"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?', html)

        if rating_match:
            year = int(year_match.group(1)) if year_match else None
            return {
                "title": title_match.group(1) if title_match else movie_title,
                "rating": float(rating_match.group(1)),
                "year": year,
            }

        fallback_title = title_match.group(1) if title_match else movie_title
        fallback_year = int(year_match.group(1)) if year_match else None
        if fallback_title:
            return {
                "title": fallback_title,
                "rating": None,
                "year": fallback_year,
            }

        # increment monitor for not-found upstream responses
        try:
            from app.core.monitor import incr
            incr('letterboxd.not_found')
        except Exception:
            pass

        return {"error": "Movie not found"}

    def _extract_rating_data(self, payload: Any, movie_title: str) -> dict[str, Any] | None:
        if isinstance(payload, list):
            for item in payload:
                result = self._extract_rating_data(item, movie_title)
                if result is not None:
                    return result
            return None

        if not isinstance(payload, dict):
            return None

        if payload.get("@type") != "Movie" and "aggregateRating" not in payload:
            return None

        rating_value = payload.get("aggregateRating", {}).get("ratingValue")
        year_value = payload.get("datePublished") or payload.get("releaseDate") or payload.get("dateCreated")
        year = int(str(year_value)[:4]) if year_value else None

        return {
            "title": payload.get("name") or movie_title,
            "rating": float(rating_value) if rating_value is not None else None,
            "year": year,
        }

    def sanitize(self, title: str) -> str:
        title = unicodedata.normalize('NFKD', title)
        title = title.encode('ascii', 'ignore').decode('ascii')
        title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        title = title.replace(' ', '-').lower().replace('--', '-')
        return title.strip('-')