"""
Practice 11 — Racer
Extends Practice 10 with:
  1. Weighted coins (gold=1pt common, silver=3pt uncommon, orange=5pt rare)
  2. Enemy speed increases every SPEED_UP_EVERY coins collected
Controls: LEFT / RIGHT arrows to change lane.
"""

import pygame
import random
import sys

# ── Window ──────────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 600, 700
FPS = 60

# ── Road layout ─────────────────────────────────────────────────────────────────
ROAD_LEFT  = 100
ROAD_RIGHT = 500
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
NUM_LANES  = 3
LANE_WIDTH = ROAD_WIDTH // NUM_LANES
# X-centre of each lane
LANE_CENTERS = [ROAD_LEFT + LANE_WIDTH * i + LANE_WIDTH // 2 for i in range(NUM_LANES)]

# ── Colours ─────────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
GRAY   = ( 80,  80,  80)
DKGRAY = ( 40,  40,  40)
GREEN  = ( 34, 139,  34)
RED    = (200,  30,  30)
BLUE   = ( 30, 100, 200)

# Coin colours keyed by point value
COIN_COLORS = {
    1: (255, 215,   0),   # gold
    3: (192, 192, 192),   # silver
    5: (255, 140,   0),   # dark-orange (rare)
}

# ── Car dimensions ───────────────────────────────────────────────────────────────
CAR_W, CAR_H = 36, 58

# ── Difficulty ───────────────────────────────────────────────────────────────────
BASE_ENEMY_SPEED  = 3.0   # pixels per frame
SPEED_INCREMENT   = 0.6   # added to enemy speed per milestone
SPEED_UP_EVERY    = 10    # coins needed to trigger a speed-up


# ── Coin class ───────────────────────────────────────────────────────────────────
class Coin:
    # Weighted distribution: gold=1 is common, silver=3 medium, orange=5 rare
    VALUES   = [1,  3,  5]
    WEIGHTS  = [60, 30, 10]

    def __init__(self, lane: int, speed: float):
        self.x      = LANE_CENTERS[lane]
        self.y      = -20.0
        self.value  = random.choices(self.VALUES, weights=self.WEIGHTS)[0]
        self.speed  = speed
        self.active = True
        self.radius = 10

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT + 30:
            self.active = False

    @property
    def rect(self) -> pygame.Rect:
        r = self.radius
        return pygame.Rect(self.x - r, int(self.y) - r, r * 2, r * 2)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        color = COIN_COLORS[self.value]
        cx, cy = self.x, int(self.y)
        pygame.draw.circle(surface, color,  (cx, cy), self.radius)
        pygame.draw.circle(surface, WHITE,  (cx, cy), self.radius, 2)
        # Show coin value in centre
        lbl = font.render(str(self.value), True, BLACK)
        surface.blit(lbl, lbl.get_rect(center=(cx, cy)))


# ── Enemy car ────────────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, speed: float):
        self.speed = speed
        self._respawn()

    def _respawn(self):
        self.lane = random.randint(0, NUM_LANES - 1)
        self.x    = float(LANE_CENTERS[self.lane])
        self.y    = float(-CAR_H)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT + CAR_H:
            self._respawn()

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - CAR_W // 2, int(self.y) - CAR_H // 2,
                           CAR_W, CAR_H)

    def draw(self, surface: pygame.Surface):
        r = self.rect
        pygame.draw.rect(surface, BLUE, r, border_radius=6)
        # Rear windshield stripe
        pygame.draw.rect(surface, (180, 220, 255),
                         (r.x + 4, r.bottom - 20, r.width - 8, 12),
                         border_radius=3)


# ── Road background drawing ──────────────────────────────────────────────────────
def draw_road(surface: pygame.Surface, scroll_y: float):
    # Grass on both sides
    surface.fill(GREEN)
    # Road bed
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
    # Dashed lane dividers
    for lane in range(1, NUM_LANES):
        x = ROAD_LEFT + lane * LANE_WIDTH
        y = -scroll_y
        while y < HEIGHT:
            pygame.draw.rect(surface, WHITE, (x - 2, int(y), 4, 30))
            y += 60
    # Solid road edges
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT - 4, 0, 4, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT, 0, 4, HEIGHT))


