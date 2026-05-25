"""Configuration module for SpeedMeter."""
import json
import os
from typing import Any, Dict, Optional

try:
    from platformdirs import user_config_dir, user_cache_dir, user_log_dir
    HAS_PLATFORMDIRS = True
except ImportError:
    HAS_PLATFORMDIRS = False


__version__ = "1.0.0"


def get_app_dirs():
    """Get standard OS directory paths for config, cache, and logs."""
    if HAS_PLATFORMDIRS:
        return {
            "config_dir": user_config_dir("speedmeter", ensure_exists=True),
            "cache_dir": user_cache_dir("speedmeter", ensure_exists=True),
            "log_dir": user_log_dir("speedmeter", ensure_exists=True),
        }
    # Fallback
    home = os.path.expanduser("~")
    return {
        "config_dir": os.path.join(home, ".config", "speedmeter"),
        "cache_dir": os.path.join(home, ".cache", "speedmeter"),
        "log_dir": os.path.join(home, ".local", "share", "speedmeter", "logs"),
    }


def get_default_config() -> Dict[str, Any]:
    """Return the default configuration dictionary."""
    dirs = get_app_dirs()
    return {
        "app": {
            "refresh_interval": 5,           # seconds between auto-refresh
            "theme": "auto",                 # auto, dark, light
            "history_size": 50,              # max results stored
            "chart_points": 30,              # points in live chart
            "timeout": 30,                   # speed test timeout in seconds
        },
        "paths": {
            "config_dir": dirs["config_dir"],
            "cache_dir": dirs["cache_dir"],
            "log_dir": dirs["log_dir"],
            "history_file": os.path.join(dirs["cache_dir"], "history.json"),
            "config_file": os.path.join(dirs["config_dir"], "config.json"),
        },
        "units": {
            "speed": "Mbps",                 # Mbps, MB/s
            "precision": 2,                  # decimal places
        },
        "notifications": {
            "enabled": True,
            "threshold_download": None,      # alert if below this Mbps
            "threshold_upload": None,        # alert if below this Mbps
        },
    }


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """Load config from a JSON file, merging with defaults."""
    config = get_default_config()

    if path and os.path.isfile(path):
        with open(path, "r") as f:
            user_config = json.load(f)
        _deep_merge(config, user_config)
    else:
        # Try loading from default config path
        config_path = config["paths"]["config_file"]
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r") as f:
                    user_config = json.load(f)
                _deep_merge(config, user_config)
            except (json.JSONDecodeError, IOError):
                pass

    return config


def save_config(config: Dict[str, Any], path: Optional[str] = None) -> bool:
    """Save configuration to a JSON file."""
    if path is None:
        path = config.get("paths", {}).get("config_file")
        if not path:
            return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False


def _deep_merge(base: Dict, override: Dict) -> None:
    """Recursively merge override dict into base dict."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value