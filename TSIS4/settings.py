import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULTS = {
    "snake_color": [0, 200, 0],
    "grid_overlay": False,
    "sound": True,
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for key, val in DEFAULTS.items():
            data.setdefault(key, val)
        return data
    return dict(DEFAULTS)


def save_settings(settings: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
