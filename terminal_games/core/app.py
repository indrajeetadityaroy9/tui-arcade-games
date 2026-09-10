"""Shared App base and binding sets.

Collects the wiring every game repeated verbatim: the light/dark toggle, the
resize hook, and the mount sequence.
"""

from pathlib import Path

from textual import events
from textual.app import App
from textual.binding import Binding
from textual.geometry import Size

from ..config import get_theme, set_theme
from .overlay import MessageOverlay
from .render import ThemedWidget

LIGHT_THEME = "textual-light"
DARK_THEME = "textual-dark"

#: Chrome shared by every game except chess, which has its own board/sidebar layout.
GAME_CSS = Path(__file__).parent / "styles" / "game.tcss"


def arrow_bindings(up: str, down: str, left: str, right: str) -> list[Binding]:
    """Arrow keys and WASD bound to the same four actions."""
    return [
        Binding(key, action, "", show=False)
        for action, keys in (
            (up, ("up", "w")),
            (down, ("down", "s")),
            (left, ("left", "a")),
            (right, ("right", "d")),
        )
        for key in keys
    ]


#: Restart / theme / quit — present in every game.
COMMON_BINDINGS = [
    Binding("r", "reset", "Restart"),
    Binding("t", "toggle_theme", "Theme"),
    Binding("q", "quit", "Quit"),
]

#: Adds pause, for the games with a running clock.
ARCADE_BINDINGS = [Binding("p", "pause", "Pause")] + COMMON_BINDINGS


class GameApp(App):
    """Base for the five games.

    Subclasses implement `_configure_layout(force_reset)` and `_update_widgets()`,
    and may override `_start()` to kick off timers once the layout exists.
    """

    ENABLE_COMMAND_PALETTE = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._viewport: Size | None = None

    @property
    def viewport(self) -> Size:
        """Current terminal size.

        `App.size` is still the *previous* size while an `on_resize` handler
        runs, so laying out from it silently pins every game to its start-up
        dimensions. The Resize event carries the authoritative size; this
        property prefers it.
        """
        return self._viewport if self._viewport is not None else self.size

    def on_mount(self) -> None:
        self._configure_layout(force_reset=True)
        self._start()
        self._update_widgets()
        self.theme = get_theme()

    def on_resize(self, event: events.Resize) -> None:
        self._viewport = event.size
        self._configure_layout()

    def _start(self) -> None:
        """Hook for timers and other post-layout setup."""

    def show_message(self, message: str) -> None:
        """Put `message` in the centred overlay, or clear it when empty."""
        overlays = self.query(MessageOverlay)
        if overlays:
            overlays.first(MessageOverlay).show(message)

    def _configure_layout(self, force_reset: bool = False) -> None:
        raise NotImplementedError

    def _update_widgets(self) -> None:
        raise NotImplementedError

    def action_toggle_theme(self) -> None:
        self.theme = LIGHT_THEME if self.theme == DARK_THEME else DARK_THEME
        set_theme(self.theme)
        for widget in self.query(ThemedWidget):
            widget.refresh()
