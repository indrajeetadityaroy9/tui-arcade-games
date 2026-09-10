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

GAME_CSS = Path(__file__).parent / "styles" / "game.tcss"


def arrow_bindings(up: str, down: str, left: str, right: str) -> list[Binding]:
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


COMMON_BINDINGS = [
    Binding("r", "reset", "Restart"),
    Binding("t", "toggle_theme", "Theme"),
    Binding("q", "quit", "Quit"),
]

ARCADE_BINDINGS = [Binding("p", "pause", "Pause")] + COMMON_BINDINGS


class GameApp(App):

    ENABLE_COMMAND_PALETTE = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._viewport: Size | None = None

    @property
    def viewport(self) -> Size:
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
        pass

    def show_message(self, message: str) -> None:
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
