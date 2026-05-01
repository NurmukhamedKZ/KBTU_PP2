"""
Practice 11 — Paint
Extends Practice 10 (Rectangle, Circle, Eraser, Color picker) with:
  1. Square
  2. Right triangle
  3. Equilateral triangle
  4. Rhombus
Keyboard shortcuts: R=rect, C=circle, Q=square, T=right-tri,
                    E=eq-tri, D=rhombus, X=eraser, I=color-picker
Click-drag on canvas to draw each shape. Right-click canvas to pick colour.
"""

import pygame
import math
import sys

# ── Window layout ────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 1100, 700
TOOLBAR_W    = 160
PALETTE_H    = 60
CANVAS_X     = TOOLBAR_W
CANVAS_Y     = 0
CANVAS_W     = WIN_W - TOOLBAR_W
CANVAS_H     = WIN_H - PALETTE_H

# ── Colours ─────────────────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GRAY       = (180, 180, 180)
DARK_GRAY  = ( 70,  70,  70)
ACCENT     = ( 60, 120, 200)   # selected-tool highlight
ACCENT_TXT = (255, 255, 255)

# Colour palette shown at the bottom
PALETTE = [
    (  0,   0,   0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255,   0,   0), (200,   0,   0), (255, 165,   0), (255, 215,   0),
    (  0, 200,   0), (  0, 100,   0), (  0, 200, 200), (  0, 128, 128),
    (  0,   0, 255), (  0,   0, 139), (148,   0, 211), (255,  20, 147),
    (139,  69,  19), (210, 180, 140), (255, 192, 203), ( 50, 205,  50),
]

# Brush (outline) thickness
BRUSH = 2

# ── Tool names ───────────────────────────────────────────────────────────────────
TOOLS = [
    ("Rectangle",     "R"),
    ("Circle",        "C"),
    ("Square",        "Q"),   # NEW in Practice 11
    ("R.Triangle",    "T"),   # NEW in Practice 11
    ("Eq.Triangle",   "E"),   # NEW in Practice 11
    ("Rhombus",       "D"),   # NEW in Practice 11
    ("Eraser",        "X"),
    ("Picker",        "I"),
]

KEY_MAP = {
    pygame.K_r: "Rectangle",
    pygame.K_c: "Circle",
    pygame.K_q: "Square",
    pygame.K_t: "R.Triangle",
    pygame.K_e: "Eq.Triangle",
    pygame.K_d: "Rhombus",
    pygame.K_x: "Eraser",
    pygame.K_i: "Picker",
}


# ── Shape drawing functions ──────────────────────────────────────────────────────

def draw_rectangle(surface, color, start, end):
    x1, y1 = start
    x2, y2 = end
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    if rect.width > 0 and rect.height > 0:
        pygame.draw.rect(surface, color, rect, BRUSH)


def draw_circle(surface, color, start, end):
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    radius = int(math.hypot(x2 - cx, y2 - cy))
    if radius > 0:
        pygame.draw.circle(surface, color, (cx, cy), radius, BRUSH)


def draw_square(surface, color, start, end):
    """Square: the shorter of width/height is used for both sides."""
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))
    # Anchor at top-left, respecting drag direction
    sx = x1 if x2 >= x1 else x1 - side
    sy = y1 if y2 >= y1 else y1 - side
    if side > 0:
        pygame.draw.rect(surface, color, pygame.Rect(sx, sy, side, side), BRUSH)


def draw_right_triangle(surface, color, start, end):
    """Right triangle with the right angle at the bottom-left."""
    x1, y1 = start
    x2, y2 = end
    pts = [(x1, y1), (x1, y2), (x2, y2)]
    pygame.draw.polygon(surface, color, pts, BRUSH)


def draw_equilateral_triangle(surface, color, start, end):
    """Equilateral triangle: base is the horizontal distance between start/end."""
    x1, y1 = start
    x2, y2 = end
    base = abs(x2 - x1)
    height = int(base * math.sqrt(3) / 2)
    cx = (x1 + x2) // 2
    pts = [(x1, y2), (x2, y2), (cx, y2 - height)]
    if base > 0:
        pygame.draw.polygon(surface, color, pts, BRUSH)


def draw_rhombus(surface, color, start, end):
    """Rhombus (diamond) with vertices at the midpoints of the bounding box."""
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
    pygame.draw.polygon(surface, color, pts, BRUSH)


# Map tool name → drawing function
SHAPE_FUNCS = {
    "Rectangle":   draw_rectangle,
    "Circle":      draw_circle,
    "Square":      draw_square,
    "R.Triangle":  draw_right_triangle,
    "Eq.Triangle": draw_equilateral_triangle,
    "Rhombus":     draw_rhombus,
}


# ── Coordinate helpers ───────────────────────────────────────────────────────────

def to_canvas(screen_pos):
    """Convert screen position to canvas-local position."""
    return (screen_pos[0] - CANVAS_X, screen_pos[1] - CANVAS_Y)


def in_canvas(screen_pos):
    x, y = screen_pos
    return CANVAS_X <= x < CANVAS_X + CANVAS_W and CANVAS_Y <= y < CANVAS_Y + CANVAS_H


# ── Toolbar / palette helpers ────────────────────────────────────────────────────

def draw_button(screen, rect, label, selected, font):
    """Draw a single toolbar button."""
    bg = ACCENT if selected else WHITE
    fg = ACCENT_TXT if selected else DARK_GRAY
    pygame.draw.rect(screen, bg, rect, border_radius=4)
    pygame.draw.rect(screen, GRAY, rect, 1, border_radius=4)
    txt = font.render(label, True, fg)
    screen.blit(txt, txt.get_rect(center=rect.center))


