import math
import pygame


def ball_intersects_paddle(ball, paddle) -> bool:
    return paddle.rect.colliderect(
        pygame.Rect(int(ball.x - ball.radius), int(ball.y - ball.radius), ball.radius * 2, ball.radius * 2)
    )


def handle_collision(ball, left_paddle, right_paddle, current_speed: float, window_height: int, max_bounce_angle_deg: float, snd_paddle) -> bool:
    """Handle ball collisions with top/bottom bounds and paddles with angle deflection."""
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.vel_y = abs(ball.vel_y)
    elif ball.y + ball.radius >= window_height:
        ball.y = window_height - ball.radius
        ball.vel_y = -abs(ball.vel_y)

    max_angle_rad = math.radians(max_bounce_angle_deg)

    if ball_intersects_paddle(ball, left_paddle) and ball.vel_x < 0:
        relative_intersect_y = (ball.y - left_paddle.center_y)
        normalized = max(-1.0, min(1.0, relative_intersect_y / (left_paddle.height / 2)))
        bounce_angle = normalized * max_angle_rad

        speed = current_speed
        ball.vel_x = speed * math.cos(bounce_angle)
        ball.vel_y = speed * math.sin(bounce_angle)

        ball.x = left_paddle.x + left_paddle.width + ball.radius
        if snd_paddle:
            snd_paddle.play()
        return True

    elif ball_intersects_paddle(ball, right_paddle) and ball.vel_x > 0:
        relative_intersect_y = (ball.y - right_paddle.center_y)
        normalized = max(-1.0, min(1.0, relative_intersect_y / (right_paddle.height / 2)))
        bounce_angle = normalized * max_angle_rad

        speed = current_speed
        ball.vel_x = -speed * math.cos(bounce_angle)
        ball.vel_y = speed * math.sin(bounce_angle)

        ball.x = right_paddle.x - ball.radius
        if snd_paddle:
            snd_paddle.play()
        return True

    return False

