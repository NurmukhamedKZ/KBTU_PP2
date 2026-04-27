# TSIS3/tests/test_scoring.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scoring import calculate_score

def test_zero_state_gives_zero():
    assert calculate_score(coins=0, distance=0, powerup_bonus=0) == 0

def test_coins_contribute():
    assert calculate_score(coins=5, distance=0, powerup_bonus=0) == 50

def test_distance_contributes():
    # 1 point per 100 px
    assert calculate_score(coins=0, distance=1000, powerup_bonus=0) == 10

def test_powerup_bonus_contributes():
    assert calculate_score(coins=0, distance=0, powerup_bonus=200) == 200

def test_combined():
    # coins=3 -> 30, distance=500 -> 5, bonus=100 -> 100  => 135
    assert calculate_score(coins=3, distance=500, powerup_bonus=100) == 135
