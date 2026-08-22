"""Notification backends: console, desktop popup, and Discord webhook."""

import requests


def notify_console(stream):
    print(
        f'[LIVE] {stream["user_name"]} is doing level requests! '
        f'"{stream["title"]}" -> https://twitch.tv/{stream["user_login"]}'
    )


def notify_desktop(stream):
    try:
        from plyer import notification
    except ImportError:
        print("plyer is not installed; skipping desktop notification (pip install plyer)")
        return

    try:
        notification.notify(
            title=f'{stream["user_name"]} is live - GD Level Requests!',
            message=stream.get("title", ""),
            app_name="GD Level Request Notifier",
            timeout=15,
        )
    except Exception as e:  # desktop notification backends vary by OS
        print(f"Failed to send desktop notification: {e}")


def notify_discord(webhook_url, stream):
    if not webhook_url:
        return
    content = (
        f'🟢 **{stream["user_name"]}** is live doing level requests!\n'
        f'**{stream["title"]}**\n'
        f'https://twitch.tv/{stream["user_login"]}'
    )
    try:
        requests.post(webhook_url, json={"content": content}, timeout=10)
    except requests.RequestException as e:
        print(f"Failed to send Discord notification: {e}")


def notify_all(stream, config):
    notif_cfg = config.get("notifications", {})
    if notif_cfg.get("console", True):
        notify_console(stream)
    if notif_cfg.get("desktop", False):
        notify_desktop(stream)
    webhook = notif_cfg.get("discord_webhook_url")
    if webhook:
        notify_discord(webhook, stream)
