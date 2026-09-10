from dataclasses import dataclass
from enum import Enum, auto
class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
@dataclass(frozen=True, slots=True)
class Position:
    x: int
    y: int
    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)
    def __hash__(self) -> int:
        return hash((self.x, self.y))
@dataclass(frozen=True)
class Snake:
    head: Position
    velocity: Position  
    cells: tuple[Position, ...]  
    max_cells: int = 6
    @property
    def direction(self) -> Direction:
        if self.velocity.x < 0:
            return Direction.LEFT
        elif self.velocity.x > 0:
            return Direction.RIGHT
        elif self.velocity.y < 0:
            return Direction.UP
        return Direction.DOWN
@dataclass(frozen=True)
class BoardConfig:
    columns: int = 40
    rows: int = 30
@dataclass(frozen=True)
class GameState:
    snake: Snake
    apple: Position
    score: int = 0
    high_score: int = 0
    is_game_over: bool = False
    is_paused: bool = False
    @property
    def level(self) -> int:
        return min(8, (self.score // 8) + 1)
DIRECTION_VECTORS: dict[Direction, Position] = {
    Direction.UP: Position(0, -1),
    Direction.DOWN: Position(0, 1),
    Direction.LEFT: Position(-1, 0),
    Direction.RIGHT: Position(1, 0),
}
OPPOSITE_DIRECTIONS: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}
