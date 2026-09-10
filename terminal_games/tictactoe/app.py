from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from ..core.app import COMMON_BINDINGS, GAME_CSS, GameApp, arrow_bindings
from ..core.hud import Status
from ..core.overlay import MessageOverlay
from .game_logic import (
    create_initial_state,
    make_move,
    move_cursor_down,
    move_cursor_left,
    move_cursor_right,
    move_cursor_up,
)
from .widgets.game_board import GameBoard

MAX_CELL_HEIGHT = 13

TURN_MESSAGE = "[bold cyan]Your turn (O)[/]"
RESULT_COLORS = {"Win": "green", "Lose": "red"}


class TicTacToeApp(GameApp):
    CSS_PATH = GAME_CSS
    TITLE = "Terminal Tic-Tac-Toe"
    BINDINGS = [
        *arrow_bindings("cursor_up", "cursor_down", "cursor_left", "cursor_right"),
        Binding("enter", "place_move", "Place"),
        Binding("space", "place_move", "Place", show=False),
        *COMMON_BINDINGS,
    ]

    def __init__(self) -> None:
        super().__init__()
        self.state = create_initial_state()
        self._board: GameBoard | None = None
        self._status: Status | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(id="game-container")
        yield Footer()
        yield MessageOverlay()


    def _cell_size(self) -> tuple[int, int]:
        available_width = max(30, self.viewport.width - 10)
        available_height = max(15, self.viewport.height - 11)
        cell_height = min(
            MAX_CELL_HEIGHT,
            (available_height - 4) // 3,
            (available_width - 4) // 6,
        )
        cell_height = max(3, cell_height)
        return cell_height * 2, cell_height

    def _configure_layout(self, force_reset: bool = False) -> None:
        cell_width, cell_height = self._cell_size()

        if self._board is None:
            self._status = Status(id="status")
            self._board = GameBoard(cell_width, cell_height, id="game-board")
            self.query_one("#game-container").mount(self._status, self._board)
        elif force_reset or (self._board.cell_width, self._board.cell_height) != (
            cell_width,
            cell_height,
        ):
            self._board.resize_cells(cell_width, cell_height)
        else:
            return

        self._update_widgets()

    def _update_widgets(self) -> None:
        if self._board:
            self._board.update_state(
                board=self.state.board,
                cursor_position=self.state.cursor_position,
                winning_cells=self.state.winning_cells,
            )
        finished = self.state.is_game_over and self.state.winner
        if self._status:
            self._status.show("" if finished else TURN_MESSAGE)
        self.show_message(self._result_markup() if finished else "")

    def _result_markup(self) -> str:
        message = self.state.winner
        color = next(
            (c for word, c in RESULT_COLORS.items() if word in message), "yellow"
        )
        return f"[bold {color}]{message}[/]\n\n[dim]Press R to restart[/]"


    def _apply(self, transform) -> None:
        if self.state.is_game_over:
            return
        self.state = transform(self.state)
        self._update_widgets()

    def action_cursor_up(self) -> None:
        self._apply(move_cursor_up)

    def action_cursor_down(self) -> None:
        self._apply(move_cursor_down)

    def action_cursor_left(self) -> None:
        self._apply(move_cursor_left)

    def action_cursor_right(self) -> None:
        self._apply(move_cursor_right)

    def action_place_move(self) -> None:
        self._apply(lambda state: make_move(state, state.cursor_position))

    def action_reset(self) -> None:
        self.state = create_initial_state()
        self._update_widgets()


def main() -> None:
    TicTacToeApp().run()


if __name__ == "__main__":
    main()
