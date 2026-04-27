# Racer Game (TSIS 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete arcade Racer game in Pygame with lane hazards, traffic, power-ups, persistent leaderboard, and full menu/settings/game-over screens.

**Architecture:** State-machine game loop in `main.py` transitions between MENU / USERNAME / GAME / GAMEOVER / LEADERBOARD / SETTINGS screens. Gameplay logic lives in `racer.py`, screen drawing in `ui.py`, and JSON persistence in `persistence.py`. Constants are centralised in `constants.py`.

**Tech Stack:** Python 3.11+, Pygame 2.x, `json` stdlib, `pytest` for persistence/logic unit tests.

---

## File Map

| File | Responsibility |
|---|---|
| `TSIS3/main.py` | Entry point; event loop; state machine |
| `TSIS3/racer.py` | Player, Road, TrafficCar, Obstacle, PowerUp, Coin classes; Game logic |
| `TSIS3/ui.py` | Draw functions for every screen (no game logic) |
| `TSIS3/persistence.py` | Load/save `leaderboard.json` and `settings.json` |
| `TSIS3/constants.py` | All magic numbers: screen size, colours, speeds, lane coords |
| `TSIS3/settings.json` | Created at runtime if missing |
| `TSIS3/leaderboard.json` | Created at runtime if missing |
| `TSIS3/tests/test_persistence.py` | Unit tests for persistence layer |
| `TSIS3/tests/test_scoring.py` | Unit tests for score calculation |

---

## Task 1: Project skeleton + constants

**Files:**
- Create: `TSIS3/constants.py`
- Create: `TSIS3/__init__.py` (empty)
- Create: `TSIS3/tests/__init__.py` (empty)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p /Users/nurma/vscode_projects/KBTU_PP2/TSIS3/tests
touch /Users/nurma/vscode_projects/KBTU_PP2/TSIS3/__init__.py
touch /Users/nurma/vscode_projects/KBTU_PP2/TSIS3/tests/__init__.py
```

- [ ] **Step 2: Write `constants.py`**

```python
# TSIS3/constants.py
import pygame

# Screen
WIDTH, HEIGHT = 480, 700
FPS = 60

# Road
ROAD_LEFT = 60
ROAD_RIGHT = 420
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
NUM_LANES = 4
LANE_WIDTH = ROAD_WIDTH // NUM_LANES

def lane_center(lane: int) -> int:
    """Return x-centre of lane 0..3."""
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2

LANE_CENTERS = [lane_center(i) for i in range(NUM_LANES)]

# Colours
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (100, 100, 100)
DARK_GRAY  = (50,  50,  50)
RED        = (220, 50,  50)
GREEN      = (50,  200, 50)
BLUE       = (50,  100, 220)
YELLOW     = (240, 200, 0)
ORANGE     = (230, 130, 0)
CYAN       = (0,   220, 220)
ROAD_COLOR = (60,  60,  60)
STRIPE_COLOR = (240, 240, 0)
GRASS_COLOR  = (40, 120, 40)
SKY_COLOR    = (100, 180, 240)

# Player
PLAYER_WIDTH  = 36
PLAYER_HEIGHT = 60
PLAYER_Y      = HEIGHT - 120
PLAYER_SPEED  = 6          # pixels per frame for lane-switch slide

# Road scroll
BASE_SCROLL_SPEED = 4      # pixels per frame at difficulty 1
STRIPE_HEIGHT     = 40
STRIPE_GAP        = 40

# Coins
COIN_RADIUS = 10
COIN_WEIGHTS = {1: 50, 3: 30, 5: 20}   # value: weight
COIN_SPAWN_INTERVAL = 90   # frames

# Traffic
TRAFFIC_WIDTH  = 34
TRAFFIC_HEIGHT = 56
TRAFFIC_COLORS = [RED, BLUE, ORANGE, CYAN, (180, 60, 180)]
BASE_TRAFFIC_INTERVAL = 120   # frames between spawns at difficulty 1

# Obstacles
OBSTACLE_WIDTH  = 40
OBSTACLE_HEIGHT = 24
OBSTACLE_TYPES  = ["oil", "pothole", "barrier"]
BASE_OBSTACLE_INTERVAL = 150

# Power-ups
POWERUP_SIZE     = 32
POWERUP_TIMEOUT  = 8000   # ms before disappearing if not collected
NITRO_DURATION   = 4000   # ms
SHIELD_DURATION  = 999999 # until hit
REPAIR_DURATION  = 0      # instant

# Scoring
DISTANCE_SCORE_RATE = 1    # points per 100 px scrolled
COIN_BONUS_MULTIPLIER = 10

# Difficulty
DIFFICULTY_STEP_DISTANCE = 1500  # px scrolled before next level
MAX_DIFFICULTY = 10

# States
STATE_MENU        = "menu"
STATE_USERNAME    = "username"
STATE_GAME        = "game"
STATE_GAMEOVER    = "gameover"
STATE_LEADERBOARD = "leaderboard"
STATE_SETTINGS    = "settings"

# Default settings
DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "red",
    "difficulty": "normal",   # easy / normal / hard
}

CAR_COLOR_MAP = {
    "red":    RED,
    "blue":   BLUE,
    "green":  GREEN,
    "yellow": YELLOW,
}

DIFFICULTY_SPEED_MULT = {
    "easy":   0.7,
    "normal": 1.0,
    "hard":   1.4,
}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/
git commit -m "feat(tsis3): project skeleton and constants"
```

---

## Task 2: Persistence layer with tests

**Files:**
- Create: `TSIS3/persistence.py`
- Create: `TSIS3/tests/test_persistence.py`

- [ ] **Step 1: Write failing tests first**

```python
# TSIS3/tests/test_persistence.py
import json, os, sys, tempfile, pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import persistence as P

# ---- leaderboard ----

def test_load_leaderboard_returns_empty_list_when_file_missing(tmp_path):
    path = tmp_path / "lb.json"
    result = P.load_leaderboard(str(path))
    assert result == []

