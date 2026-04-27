# TSIS3/scoring.py
from constants import COIN_BONUS_MULTIPLIER, DISTANCE_SCORE_RATE

def calculate_score(coins: int, distance: float, powerup_bonus: int) -> int:
    coin_pts     = coins * COIN_BONUS_MULTIPLIER
    distance_pts = int(distance / 100) * DISTANCE_SCORE_RATE
    return coin_pts + distance_pts + powerup_bonus
