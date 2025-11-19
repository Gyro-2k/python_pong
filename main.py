import math
import sys
import pygame
import random
import config as cfg
from paddle import Paddle
from ball import Ball
from ai import move_ai_paddle, AI_LEVELS
from ui import draw as ui_draw, draw_winner as ui_draw_winner, show_main_menu as ui_show_main_menu, screen_ai_difficulty as ui_screen_ai_difficulty, prompt_for_name as ui_prompt_for_name
from audio import init_audio
from physics import handle_collision as phys_handle_collision


# pull constants from config
WINDOW_WIDTH = cfg.WINDOW_WIDTH
WINDOW_HEIGHT = cfg.WINDOW_HEIGHT
FPS = cfg.FPS
BLACK = cfg.BLACK
WHITE = cfg.WHITE
PADDLE_WIDTH = cfg.PADDLE_WIDTH
PADDLE_HEIGHT = cfg.PADDLE_HEIGHT
PADDLE_SPEED = cfg.PADDLE_SPEED
BALL_RADIUS = cfg.BALL_RADIUS
BALL_SPEED = cfg.BALL_SPEED
MAX_BOUNCE_ANGLE_DEG = cfg.MAX_BOUNCE_ANGLE_DEG
HITS_PER_SPEEDUP = cfg.HITS_PER_SPEEDUP
SPEED_INCREMENT = cfg.SPEED_INCREMENT
MAX_BALL_SPEED = cfg.MAX_BALL_SPEED
WINNING_SCORE = cfg.WINNING_SCORE
WIN_MESSAGE_DURATION_MS = cfg.WIN_MESSAGE_DURATION_MS

# Player names (shown beside scores)
LEFT_PLAYER_NAME = "Left"
RIGHT_PLAYER_NAME = "Right"

# Audio globals (initialized in main) using provided asset WAVs
SND_PADDLE = None
SND_SCORE = None
SND_VICTORY = None

# AI configuration
AI_LEVELS = ("Easy", "Medium", "Hard")
AI_SPEED_FACTORS = {
    "Easy": 0.40,    # much slower tracking
    "Medium": 0.65,  # noticeably slower than player
    "Hard": 1.15,    # faster than player
}


def _init_audio() -> None:
    global SND_PADDLE, SND_SCORE, SND_VICTORY
    SND_PADDLE, SND_SCORE, SND_VICTORY = init_audio()


## Paddle and Ball classes are now in paddle.py and ball.py


def draw(window, left_paddle, right_paddle, ball, left_score, right_score, font):
    globals()['LEFT_PLAYER_NAME'] = LEFT_PLAYER_NAME
    globals()['RIGHT_PLAYER_NAME'] = RIGHT_PLAYER_NAME
    ui_draw(window, left_paddle, right_paddle, ball, left_score, right_score, font)


def handle_paddle_movement(keys: pygame.key.ScancodeWrapper, left_paddle: Paddle, right_paddle: Paddle, allow_right_human: bool) -> None:
    """Update paddles based on keyboard input for both players."""
    # Left paddle (W/S)
    if keys[pygame.K_w]:
        left_paddle.move_up(WINDOW_HEIGHT)
    if keys[pygame.K_s]:
        left_paddle.move_down(WINDOW_HEIGHT)

    # Right paddle (Up/Down)
    if allow_right_human:
        if keys[pygame.K_UP]:
            right_paddle.move_up(WINDOW_HEIGHT)
        if keys[pygame.K_DOWN]:
            right_paddle.move_down(WINDOW_HEIGHT)


def handle_collision(ball: Ball, left_paddle: Paddle, right_paddle: Paddle, current_speed: float) -> None:
    phys_handle_collision(ball, left_paddle, right_paddle, current_speed, WINDOW_HEIGHT, MAX_BOUNCE_ANGLE_DEG, SND_PADDLE)


def _draw_winner(window, message, large_font, score_font, selected, mouse_pos):
    return ui_draw_winner(window, message, large_font, score_font, selected, mouse_pos)


def _show_main_menu(window, title_font, ui_font):
    return ui_show_main_menu(window, title_font, ui_font)


def _screen_ai_difficulty(window, ui_font, initial="Medium"):
    return ui_screen_ai_difficulty(window, ui_font, AI_LEVELS, initial)


def _prompt_for_name(window, prompt_label, initial_value, font):
    return ui_prompt_for_name(window, prompt_label, initial_value, font)


