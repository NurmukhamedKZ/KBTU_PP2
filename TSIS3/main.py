# TSIS3/main.py  (smoke test v4 - Game class)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED, WHITE
from racer import Game

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer - Game class test")
clock = pygame.time.Clock()
game = Game(car_color=RED, difficulty_name="normal")

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
    game.update(events)
    game.draw(screen)
    if game.is_over:
        font = pygame.font.SysFont("Arial", 40, bold=True)
        label = font.render("GAME OVER", True, RED)
        screen.blit(label, label.get_rect(center=(WIDTH//2, HEIGHT//2)))
    pygame.display.flip()
    clock.tick(FPS)
