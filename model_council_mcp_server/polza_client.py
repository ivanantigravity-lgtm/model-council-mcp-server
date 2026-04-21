"""Polza client for model council."""

from __future__ import annotations

from typing import Any

import httpx

from .config import Settings


class PolzaClient:
    """Thin async client for Polza chat completions."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self._settings.polza_base_url,
            timeout=180.0,
            headers={"Authorization": f"Bearer {self._settings.polza_api_key}"},
        ) as client:
            response = await client.post("/chat/completions", json=payload)

        response.raise_for_status()
        return response.json()
