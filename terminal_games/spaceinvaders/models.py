from dataclasses import dataclass

from .sprites import LARGE

DEFAULT_BOARD_WIDTH = 76
DEFAULT_BOARD_HEIGHT = 24


@dataclass(frozen=True)
class Player:
    x: int
    width: int = 7


@dataclass(frozen=True)
class Bullet:
    x: int
    y: int
    active: bool = True
    is_enemy: bool = False


@dataclass(frozen=True)
class Enemy:
    x: int
    y: int
    enemy_type: int
    active: bool = True


@dataclass(frozen=True)
class BoardConfig:
    width: int = DEFAULT_BOARD_WIDTH
    height: int = DEFAULT_BOARD_HEIGHT
    player_y: int = DEFAULT_BOARD_HEIGHT - LARGE.player_height
    player_width: int = LARGE.player_width
    player_height: int = LARGE.player_height
    enemy_rows: int = 4
    enemy_cols: int = 9
    enemy_width: int = LARGE.enemy_width
    enemy_height: int = LARGE.enemy_height
    enemy_spacing: int = 2
    enemy_row_spacing: int = 0


@dataclass(frozen=True)
class GameState:
    config: BoardConfig
    player: Player
    enemies: tuple[Enemy, ...] = ()
    player_bullets: tuple[Bullet, ...] = ()
    enemy_bullets: tuple[Bullet, ...] = ()
    score: int = 0
    high_score: int = 0
    level: int = 1
    direction: int = 1
    is_paused: bool = False
    is_game_over: bool = False
    is_won: bool = False
    can_shoot: bool = True
