# Model Council MCP Server

`mcp-name: io.github.ivanantigravity-lgtm/model-council-mcp-server`

MCP сервер, который прогоняет одну и ту же задачу через **3 модели параллельно** и возвращает Claude их короткие ответы. Claude сам сверху делает итоговую выжимку.

Два пресета:

- `china` — Moonshot Kimi, Qwen, DeepSeek
- `usa` — Gemini, Grok, OpenAI

## Когда вызывать

Полезно, когда:

- задача неоднозначная
- есть риск самоуверенного ответа одной модели
- важны слабые места, возражения, trade-offs
- нужно 3 разные перспективы, а не один ответ

Не надо вызывать для:

- простого факта
- быстрой суммаризации
- задачи, которую решит одна нормальная модель

## Что нужно для установки

- `Claude Desktop` или `Claude Code`
- [`uv`](https://docs.astral.sh/uv/)
- Python 3.11+
- `POLZA_AI_API_KEY` — ключ берётся на [polza.ai/dashboard/api-keys](https://polza.ai/dashboard/api-keys)

Поставить `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Установка за 2 минуты (через PyPI + uvx)

### Claude Code / VS Code

Создай `.mcp.json` в корне проекта:

```json
{
  "mcpServers": {
    "model-council": {
      "command": "uvx",
      "args": ["model-council-mcp-server@latest"],
      "env": {
        "POLZA_AI_API_KEY": "your-polza-api-key-here"
      }
    }
  }
}
```

Перезапусти Claude Code.

### Claude Desktop (macOS)

Файл `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "model-council": {
      "command": "uvx",
      "args": ["model-council-mcp-server@latest"],
      "env": {
        "POLZA_AI_API_KEY": "your-polza-api-key-here"
      }
    }
  }
}
```

### Claude Desktop (Windows)

Файл: `%APPDATA%\Claude\claude_desktop_config.json`. Содержимое идентичное.

## Как проверить, что работает

После перезапуска Claude попроси:

> Прогони через model council (usa) задачу: стоит ли мне добавить подписку в мой продукт?

Claude должен вызвать tool `tri_model_scan` и вернуть 3 коротких ответа.

## Tools

- `tri_model_scan` — 3 модели отвечают на одну задачу
- `tri_model_compare` — сравнение нескольких вариантов
- `tri_model_red_team` — атака на идею, план или оффер
- `council_model_guide` — краткая памятка по сильным и слабым сторонам моделей

У каждого tool есть параметр `preset` (`china` или `usa`).

## Пресеты

### `china`

- `moonshotai/kimi-k2.5`
- `qwen/qwen3.6-plus`
- `deepseek/deepseek-v3.2`

### `usa`

- `google/gemini-3.1-flash-lite-preview`
- `x-ai/grok-4.1-fast`
- `openai/gpt-5.4-nano`

Проверить актуальность ID моделей можно через `GET https://polza.ai/api/v1/models/catalog`. Если какая-то модель у Polza переименована — подставь свой ID через переменные окружения ниже.

## Переменные окружения

| Переменная | Обязательная | По умолчанию |
| --- | --- | --- |
| `POLZA_AI_API_KEY` | да | — |
| `POLZA_BASE_URL` | нет | `https://polza.ai/api/v1` |
| `COUNCIL_CHINA_MOONSHOT_MODEL` | нет | `moonshotai/kimi-k2.5` |
| `COUNCIL_CHINA_QWEN_MODEL` | нет | `qwen/qwen3.6-plus` |
| `COUNCIL_CHINA_DEEPSEEK_MODEL` | нет | `deepseek/deepseek-v3.2` |
| `COUNCIL_USA_GEMINI_MODEL` | нет | `google/gemini-3.1-flash-lite-preview` |
| `COUNCIL_USA_GROK_MODEL` | нет | `x-ai/grok-4.1-fast` |
| `COUNCIL_USA_OPENAI_MODEL` | нет | `openai/gpt-5.4-nano` |
| `LOG_LEVEL` | нет | `INFO` |

## Что возвращает сервер

Компактный JSON:

- задача
- контекст
- 3 сырых коротких ответа от моделей
- источники по каждой модели

Сервер заставляет модели отвечать коротко, без воды и без повтора вопроса — чтобы не раздувать контекст Claude.

## Локальная разработка

```bash
git clone https://github.com/ivanantigravity-lgtm/model-council-mcp-server.git
cd model-council-mcp-server
uv sync
POLZA_AI_API_KEY=your_key uv run python -m model_council_mcp_server.server
```

## Лицензия

MIT.
