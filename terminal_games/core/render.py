from rich.style import Style
from textual.widget import Widget

DARK_THEME = "textual-dark"


class ThemedWidget(Widget):
    DARK: dict[str, str] = {}
    LIGHT: dict[str, str] = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._style_cache: dict = {}
        self._cached_theme: str | None = None

    def build_styles(self, colors: dict[str, str]) -> dict:
        raise NotImplementedError

    @property
    def styles_for_theme(self) -> dict:
        try:
            theme = self.app.theme
        except Exception:
            theme = DARK_THEME
        if not self._style_cache or theme != self._cached_theme:
            self._cached_theme = theme
            self._style_cache = self.build_styles(
                self.DARK if theme == DARK_THEME else self.LIGHT
            )
        return self._style_cache


def on_bg(color: str, bg: str, *, bold: bool = False) -> Style:
    return Style(color=color, bgcolor=bg, bold=bold)