def test_save_and_load_leaderboard_round_trips(tmp_path):
    path = tmp_path / "lb.json"
    entries = [{"name": "Alice", "score": 500, "distance": 1200, "coins": 10}]
    P.save_leaderboard(entries, str(path))
    loaded = P.load_leaderboard(str(path))
    assert loaded == entries

def test_leaderboard_kept_sorted_and_truncated(tmp_path):
    path = tmp_path / "lb.json"
    entries = [{"name": f"P{i}", "score": i * 10, "distance": i * 100, "coins": i} for i in range(15)]
    P.save_leaderboard(entries, str(path))
    loaded = P.load_leaderboard(str(path))
    assert len(loaded) == 10
    assert loaded[0]["score"] >= loaded[-1]["score"]

def test_add_entry_inserts_and_keeps_top10(tmp_path):
    path = tmp_path / "lb.json"
    for i in range(10):
        P.add_entry({"name": f"P{i}", "score": i * 10, "distance": 100, "coins": 1}, str(path))
    P.add_entry({"name": "Winner", "score": 999, "distance": 9000, "coins": 99}, str(path))
    loaded = P.load_leaderboard(str(path))
    assert len(loaded) == 10
    assert loaded[0]["name"] == "Winner"

# ---- settings ----

def test_load_settings_returns_defaults_when_missing(tmp_path):
    path = tmp_path / "settings.json"
    result = P.load_settings(str(path))
    assert result["sound"] is True
    assert result["car_color"] == "red"
    assert result["difficulty"] == "normal"

def test_save_and_load_settings_round_trips(tmp_path):
    path = tmp_path / "settings.json"
    s = {"sound": False, "car_color": "blue", "difficulty": "hard"}
    P.save_settings(s, str(path))
    loaded = P.load_settings(str(path))
    assert loaded == s

def test_load_settings_fills_missing_keys_with_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"sound": False}))
    loaded = P.load_settings(str(path))
    assert loaded["car_color"] == "red"
    assert loaded["difficulty"] == "normal"
    assert loaded["sound"] is False
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
python -m pytest TSIS3/tests/test_persistence.py -v 2>&1 | head -30
```
Expected: `ModuleNotFoundError: No module named 'persistence'`

- [ ] **Step 3: Implement `persistence.py`**

```python
# TSIS3/persistence.py
import json
import os
from constants import DEFAULT_SETTINGS

_LB_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")
_ST_FILE = os.path.join(os.path.dirname(__file__), "settings.json")


def load_leaderboard(path: str = _LB_FILE) -> list[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data, key=lambda e: e["score"], reverse=True)[:10]
    except (json.JSONDecodeError, KeyError):
        return []


def save_leaderboard(entries: list[dict], path: str = _LB_FILE) -> None:
    sorted_entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:10]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted_entries, f, indent=2)


def add_entry(entry: dict, path: str = _LB_FILE) -> None:
    entries = load_leaderboard(path)
    entries.append(entry)
    save_leaderboard(entries, path)


def load_settings(path: str = _ST_FILE) -> dict:
    defaults = dict(DEFAULT_SETTINGS)
    if not os.path.exists(path):
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        defaults.update(data)
        return defaults
    except (json.JSONDecodeError, KeyError):
        return defaults


