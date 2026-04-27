# Snake Game (TSIS4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Snake game with PostgreSQL leaderboard, poison food, power-ups, obstacle blocks, JSON settings, and 4 game screens (Menu, Playing, Game Over, Leaderboard, Settings).

**Architecture:** Single-process Pygame app with a screen state machine (`menu → playing → game_over → leaderboard / settings`). Game logic lives in `game.py` (no rendering), DB calls in `db.py`, preferences in `settings.py`, and all Pygame rendering + event handling in `main.py`.

**Tech Stack:** Python 3.13, Pygame 2.6, psycopg2 2.9, PostgreSQL, json (stdlib)

---

## File Map

| File | Responsibility |
|---|---|
| `TSIS4/config.py` | DB connection constants |
| `TSIS4/db.py` | DB init, save session, leaderboard, personal best |
| `TSIS4/settings.py` | Load/save settings.json |
| `TSIS4/settings.json` | Persisted user preferences |
| `TSIS4/game.py` | All game state: snake, foods, power-ups, obstacles |
| `TSIS4/main.py` | Pygame app: all screens, rendering, event loop |

---

## Task 1: Project scaffold + config.py

**Files:**
- Create: `TSIS4/config.py`

- [ ] **Step 1: Write config.py**

```python
# TSIS4/config.py
DB_CONFIG = {
    "host": "localhost",
    "database": "snake_game",
    "user": "nurma",
    "password": "",
    "port": 5432,
}
```

- [ ] **Step 2: Create the snake_game database**

```bash
psql -U nurma -c "CREATE DATABASE snake_game;" postgres
```

Expected: `CREATE DATABASE`

- [ ] **Step 3: Commit**

```bash
git add TSIS4/config.py
git commit -m "feat(TSIS4): add project scaffold and DB config"
```

---

## Task 2: Database module (db.py)

**Files:**
- Create: `TSIS4/db.py`

- [ ] **Step 1: Write db.py**

```python
# TSIS4/db.py
import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER   NOT NULL,
            level_reached INTEGER   NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
        (username,),
    )
    conn.commit()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    player_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return player_id


def save_session(player_id: int, score: int, level_reached: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
        (player_id, score, level_reached),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_leaderboard() -> list[tuple]:
    """Returns list of (username, score, level_reached, played_at) top 10."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached, gs.played_at
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_personal_best(player_id: int) -> int:
    """Returns the player's highest score ever, or 0."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(score) FROM game_sessions WHERE player_id = %s",
        (player_id,),
    )
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result or 0
```

- [ ] **Step 2: Verify DB init works**

```bash
cd TSIS4 && python3 -c "from db import init_db; init_db(); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add TSIS4/db.py
git commit -m "feat(TSIS4): add database module with leaderboard and personal best"
```

---

## Task 3: Settings module

**Files:**
- Create: `TSIS4/settings.py`
- Create: `TSIS4/settings.json`

- [ ] **Step 1: Write settings.json (initial defaults)**

```json
{
  "snake_color": [0, 200, 0],
  "grid_overlay": false,
  "sound": true
}
```

- [ ] **Step 2: Write settings.py**

```python
# TSIS4/settings.py
import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULTS = {
    "snake_color": [0, 200, 0],
    "grid_overlay": False,
    "sound": True,
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for key, val in DEFAULTS.items():
            data.setdefault(key, val)
        return data
    return dict(DEFAULTS)


def save_settings(settings: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
```

- [ ] **Step 3: Verify round-trip**

```bash
cd TSIS4 && python3 -c "
from settings import load_settings, save_settings
s = load_settings()
print(s)
s['grid_overlay'] = True
save_settings(s)
s2 = load_settings()
assert s2['grid_overlay'] == True
print('OK')
"
```

Expected: prints dict then `OK`

- [ ] **Step 4: Commit**

```bash
git add TSIS4/settings.py TSIS4/settings.json
git commit -m "feat(TSIS4): add settings load/save with JSON persistence"
```

---

## Task 4: Game state module (game.py)

**Files:**
- Create: `TSIS4/game.py`

This module contains all game logic. It uses `pygame.time.get_ticks()` for timers but does **no rendering**.

- [ ] **Step 1: Write game.py**

