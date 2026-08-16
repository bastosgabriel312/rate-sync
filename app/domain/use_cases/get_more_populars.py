# app/domain/use_cases/get_more_populars.py

from typing import Any
from app.infrastructure.api_clients.cinemeta_client import CinemetaClient


class GetMorePopulars:
    def __init__(self, cinemeta_client: CinemetaClient):
        self.cinemeta_client = cinemeta_client

    async def execute(self) -> list[dict[str, Any]] | dict[str, str]:
        more_populars = await self.cinemeta_client.find_more_populars()
        return more_populars