def save_settings(settings: dict, path: str = _ST_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
python -m pytest TSIS3/tests/test_persistence.py -v
```
Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add TSIS3/persistence.py TSIS3/tests/test_persistence.py
git commit -m "feat(tsis3): persistence layer with leaderboard and settings"
```

---

## Task 3: Scoring logic with tests

**Files:**
- Create: `TSIS3/scoring.py`
- Create: `TSIS3/tests/test_scoring.py`

- [ ] **Step 1: Write failing tests**

```python
# TSIS3/tests/test_scoring.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scoring import calculate_score

def test_zero_state_gives_zero():
    assert calculate_score(coins=0, distance=0, powerup_bonus=0) == 0

def test_coins_contribute():
    assert calculate_score(coins=5, distance=0, powerup_bonus=0) == 50

def test_distance_contributes():
    # 1 point per 100 px
    assert calculate_score(coins=0, distance=1000, powerup_bonus=0) == 10

def test_powerup_bonus_contributes():
    assert calculate_score(coins=0, distance=0, powerup_bonus=200) == 200

def test_combined():
    # coins=3 → 30, distance=500 → 5, bonus=100 → 100  => 135
    assert calculate_score(coins=3, distance=500, powerup_bonus=100) == 135
```

- [ ] **Step 2: Run to confirm fail**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
python -m pytest TSIS3/tests/test_scoring.py -v 2>&1 | head -10
```
Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `scoring.py`**

```python
# TSIS3/scoring.py
from constants import COIN_BONUS_MULTIPLIER, DISTANCE_SCORE_RATE

def calculate_score(coins: int, distance: float, powerup_bonus: int) -> int:
    coin_pts     = coins * COIN_BONUS_MULTIPLIER
    distance_pts = int(distance / 100) * DISTANCE_SCORE_RATE
    return coin_pts + distance_pts + powerup_bonus
```

- [ ] **Step 4: Run to confirm pass**

```bash
python -m pytest TSIS3/tests/test_scoring.py -v
```
Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add TSIS3/scoring.py TSIS3/tests/test_scoring.py
git commit -m "feat(tsis3): scoring logic with unit tests"
```

---

## Task 4: Road, stripes, and player car (racer.py — part 1)

**Files:**
- Create: `TSIS3/racer.py`

This task implements the scrolling road and the player car. No coins/traffic yet.

- [ ] **Step 1: Write `racer.py` with Road and Player**

```python
# TSIS3/racer.py
import pygame
import random
from constants import (
    WIDTH, HEIGHT, ROAD_LEFT, ROAD_RIGHT, ROAD_COLOR, STRIPE_COLOR,
    GRASS_COLOR, SKY_COLOR, STRIPE_HEIGHT, STRIPE_GAP,
    LANE_CENTERS, NUM_LANES, LANE_WIDTH, ROAD_WIDTH,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_Y, PLAYER_SPEED,
    BASE_SCROLL_SPEED, DIFFICULTY_SPEED_MULT,
    WHITE, BLACK, GRAY, RED, GREEN, BLUE, YELLOW,
    CAR_COLOR_MAP,
)


class Road:
    """Scrolling road background."""

    def __init__(self):
        self.scroll_y = 0
        self.speed = BASE_SCROLL_SPEED

    def update(self):
        self.scroll_y = (self.scroll_y + self.speed) % (STRIPE_HEIGHT + STRIPE_GAP)

    def draw(self, surface: pygame.Surface):
        # Grass sides
        surface.fill(GRASS_COLOR)
        # Road bed
        pygame.draw.rect(surface, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
        # Lane stripes
        for lane in range(1, NUM_LANES):
            x = ROAD_LEFT + lane * LANE_WIDTH
            y = -self.scroll_y
            while y < HEIGHT:
                pygame.draw.rect(surface, STRIPE_COLOR, (x - 2, y, 4, STRIPE_HEIGHT))
                y += STRIPE_HEIGHT + STRIPE_GAP
        # Road borders
        pygame.draw.rect(surface, WHITE, (ROAD_LEFT - 4, 0, 4, HEIGHT))
        pygame.draw.rect(surface, WHITE, (ROAD_RIGHT, 0, 4, HEIGHT))


class Player:
    """Lane-based player car with smooth slide animation."""

    def __init__(self, car_color: tuple = RED):
        self.lane = 1
        self.target_lane = 1
        self.x = float(LANE_CENTERS[self.lane])
        self.y = PLAYER_Y
        self.color = car_color
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.shield = False
        self.nitro = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x) - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height,
        )

    def move_left(self):
        if self.target_lane > 0:
            self.target_lane -= 1

    def move_right(self):
        if self.target_lane < NUM_LANES - 1:
            self.target_lane += 1

    def update(self):
        target_x = float(LANE_CENTERS[self.target_lane])
        diff = target_x - self.x
        if abs(diff) < PLAYER_SPEED:
            self.x = target_x
            self.lane = self.target_lane
        else:
            self.x += PLAYER_SPEED if diff > 0 else -PLAYER_SPEED

    def draw(self, surface: pygame.Surface):
        r = self.rect
        # Body
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        # Windshield
        ww, wh = r.width - 8, 14
        pygame.draw.rect(surface, (180, 220, 255),
                         (r.x + 4, r.y + 8, ww, wh), border_radius=3)
        # Wheels
        for wx, wy in [(r.x - 4, r.y + 6), (r.right, r.y + 6),
                       (r.x - 4, r.bottom - 18), (r.right, r.bottom - 18)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 8, 12), border_radius=2)
        # Shield bubble
        if self.shield:
            pygame.draw.circle(surface, (100, 180, 255),
                                r.center, max(r.width, r.height) // 2 + 8, 3)
        # Nitro flames
        if self.nitro:
            for i in range(3):
                fx = r.centerx + (i - 1) * 8
                pygame.draw.polygon(surface, YELLOW,
                                    [(fx, r.bottom), (fx - 4, r.bottom + 14), (fx + 4, r.bottom + 14)])
```

- [ ] **Step 2: Create minimal `main.py` to visually verify road + player**

```python
# TSIS3/main.py  (temporary smoke-test version — will be replaced in Task 10)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED
from racer import Road, Player

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer – smoke test")
clock = pygame.time.Clock()
road = Road()
player = Player(RED)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  player.move_left()
            if event.key == pygame.K_RIGHT: player.move_right()
    road.update()
    player.update()
    road.draw(screen)
    player.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
```

- [ ] **Step 3: Run smoke test visually**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2/TSIS3
python main.py
```
Verify: road scrolls, player car slides between lanes with arrow keys.

- [ ] **Step 4: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/racer.py TSIS3/main.py
git commit -m "feat(tsis3): scrolling road and player car"
```

---

## Task 5: Coins

**Files:**
- Modify: `TSIS3/racer.py` — add `Coin` class + `CoinManager`

- [ ] **Step 1: Append Coin classes to `racer.py`**

Add at the end of `racer.py`:

```python
class Coin:
    COIN_COLORS = {1: (255, 215, 0), 3: (192, 192, 192), 5: (255, 140, 0)}

    def __init__(self, lane: int, value: int):
        self.lane = lane
        self.value = value
        self.x = LANE_CENTERS[lane]
        self.y = -20
        self.radius = 10
        self.active = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def update(self, speed: float):
        self.y += speed
        if self.y > HEIGHT + 30:
            self.active = False

    def draw(self, surface: pygame.Surface):
        color = self.COIN_COLORS.get(self.value, (255, 215, 0))
        pygame.draw.circle(surface, color, (self.x, int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (self.x, int(self.y)), self.radius, 2)
        font = pygame.font.SysFont("Arial", 10, bold=True)
        label = font.render(str(self.value), True, BLACK)
        surface.blit(label, label.get_rect(center=(self.x, int(self.y))))


class CoinManager:
    """Spawns and manages coins on the road."""

    WEIGHTS = list(zip([1, 3, 5], [50, 30, 20]))  # (value, weight) pairs

    def __init__(self):
        self.coins: list[Coin] = []
        self.timer = 0
        self.interval = 90   # frames

    def _pick_value(self) -> int:
        values, weights = zip(*self.WEIGHTS)
        return random.choices(values, weights=weights, k=1)[0]

    def update(self, speed: float, player_lane: int):
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            lane = random.choice([l for l in range(NUM_LANES)])
            self.coins.append(Coin(lane, self._pick_value()))
        for c in self.coins:
            c.update(speed)
        self.coins = [c for c in self.coins if c.active]

    def check_collect(self, player_rect: pygame.Rect) -> int:
        """Returns total value of collected coins this frame."""
        total = 0
        for c in self.coins:
            if c.active and c.rect.colliderect(player_rect):
                total += c.value
                c.active = False
        return total

    def draw(self, surface: pygame.Surface):
        for c in self.coins:
            c.draw(surface)
```

- [ ] **Step 2: Update smoke-test `main.py` to include coins**

Replace `main.py` entirely:

```python
# TSIS3/main.py  (smoke test v2)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED, WHITE
from racer import Road, Player, CoinManager

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer – coins test")
clock = pygame.time.Clock()
road = Road()
player = Player(RED)
coins = CoinManager()
score = 0
font = pygame.font.SysFont("Arial", 20, bold=True)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  player.move_left()
            if event.key == pygame.K_RIGHT: player.move_right()
    road.update()
    player.update()
    coins.update(road.speed, player.lane)
    score += coins.check_collect(player.rect)
    road.draw(screen)
    coins.draw(screen)
    player.draw(screen)
    label = font.render(f"Coins: {score}", True, WHITE)
    screen.blit(label, (10, 10))
    pygame.display.flip()
    clock.tick(FPS)
```

- [ ] **Step 3: Run smoke test**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2/TSIS3
python main.py
```
Verify: coins spawn, driving over them increments the score counter.

- [ ] **Step 4: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/racer.py TSIS3/main.py
git commit -m "feat(tsis3): coin spawning with weighted values"
```

---

## Task 6: Traffic cars and collision detection

**Files:**
- Modify: `TSIS3/racer.py` — add `TrafficCar`, `TrafficManager`

- [ ] **Step 1: Append to `racer.py`**

```python
class TrafficCar:
    def __init__(self, lane: int, color: tuple):
        self.lane = lane
        self.x = LANE_CENTERS[lane]
        self.y = -40
        self.width = PLAYER_WIDTH - 2
        self.height = PLAYER_HEIGHT - 4
        self.color = color
        self.active = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width, self.height,
        )

    def update(self, speed: float):
        self.y += speed * 0.8   # traffic slightly slower than road
        if self.y > HEIGHT + 60:
            self.active = False

    def draw(self, surface: pygame.Surface):
        r = self.rect
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        ww, wh = r.width - 8, 12
        pygame.draw.rect(surface, (180, 220, 255),
                         (r.x + 4, r.bottom - 20, ww, wh), border_radius=3)
        for wx, wy in [(r.x - 4, r.y + 6), (r.right, r.y + 6),
                       (r.x - 4, r.bottom - 18), (r.right, r.bottom - 18)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 8, 12), border_radius=2)


class TrafficManager:
    def __init__(self):
        self.cars: list[TrafficCar] = []
        self.timer = 0
        self.interval = 120

    def _safe_lane(self, player_lane: int) -> int:
        lanes = list(range(NUM_LANES))
        random.shuffle(lanes)
        for lane in lanes:
            if lane != player_lane:
                if not any(abs(c.y) < 80 and c.lane == lane for c in self.cars):
                    return lane
        return random.randint(0, NUM_LANES - 1)

    def update(self, speed: float, player_lane: int, difficulty: int):
        self.interval = max(40, 120 - difficulty * 8)
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            lane = self._safe_lane(player_lane)
            color = random.choice(TRAFFIC_COLORS)
            self.cars.append(TrafficCar(lane, color))
            if difficulty >= 5 and random.random() < 0.3:
                lane2 = self._safe_lane(player_lane)
                self.cars.append(TrafficCar(lane2, random.choice(TRAFFIC_COLORS)))
        for c in self.cars:
            c.update(speed)
        self.cars = [c for c in self.cars if c.active]

    def check_collision(self, player_rect: pygame.Rect) -> bool:
        return any(c.rect.colliderect(player_rect) for c in self.cars)

    def draw(self, surface: pygame.Surface):
        for c in self.cars:
            c.draw(surface)
```

Also add at top of `racer.py` (after existing imports):
```python
from constants import TRAFFIC_COLORS
```

- [ ] **Step 2: Update `main.py` smoke test**

```python
# TSIS3/main.py  (smoke test v3 — traffic)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED, WHITE, BLACK
from racer import Road, Player, CoinManager, TrafficManager

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer – traffic test")
clock = pygame.time.Clock()
road = Road()
player = Player(RED)
coins = CoinManager()
traffic = TrafficManager()
score = 0
alive = True
font = pygame.font.SysFont("Arial", 20, bold=True)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  player.move_left()
            if event.key == pygame.K_RIGHT: player.move_right()
    if alive:
        road.update()
        player.update()
        coins.update(road.speed, player.lane)
        traffic.update(road.speed, player.lane, 1)
        score += coins.check_collect(player.rect)
        if traffic.check_collision(player.rect):
            alive = False
    road.draw(screen)
    coins.draw(screen)
    traffic.draw(screen)
    player.draw(screen)
    label = font.render(f"Score: {score}" if alive else "CRASH!", True, WHITE if alive else RED)
    screen.blit(label, (10, 10))
    pygame.display.flip()
    clock.tick(FPS)
```

- [ ] **Step 3: Run smoke test**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2/TSIS3
python main.py
```
Verify: enemy cars scroll down, crash shows "CRASH!" label.

- [ ] **Step 4: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/racer.py TSIS3/main.py
git commit -m "feat(tsis3): traffic cars with collision detection"
```

---

## Task 7: Road obstacles (oil spills, potholes, barriers)

**Files:**
- Modify: `TSIS3/racer.py` — add `Obstacle`, `ObstacleManager`

- [ ] **Step 1: Append to `racer.py`**

```python
class Obstacle:
    _COLORS = {"oil": (20, 20, 20), "pothole": (40, 30, 20), "barrier": (240, 60, 60)}
    _SLOW  = {"oil": 0.5, "pothole": 0.4, "barrier": 0.0}   # speed multiplier (0 = instant death/stop)

    def __init__(self, lane: int, kind: str):
        self.lane = lane
        self.kind = kind
        self.x = LANE_CENTERS[lane]
        self.y = -30
        self.width = 36
        self.height = 20
        self.active = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)

    def update(self, speed: float):
        self.y += speed
        if self.y > HEIGHT + 40:
            self.active = False

    def draw(self, surface: pygame.Surface):
        color = self._COLORS[self.kind]
        if self.kind == "oil":
            pygame.draw.ellipse(surface, color, self.rect)
            pygame.draw.ellipse(surface, (60, 60, 80),
                                self.rect.inflate(-8, -6), 2)
        elif self.kind == "pothole":
            pygame.draw.ellipse(surface, color, self.rect)
        else:  # barrier
            pygame.draw.rect(surface, color, self.rect, border_radius=4)
            pygame.draw.rect(surface, WHITE, self.rect.inflate(-4, -4), 2)


class ObstacleManager:
    def __init__(self):
        self.obstacles: list[Obstacle] = []
        self.timer = 0
        self.interval = 150

    def update(self, speed: float, player_lane: int, difficulty: int):
        self.interval = max(60, 150 - difficulty * 9)
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            lane = random.choice([l for l in range(NUM_LANES) if l != player_lane])
            kind = random.choice(["oil", "pothole", "barrier"])
            self.obstacles.append(Obstacle(lane, kind))
        for o in self.obstacles:
            o.update(speed)
        self.obstacles = [o for o in self.obstacles if o.active]

    def check_hit(self, player_rect: pygame.Rect) -> str | None:
        """Returns obstacle kind if hit, else None."""
        for o in self.obstacles:
            if o.active and o.rect.colliderect(player_rect):
                o.active = False
                return o.kind
        return None

    def draw(self, surface: pygame.Surface):
        for o in self.obstacles:
            o.draw(surface)
```

- [ ] **Step 2: Commit** (no new smoke test — will be tested in full integration)

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/racer.py
git commit -m "feat(tsis3): road obstacles (oil, pothole, barrier)"
```

---

## Task 8: Power-ups (Nitro, Shield, Repair)

**Files:**
- Modify: `TSIS3/racer.py` — add `PowerUp`, `PowerUpManager`, `PowerUpState`

- [ ] **Step 1: Append to `racer.py`**

```python
class PowerUp:
    _COLORS = {"nitro": YELLOW, "shield": BLUE, "repair": GREEN}
    _LABELS = {"nitro": "N", "shield": "S", "repair": "R"}

    def __init__(self, lane: int, kind: str):
        self.lane = lane
        self.kind = kind
        self.x = LANE_CENTERS[lane]
        self.y = -20
        self.size = 28
        self.active = True
        self.spawn_time = pygame.time.get_ticks()

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2,
                           self.size, self.size)

    def update(self, speed: float):
        self.y += speed
        if self.y > HEIGHT + 40:
            self.active = False
        if pygame.time.get_ticks() - self.spawn_time > 8000:
            self.active = False

    def draw(self, surface: pygame.Surface):
        color = self._COLORS[self.kind]
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=6)
        font = pygame.font.SysFont("Arial", 16, bold=True)
        label = font.render(self._LABELS[self.kind], True, BLACK)
        surface.blit(label, label.get_rect(center=self.rect.center))


