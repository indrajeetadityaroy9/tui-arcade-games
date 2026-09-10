from dataclasses import replace

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Footer, Header

from ..core.app import ARCADE_BINDINGS, GAME_CSS, GameApp
from ..core.hud import HUD, Stat
from ..core.overlay import MessageOverlay, overlay_message
from .game_logic import (
    check_collisions,
    check_win,
    create_initial_state,
    enemy_shoot,
    get_enemy_move_interval,
    get_enemy_shoot_interval,
    move_player_left,
    move_player_right,
    reset_shoot_cooldown,
    shoot_player_bullet,
    toggle_pause,
    update_enemies,
    update_enemy_bullets,
    update_player_bullets,
)
from .models import BoardConfig, GameState
from .sprites import LARGE, SMALL, SpriteSet
from .widgets.game_board import GameBoard

TICK_INTERVAL = 0.05
SHOOT_COOLDOWN = 0.25
MAX_LEVEL = 8

MAX_BOARD_WIDTH = 80
MAX_ENEMY_ROWS = 4
MAX_ENEMY_COLS = 7
DESCENT_MARGIN = 3
FLEET_TOP = 2

STATS = (
    Stat("score", "SCORE", pad=6),
    Stat("high", "HIGH SCORE", pad=6),
    Stat("level", "LEVEL"),
)


