import sys
from importlib import import_module
from typing import Optional
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static, ListView, ListItem, Label
from .config import get_theme, set_theme

GAMES = [
    ("chess", "Chess", "Classic chess with AI opponent"),
    ("snake", "Snake", "Eat food and grow longer"),
    ("tetris", "Tetris", "Stack falling blocks"),
    ("tictactoe", "Tic-Tac-Toe", "Classic X and O game"),
    ("spaceinvaders", "Space Invaders", "Defend against alien invasion"),
]

GAME_ICONS = {
    "chess": "\u265a",
    "snake": "\u25cf",
    "tetris": "\u25a0",
    "tictactoe": "\u2715",
    "spaceinvaders": "\u25b2",
}

class LauncherApp(App):
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen {
        align: center middle;
        background: $background;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        padding: 1 0;
        margin-bottom: 1;
    }

    #menu-container {
        width: 60;
        height: auto;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }

    ListView {
        width: 100%;
        height: auto;
        max-height: 20;
    }

    ListItem {
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }

    Label {
        width: 100%;
    }

    #instructions {
        text-align: center;
        color: $text-muted;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("t", "toggle_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Terminal Games"

    def __init__(self) -> None:
        super().__init__()
        self._selected_game: Optional[str] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("[bold]Terminal Games[/bold]", id="title", markup=True),
            ListView(
                *[
                    ListItem(
                        Label(
                            f"{GAME_ICONS.get(game_id, ' ')} [bold]{name}[/]\n[dim]{desc}[/]",
                        ),
                        id=f"game-{game_id}",
                    )
                    for game_id, name, desc in GAMES
                ],
                id="menu",
            ),
            Static("[dim]Arrow keys to navigate, Enter to select, Q to quit[/dim]", id="instructions", markup=True),
            id="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.theme = get_theme()
        self.query_one(ListView).focus()

    @on(ListView.Selected)
    def handle_game_selected(self, event: ListView.Selected) -> None:
        if event.item:
            game_id = event.item.id.replace("game-", "")
            self._selected_game = game_id
            self.exit()

    def action_toggle_theme(self) -> None:
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"
        set_theme(self.theme)

    @property
    def selected_game(self) -> Optional[str]:
        return self._selected_game


def launch_game(game_id: str) -> int:
    try:
        module = import_module(f"terminal_games.{game_id}.app")
        main_func = getattr(module, "main")
        main_func()
        return 0
    except (ImportError, AttributeError) as e:
        print(f"Error launching {game_id}: {e}")
        return 1


def main() -> int:
    if len(sys.argv) > 1:
        game_id = sys.argv[1].lower()
        valid_games = [g[0] for g in GAMES]
        if game_id in valid_games:
            return launch_game(game_id)
        else:
            print(f"Unknown game: {game_id}")
            print(f"Available games: {', '.join(valid_games)}")
            return 1

    while True:
        app = LauncherApp()
        app.run()

        selected = app.selected_game
        if selected is None:
            return 0

        launch_game(selected)


if __name__ == "__main__":
    sys.exit(main())
