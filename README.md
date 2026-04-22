# Model Council MCP Server

`mcp-name: io.github.ivanantigravity-lgtm/model-council-mcp-server`

MCP сервер, который один раз прогоняет одну и ту же задачу через 3 модели.

Есть 2 режима:

- `china`
- `usa`

Claude потом читает 3 коротких ответа и сам делает итоговую выжимку.

Это полезно там, где:

- задача неоднозначная
- есть риск самоуверенного ответа
- важны слабые места, возражения и trade-offs
- нужен не просто один ответ, а 3 разные перспективы

Это лишнее там, где:

- нужен простой факт
- нужен дешёвый быстрый ответ
- задача решается одной нормальной моделью

## Пресеты

`china`

- `moonshotai/kimi-k2.5`
- `qwen/qwen3.6-plus`
- `deepseek/deepseek-v3.2`

`usa`

- `google/gemini-3.1-flash-lite-preview`
- `x-ai/grok-4.1-fast`
- `openai/gpt-5.4-nano`

## Что умеет

- `tri_model_scan` — 3 модели отвечают на одну задачу
- `tri_model_compare` — сравнение нескольких вариантов
- `tri_model_red_team` — атака на идею, план или оффер
- `council_model_guide` — краткая памятка по сильным и слабым сторонам моделей

## Переменные окружения

```env
POLZA_API_KEY=YOUR_POLZA_API_KEY
POLZA_BASE_URL=https://polza.ai/api/v1
COUNCIL_CHINA_MOONSHOT_MODEL=moonshotai/kimi-k2.5
COUNCIL_CHINA_QWEN_MODEL=qwen/qwen3.6-plus
COUNCIL_CHINA_DEEPSEEK_MODEL=deepseek/deepseek-v3.2
COUNCIL_USA_GEMINI_MODEL=google/gemini-3.1-flash-lite-preview
COUNCIL_USA_GROK_MODEL=x-ai/grok-4.1-fast
COUNCIL_USA_OPENAI_MODEL=openai/gpt-5.4-nano
LOG_LEVEL=INFO
```

## Локальный запуск

```bash
uv run python -m model_council_mcp_server.server
```

## Что возвращает сервер

Сервер возвращает компактный JSON:

- задача
- контекст
- 3 сырых коротких ответа моделей
- источники по каждой модели

Claude уже сверху чистит это и делает короткую сводку для пользователя.

## Как выбирать режим

`china`

- если хочешь прогон по китайским моделям
- если нужен более альтернативный угол зрения для контента

`usa`

- если хочешь прогон по американским моделям
- если нужен более привычный стек для зрителя

## Принцип экономии контекста

Сервер заставляет модели отвечать коротко и по делу:

- без длинных вступлений
- без повторения исходной задачи
- без лишней “воды”
- с максимально коротким ответом
- без вступлений
- без повтора вопроса

Если задача простая, этот сервер лучше не использовать.
