from .models import Tetromino
I_PIECE = Tetromino(
    shape=(
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
    ),
    color=1,
)
J_PIECE = Tetromino(
    shape=(
        (2, 0, 0),
        (2, 2, 2),
        (0, 0, 0),
    ),
    color=2,
)
L_PIECE = Tetromino(
    shape=(
        (0, 0, 3),
        (3, 3, 3),
        (0, 0, 0),
    ),
    color=3,
)
O_PIECE = Tetromino(
    shape=(
        (4, 4),
        (4, 4),
    ),
    color=4,
)
S_PIECE = Tetromino(
    shape=(
        (0, 5, 5),
        (5, 5, 0),
        (0, 0, 0),
    ),
    color=5,
)
T_PIECE = Tetromino(
    shape=(
        (0, 6, 0),
        (6, 6, 6),
        (0, 0, 0),
    ),
    color=6,
)
Z_PIECE = Tetromino(
    shape=(
        (7, 7, 0),
        (0, 7, 7),
        (0, 0, 0),
    ),
    color=7,
)
ALL_PIECES = [I_PIECE, J_PIECE, L_PIECE, O_PIECE, S_PIECE, T_PIECE, Z_PIECE]
