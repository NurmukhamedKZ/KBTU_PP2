import pygame
import os


class MusicPlayer:
    def __init__(self, music_dir="music"):
        pygame.mixer.init()
        self.music_dir = music_dir
        self.playlist = self._load_playlist()
        self.index = 0       # current track index
        self.playing = False

    def _load_playlist(self):
        """Collect all mp3/wav files from the music directory."""
        supported = (".mp3", ".wav", ".ogg")
        if not os.path.isdir(self.music_dir):
            return []
        files = [
            os.path.join(self.music_dir, f)
            for f in sorted(os.listdir(self.music_dir))
            if f.lower().endswith(supported)
        ]
        return files

    def current_track_name(self):
        """Return display name of the current track."""
        if not self.playlist:
            return "No tracks found"
        return os.path.basename(self.playlist[self.index])

    def play(self):
        """Start or resume playing current track."""
        if not self.playlist:
            return
        pygame.mixer.music.load(self.playlist[self.index])
        pygame.mixer.music.play()
        self.playing = True

    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.playing = False

    def next_track(self):
        """Advance to next track."""
        if not self.playlist:
            return
        self.index = (self.index + 1) % len(self.playlist)
        self.play()

    def prev_track(self):
        """Go back to previous track."""
        if not self.playlist:
            return
        self.index = (self.index - 1) % len(self.playlist)
        self.play()

    def get_position_sec(self):
        """Return playback position in seconds."""
        if self.playing:
            return pygame.mixer.music.get_pos() // 1000
        return 0
