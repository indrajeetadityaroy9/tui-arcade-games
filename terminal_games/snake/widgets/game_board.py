from rich.segment import Segment
from rich.style import Style
from textual.geometry import Size
from textual.strip import Strip

from ...core.render import ThemedWidget, on_bg
from ..models import BoardConfig, Position

HEAD = "█"
BODY = "▓"
TAIL = "░"
APPLE = "●"
BORDER_H = "─"
BORDER_V = "│"
CORNERS = ("┌", "┐", "└", "┘")

PART_CHARS = {"head": HEAD, "body": BODY, "tail": TAIL}


class GameBoard(ThemedWidget):
    DARK = {
        "bg": "#0a0a0a",
        "head": "bright_white",
        "body": "grey70",
        "tail": "grey50",
        "apple": "bright_red",
        "empty": "#1a1a1a",
        "border": "bright_cyan",
    }
    LIGHT = {
        "bg": "#e8e8e8",
        "head": "grey11",
        "body": "grey35",
        "tail": "grey58",
        "apple": "red3",
        "empty": "#d0d0d0",
        "border": "dark_cyan",
    }

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
        self._apple = Position(0, 0)
        # Flattened once per update so render_line does O(1) lookups per cell.
        self._segment_at: dict[Position, str] = {}

    def build_styles(self, colors: dict[str, str]) -> dict:
        bg = colors["bg"]
        return {
            "head": on_bg(colors["head"], bg, bold=True),
            "body": on_bg(colors["body"], bg),
            "tail": on_bg(colors["tail"], bg),
            "apple": on_bg(colors["apple"], bg, bold=True),
            "empty": on_bg(colors["empty"], bg),
            "border": on_bg(colors["border"], bg),
        }

    def resize_cells(self, cell_width: int, cell_height: int) -> None:
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.refresh()

    def update_state(self, snake_cells: tuple[Position, ...], apple: Position) -> None:
        self._apple = apple
        self._segment_at = {}
        if snake_cells:
            self._segment_at[snake_cells[0]] = "head"
            for cell in snake_cells[1:-1]:
                self._segment_at[cell] = "body"
            if len(snake_cells) > 1:
                self._segment_at[snake_cells[-1]] = "tail"
        self.refresh()

    @property
    def _inner_width(self) -> int:
        return self.config.columns * self.cell_width

    @property
    def _apple_text(self) -> str:
        """Inset from the cell edges so the apple stays distinguishable from a
        snake segment by shape, not colour alone."""
        if self.cell_width >= 4:
            return " " + HEAD * (self.cell_width - 2) + " "
        return APPLE.center(self.cell_width)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self._inner_width + 2

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return self.config.rows * self.cell_height + 2

    def render_line(self, y: int) -> Strip:
        styles = self.styles_for_theme
        border: Style = styles["border"]
        last = self.config.rows * self.cell_height + 1

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
        for col in range(self.config.columns):
            pos = Position(col, row)
            if pos == self._apple:
                segments.append(Segment(self._apple_text, styles["apple"]))
            elif pos in self._segment_at:
                part = self._segment_at[pos]
                # Fill the whole cell so the body reads as one continuous snake.
                segments.append(Segment(PART_CHARS[part] * width, styles[part]))
            else:
                segments.append(Segment(" " * width, styles["empty"]))
        segments.append(Segment(BORDER_V, border))
        return Strip(segments)
