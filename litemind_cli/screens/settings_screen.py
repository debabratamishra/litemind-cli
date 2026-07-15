"""
Settings panel — configure backend URL, model, provider, and generation params.

Widget (not Screen) — hosted inside a TabPane. No own Header/Footer.

Changes update the live `config` singleton but are NOT persisted to .env.
"""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select, Static

from ..config import config


class SettingsPanel(Widget):
    """Settings panel for runtime configuration."""

    BINDINGS = [
        Binding("ctrl+s", "save_settings", "Save"),
    ]

    DEFAULT_CSS = """
    SettingsPanel {
        layout: vertical;
        height: 1fr;
    }

    #scroll {
        height: 1fr;
        padding: 1 2;
    }

    .section-header {
        color: $accent;
        text-style: bold;
        margin-top: 2;
        margin-bottom: 1;
    }

    .field-row {
        height: 3;
        layout: horizontal;
        align: left middle;
        margin-bottom: 1;
    }

    .field-label {
        width: 26;
        color: $text-muted;
    }

    .field-input {
        width: 1fr;
    }

    #status-bar {
        height: 2;
        padding: 0 2;
        background: $panel;
        color: $text-muted;
        content-align: left middle;
    }

    #save-btn {
        width: 20;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="scroll"):
            yield Static("── Backend ──────────────────────────────────", classes="section-header")

            with Horizontal(classes="field-row"):
                yield Label("Backend URL", classes="field-label")
                yield Input(value=config.fastapi_url, placeholder="http://localhost:8000",
                            id="input-fastapi-url", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("Connect timeout (s)", classes="field-label")
                yield Input(value=str(config.connect_timeout), placeholder="5",
                            id="input-connect-timeout", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("Read timeout (s)", classes="field-label")
                yield Input(value=str(config.read_timeout), placeholder="600",
                            id="input-read-timeout", classes="field-input")

            yield Static("── Model defaults ───────────────────────────", classes="section-header")

            with Horizontal(classes="field-row"):
                yield Label("Default backend", classes="field-label")
                yield Select(
                    [("🦙 Ollama", "ollama"), ("🌐 OpenRouter", "openrouter"), ("⚡ NIM", "nim")],
                    value=config.default_backend,
                    id="select-backend", classes="field-input",
                )

            with Horizontal(classes="field-row"):
                yield Label("Default model", classes="field-label")
                yield Input(value=config.default_model, placeholder="llama3.2",
                            id="input-default-model", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("API base URL", classes="field-label")
                yield Input(value=config.api_base or "", placeholder="https://openrouter.ai/api/v1",
                            id="input-api-base", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("API key", classes="field-label")
                yield Input(value=config.api_key or "", placeholder="sk-…",
                            id="input-api-key", password=True, classes="field-input")

            yield Static("── Generation parameters ────────────────────", classes="section-header")

            with Horizontal(classes="field-row"):
                yield Label("Temperature", classes="field-label")
                yield Input(value=str(config.temperature), placeholder="0.7",
                            id="input-temperature", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("Max tokens", classes="field-label")
                yield Input(value=str(config.max_tokens), placeholder="2048",
                            id="input-max-tokens", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("Top-p", classes="field-label")
                yield Input(value=str(config.top_p), placeholder="0.9",
                            id="input-top-p", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("Frequency penalty", classes="field-label")
                yield Input(value=str(config.frequency_penalty), placeholder="0.0",
                            id="input-freq-penalty", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("Repetition penalty", classes="field-label")
                yield Input(value=str(config.repetition_penalty), placeholder="1.0",
                            id="input-rep-penalty", classes="field-input")

            yield Static("── RAG defaults ─────────────────────────────", classes="section-header")

            with Horizontal(classes="field-row"):
                yield Label("Chunk size", classes="field-label")
                yield Input(value=str(config.default_chunk_size), placeholder="500",
                            id="input-chunk-size", classes="field-input")

            with Horizontal(classes="field-row"):
                yield Label("N results", classes="field-label")
                yield Input(value=str(config.default_n_results), placeholder="3",
                            id="input-n-results", classes="field-input")

            yield Button("Save settings  (Ctrl+S)", id="save-btn", variant="success")

        yield Static(
            "Settings apply to this session only — edit .env to persist them.",
            id="status-bar",
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    @on(Button.Pressed, "#save-btn")
    def on_save_pressed(self) -> None:
        self.action_save_settings()

    def action_save_settings(self) -> None:
        errors: list[str] = []

        def _text(wid: str) -> str:
            return self.query_one(wid, Input).value.strip()

        def _float(wid: str, name: str) -> float | None:
            try:
                return float(_text(wid))
            except ValueError:
                errors.append(f"Invalid number for {name}")
                return None

        def _int(wid: str, name: str) -> int | None:
            try:
                return int(_text(wid))
            except ValueError:
                errors.append(f"Invalid integer for {name}")
                return None

        # --- Backend ---
        url = _text("#input-fastapi-url")
        if url:
            config.fastapi_url = url
        v = _int("#input-connect-timeout", "connect timeout")
        if v is not None:
            config.connect_timeout = v
        v = _int("#input-read-timeout", "read timeout")
        if v is not None:
            config.read_timeout = v

        # --- Model ---
        backend_sel: Select = self.query_one("#select-backend", Select)
        if backend_sel.value:
            config.default_backend = str(backend_sel.value)
        m = _text("#input-default-model")
        if m:
            config.default_model = m
        config.api_base = _text("#input-api-base") or None
        config.api_key  = _text("#input-api-key")  or None

        # --- Generation ---
        for wid, name, attr in [
            ("#input-temperature",   "temperature",         "temperature"),
            ("#input-top-p",         "top-p",               "top_p"),
            ("#input-freq-penalty",  "frequency penalty",   "frequency_penalty"),
            ("#input-rep-penalty",   "repetition penalty",  "repetition_penalty"),
        ]:
            fv = _float(wid, name)
            if fv is not None:
                setattr(config, attr, fv)

        for wid, name, attr in [
            ("#input-max-tokens",  "max tokens",  "max_tokens"),
            ("#input-chunk-size",  "chunk size",  "default_chunk_size"),
            ("#input-n-results",   "n results",   "default_n_results"),
        ]:
            iv = _int(wid, name)
            if iv is not None:
                setattr(config, attr, iv)

        if errors:
            self.app.notify("\n".join(errors), severity="error")
        else:
            self.app.notify("Settings saved for this session")
            self.check_backend()

    @work(exclusive=False, thread=False)
    async def check_backend(self) -> None:
        from ..services.backend_service import backend_service

        ok = await backend_service.check_health()
        status: Static = self.query_one("#status-bar", Static)
        if ok:
            status.update(f"✓ Backend reachable at {config.fastapi_url}")
        else:
            status.update(f"✗ Backend NOT reachable at {config.fastapi_url}")
