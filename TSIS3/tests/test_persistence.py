# TSIS3/tests/test_persistence.py
import json, os, sys, tempfile, pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import persistence as P

# ---- leaderboard ----

def test_load_leaderboard_returns_empty_list_when_file_missing(tmp_path):
    path = tmp_path / "lb.json"
    result = P.load_leaderboard(str(path))
    assert result == []

def test_save_and_load_leaderboard_round_trips(tmp_path):
    path = tmp_path / "lb.json"
    entries = [{"name": "Alice", "score": 500, "distance": 1200, "coins": 10}]
    P.save_leaderboard(entries, str(path))
    loaded = P.load_leaderboard(str(path))
    assert loaded == entries

def test_leaderboard_kept_sorted_and_truncated(tmp_path):
    path = tmp_path / "lb.json"
    entries = [{"name": f"P{i}", "score": i * 10, "distance": i * 100, "coins": i} for i in range(15)]
    P.save_leaderboard(entries, str(path))
    loaded = P.load_leaderboard(str(path))
    assert len(loaded) == 10
    assert loaded[0]["score"] >= loaded[-1]["score"]

def test_add_entry_inserts_and_keeps_top10(tmp_path):
    path = tmp_path / "lb.json"
    for i in range(10):
        P.add_entry({"name": f"P{i}", "score": i * 10, "distance": 100, "coins": 1}, str(path))
    P.add_entry({"name": "Winner", "score": 999, "distance": 9000, "coins": 99}, str(path))
    loaded = P.load_leaderboard(str(path))
    assert len(loaded) == 10
    assert loaded[0]["name"] == "Winner"

# ---- settings ----

def test_load_settings_returns_defaults_when_missing(tmp_path):
    path = tmp_path / "settings.json"
    result = P.load_settings(str(path))
    assert result["sound"] is True
    assert result["car_color"] == "red"
    assert result["difficulty"] == "normal"

def test_save_and_load_settings_round_trips(tmp_path):
    path = tmp_path / "settings.json"
    s = {"sound": False, "car_color": "blue", "difficulty": "hard"}
    P.save_settings(s, str(path))
    loaded = P.load_settings(str(path))
    assert loaded == s

def test_load_settings_fills_missing_keys_with_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"sound": False}))
    loaded = P.load_settings(str(path))
    assert loaded["car_color"] == "red"
    assert loaded["difficulty"] == "normal"
    assert loaded["sound"] is False
