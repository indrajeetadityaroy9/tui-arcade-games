from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from typing import Optional

import chess
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header, Static

from ..core.app import COMMON_BINDINGS, GameApp, arrow_bindings
from ..core.overlay import MessageOverlay
from .chess_ai import get_best_move, get_captured_pieces
from .models import PIECE_SYMBOLS, create_initial_state, push_move
from .widgets.chess_board import ChessBoard

SIDEBAR_WIDTH = 34
MAX_CELL_WIDTH = 13
MAX_CELL_HEIGHT = 7


class ChessApp(GameApp):
    CSS_PATH = Path(__file__).parent / "styles" / "chess.tcss"
    TITLE = "Terminal Chess"
    BINDINGS = [
        *arrow_bindings("move_up", "move_down", "move_left", "move_right"),
        Binding("enter", "select", "Select"),
        Binding("escape", "deselect", "Cancel"),
        *COMMON_BINDINGS,
    ]

    def __init__(self) -> None:
        super().__init__()
        self.state = create_initial_state()
        self._board: Optional[ChessBoard] = None
        self._sidebar: Optional[Static] = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="chess-ai")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(
            Container(ChessBoard(id="chess-board"), id="board-container"),
            Container(Static("", id="sidebar", markup=True), id="sidebar-container"),
            id="game-container",
        )
        yield Footer()
        yield MessageOverlay()

    def _start(self) -> None:
        if not self.state.is_player_turn():
            self._trigger_ai_move()

    def on_unmount(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    # ---- layout -----------------------------------------------------------

    def _configure_layout(self, force_reset: bool = False) -> None:
        if self._board is None:
            self._board = self.query_one("#chess-board", ChessBoard)
            self._sidebar = self.query_one("#sidebar", Static)

        available_width = max(40, self.viewport.width - SIDEBAR_WIDTH)
        available_height = max(24, self.viewport.height - 6)
        cell_width = min(MAX_CELL_WIDTH, max(5, (available_width - 4) // 8))
        cell_height = min(MAX_CELL_HEIGHT, max(3, (available_height - 2) // 8))

        if force_reset or (self._board.cell_width, self._board.cell_height) != (
            cell_width,
            cell_height,
        ):
            self._board.resize_cells(cell_width, cell_height)

    def _update_widgets(self) -> None:
        if self._board:
            self._board.update_state(
                board=self.state.board,
                cursor_square=self.state.cursor_square,
                selected_square=self.state.selected_square,
                legal_moves=(
                    self.state.get_legal_moves_from_selected()
                    if self.state.is_player_turn()
                    else []
                ),
                player_color=self.state.config.player_color,
            )
        if self._sidebar:
            self._sidebar.update(self._sidebar_content())
        self.show_message(self._result_markup())

    def _result_markup(self) -> str:
        """Terminal positions interrupt play; a plain check does not."""
        if not self.state.is_game_over():
            return ""
        status = self.state.get_game_status() or "Game over"
        return f"[bold magenta]{status}[/]\n\n[dim]Press R to restart[/]"

    def _sidebar_content(self) -> str:
        lines: list[str] = []
        status = self.state.get_game_status()
        if status and not self.state.is_game_over():
            lines.append(f"[bold red]{status}[/]")
        if self.state.is_thinking:
            lines.append("[dim]Thinking...[/]")

        lines.append("")
        lines.append("[bold]Captured:[/bold]")
        captured = get_captured_pieces(self.state.board)
        for color, name in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
            symbols = "".join(
                PIECE_SYMBOLS.get((piece_type, color), "?")
                for piece_type in sorted(captured[color], reverse=True)
            )
            lines.append(f"  {name} lost: {symbols or '-'}")
        return "\n".join(lines)

    # ---- AI ---------------------------------------------------------------

    def _trigger_ai_move(self) -> None:
        if self.state.is_game_over() or self.state.is_player_turn():
            return
        self.state = replace(self.state, is_thinking=True)
        self._update_widgets()
        future = self._executor.submit(
            get_best_move,
            self.state.board.copy(),
            self.state.config.difficulty.value,
        )
        future.add_done_callback(self._ai_move_ready)

    def _ai_move_ready(self, future: Future) -> None:
        """Runs on the worker thread — hand the result back before touching state."""
        try:
            move = future.result()
        except Exception:
            return  # Executor shut down while a search was in flight.
        try:
            self.call_from_thread(self._apply_ai_move, move)
        except Exception:
            pass  # App already closed.

    def _apply_ai_move(self, move: Optional[chess.Move]) -> None:
        state = replace(self.state, is_thinking=False)
        self.state = push_move(state, move) if move else state
        self._update_widgets()

    # ---- actions ----------------------------------------------------------

    @property
    def _accepts_input(self) -> bool:
        return not (self.state.is_thinking or self.state.is_game_over())

    def _move_cursor(self, file_delta: int, rank_delta: int) -> None:
        if not self._accepts_input:
            return
        if self.state.config.player_color == chess.BLACK:
            file_delta, rank_delta = -file_delta, -rank_delta
        file = chess.square_file(self.state.cursor_square) + file_delta
        rank = chess.square_rank(self.state.cursor_square) + rank_delta
        if 0 <= file < 8 and 0 <= rank < 8:
            self.state = replace(self.state, cursor_square=chess.square(file, rank))
            self._update_widgets()

    def action_move_up(self) -> None:
        self._move_cursor(0, 1)

    def action_move_down(self) -> None:
        self._move_cursor(0, -1)

    def action_move_left(self) -> None:
        self._move_cursor(-1, 0)

    def action_move_right(self) -> None:
        self._move_cursor(1, 0)

    def _select_if_movable(self, square: int) -> bool:
        """Select `square` when it holds a player piece that has a legal move."""
        piece = self.state.board.piece_at(square)
        if piece is None or piece.color != self.state.config.player_color:
            return False
        if not any(m.from_square == square for m in self.state.board.legal_moves):
            return False
        self.state = replace(self.state, selected_square=square)
        return True

    def action_select(self) -> None:
        if not self._accepts_input or not self.state.is_player_turn():
            return
        cursor = self.state.cursor_square

        if self.state.selected_square is None:
            self._select_if_movable(cursor)
            self._update_widgets()
            return

        move = self._find_move(self.state.selected_square, cursor)
        if move is not None:
            self.state = push_move(self.state, move)
            self._update_widgets()
            if not self.state.is_game_over():
                self._trigger_ai_move()
            return

        # Not a legal destination — retarget onto another piece, or clear.
        if not self._select_if_movable(cursor):
            self.state = replace(self.state, selected_square=None)
        self._update_widgets()

    def _find_move(self, from_square: int, to_square: int) -> Optional[chess.Move]:
        """The move between two squares, auto-promoting to a queen."""
        candidates = [
            m
            for m in self.state.board.legal_moves
            if m.from_square == from_square and m.to_square == to_square
        ]
        if not candidates:
            return None
        return next((m for m in candidates if m.promotion == chess.QUEEN), candidates[0])

    def action_deselect(self) -> None:
        if self.state.selected_square is not None:
            self.state = replace(self.state, selected_square=None)
            self._update_widgets()

    def action_reset(self) -> None:
        self.state = create_initial_state(
            player_color=self.state.config.player_color,
            difficulty=self.state.config.difficulty,
        )
        self._update_widgets()
        if not self.state.is_player_turn():
            self._trigger_ai_move()


def main() -> None:
    ChessApp().run()


if __name__ == "__main__":
    main()
