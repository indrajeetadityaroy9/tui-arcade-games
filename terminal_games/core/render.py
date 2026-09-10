"""Theme-aware widget base.

Board widgets rebuild their `rich.Style` objects only when the theme actually
changes — rebuilding per frame would allocate thousands of Style objects a
second at Space Invaders' 20 Hz. Each game supplies its own palette; the caching
and invalidation live here.
"""

from rich.style import Style
from textual.widget import Widget

DARK_THEME = "textual-dark"


class ThemedWidget(Widget):
    #: Colour maps keyed the same way, one per theme. Subclasses override both.
    DARK: dict[str, str] = {}
    LIGHT: dict[str, str] = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._style_cache: dict = {}
        self._cached_theme: str | None = None

    def build_styles(self, colors: dict[str, str]) -> dict:
        """Turn a palette into the Style objects `render_line` will use."""
        raise NotImplementedError

    @property
    def styles_for_theme(self) -> dict:
        try:
            theme = self.app.theme
        except Exception:
            # No active app: mid-teardown, or the widget rendered standalone.
            theme = DARK_THEME
        if not self._style_cache or theme != self._cached_theme:
            self._cached_theme = theme
            self._style_cache = self.build_styles(
                self.DARK if theme == DARK_THEME else self.LIGHT
            )
        return self._style_cache


def on_bg(color: str, bg: str, *, bold: bool = False) -> Style:
    """A foreground colour painted onto the board background."""
    return Style(color=color, bgcolor=bg, bold=bold)
