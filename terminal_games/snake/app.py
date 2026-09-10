from dataclasses import replace

from textual.app import ComposeResult
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header

from ..core.app import ARCADE_BINDINGS, GAME_CSS, GameApp, arrow_bindings
from ..core.hud import HUD, Stat
from ..core.layout import Grid, fit_grid
from ..core.overlay import MessageOverlay, overlay_message
from .game_logic import (
    change_direction,
    create_initial_state,
    spawn_apple,
    tick,
    toggle_pause,
)
from .models import BoardConfig, Direction, GameState, Position, Snake
from .widgets.game_board import GameBoard

TICK_INTERVAL = 1 / 10

STATS = (
    Stat("level", "LEVEL"),
    Stat("score", "SCORE", pad=4),
    Stat("high", "HIGH SCORE", pad=4),
)


class SnakeApp(GameApp):
    CSS_PATH = GAME_CSS
    TITLE = "Terminal Snake"
    BINDINGS = [
        *arrow_bindings("move_up", "move_down", "move_left", "move_right"),
        *ARCADE_BINDINGS,
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config: BoardConfig | None = None
        self.state: GameState | None = None
        self._timer: Timer | None = None
        self._board: GameBoard | None = None
        self._hud: HUD | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(id="game-container")
        yield Footer()
        yield MessageOverlay()

    def _start(self) -> None:
        self._timer = self.set_interval(TICK_INTERVAL, self._game_tick)


    def _grid(self) -> Grid:
        return fit_grid(
            max(40, self.viewport.width - 6),
            max(14, self.viewport.height - 13),
            min_columns=16,
            min_rows=10,
            max_columns=32,
            max_rows=24,
        )

    def _configure_layout(self, force_reset: bool = False) -> None:
        grid = self._grid()
        new_config = BoardConfig(columns=grid.columns, rows=grid.rows)
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

        if self._timer:
            self._timer.resume()
        self._update_widgets()

    @staticmethod
    def _offset(
        cells: list[Position],
        old: BoardConfig,
        new: BoardConfig,
    ) -> tuple[int, int] | None:
        min_x = min(c.x for c in cells)
        max_x = max(c.x for c in cells)
        min_y = min(c.y for c in cells)
        max_y = max(c.y for c in cells)

        if max_x - min_x + 1 > new.columns or max_y - min_y + 1 > new.rows:
            return None

        dx = max(-min_x, min(new.columns - 1 - max_x, (new.columns - old.columns) // 2))
        dy = max(-min_y, min(new.rows - 1 - max_y, (new.rows - old.rows) // 2))
        return dx, dy

    @staticmethod
    def _scale(value: int, old_max: int, new_max: int) -> int:
        if old_max <= 1:
            return 0
        return round(value * (new_max - 1) / (old_max - 1))

    def _remap(
        self,
        state: GameState,
        old: BoardConfig,
        new: BoardConfig,
    ) -> GameState:
        cells = list(state.snake.cells)
        offset = self._offset(cells, old, new)

        if offset is not None:
            dx, dy = offset
            mapped = [Position(c.x + dx, c.y + dy) for c in cells]
            apple = Position(state.apple.x + dx, state.apple.y + dy)
        else:
            seen: set[Position] = set()
            mapped = []
            for cell in cells:
                pos = self._clamp(
                    self._scale(cell.x, old.columns, new.columns),
                    self._scale(cell.y, old.rows, new.rows),
                    new,
                )
                if pos not in seen:
                    seen.add(pos)
                    mapped.append(pos)
            apple = Position(
                self._scale(state.apple.x, old.columns, new.columns),
                self._scale(state.apple.y, old.rows, new.rows),
            )

        if not mapped:
            mapped = [Position(new.columns // 2, new.rows // 2)]

        snake = Snake(
            head=mapped[0],
            velocity=state.snake.velocity,
            cells=tuple(mapped),
            max_cells=state.snake.max_cells,
        )
        apple = self._clamp(apple.x, apple.y, new)
        if apple in snake.cells:
            apple = spawn_apple(snake.cells, new)

        return replace(state, snake=snake, apple=apple)

    @staticmethod
    def _clamp(x: int, y: int, config: BoardConfig) -> Position:
        return Position(
            max(0, min(config.columns - 1, x)),
            max(0, min(config.rows - 1, y)),
        )


    def _game_tick(self) -> None:
        if self.state is None or self.state.is_game_over or self.state.is_paused:
            return
        self.state = tick(self.state, self.config)
        self._update_widgets()
        if self.state.is_game_over and self._timer:
            self._timer.pause()

    def _update_widgets(self) -> None:
        if self.state is None:
            return
        if self._hud:
            self._hud.show(
                level=self.state.level,
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
                snake_cells=self.state.snake.cells,
                apple=self.state.apple,
            )


    def _steer(self, direction: Direction) -> None:
        if self.state:
            self.state = change_direction(self.state, direction)

    def action_move_up(self) -> None:
        self._steer(Direction.UP)

    def action_move_down(self) -> None:
        self._steer(Direction.DOWN)

    def action_move_left(self) -> None:
        self._steer(Direction.LEFT)

    def action_move_right(self) -> None:
        self._steer(Direction.RIGHT)

    def action_reset(self) -> None:
        if self.state:
            self.state = create_initial_state(self.config, self.state.high_score)
            if self._timer:
                self._timer.resume()
            self._update_widgets()

    def action_pause(self) -> None:
        if self.state:
            self.state = toggle_pause(self.state)
            if self._timer:
                self._timer.pause() if self.state.is_paused else self._timer.resume()
            self._update_widgets()


def main() -> None:
    SnakeApp().run()


if __name__ == "__main__":
    main()
