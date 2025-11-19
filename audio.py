import pygame


def init_audio() -> tuple[pygame.mixer.Sound | None, pygame.mixer.Sound | None, pygame.mixer.Sound | None]:
    """Initialize mixer and load external WAV sound effects from assets/ folder.

    Returns (paddle_sound, score_sound, victory_sound); any may be None if loading fails.
    """
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

    try:
        snd_paddle = pygame.mixer.Sound("assets/pong_hit.wav")
    except Exception:
        snd_paddle = None
    try:
        snd_score = pygame.mixer.Sound("assets/pong_score.wav")
    except Exception:
        snd_score = None
    try:
        snd_victory = pygame.mixer.Sound("assets/pong_win.wav")
    except Exception:
        snd_victory = None

    return snd_paddle, snd_score, snd_victory


