# TSIS3/main.py
import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from constants import (
    WIDTH, HEIGHT, FPS,
    STATE_MENU, STATE_USERNAME, STATE_GAME, STATE_GAMEOVER,
    STATE_LEADERBOARD, STATE_SETTINGS,
    CAR_COLOR_MAP, RED,
)
from racer import Game
import ui
import persistence


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racer")
    clock = pygame.time.Clock()

    settings = persistence.load_settings()

    state = STATE_MENU
    username = ""
    username_input = ""
    username_error = False
    game = None
    last_result = {}

    while True:
        mouse_pos = pygame.mouse.get_pos()
        events    = pygame.event.get()

        clicked = False
        for event in events:
            if event.type == pygame.QUIT:
                persistence.save_settings(settings)
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True

        # ── MENU ──────────────────────────────────────────────────────────────
        if state == STATE_MENU:
            buttons = ui.draw_menu(screen, mouse_pos)
            if clicked:
                if buttons["play"].collidepoint(mouse_pos):
                    username_input = ""
                    username_error = False
                    state = STATE_USERNAME
                elif buttons["leaderboard"].collidepoint(mouse_pos):
                    state = STATE_LEADERBOARD
                elif buttons["settings"].collidepoint(mouse_pos):
                    state = STATE_SETTINGS
                elif buttons["quit"].collidepoint(mouse_pos):
                    persistence.save_settings(settings)
                    pygame.quit()
                    sys.exit()

        # ── USERNAME ──────────────────────────────────────────────────────────
        elif state == STATE_USERNAME:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if username_input.strip():
                            username = username_input.strip()
                            car_color = CAR_COLOR_MAP.get(settings["car_color"], RED)
                            game = Game(car_color=car_color,
                                        difficulty_name=settings["difficulty"])
                            state = STATE_GAME
                        else:
                            username_error = True
                    elif event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    elif len(username_input) < 16 and event.unicode.isprintable():
                        username_input += event.unicode
            ui.draw_username(screen, username_input, username_error)

        # ── GAME ──────────────────────────────────────────────────────────────
        elif state == STATE_GAME:
            game.update(events)
            game.draw(screen)
            if game.is_over:
                last_result = game.result()
                last_result["name"] = username
                persistence.add_entry(last_result)
                state = STATE_GAMEOVER

        # ── GAME OVER ─────────────────────────────────────────────────────────
        elif state == STATE_GAMEOVER:
            buttons = ui.draw_gameover(screen, last_result, mouse_pos)
            if clicked:
                if buttons["retry"].collidepoint(mouse_pos):
                    car_color = CAR_COLOR_MAP.get(settings["car_color"], RED)
                    game = Game(car_color=car_color,
                                difficulty_name=settings["difficulty"])
                    state = STATE_GAME
                elif buttons["menu"].collidepoint(mouse_pos):
                    state = STATE_MENU

        # ── LEADERBOARD ───────────────────────────────────────────────────────
        elif state == STATE_LEADERBOARD:
            entries = persistence.load_leaderboard()
            buttons = ui.draw_leaderboard(screen, entries, mouse_pos)
            if clicked and buttons["back"].collidepoint(mouse_pos):
                state = STATE_MENU

        # ── SETTINGS ──────────────────────────────────────────────────────────
        elif state == STATE_SETTINGS:
            buttons = ui.draw_settings(screen, settings, mouse_pos)
            if clicked:
                if buttons["sound"].collidepoint(mouse_pos):
                    settings["sound"] = not settings["sound"]
                for cname in CAR_COLOR_MAP:
                    key = f"color_{cname}"
                    if key in buttons and buttons[key].collidepoint(mouse_pos):
                        settings["car_color"] = cname
                for d in ["easy", "normal", "hard"]:
                    key = f"diff_{d}"
                    if key in buttons and buttons[key].collidepoint(mouse_pos):
                        settings["difficulty"] = d
                if buttons["back"].collidepoint(mouse_pos):
                    persistence.save_settings(settings)
                    state = STATE_MENU

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
