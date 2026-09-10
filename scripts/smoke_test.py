import asyncio
import sys
from importlib import import_module

APPS = [
    ("launcher", "terminal_games.launcher", "LauncherApp"),
    ("chess", "terminal_games.chess.app", "ChessApp"),
    ("snake", "terminal_games.snake.app", "SnakeApp"),
    ("tetris", "terminal_games.tetris.app", "TetrisApp"),
    ("tictactoe", "terminal_games.tictactoe.app", "TicTacToeApp"),
    ("spaceinvaders", "terminal_games.spaceinvaders.app", "SpaceInvadersApp"),
]

SIZES = [(120, 40), (80, 24)]


async def check(module: str, cls: str, size: tuple[int, int]) -> None:
    app = getattr(import_module(module), cls)()
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await pilot.resize_terminal(size[0] - 10, size[1] - 4)
        await pilot.pause()


async def main() -> int:
    failures = 0
    for name, module, cls in APPS:
        for size in SIZES:
            label = f"{name} @ {size[0]}x{size[1]}"
            try:
                await check(module, cls, size)
                print(f"  ok    {label}")
            except Exception as exc:
                failures += 1
                print(f"  FAIL  {label}: {type(exc).__name__}: {exc}")
    print(f"\n{len(APPS) * len(SIZES) - failures}/{len(APPS) * len(SIZES)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
