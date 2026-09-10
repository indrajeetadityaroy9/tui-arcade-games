"""Block sizing for the grid games.

A terminal cell is about twice as tall as it is wide, so a square-looking block
is `2 * scale` columns by `scale` rows. Scale 1 (the old fixed size) draws each
game cell as a single terminal row, which reads as granular speckle rather than
as blocks. This picks the largest scale that still leaves a playable grid.
"""

from dataclasses import dataclass

#: Blocks stop growing here — past this they crowd out the playfield.
MAX_SCALE = 2


@dataclass(frozen=True)
class Grid:
    columns: int
    rows: int
    cell_width: int
    cell_height: int


def fit_grid(
    available_width: int,
    available_height: int,
    *,
    min_columns: int,
    min_rows: int,
    max_columns: int,
    max_rows: int,
    max_scale: int = MAX_SCALE,
) -> Grid:
    """Largest block scale whose grid still meets the minimums.

    `available_*` is the space left for the board including its own 1-char
    border. Falls back to scale 1 when even that cannot meet the minimums —
    the terminal is simply too small, and the game clamps instead of vanishing.
    """
    inner_width = max(0, available_width - 2)
    inner_height = max(0, available_height - 2)

    for scale in range(max_scale, 0, -1):
        cell_width, cell_height = scale * 2, scale
        columns = inner_width // cell_width
        rows = inner_height // cell_height
        if scale > 1 and (columns < min_columns or rows < min_rows):
            continue
        return Grid(
            columns=max(min_columns, min(max_columns, columns)),
            rows=max(min_rows, min(max_rows, rows)),
            cell_width=cell_width,
            cell_height=cell_height,
        )

    raise AssertionError("scale 1 always returns")
