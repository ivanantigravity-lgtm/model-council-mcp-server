"""Configuration for the model council server."""

from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime configuration."""

    polza_api_key: str
    polza_base_url: str = "https://polza.ai/api/v1"
    china_moonshot_model: str = "moonshotai/kimi-k2.5"
    china_qwen_model: str = "qwen/qwen3.6-plus"
    china_deepseek_model: str = "deepseek/deepseek-v3.2"
    usa_gemini_model: str = "google/gemini-3.1-flash-lite-preview"
    usa_grok_model: str = "x-ai/grok-4.1-fast"
    usa_openai_model: str = "openai/gpt-5.4-nano"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.environ.get("POLZA_AI_API_KEY") or os.environ.get("POLZA_API_KEY")
        if not api_key:
            raise KeyError("POLZA_AI_API_KEY")
        return cls(
            polza_api_key=api_key,
            polza_base_url=os.getenv("POLZA_BASE_URL", "https://polza.ai/api/v1").rstrip("/"),
            china_moonshot_model=os.getenv("COUNCIL_CHINA_MOONSHOT_MODEL", "moonshotai/kimi-k2.5"),
            china_qwen_model=os.getenv("COUNCIL_CHINA_QWEN_MODEL", "qwen/qwen3.6-plus"),
            china_deepseek_model=os.getenv("COUNCIL_CHINA_DEEPSEEK_MODEL", "deepseek/deepseek-v3.2"),
            usa_gemini_model=os.getenv("COUNCIL_USA_GEMINI_MODEL", "google/gemini-3.1-flash-lite-preview"),
            usa_grok_model=os.getenv("COUNCIL_USA_GROK_MODEL", "x-ai/grok-4.1-fast"),
            usa_openai_model=os.getenv("COUNCIL_USA_OPENAI_MODEL", "openai/gpt-5.4-nano"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