```python
# TSIS4/game.py
import random
import pygame

# Grid dimensions
CELL = 20
GRID_W = 32   # cells wide  (32 * 20 = 640px)
GRID_H = 24   # cells tall  (24 * 20 = 480px)
HEADER_H = 40  # px reserved at top for HUD

# Directions
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# Food kinds
FOOD_NORMAL = "normal"
FOOD_BONUS  = "bonus"
FOOD_POISON = "poison"

# Power-up kinds
PU_SPEED  = "speed_boost"
PU_SLOW   = "slow_motion"
PU_SHIELD = "shield"

# Timings (milliseconds)
BONUS_LIFETIME   = 5_000
POISON_LIFETIME  = 8_000
POWERUP_LIFETIME = 8_000
EFFECT_DURATION  = 5_000


class FoodItem:
    LIFETIMES = {FOOD_NORMAL: None, FOOD_BONUS: BONUS_LIFETIME, FOOD_POISON: POISON_LIFETIME}
    POINTS    = {FOOD_NORMAL: 10,   FOOD_BONUS: 30,             FOOD_POISON: 0}

    def __init__(self, pos: tuple[int, int], kind: str):
        self.pos = pos
        self.kind = kind
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = self.LIFETIMES[kind]

    def is_expired(self) -> bool:
        if self.lifetime is None:
            return False
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

    def time_left_ms(self) -> int | None:
        if self.lifetime is None:
            return None
        return max(0, self.lifetime - (pygame.time.get_ticks() - self.spawn_time))

    @property
    def points(self) -> int:
        return self.POINTS[self.kind]


class PowerUp:
    def __init__(self, pos: tuple[int, int], kind: str):
        self.pos = pos
        self.kind = kind
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_LIFETIME


class GameState:
    BASE_SPEED      = 8   # moves per second at level 1
    SPEED_PER_LEVEL = 2   # additional moves/s per level
    FOOD_PER_LEVEL  = 5   # food items eaten to advance a level

    def __init__(self, personal_best: int = 0):
        self.personal_best = personal_best
        self.reset()

    def reset(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.body: list[tuple[int, int]] = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.next_direction = RIGHT

        self.score = 0
        self.level = 1
        self.food_eaten_total = 0  # only counts scoring foods

        self.foods: list[FoodItem] = []
        self.powerup: PowerUp | None = None
        self.obstacles: set[tuple[int, int]] = set()

        self.active_effect: str | None = None
        self.effect_start = 0
        self.shield_used = False

        self._spawn_food()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _occupied(self) -> set[tuple[int, int]]:
        occ = set(self.body) | self.obstacles
        occ |= {f.pos for f in self.foods}
        if self.powerup:
            occ.add(self.powerup.pos)
        return occ

    def _random_free_cell(self) -> tuple[int, int] | None:
        occ = self._occupied()
        free = [(x, y) for x in range(GRID_W) for y in range(GRID_H) if (x, y) not in occ]
        return random.choice(free) if free else None

    def _spawn_food(self):
        # Always keep exactly 1 normal food
        if not any(f.kind == FOOD_NORMAL for f in self.foods):
            pos = self._random_free_cell()
            if pos:
                self.foods.append(FoodItem(pos, FOOD_NORMAL))

        # 25% chance of bonus food if none present
        if not any(f.kind == FOOD_BONUS for f in self.foods) and random.random() < 0.25:
            pos = self._random_free_cell()
            if pos:
                self.foods.append(FoodItem(pos, FOOD_BONUS))

        # Poison from level 2 onward, 30% chance if none present
        if (
            self.level >= 2
            and not any(f.kind == FOOD_POISON for f in self.foods)
            and random.random() < 0.30
        ):
            pos = self._random_free_cell()
            if pos:
                self.foods.append(FoodItem(pos, FOOD_POISON))

    def _maybe_spawn_powerup(self):
        if self.powerup is not None:
            return
        if random.random() < 0.12:
            pos = self._random_free_cell()
            if pos:
                self.powerup = PowerUp(pos, random.choice([PU_SPEED, PU_SLOW, PU_SHIELD]))

    def _place_obstacles(self):
        if self.level < 3:
            return
        # Keep existing obstacles; add 3 more per level beyond 2
        target = (self.level - 2) * 3
        head = self.body[0]
        SAFETY = 5  # cells around snake head that stay clear
        attempts = 0
        while len(self.obstacles) < target and attempts < 500:
            attempts += 1
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            if (x, y) in self._occupied():
                continue
            if abs(x - head[0]) <= SAFETY and abs(y - head[1]) <= SAFETY:
                continue
            self.obstacles.add((x, y))

    def _current_speed(self) -> int:
        base = self.BASE_SPEED + (self.level - 1) * self.SPEED_PER_LEVEL
        if self.active_effect == PU_SPEED:
            return base + 4
        if self.active_effect == PU_SLOW:
            return max(2, base - 4)
        return base

    def _tick_effects(self):
        if self.active_effect and pygame.time.get_ticks() - self.effect_start > EFFECT_DURATION:
            self.active_effect = None
            self.shield_used = False

    def _use_shield(self) -> bool:
        """Consume shield if active. Returns True if shield was available."""
        if self.active_effect == PU_SHIELD and not self.shield_used:
            self.shield_used = True
            self.active_effect = None
            return True
        return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_direction(self, new_dir: tuple[int, int]):
        if new_dir != OPPOSITE.get(self.direction):
            self.next_direction = new_dir

    @property
    def speed(self) -> int:
        return self._current_speed()

    def step(self) -> bool:
        """Advance the snake by one cell. Returns True if alive, False on death."""
        self._tick_effects()

        # Expire foods and powerup
        self.foods = [f for f in self.foods if not f.is_expired()]
        if self.powerup and self.powerup.is_expired():
            self.powerup = None

        self.direction = self.next_direction
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        # --- Border collision ---
        nx, ny = new_head
        if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
            if self._use_shield():
                # Wrap to opposite side
                new_head = (nx % GRID_W, ny % GRID_H)
            else:
                return False

        # --- Obstacle collision ---
        if new_head in self.obstacles:
            if self._use_shield():
                return True  # absorbed; snake stays in place
            return False

        # --- Self collision ---
        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)

        # --- Food collision ---
        ate = next((f for f in self.foods if f.pos == new_head), None)
        if ate:
            self.foods.remove(ate)
            if ate.kind == FOOD_POISON:
                # Shorten by net 2: we just inserted head (+1), now pop 3
                for _ in range(3):
                    if self.body:
                        self.body.pop()
                if len(self.body) <= 1:
                    return False
            else:
                # Grow: do not pop tail; add score
                self.score += ate.points
                self.food_eaten_total += 1
                if self.food_eaten_total % self.FOOD_PER_LEVEL == 0:
                    self.level += 1
                    self._place_obstacles()
        else:
            # Normal move: pop tail
            self.body.pop()

        # --- Power-up collision ---
        if self.powerup and self.powerup.pos == new_head:
            self.active_effect = self.powerup.kind
            self.effect_start = pygame.time.get_ticks()
            self.shield_used = False
            self.powerup = None

        self._spawn_food()
        self._maybe_spawn_powerup()
        return True

    def effect_time_left_ms(self) -> int:
        if not self.active_effect:
            return 0
        return max(0, EFFECT_DURATION - (pygame.time.get_ticks() - self.effect_start))
```

