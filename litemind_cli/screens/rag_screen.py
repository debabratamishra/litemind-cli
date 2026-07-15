"""
RAG panel — document management + retrieval-augmented generation.

Same provider-aware toolbar as ChatPanel:
  - ollama     → model picker (local + cloud from /models/enhanced)
  - openrouter → text input + API key/base
  - nim        → text input + API key/base

Left side:  file list, upload, remove, reset
Right side: streaming RAG query
"""

from __future__ import annotations

import uuid
from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label, Select, Static

from ..config import config
from ..services.rag_service import rag_service
from ..widgets.message_list import MessageList

_OR_PLACEHOLDER  = "e.g. openai/gpt-4o  or  meta-llama/llama-3.3-70b-instruct"
_NIM_PLACEHOLDER = "e.g. meta/llama-3.3-70b-instruct"

# (label, value) — Textual Select expects label first
_PROVIDERS = [("🦙 Ollama", "ollama"), ("🌐 OpenRouter", "openrouter"), ("⚡ NIM", "nim")]

_DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful RAG assistant. "
    "Answer strictly from the provided document context. "
    "If the context is insufficient, say so clearly."
)


class RAGPanel(Widget):
    """RAG document management and query panel."""

    BINDINGS = [
        Binding("ctrl+l", "clear_chat",     "Clear chat"),
        Binding("ctrl+r", "refresh_files",  "Refresh files"),
    ]

    DEFAULT_CSS = """
    RAGPanel {
        layout: horizontal;
        height: 1fr;
    }

    /* ── Left file panel ── */
    #file-panel {
        width: 40;
        min-width: 30;
        border-right: solid $panel;
        layout: vertical;
        padding: 0 1;
    }

    #file-panel Label {
        color: $text-muted;
        margin-top: 1;
    }

    #file-table {
        height: 1fr;
        min-height: 6;
    }

    #upload-input {
        width: 1fr;
        margin-top: 1;
    }

    /* Stack buttons vertically so all three are fully visible */
    #btn-row {
        height: auto;
        layout: vertical;
        margin-top: 1;
    }

    #upload-btn {
        width: 1fr;
        margin-bottom: 1;
    }

    #remove-btn {
        width: 1fr;
        margin-bottom: 1;
    }

    #reset-btn {
        width: 1fr;
    }

    #rag-status {
        height: 2;
        color: $text-muted;
        margin-top: 1;
    }

    /* ── Right query panel ── */
    #query-panel {
        width: 1fr;
        layout: vertical;
    }

    /* toolbar mirrors ChatPanel */
    #rag-toolbar {
        height: auto;
        background: $panel;
        padding: 0 1;
        layout: vertical;
    }

    #rag-toolbar-row1 {
        height: 3;
        layout: horizontal;
        align: left middle;
    }

    #rag-toolbar-row2 {
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

    #rag-input-row {
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
        # ── Left: file management ──
        with Vertical(id="file-panel"):
            yield Label("Indexed files")
            tbl: DataTable = DataTable(id="file-table", cursor_type="row")
            tbl.add_columns("Filename", "Chunks")
            yield tbl
            yield Label("Upload (space-separated paths):")
            yield Input(placeholder="/path/to/doc.pdf …", id="upload-input")
            with Vertical(id="btn-row"):
                yield Button("Upload", id="upload-btn", variant="success")
                yield Button("Remove selected", id="remove-btn", variant="warning")
                yield Button("Reset all", id="reset-btn", variant="error")
            yield Static("", id="rag-status")

        # ── Right: query ──
        with Vertical(id="query-panel"):
            with Vertical(id="rag-toolbar"):
                with Horizontal(id="rag-toolbar-row1"):
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
                with Horizontal(id="rag-toolbar-row2"):
                    yield Label("API key:", classes="tb-label")
                    yield Input(value=self._api_key, placeholder="sk-…",
                                password=True, id="apikey-input")
                    yield Label("API base:", classes="tb-label")
                    yield Input(value=self._api_base,
                                placeholder="https://openrouter.ai/api/v1",
                                id="apibase-input")

            yield MessageList(id="message-list")
            with Horizontal(id="rag-input-row"):
                yield Input(placeholder="Ask about your documents…", id="message-input")
                yield Button("Send", id="send-btn", variant="primary")

    def on_mount(self) -> None:
        self._apply_provider_ui(self._backend)
        self.load_models()
        self.refresh_files()

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    @work(exclusive=False, thread=False)
    async def load_models(self) -> None:
        from ..services.backend_service import backend_service

        data   = await backend_service.get_enhanced_models()
        local  = [m["name"] for m in data.get("local_models",  [])]
        cloud  = [m["name"] for m in data.get("cloud_models", [])]

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

    @work(exclusive=False, thread=False)
    async def refresh_files(self) -> None:
        status: Static = self.query_one("#rag-status", Static)
        status.update("Refreshing…")
        tbl: DataTable = self.query_one("#file-table", DataTable)
        tbl.clear()

        data = await rag_service.get_processed_files()
        if data:
            files: list[dict] = data.get("files", [])
            for f in files:
                tbl.add_row(f.get("filename", "?"), str(f.get("chunk_count", "?")))
            status.update(f"{len(files)} file(s) indexed")
        else:
            status.update("No files indexed (or backend unreachable)")

    @work(exclusive=False, thread=False)
    async def do_upload(self, paths: list[Path]) -> None:
        status: Static = self.query_one("#rag-status", Static)
        status.update(f"Uploading {len(paths)} file(s)…")
        ok, result = await rag_service.upload_files(paths)
        if ok:
            processed = result.get("processed_files", len(paths))
            status.update(f"Uploaded {processed} file(s)")
        else:
            status.update("Upload failed")
        self.refresh_files()

    @work(exclusive=False, thread=False)
    async def do_remove(self, filename: str) -> None:
        ok, msg = await rag_service.remove_file(filename)
        self.query_one("#rag-status", Static).update(msg)
        self.refresh_files()

    @work(exclusive=False, thread=False)
    async def do_reset(self) -> None:
        status: Static = self.query_one("#rag-status", Static)
        status.update("Resetting RAG store…")
        ok, msg = await rag_service.reset_system()
        status.update(msg)
        self.refresh_files()

    @work(exclusive=True, thread=False)
    async def send_query(self, query: str) -> None:
        if self._streaming:
            return
        self._streaming = True

        msg_list: MessageList = self.query_one("#message-list", MessageList)
        msg_list.add_message("user", query)
        self._history.append({"role": "user", "content": query})
        bubble = msg_list.add_message("assistant")
        full_response = ""

        api_key  = self.query_one("#apikey-input",  Input).value.strip() or None
        api_base = self.query_one("#apibase-input", Input).value.strip() or None

        try:
            stream = rag_service.stream_rag_query(
                query,
                self._history[:-1],
                model=self._model,
                backend=self._backend,
                api_key=api_key,
                api_base=api_base,
                system_prompt=_DEFAULT_SYSTEM_PROMPT,
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
        model_sel   = self.query_one("#model-select",     Select)
        model_input = self.query_one("#model-input",      Input)
        row2        = self.query_one("#rag-toolbar-row2", Horizontal)

        model_sel.display   = is_ollama
        model_input.display = not is_ollama
        row2.display        = not is_ollama

        if not is_ollama:
            model_input.placeholder = _NIM_PLACEHOLDER if backend == "nim" else _OR_PLACEHOLDER
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

    @on(Button.Pressed, "#upload-btn")
    def on_upload(self) -> None:
        raw = self.query_one("#upload-input", Input).value.strip()
        if not raw:
            return
        paths = [Path(p) for p in raw.split()]
        valid = [p for p in paths if p.exists() and p.is_file()]
        if not valid:
            self.app.notify("No valid file paths provided", severity="error")
            return
        self.do_upload(valid)

    @on(Button.Pressed, "#remove-btn")
    def on_remove(self) -> None:
        tbl: DataTable = self.query_one("#file-table", DataTable)
        if tbl.row_count == 0:
            self.app.notify("No files to remove", severity="warning")
            return
        row = tbl.cursor_row
        if row is None or row >= tbl.row_count:
            self.app.notify("Select a file row first", severity="warning")
            return
        try:
            cell = tbl.get_cell_at((row, 0))
            self.do_remove(str(cell))
        except Exception:
            self.app.notify("Could not determine selected file", severity="error")

    @on(Button.Pressed, "#reset-btn")
    def on_reset(self) -> None:
        self.do_reset()

    @on(Button.Pressed, "#send-btn")
    def on_send(self) -> None:
        inp: Input = self.query_one("#message-input", Input)
        text = inp.value.strip()
        if text:
            inp.value = ""
            self.send_query(text)

    @on(Input.Submitted, "#message-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text:
            event.input.value = ""
            self.send_query(text)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_clear_chat(self) -> None:
        self.query_one("#message-list", MessageList).clear()
        self._history.clear()

    def action_refresh_files(self) -> None:
        self.refresh_files()
