"""Minimal Twitch Helix API client for looking up live streams."""

import time

import requests

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
STREAMS_URL = "https://api.twitch.tv/helix/streams"


class TwitchClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expires_at = 0

    def _get_app_token(self):
        # App access token via client credentials grant; no user login needed
        # since we only read public stream data.
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token

        resp = requests.post(
            TOKEN_URL,
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 3600)
        return self._token

    def get_live_streams(self, user_logins):
        """Return Helix stream objects for whichever of the given logins are
        currently live. Handles Twitch's 100-login-per-request limit."""
        if not user_logins:
            return []

        token = self._get_app_token()
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {token}",
        }

        streams = []
        for i in range(0, len(user_logins), 100):
            batch = user_logins[i : i + 100]
            params = [("user_login", login) for login in batch]
            params.append(("first", 100))
            resp = requests.get(STREAMS_URL, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            streams.extend(resp.json().get("data", []))
        return streams