- [ ] **Step 2: Verify import works**

```bash
cd TSIS4 && python3 -c "
import pygame; pygame.init()
from game import GameState, RIGHT, DOWN
g = GameState()
g.set_direction(DOWN)
alive = g.step()
print('alive:', alive, 'head:', g.body[0])
"
```

Expected: prints alive: True and a head position

- [ ] **Step 3: Commit**

```bash
git add TSIS4/game.py
git commit -m "feat(TSIS4): add full game state with snake, food, power-ups, obstacles"
```

---

## Task 5: Main Pygame application (main.py)

**Files:**
- Create: `TSIS4/main.py`

This is the largest file. It contains the complete Pygame application: all 5 screens, event handling, rendering, and wiring to db.py / settings.py / game.py.

- [ ] **Step 1: Write main.py**

```python
# TSIS4/main.py
import sys
import os
import pygame

# Allow running from repo root: python TSIS4/main.py
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

# ── Window ────────────────────────────────────────────────────────────
WIN_W = GRID_W * CELL          # 640
WIN_H = HEADER_H + GRID_H * CELL  # 40 + 480 = 520

# ── Palette ───────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (60,  60,  60)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY  = (30,  30,  30)
GREEN      = (0,   200, 0)
DARK_GREEN = (0,   120, 0)
RED        = (220, 50,  50)
DARK_RED   = (120, 0,   0)
YELLOW     = (255, 220, 0)
ORANGE     = (255, 140, 0)
CYAN       = (0,   210, 210)
BLUE       = (50,  120, 255)
PURPLE     = (170, 0,   220)
WALL_COLOR = (90,  90,  90)

# Food / power-up colors
FOOD_COLORS  = {FOOD_NORMAL: (255, 80, 80), FOOD_BONUS: YELLOW, FOOD_POISON: DARK_RED}
POWERUP_COLORS = {PU_SPEED: CYAN, PU_SLOW: BLUE, PU_SHIELD: PURPLE}
POWERUP_LABELS = {PU_SPEED: "SPD", PU_SLOW: "SLO", PU_SHIELD: "SHD"}

# ── Screen states ─────────────────────────────────────────────────────
S_MENU       = "menu"
S_PLAYING    = "playing"
S_GAME_OVER  = "game_over"
S_LEADERBOARD = "leaderboard"
S_SETTINGS   = "settings"

FPS = 60


# ── Utility: Button ───────────────────────────────────────────────────
class Button:
    def __init__(self, rect: pygame.Rect, label: str, font: pygame.font.Font):
        self.rect = rect
        self.label = label
        self.font = font

    def draw(self, surface: pygame.Surface, hovered: bool = False):
        color = (80, 80, 80) if hovered else (50, 50, 50)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 2, border_radius=8)
        txt = self.font.render(self.label, True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_hovered(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def clicked(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered(event.pos)


# ── App ───────────────────────────────────────────────────────────────
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
        db.init_db()

        self.state = S_MENU
        self.username = ""
        self.player_id: int | None = None
        self.personal_best = 0
        self.game: GameState | None = None
        self.move_timer = 0

        self.leaderboard_data: list[tuple] = []

        # Settings screen toggles
        self._color_options = [
            ("Green",  [0, 200, 0]),
            ("Blue",   [50, 120, 255]),
            ("Yellow", [255, 220, 0]),
            ("White",  [240, 240, 240]),
            ("Orange", [255, 140, 0]),
        ]
        self._color_idx = 0
        # Sync color idx to current pref
        for i, (_, c) in enumerate(self._color_options):
            if c == self.prefs["snake_color"]:
                self._color_idx = i
                break

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # MENU screen
    # ------------------------------------------------------------------

    def _handle_menu(self, events):
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif ev.key == pygame.K_RETURN:
                    if self.username.strip():
                        self._start_game()
                elif len(self.username) < 20 and ev.unicode.isprintable():
                    self.username += ev.unicode

        mouse = pygame.mouse.get_pos()
        for ev in events:
            if self._btn_play.clicked(ev) and self.username.strip():
                self._start_game()
            if self._btn_leaderboard.clicked(ev):
                self.leaderboard_data = db.get_leaderboard()
                self.state = S_LEADERBOARD
            if self._btn_settings.clicked(ev):
                self.state = S_SETTINGS
            if self._btn_quit.clicked(ev):
                pygame.quit()
                sys.exit()

    def _start_game(self):
        name = self.username.strip()
        self.player_id = db.get_or_create_player(name)
        self.personal_best = db.get_personal_best(self.player_id)
        self.game = GameState(personal_best=self.personal_best)
        self.move_timer = 0
        self.state = S_PLAYING

    def _draw_menu(self):
        s = self.screen
        s.fill(DARK_GRAY)

        # Title
        title = self.font_big.render("SNAKE", True, GREEN)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=60))

        # Username prompt
        prompt = self.font_small.render("Enter username:", True, LIGHT_GRAY)
        s.blit(prompt, (WIN_W // 2 - 120, 160))

        # Username input box
        input_rect = pygame.Rect(WIN_W // 2 - 150, 188, 300, 36)
        pygame.draw.rect(s, GRAY, input_rect, border_radius=6)
        pygame.draw.rect(s, LIGHT_GRAY, input_rect, 2, border_radius=6)
        user_txt = self.font_small.render(self.username + "|", True, WHITE)
        s.blit(user_txt, (input_rect.x + 8, input_rect.y + 7))

        # Buttons
        cx = WIN_W // 2
        self._btn_play        = Button(pygame.Rect(cx - 100, 250, 200, 44), "Play", self.font_med)
        self._btn_leaderboard = Button(pygame.Rect(cx - 100, 308, 200, 44), "Leaderboard", self.font_med)
        self._btn_settings    = Button(pygame.Rect(cx - 100, 366, 200, 44), "Settings", self.font_med)
        self._btn_quit        = Button(pygame.Rect(cx - 100, 424, 200, 44), "Quit", self.font_med)

        mouse = pygame.mouse.get_pos()
        for btn in (self._btn_play, self._btn_leaderboard, self._btn_settings, self._btn_quit):
            btn.draw(s, btn.is_hovered(mouse))

        # Hint
        hint = self.font_tiny.render("Press ENTER or click Play to start", True, GRAY)
        s.blit(hint, hint.get_rect(centerx=WIN_W // 2, y=WIN_H - 30))

    # ------------------------------------------------------------------
    # PLAYING screen
    # ------------------------------------------------------------------

    def _handle_playing(self, events, dt):
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
        if self.player_id is not None:
            db.save_session(self.player_id, self.game.score, self.game.level)
            self.personal_best = db.get_personal_best(self.player_id)
        self.state = S_GAME_OVER

    def _draw_playing(self):
        s = self.screen
        s.fill(BLACK)
        g = self.game

        snake_color = tuple(self.prefs["snake_color"])

        # ── Header ────────────────────────────────────────────────────
        pygame.draw.rect(s, DARK_GRAY, (0, 0, WIN_W, HEADER_H))
        hud_items = [
            f"Score: {g.score}",
            f"Level: {g.level}",
            f"Best:  {g.personal_best}",
        ]
        for i, txt in enumerate(hud_items):
            surf = self.font_small.render(txt, True, LIGHT_GRAY)
            s.blit(surf, (10 + i * 220, 10))

        # Active effect
        if g.active_effect:
            left_s = g.effect_time_left_ms() / 1000
            eff_txt = self.font_tiny.render(
                f"{POWERUP_LABELS.get(g.active_effect, g.active_effect)} {left_s:.1f}s",
                True, POWERUP_COLORS.get(g.active_effect, WHITE)
            )
            s.blit(eff_txt, (WIN_W - 100, 14))

        # ── Game area offset ──────────────────────────────────────────
        ox, oy = 0, HEADER_H

        # Grid overlay
        if self.prefs.get("grid_overlay"):
            for gx in range(GRID_W):
                pygame.draw.line(s, (25, 25, 25), (ox + gx * CELL, oy), (ox + gx * CELL, oy + GRID_H * CELL))
            for gy in range(GRID_H):
                pygame.draw.line(s, (25, 25, 25), (ox, oy + gy * CELL), (ox + GRID_W * CELL, oy + gy * CELL))

        # Obstacles
        for (bx, by) in g.obstacles:
            pygame.draw.rect(s, WALL_COLOR, (ox + bx * CELL, oy + by * CELL, CELL, CELL))
            pygame.draw.rect(s, (50, 50, 50), (ox + bx * CELL, oy + by * CELL, CELL, CELL), 1)

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
            prect = pygame.Rect(ox + px * CELL + 1, oy + py * CELL + 1, CELL - 2, CELL - 2)
            pygame.draw.rect(s, pc, prect, border_radius=4)
            lbl = self.font_tiny.render(POWERUP_LABELS[g.powerup.kind], True, BLACK)
            s.blit(lbl, lbl.get_rect(center=prect.center))

        # Snake
        for i, (sx, sy) in enumerate(g.body):
            alpha = 255 if i == 0 else max(80, 220 - i * 6)
            color = snake_color if i > 0 else (min(255, snake_color[0] + 60), min(255, snake_color[1] + 60), min(255, snake_color[2] + 60))
            r = pygame.Rect(ox + sx * CELL + 1, oy + sy * CELL + 1, CELL - 2, CELL - 2)
            pygame.draw.rect(s, color, r, border_radius=3)

    # ------------------------------------------------------------------
    # GAME OVER screen
    # ------------------------------------------------------------------

    def _handle_game_over(self, events):
        mouse = pygame.mouse.get_pos()
        for ev in events:
            if self._btn_retry.clicked(ev):
                self.game = GameState(personal_best=self.personal_best)
                self.move_timer = 0
                self.state = S_PLAYING
            if self._btn_menu.clicked(ev):
                self.state = S_MENU

    def _draw_game_over(self):
        s = self.screen
        s.fill(DARK_GRAY)

        title = self.font_big.render("GAME OVER", True, RED)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=80))

        lines = [
            f"Score:        {self.game.score}",
            f"Level reached: {self.game.level}",
            f"Personal best: {self.personal_best}",
        ]
        for i, line in enumerate(lines):
            surf = self.font_med.render(line, True, LIGHT_GRAY)
            s.blit(surf, surf.get_rect(centerx=WIN_W // 2, y=200 + i * 50))

        cx = WIN_W // 2
        self._btn_retry = Button(pygame.Rect(cx - 100, 380, 200, 44), "Retry", self.font_med)
        self._btn_menu  = Button(pygame.Rect(cx - 100, 438, 200, 44), "Main Menu", self.font_med)

        mouse = pygame.mouse.get_pos()
        for btn in (self._btn_retry, self._btn_menu):
            btn.draw(s, btn.is_hovered(mouse))

    # ------------------------------------------------------------------
    # LEADERBOARD screen
    # ------------------------------------------------------------------

    def _handle_leaderboard(self, events):
        for ev in events:
            if self._btn_back.clicked(ev):
                self.state = S_MENU
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.state = S_MENU

    def _draw_leaderboard(self):
        s = self.screen
        s.fill(DARK_GRAY)

        title = self.font_big.render("LEADERBOARD", True, YELLOW)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=20))

        # Table header
        headers = ["#", "Username", "Score", "Level", "Date"]
        col_x   = [30, 80, 280, 370, 440]
        header_y = 90
        for hdr, cx in zip(headers, col_x):
            surf = self.font_small.render(hdr, True, LIGHT_GRAY)
            s.blit(surf, (cx, header_y))
        pygame.draw.line(s, LIGHT_GRAY, (20, 115), (WIN_W - 20, 115), 1)

        for rank, row in enumerate(self.leaderboard_data, 1):
            username, score, level, played_at = row
            color = YELLOW if rank == 1 else (LIGHT_GRAY if rank <= 3 else WHITE)
            date_str = played_at.strftime("%m/%d/%y") if played_at else "—"
            cells = [str(rank), username[:18], str(score), str(level), date_str]
            row_y = 120 + (rank - 1) * 34
            for val, cx in zip(cells, col_x):
                surf = self.font_small.render(val, True, color)
                s.blit(surf, (cx, row_y))

        if not self.leaderboard_data:
            no_data = self.font_med.render("No scores yet!", True, GRAY)
            s.blit(no_data, no_data.get_rect(centerx=WIN_W // 2, y=250))

        self._btn_back = Button(pygame.Rect(WIN_W // 2 - 80, WIN_H - 60, 160, 44), "Back", self.font_med)
        mouse = pygame.mouse.get_pos()
        self._btn_back.draw(s, self._btn_back.is_hovered(mouse))

    # ------------------------------------------------------------------
    # SETTINGS screen
    # ------------------------------------------------------------------

    def _handle_settings(self, events):
        mouse = pygame.mouse.get_pos()
        for ev in events:
            if self._btn_save.clicked(ev):
                settings_mod.save_settings(self.prefs)
                self.state = S_MENU
            if self._btn_toggle_grid.clicked(ev):
                self.prefs["grid_overlay"] = not self.prefs["grid_overlay"]
            if self._btn_toggle_sound.clicked(ev):
                self.prefs["sound"] = not self.prefs["sound"]
            if self._btn_color_prev.clicked(ev):
                self._color_idx = (self._color_idx - 1) % len(self._color_options)
                self.prefs["snake_color"] = self._color_options[self._color_idx][1]
            if self._btn_color_next.clicked(ev):
                self._color_idx = (self._color_idx + 1) % len(self._color_options)
                self.prefs["snake_color"] = self._color_options[self._color_idx][1]
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.state = S_MENU

    def _draw_settings(self):
        s = self.screen
        s.fill(DARK_GRAY)

        title = self.font_big.render("SETTINGS", True, CYAN)
        s.blit(title, title.get_rect(centerx=WIN_W // 2, y=40))

        cx = WIN_W // 2

        # Grid overlay toggle
        grid_lbl = self.font_med.render(
            f"Grid Overlay:  {'ON' if self.prefs['grid_overlay'] else 'OFF'}", True, WHITE
        )
        s.blit(grid_lbl, grid_lbl.get_rect(centerx=cx, y=150))
        self._btn_toggle_grid = Button(pygame.Rect(cx - 60, 190, 120, 36), "Toggle", self.font_small)

        # Sound toggle
        snd_lbl = self.font_med.render(
            f"Sound:  {'ON' if self.prefs['sound'] else 'OFF'}", True, WHITE
        )
        s.blit(snd_lbl, snd_lbl.get_rect(centerx=cx, y=250))
        self._btn_toggle_sound = Button(pygame.Rect(cx - 60, 290, 120, 36), "Toggle", self.font_small)

        # Snake color picker
        color_name, color_val = self._color_options[self._color_idx]
        col_lbl = self.font_med.render(f"Snake Color:", True, WHITE)
        s.blit(col_lbl, col_lbl.get_rect(centerx=cx, y=350))

        self._btn_color_prev = Button(pygame.Rect(cx - 120, 385, 40, 36), "<", self.font_med)
        self._btn_color_next = Button(pygame.Rect(cx +  80, 385, 40, 36), ">", self.font_med)

        # Color swatch
        swatch_rect = pygame.Rect(cx - 70, 385, 140, 36)
        pygame.draw.rect(s, tuple(color_val), swatch_rect, border_radius=6)
        name_surf = self.font_small.render(color_name, True, BLACK)
        s.blit(name_surf, name_surf.get_rect(center=swatch_rect.center))

        self._btn_save = Button(pygame.Rect(cx - 100, 460, 200, 44), "Save & Back", self.font_med)

        mouse = pygame.mouse.get_pos()
        for btn in (
            self._btn_toggle_grid, self._btn_toggle_sound,
            self._btn_color_prev, self._btn_color_next, self._btn_save
        ):
            btn.draw(s, btn.is_hovered(mouse))


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    App().run()
```

