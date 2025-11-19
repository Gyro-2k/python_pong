import pygame


class Paddle:
    """Represents a paddle controlled by a player."""

    def __init__(self, x: int, y: int, width: int, height: int, speed: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    def move_up(self, window_height: int) -> None:
        self.y = max(0, self.y - self.speed)

    def move_down(self, window_height: int) -> None:
        self.y = min(window_height - self.height, self.y + self.speed)


