from rich.segment import Segment
from rich.style import Style
from textual.geometry import Size
from textual.strip import Strip

from ...core.render import ThemedWidget, on_bg
from ..models import BoardConfig, Position, Tetromino

FILLED = "█"
BORDER_H = "─"
BORDER_V = "│"
CORNERS = ("┌", "┐", "└", "┘")

DARK_PIECES = ("#1a1a1a", "cyan", "blue", "orange1", "yellow", "green", "magenta", "red")
LIGHT_PIECES = (
    "#d0d0d0",
    "dark_cyan",
    "dark_blue",
    "dark_orange",
    "gold3",
    "dark_green",
    "dark_magenta",
    "dark_red",
)


class GameBoard(ThemedWidget):
    DARK = {"bg": "#0a0a0a", "border": "bright_cyan", "pieces": DARK_PIECES}
    LIGHT = {"bg": "#e8e8e8", "border": "dark_cyan", "pieces": LIGHT_PIECES}

    def __init__(
        self,
        config: BoardConfig | None = None,
        cell_width: int = 4,
        cell_height: int = 2,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.config = config or BoardConfig()
        self.cell_width = cell_width
        self.cell_height = cell_height
        self._board: tuple[tuple[int, ...], ...] = ()
        self._piece: Tetromino | None = None
        self._piece_position = Position(0, 0)

    def build_styles(self, colors: dict) -> dict:
        bg = colors["bg"]
        pieces = colors["pieces"]
        styles: dict = {"border": on_bg(colors["border"], bg), 0: on_bg(pieces[0], bg)}
        for index in range(1, 8):
            styles[index] = on_bg(pieces[index], bg, bold=True)
        return styles

    def resize_cells(self, cell_width: int, cell_height: int) -> None:
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.refresh()

    def update_state(
        self,
        board: tuple[tuple[int, ...], ...],
        current_piece: Tetromino | None,
        piece_position: Position,
    ) -> None:
        self._board = board
        self._piece = current_piece
        self._piece_position = piece_position
        self.refresh()

    @property
    def _inner_width(self) -> int:
        return self.config.width * self.cell_width

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self._inner_width + 2

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return self.config.height * self.cell_height + 2

    def _cell_at(self, x: int, y: int) -> int:
        if self._piece is not None:
            px = x - self._piece_position.x
            py = y - self._piece_position.y
            shape = self._piece.shape
            if 0 <= py < len(shape) and 0 <= px < len(shape[0]) and shape[py][px]:
                return shape[py][px]
        if 0 <= y < len(self._board) and 0 <= x < len(self._board[0]):
            return self._board[y][x]
        return 0

    def render_line(self, y: int) -> Strip:
        styles = self.styles_for_theme
        border: Style = styles["border"]
        last = self.config.height * self.cell_height + 1

        if y == 0 or y == last:
            left, right = CORNERS[0:2] if y == 0 else CORNERS[2:4]
            return Strip([
                Segment(left, border),
                Segment(BORDER_H * self._inner_width, border),
                Segment(right, border),
            ])

        row = (y - 1) // self.cell_height
        width = self.cell_width
        segments = [Segment(BORDER_V, border)]
        for col in range(self.config.width):
            cell = self._cell_at(col, row)
            if cell == 0:
                segments.append(Segment(" " * width, styles[0]))
            else:
                segments.append(Segment(FILLED * width, styles.get(cell, styles[1])))
        segments.append(Segment(BORDER_V, border))
        return Strip(segments)
