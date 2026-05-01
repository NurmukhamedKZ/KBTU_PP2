"""
Practice 11 — Snake
Extends Practice 10 with:
  1. Food with different weights (normal=10pts, bonus=25pts)
  2. Bonus food disappears after a timer (5 seconds)
Controls: Arrow keys to change direction. R to restart.
"""

import pygame
import random
import sys

# ── Grid dimensions ──────────────────────────────────────────────────────────────
CELL     = 20           # pixel size of one grid cell
COLS     = 30           # number of columns
ROWS     = 25           # number of rows
HEADER_H = 50           # HUD height in pixels

WIN_W = COLS * CELL
WIN_H = ROWS * CELL + HEADER_H

# ── Colours ─────────────────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREEN = ( 20, 100,  20)
SNAKE_CLR  = ( 50, 200,  50)
SNAKE_HEAD = ( 30, 160,  30)
WALL_CLR   = ( 60,  60,  60)
BG_CLR     = ( 15,  15,  15)
RED        = (200,  40,  40)
GOLD       = (255, 215,   0)
GRAY       = (150, 150, 150)
DKGRAY     = ( 30,  30,  30)

# ── Directions ───────────────────────────────────────────────────────────────────
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)
# Opposite directions (cannot reverse directly)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# ── Food timing ──────────────────────────────────────────────────────────────────
BONUS_LIFETIME_MS = 5_000   # bonus food disappears after 5 s

# ── Gameplay constants ───────────────────────────────────────────────────────────
FOOD_PER_LEVEL = 5          # scoring foods eaten before advancing a level
BASE_SPEED     = 8          # moves per second at level 1
SPEED_STEP     = 2          # extra moves/s per level

# ── Food types ───────────────────────────────────────────────────────────────────
FOOD_NORMAL = "normal"   # always present, does not expire, worth 10 pts
FOOD_BONUS  = "bonus"    # spawns with 25 % chance, worth 25 pts, disappears in 5 s


class FoodItem:
    """A single food piece with a kind, position, and optional expiry."""

    # Point values per food type
    POINTS = {FOOD_NORMAL: 10, FOOD_BONUS: 25}

    def __init__(self, pos: tuple, kind: str):
        self.pos        = pos
        self.kind       = kind
        self.spawn_time = pygame.time.get_ticks()
        # Only bonus food expires; normal food stays forever
        self.lifetime   = BONUS_LIFETIME_MS if kind == FOOD_BONUS else None

    def is_expired(self) -> bool:
        """Returns True when a timed food has exceeded its lifetime."""
        if self.lifetime is None:
            return False
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

    def time_left_s(self) -> float | None:
        """Seconds remaining before expiry (None for normal food)."""
        if self.lifetime is None:
            return None
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, (self.lifetime - elapsed) / 1000)

    @property
    def points(self) -> int:
        return self.POINTS[self.kind]


class Game:
    """All game state and logic for the Snake game."""

    def __init__(self):
        self.reset()

    def reset(self):
        # Start snake in the middle of the grid, moving right
        cx, cy = COLS // 2, ROWS // 2
        self.body       = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction  = RIGHT
        self.next_dir   = RIGHT

        self.score      = 0
        self.level      = 1
        self.foods_eaten = 0   # counts scoring foods for level progression

        self.foods: list[FoodItem] = []
        self._spawn_food()

    # ── Helpers ──────────────────────────────────────────────────────────────────

    def _occupied(self) -> set:
        """All grid cells blocked by snake body and existing food."""
        occupied = set(self.body)
        occupied |= {f.pos for f in self.foods}
        return occupied

    def _random_free_cell(self) -> tuple | None:
        """Pick a random cell not occupied by the snake or existing food."""
        occ  = self._occupied()
        free = [
            (x, y)
            for x in range(COLS)
            for y in range(ROWS)
            if (x, y) not in occ
        ]
        return random.choice(free) if free else None

    def _spawn_food(self):
        """Ensure exactly 1 normal food exists; maybe add a bonus food."""
        # Keep exactly one normal food on the grid
        if not any(f.kind == FOOD_NORMAL for f in self.foods):
            pos = self._random_free_cell()
            if pos:
                self.foods.append(FoodItem(pos, FOOD_NORMAL))

        # 25 % chance to spawn a bonus food if none currently visible
        if not any(f.kind == FOOD_BONUS for f in self.foods):
            if random.random() < 0.25:
                pos = self._random_free_cell()
                if pos:
                    self.foods.append(FoodItem(pos, FOOD_BONUS))

    # ── Per-frame update ─────────────────────────────────────────────────────────

    def set_direction(self, new_dir: tuple):
        """Queue a direction change; ignore reversal into self."""
        if new_dir != OPPOSITE.get(self.direction):
            self.next_dir = new_dir

    def step(self) -> bool:
        """
        Advance the snake by one cell.
        Returns False if the move results in a collision (game over).
        """
        self.direction = self.next_dir
        hx, hy = self.body[0]
        dx, dy  = self.direction
        new_head = (hx + dx, hy + dy)

        # Wall collision
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            return False

        # Self collision
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)

        # Check if any food is eaten
        ate_food = False
        for food in self.foods:
            if food.pos == new_head:
                self.score      += food.points
                self.foods_eaten += 1
                self.foods.remove(food)
                ate_food = True
                break

        if not ate_food:
            self.body.pop()   # no growth when no food eaten

        # Remove expired bonus food
        self.foods = [f for f in self.foods if not f.is_expired()]

        # Respawn food as needed
        self._spawn_food()

        # Advance level every FOOD_PER_LEVEL scoring foods eaten
        new_level = self.foods_eaten // FOOD_PER_LEVEL + 1
        if new_level > self.level:
            self.level = new_level

        return True

    @property
    def move_speed(self) -> int:
        """Moves per second at the current level."""
        return BASE_SPEED + (self.level - 1) * SPEED_STEP


