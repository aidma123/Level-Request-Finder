#!/usr/bin/env python3
"""Watches a list of Geometry Dash moderator Twitch and YouTube channels
and notifies you when one goes live and appears to be running a
level-request stream."""

import argparse
import sys
import time

from gd_notifier.config import load_config
from gd_notifier.filters import is_level_request_stream, title_matches_keywords
from gd_notifier.notifier import notify_all
from gd_notifier.state import load_state, save_state
from gd_notifier.twitch import TwitchClient
from gd_notifier.youtube import YouTubeClient


def _twitch_events(config, twitch_client):
    moderators = config.get("moderators", [])
    if not moderators:
        return [], set()

    streams = twitch_client.get_live_streams(moderators)
    live_ids = {f"twitch:{s['id']}" for s in streams}

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

    events = [
        {
            "id": f"twitch:{s['id']}",
            "platform": "twitch",
            "channel_name": s["user_name"],
            "title": s["title"],
            "url": f"https://twitch.tv/{s['user_login']}",
        }
        for s in matching
    ]
    return events, live_ids


def _youtube_events(config, youtube_client):
    channel_map = config.get("youtube_channels", {})
    if not channel_map:
        return [], set()

    live_streams = youtube_client.get_live_channels(channel_map)
    live_ids = {f"youtube:{s['video_id']}" for s in live_streams}

    matching = [
        s
        for s in live_streams
        if title_matches_keywords(s["title"], config["level_request_keywords"])
    ]

    events = [
        {
            "id": f"youtube:{s['video_id']}",
            "platform": "youtube",
            "channel_name": s["channel_name"],
            "title": s["title"],
            "url": s["url"],
        }
        for s in matching
    ]
    return events, live_ids


def send_test_notification(config):
    """Fire a fake event through the real notification code path (console,
    desktop, Discord) without touching Twitch/YouTube, so the delivery
    pipeline can be tested on demand."""
    event = {
        "platform": "twitch",
        "channel_name": "TestModerator",
        "title": "[TEST] Sending Levels! Come get your level rated - LR stream",
        "url": "https://twitch.tv/example",
    }
    notify_all(event, config)


def check_once(config, twitch_client, youtube_client, state):
    if not config.get("moderators") and not config.get("youtube_channels"):
        print(
            "No channels configured. Add Twitch usernames to 'moderators' and/or "
            "YouTube channel IDs to 'youtube_channels' in your config file."
        )
        return state

    twitch_events, twitch_live_ids = _twitch_events(config, twitch_client)
    youtube_events, youtube_live_ids = _youtube_events(config, youtube_client)
    all_events = twitch_events + youtube_events
    all_live_ids = twitch_live_ids | youtube_live_ids

    notified = set(state.get("notified_ids", []))
    for event in all_events:
        if event["id"] not in notified:
            notify_all(event, config)
            notified.add(event["id"])

    # Drop ids for streams that ended, so a future stream from the same
    # channel notifies again.
    state["notified_ids"] = list(notified & all_live_ids)
    return state


def main():
    parser = argparse.ArgumentParser(
        description="Notify when GD moderators are live doing level requests."
    )
    parser.add_argument("--config", default="config.json", help="Path to config JSON file")
    parser.add_argument("--once", action="store_true", help="Run a single check and exit")
    parser.add_argument("--interval", type=int, help="Override poll interval in seconds")
    parser.add_argument(
        "--test-notify",
        action="store_true",
        help="Send a fake notification through console/desktop/Discord and exit, to test delivery",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if args.interval:
        config["poll_interval_seconds"] = args.interval

    if args.test_notify:
        send_test_notification(config)
        return

    moderators = config.get("moderators", [])
    youtube_channels = config.get("youtube_channels", {})

    if moderators and (
        not config.get("twitch_client_id") or not config.get("twitch_client_secret")
    ):
        print("Missing Twitch API credentials.")
        print(
            "Set twitch_client_id / twitch_client_secret in your config file, "
            "or the TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET environment variables."
        )
        print("Register a free app at https://dev.twitch.tv/console/apps to get these.")
        sys.exit(1)

    twitch_client = TwitchClient(config.get("twitch_client_id"), config.get("twitch_client_secret"))
    youtube_client = YouTubeClient()
    state = load_state(config["state_file"])

    if args.once:
        state = check_once(config, twitch_client, youtube_client, state)
        save_state(config["state_file"], state)
        return

    print(
        f"Watching {len(moderators)} Twitch channel(s) and {len(youtube_channels)} "
        f"YouTube channel(s) every {config['poll_interval_seconds']}s. Ctrl+C to stop."
    )
    try:
        while True:
            state = check_once(config, twitch_client, youtube_client, state)
            save_state(config["state_file"], state)
            time.sleep(config["poll_interval_seconds"])
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
