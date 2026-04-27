import pygame
import sys
from player import MusicPlayer

# --- constants ---
WIDTH, HEIGHT = 500, 340
FPS = 30

BG      = (15, 15, 30)
ACCENT  = (80, 200, 120)
WHITE   = (240, 240, 240)
GRAY    = (120, 120, 140)
DARK    = (30, 30, 50)


def draw_ui(screen, player, fonts):
    """Render the full player UI each frame."""
    screen.fill(BG)
    title_f, track_f, info_f = fonts

    # Title bar
    pygame.draw.rect(screen, DARK, (0, 0, WIDTH, 60))
    title = title_f.render("Music Player", True, ACCENT)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 30)))

    # Track info
    track_name = player.current_track_name()
    track_surf = track_f.render(track_name, True, WHITE)
    screen.blit(track_surf, track_surf.get_rect(center=(WIDTH // 2, 120)))

    # Status + position
    status = "PLAYING" if player.playing else "STOPPED"
    pos = player.get_position_sec()
    status_surf = info_f.render(f"{status}  |  {pos}s", True, GRAY)
    screen.blit(status_surf, status_surf.get_rect(center=(WIDTH // 2, 170)))

    # Playlist index
    total = len(player.playlist)
    idx_text = f"Track {player.index + 1} / {total}" if total else "No tracks"
    idx_surf = info_f.render(idx_text, True, GRAY)
    screen.blit(idx_surf, idx_surf.get_rect(center=(WIDTH // 2, 200)))

    # Controls legend
    controls = [
        ("[P] Play", ACCENT),
        ("[S] Stop", (200, 80, 80)),
        ("[N] Next", WHITE),
        ("[B] Prev", WHITE),
        ("[Q] Quit", GRAY),
    ]
    x = 30
    for label, color in controls:
        surf = info_f.render(label, True, color)
        screen.blit(surf, (x, 270))
        x += surf.get_width() + 20

    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player")
    fps_clock = pygame.time.Clock()

    fonts = (
        pygame.font.SysFont("Arial", 28, bold=True),   # title
        pygame.font.SysFont("Arial", 20),               # track name
        pygame.font.SysFont("Arial", 16),               # info / controls
    )

    player = MusicPlayer(music_dir="music")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()

        draw_ui(screen, player, fonts)
        fps_clock.tick(FPS)


if __name__ == "__main__":
    main()
