from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from ...core.render import ThemedWidget, on_bg
from ..models import Board, Player


class GameBoard(ThemedWidget):
    DARK = {
        "bg": "#0a0a0a",
        "border": "#555555",
        "x": "#00d4ff",
        "o": "#ff69b4",
        "cursor": "#444400",
        "win": "#2d5a2d",
    }
    LIGHT = {
        "bg": "#f5f5f5",
        "border": "#666666",
        "x": "#0066cc",
        "o": "#cc0066",
        "cursor": "#ffddaa",
        "win": "#90ee90",
    }

    def __init__(self, cell_width: int = 11, cell_height: int = 5, id: str | None = None) -> None:
        super().__init__(id=id)
        self.cell_width = cell_width
        self.cell_height = cell_height
        self._board: Board = tuple(range(9))
        self._cursor = 4
        self._winning_cells: tuple[int, ...] = ()

    def build_styles(self, colors: dict[str, str]) -> dict:
        bg = colors["bg"]
        styles = {
            "border": on_bg(colors["border"], bg),
            "bg": Style(bgcolor=bg),
            "cursor": Style(bgcolor=colors["cursor"]),
            "win": Style(bgcolor=colors["win"]),
        }
        # A mark's colour is constant; only the background behind it changes.
        for mark in ("x", "o"):
            for state, background in (
                ("", bg),
                ("_cursor", colors["cursor"]),
                ("_win", colors["win"]),
            ):
                styles[mark + state] = on_bg(colors[mark], background, bold=True)
        return styles

    @property
    def total_height(self) -> int:
        return self.cell_height * 3 + 4

    def resize_cells(self, cell_width: int, cell_height: int) -> None:
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.refresh()

    def update_state(
        self,
        board: Board,
        cursor_position: int,
        winning_cells: tuple[int, ...],
    ) -> None:
        self._board = board
        self._cursor = cursor_position
        self._winning_cells = winning_cells
        self.refresh()

    def get_content_width(self, container, viewport) -> int:
        return self.cell_width * 3 + 4

    def get_content_height(self, container, viewport, width) -> int:
        return self.total_height

    def _row_at(self, y: int) -> tuple[int, int] | None:
        """Map a screen line to (board row, line within that row's cells)."""
        for row in range(3):
            start = 1 + row * (self.cell_height + 1)
            if start <= y < start + self.cell_height:
                return row, y - start
        return None

    def render_line(self, y: int) -> Strip:
        styles = self.styles_for_theme
        border: Style = styles["border"]
        rule = "─" * self.cell_width

        # The four horizontal rules: top, two dividers, bottom.
        if y == 0:
            return Strip([Segment(f"┌{rule}┬{rule}┬{rule}┐", border)])
        if y == self.total_height - 1:
            return Strip([Segment(f"└{rule}┴{rule}┴{rule}┘", border)])
        if (y - 1) % (self.cell_height + 1) == self.cell_height:
            return Strip([Segment(f"├{rule}┼{rule}┼{rule}┤", border)])

        position = self._row_at(y)
        if position is None:
            return Strip([])
        row, line = position

        segments = [Segment("│", border)]
        for col in range(3):
            index = row * 3 + col
            value = self._board[index]

            if index in self._winning_cells:
                suffix, background = "_win", styles["win"]
            elif index == self._cursor:
                suffix, background = "_cursor", styles["cursor"]
            else:
                suffix, background = "", styles["bg"]

            mark = {Player.X: "x", Player.O: "o"}.get(value)
            if mark and line == self.cell_height // 2:
                left = (self.cell_width - 1) // 2
                right = self.cell_width - 1 - left  # keeps even widths exact
                segments += [
                    Segment(" " * left, background),
                    Segment(mark.upper(), styles[mark + suffix]),
                    Segment(" " * right, background),
                ]
            else:
                segments.append(Segment(" " * self.cell_width, background))

            segments.append(Segment("│", border))
        return Strip(segments)
