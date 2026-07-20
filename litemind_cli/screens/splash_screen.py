"""
Splash screen shown briefly at startup before the main TUI.

Press any key or wait for the timer to dismiss it.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static

_ASCII = r"""
  _     _ _       __  __ _           _    ____ _     ___
 | |   (_) |_ ___|  \/  (_)_ __   __| |  / ___| |   |_ _|
 | |   | | __/ _ \ |\/| | | '_ \ / _` | | |   | |    | |
 | |___| | ||  __/ |  | | | | | | (_| | | |___| |___ | |
 |_____|_|\__\___|_|  |_|_|_| |_|\__,_|  \____|_____|___|
"""

_TAGLINE = "Terminal interface for LiteMindUI  ·  Chat · RAG"
_HINT    = "Press any key to continue…"


class SplashScreen(Screen):
    """One-shot splash shown at launch."""

    AUTO_FOCUS = ""          # don't focus any widget — any key dismisses
    BINDINGS = [
        Binding("escape", "dismiss_splash", show=False),
    ]

    DEFAULT_CSS = """
    SplashScreen {
        align: center middle;
        background: $background;
    }

    #splash-box {
        width: auto;
        height: auto;
        padding: 2 4;
        border: double $accent;
        background: $surface;
        align: center middle;
        layout: vertical;
    }

    #ascii-art {
        color: $accent;
        text-style: bold;
        content-align: center middle;
        width: auto;
    }

    #tagline {
        color: $text;
        content-align: center middle;
        margin-top: 1;
        width: auto;
    }

    #hint {
        color: $text-muted;
        content-align: center middle;
        margin-top: 2;
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Static(id="splash-box"):
            yield Static(_ASCII, id="ascii-art")
            yield Static(_TAGLINE, id="tagline")
            yield Static(_HINT, id="hint")

    def on_mount(self) -> None:
        # Auto-dismiss after 5 seconds
        self.set_timer(5.0, self.action_dismiss_splash)

    def on_key(self) -> None:
        self.action_dismiss_splash()

    def action_dismiss_splash(self) -> None:
        self.app.pop_screen()
