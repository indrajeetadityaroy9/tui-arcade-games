from dataclasses import replace
from typing import Optional
from .models import Player, Board, GameState, CellValue
HUMAN_PLAYER = Player.O
AI_PLAYER = Player.X
WIN_COMBOS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (6, 4, 2),
)
def create_empty_board() -> Board:
    return tuple(range(9))
def create_initial_state() -> GameState:
    return GameState(
        board=create_empty_board(),
        cursor_position=4,
        is_game_over=False,
        winner=None,
        winning_cells=(),
    )
def get_empty_squares(board: Board) -> list[int]:
    return [cell for cell in board if isinstance(cell, int)]
def check_win(board: Board, player: Player) -> Optional[int]:
    plays = [i for i, cell in enumerate(board) if cell == player]
    for combo_idx, combo in enumerate(WIN_COMBOS):
        if all(cell in plays for cell in combo):
            return combo_idx
    return None
def check_tie(board: Board) -> bool:
    return len(get_empty_squares(board)) == 0
def set_cell(board: Board, index: int, value: CellValue) -> Board:
    return tuple(value if i == index else cell for i, cell in enumerate(board))
def minimax(board: Board, player: Player) -> dict:
    available_spots = get_empty_squares(board)
    if check_win(board, HUMAN_PLAYER) is not None:
        return {"score": -10}
    elif check_win(board, AI_PLAYER) is not None:
        return {"score": 10}
    elif len(available_spots) == 0:
        return {"score": 0}
    moves = []
    for spot in available_spots:
        move = {"index": spot, "score": 0}
        new_board = set_cell(board, spot, player)
        if player == AI_PLAYER:
            result = minimax(new_board, HUMAN_PLAYER)
        else:
            result = minimax(new_board, AI_PLAYER)
        move["score"] = result["score"]
        moves.append(move)
    if player == AI_PLAYER:
        best_score = -10000
        best_move = moves[0]
        for move in moves:
            if move["score"] > best_score:
                best_score = move["score"]
                best_move = move
    else:
        best_score = 10000
        best_move = moves[0]
        for move in moves:
            if move["score"] < best_score:
                best_score = move["score"]
                best_move = move
    return best_move
def get_best_move(board: Board) -> int:
    result = minimax(board, AI_PLAYER)
    return result["index"]
def make_move(state: GameState, index: int) -> GameState:
    if state.is_game_over:
        return state
    if not isinstance(state.board[index], int):
        return state
    new_board = set_cell(state.board, index, HUMAN_PLAYER)
    human_win = check_win(new_board, HUMAN_PLAYER)
    if human_win is not None:
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="You Win!",
            winning_cells=WIN_COMBOS[human_win],
        )
    if check_tie(new_board):
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="Tie Game!",
        )
    ai_move = get_best_move(new_board)
    new_board = set_cell(new_board, ai_move, AI_PLAYER)
    ai_win = check_win(new_board, AI_PLAYER)
    if ai_win is not None:
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="You Lose!",
            winning_cells=WIN_COMBOS[ai_win],
        )
    if check_tie(new_board):
        return replace(
            state,
            board=new_board,
            is_game_over=True,
            winner="Tie Game!",
        )
    return replace(state, board=new_board)
def move_cursor_up(state: GameState) -> GameState:
    if state.cursor_position >= 3:
        return replace(state, cursor_position=state.cursor_position - 3)
    return state
def move_cursor_down(state: GameState) -> GameState:
    if state.cursor_position <= 5:
        return replace(state, cursor_position=state.cursor_position + 3)
    return state
def move_cursor_left(state: GameState) -> GameState:
    if state.cursor_position % 3 != 0:
        return replace(state, cursor_position=state.cursor_position - 1)
    return state
def move_cursor_right(state: GameState) -> GameState:
    if state.cursor_position % 3 != 2:
        return replace(state, cursor_position=state.cursor_position + 1)
    return state