class PowerUpState:
    """Tracks the currently active power-up effect."""

    def __init__(self):
        self.kind: str | None = None
        self.end_time: int = 0
        self.bonus_pts: int = 0

    @property
    def active(self) -> bool:
        if self.kind == "shield":
            return True   # shield stays until consumed
        return self.kind is not None and pygame.time.get_ticks() < self.end_time

    def activate(self, kind: str):
        now = pygame.time.get_ticks()
        self.kind = kind
        if kind == "nitro":
            self.end_time = now + 4000
            self.bonus_pts += 50
        elif kind == "shield":
            self.end_time = now + 999_999
            self.bonus_pts += 30
        elif kind == "repair":
            self.end_time = now          # instant — caller handles effect
            self.bonus_pts += 20

    def consume_shield(self):
        self.kind = None

    def remaining_ms(self) -> int:
        return max(0, self.end_time - pygame.time.get_ticks())

    def tick(self):
        if self.kind and self.kind != "shield" and pygame.time.get_ticks() >= self.end_time:
            self.kind = None


class PowerUpManager:
    def __init__(self):
        self.items: list[PowerUp] = []
        self.timer = 0
        self.interval = 300

    def update(self, speed: float, difficulty: int):
        self.interval = max(180, 300 - difficulty * 10)
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            lane = random.randint(0, NUM_LANES - 1)
            kind = random.choice(["nitro", "shield", "repair"])
            self.items.append(PowerUp(lane, kind))
        for p in self.items:
            p.update(speed)
        self.items = [p for p in self.items if p.active]

    def check_collect(self, player_rect: pygame.Rect) -> str | None:
        for p in self.items:
            if p.active and p.rect.colliderect(player_rect):
                p.active = False
                return p.kind
        return None

    def draw(self, surface: pygame.Surface):
        for p in self.items:
            p.draw(surface)
