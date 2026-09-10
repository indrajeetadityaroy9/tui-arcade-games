from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union
class Player(Enum):
    X = "X"
    O = "O"
CellValue = Union[int, Player]
Board = tuple[CellValue, ...]
@dataclass(frozen=True)
class GameState:
    board: Board = (0, 1, 2, 3, 4, 5, 6, 7, 8)
    cursor_position: int = 4
    is_game_over: bool = False
    winner: Optional[str] = None
    winning_cells: tuple[int, ...] = ()
