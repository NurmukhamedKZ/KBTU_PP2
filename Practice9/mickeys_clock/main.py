import pygame
import sys
import datetime
from clock import Clock

# --- constants ---
WIDTH, HEIGHT = 600, 600
FPS = 10          # update frequently enough to catch each new second
CENTER = (WIDTH // 2, HEIGHT // 2)
RADIUS = 220

# Colors
BG_COLOR = (20, 20, 40)
TEXT_COLOR = (255, 255, 200)


def load_hand(path, size):
    """Load and scale a hand image; fall back to a simple surface if missing."""
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        return img
    except Exception:
        # Fallback: draw a plain rectangle hand
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((220, 50, 50, 200))
        return surf


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey's Clock")
    clock_tick = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 36, bold=True)

    # Load Mickey's face as background image
    try:
        bg_img = pygame.image.load("images/mickeyclock.jpeg").convert()
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    except Exception:
        bg_img = None

    # Hand images (right=minutes, left=seconds)
    # Using the same source image scaled differently to distinguish them
    hand_right = load_hand("images/mickeyclock.jpeg", (40, int(RADIUS * 0.7)))
    hand_left  = load_hand("images/mickeyclock.jpeg", (30, int(RADIUS * 0.8)))

    game_clock = Clock(screen, CENTER, RADIUS)

    last_second = -1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

        # Draw background
        if bg_img:
            screen.blit(bg_img, (0, 0))
            # Semi-transparent overlay so clock is readable
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(BG_COLOR)

        # Draw clock (hands + face)
        game_clock.draw(hand_right, hand_left)

        # Display digital time (MM:SS)
        now = datetime.datetime.now()
        time_str = now.strftime("%M:%S")
        text_surf = font.render(time_str, True, TEXT_COLOR)
        screen.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

        pygame.display.flip()
        clock_tick.tick(FPS)


if __name__ == "__main__":
    main()
