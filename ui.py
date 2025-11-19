import sys
import pygame
import config as cfg


def draw(window: pygame.Surface, left_paddle, right_paddle, ball, left_score: int, right_score: int, left_name: str, right_name: str, font: pygame.font.Font) -> None:
    window.fill(cfg.BLACK)

    width, height = window.get_size()
    dash_height = 15
    gap = 12
    x = width // 2
    for y in range(0, height, dash_height + gap):
        pygame.draw.rect(window, cfg.WHITE, pygame.Rect(x - 2, y, 4, dash_height))

    pygame.draw.rect(window, cfg.WHITE, left_paddle.rect)
    pygame.draw.rect(window, cfg.WHITE, right_paddle.rect)

    pygame.draw.circle(window, cfg.WHITE, (int(ball.x), int(ball.y)), ball.radius)

    left_label = f"{left_name} {left_score}"
    right_label = f"{right_name} {right_score}"

    left_text = font.render(left_label, True, cfg.WHITE)
    right_text = font.render(right_label, True, cfg.WHITE)

    window.blit(left_text, (width // 4 - left_text.get_width() // 2, 12))
    window.blit(right_text, (width * 3 // 4 - right_text.get_width() // 2, 12))


def draw_winner(window: pygame.Surface, message: str, large_font: pygame.font.Font, score_font: pygame.font.Font, selected: int, mouse_pos: tuple[int, int]):
    width, height = window.get_size()
    text = large_font.render(message, True, cfg.WHITE)
    text_pos = (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 - 40)
    window.blit(text, text_pos)

    padding_x, padding_y = 22, 12
    restart_label = score_font.render("Restart", True, cfg.BLACK)
    menu_label = score_font.render("Back to Menu", True, cfg.BLACK)
    restart_w = restart_label.get_width() + padding_x * 2
    restart_h = restart_label.get_height() + padding_y * 2
    menu_w = menu_label.get_width() + padding_x * 2
    menu_h = menu_label.get_height() + padding_y * 2
    spacing = 24
    total_w = restart_w + spacing + menu_w
    base_y = height // 2 + 40
    start_x = width // 2 - total_w // 2
    restart_rect = pygame.Rect(start_x, base_y, restart_w, restart_h)
    menu_rect = pygame.Rect(start_x + restart_w + spacing, base_y, menu_w, menu_h)

    is_restart_hover = restart_rect.collidepoint(mouse_pos)
    is_menu_hover = menu_rect.collidepoint(mouse_pos)

    def btn_bg(active: bool, hover: bool):
        if active:
            return (200, 200, 200)
        return (120, 120, 120) if hover else (60, 60, 60)

    pygame.draw.rect(window, btn_bg(selected == 0, is_restart_hover), restart_rect)
    pygame.draw.rect(window, btn_bg(selected == 1, is_menu_hover), menu_rect)
    window.blit(restart_label, (restart_rect.x + padding_x, restart_rect.y + padding_y))
    window.blit(menu_label, (menu_rect.x + padding_x, menu_rect.y + padding_y))
    pygame.draw.rect(window, cfg.WHITE, restart_rect, 2)
    pygame.draw.rect(window, cfg.WHITE, menu_rect, 2)
    return restart_rect, menu_rect


def show_main_menu(window: pygame.Surface, title_font: pygame.font.Font, ui_font: pygame.font.Font) -> str:
    clock = pygame.time.Clock()
    selection = '1p'
    title_image = None
    try:
        title_image = pygame.image.load(cfg.TITLE_IMAGE_PNG).convert_alpha()
    except Exception:
        try:
            title_image = pygame.image.load(cfg.TITLE_IMAGE_JPG).convert()
        except Exception:
            title_image = None
    while True:
        clock.tick(cfg.FPS)
        mouse_pos = pygame.mouse.get_pos()
        width, height = window.get_size()
        btn1_label = ui_font.render("1 Player", True, cfg.BLACK)
        btn2_label = ui_font.render("2 Players", True, cfg.BLACK)
        padding_x, padding_y = 26, 14
        b1w, b1h = btn1_label.get_width() + padding_x * 2, btn1_label.get_height() + padding_y * 2
        b2w, b2h = btn2_label.get_width() + padding_x * 2, btn2_label.get_height() + padding_y * 2
        spacing = 36
        total_w = b1w + spacing + b2w
        img_h = title_image.get_height() if title_image else 0
        base_y = img_h + 24
        start_x = width // 2 - total_w // 2
        one_rect = pygame.Rect(start_x, base_y, b1w, b1h)
        two_rect = pygame.Rect(start_x + b1w + spacing, base_y, b2w, b2h)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_1):
                    selection = '1p'
                elif event.key in (pygame.K_RIGHT, pygame.K_2):
                    selection = '2p'
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selection
            elif event.type == pygame.MOUSEMOTION:
                if one_rect.collidepoint(event.pos):
                    selection = '1p'
                elif two_rect.collidepoint(event.pos):
                    selection = '2p'
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if one_rect.collidepoint(event.pos):
                    return '1p'
                if two_rect.collidepoint(event.pos):
                    return '2p'

        window.fill(cfg.BLACK)
        if title_image:
            img_w, img_h = title_image.get_size()
            window.blit(title_image, (width // 2 - img_w // 2, 0))
        else:
            title = title_font.render("PONG by gyrø", True, cfg.WHITE)
            window.blit(title, (width // 2 - title.get_width() // 2, 40))

        def draw_btn(rect: pygame.Rect, label: pygame.Surface, active: bool) -> None:
            bg = (200, 200, 200) if active else (60, 60, 60)
            pygame.draw.rect(window, bg, rect, border_radius=8)
            pygame.draw.rect(window, cfg.WHITE, rect, 2, border_radius=8)
            window.blit(label, (rect.x + (rect.w - label.get_width()) // 2, rect.y + (rect.h - label.get_height()) // 2))

        draw_btn(one_rect, btn1_label, selection == '1p' or one_rect.collidepoint(mouse_pos))
        draw_btn(two_rect, btn2_label, selection == '2p' or two_rect.collidepoint(mouse_pos))
        pygame.display.flip()


def screen_ai_difficulty(window: pygame.Surface, ui_font: pygame.font.Font, levels, initial: str = "Medium") -> str:
    clock = pygame.time.Clock()
    idx = max(0, list(levels).index(initial) if initial in levels else 1)
    while True:
        clock.tick(cfg.FPS)
        width, height = window.get_size()
        tab_w = 220
        tab_h = 60
        spacing = 24
        total_w = tab_w * 3 + spacing * 2
        start_x = width // 2 - total_w // 2
        y = height // 2 - 20
        tab_rects = [pygame.Rect(start_x + i * (tab_w + spacing), y, tab_w, tab_h) for i in range(3)]
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1): idx = 0
                elif event.key in (pygame.K_2, pygame.K_KP2): idx = 1
                elif event.key in (pygame.K_3, pygame.K_KP3): idx = 2
                elif event.key == pygame.K_LEFT: idx = (idx - 1) % 3
                elif event.key == pygame.K_RIGHT: idx = (idx + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return levels[idx]
            elif event.type == pygame.MOUSEMOTION:
                for i, r in enumerate(tab_rects):
                    if r.collidepoint(event.pos):
                        idx = i
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(tab_rects):
                    if r.collidepoint(event.pos):
                        return levels[i]

        window.fill(cfg.BLACK)
        title = ui_font.render("Select AI Difficulty", True, cfg.WHITE)
        window.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 120))
        for i, lvl in enumerate(levels):
            rect = tab_rects[i]
            active = (i == idx) or rect.collidepoint(mouse_pos)
            bg = (200, 200, 200) if active else (60, 60, 60)
            pygame.draw.rect(window, bg, rect, border_radius=8)
            pygame.draw.rect(window, cfg.WHITE, rect, 2, border_radius=8)
            label = ui_font.render(lvl, True, cfg.BLACK)
            window.blit(label, (rect.x + (rect.w - label.get_width()) // 2, rect.y + (rect.h - label.get_height()) // 2))
        # Removed on-screen hint as requested
        pygame.display.flip()


def prompt_for_name(window: pygame.Surface, prompt_label: str, initial_value: str, font: pygame.font.Font) -> str:
    buffer = initial_value
    clock = pygame.time.Clock()
    while True:
        clock.tick(cfg.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return buffer.strip() or initial_value
                elif event.key == pygame.K_ESCAPE:
                    return initial_value
                elif event.key == pygame.K_BACKSPACE:
                    buffer = buffer[:-1]
                else:
                    if event.unicode and event.unicode.isprintable() and len(buffer) < 16:
                        buffer += event.unicode
        window.fill(cfg.BLACK)
        title = font.render(prompt_label, True, cfg.WHITE)
        name = font.render(buffer, True, cfg.WHITE)
        box_w = max(title.get_width(), name.get_width()) + 40
        box_h = title.get_height() + name.get_height() + 30
        box = pygame.Rect(0, 0, box_w, box_h)
        width, height = window.get_size()
        box.center = (width // 2, height // 2)
        pygame.draw.rect(window, (20, 20, 20), box)
        pygame.draw.rect(window, cfg.WHITE, box, 2)
        window.blit(title, (box.x + (box_w - title.get_width()) // 2, box.y + 8))
        window.blit(name, (box.x + (box_w - name.get_width()) // 2, box.y + 12 + title.get_height()))
        pygame.display.flip()


