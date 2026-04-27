# TSIS3/main.py  (smoke test v3 - traffic)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED, WHITE
from racer import Road, Player, CoinManager, TrafficManager

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer - traffic test")
clock = pygame.time.Clock()
road = Road()
player = Player(RED)
coins = CoinManager()
traffic = TrafficManager()
score = 0
alive = True
font = pygame.font.SysFont("Arial", 20, bold=True)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  player.move_left()
            if event.key == pygame.K_RIGHT: player.move_right()
    if alive:
        road.update()
        player.update()
        coins.update(road.speed, player.lane)
        traffic.update(road.speed, player.lane, 1)
        score += coins.check_collect(player.rect)
        if traffic.check_collision(player.rect):
            alive = False
    road.draw(screen)
    coins.draw(screen)
    traffic.draw(screen)
    player.draw(screen)
    label = font.render(f"Score: {score}" if alive else "CRASH!", True, WHITE if alive else RED)
    screen.blit(label, (10, 10))
    pygame.display.flip()
    clock.tick(FPS)
