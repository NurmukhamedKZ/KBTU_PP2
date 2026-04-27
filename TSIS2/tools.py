import pygame
import math
from collections import deque
from enum import Enum, auto


class Tool(Enum):
    PENCIL = auto()
    LINE = auto()
    RECTANGLE = auto()
    CIRCLE = auto()
    SQUARE = auto()
    RIGHT_TRIANGLE = auto()
    EQUILATERAL_TRIANGLE = auto()
    RHOMBUS = auto()
    ERASER = auto()
    FILL = auto()
    TEXT = auto()
    COLOR_PICKER = auto()


def flood_fill(surface, start_x, start_y, fill_color):
    """BFS flood fill using get_at / set_at."""
    width, height = surface.get_size()
    if not (0 <= start_x < width and 0 <= start_y < height):
        return

    target = surface.get_at((start_x, start_y))
    target_rgb = (target.r, target.g, target.b)
    fill_rgb = (fill_color[0], fill_color[1], fill_color[2])

    if target_rgb == fill_rgb:
        return

    surface.lock()
    try:
        queue = deque([(start_x, start_y)])
        visited = {(start_x, start_y)}

        while queue:
            x, y = queue.popleft()
            c = surface.get_at((x, y))
            if (c.r, c.g, c.b) != target_rgb:
                continue
            surface.set_at((x, y), fill_rgb)
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    finally:
        surface.unlock()


def draw_line(surface, color, start, end, width):
    pygame.draw.line(surface, color, start, end, max(1, width))


def draw_rect(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    if rect.width > 0 and rect.height > 0:
        pygame.draw.rect(surface, color, rect, max(1, width))


def draw_circle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    radius = int(math.hypot(x2 - cx, y2 - cy))
    if radius > 0:
        pygame.draw.circle(surface, color, (cx, cy), radius, max(1, width))


def draw_square(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))
    sx = x1 if x2 >= x1 else x1 - side
    sy = y1 if y2 >= y1 else y1 - side
    rect = pygame.Rect(sx, sy, side, side)
    if side > 0:
        pygame.draw.rect(surface, color, rect, max(1, width))


def draw_right_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    pts = [(x1, y1), (x1, y2), (x2, y2)]
    pygame.draw.polygon(surface, color, pts, max(1, width))


def draw_equilateral_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    base = abs(x2 - x1)
    h = int(base * math.sqrt(3) / 2)
    cx = (x1 + x2) // 2
    pts = [(x1, y2), (x2, y2), (cx, y2 - h)]
    pygame.draw.polygon(surface, color, pts, max(1, width))


def draw_rhombus(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
    pygame.draw.polygon(surface, color, pts, max(1, width))
