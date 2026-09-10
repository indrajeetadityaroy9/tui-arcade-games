import math
from functools import lru_cache

BLOCK = "█"
SQRT2 = math.sqrt(2.0)

STROKE = 0.16
INNER_RADIUS = 0.74


def _clamp(value: float, low: float, high: float) -> float:
    return low if value < low else high if value > high else value


@lru_cache(maxsize=512)
def mark_row(mark: str, cell_width: int, cell_height: int, line: int) -> str:
    height = max(3, cell_height - 2)
    width = max(6, cell_width - 4)
    top = (cell_height - height) // 2
    left = max(0, (cell_width - width) // 2)

    row = line - top
    if not 0 <= row < height:
        return " " * cell_width

    centre_y, radius_y = (height - 1) / 2, height / 2
    centre_x, radius_x = (width - 1) / 2, width / 2

    y = (row - centre_y) / radius_y
    y_low = (row - 0.5 - centre_y) / radius_y
    y_high = (row + 0.5 - centre_y) / radius_y

    cells = []
    for column in range(width):
        x = (column - centre_x) / radius_x
        x_low = (column - 0.5 - centre_x) / radius_x
        x_high = (column + 0.5 - centre_x) / radius_x

        if mark == "O":
            nearest = math.hypot(_clamp(0.0, x_low, x_high), _clamp(0.0, y_low, y_high))
            farthest = math.hypot(
                max(abs(x_low), abs(x_high)), max(abs(y_low), abs(y_high))
            )
            on = nearest <= 1.0 <= farthest or INNER_RADIUS <= math.hypot(x, y) <= 1.0
        else:
            distance = min(abs(x - y), abs(x + y)) / SQRT2
            on = distance <= STROKE and max(abs(x), abs(y)) <= 1.0

        cells.append(BLOCK if on else " ")

    body = "".join(cells)
    return (" " * left + body + " " * cell_width)[:cell_width]
