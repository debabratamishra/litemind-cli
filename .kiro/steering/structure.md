---
inclusion: always
---

# Structure — litemind-cli

Textual TUI frontend for the LiteMindUI backend. One process, async HTTP to a separate backend.

## Top-level layout
```
litemind_cli/
  main.py                 Typer CLI entrypoint (commands: chat, rag, status)
  app.py                  LiteMindApp + MainScreen (tabs) + SplashScreen
  config.py               Config dataclass singleton `config`
  __init__.py             __version__ = "0.1.0"
  services/               async HTTP singletons (backend boundary)
    backend_service.py    health, model listing, capabilities
    chat_service.py       streaming chat (SSE), web-search, memory
    rag_service.py        upload, status, file mgmt, query streaming
  screens/                UI panels (Widgets) + one Screen
    splash_screen.py      SplashScreen (real Screen, auto-dismiss 5s)
    chat_screen.py        ChatPanel (Widget)
    rag_screen.py         RAGPanel (Widget)
    settings_screen.py    SettingsPanel (Widget)
  widgets/
    message_list.py       MessageList + MessageBubble (Markdown bubbles)
pyproject.toml            deps, ruff/mypy config, console script
README.md                 user docs
```

## How the pieces fit
- **main.py** parses Typer flags (`-b/--backend`, `-m/--model`, `--version`), applies overrides onto `config`, then `LiteMindApp(...).run()`.
- **app.py** `LiteMindApp.on_mount` pushes `MainScreen` then overlays `SplashScreen`, and runs `check_backend` (async worker) to set the subtitle / notify.
- **MainScreen** holds a single `TabbedContent` with three `TabPane`s — Chat / RAG / Settings — each yielding one panel `Widget`. One `Header`+`Footer` for the whole app.
- **config.py** `Config` is a dataclass populated from env/`.env` via `load_dotenv()`; flags override at launch. Imported as the singleton `config` everywhere.
- **services/** are module-level singletons (`backend_service`, `chat_service`, `rag_service`). Each builds an `httpx.Timeout` from `config`. They are the only place that knows backend URLs/paths.

## Conventions / invariants
- Only `SplashScreen` and `MainScreen` are `Screen`s. Chat/RAG/Settings are `Widget`s inside `TabPane`s.
- Singleton pattern: import `config` / `*_service` directly; never reinstantiate.
- Streaming services yield plain `str` chunks. SSE (`/api/chat/stream`) is normalized by `_parse_sse_chunk` → `obj["chunk"]`.
- Provider UI: `ollama` uses a model `Select` (filled from `/models/enhanced`); `openrouter`/`nim` use a free-text model `Input` plus an API key/base row (base URL auto-filled on switch).
- `SettingsPanel` mutates the `config` singleton but does **not** write `.env`.
- Keyboard: `1/2/3` tabs, `Ctrl+L` clear, `Ctrl+N` new session, `Ctrl+R` refresh files (RAG), `Ctrl+S` save (Settings), `Q` quit.

## Dependencies & tooling
- Runtime: `textual`, `typer`, `httpx`, `python-dotenv`, `rich`.
- Dev: `pytest`, `pytest-asyncio`, `ruff`, `mypy`. Install via `uv sync`.
- `ruff`: line-length 120, py311, select E,F,I,N,W, ignore E501. `mypy`: py311.