# ── Drawing helpers ──────────────────────────────────────────────────────────────

def cell_rect(col: int, row: int) -> pygame.Rect:
    """Return the screen Rect for a grid cell (accounting for header)."""
    return pygame.Rect(col * CELL, HEADER_H + row * CELL, CELL, CELL)


def draw_game(surface: pygame.Surface, game: Game, font: pygame.font.Font):
    # Background
    surface.fill(BG_CLR)

    # Grid cells (faint lines)
    for x in range(0, WIN_W, CELL):
        pygame.draw.line(surface, (25, 25, 25), (x, HEADER_H), (x, WIN_H))
    for y in range(HEADER_H, WIN_H, CELL):
        pygame.draw.line(surface, (25, 25, 25), (0, y), (WIN_W, y))

    # Snake body
    for i, (cx, cy) in enumerate(game.body):
        r = cell_rect(cx, cy).inflate(-2, -2)
        color = SNAKE_HEAD if i == 0 else SNAKE_CLR
        pygame.draw.rect(surface, color, r, border_radius=4)

    # Food items
    for food in game.foods:
        r = cell_rect(*food.pos).inflate(-4, -4)
        color = GOLD if food.kind == FOOD_BONUS else RED

        pygame.draw.ellipse(surface, color, r)

        # Show remaining time for bonus food
        if food.kind == FOOD_BONUS:
            t = food.time_left_s()
            if t is not None:
                lbl = font.render(f"{t:.1f}", True, WHITE)
                surface.blit(lbl, (r.x, r.y - 14))

    # HUD bar at top
    pygame.draw.rect(surface, DKGRAY, (0, 0, WIN_W, HEADER_H))
    hud = font.render(
        f"Score: {game.score}   Level: {game.level}   Speed: {game.move_speed} mv/s",
        True, WHITE,
    )
    surface.blit(hud, (10, (HEADER_H - hud.get_height()) // 2))

    # Legend: food colours
    legend = font.render("Red=10pt   Gold=25pt (5s)", True, GRAY)
    surface.blit(legend, (WIN_W - legend.get_width() - 10,
                           (HEADER_H - legend.get_height()) // 2))


# ── Main ─────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snake — Practice 11")
    clock = pygame.time.Clock()

    font     = pygame.font.SysFont("Arial", 16, bold=True)
    font_big = pygame.font.SysFont("Arial", 36, bold=True)

    game         = Game()
    game_over    = False
    # Track elapsed time to control move speed
    last_move_ms = pygame.time.get_ticks()

    while True:
        clock.tick(60)
        now = pygame.time.get_ticks()

        # ── Events ──────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        game      = Game()
                        game_over = False
                        last_move_ms = pygame.time.get_ticks()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP:
                        game.set_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        game.set_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        game.set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        game.set_direction(RIGHT)

        # ── Game-over screen ─────────────────────────────────────────────────────
        if game_over:
            screen.fill(BLACK)
            screen.blit(font_big.render("GAME OVER", True, RED),
                        font_big.render("GAME OVER", True, RED)
                        .get_rect(center=(WIN_W // 2, WIN_H // 2 - 60)))
            screen.blit(font.render(f"Score: {game.score}   Level: {game.level}", True, WHITE),
                        font.render(f"Score: {game.score}   Level: {game.level}", True, WHITE)
                        .get_rect(center=(WIN_W // 2, WIN_H // 2)))
            screen.blit(font.render("R — Restart   ESC — Quit", True, GRAY),
                        font.render("R — Restart   ESC — Quit", True, GRAY)
                        .get_rect(center=(WIN_W // 2, WIN_H // 2 + 50)))
            pygame.display.flip()
            continue

        # ── Step snake at current move speed ────────────────────────────────────
        ms_per_move = 1000 // game.move_speed
        if now - last_move_ms >= ms_per_move:
            last_move_ms = now
            alive = game.step()
            if not alive:
                game_over = True

        # ── Draw ────────────────────────────────────────────────────────────────
        draw_game(screen, game, font)
        pygame.display.flip()


if __name__ == "__main__":
    main()
