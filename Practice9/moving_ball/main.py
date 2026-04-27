import pygame
import sys
from ball import Ball

# --- constants ---
WIDTH, HEIGHT = 600, 600
FPS = 60
BG_COLOR = (255, 255, 255)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    # Start ball in the center
    ball = Ball(WIDTH // 2, HEIGHT // 2, WIDTH, HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                # Delegate arrow-key handling to ball
                ball.handle_key(event.key)

        # Clear screen
        screen.fill(BG_COLOR)

        # Draw ball
        ball.draw(screen)

        # Show position hint
        hint = font.render(f"({ball.x}, {ball.y})  Arrow keys to move  |  Q to quit", True, (100, 100, 100))
        screen.blit(hint, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
