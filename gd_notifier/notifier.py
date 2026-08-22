"""Notification backends: console, desktop popup, and Discord webhook.

All notify_* functions take a normalized "event" dict:
{"platform": "twitch"|"youtube", "channel_name": str, "title": str, "url": str}
"""

import requests


def notify_console(event):
    platform = event["platform"].capitalize()
    print(
        f'[LIVE - {platform}] {event["channel_name"]} is doing level requests! '
        f'"{event["title"]}" -> {event["url"]}'
    )


def notify_desktop(event):
    try:
        from plyer import notification
    except ImportError:
        print("plyer is not installed; skipping desktop notification (pip install plyer)")
        return

    try:
        notification.notify(
            title=f'{event["channel_name"]} is live - GD Level Requests!',
            message=event.get("title", ""),
            app_name="GD Level Request Notifier",
            timeout=15,
        )
    except Exception as e:  # desktop notification backends vary by OS
        print(f"Failed to send desktop notification: {e}")


def notify_discord(webhook_url, event):
    if not webhook_url:
        return
    content = (
        f'@everyone 🟢 **{event["channel_name"]}** is live on {event["platform"].capitalize()} '
        f'doing level requests!\n'
        f'**{event["title"]}**\n'
        f'{event["url"]}'
    )
    payload = {
        "content": content,
        "allowed_mentions": {"parse": ["everyone"]},
    }
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except requests.RequestException as e:
        print(f"Failed to send Discord notification: {e}")


def notify_ntfy(ntfy_url, event):
    if not ntfy_url:
        return
    body = f'{event["title"]}\n{event["url"]}'.encode("utf-8")
    headers = {
        "Title": f'{event["channel_name"]} is live - GD Level Requests!',
        "Click": event["url"],
        "Tags": "loudspeaker",
    }
    try:
        requests.post(ntfy_url, data=body, headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"Failed to send ntfy notification: {e}")


def notify_all(event, config):
    notif_cfg = config.get("notifications", {})
    if notif_cfg.get("console", True):
        notify_console(event)
    if notif_cfg.get("desktop", False):
        notify_desktop(event)
    webhook = notif_cfg.get("discord_webhook_url")
    if webhook:
        notify_discord(webhook, event)
    ntfy_url = notif_cfg.get("ntfy_url")
    if ntfy_url:
        notify_ntfy(ntfy_url, event)
