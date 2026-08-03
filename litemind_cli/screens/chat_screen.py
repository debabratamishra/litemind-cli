"""
Chat panel — streaming AI conversation.

Provider-aware toolbar:
  - ollama     → model picker populated from /models/enhanced (local + cloud)
  - openrouter → free-text model input + API key / base row
  - nim        → free-text model input + API key / base row

No web-search.
"""

from __future__ import annotations

import uuid

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select

from ..config import config
from ..services.chat_service import chat_service
from ..widgets.message_list import MessageBubble, MessageList

_OR_PLACEHOLDER  = "e.g. openai/gpt-4o  or  meta-llama/llama-3.3-70b-instruct"
_NIM_PLACEHOLDER = "e.g. meta/llama-3.3-70b-instruct"

# (label, value) — Textual Select expects label first
_PROVIDERS = [("🦙 Ollama", "ollama"), ("🌐 OpenRouter", "openrouter"), ("⚡ NIM", "nim")]


class ChatPanel(Widget):
    """Streaming chat panel hosted inside a TabPane."""

    BINDINGS = [
        Binding("ctrl+l", "clear_chat",  "Clear chat"),
        Binding("ctrl+n", "new_session", "New session"),
        Binding("super+c", "copy_message", "Copy last msg"),
        Binding("super+v", "paste_message", "Paste"),
    ]

    DEFAULT_CSS = """
    ChatPanel {
        layout: vertical;
        height: 1fr;
    }

    #toolbar {
        height: auto;
        padding: 0 1;
        background: $panel;
        layout: vertical;
    }

    #toolbar-row1 {
        height: 3;
        layout: horizontal;
        align: left middle;
    }

    #toolbar-row2 {
        height: 3;
        layout: horizontal;
        align: left middle;
        display: none;
    }

    .tb-label { width: auto; margin-right: 1; color: $text-muted; }

    #provider-select { width: 20; margin-right: 2; }
    #model-select    { width: 1fr; }
    #model-input     { width: 1fr; display: none; }
    #apikey-input    { width: 1fr; }
    #apibase-input   { width: 1fr; margin-left: 1; }

    #message-list { height: 1fr; }

    #input-row {
        height: 3;
        padding: 0 1;
        layout: horizontal;
    }

    #message-input { width: 1fr; }
    #send-btn { width: 10; margin-left: 1; }
    """

    def __init__(self, initial_model: str | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._model      = initial_model or config.default_model
        self._backend    = config.default_backend
        self._api_key    = config.api_key or ""
        self._api_base   = config.api_base or ""
        self._session_id = str(uuid.uuid4())
        self._history: list[dict[str, str]] = []
        self._streaming  = False

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        with Vertical(id="toolbar"):
            with Horizontal(id="toolbar-row1"):
                yield Label("Provider:", classes="tb-label")
                yield Select(_PROVIDERS, value=self._backend, id="provider-select")
                yield Label("Model:", classes="tb-label")
                yield Select(
                    [(self._model, self._model)],
                    value=self._model,
                    id="model-select",
                )
                yield Input(
                    value=self._model if self._backend != "ollama" else "",
                    placeholder=_OR_PLACEHOLDER,
                    id="model-input",
                )
            with Horizontal(id="toolbar-row2"):
                yield Label("API key:", classes="tb-label")
                yield Input(value=self._api_key, placeholder="sk-…",
                            password=True, id="apikey-input")
                yield Label("API base:", classes="tb-label")
                yield Input(value=self._api_base,
                            placeholder="https://openrouter.ai/api/v1",
                            id="apibase-input")

        yield MessageList(id="message-list")
        with Horizontal(id="input-row"):
            yield Input(placeholder="Type a message and press Enter…", id="message-input")
            yield Button("Send", id="send-btn", variant="primary")

    def on_mount(self) -> None:
        self._apply_provider_ui(self._backend)
        self.load_models()
        self.query_one("#message-input", Input).focus()

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    @work(exclusive=False, thread=False)
    async def load_models(self) -> None:
        """Fetch local + cloud Ollama models and populate the picker."""
        from ..services.backend_service import backend_service

        data  = await backend_service.get_enhanced_models()
        local = [m["name"] for m in data.get("local_models", [])]
        cloud = [m["name"] for m in data.get("cloud_models", [])]

        all_models = local + (["── cloud ──"] + cloud if cloud else [])
        if not all_models:
            all_models = [self._model]

        sel: Select = self.query_one("#model-select", Select)
        sel.set_options([(m, m) for m in all_models])
        if self._model in all_models:
            sel.value = self._model
        elif local:
            sel.value = local[0]
            self._model = local[0]

    @work(exclusive=True, thread=False)
    async def send_message(self, text: str) -> None:
        if self._streaming:
            return
        self._streaming = True

        msg_list: MessageList = self.query_one("#message-list", MessageList)
        msg_list.add_message("user", text)
        self._history.append({"role": "user", "content": text})
        bubble = msg_list.add_message("assistant")
        full_response = ""

        api_key  = self.query_one("#apikey-input",  Input).value.strip() or None
        api_base = self.query_one("#apibase-input", Input).value.strip() or None

        try:
            stream = chat_service.stream_chat(
                text,
                model=self._model,
                backend=self._backend,
                api_key=api_key,
                api_base=api_base,
                conversation_history=self._history[:-1],
                session_id=self._session_id,
            )
            async for chunk in stream:
                full_response += chunk
                bubble.append_text(chunk)
                msg_list.scroll_end(animate=False)
        except Exception as exc:  # noqa: BLE001
            bubble.append_text(f"\n\n⚠ {exc}")
        finally:
            self._history.append({"role": "assistant", "content": full_response})
            self._streaming = False

    # ------------------------------------------------------------------
    # Provider UI switching
    # ------------------------------------------------------------------

    def _apply_provider_ui(self, backend: str) -> None:
        is_ollama = backend == "ollama"

        self.query_one("#model-select", Select).display  = is_ollama
        self.query_one("#model-input",  Input).display   = not is_ollama
        self.query_one("#toolbar-row2", Horizontal).display = not is_ollama

        if not is_ollama:
            self.query_one("#model-input", Input).placeholder = (
                _NIM_PLACEHOLDER if backend == "nim" else _OR_PLACEHOLDER
            )
            ab = self.query_one("#apibase-input", Input)
            if not ab.value:
                ab.value = (
                    "https://integrate.api.nvidia.com/v1" if backend == "nim"
                    else "https://openrouter.ai/api/v1"
                )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    @on(Select.Changed, "#provider-select")
    def on_provider_changed(self, event: Select.Changed) -> None:
        if event.value and str(event.value) != self._backend:
            self._backend = str(event.value)
            self._apply_provider_ui(self._backend)

    @on(Select.Changed, "#model-select")
    def on_model_select_changed(self, event: Select.Changed) -> None:
        val = str(event.value) if event.value else ""
        if val and not val.startswith("──"):
            self._model = val

    @on(Input.Changed, "#model-input")
    def on_model_input_changed(self, event: Input.Changed) -> None:
        self._model = event.value.strip()

    @on(Button.Pressed, "#send-btn")
    def on_send(self) -> None:
        inp: Input = self.query_one("#message-input", Input)
        text = inp.value.strip()
        if text:
            inp.value = ""
            self.send_message(text)

    @on(Input.Submitted, "#message-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text:
            event.input.value = ""
            self.send_message(text)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_clear_chat(self) -> None:
        self.query_one("#message-list", MessageList).clear()
        self._history.clear()

    def action_new_session(self) -> None:
        self.action_clear_chat()
        self._session_id = str(uuid.uuid4())
        self.app.notify("New chat session started")

    def action_copy_message(self) -> None:
        """Copy the last assistant message to the system clipboard."""
        msg_list: MessageList = self.query_one("#message-list", MessageList)
        for child in reversed(list(msg_list.children)):
            if isinstance(child, MessageBubble) and child._role == "assistant":
                self.app.copy_to_clipboard(child._content)
                self.app.notify("Copied to clipboard")
                return
        self.app.notify("No assistant message to copy", severity="warning")

    def action_paste_message(self) -> None:
        """Paste clipboard content into the message input."""
        inp: Input = self.query_one("#message-input", Input)
        inp.focus()
        inp.value = self.app.clipboard
