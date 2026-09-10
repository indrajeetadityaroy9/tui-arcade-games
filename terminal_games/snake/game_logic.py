import random
from dataclasses import replace
from typing import Optional

from .models import (
    Position,
    Snake,
    GameState,
    BoardConfig,
    Direction,
    DIRECTION_VECTORS,
    OPPOSITE_DIRECTIONS,
)


def create_initial_state(config: BoardConfig, high_score: int = 0) -> GameState:
    center = Position(config.columns // 2, config.rows // 2)
    initial_cells = tuple(Position(center.x - i, center.y) for i in range(6))
    snake = Snake(
        head=center,
        velocity=Position(1, 0),
        cells=initial_cells,
        max_cells=6,
    )
    return GameState(
        snake=snake,
        apple=spawn_apple(snake.cells, config),
        high_score=high_score,
    )


def spawn_apple(
    occupied_cells: tuple[Position, ...],
    config: BoardConfig,
    max_attempts: int = 512,
) -> Position:
    occupied = set(occupied_cells)
    for _ in range(max_attempts):
        pos = Position(
            random.randint(0, config.columns - 1),
            random.randint(0, config.rows - 1),
        )
        if pos not in occupied:
            return pos
    # Board is nearly full — fall back to an exhaustive scan.
    free = {
        Position(x, y)
        for x in range(config.columns)
        for y in range(config.rows)
    } - occupied
    return next(iter(free)) if free else Position(0, 0)


def wrap_position(pos: Position, config: BoardConfig) -> Position:
    return Position(pos.x % config.columns, pos.y % config.rows)


def can_change_direction(current: Direction, target: Direction) -> bool:
    return OPPOSITE_DIRECTIONS[current] != target


def update_snake(
    snake: Snake,
    config: BoardConfig,
) -> tuple[Snake, Optional[Position]]:
    new_head = wrap_position(snake.head + snake.velocity, config)
    new_cells = (new_head,) + snake.cells
    old_tail: Optional[Position] = None
    if len(new_cells) > snake.max_cells:
        old_tail = new_cells[-1]
        new_cells = new_cells[:-1]
    return replace(snake, head=new_head, cells=new_cells), old_tail


def check_self_collision(snake: Snake) -> bool:
    if len(snake.cells) < 2:
        return False
    return snake.head in snake.cells[1:]


def check_apple_collision(snake: Snake, apple: Position) -> bool:
    return snake.head == apple


def grow_snake(snake: Snake) -> Snake:
    return replace(snake, max_cells=snake.max_cells + 1)


def tick(state: GameState, config: BoardConfig) -> GameState:
    if state.is_paused or state.is_game_over:
        return state

    new_snake, _ = update_snake(state.snake, config)

    if check_self_collision(new_snake):
        return replace(
            state,
            snake=new_snake,
            high_score=max(state.high_score, state.score),
            is_game_over=True,
            is_paused=False,
        )

    score = state.score
    apple = state.apple
    if check_apple_collision(new_snake, apple):
        new_snake = grow_snake(new_snake)
        score += 1
        apple = spawn_apple(new_snake.cells, config)

    return replace(
        state,
        snake=new_snake,
        apple=apple,
        score=score,
        high_score=max(state.high_score, score),
    )


def change_direction(state: GameState, new_direction: Direction) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    if not can_change_direction(state.snake.direction, new_direction):
        return state
    velocity = DIRECTION_VECTORS[new_direction]
    return replace(state, snake=replace(state.snake, velocity=velocity))


def toggle_pause(state: GameState) -> GameState:
    if state.is_game_over:
        return state
    return replace(state, is_paused=not state.is_paused)
