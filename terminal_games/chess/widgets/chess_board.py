from typing import Optional

import chess
from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from ...core.render import ThemedWidget
from ..models import get_piece_symbol

LEGAL_MOVE_DOT = "•"


class ChessBoard(ThemedWidget):
    DARK = {
        "light_square": "#f0d9b5",
        "dark_square": "#b58863",
        "cursor": "#ffff00",
        "selected": "#7fff00",
        "legal_move": "#66c2ff",
        "check": "#ff4444",
        "white_piece": "#ffffff",
        "black_piece": "#000000",
    }
    LIGHT = {
        "light_square": "#eeeed2",
        "dark_square": "#769656",
        "cursor": "#ff6600",
        "selected": "#f6f669",
        "legal_move": "#baca44",
        "check": "#ff0000",
        "white_piece": "#4a4a4a",
        "black_piece": "#000000",
    }

    def __init__(self, id: Optional[str] = None) -> None:
        super().__init__(id=id)
        self.cell_width = 9
        self.cell_height = 5
        self._board = chess.Board()
        self._cursor_square = chess.E2
        self._selected_square: Optional[int] = None
        self._legal_moves: set[int] = set()
        self._flipped = False

    def build_styles(self, colors: dict[str, str]) -> dict:
        styles: dict = {
            "label": Style(color="cyan", bold=True),
            "colors": colors,
        }
        for key in ("light_square", "dark_square", "cursor", "selected", "legal_move", "check"):
            styles[key] = Style(bgcolor=colors[key])
        return styles

    def resize_cells(self, cell_width: int, cell_height: int) -> None:
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.refresh()

    def update_state(
        self,
        board: chess.Board,
        cursor_square: int,
        selected_square: Optional[int],
        legal_moves: list[int],
        player_color: chess.Color,
    ) -> None:
        self._board = board
        self._cursor_square = cursor_square
        self._selected_square = selected_square
        self._legal_moves = set(legal_moves)
        self._flipped = player_color == chess.BLACK
        self.refresh()

    @property
    def _mid_row(self) -> int:
        return self.cell_height // 2

    def get_content_width(self, container, viewport) -> int:
        return 8 * self.cell_width + 4

    def get_content_height(self, container, viewport, width) -> int:
        return 8 * self.cell_height + 2

    def _file_order(self) -> range:
        return range(7, -1, -1) if self._flipped else range(8)

    def render_line(self, y: int) -> Strip:
        styles = self.styles_for_theme
        label = styles["label"]
        board_height = 8 * self.cell_height

        # File letters above and below the board.
        if y == 0 or y == board_height + 1:
            segments = [Segment("  ")]
            for file in self._file_order():
                letter = chr(ord("a") + file)
                segments.append(Segment(letter.center(self.cell_width), label))
            return Strip(segments)

        if not 1 <= y <= board_height:
            return Strip([])

        board_y = y - 1
        row = board_y // self.cell_height
        cell_y = board_y % self.cell_height
        rank = row if self._flipped else 7 - row
        show_rank = cell_y == self._mid_row

        rank_label = f"{rank + 1} " if show_rank else "  "
        segments = [Segment(rank_label, label)]
        for file in self._file_order():
            segments.extend(self._render_cell(chess.square(file, rank), cell_y, styles))
        if show_rank:
            segments.append(Segment(f" {rank + 1}", label))
        return Strip(segments)

    def _render_cell(self, square: int, cell_y: int, styles: dict) -> list[Segment]:
        colors = styles["colors"]
        piece = self._board.piece_at(square)

        is_cursor = square == self._cursor_square
        is_selected = square == self._selected_square
        is_legal = square in self._legal_moves
        in_check = (
            piece is not None
            and piece.piece_type == chess.KING
            and piece.color == self._board.turn
            and self._board.is_check()
        )

        # Selected beats cursor beats check beats legal-move beats plain square.
        if is_selected:
            key = "selected"
        elif is_cursor:
            key = "cursor"
        elif in_check:
            key = "check"
        elif is_legal:
            key = "legal_move"
        else:
            light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
            key = "light_square" if light else "dark_square"

        background = styles[key]

        if cell_y == self._mid_row:
            if piece:
                color = colors["black_piece" if piece.color == chess.BLACK else "white_piece"]
                style = Style(color=color, bgcolor=colors[key], bold=True)
                return [Segment(get_piece_symbol(piece).center(self.cell_width), style)]
            if is_legal and not is_cursor and not is_selected:
                style = Style(color="#004080", bgcolor=colors[key], bold=True)
                return [Segment(LEGAL_MOVE_DOT.center(self.cell_width), style)]

        return [Segment(" " * self.cell_width, background)]
