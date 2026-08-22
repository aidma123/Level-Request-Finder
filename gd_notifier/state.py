"""Persisted state so we don't re-notify for a stream we already caught."""

import json
import os

DEFAULT_STATE = {"notified_stream_ids": []}


def load_state(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return dict(DEFAULT_STATE)


def save_state(path, state):
    with open(path, "w") as f:
        json.dump(state, f, indent=2)
