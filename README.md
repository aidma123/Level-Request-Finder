# Level Request Finder

Watches a list of Geometry Dash Twitch streamers/moderators and notifies you
the moment one of them goes live doing a level-request stream.

Twitch has no "GD moderator" flag to query, so this tool polls a list of
channels *you* maintain (`moderators` in your config) and flags any that are:

1. Live
2. Streaming under the "Geometry Dash" category (optional, on by default)
3. Have a title that matches a level-request keyword (e.g. "level request",
   "sending levels", "LR stream", ...)

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Register a free Twitch app to get API credentials:
   - Go to https://dev.twitch.tv/console/apps and create an application
     (any name, OAuth redirect URL can be `http://localhost`, category
     "Application Integration").
   - Copy the generated **Client ID** and **Client Secret**.

3. Create your config file:

   ```bash
   cp config.example.json config.json
   ```

   Then edit `config.json`:
   - Fill in `twitch_client_id` / `twitch_client_secret` (or instead set the
     `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET` environment variables and
     leave these blank — env vars take precedence).
   - Replace `moderators` with the actual Twitch usernames (the part after
     `twitch.tv/`) of the GD moderators/streamers you want to watch. You can
     find current level-request streamers via the Geometry Dash Twitch
     directory (https://www.twitch.tv/directory/game/Geometry%20Dash) or the
     GD community Discord.
   - Adjust `level_request_keywords` if you want to catch different title
     phrasing.
   - Set `require_gd_category` to `false` if you want to catch streams even
     when Twitch has them miscategorized.

4. (Optional) Enable a Discord webhook notification by setting
   `notifications.discord_webhook_url` to a webhook URL from your server's
   channel settings.

## Usage

Run continuously, polling every `poll_interval_seconds` (default 60):

```bash
python main.py
```

Run a single check and exit (useful for cron/systemd timers instead of a
long-running loop):

```bash
python main.py --once
```

Override the poll interval or config path:

```bash
python main.py --interval 30 --config /path/to/config.json
```

## Notifications

- **Console**: always prints a line when a match is found (unless disabled).
- **Desktop popup**: uses [`plyer`](https://github.com/kivy/plyer); works on
  Linux (requires `notify-send`/a notification daemon), macOS, and Windows.
- **Discord webhook**: posts a message to a Discord channel.

Each live stream is only notified once per "session" — if a channel goes
offline and back online, or the title changes to start matching, you'll be
notified again. State is tracked in `state.json` (gitignored).

## Notes

- The Twitch API only reports what's actually live and its title/category —
  it can't tell you a streamer's GD moderator status, so the `moderators`
  list is the source of truth for *who* to watch.
- Rerunning with `--once` on a schedule (cron/systemd/Task Scheduler) avoids
  keeping a process running all the time, at the cost of only checking on
  that schedule.
