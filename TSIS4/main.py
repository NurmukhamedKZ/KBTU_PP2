import sys
import os
import pygame

# Allow `python TSIS4/main.py` from repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db
import settings as settings_mod
from game import (
    GameState,
    UP, DOWN, LEFT, RIGHT,
    CELL, GRID_W, GRID_H, HEADER_H,
    FOOD_NORMAL, FOOD_BONUS, FOOD_POISON,
    PU_SPEED, PU_SLOW, PU_SHIELD,
)

# ── Window ──────────────────────────────────────────────────────────────
WIN_W = GRID_W * CELL               # 640
WIN_H = HEADER_H + GRID_H * CELL   # 40 + 480 = 520

# ── Palette ──────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (60,  60,  60)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY  = (25,  25,  25)
GREEN      = (0,   200, 0)
RED        = (220, 50,  50)
DARK_RED   = (120, 0,   0)
YELLOW     = (255, 220, 0)
ORANGE     = (255, 140, 0)
CYAN       = (0,   210, 210)
BLUE       = (50,  120, 255)
PURPLE     = (170, 0,   220)
WALL_COLOR = (90,  90,  90)

FOOD_COLORS    = {FOOD_NORMAL: (255, 80, 80), FOOD_BONUS: YELLOW, FOOD_POISON: DARK_RED}
POWERUP_COLORS = {PU_SPEED: CYAN, PU_SLOW: BLUE, PU_SHIELD: PURPLE}
POWERUP_LABELS = {PU_SPEED: "SPD", PU_SLOW: "SLO", PU_SHIELD: "SHD"}

# ── Screen states ─────────────────────────────────────────────────────────
S_MENU        = "menu"
S_PLAYING     = "playing"
S_GAME_OVER   = "game_over"
S_LEADERBOARD = "leaderboard"
S_SETTINGS    = "settings"

FPS = 60


# ── Button helper ─────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect: pygame.Rect, label: str, font: pygame.font.Font):
        self.rect = rect
        self.label = label
        self.font = font

    def draw(self, surface: pygame.Surface, hovered: bool = False):
        color = (80, 80, 80) if hovered else (45, 45, 45)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 2, border_radius=8)
        txt = self.font.render(self.label, True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_hovered(self, pos) -> bool:
        return self.rect.collidepoint(pos)

    def clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.is_hovered(event.pos)
        )


