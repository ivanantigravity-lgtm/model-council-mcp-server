"""Configuration for the model council server."""

from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime configuration."""

    polza_api_key: str
    polza_base_url: str = "https://polza.ai/api/v1"
    grok_model: str = "x-ai/grok-4"
    gemini_model: str = "google/gemini-2.5-flash"
    deepseek_model: str = "deepseek/deepseek-chat-v3.1"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            polza_api_key=os.environ["POLZA_API_KEY"],
            polza_base_url=os.getenv("POLZA_BASE_URL", "https://polza.ai/api/v1").rstrip("/"),
            grok_model=os.getenv("COUNCIL_GROK_MODEL", "x-ai/grok-4"),
            gemini_model=os.getenv("COUNCIL_GEMINI_MODEL", "google/gemini-2.5-flash"),
            deepseek_model=os.getenv("COUNCIL_DEEPSEEK_MODEL", "deepseek/deepseek-chat-v3.1"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
