import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".autoclicker"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILES_DIR = CONFIG_DIR / "profiles"

DEFAULT_CONFIG = {
    "cps": 10,
    "interval_min_ms": 80,
    "interval_max_ms": 120,
    "click_mode": "left",
    "hold_duration_ms": 50,
    "circle_x": 960,
    "circle_y": 540,
    "circle_radius": 50,
    "overlay_visible": True,
    "hotkey_start_stop": "F6",
    "hotkey_toggle_overlay": "F7",
    "hotkey_emergency_stop": "F8",
    "human_mode": False,
    "human_intensity": 50,
    "timer_mode": "continuous",
    "countdown_seconds": 60,
    "delay_start_seconds": 0,
    "window_x": None,
    "window_y": None,
    "last_profile": "default",
    "position_jitter_px": 5,
    "micro_pause_chance": 0.02,
    "micro_pause_min_ms": 100,
    "micro_pause_max_ms": 500,
}


class ConfigManager:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self._config = dict(DEFAULT_CONFIG)
        self.load()

    def load(self, profile_name=None):
        path = self._profile_path(profile_name) if profile_name else CONFIG_FILE
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._config.update(saved)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self, profile_name=None):
        path = self._profile_path(profile_name) if profile_name else CONFIG_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value

    def update(self, data):
        self._config.update(data)

    def to_dict(self):
        return dict(self._config)

    def reset(self):
        self._config = dict(DEFAULT_CONFIG)

    def list_profiles(self):
        profiles = []
        for p in PROFILES_DIR.glob("*.json"):
            profiles.append(p.stem)
        if "default" not in profiles:
            profiles.insert(0, "default")
        return sorted(profiles)

    def save_profile(self, name):
        self.save(profile_name=name)

    def load_profile(self, name):
        self.reset()
        self.load(profile_name=name)

    def delete_profile(self, name):
        path = self._profile_path(name)
        if path.exists():
            path.unlink()

    @staticmethod
    def _profile_path(name):
        safe = "".join(c for c in name if c.isalnum() or c in "_- ")
        return PROFILES_DIR / f"{safe}.json"
