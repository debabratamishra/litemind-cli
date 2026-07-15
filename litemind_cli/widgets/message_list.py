"""
MessageList widget — scrollable, auto-growing list of chat bubbles.

Each message is rendered as a Markdown widget so code fences,
bold, etc. look good in the terminal.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Markdown, Static


import itertools

_id_counter = itertools.count(1)


class MessageBubble(Static):
    """A single chat turn (user or assistant)."""

    DEFAULT_CSS = """
    MessageBubble {
        width: 1fr;
        padding: 0 1;
        margin-bottom: 1;
    }
    MessageBubble.user {
        color: $text;
        background: $surface;
        border-left: thick $accent;
        padding-left: 2;
    }
    MessageBubble.assistant {
        color: $text;
        background: $panel;
        border-left: thick $success;
        padding-left: 2;
    }
    MessageBubble.system {
        color: $text-muted;
        background: $background;
        border-left: thick $warning;
        padding-left: 2;
    }
    """

    def __init__(self, role: str, content: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._role = role
        self._content = content
        self.add_class(role)

    def compose(self) -> ComposeResult:
        label = {"user": "You", "assistant": "Assistant", "system": "System"}.get(
            self._role, self._role
        )
        yield Static(f"[bold]{label}[/bold]", markup=True)
        yield Markdown(self._content)

    def append_text(self, text: str) -> None:
        """Stream additional text into the last Markdown widget."""
        md = self.query_one(Markdown)
        self._content += text
        md.update(self._content)


class MessageList(ScrollableContainer):
    """Scrollable container holding MessageBubble instances."""

    DEFAULT_CSS = """
    MessageList {
        width: 1fr;
        height: 1fr;
        overflow-y: auto;
        padding: 0 1;
    }
    """

    def add_message(self, role: str, content: str = "") -> MessageBubble:
        """
        Add a new message bubble and scroll to the bottom.

        Returns the bubble so the caller can stream text into it.
        """
        bubble = MessageBubble(role, content, id=f"msg-{next(_id_counter)}")
        self.mount(bubble)
        self.scroll_end(animate=False)
        return bubble

    def clear(self) -> None:
        """Remove all message bubbles."""
        for child in list(self.children):
            child.remove()
