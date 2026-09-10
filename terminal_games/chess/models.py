from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional
import chess
class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4
@dataclass(frozen=True)
class GameConfig:
    player_color: chess.Color = chess.WHITE
    difficulty: Difficulty = Difficulty.HARD
@dataclass(frozen=True)
class GameState:
    board: chess.Board
    cursor_square: int = chess.E2
    selected_square: Optional[int] = None
    config: GameConfig = GameConfig()
    is_thinking: bool = False
    def get_legal_moves_from_selected(self) -> list[int]:
        if self.selected_square is None:
            return []
        moves = []
        for move in self.board.legal_moves:
            if move.from_square == self.selected_square:
                moves.append(move.to_square)
        return moves
    def is_player_turn(self) -> bool:
        return self.board.turn == self.config.player_color
    def get_game_status(self) -> str:
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"Checkmate! {winner} wins!"
        if self.board.is_stalemate():
            return "Stalemate - Draw!"
        if self.board.is_insufficient_material():
            return "Draw - Insufficient material"
        if self.board.is_seventyfive_moves():
            return "Draw - 75 move rule"
        if self.board.is_fivefold_repetition():
            return "Draw - Fivefold repetition"
        if self.board.is_check():
            return "Check!"
        return ""
    def is_game_over(self) -> bool:
        return self.board.is_game_over()
def create_initial_state(
    player_color: chess.Color = chess.WHITE,
    difficulty: Difficulty = Difficulty.HARD
) -> GameState:
    config = GameConfig(player_color=player_color, difficulty=difficulty)
    cursor = chess.E2 if player_color == chess.WHITE else chess.E7
    return GameState(
        board=chess.Board(),
        cursor_square=cursor,
        config=config,
    )
def push_move(state: GameState, move: chess.Move) -> GameState:
    new_board = state.board.copy()
    new_board.push(move)
    return replace(state, board=new_board, selected_square=None)
PIECE_SYMBOLS = {
    (chess.PAWN, chess.WHITE): "♙",
    (chess.KNIGHT, chess.WHITE): "♘",
    (chess.BISHOP, chess.WHITE): "♗",
    (chess.ROOK, chess.WHITE): "♖",
    (chess.QUEEN, chess.WHITE): "♕",
    (chess.KING, chess.WHITE): "♔",
    (chess.PAWN, chess.BLACK): "♟",
    (chess.KNIGHT, chess.BLACK): "♞",
    (chess.BISHOP, chess.BLACK): "♝",
    (chess.ROOK, chess.BLACK): "♜",
    (chess.QUEEN, chess.BLACK): "♛",
    (chess.KING, chess.BLACK): "♚",
}
def get_piece_symbol(piece: Optional[chess.Piece]) -> str:
    if piece is None:
        return " "
    return PIECE_SYMBOLS.get((piece.piece_type, piece.color), "?")
