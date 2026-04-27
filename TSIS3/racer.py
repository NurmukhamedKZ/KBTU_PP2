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