# ── Player car drawing ───────────────────────────────────────────────────────────
def draw_player(surface: pygame.Surface, x: float, y: float):
    r = pygame.Rect(int(x) - CAR_W // 2, int(y) - CAR_H // 2, CAR_W, CAR_H)
    pygame.draw.rect(surface, RED, r, border_radius=6)
    # Front windshield
    pygame.draw.rect(surface, (180, 220, 255),
                     (r.x + 4, r.y + 8, r.width - 8, 14), border_radius=3)


# ── Main game loop ───────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racer — Practice 11")
    clock = pygame.time.Clock()

    font_hud  = pygame.font.SysFont("Arial", 20, bold=True)
    font_coin = pygame.font.SysFont("Arial", 10, bold=True)
    font_big  = pygame.font.SysFont("Arial", 36, bold=True)

    def reset():
        """Return initial game state as a dict."""
        return dict(
            player_lane=1,
            player_x=float(LANE_CENTERS[1]),
            player_y=float(HEIGHT - 100),
            enemy_speed=BASE_ENEMY_SPEED,
            enemy=Enemy(BASE_ENEMY_SPEED),
            scroll_y=0.0,
            coins=[],
            coin_timer=0,
            total_coins=0,
            speed_milestones=0,   # how many speed-ups have occurred
            game_over=False,
        )

    state = reset()

    running = True
    while running:
        clock.tick(FPS)

        # ── Events ──────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if state["game_over"]:
                    if event.key == pygame.K_r:
                        state = reset()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                else:
                    # Move player left / right between lanes
                    if event.key == pygame.K_LEFT and state["player_lane"] > 0:
                        state["player_lane"] -= 1
                    if event.key == pygame.K_RIGHT and state["player_lane"] < NUM_LANES - 1:
                        state["player_lane"] += 1

        # ── Game-over screen ─────────────────────────────────────────────────────
        if state["game_over"]:
            screen.fill(DKGRAY)
            screen.blit(font_big.render("GAME OVER", True, RED),
                        font_big.render("GAME OVER", True, RED)
                        .get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            screen.blit(font_hud.render(f"Coins collected: {state['total_coins']}", True, WHITE),
                        font_hud.render(f"Coins collected: {state['total_coins']}", True, WHITE)
                        .get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            screen.blit(font_hud.render("R — Retry   ESC — Quit", True, GRAY),
                        font_hud.render("R — Retry   ESC — Quit", True, GRAY)
                        .get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
            pygame.display.flip()
            continue

        # ── Update ──────────────────────────────────────────────────────────────

        es = state["enemy_speed"]

        # Scroll road at enemy speed
        state["scroll_y"] = (state["scroll_y"] + es) % 60

        # Smooth-slide player x toward target lane
        target_x = float(LANE_CENTERS[state["player_lane"]])
        state["player_x"] += (target_x - state["player_x"]) * 0.2

        # Move enemy
        state["enemy"].speed = es
        state["enemy"].update()

        # Spawn a coin every COIN_INTERVAL frames
        state["coin_timer"] += 1
        COIN_INTERVAL = 70
        if state["coin_timer"] >= COIN_INTERVAL:
            state["coin_timer"] = 0
            lane = random.randint(0, NUM_LANES - 1)
            state["coins"].append(Coin(lane, es))

        # Update coins
        for c in state["coins"]:
            c.update()

        # Collect coins that touch the player
        player_rect = pygame.Rect(
            int(state["player_x"]) - CAR_W // 2,
            int(state["player_y"]) - CAR_H // 2,
            CAR_W, CAR_H,
        )
        for c in state["coins"]:
            if c.active and c.rect.colliderect(player_rect):
                state["total_coins"] += c.value
                c.active = False

        # Remove off-screen or collected coins
        state["coins"] = [c for c in state["coins"] if c.active]

        # Speed up enemy every SPEED_UP_EVERY coins
        milestones = state["total_coins"] // SPEED_UP_EVERY
        if milestones > state["speed_milestones"]:
            state["speed_milestones"] = milestones
            state["enemy_speed"] += SPEED_INCREMENT

        # Check player–enemy collision → game over
        if player_rect.colliderect(state["enemy"].rect):
            state["game_over"] = True

        # ── Draw ────────────────────────────────────────────────────────────────

        draw_road(screen, state["scroll_y"])
        state["enemy"].draw(screen)
        for c in state["coins"]:
            c.draw(screen, font_coin)
        draw_player(screen, state["player_x"], state["player_y"])

        # HUD: coins and current enemy speed
        hud = font_hud.render(
            f"Coins: {state['total_coins']}   Enemy speed: {state['enemy_speed']:.1f}",
            True, WHITE,
        )
        screen.blit(hud, (10, 10))

        # Next speed-up threshold
        next_milestone = (state["speed_milestones"] + 1) * SPEED_UP_EVERY
        info = font_hud.render(
            f"Next speed-up at {next_milestone} coins", True, (220, 220, 100),
        )
        screen.blit(info, (10, 34))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
