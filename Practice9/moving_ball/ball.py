import pygame

RADIUS = 25
STEP = 20       # pixels per key press
COLOR = (220, 30, 30)   # red


class Ball:
    def __init__(self, x, y, screen_w, screen_h):
        self.x = x
        self.y = y
        self.r = RADIUS
        self.sw = screen_w
        self.sh = screen_h

    def move(self, dx, dy):
        """Move the ball by (dx, dy), ignoring moves that would go off-screen."""
        new_x = self.x + dx
        new_y = self.y + dy
        # Only apply if the new position keeps the ball fully inside
        if self.r <= new_x <= self.sw - self.r:
            self.x = new_x
        if self.r <= new_y <= self.sh - self.r:
            self.y = new_y

    def handle_key(self, key):
        """Map arrow keys to movement deltas."""
        if key == pygame.K_UP:
            self.move(0, -STEP)
        elif key == pygame.K_DOWN:
            self.move(0, STEP)
        elif key == pygame.K_LEFT:
            self.move(-STEP, 0)
        elif key == pygame.K_RIGHT:
            self.move(STEP, 0)

    def draw(self, screen):
        pygame.draw.circle(screen, COLOR, (self.x, self.y), self.r)