```

- [ ] **Step 2: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/racer.py
git commit -m "feat(tsis3): power-ups (nitro, shield, repair)"
```

---

## Task 9: Game class — wires everything together

**Files:**
- Modify: `TSIS3/racer.py` — add `Game` class at the end

- [ ] **Step 1: Append `Game` class to `racer.py`**

```python
from scoring import calculate_score

class Game:
    """
    Owns all gameplay objects and exposes:
      update(events) -> None
      draw(surface)  -> None
      is_over        -> bool
      result()       -> dict  (score, distance, coins, powerup_bonus)
    """

    def __init__(self, car_color: tuple, difficulty_name: str):
        speed_mult = DIFFICULTY_SPEED_MULT[difficulty_name]
        self.road = Road()
        self.road.speed = BASE_SCROLL_SPEED * speed_mult
        self.player = Player(car_color)
        self.coins = CoinManager()
        self.traffic = TrafficManager()
        self.obstacles = ObstacleManager()
        self.powerups = PowerUpManager()
        self.powerup_state = PowerUpState()

        self.coin_count = 0
        self.distance = 0.0
        self.difficulty = 1
        self.difficulty_name = difficulty_name
        self.is_over = False
        self._crashed = False

        self._font_hud = pygame.font.SysFont("Arial", 18, bold=True)

    def _current_speed(self) -> float:
        speed = self.road.speed
        if self.powerup_state.kind == "nitro" and self.powerup_state.active:
            speed *= 1.6
        return speed

    def _scale_difficulty(self):
        self.difficulty = min(10, 1 + int(self.distance / 1500))

    def update(self, events: list[pygame.event.Event]):
        if self.is_over:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  self.player.move_left()
                if event.key == pygame.K_RIGHT: self.player.move_right()

        speed = self._current_speed()
        self.distance += speed
        self._scale_difficulty()
        self.road.speed = BASE_SCROLL_SPEED * DIFFICULTY_SPEED_MULT[self.difficulty_name] * (1 + self.difficulty * 0.05)

        self.road.update()
        self.player.update()
        self.coins.update(speed, self.player.lane)
        self.traffic.update(speed, self.player.lane, self.difficulty)
        self.obstacles.update(speed, self.player.lane, self.difficulty)
        self.powerups.update(speed, self.difficulty)
        self.powerup_state.tick()

        # Collect coins
        self.coin_count += self.coins.check_collect(self.player.rect)

        # Collect power-up (only one at a time)
        if not self.powerup_state.active:
            kind = self.powerups.check_collect(self.player.rect)
            if kind:
                self.powerup_state.activate(kind)
                if kind == "nitro":
                    self.player.nitro = True
                elif kind == "shield":
                    self.player.shield = True

        # Nitro timeout
        if self.powerup_state.kind == "nitro" and not self.powerup_state.active:
            self.player.nitro = False

        # Obstacle hit
        hit_kind = self.obstacles.check_hit(self.player.rect)
        if hit_kind:
            if hit_kind == "barrier":
                if self.powerup_state.kind == "shield":
                    self.powerup_state.consume_shield()
                    self.player.shield = False
                else:
                    self.is_over = True
            elif hit_kind in ("oil", "pothole"):
                self.road.speed = max(2, self.road.speed * 0.6)  # slow down
                if self.powerup_state.kind == "repair":
                    pass   # repair cancels slow effect — do nothing

        # Traffic collision
        if self.traffic.check_collision(self.player.rect):
            if self.powerup_state.kind == "shield":
                self.powerup_state.consume_shield()
                self.player.shield = False
                # remove colliding cars
                player_r = self.player.rect
                self.traffic.cars = [c for c in self.traffic.cars if not c.rect.colliderect(player_r)]
            else:
                self.is_over = True

    def draw(self, surface: pygame.Surface):
        self.road.draw(surface)
        self.coins.draw(surface)
        self.obstacles.draw(surface)
        self.powerups.draw(surface)
        self.traffic.draw(surface)
        self.player.draw(surface)
        self._draw_hud(surface)

    def _draw_hud(self, surface: pygame.Surface):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        YELLOW = (240, 200, 0)
        score = self.result()["score"]
        dist_m = int(self.distance / 10)

        lines = [
            f"Score:  {score}",
            f"Dist:   {dist_m} m",
            f"Coins:  {self.coin_count}",
            f"Level:  {self.difficulty}",
        ]
        for i, line in enumerate(lines):
            surf = self._font_hud.render(line, True, WHITE)
            shadow = self._font_hud.render(line, True, BLACK)
            surface.blit(shadow, (11, 11 + i * 22))
            surface.blit(surf,   (10, 10 + i * 22))

        # Power-up bar
        if self.powerup_state.active and self.powerup_state.kind:
            kind = self.powerup_state.kind
            rem_s = self.powerup_state.remaining_ms() / 1000
            pu_text = f"{kind.upper()}"
            if kind != "repair":
                pu_text += f" {rem_s:.1f}s" if kind != "shield" else " (shield)"
            pu_surf = self._font_hud.render(pu_text, True, YELLOW)
            surface.blit(pu_surf, (surface.get_width() - pu_surf.get_width() - 10, 10))

    def result(self) -> dict:
        score = calculate_score(self.coin_count, self.distance, self.powerup_state.bonus_pts)
        return {
            "score":    score,
            "distance": int(self.distance / 10),
            "coins":    self.coin_count,
            "bonus":    self.powerup_state.bonus_pts,
        }
```

