"""Configuration loading for the GD level-request stream notifier."""

import json
import os

DEFAULTS = {
    "poll_interval_seconds": 60,
    "moderators": [],
    "youtube_channels": {},
    "level_request_keywords": [
        "level request",
        "lvl request",
        "level req",
        "lr stream",
        "req stream",
        "sending levels",
        "send your level",
        "send levels",
        " lr ",
    ],
    "require_gd_category": True,
    "gd_category_name": "Geometry Dash",
    "notifications": {
        "desktop": True,
        "console": True,
        "discord_webhook_url": "",
    },
    "state_file": "state.json",
}


def load_config(path):
    """Load config from a JSON file, layered over defaults, with env var overrides
    for Twitch credentials so secrets don't need to live in the file."""
    config = json.loads(json.dumps(DEFAULTS))  # deep copy

    if os.path.exists(path):
        with open(path, "r") as f:
            user_config = json.load(f)
        for key, value in user_config.items():
            if isinstance(value, dict) and isinstance(config.get(key), dict):
                config[key].update(value)
            else:
                config[key] = value

    config["twitch_client_id"] = os.environ.get(
        "TWITCH_CLIENT_ID", config.get("twitch_client_id", "")
    )
    config["twitch_client_secret"] = os.environ.get(
        "TWITCH_CLIENT_SECRET", config.get("twitch_client_secret", "")
    )
    return config
