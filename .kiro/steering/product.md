---
inclusion: always
---

# Product — litemind-cli

**LiteMind CLI** is a terminal user interface (TUI) for the [LiteMindUI](https://github.com/debabratamishra/litemind-ui) backend. It lets users chat with local and cloud AI models and query their own documents (RAG) — all from the terminal, no browser required.

## What it is
- A **frontend-only** terminal client. It does not run models itself; it calls a running LiteMindUI FastAPI backend (default `http://localhost:8000`).
- Built with [Textual](https://textual.textualize.io/).

## Core capabilities
- **Chat** — streaming AI chat with full conversation history; inline provider/model switching mid-session.
- **RAG** — upload documents, index them, and query a knowledge base with streaming responses.
- **Provider switching** — Ollama (local+cloud), OpenRouter, and NIM, selected from the toolbar.

## Target user
- Developers/technical users who want a fast, keyboard-driven terminal interface to LiteMindUI instead of the Streamlit web frontend.

## Why it exists
- Companion to litemind-ui for users who prefer the terminal. Mirrors litemind-ui's frontend services (chat/rag/backend) but reimplemented async with `httpx` to fit inside Textual's async worker model.

## Non-goals
- Not a backend, model server, or embedding engine.
- Settings changes are session-scoped; persisting config is out of scope (users edit `.env`).