# ── Main application ───────────────────────────────────────────────────────
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Snake — TSIS4")
        self.clock = pygame.time.Clock()

        self.font_big   = pygame.font.SysFont("monospace", 42, bold=True)
        self.font_med   = pygame.font.SysFont("monospace", 26, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 18)
        self.font_tiny  = pygame.font.SysFont("monospace", 14)

        self.prefs = settings_mod.load_settings()

        # Try to initialise DB; if it fails, game still runs (no leaderboard)
        self.db_ok = False
        try:
            db.init_db()
            self.db_ok = True
        except Exception as e:
            print(f"[DB] Could not connect: {e}\nGame will run without leaderboard.")

        self.state = S_MENU
        self.username = ""
        self.player_id = None
        self.personal_best = 0
        self.game = None
        self.move_timer = 0
        self.leaderboard_data = []

        # Colour picker for settings screen
        self._color_options = [
            ("Green",  [0, 200, 0]),
            ("Blue",   [50, 120, 255]),
            ("Yellow", [255, 220, 0]),
            ("White",  [240, 240, 240]),
            ("Orange", [255, 140, 0]),
        ]
        self._color_idx = 0
        for i, (_, c) in enumerate(self._color_options):
            if c == self.prefs.get("snake_color"):
                self._color_idx = i
                break

        # Build persistent button objects (rebuilt each frame that needs them)
        self._menu_buttons = {}
        self._go_buttons = {}
        self._lb_buttons = {}
        self._set_buttons = {}

    # ── Main loop ──────────────────────────────────────────────────────────

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            events = pygame.event.get()

            for ev in events:
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.state == S_MENU:
                self._handle_menu(events)
                self._draw_menu()
            elif self.state == S_PLAYING:
                self._handle_playing(events, dt)
                self._draw_playing()
            elif self.state == S_GAME_OVER:
                self._handle_game_over(events)
                self._draw_game_over()
            elif self.state == S_LEADERBOARD:
                self._handle_leaderboard(events)
                self._draw_leaderboard()
            elif self.state == S_SETTINGS:
                self._handle_settings(events)
                self._draw_settings()

            pygame.display.flip()

    # ── MENU ───────────────────────────────────────────────────────────────

    def _make_menu_buttons(self):
        cx = WIN_W // 2
        self._menu_buttons = {
            "play":   Button(pygame.Rect(cx - 110, 255, 220, 46), "Play", self.font_med),
            "lb":     Button(pygame.Rect(cx - 110, 315, 220, 46), "Leaderboard", self.font_med),
            "set":    Button(pygame.Rect(cx - 110, 375, 220, 46), "Settings", self.font_med),
            "quit":   Button(pygame.Rect(cx - 110, 435, 220, 46), "Quit", self.font_med),
        }

    def _handle_menu(self, events):
        self._make_menu_buttons()
        mouse = pygame.mouse.get_pos()
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif ev.key == pygame.K_RETURN and self.username.strip():
                    self._start_game()
                elif len(self.username) < 20 and ev.unicode.isprintable() and ev.unicode != "":
                    self.username += ev.unicode

            if self._menu_buttons["play"].clicked(ev) and self.username.strip():
                self._start_game()
            if self._menu_buttons["lb"].clicked(ev):
                if self.db_ok:
                    self.leaderboard_data = db.get_leaderboard()
                self.state = S_LEADERBOARD
            if self._menu_buttons["set"].clicked(ev):
                self.state = S_SETTINGS
            if self._menu_buttons["quit"].clicked(ev):
                pygame.quit()
                sys.exit()

    def _start_game(self):
        name = self.username.strip()
        if self.db_ok:
            self.player_id = db.get_or_create_player(name)
            self.personal_best = db.get_personal_best(self.player_id)
        self.game = GameState(personal_best=self.personal_best)
        self.move_timer = 0
        self.state = S_PLAYING

    def _draw_menu(self):
        s = self.screen
        s.fill(DARK_GRAY)

        title = self.font_big.render("S N A K E", True, GREEN)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=55))

        sub = self.font_small.render("TSIS 4 — Pygame + PostgreSQL", True, GRAY)
        s.blit(sub, sub.get_rect(centerx=WIN_W // 2, y=115))

        # Username input
        prompt = self.font_small.render("Username:", True, LIGHT_GRAY)
        s.blit(prompt, (WIN_W // 2 - 150, 162))
        input_rect = pygame.Rect(WIN_W // 2 - 150, 186, 300, 38)
        pygame.draw.rect(s, GRAY, input_rect, border_radius=6)
        pygame.draw.rect(s, LIGHT_GRAY, input_rect, 2, border_radius=6)
        user_surf = self.font_small.render(self.username + "|", True, WHITE)
        s.blit(user_surf, (input_rect.x + 8, input_rect.y + 8))

        mouse = pygame.mouse.get_pos()
        for btn in self._menu_buttons.values():
            btn.draw(s, btn.is_hovered(mouse))

        hint = self.font_tiny.render("Arrow keys / WASD to move  |  ESC to pause", True, GRAY)
        s.blit(hint, hint.get_rect(centerx=WIN_W // 2, y=WIN_H - 24))

    # ── PLAYING ────────────────────────────────────────────────────────────

    def _handle_playing(self, events, dt: int):
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    self.game.set_direction(UP)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.game.set_direction(DOWN)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    self.game.set_direction(LEFT)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    self.game.set_direction(RIGHT)
                elif ev.key == pygame.K_ESCAPE:
                    self.state = S_MENU

        self.move_timer += dt
        interval = 1000 / self.game.speed
        if self.move_timer >= interval:
            self.move_timer -= interval
            alive = self.game.step()
            if not alive:
                self._on_game_over()

    def _on_game_over(self):
        if self.db_ok and self.player_id is not None:
            db.save_session(self.player_id, self.game.score, self.game.level)
            self.personal_best = db.get_personal_best(self.player_id)
            self.game.personal_best = self.personal_best
        self.state = S_GAME_OVER

    def _draw_playing(self):
        s = self.screen
        g = self.game
        s.fill(BLACK)

        snake_color = tuple(self.prefs.get("snake_color", [0, 200, 0]))

        # HUD
        pygame.draw.rect(s, (20, 20, 20), (0, 0, WIN_W, HEADER_H))
        hud = [
            f"Score: {g.score}",
            f"Level: {g.level}",
            f"Best:  {g.personal_best}",
        ]
        for i, txt in enumerate(hud):
            surf = self.font_small.render(txt, True, LIGHT_GRAY)
            s.blit(surf, (10 + i * 215, 11))

        if g.active_effect:
            left_s = g.effect_time_left_ms() / 1000
            clr = POWERUP_COLORS.get(g.active_effect, WHITE)
            eff = self.font_tiny.render(
                f"{POWERUP_LABELS[g.active_effect]} {left_s:.1f}s", True, clr
            )
            s.blit(eff, (WIN_W - 90, 14))

        ox, oy = 0, HEADER_H

        # Grid overlay
        if self.prefs.get("grid_overlay"):
            for gx in range(GRID_W):
                pygame.draw.line(s, (30, 30, 30), (ox + gx * CELL, oy), (ox + gx * CELL, oy + GRID_H * CELL))
            for gy in range(GRID_H):
                pygame.draw.line(s, (30, 30, 30), (ox, oy + gy * CELL), (ox + GRID_W * CELL, oy + gy * CELL))

        # Obstacles
        for bx, by in g.obstacles:
            r = pygame.Rect(ox + bx * CELL, oy + by * CELL, CELL, CELL)
            pygame.draw.rect(s, WALL_COLOR, r)
            pygame.draw.rect(s, (50, 50, 50), r, 1)

        # Foods
        for food in g.foods:
            fc = FOOD_COLORS[food.kind]
            fx, fy = food.pos
            rect = pygame.Rect(ox + fx * CELL + 2, oy + fy * CELL + 2, CELL - 4, CELL - 4)
            pygame.draw.ellipse(s, fc, rect)
            # Timer bar for expiring foods
            tl = food.time_left_ms()
            if tl is not None and food.lifetime:
                ratio = tl / food.lifetime
                bar_w = int((CELL - 4) * ratio)
                pygame.draw.rect(s, WHITE, (ox + fx * CELL + 2, oy + fy * CELL + CELL - 4, bar_w, 2))

        # Power-up
        if g.powerup:
            px, py = g.powerup.pos
            pc = POWERUP_COLORS[g.powerup.kind]
            pr = pygame.Rect(ox + px * CELL + 1, oy + py * CELL + 1, CELL - 2, CELL - 2)
            pygame.draw.rect(s, pc, pr, border_radius=4)
            lbl = self.font_tiny.render(POWERUP_LABELS[g.powerup.kind], True, BLACK)
            s.blit(lbl, lbl.get_rect(center=pr.center))

        # Snake
        for i, (sx, sy) in enumerate(g.body):
            if i == 0:
                # Brighter head
                head_clr = tuple(min(255, c + 70) for c in snake_color)
                r = pygame.Rect(ox + sx * CELL + 1, oy + sy * CELL + 1, CELL - 2, CELL - 2)
                pygame.draw.rect(s, head_clr, r, border_radius=4)
            else:
                fade = max(60, 220 - i * 5)
                body_clr = tuple(int(c * fade / 220) for c in snake_color)
                r = pygame.Rect(ox + sx * CELL + 2, oy + sy * CELL + 2, CELL - 4, CELL - 4)
                pygame.draw.rect(s, body_clr, r, border_radius=3)

    # ── GAME OVER ──────────────────────────────────────────────────────────

    def _make_go_buttons(self):
        cx = WIN_W // 2
        self._go_buttons = {
            "retry": Button(pygame.Rect(cx - 110, 385, 220, 46), "Retry", self.font_med),
            "menu":  Button(pygame.Rect(cx - 110, 445, 220, 46), "Main Menu", self.font_med),
        }

    def _handle_game_over(self, events):
        self._make_go_buttons()
        for ev in events:
            if self._go_buttons["retry"].clicked(ev):
                self.game = GameState(personal_best=self.personal_best)
                self.move_timer = 0
                self.state = S_PLAYING
            if self._go_buttons["menu"].clicked(ev):
                self.state = S_MENU

    def _draw_game_over(self):
        s = self.screen
        s.fill(DARK_GRAY)

        title = self.font_big.render("GAME  OVER", True, RED)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=80))

        lines = [
            ("Score",         str(self.game.score)),
            ("Level reached", str(self.game.level)),
            ("Personal best", str(self.personal_best)),
        ]
        for i, (label, val) in enumerate(lines):
            row_y = 200 + i * 54
            lbl_s = self.font_med.render(f"{label}:", True, LIGHT_GRAY)
            val_s = self.font_med.render(val, True, YELLOW if label == "Personal best" else WHITE)
            s.blit(lbl_s, (WIN_W // 2 - 200, row_y))
            s.blit(val_s, (WIN_W // 2 + 60,  row_y))

        mouse = pygame.mouse.get_pos()
        for btn in self._go_buttons.values():
            btn.draw(s, btn.is_hovered(mouse))

    # ── LEADERBOARD ────────────────────────────────────────────────────────

    def _make_lb_buttons(self):
        self._lb_buttons = {
            "back": Button(pygame.Rect(WIN_W // 2 - 90, WIN_H - 58, 180, 44), "Back", self.font_med),
        }

    def _handle_leaderboard(self, events):
        self._make_lb_buttons()
        for ev in events:
            if self._lb_buttons["back"].clicked(ev):
                self.state = S_MENU
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.state = S_MENU

    def _draw_leaderboard(self):
        s = self.screen
        s.fill(DARK_GRAY)

        title = self.font_big.render("LEADERBOARD", True, YELLOW)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=18))

        col_x   = [28, 72, 260, 360, 450]
        headers = ["#", "Username", "Score", "Level", "Date"]
        hy = 85
        for hdr, cx in zip(headers, col_x):
            surf = self.font_small.render(hdr, True, LIGHT_GRAY)
            s.blit(surf, (cx, hy))
        pygame.draw.line(s, LIGHT_GRAY, (20, 110), (WIN_W - 20, 110), 1)

        rank_colors = {1: YELLOW, 2: (200, 200, 200), 3: ORANGE}
        for rank, row in enumerate(self.leaderboard_data, 1):
            username, score, level, played_at = row
            color = rank_colors.get(rank, WHITE)
            date_str = played_at.strftime("%d/%m/%y") if played_at else "—"
            cells = [str(rank), username[:16], str(score), str(level), date_str]
            row_y = 116 + (rank - 1) * 34
            for val, cx in zip(cells, col_x):
                surf = self.font_small.render(val, True, color)
                s.blit(surf, (cx, row_y))

        if not self.leaderboard_data:
            no = self.font_med.render("No scores yet — play first!", True, GRAY)
            s.blit(no, no.get_rect(centerx=WIN_W // 2, y=260))

        mouse = pygame.mouse.get_pos()
        for btn in self._lb_buttons.values():
            btn.draw(s, btn.is_hovered(mouse))

    # ── SETTINGS ───────────────────────────────────────────────────────────

    def _make_set_buttons(self):
        cx = WIN_W // 2
        self._set_buttons = {
            "toggle_grid":  Button(pygame.Rect(cx - 60, 196, 120, 36), "Toggle", self.font_small),
            "toggle_sound": Button(pygame.Rect(cx - 60, 296, 120, 36), "Toggle", self.font_small),
            "color_prev":   Button(pygame.Rect(cx - 130, 390, 40, 36), "<", self.font_med),
            "color_next":   Button(pygame.Rect(cx +  90, 390, 40, 36), ">", self.font_med),
            "save":         Button(pygame.Rect(cx - 110, 460, 220, 46), "Save & Back", self.font_med),
        }

    def _handle_settings(self, events):
        self._make_set_buttons()
        for ev in events:
            if self._set_buttons["toggle_grid"].clicked(ev):
                self.prefs["grid_overlay"] = not self.prefs["grid_overlay"]
            if self._set_buttons["toggle_sound"].clicked(ev):
                self.prefs["sound"] = not self.prefs["sound"]
            if self._set_buttons["color_prev"].clicked(ev):
                self._color_idx = (self._color_idx - 1) % len(self._color_options)
                self.prefs["snake_color"] = self._color_options[self._color_idx][1]
            if self._set_buttons["color_next"].clicked(ev):
                self._color_idx = (self._color_idx + 1) % len(self._color_options)
                self.prefs["snake_color"] = self._color_options[self._color_idx][1]
            if self._set_buttons["save"].clicked(ev):
                settings_mod.save_settings(self.prefs)
                self.state = S_MENU
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.state = S_MENU

    def _draw_settings(self):
        s = self.screen
        s.fill(DARK_GRAY)

        title = self.font_big.render("SETTINGS", True, CYAN)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=35))

        cx = WIN_W // 2

        # Grid overlay row
        g_val = "ON" if self.prefs.get("grid_overlay") else "OFF"
        g_clr = GREEN if self.prefs.get("grid_overlay") else RED
        g_lbl = self.font_med.render(f"Grid Overlay:  {g_val}", True, WHITE)
        g_lbl_val = self.font_med.render(g_val, True, g_clr)
        base_surf = self.font_med.render("Grid Overlay:  ", True, WHITE)
        s.blit(base_surf, base_surf.get_rect(centerx=cx - 30, y=150))
        s.blit(g_lbl_val, (cx + base_surf.get_width() - 80, 150))

        # Sound row
        snd_val = "ON" if self.prefs.get("sound") else "OFF"
        snd_clr = GREEN if self.prefs.get("sound") else RED
        base_snd = self.font_med.render("Sound:  ", True, WHITE)
        snd_v = self.font_med.render(snd_val, True, snd_clr)
        s.blit(base_snd, base_snd.get_rect(centerx=cx - 30, y=250))
        s.blit(snd_v, (cx + base_snd.get_width() - 80, 250))

        # Color picker
        col_label = self.font_med.render("Snake Color:", True, WHITE)
        s.blit(col_label, col_label.get_rect(centerx=cx, y=350))
        color_name, color_val = self._color_options[self._color_idx]
        swatch = pygame.Rect(cx - 80, 390, 160, 36)
        pygame.draw.rect(s, tuple(color_val), swatch, border_radius=6)
        name_s = self.font_small.render(color_name, True, BLACK)
        s.blit(name_s, name_s.get_rect(center=swatch.center))

        mouse = pygame.mouse.get_pos()
        for btn in self._set_buttons.values():
            btn.draw(s, btn.is_hovered(mouse))


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    App().run()