class SpaceInvadersApp(GameApp):
    CSS_PATH = GAME_CSS
    TITLE = "Terminal Space Invaders"
    BINDINGS = [
        Binding("left", "move_left", "", show=False),
        Binding("a", "move_left", "", show=False),
        Binding("right", "move_right", "", show=False),
        Binding("d", "move_right", "", show=False),
        Binding("space", "shoot", "Fire"),
        *ARCADE_BINDINGS,
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config: BoardConfig | None = None
        self.sprites: SpriteSet = LARGE
        self.state: GameState | None = None
        self._board: GameBoard | None = None
        self._hud: HUD | None = None
        self._timer: Timer | None = None
        self._cooldown: Timer | None = None
        self._move_accum = 0.0
        self._shoot_accum = 0.0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(HUD(*STATS, id="hud"), GameBoard(id="game-board"), id="game-container")
        yield Footer()
        yield MessageOverlay()

    def _start(self) -> None:
        self._board = self.query_one("#game-board", GameBoard)
        self._hud = self.query_one("#hud", HUD)
        self._board.set_config(self.config, self.sprites)
        self._restart_timers()


    def _calculate_config(self) -> tuple[SpriteSet, BoardConfig]:
        available_width = max(30, self.viewport.width - 6)
        available_height = max(11, self.viewport.height - 14)

        sprites = LARGE if available_width >= 50 and available_height >= 20 else SMALL

        width = min(MAX_BOARD_WIDTH, available_width)
        height = available_height
        player_y = max(sprites.player_height + 3, height - sprites.player_height)

        spacing, row_spacing = 2, 0
        pitch_x = sprites.enemy_width + spacing
        pitch_y = sprites.enemy_height + row_spacing

        cols = min(MAX_ENEMY_COLS, max(2, (width + spacing) // pitch_x))
        room = player_y - FLEET_TOP - DESCENT_MARGIN
        rows = min(MAX_ENEMY_ROWS, max(2, room // pitch_y))

        return sprites, BoardConfig(
            width=width,
            height=height,
            player_y=player_y,
            player_width=sprites.player_width,
            player_height=sprites.player_height,
            enemy_rows=rows,
            enemy_cols=cols,
            enemy_width=sprites.enemy_width,
            enemy_height=sprites.enemy_height,
            enemy_spacing=spacing,
            enemy_row_spacing=row_spacing,
        )

    def _configure_layout(self, force_reset: bool = False) -> None:
        sprites, new_config = self._calculate_config()
        if not force_reset and self.config == new_config and self.sprites is sprites:
            return
        self.sprites = sprites

        old_config, self.config = self.config, new_config
        if self.state and old_config:
            self.state = self._remap(self.state, old_config, new_config)
        else:
            self.state = create_initial_state(
                level=self.state.level if self.state else 1,
                high_score=self.state.high_score if self.state else 0,
                config=new_config,
            )

        if self._board:
            self._board.set_config(new_config, sprites)
            self._restart_timers()
        self._update_widgets()

    def _remap(
        self,
        state: GameState,
        old: BoardConfig,
        new: BoardConfig,
    ) -> GameState:
        dx = (new.width - old.width) // 2
        dy = new.player_y - old.player_y

        if state.enemies:
            min_x = min(e.x for e in state.enemies)
            max_x = max(e.x + old.enemy_width - 1 for e in state.enemies)
            min_y = min(e.y for e in state.enemies)
            max_y = max(e.y + old.enemy_height - 1 for e in state.enemies)
            dx = max(-min_x, min(new.width - 1 - max_x, dx))
            dy = max(-min_y, min(new.height - 1 - max_y, dy))

        def shift(bullets):
            moved = (replace(b, x=b.x + dx, y=b.y + dy) for b in bullets)
            return tuple(b for b in moved if 0 <= b.x < new.width and 0 <= b.y < new.height)

        return replace(
            state,
            config=new,
            player=replace(
                state.player,
                x=max(0, min(new.width - new.player_width, state.player.x + dx)),
            ),
            enemies=tuple(
                replace(
                    e,
                    x=max(0, min(new.width - new.enemy_width, e.x + dx)),
                    y=max(0, min(new.height - new.enemy_height, e.y + dy)),
                )
                for e in state.enemies
            ),
            player_bullets=shift(state.player_bullets),
            enemy_bullets=shift(state.enemy_bullets),
        )


    def _restart_timers(self) -> None:
        for timer in (self._timer, self._cooldown):
            if timer:
                timer.stop()
        self._cooldown = None
        self._move_accum = self._shoot_accum = 0.0
        self._timer = self.set_interval(TICK_INTERVAL, self._game_tick)

    @property
    def _is_active(self) -> bool:
        state = self.state
        return bool(state and not (state.is_game_over or state.is_paused or state.is_won))

    def _game_tick(self) -> None:
        if not self._is_active:
            return
        state = self.state

        self._move_accum += TICK_INTERVAL
        move_interval = get_enemy_move_interval(state.level)
        if self._move_accum >= move_interval:
            state = update_enemies(state)
            self._move_accum -= move_interval

        self._shoot_accum += TICK_INTERVAL
        shoot_interval = get_enemy_shoot_interval(state.level)
        if self._shoot_accum >= shoot_interval:
            state = enemy_shoot(state)
            self._shoot_accum -= shoot_interval

        state = update_player_bullets(state)
        state = update_enemy_bullets(state)
        state = check_collisions(state)
        self.state = check_win(state)
        self._update_widgets()

    def _update_widgets(self) -> None:
        if self.state is None:
            return
        if self._hud:
            self._hud.show(
                score=self.state.score,
                high=self.state.high_score,
                level=self.state.level,
            )
        self.show_message(self._status())
        if self._board:
            self._board.update_state(
                player=self.state.player,
                enemies=self.state.enemies,
                player_bullets=self.state.player_bullets,
                enemy_bullets=self.state.enemy_bullets,
            )

    def _status(self) -> str:
        won = ""
        if self.state.is_won:
            won = (
                "[bold green]YOU WIN![/]\n\n[dim]Press R to play again[/]"
                if self.state.level >= MAX_LEVEL
                else "[bold green]STAGE CLEAR![/]\n\n[dim]Press R for next level[/]"
            )
        return overlay_message(
            is_game_over=self.state.is_game_over,
            is_paused=self.state.is_paused,
            won=won,
        )


    def action_move_left(self) -> None:
        if self._is_active:
            self.state = move_player_left(self.state)
            self._update_widgets()

    def action_move_right(self) -> None:
        if self._is_active:
            self.state = move_player_right(self.state)
            self._update_widgets()

    def action_shoot(self) -> None:
        if not self._is_active or not self.state.can_shoot:
            return
        self.state = shoot_player_bullet(self.state)
        self._update_widgets()
        if self._cooldown:
            self._cooldown.stop()
        self._cooldown = self.set_timer(SHOOT_COOLDOWN, self._clear_cooldown)

    def _clear_cooldown(self) -> None:
        if self.state:
            self.state = reset_shoot_cooldown(self.state)

    def action_reset(self) -> None:
        advancing = self.state.is_won and self.state.level < MAX_LEVEL
        carried_score = self.state.score
        self.state = create_initial_state(
            level=self.state.level + 1 if advancing else 1,
            high_score=self.state.high_score,
            config=self.config,
        )
        if advancing:
            self.state = replace(self.state, score=carried_score)
        self._restart_timers()
        self._update_widgets()

    def action_pause(self) -> None:
        if self.state:
            self.state = toggle_pause(self.state)
            self._update_widgets()


def main() -> None:
    SpaceInvadersApp().run()


if __name__ == "__main__":
    main()
