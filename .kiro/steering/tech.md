---
inclusion: always
---

# Tech — litemind-cli

## Stack
- **Language**: Python ≥ 3.11 (uses `from __future__ import annotations`, `X | None` unions).
- **TUI**: [Textual](https://textual.textualize.io/) — `App`, `Screen`, `Widget`, `work` async workers, `TabbedContent`/`TabPane`, reactive CSS via `DEFAULT_CSS`.
- **CLI**: [Typer](https://typer.tiangolo.com/) — `litemind-cli` console script → `litemind_cli.main:app`.
- **HTTP**: `httpx` async (`AsyncClient`, `client.stream`, `aiter_lines`/`aiter_text`). No `requests`.
- **Config**: `python-dotenv` (`load_dotenv()` in `config.py`).
- **Terminal text**: `rich` / Textual `Markdown` (chat bubbles render Markdown).

## Build & run
- Package manager: **uv**. `uv sync` installs deps + dev group.
- Run: `uv run litemind-cli [chat|rag|status]`. Global install: `uv tool install .`.
- Lint: `uv run ruff check .` · Types: `uv run mypy litemind_cli` · Tests: `uv run pytest`.
- Build backend: `hatchling` (wheel packages = `litemind_cli`).

## Async model
- All backend I/O goes through `httpx.AsyncClient` inside Textual `@work` workers (`thread=False`).
- Services yield `AsyncIterator[str]` for streaming; callers append chunks to a `MessageBubble`.
- Timeouts come from `config.connect_timeout` / `read_timeout` (RAG uploads get a longer write/upload timeout).

## Configuration & env
- Loaded in `config.py` from env / `.env` (via `load_dotenv()`); CLI flags override at launch.
- Vars: `FASTAPI_URL` (def `http://localhost:8000`), `DEFAULT_BACKEND` (`ollama|openrouter|nim`), `DEFAULT_MODEL` (`llama3.2`), `API_BASE`, `API_KEY`, `CONNECT_TIMEOUT` (5), `READ_TIMEOUT` (600), `LOG_LEVEL` (INFO).
- Generation defaults in `Config`: `temperature=0.7`, `max_tokens=2048`, `top_p=0.9`, `frequency_penalty=0.0`, `repetition_penalty=1.0`. RAG: `default_chunk_size=500`, `default_n_results=3`.

## Backend API contract (endpoints this frontend calls)
- `GET /health` — health
- `GET /models` — flat model list
- `GET /models/enhanced` — `{local_models:[{name,...}], cloud_models:[...]}`
- `GET /api/processing/capabilities` — optional capability probe
- `POST /api/chat/stream` — SSE `data: {"chunk": "..."}` (normalized to plain text)
- `POST /api/chat/web-search` — plain-text stream
- `GET/POST /api/chat/memory/{stats,clear}/{session_id}`
- `POST /api/rag/upload` (multipart `files` + `chunk_size`), `GET /api/rag/files`, `DELETE /api/rag/files/{filename}`, `POST /api/rag/reset`, `POST /api/rag/save_config`
- `POST /api/rag/query` — plain-text stream
- Full contract: litemind-ui `docs/api-contract.md`.

## Conventions
- Every module: `from __future__ import annotations` + docstring at top.
- Singletons imported directly (`config`, `backend_service`, `chat_service`, `rag_service`).
- SSE parsing centralised in `chat_service._parse_sse_chunk` (handles `data:` prefix + JSON `chunk`/`text`/`content`, falls back to plain text).
- RAG upload MIME map in `rag_service._MIME_MAP`; supported: pdf, docx, txt, md, csv, xlsx, pptx, html, odt, rtf, yaml, json.