Also add this import at the top of `racer.py` (alongside other imports):
```python
from constants import DIFFICULTY_SPEED_MULT, BASE_SCROLL_SPEED
```

- [ ] **Step 2: Update smoke-test `main.py` to use `Game`**

```python
# TSIS3/main.py  (smoke test v4 — Game class)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED, WHITE
from racer import Game

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer – Game class test")
clock = pygame.time.Clock()
game = Game(car_color=RED, difficulty_name="normal")

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
    game.update(events)
    game.draw(screen)
    if game.is_over:
        font = pygame.font.SysFont("Arial", 40, bold=True)
        label = font.render("GAME OVER", True, RED)
        screen.blit(label, label.get_rect(center=(WIDTH//2, HEIGHT//2)))
    pygame.display.flip()
    clock.tick(FPS)
```

- [ ] **Step 3: Run smoke test**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2/TSIS3
python main.py
```
Verify: full gameplay with HUD, power-ups, obstacles, traffic.

- [ ] **Step 4: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/racer.py TSIS3/main.py
git commit -m "feat(tsis3): Game class integrating all gameplay systems"
```

---

## Task 10: UI screens

**Files:**
- Create: `TSIS3/ui.py`

This module contains only draw functions — no game logic.

- [ ] **Step 1: Write `ui.py`**

