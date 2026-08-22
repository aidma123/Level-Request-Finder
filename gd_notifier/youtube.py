"""Lightweight YouTube live-stream detection.

Uses each channel's public /live URL instead of the YouTube Data API,
since that API's free quota (10,000 units/day, ~100 units per live-check
call) can't support checking more than a handful of channels on anything
shorter than a very long interval. This trades an official, stable API
contract for one that depends on YouTube's current page markup — if
YouTube changes their page structure, the regexes below may need updating.
"""

import re

import requests

LIVE_URL_TEMPLATE = "https://www.youtube.com/channel/{channel_id}/live"
USER_AGENT = "Mozilla/5.0 (compatible; GDLevelRequestNotifier/1.0)"

# When a channel is live, YouTube's /live page has a canonical link pointing
# at the actual watch page, and the embedded player data marks the current
# broadcast as live (as opposed to an upcoming premiere or a past replay).
_CANONICAL_VIDEO_RE = re.compile(
    r'<link rel="canonical" href="https://www\.youtube\.com/watch\?v=([\w-]+)"'
)
_IS_LIVE_NOW_RE = re.compile(r'"isLiveNow"\s*:\s*true')
_TITLE_RE = re.compile(r'<meta name="title" content="([^"]*)"')


class YouTubeClient:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})

    def _check_channel(self, channel_id):
        try:
            resp = self._session.get(
                LIVE_URL_TEMPLATE.format(channel_id=channel_id), timeout=10
            )
        except requests.RequestException:
            return None

        if resp.status_code != 200:
            return None

        html = resp.text
        video_match = _CANONICAL_VIDEO_RE.search(html)
        if not video_match or not _IS_LIVE_NOW_RE.search(html):
            return None

        video_id = video_match.group(1)
        title_match = _TITLE_RE.search(html)
        return {
            "video_id": video_id,
            "title": title_match.group(1) if title_match else "",
            "url": f"https://www.youtube.com/watch?v={video_id}",
        }

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
