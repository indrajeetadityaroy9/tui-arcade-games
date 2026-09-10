from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from ...core.render import ThemedWidget, on_bg
from ..models import BoardConfig, Bullet, Enemy, Player
from ..sprites import LARGE, SpriteSet


class GameBoard(ThemedWidget):
    DARK = {
        "bg": "#0a0a0a",
        "player": "#00ff00",
        "enemy0": "#ff0000",
        "enemy1": "#ff6600",
        "enemy2": "#ffff00",
        "player_bullet": "#00ffff",
        "enemy_bullet": "#ff00ff",
    }
    LIGHT = {
        "bg": "#f0f0f0",
        "player": "#006600",
        "enemy0": "#cc0000",
        "enemy1": "#cc5500",
        "enemy2": "#999900",
        "player_bullet": "#006699",
        "enemy_bullet": "#990099",
    }

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._config = BoardConfig()
        self._sprites: SpriteSet = LARGE
        self._player = Player(x=self._config.width // 2)
        self._enemies: tuple[Enemy, ...] = ()
        self._player_bullets: tuple[Bullet, ...] = ()
        self._enemy_bullets: tuple[Bullet, ...] = ()

    def build_styles(self, colors: dict[str, str]) -> dict:
        bg = colors["bg"]
        styles = {"bg": Style(bgcolor=bg)}
        for key in (
            "player",
            "enemy0",
            "enemy1",
            "enemy2",
            "player_bullet",
            "enemy_bullet",
        ):
            styles[key] = on_bg(colors[key], bg, bold=True)
        return styles

    def set_config(self, config: BoardConfig, sprites: SpriteSet) -> None:
        self._config = config
        self._sprites = sprites
        self.refresh()

    def update_state(
        self,
        player: Player,
        enemies: tuple[Enemy, ...],
        player_bullets: tuple[Bullet, ...],
        enemy_bullets: tuple[Bullet, ...],
    ) -> None:
        self._player = player
        self._enemies = enemies
        self._player_bullets = player_bullets
        self._enemy_bullets = enemy_bullets
        self.refresh()

    def get_content_width(self, container, viewport) -> int:
        return self._config.width

    def get_content_height(self, container, viewport, width) -> int:
        return self._config.height

    def render_line(self, y: int) -> Strip:
        styles = self.styles_for_theme
        sprites = self._sprites
        width = self._config.width
        bg = styles["bg"]

        chars = [" "] * width
        cell_styles: list[Style] = [bg] * width

        def blit(text: str, x: int, style: Style) -> None:
            for offset, char in enumerate(text):
                pos = x + offset
                if 0 <= pos < width and char != " ":
                    chars[pos] = char
                    cell_styles[pos] = style

        for enemy in self._enemies:
            if not enemy.active:
                continue
            row = y - enemy.y
            if 0 <= row < sprites.enemy_height:
                blit(sprites.enemy(enemy.enemy_type)[row], enemy.x, styles[f"enemy{enemy.enemy_type}"])

        player_row = y - self._config.player_y
        if 0 <= player_row < sprites.player_height:
            blit(sprites.player[player_row], self._player.x, styles["player"])

        for bullet in self._player_bullets:
            if bullet.active and bullet.y == y:
                blit(sprites.player_bullet, bullet.x, styles["player_bullet"])

        for bullet in self._enemy_bullets:
            if bullet.active and bullet.y == y:
                blit(sprites.enemy_bullet, bullet.x, styles["enemy_bullet"])

        segments: list[Segment] = []
        run_start = 0
        for index in range(1, width + 1):
            if index == width or cell_styles[index] is not cell_styles[run_start]:
                segments.append(
                    Segment("".join(chars[run_start:index]), cell_styles[run_start])
                )
                run_start = index
        return Strip(segments)