```python
# TSIS3/ui.py
import pygame
from constants import (
    WIDTH, HEIGHT,
    WHITE, BLACK, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, ORANGE,
    CAR_COLOR_MAP, DIFFICULTY_SPEED_MULT,
)

# ── helpers ───────────────────────────────────────────────────────────────────

def _rect_button(surface, text, rect, font,
                 bg=(80, 80, 80), fg=WHITE, hover=False):
    colour = (120, 120, 120) if hover else bg
    pygame.draw.rect(surface, colour, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    lbl = font.render(text, True, fg)
    surface.blit(lbl, lbl.get_rect(center=rect.center))
    return rect


def _detect_hover(rect, mouse_pos):
    return rect.collidepoint(mouse_pos)


# ── Main Menu ─────────────────────────────────────────────────────────────────

def draw_menu(surface: pygame.Surface, mouse_pos: tuple) -> dict[str, pygame.Rect]:
    """Draw main menu. Returns dict of button name → Rect."""
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


# ── Username Entry ─────────────────────────────────────────────────────────────

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


# ── Game Over ─────────────────────────────────────────────────────────────────

def draw_gameover(surface: pygame.Surface, result: dict,
                  mouse_pos: tuple) -> dict[str, pygame.Rect]:
    surface.fill((30, 0, 0))
    font_big   = pygame.font.SysFont("Arial", 48, bold=True)
    font_stats = pygame.font.SysFont("Arial", 24)
    font_btn   = pygame.font.SysFont("Arial", 26, bold=True)

    go = font_big.render("GAME OVER", True, RED)
    surface.blit(go, go.get_rect(center=(WIDTH // 2, 100)))

    stats = [
        ("Score",    str(result["score"])),
        ("Distance", f"{result['distance']} m"),
        ("Coins",    str(result["coins"])),
        ("Bonus",    str(result["bonus"])),
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


# ── Leaderboard ───────────────────────────────────────────────────────────────

def draw_leaderboard(surface: pygame.Surface, entries: list[dict],
                     mouse_pos: tuple) -> dict[str, pygame.Rect]:
    surface.fill((10, 20, 40))
    font_title = pygame.font.SysFont("Arial", 36, bold=True)
    font_hdr   = pygame.font.SysFont("Arial", 16, bold=True)
    font_row   = pygame.font.SysFont("Arial", 18)
    font_btn   = pygame.font.SysFont("Arial", 24, bold=True)

    title = font_title.render("TOP 10 LEADERBOARD", True, YELLOW)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, 40)))

    cols = ("Rank", "Name", "Score", "Dist")
    xs   = (30, 80, 270, 370)
    for i, (col, x) in enumerate(zip(cols, xs)):
        hdr = font_hdr.render(col, True, ORANGE)
        surface.blit(hdr, (x, 90))

    for rank, entry in enumerate(entries[:10], start=1):
        y = 115 + rank * 26
        row_color = YELLOW if rank == 1 else WHITE
        vals = (str(rank), entry["name"][:14], str(entry["score"]),
                f"{entry['distance']} m")
        for val, x in zip(vals, xs):
            surface.blit(font_row.render(val, True, row_color), (x, y))

    back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 70, 160, 44)
    hover = _detect_hover(back_rect, mouse_pos)
    _rect_button(surface, "Back", back_rect, font_btn, hover=hover)
    return {"back": back_rect}


# ── Settings ──────────────────────────────────────────────────────────────────

def draw_settings(surface: pygame.Surface, settings: dict,
                  mouse_pos: tuple) -> dict[str, pygame.Rect]:
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
    sound_text = "ON" if settings["sound"] else "OFF"
    sound_rect = pygame.Rect(220, 122, 90, 36)
    _rect_button(surface, sound_text, sound_rect, font_btn,
                 bg=GREEN if settings["sound"] else RED,
                 hover=_detect_hover(sound_rect, mouse_pos))
    buttons["sound"] = sound_rect

    # Car color
    color_label = font_label.render("Car colour:", True, WHITE)
    surface.blit(color_label, (60, 200))
    color_names = list(CAR_COLOR_MAP.keys())
    for i, cname in enumerate(color_names):
        rect = pygame.Rect(60 + i * 82, 234, 74, 34)
        selected = settings["car_color"] == cname
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
        selected = settings["difficulty"] == d
        bg = (60, 180, 60) if d == "easy" else (200, 130, 0) if d == "normal" else (200, 40, 40)
        bdr = WHITE if selected else GRAY
        pygame.draw.rect(surface, bg, rect, border_radius=6)
        pygame.draw.rect(surface, bdr, rect, 3 if selected else 1, border_radius=6)
        lbl = font_btn.render(d.capitalize(), True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=rect.center))
        buttons[f"diff_{d}"] = rect

    # Back
    back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 70, 160, 44)
    hover = _detect_hover(back_rect, mouse_pos)
    _rect_button(surface, "Back", back_rect, font_btn, hover=hover)
    buttons["back"] = back_rect

    return buttons
```