def _prompt_opponent_type(window: pygame.Surface, font: pygame.font.Font) -> str:
    """Prompt for opponent type: 'human' or 'ai' with clearer UI and mouse support."""
    clock = pygame.time.Clock()
    selection = 'human'
    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        human_rect = None
        ai_rect = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_h):
                    selection = 'human'
                elif event.key in (pygame.K_RIGHT, pygame.K_a):
                    selection = 'ai'
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selection
                elif event.key == pygame.K_ESCAPE:
                    return 'human'
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if human_rect and human_rect.collidepoint(event.pos):
                    return 'human'
                if ai_rect and ai_rect.collidepoint(event.pos):
                    return 'ai'

        window.fill(BLACK)
        title = font.render("Choose Opponent", True, WHITE)
        subtitle = font.render("Use ←/→ or click a card", True, WHITE)
        opt_h = font.render("Human", True, BLACK)
        opt_a = font.render("AI", True, BLACK)
        hint = font.render("Enter/Click to confirm", True, WHITE)

        # Layout cards
        card_w = max(opt_h.get_width(), opt_a.get_width()) + 120
        card_h = opt_h.get_height() + 40
        spacing = 40
        total_w = card_w * 2 + spacing
        top_y = WINDOW_HEIGHT // 2 - card_h // 2
        left_x = WINDOW_WIDTH // 2 - total_w // 2
        human_rect = pygame.Rect(left_x, top_y, card_w, card_h)
        ai_rect = pygame.Rect(left_x + card_w + spacing, top_y, card_w, card_h)

        # Hover and selection visuals
        def draw_card(rect: pygame.Rect, label: pygame.Surface, is_selected: bool, is_hovered: bool) -> None:
            bg = (200, 200, 200) if is_selected else ((120, 120, 120) if is_hovered else (60, 60, 60))
            border = WHITE
            pygame.draw.rect(window, bg, rect, border_radius=8)
            pygame.draw.rect(window, border, rect, 2, border_radius=8)
            window.blit(label, (rect.x + (rect.w - label.get_width()) // 2, rect.y + (rect.h - label.get_height()) // 2))

        is_h_hover = human_rect.collidepoint(mouse_pos)
        is_a_hover = ai_rect.collidepoint(mouse_pos)

        # Title and instructions
        window.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, top_y - title.get_height() - 24))
        window.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, top_y - subtitle.get_height()))

        draw_card(human_rect, opt_h, selection == 'human', is_h_hover)
        draw_card(ai_rect, opt_a, selection == 'ai', is_a_hover)

        window.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, top_y + card_h + 20))
        pygame.display.flip()


