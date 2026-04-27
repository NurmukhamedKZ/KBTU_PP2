# TSIS3/main.py  (smoke test v2 - coins)
import pygame, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from constants import WIDTH, HEIGHT, FPS, RED, WHITE
from racer import Road, Player, CoinManager

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer - coins test")
clock = pygame.time.Clock()
road = Road()
player = Player(RED)
coins = CoinManager()
score = 0
font = pygame.font.SysFont("Arial", 20, bold=True)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  player.move_left()
            if event.key == pygame.K_RIGHT: player.move_right()
    road.update()
    player.update()
    coins.update(road.speed, player.lane)
    score += coins.check_collect(player.rect)
    road.draw(screen)
    coins.draw(screen)
    player.draw(screen)
    label = font.render(f"Coins: {score}", True, WHITE)
    screen.blit(label, (10, 10))
    pygame.display.flip()
    clock.tick(FPS)
