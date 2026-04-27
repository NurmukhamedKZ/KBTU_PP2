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