def _prompt_ai_difficulty(window: pygame.Surface, font: pygame.font.Font, initial: str = "Medium") -> str:
    """Prompt for AI difficulty; returns one of AI_LEVELS."""
    clock = pygame.time.Clock()
    idx = max(0, list(AI_LEVELS).index(initial) if initial in AI_LEVELS else 1)
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    idx = 0
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    idx = 1
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    idx = 2
                elif event.key in (pygame.K_LEFT,):
                    idx = (idx - 1) % 3
                elif event.key in (pygame.K_RIGHT,):
                    idx = (idx + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return AI_LEVELS[idx]
                elif event.key == pygame.K_ESCAPE:
                    return initial

        window.fill(BLACK)
        title = font.render("AI Difficulty", True, WHITE)
        subtitle = font.render("1/2/3 or ←/→ to change, Enter to confirm", True, WHITE)
        opts = [font.render(f"{i+1}. {lvl}", True, WHITE) for i, lvl in enumerate(AI_LEVELS)]
        total_h = title.get_height() + subtitle.get_height() + sum(o.get_height() for o in opts) + 36
        y = WINDOW_HEIGHT // 2 - total_h // 2
        window.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, y)); y += title.get_height() + 6
        window.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, y)); y += subtitle.get_height() + 10
        for i, o in enumerate(opts):
            color = (200, 200, 200) if i == idx else (80, 80, 80)
            pygame.draw.rect(window, color, pygame.Rect(WINDOW_WIDTH // 2 - o.get_width() // 2 - 12, y - 6, o.get_width() + 24, o.get_height() + 12))
            window.blit(o, (WINDOW_WIDTH // 2 - o.get_width() // 2, y)); y += o.get_height() + 6
        pygame.display.flip()


def _predict_ball_y_at_x(ball: "Ball", target_x: float) -> float:
    """Predict y position when ball reaches target_x, reflecting on top/bottom.

    If ball won't reach target_x (moving away), return current y.
    """
    if ball.vel_x <= 0:
        return ball.y
    time_to_reach = (target_x - ball.x) / ball.vel_x
    if time_to_reach <= 0:
        return ball.y
    projected_y = ball.y + ball.vel_y * time_to_reach
    # Reflect off bounds using mirroring in range [0, WINDOW_HEIGHT]
    period = 2 * (WINDOW_HEIGHT - ball.radius)
    if period <= 0:
        return max(ball.radius, min(WINDOW_HEIGHT - ball.radius, projected_y))
    m = (projected_y - ball.radius) % period
    if m > (WINDOW_HEIGHT - ball.radius):
        mirrored = period - m
    else:
        mirrored = m
    return mirrored + ball.radius


def _move_ai_paddle(right_paddle: Paddle, ball: Ball, difficulty: str, ai_state: dict) -> None:
    """Move the right paddle as an AI opponent based on difficulty.

    ai_state carries ephemeral state like reaction cooldown.
    """
    factor = AI_SPEED_FACTORS.get(difficulty, 0.9)
    max_step = max(1, int(PADDLE_SPEED * factor))

    # Reaction delay per difficulty (frames)
    if 'cooldown' not in ai_state:
        ai_state['cooldown'] = 0
    if 'last_seen_velx' not in ai_state:
        ai_state['last_seen_velx'] = 0.0

    # Set reaction window sizes
    if difficulty == "Easy":
        react_frames = 8
        jitter = 70
        track_only_when_approaching = True
    elif difficulty == "Medium":
        react_frames = 4
        jitter = 30
        track_only_when_approaching = True
    else:  # Hard
        react_frames = 1
        jitter = 6
        track_only_when_approaching = False

    # Update cooldown when the ball changes direction toward AI
    approaching = ball.vel_x > 0
    if approaching and ai_state.get('last_seen_velx', 0.0) <= 0:
        ai_state['cooldown'] = react_frames
    ai_state['last_seen_velx'] = ball.vel_x

    if ai_state['cooldown'] > 0:
        ai_state['cooldown'] -= 1
        return

    # Determine target_y
    if difficulty == "Hard":
        # Predict impact point at paddle front
        target_x = right_paddle.x - right_paddle.width // 2
        target_y = _predict_ball_y_at_x(ball, target_x)
        target_y += random.randint(-jitter, jitter)
    elif difficulty == "Medium":
        # Slight predictive bias but simpler
        if ball.vel_x > 0:
            t = (right_paddle.x - ball.x) / max(1e-5, ball.vel_x)
            target_y = ball.y + ball.vel_y * min(t, 0.6)
        else:
            target_y = ball.y
        target_y += random.randint(-jitter, jitter)
    else:  # Easy
        target_y = ball.y + random.randint(-jitter, jitter)

    if track_only_when_approaching and not approaching:
        # Drift back gently to center when ball moving away
        center_target = WINDOW_HEIGHT / 2
        if right_paddle.center_y < center_target - 8:
            right_paddle.y = min(WINDOW_HEIGHT - right_paddle.height, right_paddle.y + max_step // 2)
        elif right_paddle.center_y > center_target + 8:
            right_paddle.y = max(0, right_paddle.y - max_step // 2)
        return

    # Move towards target with clamped step
    if right_paddle.center_y < target_y - 6:
        right_paddle.y = min(WINDOW_HEIGHT - right_paddle.height, right_paddle.y + max_step)
    elif right_paddle.center_y > target_y + 6:
        right_paddle.y = max(0, right_paddle.y - max_step)
def main() -> None:
    """Main entry point: initialize, run the game loop, and manage rounds."""
    pygame.init()
    pygame.display.set_caption("Pong - Pygame")

    # Resize window to fit title image plus space for buttons
    title_img_w = None
    title_img_h = None
    try:
        tmp_surf = pygame.image.load("assets/retro_pong.png")
        title_img_w, title_img_h = tmp_surf.get_size()
    except Exception:
        try:
            tmp_surf = pygame.image.load("assets/retro_pong.jpg")
            title_img_w, title_img_h = tmp_surf.get_size()
        except Exception:
            tmp_surf = None
    if title_img_w and title_img_h:
        extra_button_area = 180
        globals()['WINDOW_WIDTH'] = title_img_w
        globals()['WINDOW_HEIGHT'] = title_img_h + extra_button_area

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    score_font = pygame.font.SysFont("consolas", 40, bold=True)
    winner_font = pygame.font.SysFont("consolas", 72, bold=True)
    title_font = pygame.font.SysFont("consolas", 72, bold=True)

    # Audio init
    _init_audio()

    # Entities
    left_paddle = Paddle(40, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED)
    right_paddle = Paddle(WINDOW_WIDTH - 40 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED)

    # Ball starts centered; velocity set when launched
    ball = Ball(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, BALL_RADIUS, 0, 0)

    left_score = 0
    right_score = 0
    ball_held_by = None  # 'left' or 'right' during possession
    # Renaming removed during gameplay per request
    game_over = False
    winner_message = ""
    restart_button_rect = None
    menu_button_rect = None
    winner_selected_idx = 0  # 0 restart, 1 menu
    opponent_is_ai = False
    ai_difficulty = "Medium"
    changing_difficulty = False  # overlay state for changing AI difficulty in-game
    ai_state = {"cooldown": 0, "last_seen_velx": 0.0}
    show_menu = True
    ai_launch_cooldown_ms = 0
    current_ball_speed = BALL_SPEED
    rally_hits = 0

    # Menu flow
    while show_menu:
        mode = ui_show_main_menu(window, title_font, score_font)
        if mode == '1p':
            opponent_is_ai = True
            globals()['LEFT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Your Name:", LEFT_PLAYER_NAME, score_font)
            globals()['RIGHT_PLAYER_NAME'] = "AI"
            ai_difficulty = ui_screen_ai_difficulty(window, score_font, AI_LEVELS, initial=ai_difficulty)
            show_menu = False
        else:
            opponent_is_ai = False
            globals()['LEFT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Left Player Name:", LEFT_PLAYER_NAME, score_font)
            globals()['RIGHT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Right Player Name:", RIGHT_PLAYER_NAME, score_font)
            show_menu = False

    # Random initial possession; Space launches for human, AI auto after delay
    ball_held_by = random.choice(['left', 'right'])
    if opponent_is_ai and ball_held_by == 'right':
        ai_launch_cooldown_ms = 700
    current_ball_speed = BALL_SPEED
    rally_hits = 0

    running = True
    while running:
        dt_ms = clock.tick(FPS)

        keys = pygame.key.get_pressed()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_over:
                # Restart or Back to Menu via button
                if restart_button_rect and restart_button_rect.collidepoint(event.pos):
                    left_score = 0
                    right_score = 0
                    left_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    right_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    ball.reset_to_center(WINDOW_WIDTH, WINDOW_HEIGHT, reverse_horizontal=True)
                    ball_held_by = random.choice(['left', 'right'])
                    if opponent_is_ai and ball_held_by == 'right':
                        ai_launch_cooldown_ms = 700
                    else:
                        ai_launch_cooldown_ms = 0
                    game_over = False
                    current_ball_speed = BALL_SPEED
                    rally_hits = 0
                elif menu_button_rect and menu_button_rect.collidepoint(event.pos):
                    # Back to menu
                    left_score = 0
                    right_score = 0
                    game_over = False
                    show_menu = True
                    # Re-enter menu and configuration
                    while show_menu:
                        mode = ui_show_main_menu(window, title_font, score_font)
                        if mode == '1p':
                            opponent_is_ai = True
                            globals()['LEFT_PLAYER_NAME'] = LEFT_PLAYER_NAME
                            globals()['RIGHT_PLAYER_NAME'] = "AI"
                            ai_difficulty = ui_screen_ai_difficulty(window, score_font, AI_LEVELS, initial=ai_difficulty)
                            show_menu = False
                        else:
                            opponent_is_ai = False
                            globals()['LEFT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Left Player Name:", LEFT_PLAYER_NAME, score_font)
                            globals()['RIGHT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Right Player Name:", RIGHT_PLAYER_NAME, score_font)
                            show_menu = False
                    # Reset entities for new match
                    left_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    right_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    ball.reset_to_center(WINDOW_WIDTH, WINDOW_HEIGHT, reverse_horizontal=True)
                    ball_held_by = random.choice(['left', 'right'])
                    if opponent_is_ai and ball_held_by == 'right':
                        ai_launch_cooldown_ms = 700
                    else:
                        ai_launch_cooldown_ms = 0
                    current_ball_speed = BALL_SPEED
                    rally_hits = 0
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    # Winner screen navigation with arrows, Enter confirms; Space disabled
                    if event.key == pygame.K_LEFT:
                        winner_selected_idx = 0
                    elif event.key == pygame.K_RIGHT:
                        winner_selected_idx = 1
                    elif event.key == pygame.K_RETURN:
                        if winner_selected_idx == 0:
                            left_score = 0
                            right_score = 0
                            left_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                            right_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                            ball.reset_to_center(WINDOW_WIDTH, WINDOW_HEIGHT, reverse_horizontal=True)
                            ball_held_by = random.choice(['left', 'right'])
                            if opponent_is_ai and ball_held_by == 'right':
                                ai_launch_cooldown_ms = 700
                            else:
                                ai_launch_cooldown_ms = 0
                            game_over = False
                            current_ball_speed = BALL_SPEED
                            rally_hits = 0
                        else:
                            # Back to menu
                            left_score = 0
                            right_score = 0
                            game_over = False
                            show_menu = True
                            while show_menu:
                                mode = ui_show_main_menu(window, title_font, score_font)
                                if mode == '1p':
                                    opponent_is_ai = True
                                    globals()['LEFT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Your Name:", LEFT_PLAYER_NAME, score_font)
                                    globals()['RIGHT_PLAYER_NAME'] = "AI"
                                    ai_difficulty = ui_screen_ai_difficulty(window, score_font, AI_LEVELS, initial=ai_difficulty)
                                    show_menu = False
                                else:
                                    opponent_is_ai = False
                                    globals()['LEFT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Left Player Name:", LEFT_PLAYER_NAME, score_font)
                                    globals()['RIGHT_PLAYER_NAME'] = ui_prompt_for_name(window, "Enter Right Player Name:", RIGHT_PLAYER_NAME, score_font)
                                    show_menu = False
                            left_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                            right_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
                            ball.reset_to_center(WINDOW_WIDTH, WINDOW_HEIGHT, reverse_horizontal=True)
                            ball_held_by = random.choice(['left', 'right'])
                            if opponent_is_ai and ball_held_by == 'right':
                                ai_launch_cooldown_ms = 700
                            else:
                                ai_launch_cooldown_ms = 0
                            current_ball_speed = BALL_SPEED
                            rally_hits = 0
                    # Ignore other keys during game over
                    continue
                # Open AI difficulty change
                if not game_over and not changing_difficulty and event.key == pygame.K_2 and opponent_is_ai:
                    changing_difficulty = True

                # Launch from possession
                if event.key == pygame.K_SPACE and ball_held_by is not None and not game_over:
                    if ball_held_by == 'left':
                        ball.vel_x = current_ball_speed
                        ball.vel_y = 0
                    elif ball_held_by == 'right':
                        # Only allow manual launch if human on right (2P)
                        if not opponent_is_ai:
                            ball.vel_x = -current_ball_speed
                            ball.vel_y = 0
                        else:
                            # ignore; AI will auto-launch
                            pass
                    ball_held_by = None
                    if SND_PADDLE:
                        SND_PADDLE.play()

                # No rename during gameplay per request
                # Handle AI difficulty overlay input
                if changing_difficulty:
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        ai_difficulty = "Easy"; changing_difficulty = False
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        ai_difficulty = "Medium"; changing_difficulty = False
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        ai_difficulty = "Hard"; changing_difficulty = False
                    elif event.key in (pygame.K_LEFT,):
                        idx = list(AI_LEVELS).index(ai_difficulty)
                        ai_difficulty = AI_LEVELS[(idx - 1) % 3]
                    elif event.key in (pygame.K_RIGHT,):
                        idx = list(AI_LEVELS).index(ai_difficulty)
                        ai_difficulty = AI_LEVELS[(idx + 1) % 3]
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        changing_difficulty = False
                    # reset AI reaction so difficulty takes effect instantly
                    ai_state["cooldown"] = 0

        if not running:
            break

        # Game over overlay
        if game_over:
            ui_draw(window, left_paddle, right_paddle, ball, left_score, right_score, LEFT_PLAYER_NAME, RIGHT_PLAYER_NAME, score_font)
            # Update selection from hover
            mp = pygame.mouse.get_pos()
            restart_button_rect, menu_button_rect = ui_draw_winner(window, winner_message, winner_font, score_font, winner_selected_idx, mp)
            if restart_button_rect.collidepoint(mp):
                winner_selected_idx = 0
            elif menu_button_rect.collidepoint(mp):
                winner_selected_idx = 1
            pygame.display.flip()
            continue

        # Rename overlay removed

        # AI Difficulty overlay (pauses gameplay)
        if changing_difficulty:
            ui_draw(window, left_paddle, right_paddle, ball, left_score, right_score, LEFT_PLAYER_NAME, RIGHT_PLAYER_NAME, score_font)
            line1 = score_font.render("AI Difficulty:", True, WHITE)
            line2 = score_font.render(f"< {ai_difficulty} >", True, WHITE)
            line3 = score_font.render("1/2/3 or ←/→, Enter/Esc to close", True, WHITE)
            total_h = line1.get_height() + line2.get_height() + line3.get_height() + 24
            bg_rect = pygame.Rect(0, 0, max(line1.get_width(), line2.get_width(), line3.get_width()) + 40, total_h)
            bg_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.draw.rect(window, (20, 20, 20), bg_rect)
            pygame.draw.rect(window, WHITE, bg_rect, 2)
            y = bg_rect.y + 8
            window.blit(line1, (bg_rect.x + (bg_rect.w - line1.get_width()) // 2, y)); y += line1.get_height() + 4
            window.blit(line2, (bg_rect.x + (bg_rect.w - line2.get_width()) // 2, y)); y += line2.get_height() + 4
            window.blit(line3, (bg_rect.x + (bg_rect.w - line3.get_width()) // 2, y))
            pygame.display.flip()
            continue

        # Gameplay update
        handle_paddle_movement(keys, left_paddle, right_paddle, allow_right_human=not opponent_is_ai)
        if opponent_is_ai and ball_held_by is None:
            _move_ai_paddle(right_paddle, ball, ai_difficulty, ai_state)

        # Ball update (possession-aware)
        if ball_held_by is None:
            ball.move()
            hit = phys_handle_collision(ball, left_paddle, right_paddle, current_ball_speed, WINDOW_HEIGHT, MAX_BOUNCE_ANGLE_DEG, SND_PADDLE)
            if hit:
                rally_hits += 1
                if rally_hits % HITS_PER_SPEEDUP == 0:
                    current_ball_speed = min(MAX_BALL_SPEED, current_ball_speed + SPEED_INCREMENT)
                    mag = math.hypot(ball.vel_x, ball.vel_y)
                    if mag > 0:
                        scale = current_ball_speed / mag
                        ball.vel_x *= scale
                        ball.vel_y *= scale
        else:
            # Attach ball to holder paddle
            if ball_held_by == 'left':
                ball.x = left_paddle.x + left_paddle.width + ball.radius
                ball.y = left_paddle.center_y
            elif ball_held_by == 'right':
                ball.x = right_paddle.x - ball.radius
                ball.y = right_paddle.center_y
                # AI auto-launch after small delay
                if opponent_is_ai:
                    ai_launch_cooldown_ms = max(0, ai_launch_cooldown_ms - dt_ms)
                    if ai_launch_cooldown_ms == 0:
                        ball.vel_x = -current_ball_speed
                        ball.vel_y = 0
                        ball_held_by = None
                        if SND_PADDLE:
                            SND_PADDLE.play()

        # Scoring
        pending_score_sound = False
        if ball.x + ball.radius < 0:
            right_score += 1
            # Possession to left player
            ball.vel_x = 0
            ball.vel_y = 0
            ball_held_by = 'left'
            current_ball_speed = BALL_SPEED
            rally_hits = 0
            pending_score_sound = True
        elif ball.x - ball.radius > WINDOW_WIDTH:
            left_score += 1
            # Possession to right player
            ball.vel_x = 0
            ball.vel_y = 0
            ball_held_by = 'right'
            current_ball_speed = BALL_SPEED
            rally_hits = 0
            if opponent_is_ai:
                ai_launch_cooldown_ms = 700
            else:
                ai_launch_cooldown_ms = 0
            pending_score_sound = True

        # Check for winner
        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            if left_score > right_score:
                winner_message = f"{LEFT_PLAYER_NAME} wins!"
            else:
                winner_message = f"{RIGHT_PLAYER_NAME} wins!"
            game_over = True
            ball_held_by = None
            if SND_VICTORY:
                SND_VICTORY.play()
        elif pending_score_sound and SND_SCORE:
            # Only play if the round continues (not on the winning point)
            SND_SCORE.play()

        ui_draw(window, left_paddle, right_paddle, ball, left_score, right_score, LEFT_PLAYER_NAME, RIGHT_PLAYER_NAME, score_font)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()


