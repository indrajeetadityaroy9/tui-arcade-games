from textual.widget import Widget
from textual.widgets import Static


class MessageOverlay(Widget):
    DEFAULT_CSS = """
    MessageOverlay {
        layer: overlay;
        /* Docked so it spans the whole terminal. A plain `height: 100%` is
           measured against the screen rather than the space left by the docked
           Header and Footer, which overflows and raises a scrollbar — that
           scrollbar then steals two columns and pulls the panel off-centre. */
        dock: top;
        width: 100%;
        height: 1fr;
        align: center middle;
        background: transparent;
    }
    MessageOverlay > #overlay-panel {
        width: auto;
        min-width: 24;
        max-width: 90%;
        height: auto;
        padding: 1 4;
        border: round $primary;
        background: $surface;
        text-align: center;
    }
    """

    can_focus = False

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._message = ""
        self.display = False

    def compose(self):
        yield Static(id="overlay-panel", markup=True)

    def on_mount(self) -> None:
        self.call_after_refresh(self._render_message)

    def show(self, message: str) -> None:
        if message == self._message:
            return
        self._message = message
        self._render_message()

    def _render_message(self) -> None:
        self.display = bool(self._message)
        if not self._message:
            return
        panel = self.query("#overlay-panel")
        if panel:
            panel.first(Static).update(self._message)


def overlay_message(
    *,
    is_game_over: bool = False,
    is_paused: bool = False,
    won: str = "",
) -> str:
    if is_game_over:
        return "[bold red]GAME OVER[/]\n\n[dim]Press R to restart[/]"
    if won:
        return won
    if is_paused:
        return "[bold yellow]PAUSED[/]\n\n[dim]Press P to resume[/]"
    return ""
