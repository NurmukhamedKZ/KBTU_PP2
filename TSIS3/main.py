# TSIS3/main.py  (smoke test v1)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED, WHITE
from racer import Road, Player

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer - smoke test")
clock = pygame.time.Clock()
road = Road()
player = Player(RED)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  player.move_left()
            if event.key == pygame.K_RIGHT: player.move_right()
    road.update()
    player.update()
    road.draw(screen)
    player.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
