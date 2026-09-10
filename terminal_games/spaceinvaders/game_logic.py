import random
from dataclasses import replace
from .models import (
    Player,
    Bullet,
    Enemy,
    GameState,
    BoardConfig,
)
def create_initial_state(
    level: int = 1,
    high_score: int = 0,
    config: BoardConfig | None = None,
) -> GameState:
    board_config = config or BoardConfig()
    player = Player(x=(board_config.width - board_config.player_width) // 2)
    enemies = init_enemies(board_config)
    return GameState(
        config=board_config,
        player=player,
        enemies=enemies,
        player_bullets=(),
        enemy_bullets=(),
        score=0,
        high_score=high_score,
        level=level,
        direction=1,
        is_paused=False,
        is_game_over=False,
        is_won=False,
        can_shoot=True,
    )
def init_enemies(config: BoardConfig) -> tuple[Enemy, ...]:
    enemies = []
    grid_width = (
        config.enemy_cols * (config.enemy_width + config.enemy_spacing)
        - config.enemy_spacing
    )
    start_x = (config.width - grid_width) // 2
    start_y = 2
    for row in range(config.enemy_rows):
        if row == 0:
            enemy_type = 0
        elif row == 1:
            enemy_type = 1
        else:
            enemy_type = 2
        for col in range(config.enemy_cols):
            x = start_x + col * (config.enemy_width + config.enemy_spacing)
            y = start_y + row * (config.enemy_height + config.enemy_row_spacing)
            enemies.append(Enemy(x=x, y=y, enemy_type=enemy_type))
    return tuple(enemies)
def move_player_left(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    new_x = max(0, state.player.x - 2)
    new_player = replace(state.player, x=new_x)
    return replace(state, player=new_player)
def move_player_right(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    max_x = state.config.width - state.config.player_width
    new_x = min(max_x, state.player.x + 2)
    new_player = replace(state.player, x=new_x)
    return replace(state, player=new_player)
def shoot_player_bullet(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused or not state.can_shoot:
        return state
    bullet_x = state.player.x + state.config.player_width // 2
    bullet_y = state.config.player_y - 1
    new_bullet = Bullet(x=bullet_x, y=bullet_y)
    return replace(
        state,
        player_bullets=state.player_bullets + (new_bullet,),
        can_shoot=False,
    )
def update_player_bullets(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    new_bullets = tuple(
        replace(bullet, y=bullet.y - 1)
        for bullet in state.player_bullets
        if bullet.active and bullet.y - 1 >= 0
    )
    return replace(state, player_bullets=new_bullets)
def update_enemy_bullets(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    new_bullets = tuple(
        replace(bullet, y=bullet.y + 1)
        for bullet in state.enemy_bullets
        if bullet.active and bullet.y + 1 < state.config.height
    )
    return replace(state, enemy_bullets=new_bullets)
def update_enemies(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    active_enemies = [e for e in state.enemies if e.active]
    if not active_enemies:
        return state
    hit_edge = False
    for enemy in active_enemies:
        if state.direction == 1:
            if enemy.x + state.config.enemy_width >= state.config.width - 1:
                hit_edge = True
                break
        else:
            if enemy.x <= 1:
                hit_edge = True
                break
    if hit_edge:
        new_direction = state.direction * -1
        new_enemies = tuple(
            replace(e, y=e.y + 1) if e.active else e
            for e in state.enemies
        )
        for enemy in new_enemies:
            if (
                enemy.active
                and enemy.y + state.config.enemy_height >= state.config.player_y
            ):
                return replace(
                    state,
                    enemies=new_enemies,
                    direction=new_direction,
                    is_game_over=True,
                    high_score=max(state.high_score, state.score),
                )
        return replace(state, enemies=new_enemies, direction=new_direction)
    else:
        new_enemies = tuple(
            replace(e, x=e.x + state.direction) if e.active else e
            for e in state.enemies
        )
        return replace(state, enemies=new_enemies)
def enemy_shoot(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    active_enemies = [e for e in state.enemies if e.active]
    if not active_enemies:
        return state
    shooter = random.choice(active_enemies)
    bullet_x = shooter.x + state.config.enemy_width // 2
    bullet_y = shooter.y + state.config.enemy_height
    new_bullet = Bullet(x=bullet_x, y=bullet_y, is_enemy=True)
    return replace(
        state,
        enemy_bullets=state.enemy_bullets + (new_bullet,),
    )
def check_collisions(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    player_bullet_active = list(state.player_bullets)
    enemies_active = list(state.enemies)
    score_delta = 0
    for i, bullet in enumerate(player_bullet_active):
        if not bullet.active:
            continue
        for j, enemy in enumerate(enemies_active):
            if not enemy.active:
                continue
            if (
                enemy.x <= bullet.x < enemy.x + state.config.enemy_width
                and enemy.y <= bullet.y < enemy.y + state.config.enemy_height
            ):
                player_bullet_active[i] = replace(bullet, active=False)
                enemies_active[j] = replace(enemy, active=False)
                score_delta += 10 + state.level * 2
                break
    new_score = state.score + score_delta
    new_high_score = max(state.high_score, new_score)
    new_player_bullets = tuple(b for b in player_bullet_active if b.active)
    new_enemies = tuple(enemies_active)
    player_left = state.player.x
    player_right = state.player.x + state.config.player_width
    player_top = state.config.player_y
    player_bottom = state.config.player_y + state.config.player_height
    enemy_bullets_active = list(state.enemy_bullets)
    player_hit = False
    for i, bullet in enumerate(enemy_bullets_active):
        if not bullet.active:
            continue
        if (player_left <= bullet.x < player_right and
            player_top <= bullet.y < player_bottom):
            player_hit = True
            enemy_bullets_active[i] = replace(bullet, active=False)
            break
    new_enemy_bullets = tuple(b for b in enemy_bullets_active if b.active)
    if player_hit:
        return replace(
            state,
            enemies=new_enemies,
            player_bullets=new_player_bullets,
            enemy_bullets=new_enemy_bullets,
            score=new_score,
            high_score=new_high_score,
            is_game_over=True,
        )
    return replace(
        state,
        enemies=new_enemies,
        player_bullets=new_player_bullets,
        enemy_bullets=new_enemy_bullets,
        score=new_score,
        high_score=new_high_score,
    )
def check_win(state: GameState) -> GameState:
    if state.is_game_over or state.is_paused:
        return state
    active_enemies = [e for e in state.enemies if e.active]
    if not active_enemies:
        return replace(state, is_won=True)
    return state
def toggle_pause(state: GameState) -> GameState:
    if state.is_game_over or state.is_won:
        return state
    return replace(state, is_paused=not state.is_paused)
def reset_shoot_cooldown(state: GameState) -> GameState:
    return replace(state, can_shoot=True)
def get_enemy_move_interval(level: int) -> float:
    return max(0.16, 0.4 - (level - 1) * 0.03)
def get_enemy_shoot_interval(level: int) -> float:
    return max(0.5, 1.2 - (level - 1) * 0.1)
def get_score_per_enemy(level: int) -> int:
    return 10 + level * 2
