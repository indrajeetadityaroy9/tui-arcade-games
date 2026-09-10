from enum import IntEnum

import chess


class PieceSize(IntEnum):

    SMALL = 1
    COMPACT = 2
    EXTENDED = 3
    LARGE = 4


MIN_CELL = {
    PieceSize.SMALL: (1, 1),
    PieceSize.COMPACT: (5, 3),
    PieceSize.EXTENDED: (5, 4),
    PieceSize.LARGE: (9, 5),
}

ART: dict[tuple[int, PieceSize], tuple[str, ...]] = {
    (chess.PAWN, PieceSize.COMPACT): (
        '  ▂  ',
        ' ▆█▆ ',
        ' ▔▔▔ ',
    ),
    (chess.PAWN, PieceSize.EXTENDED): (
        '     ',
        ' ▝█▘ ',
        ' ▟█▙ ',
        ' ▔▔▔ ',
    ),
    (chess.PAWN, PieceSize.LARGE): (
        '',
        ' ▄▇▄',
        ' ▜█▛',
        '▄███▄',
        '▔▔▔▔▔',
    ),
    (chess.KNIGHT, PieceSize.COMPACT): (
        ' ▄▟▟▖',
        ' ▂█▛▘',
        '▝▀▀▀▘',
    ),
    (chess.KNIGHT, PieceSize.EXTENDED): (
        '  ▖▗ ',
        '▗▇▟█▌',
        ' ▟█▛ ',
        '▝▀▀▀▘',
    ),
    (chess.KNIGHT, PieceSize.LARGE): (
        '  ▅ ▅',
        ' ▟▛███▖',
        '▝▀▜███▊',
        ' ▗███▛ ',
        ' ▀▀▀▀▀ ',
    ),
    (chess.BISHOP, PieceSize.COMPACT): (
        ' ▆▖▆ ',
        ' ▐▙▌ ',
        ' ▀▀▀ ',
    ),
    (chess.BISHOP, PieceSize.EXTENDED): (
        ' ▄▁▗ ',
        ' ██▟ ',
        ' ▟█▙ ',
        '▝▀▀▀▘',
    ),
    (chess.BISHOP, PieceSize.LARGE): (
        '▗▅  ▖',
        '██▍ █',
        '███▍█',
        '▝███▘',
        '▀▀▀▀▀',
    ),
    (chess.ROOK, PieceSize.COMPACT): (
        ' ▅ ▅ ',
        ' ███ ',
        '▝▀▀▀▘',
    ),
    (chess.ROOK, PieceSize.EXTENDED): (
        '▄ ▄ ▄',
        '█████',
        ' ███ ',
        '▀▀▀▀▀',
    ),
    (chess.ROOK, PieceSize.LARGE): (
        '▗▄ ▃ ▄▖',
        '▐█▄█▄█▌',
        '▝▜███▛▘',
        ' ▟███▙ ',
        '▝▀▀▀▀▀▘',
    ),
    (chess.QUEEN, PieceSize.COMPACT): (
        ' ▆▄▆ ',
        ' ▗█▖ ',
        ' ▀▀▀ ',
    ),
    (chess.QUEEN, PieceSize.EXTENDED): (
        '▂ ▄ ▂',
        '▜▙█▟▛',
        ' ▜█▛ ',
        '▝▀▀▀▘',
    ),
    (chess.QUEEN, PieceSize.LARGE): (
        '▗  ▂  ▖',
        '▐▙▟█▙▟▌',
        ' ▜███▛ ',
        ' ▗███▖ ',
        '▝▀▀▀▀▀▘',
    ),
    (chess.KING, PieceSize.COMPACT): (
        '▗▂╋▂▖',
        ' ▀█▀ ',
        ' ▀▀▀ ',
    ),
    (chess.KING, PieceSize.EXTENDED): (
        ' ▂╋▂ ',
        '▜███▛',
        ' ▜█▛ ',
        '▝▀▀▀▘',
    ),
    (chess.KING, PieceSize.LARGE): (
        '  ▂▃╋▃▂  ',
        ' ▐█████▋ ',
        '  ▜███▛  ',
        '   ▟█▙   ',
        '  ▀▀▀▀▀  ',
    ),
}


def size_for(cell_width: int, cell_height: int) -> PieceSize:
    for size in (PieceSize.LARGE, PieceSize.EXTENDED, PieceSize.COMPACT):
        min_width, min_height = MIN_CELL[size]
        if cell_width >= min_width and cell_height >= min_height:
            return size
    return PieceSize.SMALL


def art_for(piece_type: int, size: PieceSize) -> tuple[str, ...] | None:
    return ART.get((piece_type, size))
