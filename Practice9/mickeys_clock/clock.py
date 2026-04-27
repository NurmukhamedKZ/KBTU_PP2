import pygame
import math
import datetime


class Clock:
    def __init__(self, screen, center, radius):
        self.screen = screen
        self.center = center  # (x, y) center of clock face
        self.radius = radius

    def get_time(self):
        """Return current (minutes, seconds)."""
        now = datetime.datetime.now()
        return now.minute, now.second

    def _hand_endpoint(self, angle_deg, length):
        """Calculate endpoint of a hand given its angle (0=up, clockwise)."""
        angle_rad = math.radians(angle_deg - 90)
        x = self.center[0] + length * math.cos(angle_rad)
        y = self.center[1] + length * math.sin(angle_rad)
        return (int(x), int(y))

    def draw_face(self):
        """Draw the clock circle and tick marks."""
        pygame.draw.circle(self.screen, (255, 255, 255), self.center, self.radius, 3)
        # Draw 60 tick marks
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            inner = self.radius - (10 if i % 5 == 0 else 5)
            x1 = self.center[0] + self.radius * math.cos(angle)
            y1 = self.center[1] + self.radius * math.sin(angle)
            x2 = self.center[0] + inner * math.cos(angle)
            y2 = self.center[1] + inner * math.sin(angle)
            width = 2 if i % 5 == 0 else 1
            pygame.draw.line(self.screen, (255, 255, 255), (int(x1), int(y1)), (int(x2), int(y2)), width)

    def draw_hand(self, value, total, length, color, width):
        """Draw a single clock hand based on value/total fraction."""
        angle = (value / total) * 360
        endpoint = self._hand_endpoint(angle, length)
        pygame.draw.line(self.screen, color, self.center, endpoint, width)
        pygame.draw.circle(self.screen, color, self.center, width // 2 + 2)

    def draw(self, hand_img_right, hand_img_left):
        """Draw clock face and both hands using Mickey hand images."""
        minutes, seconds = self.get_time()

        self.draw_face()

        # Minute hand (right hand image) — full rotation in 60 min
        min_angle = (minutes / 60) * 360
        self._draw_image_hand(hand_img_right, min_angle, self.radius * 0.75)

        # Second hand (left hand image) — full rotation in 60 sec
        sec_angle = (seconds / 60) * 360
        self._draw_image_hand(hand_img_left, sec_angle, self.radius * 0.85)

        # Center dot
        pygame.draw.circle(self.screen, (255, 255, 0), self.center, 6)

    def _draw_image_hand(self, image, angle_deg, length):
        """Rotate image and blit it so its base sits at clock center."""
        rotated = pygame.transform.rotate(image, -angle_deg)
        # Offset from center along the hand direction so tip points outward
        angle_rad = math.radians(angle_deg - 90)
        offset_x = (length / 2) * math.cos(angle_rad)
        offset_y = (length / 2) * math.sin(angle_rad)
        rect = rotated.get_rect(center=(
            self.center[0] + int(offset_x),
            self.center[1] + int(offset_y)
        ))
        self.screen.blit(rotated, rect)