- [ ] **Step 2: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/ui.py
git commit -m "feat(tsis3): all UI screens (menu, gameover, leaderboard, settings)"
```

---

## Task 11: Full `main.py` — state machine

**Files:**
- Replace: `TSIS3/main.py`

- [ ] **Step 1: Write the complete `main.py`**

```python
# TSIS3/main.py
import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from constants import (
    WIDTH, HEIGHT, FPS,
    STATE_MENU, STATE_USERNAME, STATE_GAME, STATE_GAMEOVER,
    STATE_LEADERBOARD, STATE_SETTINGS,
    CAR_COLOR_MAP, RED,
)
from racer import Game
import ui
import persistence

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racer")
    clock = pygame.time.Clock()

    settings = persistence.load_settings()

    state    = STATE_MENU
    username = ""
    username_input = ""
    username_error = False
    game: Game | None = None
    last_result: dict = {}

    while True:
        mouse_pos = pygame.mouse.get_pos()
        events    = pygame.event.get()

        clicked = False
        for event in events:
            if event.type == pygame.QUIT:
                persistence.save_settings(settings)
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True

        # ── MENU ───────────────────────────────────────────────────────────────
        if state == STATE_MENU:
            buttons = ui.draw_menu(screen, mouse_pos)
            if clicked:
                if buttons["play"].collidepoint(mouse_pos):
                    username_input = ""
                    username_error = False
                    state = STATE_USERNAME
                elif buttons["leaderboard"].collidepoint(mouse_pos):
                    state = STATE_LEADERBOARD
                elif buttons["settings"].collidepoint(mouse_pos):
                    state = STATE_SETTINGS
                elif buttons["quit"].collidepoint(mouse_pos):
                    persistence.save_settings(settings)
                    pygame.quit()
                    sys.exit()

        # ── USERNAME ───────────────────────────────────────────────────────────
        elif state == STATE_USERNAME:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if username_input.strip():
                            username = username_input.strip()
                            car_color = CAR_COLOR_MAP.get(settings["car_color"], RED)
                            game = Game(car_color=car_color,
                                        difficulty_name=settings["difficulty"])
                            state = STATE_GAME
                        else:
                            username_error = True
                    elif event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    elif len(username_input) < 16 and event.unicode.isprintable():
                        username_input += event.unicode
            ui.draw_username(screen, username_input, username_error)

        # ── GAME ───────────────────────────────────────────────────────────────
        elif state == STATE_GAME:
            assert game is not None
            game.update(events)
            game.draw(screen)
            if game.is_over:
                last_result = game.result()
                last_result["name"] = username
                persistence.add_entry(last_result)
                state = STATE_GAMEOVER

        # ── GAME OVER ──────────────────────────────────────────────────────────
        elif state == STATE_GAMEOVER:
            buttons = ui.draw_gameover(screen, last_result, mouse_pos)
            if clicked:
                if buttons["retry"].collidepoint(mouse_pos):
                    car_color = CAR_COLOR_MAP.get(settings["car_color"], RED)
                    game = Game(car_color=car_color,
                                difficulty_name=settings["difficulty"])
                    state = STATE_GAME
                elif buttons["menu"].collidepoint(mouse_pos):
                    state = STATE_MENU

        # ── LEADERBOARD ────────────────────────────────────────────────────────
        elif state == STATE_LEADERBOARD:
            entries = persistence.load_leaderboard()
            buttons = ui.draw_leaderboard(screen, entries, mouse_pos)
            if clicked and buttons["back"].collidepoint(mouse_pos):
                state = STATE_MENU

        # ── SETTINGS ───────────────────────────────────────────────────────────
        elif state == STATE_SETTINGS:
            buttons = ui.draw_settings(screen, settings, mouse_pos)
            if clicked:
                if buttons["sound"].collidepoint(mouse_pos):
                    settings["sound"] = not settings["sound"]
                for cname in CAR_COLOR_MAP:
                    if buttons.get(f"color_{cname}", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                        settings["car_color"] = cname
                for d in ["easy", "normal", "hard"]:
                    if buttons.get(f"diff_{d}", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                        settings["difficulty"] = d
                if buttons["back"].collidepoint(mouse_pos):
                    persistence.save_settings(settings)
                    state = STATE_MENU

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full game end-to-end**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2/TSIS3
python main.py
```
Walk through: Main Menu → enter username → play → crash → Game Over → Retry / Menu → Leaderboard (shows saved score) → Settings (toggle sound, change colour, change difficulty) → back to Menu.

- [ ] **Step 3: Commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/main.py
git commit -m "feat(tsis3): full state machine (menu, username, game, gameover, leaderboard, settings)"
```

---

## Task 12: Run all unit tests and final polish

**Files:** no new files

- [ ] **Step 1: Run full test suite**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
python -m pytest TSIS3/tests/ -v
```
Expected: all 12 tests PASS (7 persistence + 5 scoring)

- [ ] **Step 2: Create initial `settings.json` and `leaderboard.json`**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2/TSIS3
python -c "
import sys, os; sys.path.insert(0, '.')
import persistence
persistence.save_settings(persistence.load_settings())
persistence.save_leaderboard([])
print('JSON files created.')
"
```

- [ ] **Step 3: Final commit**

```bash
cd /Users/nurma/vscode_projects/KBTU_PP2
git add TSIS3/settings.json TSIS3/leaderboard.json
git commit -m "feat(tsis3): initial settings and leaderboard JSON files"
```

- [ ] **Step 4: Push to GitHub**

```bash
git push origin main
```

---

## Spec Coverage Check

| Requirement | Task |
|---|---|
| Lane hazards / safe paths | Task 7 (oil, pothole, barrier in specific lanes) |
| Dynamic road events (barriers, nitro strip) | Task 7 + Task 8 (nitro power-up) |
| Traffic cars move downward, collisions end run | Task 6 |
| Road obstacles: barriers, oil, potholes | Task 7 |
| Safe spawn logic (not on player) | Task 6 `_safe_lane`, Task 7 obstacle lane ≠ player |
| Difficulty scaling | Task 9 `_scale_difficulty`, Task 6/7 `difficulty` param |
| Three power-ups: Nitro, Shield, Repair | Task 8 |
| One power-up at a time | Task 9 `PowerUpState` |
| Power-ups disappear after timeout | Task 8 `PowerUp.update` 8 s check |
| Active power-up + time shown on HUD | Task 9 `_draw_hud` |
| Score = coins + distance + bonus | Task 3 `scoring.py` |
| Distance meter shown on HUD | Task 9 `_draw_hud` |
| Persistent leaderboard (JSON) | Task 2 `persistence.py` |
| Username entry | Task 11 `STATE_USERNAME` |
| Top 10 leaderboard screen | Task 10 `draw_leaderboard` |
| Main Menu with Play/Leaderboard/Settings/Quit | Task 10 `draw_menu` |
| Settings: sound toggle, car colour, difficulty | Task 10 `draw_settings` |
| Save/load settings via `settings.json` | Task 2 `persistence.py` |
| Game Over: score/distance/coins + Retry/Menu | Task 10 `draw_gameover` |
| Repository structure as specified | All tasks |
| Weighted coins (different values) | Task 5 `CoinManager` |
| Increasing enemy speed after coins / difficulty | Task 9 `_scale_difficulty` |