def draw_toolbar(screen, current_tool, color, font):
    """Draw the left sidebar with tool buttons and current colour preview."""
    pygame.draw.rect(screen, (235, 235, 235), (0, 0, TOOLBAR_W, WIN_H))

    # Tool buttons
    for i, (name, key) in enumerate(TOOLS):
        rect = pygame.Rect(8, 10 + i * 40, TOOLBAR_W - 16, 34)
        draw_button(screen, rect, f"{name} ({key})", name == current_tool, font)

    # Current colour swatch
    swatch_y = 10 + len(TOOLS) * 40 + 10
    pygame.draw.rect(screen, BLACK, (8, swatch_y, TOOLBAR_W - 16, 34), 1)
    pygame.draw.rect(screen, color, (9, swatch_y + 1, TOOLBAR_W - 18, 32))
    lbl = font.render("Colour", True, DARK_GRAY)
    screen.blit(lbl, (8, swatch_y + 38))


def draw_palette(screen, font):
    """Draw the colour palette strip at the bottom."""
    pygame.draw.rect(screen, (220, 220, 220), (CANVAS_X, WIN_H - PALETTE_H, CANVAS_W, PALETTE_H))
    swatch_size = 36
    margin      = 6
    x = CANVAS_X + margin
    y = WIN_H - PALETTE_H + (PALETTE_H - swatch_size) // 2
    for c in PALETTE:
        r = pygame.Rect(x, y, swatch_size, swatch_size)
        pygame.draw.rect(screen, c, r)
        pygame.draw.rect(screen, BLACK, r, 1)
        x += swatch_size + margin


def palette_color_at(screen_pos) -> tuple | None:
    """Return the palette colour under screen_pos, or None if not on palette."""
    mx, my = screen_pos
    if not (CANVAS_X <= mx < WIN_W and WIN_H - PALETTE_H <= my < WIN_H):
        return None
    swatch_size = 36
    margin      = 6
    x_start     = CANVAS_X + margin
    for i, c in enumerate(PALETTE):
        x1 = x_start + i * (swatch_size + margin)
        x2 = x1 + swatch_size
        if x1 <= mx < x2:
            return c
    return None


# ── Main ─────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint — Practice 11")
    clock  = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 13)

    # White drawing canvas
    canvas   = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(WHITE)

    # Current state
    tool     = "Rectangle"
    color    = BLACK
    drawing  = False
    start    = None   # canvas-local drag start
    snapshot = None   # canvas copy taken at mouse-down for live preview

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Keyboard: switch tool ────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    tool = KEY_MAP[event.key]

            # ── Mouse button down ────────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Left click on palette → change colour
                pc = palette_color_at(mouse_pos)
                if pc is not None:
                    color = pc

                # Left click on toolbar → change tool
                elif mouse_pos[0] < TOOLBAR_W:
                    for i, (name, _) in enumerate(TOOLS):
                        rect = pygame.Rect(8, 10 + i * 40, TOOLBAR_W - 16, 34)
                        if rect.collidepoint(mouse_pos):
                            tool = name

                # Left click on canvas → start drawing
                elif in_canvas(mouse_pos) and event.button == 1:
                    drawing  = True
                    start    = to_canvas(mouse_pos)
                    snapshot = canvas.copy()   # save canvas so preview doesn't stack

                # Right-click on canvas → pick colour from canvas
                elif in_canvas(mouse_pos) and event.button == 3:
                    cx, cy = to_canvas(mouse_pos)
                    color  = canvas.get_at((cx, cy))[:3]

            # ── Mouse button up → commit the shape ───────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
                drawing = False
                if start is not None:
                    end_pos = to_canvas(mouse_pos)
                    if tool == "Eraser":
                        pygame.draw.circle(canvas, WHITE, end_pos, 15)
                    elif tool == "Picker":
                        ex, ey = end_pos
                        ex = max(0, min(CANVAS_W - 1, ex))
                        ey = max(0, min(CANVAS_H - 1, ey))
                        color = canvas.get_at((ex, ey))[:3]
                    elif tool in SHAPE_FUNCS:
                        # Commit to the real canvas
                        canvas.blit(snapshot, (0, 0))
                        SHAPE_FUNCS[tool](canvas, color, start, end_pos)
                start    = None
                snapshot = None

        # ── Eraser drags continuously ─────────────────────────────────────────────
        if drawing and tool == "Eraser" and in_canvas(mouse_pos):
            pygame.draw.circle(canvas, WHITE, to_canvas(mouse_pos), 15)

        # ── Live shape preview while dragging ────────────────────────────────────
        preview = canvas.copy()
        if drawing and snapshot is not None and start is not None:
            if tool in SHAPE_FUNCS:
                preview.blit(snapshot, (0, 0))
                SHAPE_FUNCS[tool](preview, color, start, to_canvas(mouse_pos))

        # ── Render ───────────────────────────────────────────────────────────────
        screen.fill(GRAY)
        screen.blit(preview, (CANVAS_X, CANVAS_Y))
        draw_toolbar(screen, tool, color, font)
        draw_palette(screen, font)

        # Divider between toolbar and canvas
        pygame.draw.rect(screen, DARK_GRAY, (TOOLBAR_W, 0, 1, WIN_H - PALETTE_H))

        pygame.display.flip()


if __name__ == "__main__":
    main()
