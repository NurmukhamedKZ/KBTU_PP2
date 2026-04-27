# TSIS3/racer.py
import pygame
import random
from constants import (
    WIDTH, HEIGHT, ROAD_LEFT, ROAD_RIGHT, ROAD_COLOR, STRIPE_COLOR,
    GRASS_COLOR, STRIPE_HEIGHT, STRIPE_GAP,
    LANE_CENTERS, NUM_LANES, LANE_WIDTH, ROAD_WIDTH,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_Y, PLAYER_SPEED,
    BASE_SCROLL_SPEED, DIFFICULTY_SPEED_MULT,
    WHITE, BLACK, GRAY, RED, GREEN, BLUE, YELLOW,
    CAR_COLOR_MAP, TRAFFIC_COLORS,
    COIN_BONUS_MULTIPLIER, DISTANCE_SCORE_RATE,
)
from scoring import calculate_score


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


class Obstacle:
    _COLORS = {"oil": (20, 20, 20), "pothole": (40, 30, 20), "barrier": (240, 60, 60)}

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


class Game:
    """
    Owns all gameplay objects.
    update(events) -> None
    draw(surface)  -> None
    is_over        -> bool
    result()       -> dict
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

        self._font_hud = pygame.font.SysFont("Arial", 18, bold=True)

    def _current_speed(self) -> float:
        speed = self.road.speed
        if self.powerup_state.kind == "nitro" and self.powerup_state.active:
            speed *= 1.6
        return speed

    def _scale_difficulty(self):
        self.difficulty = min(10, 1 + int(self.distance / 1500))

    def update(self, events: list):
        if self.is_over:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  self.player.move_left()
                if event.key == pygame.K_RIGHT: self.player.move_right()

        speed = self._current_speed()
        self.distance += speed
        self._scale_difficulty()
        self.road.speed = (BASE_SCROLL_SPEED
                           * DIFFICULTY_SPEED_MULT[self.difficulty_name]
                           * (1 + self.difficulty * 0.05))

        self.road.update()
        self.player.update()
        self.coins.update(speed, self.player.lane)
        self.traffic.update(speed, self.player.lane, self.difficulty)
        self.obstacles.update(speed, self.player.lane, self.difficulty)
        self.powerups.update(speed, self.difficulty)
        self.powerup_state.tick()

        self.coin_count += self.coins.check_collect(self.player.rect)

        if not self.powerup_state.active:
            kind = self.powerups.check_collect(self.player.rect)
            if kind:
                self.powerup_state.activate(kind)
                if kind == "nitro":
                    self.player.nitro = True
                elif kind == "shield":
                    self.player.shield = True

        if self.powerup_state.kind == "nitro" and not self.powerup_state.active:
            self.player.nitro = False

        hit_kind = self.obstacles.check_hit(self.player.rect)
        if hit_kind:
            if hit_kind == "barrier":
                if self.powerup_state.kind == "shield":
                    self.powerup_state.consume_shield()
                    self.player.shield = False
                else:
                    self.is_over = True
            elif hit_kind in ("oil", "pothole"):
                self.road.speed = max(2, self.road.speed * 0.6)

        if self.traffic.check_collision(self.player.rect):
            if self.powerup_state.kind == "shield":
                self.powerup_state.consume_shield()
                self.player.shield = False
                player_r = self.player.rect
                self.traffic.cars = [c for c in self.traffic.cars
                                     if not c.rect.colliderect(player_r)]
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
        score = self.result()["score"]
        dist_m = int(self.distance / 10)
        lines = [
            f"Score:  {score}",
            f"Dist:   {dist_m} m",
            f"Coins:  {self.coin_count}",
            f"Level:  {self.difficulty}",
        ]
        for i, line in enumerate(lines):
            shadow = self._font_hud.render(line, True, BLACK)
            surf   = self._font_hud.render(line, True, WHITE)
            surface.blit(shadow, (11, 11 + i * 22))
            surface.blit(surf,   (10, 10 + i * 22))

        if self.powerup_state.active and self.powerup_state.kind:
            kind = self.powerup_state.kind
            rem_s = self.powerup_state.remaining_ms() / 1000
            pu_text = kind.upper()
            if kind == "nitro":
                pu_text += f" {rem_s:.1f}s"
            elif kind == "shield":
                pu_text += " (shield)"
            pu_surf = self._font_hud.render(pu_text, True, YELLOW)
            surface.blit(pu_surf, (surface.get_width() - pu_surf.get_width() - 10, 10))

    def result(self) -> dict:
        score = calculate_score(self.coin_count, self.distance,
                                self.powerup_state.bonus_pts)
        return {
            "score":    score,
            "distance": int(self.distance / 10),
            "coins":    self.coin_count,
            "bonus":    self.powerup_state.bonus_pts,
        }
