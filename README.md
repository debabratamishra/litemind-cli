# LiteMind CLI

```
  _     _ _       __  __ _           _    ____ _     ___ 
 | |   (_) |_ ___|  \/  (_)_ __   __| |  / ___| |   |_ _|
 | |   | | __/ _ \ |\/| | | '_ \ / _` | | |   | |    | | 
 | |___| | ||  __/ |  | | | | | | (_| | | |___| |___ | | 
 |_____|_|\__\___|_|  |_|_|_| |_|\__,_|  \____|_____|___|

         Terminal interface for LiteMindUI  ·  Chat · RAG
```

A fully-featured terminal user interface (TUI) for the
[LiteMindUI](https://github.com/debabratamishra/litemind-ui) backend,
built with [Textual](https://textual.textualize.io/).

Chat with local and cloud AI models, and query your own documents — all from
your terminal, with no browser required.

---

## Features

| | Feature | Description |
|---|---|---|
| 💬 | **Chat** | Streaming AI chat with full conversation history |
| 📚 | **RAG** | Upload documents, query your knowledge base |
| 🔄 | **Provider switching** | Switch provider and model mid-session, inline in the toolbar |

---

## Requirements

- **Python ≥ 3.11**
- A running **LiteMindUI backend** at `http://localhost:8000`
  ([quick-start here](https://github.com/debabratamishra/litemind-ui#quick-start))
- [uv](https://docs.astral.sh/uv/) *(recommended)* or pip

---

## Quick start

### 1. Start the LiteMindUI backend

The CLI is a frontend — it needs the backend running first.

```bash
# Option A — Docker (easiest)
curl -fsSL https://raw.githubusercontent.com/debabratamishra/litemind-ui/main/install.sh | bash

# Option B — from source
git clone https://github.com/debabratamishra/litemind-ui.git
cd litemind-ui
make up
```

Backend will be available at `http://localhost:8000`.

### 2. Install and run litemind-cli

```bash
git clone https://github.com/debabratamishra/litemind-cli.git
cd litemind-cli

# Install dependencies
uv sync

# (Optional) configure environment
cp .env.example .env
# edit .env if your backend runs somewhere other than localhost:8000

# Launch the TUI
uv run litemind-cli
```

Or install globally as a tool:

```bash
uv tool install .
litemind-cli
```

---

## Usage

```
Usage: litemind-cli [OPTIONS] COMMAND [ARGS]...

  LiteMind CLI — terminal interface for the LiteMindUI backend.

Options:
  -b, --backend TEXT   Backend URL  [env: FASTAPI_URL]
  -m, --model TEXT     Default model name  [env: DEFAULT_MODEL]
  --version            Show version and exit
  --help               Show this message and exit

Commands:
  chat    Open the TUI on the Chat tab
  rag     Open the TUI on the RAG tab
  status  Check backend connectivity and print available models
```

### Examples

```bash
# Open on the Chat tab (default)
litemind-cli

# Open directly on the RAG tab
litemind-cli rag

# Use a remote backend
litemind-cli --backend http://192.168.1.10:8000

# Override model at launch
litemind-cli --model mistral:7b

# Check if the backend is reachable
litemind-cli status
```

---

## Inside the TUI

### Switching providers

The toolbar at the top of both Chat and RAG tabs has an inline provider selector:

| Selection | What appears |
|---|---|
| 🦙 **Ollama** | Model dropdown — auto-populated with your local + cloud Ollama models |
| 🌐 **OpenRouter** | Model text field + API key + API base URL |
| ⚡ **NIM** | Model text field + API key + API base URL (pre-filled) |

API base URLs are pre-filled automatically when you switch provider. You only
need to enter your API key.

**OpenRouter model format:** `provider/model-name`  
e.g. `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`, `meta-llama/llama-3.3-70b-instruct`

**NIM model format:** `org/model-name`  
e.g. `meta/llama-3.3-70b-instruct`, `nvidia/llama-3.1-nemotron-70b-instruct`

### RAG — uploading documents

In the RAG tab, enter one or more file paths (space-separated) in the upload
field and click **Upload**:

```
/Users/me/docs/report.pdf /Users/me/notes/meeting.md
```

Supported formats: PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML, ODT, RTF, YAML, JSON

### Keyboard shortcuts

| Key | Action |
|---|---|
| `1` | Switch to Chat tab |
| `2` | Switch to RAG tab |
| `3` | Switch to Settings tab |
| `Enter` | Send message |
| `Ctrl+L` | Clear current conversation |
| `Ctrl+N` | Start a new chat session |
| `Ctrl+R` | Refresh RAG file list *(RAG tab only)* |
| `Ctrl+S` | Save settings *(Settings tab only)* |
| `Q` | Quit |

---

## Configuration

All options can be set in a `.env` file (copy from `.env.example`) or as
environment variables. CLI flags always take precedence.

| Variable | Default | Description |
|---|---|---|
| `FASTAPI_URL` | `http://localhost:8000` | LiteMindUI backend URL |
| `DEFAULT_BACKEND` | `ollama` | Provider: `ollama` · `openrouter` · `nim` |
| `DEFAULT_MODEL` | `llama3.2` | Default model name |
| `API_BASE` | *(empty)* | Override provider API base URL |
| `API_KEY` | *(empty)* | Provider API key |
| `CONNECT_TIMEOUT` | `5` | HTTP connect timeout in seconds |
| `READ_TIMEOUT` | `600` | HTTP read/stream timeout in seconds |
| `LOG_LEVEL` | `INFO` | `DEBUG` · `INFO` · `WARNING` · `ERROR` |

Example `.env` for OpenRouter:

```env
FASTAPI_URL=http://localhost:8000
DEFAULT_BACKEND=openrouter
DEFAULT_MODEL=openai/gpt-4o-mini
API_KEY=sk-or-your-key-here
```

---

## Project layout

```
litemind_cli/
  config.py              env / config loading (singleton)
  app.py                 Textual App — MainScreen + SplashScreen
  main.py                Typer CLI entrypoint
  services/
    backend_service.py   health check, model listing
    chat_service.py      streaming chat (SSE parser included)
    rag_service.py       file upload, RAG query streaming
  screens/
    splash_screen.py     ASCII art intro (auto-dismisses after 3 s)
    chat_screen.py       Chat panel (Widget)
    rag_screen.py        RAG panel (Widget)
    settings_screen.py   Settings panel (Widget)
  widgets/
    message_list.py      scrollable chat bubble widget
```

---

## Dependencies

| Package | Purpose |
|---|---|
| [textual](https://github.com/Textualize/textual) | TUI framework |
| [typer](https://typer.tiangolo.com/) | CLI interface |
| [httpx](https://www.python-httpx.org/) | Async HTTP client |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | `.env` loading |
| [rich](https://github.com/Textualize/rich) | Terminal formatting |

---

## Related

- [litemind-ui](https://github.com/debabratamishra/litemind-ui) — FastAPI backend + Streamlit web frontend
- [API contract](https://github.com/debabratamishra/litemind-ui/blob/main/docs/api-contract.md) — HTTP API reference for frontend developers
