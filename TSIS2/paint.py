"""
TSIS 2 — Paint Application
Features: pencil, line, rect, circle, square, right-triangle,
          equilateral-triangle, rhombus, eraser, flood-fill,
          text tool, colour picker, 3 brush sizes, Ctrl+S save.
"""

import pygame
import sys
import math
from datetime import datetime

from tools import (
    Tool, flood_fill,
    draw_line, draw_rect, draw_circle, draw_square,
    draw_right_triangle, draw_equilateral_triangle, draw_rhombus,
)

# ── Layout ─────────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 1280, 800
TOOLBAR_W    = 165
PALETTE_H    = 58

CANVAS_X = TOOLBAR_W
CANVAS_Y = 0
CANVAS_W = WIN_W - TOOLBAR_W
CANVAS_H = WIN_H - PALETTE_H

# ── Colours ────────────────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GRAY       = (180, 180, 180)
DARK_GRAY  = ( 80,  80,  80)
LIGHT_GRAY = (235, 235, 235)
ACCENT     = ( 70, 130, 180)   # selected-tool highlight
ACCENT_TXT = (255, 255, 255)

PALETTE = [
    (  0,   0,   0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255,   0,   0), (139,   0,   0), (255, 165,   0), (255, 215,   0),
    (  0, 255,   0), (  0, 100,   0), (  0, 255, 255), (  0, 128, 128),
    (  0,   0, 255), (  0,   0, 139), (148,   0, 211), (255,  20, 147),
    (139,  69,  19), (210, 180, 140), (255, 192, 203), ( 50, 205,  50),
]

BRUSH_SIZES = [2, 5, 10]

# (Tool, display-label, keyboard-shortcut-char)
TOOLS_META = [
    (Tool.PENCIL,               "Pencil",       "P"),
    (Tool.LINE,                 "Line",         "L"),
    (Tool.RECTANGLE,            "Rectangle",    "R"),
    (Tool.CIRCLE,               "Circle",       "C"),
    (Tool.SQUARE,               "Square",       "Q"),
    (Tool.RIGHT_TRIANGLE,       "R.Triangle",   "T"),
    (Tool.EQUILATERAL_TRIANGLE, "Eq.Triangle",  "E"),
    (Tool.RHOMBUS,              "Rhombus",      "D"),
    (Tool.ERASER,               "Eraser",       "X"),
    (Tool.FILL,                 "Fill",         "F"),
    (Tool.TEXT,                 "Text",         "W"),
    (Tool.COLOR_PICKER,         "Picker",       "I"),
]

SHAPE_FUNCS = {
    Tool.LINE:                 draw_line,
    Tool.RECTANGLE:            draw_rect,
    Tool.CIRCLE:               draw_circle,
    Tool.SQUARE:               draw_square,
    Tool.RIGHT_TRIANGLE:       draw_right_triangle,
    Tool.EQUILATERAL_TRIANGLE: draw_equilateral_triangle,
    Tool.RHOMBUS:              draw_rhombus,
}

