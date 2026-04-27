# TSIS3/persistence.py
import json
import os
from constants import DEFAULT_SETTINGS

_LB_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")
_ST_FILE = os.path.join(os.path.dirname(__file__), "settings.json")


def load_leaderboard(path: str = _LB_FILE) -> list[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data, key=lambda e: e["score"], reverse=True)[:10]
    except (json.JSONDecodeError, KeyError):
        return []


def save_leaderboard(entries: list[dict], path: str = _LB_FILE) -> None:
    sorted_entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:10]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted_entries, f, indent=2)


def add_entry(entry: dict, path: str = _LB_FILE) -> None:
    entries = load_leaderboard(path)
    entries.append(entry)
    save_leaderboard(entries, path)


def load_settings(path: str = _ST_FILE) -> dict:
    defaults = dict(DEFAULT_SETTINGS)
    if not os.path.exists(path):
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        defaults.update(data)
        return defaults
    except (json.JSONDecodeError, KeyError):
        return defaults


def save_settings(settings: dict, path: str = _ST_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
