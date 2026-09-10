"""Shared score bar and turn indicator.

Interrupting messages (pause, game over, win, draw) do not live here — they go
to the centred `MessageOverlay` instead.
"""

from dataclasses import dataclass

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Digits, Label, Static


@dataclass(frozen=True)
class Stat:
    """One labelled number in the bar."""

    key: str
    label: str
    pad: int = 0  # zero-pad to this width; 0 leaves the number bare


class HUD(Widget):
    DEFAULT_CSS = """
    HUD {
        width: 100%;
        height: 5;
        layout: horizontal;
        padding: 0 1;
    }
    HUD .hud-stat {
        width: auto;
        height: auto;
        margin-right: 2;
        align-horizontal: center;
    }
    HUD Label {
        text-align: center;
        width: 100%;
        color: $text-muted;
    }
    HUD Digits {
        width: auto;
        min-width: 8;
        text-align: center;
    }
    """

    def __init__(self, *stats: Stat, id: str | None = None) -> None:
        super().__init__(id=id)
        self._stats = stats
        self._values: dict[str, int] = {stat.key: 0 for stat in stats}


    def compose(self):
        for stat in self._stats:
            yield Vertical(
                Label(stat.label),
                Digits(id=f"{stat.key}-digits"),
                classes="hud-stat",
            )

    def on_mount(self) -> None:
        # A widget's on_mount can fire before its compose() children exist, so
        # paint once the DOM has settled rather than immediately.
        self.call_after_refresh(self._render_values)

    def show(self, **values: int) -> None:
        self._values.update(values)
        self._render_values()

    def _render_values(self) -> None:
        for stat in self._stats:
            digits = self.query(f"#{stat.key}-digits")
            if not digits:
                return  # children not mounted yet
            value = self._values.get(stat.key, 0)
            text = f"{value:0{stat.pad}d}" if stat.pad else str(value)
            digits.first(Digits).update(text)


class Status(Widget):
    """A single centred line, for whose-turn-it-is style text."""

    DEFAULT_CSS = """
    Status {
        width: 100%;
        height: 3;
        layout: horizontal;
    }
    Status .status-text {
        width: 1fr;
        padding: 0 2;
        text-style: bold;
        content-align: center middle;
    }
    """

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._message = ""

    def compose(self):
        yield Static(id="status-text", classes="status-text")

    def on_mount(self) -> None:
        self.call_after_refresh(self._render_message)

    def show(self, message: str) -> None:
        self._message = message
        self._render_message()

    def _render_message(self) -> None:
        text = self.query("#status-text")
        if text:
            text.first(Static).update(self._message)
