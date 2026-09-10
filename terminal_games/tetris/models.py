from dataclasses import dataclass
from typing import Optional
@dataclass(frozen=True)
class Position:
    x: int
    y: int
    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)
@dataclass(frozen=True)
class Tetromino:
    shape: tuple[tuple[int, ...], ...]
    color: int
@dataclass(frozen=True)
class BoardConfig:
    width: int = 14
    height: int = 24
@dataclass(frozen=True)
class GameState:
    board: tuple[tuple[int, ...], ...]
    current_piece: Optional[Tetromino]
    position: Position
    score: int = 0
    high_score: int = 0
    level: int = 1
    lines_cleared: int = 0
    combo: int = 0
    last_clear_was_tetris: bool = False
    is_game_over: bool = False
    is_paused: bool = False
    clearing_rows: tuple[int, ...] = ()
