from dataclasses import replace

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header

from ..core.app import ARCADE_BINDINGS, GAME_CSS, GameApp, arrow_bindings
from ..core.hud import HUD, Stat
from ..core.layout import Grid, fit_grid
from ..core.overlay import MessageOverlay, overlay_message
from .game_logic import (
    calculate_speed,
    can_place_piece,
    create_initial_state,
    do_hard_drop,
    move_down,
    move_left,
    move_right,
    toggle_pause,
    try_rotate,
)
from .models import BoardConfig, GameState, Position, Tetromino
from .widgets.game_board import GameBoard

STATS = (
    Stat("level", "LEVEL"),
    Stat("lines", "LINES"),
    Stat("score", "SCORE", pad=6),
    Stat("high", "HIGH SCORE", pad=6),
)


class TetrisApp(GameApp):
    CSS_PATH = GAME_CSS
    TITLE = "Terminal Tetris"
    BINDINGS = [
        *arrow_bindings("rotate", "soft_drop", "move_left", "move_right"),
        Binding("space", "hard_drop", "Drop"),
        *ARCADE_BINDINGS,
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config: BoardConfig | None = None
        self.state: GameState | None = None
        self._gravity: Timer | None = None
        self._board: GameBoard | None = None
        self._hud: HUD | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(id="game-container")
        yield Footer()
        yield MessageOverlay()

    def _start(self) -> None:
        self._restart_gravity()


    def _grid(self) -> Grid:
        return fit_grid(
            max(22, self.viewport.width - 6),
            max(16, self.viewport.height - 13),
            min_columns=10,
            min_rows=10,
            max_columns=12,
            max_rows=22,
        )

    def _configure_layout(self, force_reset: bool = False) -> None:
        grid = self._grid()
        new_config = BoardConfig(width=grid.columns, height=grid.rows)
        cells = (grid.cell_width, grid.cell_height)
        if (
            not force_reset
            and self.config == new_config
            and self._board is not None
            and (self._board.cell_width, self._board.cell_height) == cells
        ):
            return

        old_config, self.config = self.config, new_config
        if self.state:
            self.state = self._remap(self.state, old_config or new_config, new_config)
        else:
            self.state = create_initial_state(new_config)

        if self._board is None:
            self._hud = HUD(*STATS, id="hud")
            self._board = GameBoard(
                config=new_config,
                cell_width=grid.cell_width,
                cell_height=grid.cell_height,
                id="game-board",
            )
            self.query_one("#game-container").mount(self._hud, self._board)
        else:
            self._board.config = new_config
            self._board.resize_cells(grid.cell_width, grid.cell_height)

        self._restart_gravity()
        self._update_widgets()

    def _remap(
        self,
        state: GameState,
        old: BoardConfig,
        new: BoardConfig,
    ) -> GameState:
        dx = (new.width - old.width) // 2
        dy = new.height - old.height

        board = [[0] * new.width for _ in range(new.height)]
        for y, row in enumerate(state.board[: old.height]):
            for x, cell in enumerate(row[: old.width]):
                if cell and 0 <= x + dx < new.width and 0 <= y + dy < new.height:
                    board[y + dy][x + dx] = cell
        packed = tuple(tuple(row) for row in board)

        position = state.position
        piece = state.current_piece
        if piece is not None:
            position = Position(
                max(0, min(new.width - len(piece.shape[0]), state.position.x + dx)),
                max(-2, min(new.height - 1, state.position.y + dy)),
            )
            if not can_place_piece(piece, position, packed, new):
                position = self._nearest_fit(piece, position, packed, new)
            if not can_place_piece(piece, position, packed, new):
                return replace(
                    state, board=packed, current_piece=None, is_game_over=True
                )

        return replace(state, board=packed, position=position)

    @staticmethod
    def _nearest_fit(
        piece: Tetromino,
        start: Position,
        board: tuple[tuple[int, ...], ...],
        config: BoardConfig,
    ) -> Position:
        for delta in range(config.height):
            for dy in (0, -delta, delta):
                y = start.y + dy
                if -2 <= y < config.height:
                    candidate = Position(start.x, y)
                    if can_place_piece(piece, candidate, board, config):
                        return candidate
        return start


    def _restart_gravity(self) -> None:
        if self._gravity:
            self._gravity.stop()
        if self.state:
            self._gravity = self.set_interval(
                calculate_speed(self.state.level), self._gravity_tick
            )

    def _gravity_tick(self) -> None:
        if self.state is None or self.state.is_game_over or self.state.is_paused:
            return
        self._advance(lambda state: move_down(state, self.config)[0])

    def _advance(self, transform) -> None:
        if self.state is None or self.state.is_game_over or self.state.is_paused:
            return
        level = self.state.level
        self.state = transform(self.state)
        self._update_widgets()
        if self.state.level != level:
            self._restart_gravity()
        if self.state.is_game_over and self._gravity:
            self._gravity.pause()

    def _update_widgets(self) -> None:
        if self.state is None:
            return
        if self._hud:
            self._hud.show(
                level=self.state.level,
                lines=self.state.lines_cleared,
                score=self.state.score,
                high=self.state.high_score,
            )
        self.show_message(
            overlay_message(
                is_game_over=self.state.is_game_over,
                is_paused=self.state.is_paused,
            )
        )
        if self._board:
            self._board.update_state(
                board=self.state.board,
                current_piece=self.state.current_piece,
                piece_position=self.state.position,
            )


    def action_move_left(self) -> None:
        self._advance(lambda state: move_left(state, self.config))

    def action_move_right(self) -> None:
        self._advance(lambda state: move_right(state, self.config))

    def action_rotate(self) -> None:
        self._advance(lambda state: try_rotate(state, self.config))

    def action_soft_drop(self) -> None:
        self._advance(lambda state: move_down(state, self.config)[0])

    def action_hard_drop(self) -> None:
        self._advance(lambda state: do_hard_drop(state, self.config))

    def action_reset(self) -> None:
        if self.state:
            self.state = create_initial_state(self.config, self.state.high_score)
            self._restart_gravity()
            self._update_widgets()

    def action_pause(self) -> None:
        if self.state:
            self.state = toggle_pause(self.state)
            if self._gravity:
                self._gravity.pause() if self.state.is_paused else self._gravity.resume()
            self._update_widgets()


def main() -> None:
    TetrisApp().run()


if __name__ == "__main__":
    main()