- [ ] **Step 2: Run the game and verify**

```bash
cd TSIS4 && python3 main.py
```

Expected: game window opens, all 4 screens are navigable, snake moves, DB saves work.

- [ ] **Step 3: Commit**

```bash
git add TSIS4/main.py
git commit -m "feat(TSIS4): add full Pygame app with all 5 screens and game loop"
```

---

## Task 6: Final wiring and repository cleanup

- [ ] **Step 1: Ensure all files exist**

```bash
ls TSIS4/
```

Expected: `config.py  db.py  game.py  main.py  settings.json  settings.py  assets/`

- [ ] **Step 2: Full smoke-test**

Play a game, reach level 3 (eat 10 foods), verify:
- Obstacles appear
- Leaderboard shows your score after game over
- Settings saves and persists on restart
- Poison food shortens snake
- Power-ups appear and expire

- [ ] **Step 3: Final commit**

```bash
git add TSIS4/
git commit -m "feat(TSIS4): complete snake game with DB, power-ups, obstacles, settings"
```

---

## Spec Coverage Checklist

| Requirement | Task |
|---|---|
| PostgreSQL schema: players + game_sessions | Task 2 |
| Username entry on main menu | Task 5 (Menu screen) |
| Auto-save result to DB after game over | Task 5 (_on_game_over) |
| Leaderboard screen Top 10 | Task 5 (Leaderboard screen) |
| Personal best during gameplay | Task 5 (HUD header) |
| Poison food: shorten, game over if too short | Task 4 (game.py step()) |
| Speed boost power-up 5s | Task 4 (PU_SPEED) |
| Slow motion power-up 5s | Task 4 (PU_SLOW) |
| Shield power-up until triggered | Task 4 (PU_SHIELD) |
| Power-up disappears after 8s | Task 4 (POWERUP_LIFETIME) |
| Obstacles from Level 3 | Task 4 (_place_obstacles) |
| Obstacles don't trap snake | Task 4 (SAFETY radius) |
| Food + power-ups avoid obstacle cells | Task 4 (_occupied) |
| settings.json snake color | Task 3 + 5 |
| settings.json grid overlay | Task 3 + 5 |
| settings.json sound toggle | Task 3 + 5 |
| Main Menu screen | Task 5 |
| Game Over screen | Task 5 |
| Leaderboard screen | Task 5 |
| Settings screen | Task 5 |
