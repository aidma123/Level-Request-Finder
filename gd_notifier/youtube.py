"""Lightweight YouTube live-stream detection.

Uses YouTube's internal "innertube" browse API (the same anonymous AJAX
call the web client itself makes to render a channel's "Live" tab) instead
of the official Data API, since that API's free quota (10,000 units/day,
~100 units per live-check call) can't support polling more than a handful
of channels on anything shorter than a very long interval.

An earlier version of this fetched the channel's public HTML /live page
directly and parsed it for a live marker. That was scrapped after testing
showed YouTube serves a "Sign in to confirm you're not a bot" wall
(playabilityStatus: LOGIN_REQUIRED) for that HTML endpoint when requests
come from a datacenter/cloud IP, even with realistic browser headers. The
innertube browse endpoint below is not gated the same way, since it's the
same request path used by every anonymous pageview, but it still depends
on YouTube's internal response shape rather than a stable, versioned
public API — if YouTube changes it, this may need updating.
"""

import requests

BROWSE_URL = "https://www.youtube.com/youtubei/v1/browse"

# Public API key embedded in every anonymous YouTube pageview's client JS.
# This is what the web client itself uses to call innertube endpoints; it's
# not a scraped secret and carries no special privileges.
API_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"

# Opaque protobuf "params" value selecting a channel's "Live" tab, as sent
# by the real web client when you open a channel's Live tab.
LIVE_TAB_PARAMS = "EgdzdHJlYW1z8gYECgJ6AA%3D%3D"

_CLIENT_CONTEXT = {
    "client": {"clientName": "WEB", "clientVersion": "2.20240101.00.00"}
}


def _iter_rich_items(obj):
    """Walk the browse response looking for richItemRenderer nodes, which
    wrap each video/stream tile in the channel's Live tab grid."""
    if isinstance(obj, dict):
        if "richItemRenderer" in obj:
            yield obj["richItemRenderer"]
        for value in obj.values():
            yield from _iter_rich_items(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _iter_rich_items(value)


def _is_live_lockup(lockup):
    overlays = (
        lockup.get("contentImage", {})
        .get("thumbnailViewModel", {})
        .get("overlays", [])
    )
    return any(
        badge.get("thumbnailBadgeViewModel", {}).get("badgeStyle")
        == "THUMBNAIL_OVERLAY_BADGE_STYLE_LIVE"
        for overlay in overlays
        for badge in overlay.get("thumbnailBottomOverlayViewModel", {}).get("badges", [])
    )


class YouTubeClient:
    def __init__(self):
        self._session = requests.Session()

    def _check_channel(self, channel_id):
        body = {
            "context": _CLIENT_CONTEXT,
            "browseId": channel_id,
            "params": LIVE_TAB_PARAMS,
        }
        try:
            resp = self._session.post(
                BROWSE_URL, params={"key": API_KEY}, json=body, timeout=10
            )
        except requests.RequestException:
            return None

        if resp.status_code != 200:
            return None

        try:
            data = resp.json()
        except ValueError:
            return None

        for item in _iter_rich_items(data):
            lockup = item.get("content", {}).get("lockupViewModel", {})
            if not _is_live_lockup(lockup):
                continue

            video_id = lockup.get("contentId")
            if not video_id:
                continue

            title = (
                lockup.get("metadata", {})
                .get("lockupMetadataViewModel", {})
                .get("title", {})
                .get("content", "")
            )
            return {
                "video_id": video_id,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        return None

    def get_live_channels(self, channel_map):
        """channel_map: {display_name: channel_id}. Returns a list of live
        stream dicts (video_id/title/url) with 'channel_name' merged in."""
        live = []
        for name, channel_id in channel_map.items():
            result = self._check_channel(channel_id)
            if result:
                result["channel_name"] = name
                live.append(result)
        return live
