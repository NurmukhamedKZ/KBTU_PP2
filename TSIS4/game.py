import random
import pygame

# Grid dimensions
CELL = 20
GRID_W = 32    # cells wide  (32 * 20 = 640 px)
GRID_H = 24    # cells tall  (24 * 20 = 480 px)
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
    _LIFETIMES = {FOOD_NORMAL: None, FOOD_BONUS: BONUS_LIFETIME, FOOD_POISON: POISON_LIFETIME}
    _POINTS    = {FOOD_NORMAL: 10,   FOOD_BONUS: 30,             FOOD_POISON: 0}

    def __init__(self, pos: tuple, kind: str):
        self.pos = pos
        self.kind = kind
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = self._LIFETIMES[kind]

    def is_expired(self) -> bool:
        if self.lifetime is None:
            return False
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

    def time_left_ms(self):
        if self.lifetime is None:
            return None
        return max(0, self.lifetime - (pygame.time.get_ticks() - self.spawn_time))

    @property
    def points(self) -> int:
        return self._POINTS[self.kind]


class PowerUp:
    def __init__(self, pos: tuple, kind: str):
        self.pos = pos
        self.kind = kind
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_LIFETIME


class GameState:
    BASE_SPEED      = 8   # moves per second at level 1
    SPEED_PER_LEVEL = 2   # extra moves/s per level
    FOOD_PER_LEVEL  = 5   # scoring foods eaten to advance a level

    def __init__(self, personal_best: int = 0):
        self.personal_best = personal_best
        self.reset()

    def reset(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.next_direction = RIGHT

        self.score = 0
        self.level = 1
        self.food_eaten_total = 0  # counts only scoring foods

        self.foods = []
        self.powerup = None
        self.obstacles = set()

        self.active_effect = None
        self.effect_start = 0
        self.shield_used = False

        self._spawn_food()

    # ── Internal helpers ────────────────────────────────────────────────

    def _occupied(self) -> set:
        occ = set(self.body) | self.obstacles
        occ |= {f.pos for f in self.foods}
        if self.powerup:
            occ.add(self.powerup.pos)
        return occ

    def _random_free_cell(self):
        occ = self._occupied()
        free = [(x, y) for x in range(GRID_W) for y in range(GRID_H) if (x, y) not in occ]
        return random.choice(free) if free else None

    def _spawn_food(self):
        # Always keep exactly 1 normal food
        if not any(f.kind == FOOD_NORMAL for f in self.foods):
            pos = self._random_free_cell()
            if pos:
                self.foods.append(FoodItem(pos, FOOD_NORMAL))

        # 25 % chance of bonus food if none present
        if not any(f.kind == FOOD_BONUS for f in self.foods) and random.random() < 0.25:
            pos = self._random_free_cell()
            if pos:
                self.foods.append(FoodItem(pos, FOOD_BONUS))

        # Poison from level 2, 30 % chance if none present
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
        target = (self.level - 2) * 3
        head = self.body[0]
        SAFETY = 5
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

    def _tick_effects(self):
        if self.active_effect and pygame.time.get_ticks() - self.effect_start > EFFECT_DURATION:
            self.active_effect = None
            self.shield_used = False

    def _use_shield(self) -> bool:
        if self.active_effect == PU_SHIELD and not self.shield_used:
            self.shield_used = True
            self.active_effect = None
            return True
        return False

    # ── Public API ──────────────────────────────────────────────────────

    def set_direction(self, new_dir: tuple):
        if new_dir != OPPOSITE.get(self.direction):
            self.next_direction = new_dir

    @property
    def speed(self) -> int:
        base = self.BASE_SPEED + (self.level - 1) * self.SPEED_PER_LEVEL
        if self.active_effect == PU_SPEED:
            return base + 4
        if self.active_effect == PU_SLOW:
            return max(2, base - 4)
        return base

    def effect_time_left_ms(self) -> int:
        if not self.active_effect:
            return 0
        return max(0, EFFECT_DURATION - (pygame.time.get_ticks() - self.effect_start))

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
        nx, ny = new_head

        # Border collision
        if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
            if self._use_shield():
                new_head = (nx % GRID_W, ny % GRID_H)
            else:
                return False

        # Obstacle collision
        if new_head in self.obstacles:
            if self._use_shield():
                return True  # shield absorbed; snake stays in place
            return False

        # Self collision
        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)

        # Food collision
        ate = next((f for f in self.foods if f.pos == new_head), None)
        if ate:
            self.foods.remove(ate)
            if ate.kind == FOOD_POISON:
                # Net effect: shorten by 2.
                # We already inserted the new head (+1), so pop 3 total.
                for _ in range(3):
                    if self.body:
                        self.body.pop()
                if len(self.body) <= 1:
                    return False
            else:
                # Grow: do NOT pop tail; add score
                self.score += ate.points
                self.food_eaten_total += 1
                if self.food_eaten_total % self.FOOD_PER_LEVEL == 0:
                    self.level += 1
                    self._place_obstacles()
        else:
            # Normal move: remove tail
            self.body.pop()

        # Power-up collision
        if self.powerup and self.powerup.pos == new_head:
            self.active_effect = self.powerup.kind
            self.effect_start = pygame.time.get_ticks()
            self.shield_used = False
            self.powerup = None

        self._spawn_food()
        self._maybe_spawn_powerup()
        return True
