"""
LiteMindCLI — Textual TUI application.

Screens
-------
  SplashScreen  — ASCII art shown once at startup (auto-dismissed after 3 s)
  MainScreen    — tabs: Chat | RAG | Settings

Each tab hosts a plain Widget panel (ChatPanel, RAGPanel, SettingsPanel)
so there is exactly one Header + Footer in the whole widget tree.
"""

from __future__ import annotations

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, TabbedContent, TabPane

from .config import config
from .screens.chat_screen import ChatPanel
from .screens.rag_screen import RAGPanel
from .screens.settings_screen import SettingsPanel
from .screens.splash_screen import SplashScreen


class MainScreen(Screen):
    """The primary screen: tabbed Chat / RAG / Settings."""

    BINDINGS = [
        Binding("q", "app.quit", "Quit", priority=True),
        Binding("1", "switch_tab('chat')",     "Chat",     show=False),
        Binding("2", "switch_tab('rag')",      "RAG",      show=False),
        Binding("3", "switch_tab('settings')", "Settings", show=False),
    ]

    def __init__(self, initial_tab: str = "chat", model: str | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._initial_tab = initial_tab
        self._model = model

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial=self._initial_tab, id="tabs"):
            with TabPane("💬 Chat", id="chat"):
                yield ChatPanel(initial_model=self._model, id="chat-panel")
            with TabPane("📚 RAG", id="rag"):
                yield RAGPanel(initial_model=self._model, id="rag-panel")
            with TabPane("⚙  Settings", id="settings"):
                yield SettingsPanel(id="settings-panel")
        yield Footer()

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one("#tabs", TabbedContent).active = tab_id


class LiteMindApp(App):
    """Top-level application — pushes SplashScreen, then MainScreen."""

    TITLE = "LiteMind CLI"
    SUB_TITLE = "Terminal interface for LiteMindUI"

    SCREENS = {
        "main":   MainScreen,
        "splash": SplashScreen,
    }

    def __init__(self, initial_tab: str = "chat", model: str | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._initial_tab = initial_tab
        self._model = model

    def on_mount(self) -> None:
        # Push the main screen first (it sits at the bottom of the stack),
        # then overlay the splash on top so it dismisses back to main.
        self.push_screen(MainScreen(initial_tab=self._initial_tab, model=self._model))
        self.push_screen(SplashScreen())
        self.check_backend()

    @work(exclusive=False, thread=False)
    async def check_backend(self) -> None:
        from .services.backend_service import backend_service

        ok = await backend_service.check_health()
        if ok:
            self.sub_title = f"Connected → {config.fastapi_url}"
        else:
            self.sub_title = f"⚠ Backend unreachable at {config.fastapi_url}"
            self.notify(
                f"Cannot reach backend at {config.fastapi_url}\n"
                "Start litemind-ui or set FASTAPI_URL in .env",
                severity="warning",
                timeout=8,
            )
