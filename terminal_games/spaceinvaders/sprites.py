"""Sprite art, in two sizes.

The board is measured in terminal characters, so a bigger invader is bigger art
rather than a scale factor — that keeps movement and collisions at single-column
resolution instead of making the fleet jump in coarse steps. LARGE is the normal
set; SMALL is the fallback for terminals too short or narrow to fit it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpriteSet:
    player: tuple[str, ...]
    enemies: tuple[tuple[str, ...], ...]  # indexed by enemy_type
    player_bullet: str
    enemy_bullet: str

    @property
    def player_width(self) -> int:
        return len(self.player[0])

    @property
    def player_height(self) -> int:
        return len(self.player)

    @property
    def enemy_width(self) -> int:
        return len(self.enemies[0][0])

    @property
    def enemy_height(self) -> int:
        return len(self.enemies[0])

    def enemy(self, enemy_type: int) -> tuple[str, ...]:
        return self.enemies[enemy_type % len(self.enemies)]


LARGE = SpriteSet(
    player=(
        "   ▄   ",
        " ▄███▄ ",
        "███████",
    ),
    enemies=(
        (  # squid
            " ▄██▄ ",
            "▐▌██▐▌",
            " ▀  ▀ ",
        ),
        (  # crab
            "▄ ██ ▄",
            "▐████▌",
            " ▀▀▀▀ ",
        ),
        (  # octopus
            " ████ ",
            "██▄▄██",
            " ▀  ▀ ",
        ),
    ),
    player_bullet="┃",
    enemy_bullet="▼",
)

SMALL = SpriteSet(
    player=(
        " ▄█▄ ",
        "█████",
    ),
    enemies=(
        ("▄█▄", "▀ ▀"),
        ("█▀█", "▀▄▀"),
        ("▀█▀", " ▀ "),
    ),
    player_bullet="│",
    enemy_bullet="▼",
)


def _validate() -> None:
    """Every sprite row must be the same width, or blitting shears the art."""
    for name, sprites in (("LARGE", LARGE), ("SMALL", SMALL)):
        for label, rows in [("player", sprites.player)] + [
            (f"enemy{i}", e) for i, e in enumerate(sprites.enemies)
        ]:
            widths = {len(row) for row in rows}
            assert len(widths) == 1, f"{name}.{label} has ragged rows: {widths}"


_validate()