KEY_TO_TOOL = {
    pygame.K_p: Tool.PENCIL,
    pygame.K_l: Tool.LINE,
    pygame.K_r: Tool.RECTANGLE,
    pygame.K_c: Tool.CIRCLE,
    pygame.K_q: Tool.SQUARE,
    pygame.K_t: Tool.RIGHT_TRIANGLE,
    pygame.K_e: Tool.EQUILATERAL_TRIANGLE,
    pygame.K_d: Tool.RHOMBUS,
    pygame.K_x: Tool.ERASER,
    pygame.K_f: Tool.FILL,
    pygame.K_w: Tool.TEXT,
    pygame.K_i: Tool.COLOR_PICKER,
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def to_canvas(screen_pos):
    return (screen_pos[0] - CANVAS_X, screen_pos[1] - CANVAS_Y)


def clamp_to_canvas(screen_pos):
    x = max(CANVAS_X, min(CANVAS_X + CANVAS_W - 1, screen_pos[0]))
    y = max(CANVAS_Y, min(CANVAS_Y + CANVAS_H - 1, screen_pos[1]))
    return to_canvas((x, y))


def in_canvas(screen_pos):
    x, y = screen_pos
    return CANVAS_X <= x < CANVAS_X + CANVAS_W and CANVAS_Y <= y < CANVAS_Y + CANVAS_H


def save_canvas(canvas):
    fname = datetime.now().strftime("canvas_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, fname)
    return fname


def draw_button(screen, rect, label, selected, font):
    bg = ACCENT if selected else WHITE
    fg = ACCENT_TXT if selected else DARK_GRAY
    pygame.draw.rect(screen, bg, rect, border_radius=4)
    pygame.draw.rect(screen, GRAY, rect, 1, border_radius=4)
    txt = font.render(label, True, fg)
    tx = rect.x + (rect.width - txt.get_width()) // 2
    ty = rect.y + (rect.height - txt.get_height()) // 2
    screen.blit(txt, (tx, ty))


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint — TSIS 2")
    clock = pygame.time.Clock()

    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(WHITE)

    font_sm  = pygame.font.SysFont("Arial", 12)
    font_btn = pygame.font.SysFont("Arial", 13)
    font_txt = pygame.font.SysFont("Arial", 20)

    # ── State ──────────────────────────────────────────────────────────────────
    tool        = Tool.PENCIL
    color       = BLACK
    brush_idx   = 0
    brush_size  = BRUSH_SIZES[brush_idx]

    drawing     = False
    draw_start  = None   # canvas-space start of current shape drag
    prev_pos    = None   # previous canvas-space point for pencil/eraser
    snapshot    = None   # canvas copy taken on mouse-down for live preview

    text_active = False
    text_pos    = (0, 0)
    text_buf    = ""

    save_msg       = ""
    save_msg_timer = 0   # ms remaining to show message

    # ── Build button rects ─────────────────────────────────────────────────────
    # Tool buttons (left toolbar)
    BTN_H = 30
    BTN_GAP = 4
    tool_rects = {}
    by = 8
    for t, label, key in TOOLS_META:
        r = pygame.Rect(5, by, TOOLBAR_W - 10, BTN_H)
        tool_rects[t] = (r, label, key)
        by += BTN_H + BTN_GAP

    # Brush-size buttons
    sz_y = by + 14
    sz_rects = []
    sz_w = (TOOLBAR_W - 10) // 3
    for i, lbl in enumerate(["S(1)", "M(2)", "L(3)"]):
        r = pygame.Rect(5 + i * sz_w, sz_y, sz_w - 3, 26)
        sz_rects.append((r, lbl, i))

    # Colour palette (bottom strip, canvas-wide)
    SWATCH = 26
    GAP    = 2
    pal_rects = []
    px = TOOLBAR_W + 5
    py = WIN_H - PALETTE_H + (PALETTE_H - SWATCH) // 2
    for c in PALETTE:
        pal_rects.append((pygame.Rect(px, py, SWATCH, SWATCH), c))
        px += SWATCH + GAP

    # Current-colour preview in toolbar bottom-left area
    cur_swatch = pygame.Rect(5, WIN_H - PALETTE_H + (PALETTE_H - 40) // 2, 40, 40)

    # ── Event loop ─────────────────────────────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(60)
        if save_msg_timer > 0:
            save_msg_timer -= dt

        for event in pygame.event.get():

            # ── Quit ──────────────────────────────────────────────────────────
            if event.type == pygame.QUIT:
                running = False

            # ── Key down ──────────────────────────────────────────────────────
            elif event.type == pygame.KEYDOWN:

                if text_active:
                    if event.key == pygame.K_RETURN:
                        surf = font_txt.render(text_buf, True, color)
                        canvas.blit(surf, text_pos)
                        text_active = False
                        text_buf = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buf = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buf = text_buf[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        text_buf += event.unicode

                else:
                    mods = pygame.key.get_mods()
                    if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                        fname = save_canvas(canvas)
                        save_msg = f"Saved: {fname}"
                        save_msg_timer = 3000
                    elif event.key in KEY_TO_TOOL:
                        tool = KEY_TO_TOOL[event.key]
                    elif event.key == pygame.K_1:
                        brush_idx = 0; brush_size = BRUSH_SIZES[0]
                    elif event.key == pygame.K_2:
                        brush_idx = 1; brush_size = BRUSH_SIZES[1]
                    elif event.key == pygame.K_3:
                        brush_idx = 2; brush_size = BRUSH_SIZES[2]

            # ── Mouse button down ──────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                clicked_ui = False

                # Tool buttons
                for t, (rect, *_) in tool_rects.items():
                    if rect.collidepoint(mx, my):
                        tool = t
                        text_active = False
                        clicked_ui = True
                        break

                # Brush-size buttons
                if not clicked_ui:
                    for r, _, idx in sz_rects:
                        if r.collidepoint(mx, my):
                            brush_idx = idx
                            brush_size = BRUSH_SIZES[idx]
                            clicked_ui = True
                            break

                # Palette swatches
                if not clicked_ui:
                    for r, c in pal_rects:
                        if r.collidepoint(mx, my):
                            color = c
                            clicked_ui = True
                            break

                # Canvas actions
                if not clicked_ui and in_canvas(event.pos):
                    cp = to_canvas(event.pos)

                    if tool == Tool.FILL:
                        flood_fill(canvas, cp[0], cp[1], color)

                    elif tool == Tool.COLOR_PICKER:
                        picked = canvas.get_at(cp)
                        color = (picked.r, picked.g, picked.b)

                    elif tool == Tool.TEXT:
                        text_pos = cp
                        text_active = True
                        text_buf = ""

                    elif tool in (Tool.PENCIL, Tool.ERASER):
                        drawing = True
                        prev_pos = cp

                    elif tool in SHAPE_FUNCS:
                        drawing = True
                        draw_start = cp
                        snapshot = canvas.copy()

            # ── Mouse motion ───────────────────────────────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                if not drawing:
                    continue
                cp = clamp_to_canvas(event.pos)

                if tool == Tool.PENCIL and prev_pos is not None:
                    if in_canvas(event.pos):
                        pygame.draw.line(canvas, color, prev_pos, cp, brush_size)
                        prev_pos = cp

                elif tool == Tool.ERASER and prev_pos is not None:
                    if in_canvas(event.pos):
                        r = brush_size * 4
                        pygame.draw.circle(canvas, WHITE, cp, r)
                        pygame.draw.circle(canvas, color, cp, r, 1)
                        prev_pos = cp

                elif tool in SHAPE_FUNCS and snapshot is not None:
                    canvas.blit(snapshot, (0, 0))
                    SHAPE_FUNCS[tool](canvas, color, draw_start, cp, brush_size)

            # ── Mouse button up ────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing:
                    cp = clamp_to_canvas(event.pos)
                    if tool in SHAPE_FUNCS and snapshot is not None:
                        canvas.blit(snapshot, (0, 0))
                        SHAPE_FUNCS[tool](canvas, color, draw_start, cp, brush_size)
                    drawing  = False
                    snapshot = None
                    draw_start = None
                    prev_pos   = None

        # ── Render ────────────────────────────────────────────────────────────
        screen.fill(GRAY)

        # Toolbar background
        pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, TOOLBAR_W, WIN_H))
        pygame.draw.line(screen, GRAY, (TOOLBAR_W, 0), (TOOLBAR_W, WIN_H), 2)

        # Tool buttons
        for t, (rect, label, key) in tool_rects.items():
            draw_button(screen, rect, f"{key}: {label}", t == tool, font_btn)

        # Brush-size section
        lbl_surf = font_sm.render("Brush size:", True, DARK_GRAY)
        screen.blit(lbl_surf, (5, sz_y - 14))
        for r, lbl, idx in sz_rects:
            draw_button(screen, r, lbl, idx == brush_idx, font_sm)

        # Canvas
        screen.blit(canvas, (CANVAS_X, CANVAS_Y))
        pygame.draw.rect(screen, DARK_GRAY,
                         (CANVAS_X - 1, CANVAS_Y - 1, CANVAS_W + 2, CANVAS_H + 2), 1)

        # Live text preview (drawn on screen, not canvas)
        if text_active:
            preview_surf = font_txt.render(text_buf + "|", True, color)
            screen.blit(preview_surf, (CANVAS_X + text_pos[0], CANVAS_Y + text_pos[1]))

        # Eraser cursor preview
        if tool == Tool.ERASER:
            mx, my = pygame.mouse.get_pos()
            if in_canvas((mx, my)):
                r = brush_size * 4
                pygame.draw.circle(screen, DARK_GRAY, (mx, my), r, 1)

        # Palette strip
        pygame.draw.rect(screen, LIGHT_GRAY, (0, WIN_H - PALETTE_H, WIN_W, PALETTE_H))
        pygame.draw.line(screen, GRAY, (0, WIN_H - PALETTE_H), (WIN_W, WIN_H - PALETTE_H), 1)

        # Current colour swatch (toolbar side)
        pygame.draw.rect(screen, color, cur_swatch)
        pygame.draw.rect(screen, DARK_GRAY, cur_swatch, 2)

        # Palette swatches
        for r, c in pal_rects:
            pygame.draw.rect(screen, c, r)
            if c == color:
                pygame.draw.rect(screen, DARK_GRAY, r, 3)
            else:
                pygame.draw.rect(screen, DARK_GRAY, r, 1)

        # Save notification
        if save_msg_timer > 0:
            msg_surf = font_btn.render(save_msg, True, (0, 120, 0))
            screen.blit(msg_surf, (TOOLBAR_W + 10, WIN_H - PALETTE_H + 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
