import random
from typing import Dict, Any


AI_LEVELS = ("Easy", "Medium", "Hard")
AI_SPEED_FACTORS = {
    "Easy": 0.45,
    "Medium": 0.75,
    "Hard": 1.35,
}


def _predict_ball_y_at_x(ball: Any, target_x: float, window_height: int) -> float:
    if ball.vel_x <= 0:
        return ball.y
    time_to_reach = (target_x - ball.x) / ball.vel_x
    if time_to_reach <= 0:
        return ball.y
    projected_y = ball.y + ball.vel_y * time_to_reach
    period = 2 * (window_height - ball.radius)
    if period <= 0:
        return max(ball.radius, min(window_height - ball.radius, projected_y))
    m = (projected_y - ball.radius) % period
    if m > (window_height - ball.radius):
        mirrored = period - m
    else:
        mirrored = m
    return mirrored + ball.radius


def move_ai_paddle(right_paddle: Any, ball: Any, difficulty: str, ai_state: Dict[str, float], paddle_speed: int, window_height: int) -> None:
    factor = AI_SPEED_FACTORS.get(difficulty, 0.9)
    max_step = max(1, int(paddle_speed * factor))

    if 'cooldown' not in ai_state:
        ai_state['cooldown'] = 0
    if 'last_seen_velx' not in ai_state:
        ai_state['last_seen_velx'] = 0.0

    if difficulty == "Easy":
        react_frames = 8
        jitter = 70
        track_only_when_approaching = True
    elif difficulty == "Medium":
        react_frames = 4
        jitter = 30
        track_only_when_approaching = True
    else:
        react_frames = 1
        jitter = 6
        track_only_when_approaching = False

    approaching = ball.vel_x > 0
    if approaching and ai_state.get('last_seen_velx', 0.0) <= 0:
        ai_state['cooldown'] = react_frames
    ai_state['last_seen_velx'] = ball.vel_x

    if ai_state['cooldown'] > 0:
        ai_state['cooldown'] -= 1
        return

    if difficulty == "Hard":
        target_x = right_paddle.x - right_paddle.width // 2
        target_y = _predict_ball_y_at_x(ball, target_x, window_height)
        target_y += random.randint(-jitter, jitter)
    elif difficulty == "Medium":
        if ball.vel_x > 0:
            t = (right_paddle.x - ball.x) / max(1e-5, ball.vel_x)
            target_y = ball.y + ball.vel_y * min(t, 0.6)
        else:
            target_y = ball.y
        target_y += random.randint(-jitter, jitter)
    else:
        target_y = ball.y + random.randint(-jitter, jitter)

    if track_only_when_approaching and not approaching:
        center_target = window_height / 2
        if right_paddle.center_y < center_target - 8:
            right_paddle.y = min(window_height - right_paddle.height, right_paddle.y + max_step // 2)
        elif right_paddle.center_y > center_target + 8:
            right_paddle.y = max(0, right_paddle.y - max_step // 2)
        return

    if right_paddle.center_y < target_y - 6:
        right_paddle.y = min(window_height - right_paddle.height, right_paddle.y + max_step)
    elif right_paddle.center_y > target_y + 6:
        right_paddle.y = max(0, right_paddle.y - max_step)


