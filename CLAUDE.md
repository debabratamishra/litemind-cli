# CLAUDE.md — litemind-cli

Terminal TUI frontend (Textual) for the **LiteMindUI** FastAPI backend — streaming chat + RAG over local/cloud models, no browser. This repo is the **frontend only**; it needs the backend running at `http://localhost:8000`.

## Quick facts
- **Language**: Python ≥ 3.11, async (`httpx.AsyncClient` everywhere).
- **Key deps**: `textual` (TUI), `typer` (CLI), `httpx` (async HTTP), `python-dotenv`, `rich`.
- **Package manager**: `uv` (`uv sync`, `uv run litemind-cli`).
- **Backend**: separate repo `debabratamishra/litemind-ui` (FastAPI + Streamlit). CLI talks to its REST API.
- **Entry point**: `litemind_cli/main.py` (`litemind-cli` script) → `litemind_cli/app.py` (`LiteMindApp`).

## Commands
```bash
uv sync                                   # install deps
uv run litemind-cli [chat|rag|status]     # run TUI (chat=default)
uv run litemind-cli --backend URL --model M
uv run litemind-cli status                # check backend health + list models
uv run ruff check .                        # lint (line-length 120)
uv run mypy litemind_cli                   # type check
uv run pytest                              # tests
```

## Architecture (read-only mental model)
```
main.py  → Typer CLI, applies -b/-m overrides, launches LiteMindApp
app.py   → LiteMindApp: pushes MainScreen (tabs Chat|RAG|Settings) + SplashScreen overlay
config.py → Config dataclass singleton `config` (env/.env via load_dotenv; CLI flags override)
services/ → async singletons, one per backend concern:
  backend_service.py → /health, /models, /models/enhanced, /api/processing/capabilities
  chat_service.py    → /api/chat/stream (SSE), /api/chat/web-search, memory endpoints
  rag_service.py     → /api/rag/{upload,status,files,reset,query,save_config}
screens/  → ChatPanel, RAGPanel, SettingsPanel (Widgets inside TabPanes), SplashScreen (Screen)
widgets/  → message_list.py: MessageList + MessageBubble (Markdown-rendered)
```
- **Screens vs Panels**: only `SplashScreen` and `MainScreen` are `Screen`s. Chat/RAG/Settings are `Widget`s hosted in `TabPane`s (exactly one Header+Footer for the app).
- **Singletons**: `config`, `backend_service`, `chat_service`, `rag_service` are module-level — import directly, don't instantiate.
- **Streaming**: chat/rag services yield plain text. SSE from `/api/chat/stream` is parsed by `_parse_sse_chunk` → `obj["chunk"]`. RAG query/web-search yield raw text.
- **Provider UI**: `ollama` → model `Select` populated from `/models/enhanced` (local+cloud). `openrouter`/`nim` → free-text model `Input` + API key/base row (base pre-filled when switched).
- **Settings are runtime-only**: `SettingsPanel` mutates the `config` singleton but does NOT persist to `.env`. Persistence requires editing `.env`.

## Conventions
- `ruff`: `line-length = 120`, `target = py311`, `select = E,F,I,N,W`, `ignore = E501`.
- `mypy`: `python_version = 3.11`, `warn_return_any`, `warn_unused_configs`.
- All modules start with `from __future__ import annotations` and a module docstring.

## Backend API endpoints used (reference)
| Endpoint | Service method | Notes |
|---|---|---|
| `GET /health` | `check_health` | 200 = reachable |
| `GET /models` | `get_available_models` | flat list |
| `GET /models/enhanced` | `get_enhanced_models` | `{local_models, cloud_models}` |
| `GET /api/processing/capabilities` | `get_processing_capabilities` | optional |
| `POST /api/chat/stream` | `stream_chat` | SSE `{"chunk":...}` |
| `POST /api/chat/web-search` | `stream_web_search_chat` | plain text |
| `GET/POST /api/chat/memory/{stats,clear}/{session_id}` | `get_memory_stats`/`clear_memory` | |
| `POST /api/rag/upload`, `GET /api/rag/files`, `DELETE /api/rag/files/{name}`, `POST /api/rag/reset` | RAG file mgmt | |
| `POST /api/rag/query` | `stream_rag_query` | plain text |
| `POST /api/rag/save_config` | `save_configuration` | |

## Env / config (`.env`)
`FASTAPI_URL` (def `http://localhost:8000`), `DEFAULT_BACKEND` (`ollama|openrouter|nim`), `DEFAULT_MODEL` (def `llama3.2`), `API_BASE`, `API_KEY`, `CONNECT_TIMEOUT` (5), `READ_TIMEOUT` (600), `LOG_LEVEL` (INFO). CLI flags always win over env.
