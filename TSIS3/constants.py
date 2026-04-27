# TSIS3/constants.py
import pygame

# Screen
WIDTH, HEIGHT = 480, 700
FPS = 60

# Road
ROAD_LEFT = 60
ROAD_RIGHT = 420
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
NUM_LANES = 4
LANE_WIDTH = ROAD_WIDTH // NUM_LANES

def lane_center(lane: int) -> int:
    """Return x-centre of lane 0..3."""
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2

LANE_CENTERS = [lane_center(i) for i in range(NUM_LANES)]

# Colours
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (100, 100, 100)
DARK_GRAY  = (50,  50,  50)
RED        = (220, 50,  50)
GREEN      = (50,  200, 50)
BLUE       = (50,  100, 220)
YELLOW     = (240, 200, 0)
ORANGE     = (230, 130, 0)
CYAN       = (0,   220, 220)
ROAD_COLOR = (60,  60,  60)
STRIPE_COLOR = (240, 240, 0)
GRASS_COLOR  = (40, 120, 40)
SKY_COLOR    = (100, 180, 240)

# Player
PLAYER_WIDTH  = 36
PLAYER_HEIGHT = 60
PLAYER_Y      = HEIGHT - 120
PLAYER_SPEED  = 6          # pixels per frame for lane-switch slide

# Road scroll
BASE_SCROLL_SPEED = 4      # pixels per frame at difficulty 1
STRIPE_HEIGHT     = 40
STRIPE_GAP        = 40

# Coins
COIN_RADIUS = 10
COIN_WEIGHTS = {1: 50, 3: 30, 5: 20}   # value: weight
COIN_SPAWN_INTERVAL = 90   # frames

# Traffic
TRAFFIC_WIDTH  = 34
TRAFFIC_HEIGHT = 56
TRAFFIC_COLORS = [RED, BLUE, ORANGE, CYAN, (180, 60, 180)]
BASE_TRAFFIC_INTERVAL = 120   # frames between spawns at difficulty 1

# Obstacles
OBSTACLE_WIDTH  = 40
OBSTACLE_HEIGHT = 24
OBSTACLE_TYPES  = ["oil", "pothole", "barrier"]
BASE_OBSTACLE_INTERVAL = 150

# Power-ups
POWERUP_SIZE     = 32
POWERUP_TIMEOUT  = 8000   # ms before disappearing if not collected
NITRO_DURATION   = 4000   # ms
SHIELD_DURATION  = 999999 # until hit
REPAIR_DURATION  = 0      # instant

# Scoring
DISTANCE_SCORE_RATE = 1    # points per 100 px scrolled
COIN_BONUS_MULTIPLIER = 10

# Difficulty
DIFFICULTY_STEP_DISTANCE = 1500  # px scrolled before next level
MAX_DIFFICULTY = 10

# States
STATE_MENU        = "menu"
STATE_USERNAME    = "username"
STATE_GAME        = "game"
STATE_GAMEOVER    = "gameover"
STATE_LEADERBOARD = "leaderboard"
STATE_SETTINGS    = "settings"

# Default settings
DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "red",
    "difficulty": "normal",   # easy / normal / hard
}

CAR_COLOR_MAP = {
    "red":    RED,
    "blue":   BLUE,
    "green":  GREEN,
    "yellow": YELLOW,
}

DIFFICULTY_SPEED_MULT = {
    "easy":   0.7,
    "normal": 1.0,
    "hard":   1.4,
}
