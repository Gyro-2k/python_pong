import math


class Ball:
    """Represents the game ball with movement and collision state."""

    def __init__(self, x: float, y: float, radius: int, vel_x: float, vel_y: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = vel_x
        self.vel_y = vel_y

    def move(self) -> None:
        self.x += self.vel_x
        self.y += self.vel_y

    def reset_to_center(self, window_width: int, window_height: int, reverse_horizontal: bool = True) -> None:
        self.x = window_width / 2
        self.y = window_height / 2
        if reverse_horizontal:
            self.vel_x = -self.vel_x
        self._normalize_speed_magnitude()

    def normalize_to_speed(self, speed: float) -> None:
        mag = math.hypot(self.vel_x, self.vel_y)
        if mag == 0:
            self.vel_x = speed
            self.vel_y = 0
            return
        scale = speed / mag
        self.vel_x *= scale
        self.vel_y *= scale

    def _normalize_speed_magnitude(self) -> None:
        mag = math.hypot(self.vel_x, self.vel_y)
        if mag == 0:
            return
        # Keep direction, magnitude unchanged (caller will set)
        pass


