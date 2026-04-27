# TSIS3/ui.py
import pygame
from constants import (
    WIDTH, HEIGHT,
    WHITE, BLACK, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, ORANGE,
    CAR_COLOR_MAP, DIFFICULTY_SPEED_MULT,
)


def _rect_button(surface, text, rect, font, bg=(80, 80, 80), fg=WHITE, hover=False):
    colour = (120, 120, 120) if hover else bg
    pygame.draw.rect(surface, colour, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    lbl = font.render(text, True, fg)
    surface.blit(lbl, lbl.get_rect(center=rect.center))
    return rect


def _detect_hover(rect, mouse_pos):
    return rect.collidepoint(mouse_pos)


def draw_menu(surface: pygame.Surface, mouse_pos: tuple) -> dict:
    """Draw main menu. Returns dict of button name -> Rect."""
    surface.fill((20, 20, 40))
    font_title = pygame.font.SysFont("Arial", 52, bold=True)
    font_btn   = pygame.font.SysFont("Arial", 28, bold=True)

    title = font_title.render("RACER", True, YELLOW)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, 130)))

    buttons = {}
    labels = [("play", "Play"), ("leaderboard", "Leaderboard"),
              ("settings", "Settings"), ("quit", "Quit")]
    for i, (key, text) in enumerate(labels):
        rect = pygame.Rect(WIDTH // 2 - 110, 240 + i * 70, 220, 50)
        hover = _detect_hover(rect, mouse_pos)
        bg = GREEN if key == "play" else (80, 80, 80)
        _rect_button(surface, text, rect, font_btn, bg=bg, hover=hover)
        buttons[key] = rect

    return buttons


def draw_username(surface: pygame.Surface, current_text: str, error: bool = False):
    surface.fill((20, 20, 40))
    font_title = pygame.font.SysFont("Arial", 36, bold=True)
    font_label = pygame.font.SysFont("Arial", 22)
    font_input = pygame.font.SysFont("Arial", 28)

    title = font_title.render("Enter Your Name", True, WHITE)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, 160)))

    box = pygame.Rect(WIDTH // 2 - 130, 230, 260, 48)
    pygame.draw.rect(surface, WHITE, box, border_radius=6)
    text_surf = font_input.render(current_text + "|", True, BLACK)
    surface.blit(text_surf, (box.x + 8, box.y + 10))

    if error:
        err = font_label.render("Name cannot be empty!", True, RED)
        surface.blit(err, err.get_rect(center=(WIDTH // 2, 295)))

    hint = font_label.render("Press ENTER to start", True, GRAY)
    surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 330)))


def draw_gameover(surface: pygame.Surface, result: dict, mouse_pos: tuple) -> dict:
    surface.fill((30, 0, 0))
    font_big   = pygame.font.SysFont("Arial", 48, bold=True)
    font_stats = pygame.font.SysFont("Arial", 24)
    font_btn   = pygame.font.SysFont("Arial", 26, bold=True)

    go = font_big.render("GAME OVER", True, RED)
    surface.blit(go, go.get_rect(center=(WIDTH // 2, 100)))

    stats = [
        ("Score",    str(result.get("score", 0))),
        ("Distance", f"{result.get('distance', 0)} m"),
        ("Coins",    str(result.get("coins", 0))),
        ("Bonus",    str(result.get("bonus", 0))),
    ]
    for i, (label, val) in enumerate(stats):
        lbl = font_stats.render(f"{label}:  {val}", True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=(WIDTH // 2, 200 + i * 36)))

    buttons = {}
    for i, (key, text) in enumerate([("retry", "Retry"), ("menu", "Main Menu")]):
        rect = pygame.Rect(WIDTH // 2 - 110, 400 + i * 70, 220, 50)
        hover = _detect_hover(rect, mouse_pos)
        _rect_button(surface, text, rect, font_btn, hover=hover)
        buttons[key] = rect

    return buttons


def draw_leaderboard(surface: pygame.Surface, entries: list, mouse_pos: tuple) -> dict:
    surface.fill((10, 20, 40))
    font_title = pygame.font.SysFont("Arial", 36, bold=True)
    font_hdr   = pygame.font.SysFont("Arial", 16, bold=True)
    font_row   = pygame.font.SysFont("Arial", 18)
    font_btn   = pygame.font.SysFont("Arial", 24, bold=True)

    title = font_title.render("TOP 10 LEADERBOARD", True, YELLOW)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, 40)))

    cols = ("Rank", "Name", "Score", "Dist")
    xs   = (30, 80, 270, 370)
    for col, x in zip(cols, xs):
        hdr = font_hdr.render(col, True, ORANGE)
        surface.blit(hdr, (x, 90))

    for rank, entry in enumerate(entries[:10], start=1):
        y = 115 + rank * 26
        row_color = YELLOW if rank == 1 else WHITE
        vals = (str(rank), entry.get("name", "?")[:14],
                str(entry.get("score", 0)), f"{entry.get('distance', 0)} m")
        for val, x in zip(vals, xs):
            surface.blit(font_row.render(val, True, row_color), (x, y))

    back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 70, 160, 44)
    hover = _detect_hover(back_rect, mouse_pos)
    _rect_button(surface, "Back", back_rect, font_btn, hover=hover)
    return {"back": back_rect}


def draw_settings(surface: pygame.Surface, settings: dict, mouse_pos: tuple) -> dict:
    surface.fill((15, 15, 35))
    font_title = pygame.font.SysFont("Arial", 36, bold=True)
    font_label = pygame.font.SysFont("Arial", 22)
    font_btn   = pygame.font.SysFont("Arial", 20, bold=True)

    title = font_title.render("SETTINGS", True, WHITE)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, 50)))

    buttons = {}

    # Sound toggle
    sound_label = font_label.render("Sound:", True, WHITE)
    surface.blit(sound_label, (60, 130))
    sound_text = "ON" if settings.get("sound", True) else "OFF"
    sound_rect = pygame.Rect(220, 122, 90, 36)
    _rect_button(surface, sound_text, sound_rect, font_btn,
                 bg=GREEN if settings.get("sound", True) else RED,
                 hover=_detect_hover(sound_rect, mouse_pos))
    buttons["sound"] = sound_rect

    # Car color
    color_label = font_label.render("Car colour:", True, WHITE)
    surface.blit(color_label, (60, 200))
    color_names = list(CAR_COLOR_MAP.keys())
    for i, cname in enumerate(color_names):
        rect = pygame.Rect(60 + i * 82, 234, 74, 34)
        selected = settings.get("car_color") == cname
        bg = CAR_COLOR_MAP[cname]
        bdr = WHITE if selected else GRAY
        pygame.draw.rect(surface, bg, rect, border_radius=6)
        pygame.draw.rect(surface, bdr, rect, 3 if selected else 1, border_radius=6)
        lbl = font_btn.render(cname, True, BLACK if cname == "yellow" else WHITE)
        surface.blit(lbl, lbl.get_rect(center=rect.center))
        buttons[f"color_{cname}"] = rect

    # Difficulty
    diff_label = font_label.render("Difficulty:", True, WHITE)
    surface.blit(diff_label, (60, 300))
    diffs = ["easy", "normal", "hard"]
    for i, d in enumerate(diffs):
        rect = pygame.Rect(60 + i * 120, 334, 108, 34)
        selected = settings.get("difficulty") == d
        bg = (60, 180, 60) if d == "easy" else (200, 130, 0) if d == "normal" else (200, 40, 40)
        bdr = WHITE if selected else GRAY
        pygame.draw.rect(surface, bg, rect, border_radius=6)
        pygame.draw.rect(surface, bdr, rect, 3 if selected else 1, border_radius=6)
        lbl = font_btn.render(d.capitalize(), True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=rect.center))
        buttons[f"diff_{d}"] = rect

    # Back button
    back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 70, 160, 44)
    hover = _detect_hover(back_rect, mouse_pos)
    _rect_button(surface, "Back", back_rect, font_btn, hover=hover)
    buttons["back"] = back_rect

    return buttons
