#!/usr/bin/env python3
"""Watches a list of Geometry Dash moderator Twitch channels and notifies
you when one goes live and appears to be running a level-request stream."""

import argparse
import sys
import time

from gd_notifier.config import load_config
from gd_notifier.filters import is_level_request_stream
from gd_notifier.notifier import notify_all
from gd_notifier.state import load_state, save_state
from gd_notifier.twitch import TwitchClient


def check_once(config, client, state):
    moderators = config.get("moderators", [])
    if not moderators:
        print(
            "No moderators configured. Add Twitch usernames to 'moderators' "
            "in your config file."
        )
        return state

    streams = client.get_live_streams(moderators)
    live_ids = {s["id"] for s in streams}

    matching = [
        s
        for s in streams
        if is_level_request_stream(
            s,
            config["level_request_keywords"],
            config["require_gd_category"],
            config["gd_category_name"],
        )
    ]

    notified = set(state.get("notified_stream_ids", []))
    for stream in matching:
        if stream["id"] not in notified:
            notify_all(stream, config)
            notified.add(stream["id"])

    # Drop ids for streams that ended, so a future stream from the same
    # channel notifies again.
    state["notified_stream_ids"] = list(notified & live_ids)
    return state


def main():
    parser = argparse.ArgumentParser(
        description="Notify when GD moderators are live doing level requests."
    )
    parser.add_argument("--config", default="config.json", help="Path to config JSON file")
    parser.add_argument("--once", action="store_true", help="Run a single check and exit")
    parser.add_argument("--interval", type=int, help="Override poll interval in seconds")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.interval:
        config["poll_interval_seconds"] = args.interval

    if not config.get("twitch_client_id") or not config.get("twitch_client_secret"):
        print("Missing Twitch API credentials.")
        print(
            "Set twitch_client_id / twitch_client_secret in your config file, "
            "or the TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET environment variables."
        )
        print("Register a free app at https://dev.twitch.tv/console/apps to get these.")
        sys.exit(1)

    client = TwitchClient(config["twitch_client_id"], config["twitch_client_secret"])
    state = load_state(config["state_file"])

    if args.once:
        state = check_once(config, client, state)
        save_state(config["state_file"], state)
        return

    print(
        f"Watching {len(config.get('moderators', []))} moderator(s) "
        f"every {config['poll_interval_seconds']}s. Ctrl+C to stop."
    )
    try:
        while True:
            state = check_once(config, client, state)
            save_state(config["state_file"], state)
            time.sleep(config["poll_interval_seconds"])
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
