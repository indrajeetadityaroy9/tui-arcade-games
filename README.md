# Terminal Games

A collection of classic terminal games — Chess, Snake, Tetris, Tic-Tac-Toe and
Space Invaders — built with [Textual](https://textual.textualize.io/).

All five resize live with your terminal and preserve game state while they do it.
Snake and Tetris also scale their block size to the space available, falling back
to single-row blocks only when the terminal is too small for anything larger.

## Play

Install once, play from anywhere:

```bash
uv tool install .
terminal-games
```

That puts `terminal-games` and `tg-chess` / `tg-snake` / `tg-tetris` /
`tg-tictactoe` / `tg-spaceinvaders` on your `PATH` in an isolated environment.
No virtualenv to activate. Upgrade later with `uv tool upgrade terminal-games`.

`terminal-games` opens a menu; `terminal-games snake` jumps straight into one.

## Develop

The project is configured for [mise](https://mise.jdx.dev/), which auto-activates
`.venv` when you `cd` in and keeps it matching `uv.lock`:

```bash
mise trust        # once, to allow this repo's mise.toml
mise run play
```

After that, `terminal-games` works directly in the project directory — no
`source .venv/bin/activate`.

Without mise, prefix any command with `uv run`:

```bash
uv run terminal-games
```

Both paths install the package in editable mode, so source edits take effect
immediately.

### Tasks

```
mise run play     # launcher menu          mise run sync   # reinstall from uv.lock
mise run chess    # a single game          mise run smoke  # headless render check
```

`mise run smoke` mounts all six apps through Textual's test pilot at two terminal
sizes and forces a resize on each — the only practical way to verify a TUI starts
without a human watching it.

## Controls

Shared across games: arrow keys or `WASD` to move, `r` restart, `t` toggle
light/dark, `q` quit. `p` pauses Snake, Tetris and Space Invaders. `space` is
hard-drop in Tetris and fire in Space Invaders; `enter` selects in Chess and
Tic-Tac-Toe.

The theme choice persists across games within a session.

## Layout

Each game is a self-contained package with the same four-layer split:

```
terminal_games/
├── core/           shared GameApp base, HUD/Status widgets, themed renderer, game.tcss
├── launcher.py     the menu
├── config.py       cross-game theme setting
└── <game>/
    ├── models.py       frozen dataclasses — GameState, BoardConfig
    ├── game_logic.py   pure state → state functions, no Textual imports
    ├── widgets/        ThemedWidget subclasses overriding render_line(y)
    └── app.py          GameApp subclass — bindings, timers, wiring
```

`core.GameApp` owns the mount sequence, the resize hook and the theme toggle;
`core.ThemedWidget` caches `rich.Style` objects and rebuilds them only when the
theme changes. Only chess carries its own stylesheet — the rest share
`core/styles/game.tcss`.

Requires Python 3.10+.
