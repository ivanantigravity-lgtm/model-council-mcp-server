"""FastMCP server for a simple three-model scan."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from fastmcp import FastMCP

from .config import Settings
from .polza_client import PolzaClient


LOGGER = logging.getLogger(__name__)
MODEL_GUIDE = """Three-model scan guide:

China preset:
- moonshotai/kimi-k2.5
- qwen/qwen3.6-plus
- deepseek/deepseek-v3.2

USA preset:
- google/gemini-3.1-flash-lite-preview
- x-ai/grok-4.1-fast
- openai/gpt-5.4-nano

Use this server when you want three short perspectives and let Claude summarize them.
Do not use it for simple facts.
"""

COMPRESSION_RULES = (
    "No intro. Do not restate the task. Be concise. No fluff. "
    "Return only the useful answer."
)


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _message_text(response: dict[str, Any]) -> str:
    message = ((response.get("choices") or [{}])[0].get("message") or {})
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(part.strip() for part in parts if part).strip()
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False, indent=2)


def _sources(response: dict[str, Any]) -> list[str]:
    message = ((response.get("choices") or [{}])[0].get("message") or {})
    annotations = message.get("annotations") or []
    result = []
    for index, annotation in enumerate(annotations, start=1):
        citation = annotation.get("url_citation") if isinstance(annotation, dict) else None
        title = (
            (annotation.get("title") if isinstance(annotation, dict) else None)
            or (annotation.get("name") if isinstance(annotation, dict) else None)
            or (citation.get("title") if isinstance(citation, dict) else None)
            or f"Source {index}"
        )
        url = (
            (annotation.get("url") if isinstance(annotation, dict) else None)
            or (annotation.get("uri") if isinstance(annotation, dict) else None)
            or (annotation.get("source") if isinstance(annotation, dict) else None)
            or (citation.get("url") if isinstance(citation, dict) else None)
        )
        if url:
            result.append(f"{title} — {url}")
    return result


class CouncilEngine:
    """Run Grok, Gemini, and DeepSeek once each and return all results."""

    def __init__(self, settings: Settings, client: PolzaClient) -> None:
        self.settings = settings
        self.client = client

    def _preset_models(self, preset: str) -> list[tuple[str, str, str]]:
        if preset == "usa":
            return [
                (
                    "gemini",
                    self.settings.usa_gemini_model,
                    "You are Gemini. Give the most structured and balanced version of the answer. "
                    + COMPRESSION_RULES,
                ),
                (
                    "grok",
                    self.settings.usa_grok_model,
                    "You are Grok. Give a strong position fast. Be concrete and decisive, but do not ramble. "
                    + COMPRESSION_RULES,
                ),
                (
                    "openai",
                    self.settings.usa_openai_model,
                    "You are GPT. Be crisp, direct, and practically useful. "
                    + COMPRESSION_RULES,
                ),
            ]

        return [
            (
                "moonshot",
                self.settings.china_moonshot_model,
                "You are Kimi. Be practical, concise, and useful. Focus on execution and concrete next steps. "
                + COMPRESSION_RULES,
            ),
            (
                "qwen",
                self.settings.china_qwen_model,
                "You are Qwen. Be structured, compact, and sharp. Focus on trade-offs and clean framing. "
                + COMPRESSION_RULES,
            ),
            (
                "deepseek",
                self.settings.china_deepseek_model,
                "You are DeepSeek. Focus on logic, weak assumptions, and failure modes. "
                + COMPRESSION_RULES,
            ),
        ]

    async def _run_model(
        self,
        *,
        role_name: str,
        model: str,
        system_prompt: str,
        task_prompt: str,
        max_tokens: int = 500,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_prompt},
            ],
            "max_tokens": max_tokens,
        }
        response = await self.client.chat_completion(payload)
        return {
            "role": role_name,
            "model": model,
            "response": _message_text(response),
            "sources": _sources(response),
            "usage": response.get("usage") or {},
        }

    async def scan(
        self,
        *,
        task: str,
        context: str | None = None,
        preset: str = "china",
        format_hint: str = "verdict, 3 key points, 2 risks, recommendation",
    ) -> dict[str, Any]:
        context_block = context.strip() if context else "No extra context."
        shared_task = (
            f"Task:\n{task}\n\n"
            f"Context:\n{context_block}\n\n"
            f"Requested format:\n{format_hint}\n\n"
            f"Rules:\n{COMPRESSION_RULES}"
        )

        responses = await asyncio.gather(
            *[
                self._run_model(
                    role_name=role_name,
                    model=model,
                    system_prompt=system_prompt,
                    task_prompt=shared_task,
                )
                for role_name, model, system_prompt in self._preset_models(preset)
            ]
        )

        return {
            "task": task,
            "context": context_block,
            "preset": preset,
            "format_hint": format_hint,
            "responses": responses,
        }


def create_app() -> FastMCP:
    """Create FastMCP app."""
    settings = Settings.from_env()
    _setup_logging(settings.log_level)
    client = PolzaClient(settings)
    engine = CouncilEngine(settings, client)

    app = FastMCP(
        name="model-council-mcp-server",
        instructions=(
            "This server runs Grok, Gemini, and DeepSeek once each on the same task and returns "
            "three compact raw outputs for Claude to summarize."
        ),
    )

    @app.tool
    async def council_model_guide() -> str:
        """Return a short guide on the strengths, weaknesses, and best usage of Grok, Gemini, and DeepSeek."""
        return MODEL_GUIDE

    @app.tool
    async def tri_model_scan(
        task: str,
        context: str | None = None,
        preset: str = "china",
        format_hint: str = "verdict, 3 key points, 2 risks, recommendation",
    ) -> str:
        """Run the same task through Grok, Gemini, and DeepSeek once each and return compact JSON with raw model answers."""
        result = await engine.scan(task=task, context=context, preset=preset, format_hint=format_hint)
        return json.dumps(result, ensure_ascii=False, indent=2)

    @app.tool
    async def tri_model_compare(
        objective: str,
        options: list[str],
        context: str | None = None,
        preset: str = "china",
    ) -> str:
        """Compare several options through three different model families."""
        rendered_options = "\n".join(f"- {option}" for option in options)
        task = (
            f"Objective:\n{objective}\n\n"
            f"Options:\n{rendered_options}\n\n"
            "Compare the options and recommend the strongest one."
        )
        result = await engine.scan(
            task=task,
            context=context,
            preset=preset,
            format_hint="best option, 3 reasons, 2 risks, recommendation",
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    @app.tool
    async def tri_model_red_team(
        plan: str,
        success_criteria: str | None = None,
        context: str | None = None,
        preset: str = "china",
    ) -> str:
        """Stress-test a plan through three different model families."""
        task = (
            f"Plan:\n{plan}\n\n"
            f"Success criteria:\n{success_criteria or 'Not provided'}\n\n"
            "Stress-test this plan and surface weak assumptions, major risks, and practical fixes."
        )
        result = await engine.scan(
            task=task,
            context=context,
            preset=preset,
            format_hint="verdict, weak assumptions, 2 major risks, fixes, recommendation",
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    return app


def main() -> None:
    """Entrypoint for direct execution."""
    try:
        app = create_app()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as error:
        LOGGER.error("Server failed to start: %s", error, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
