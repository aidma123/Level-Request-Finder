# Level Request Finder

Watches Geometry Dash moderators' Twitch and YouTube channels and notifies
you the moment one of them goes live doing a level-request stream.

Neither platform has a "GD moderator" flag to query, so this tool polls
lists of channels *you* maintain (`moderators` for Twitch,
`youtube_channels` for YouTube) and flags any that are:

1. Live
2. (Twitch only) Streaming under the "Geometry Dash" category (optional,
   on by default)
3. Have a title that matches a level-request keyword (e.g. "level request",
   "sending levels", "LR stream", ...)

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Register a free Twitch app to get API credentials (only needed if you're
   using the Twitch side — see below):
   - Go to https://dev.twitch.tv/console/apps and create an application
     (any name, OAuth redirect URL can be `http://localhost`, category
     "Application Integration").
   - Copy the generated **Client ID** and **Client Secret**.

   YouTube needs no API key — see "How YouTube detection works" below.

3. Create your config file:

   ```bash
   cp config.example.json config.json
   ```

   Then edit `config.json`:
   - Fill in `twitch_client_id` / `twitch_client_secret` (or instead set the
     `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET` environment variables and
     leave these blank — env vars take precedence). Only required if
     `moderators` is non-empty.
   - `moderators` and `youtube_channels` already ship pre-filled with
     current GD moderators (see the table below) — trim them down or add
     more as the mod roster changes.
   - Adjust `level_request_keywords` if you want to catch different title
     phrasing.
   - Set `require_gd_category` to `false` if you want to catch Twitch
     streams even when Twitch has them miscategorized.

4. (Optional) Enable a Discord webhook notification by setting
   `notifications.discord_webhook_url` to a webhook URL from your server's
   channel settings.

### Current GD moderators

| Name | Twitch | YouTube |
| --- | --- | --- |
| agdor (Elder) | [gdagdor](https://twitch.tv/gdagdor) | |
| Halapeenyo (Elder) | [halapeenyo](https://twitch.tv/halapeenyo) | |
| KazVixX (Elder) | [kazvixx](https://twitch.tv/kazvixx) | [channel](https://www.youtube.com/channel/UChO6WUVUrzGI7iklJHYsVYw) |
| Lia (Elder) | [liathecatto](https://twitch.tv/liathecatto) | |
| Tygore (Elder) | [tygoregd](https://twitch.tv/tygoregd) | |
| AgSilver | [itsagsilver](https://twitch.tv/itsagsilver) | |
| arcanin | [rawrcanin](https://twitch.tv/rawrcanin) | |
| Ausk | [ausk_gd](https://twitch.tv/ausk_gd) | |
| Danolex | [danolex](https://twitch.tv/danolex) | [channel](https://www.youtube.com/channel/UC5hEBLZqXINNYu1Fqpwb1VQ) |
| Destriv | [destriv_](https://twitch.tv/destriv_) | [channel](https://www.youtube.com/channel/UCl-eyZZ0MvDFJAKLZTAq1eg) |
| drane | [imdrane](https://twitch.tv/imdrane) | |
| DreamEater | [dreameater_gd](https://twitch.tv/dreameater_gd) | [channel](https://www.youtube.com/channel/UCoMhb2dbP1B4rgS48pRI8yg) |
| FakeHATETAG | [fakehatetag_](https://twitch.tv/fakehatetag_) | |
| gBen | | [channel](https://www.youtube.com/channel/UClgIANE-cdR16TAT1ly9UBw) |
| Gecko | | [channel](https://www.youtube.com/channel/UC4sbnW-8Q2PtSPqXtYJtVuQ) |
| GirlyAle02 | [girlyale02_](https://twitch.tv/girlyale02_) | |
| Hychie | [hychie_](https://twitch.tv/hychie_) | |
| Incidius | [incidiusgd](https://twitch.tv/incidiusgd) | |
| Infra | [infra553](https://twitch.tv/infra553) | [channel](https://www.youtube.com/channel/UCdMP8AUwNYuK5A6TEW4bivA) |
| ivyteal | | [channel](https://www.youtube.com/channel/UCt6szkEO6KqefIGuaWuhQsA) |
| kreno | [1kreno](https://twitch.tv/1kreno) | |
| Lagan | | [channel](https://www.youtube.com/channel/UCbSp-RwgVIVbbn3U2lZItSQ) |
| LandonGMD | | [channel](https://www.youtube.com/channel/UCBQEe6MK-WeE4gWK6s3XHYw) |
| mag | [btwmagna](https://twitch.tv/btwmagna) | |
| orots | [orots](https://twitch.tv/orots) | |
| RavingRafters | [ravingrafters](https://twitch.tv/ravingrafters) | |
| rustere | [rustere](https://twitch.tv/rustere) | |
| Sakura | | [channel](https://www.youtube.com/channel/UCOIlMHu_pKgceEAIHcWK1lA) |
| sink | | [channel](https://www.youtube.com/channel/UCsZKYORQGsiJAIknADJYt_g) |
| spark | | [channel](https://www.youtube.com/channel/UC8elOWy3VPWgOKS7dAkqiTg) |
| Starr44 | [starr44_](https://twitch.tv/starr44_) | |
| SwtCyn | [swtcyn](https://twitch.tv/swtcyn) | [channel](https://www.youtube.com/channel/UCeUuCQT3F-8-PytQBbiHGBg) |
| Tess | [strawberrytess](https://twitch.tv/strawberrytess) | |
| thejshadow | [thejshadow_](https://twitch.tv/thejshadow_) | |
| tricipital | [tricipital](https://twitch.tv/tricipital) | |

Moderators with no Discord-verified public Twitch/YouTube (Bert, Devilmine,
Ryder, SirHadoken, 2kb, CheckSteam, Chloe, Colon, connot, DashTY,
Dasher3000, Debihan, Electro, GiggsRH, Gormuck, Gusearth, MrSpaghetti,
Perox8, Pouche, SleyGD, SparksOmega, vLibra, waffybun) aren't included —
add them if you find their stream pages.

Source: [GD Mod Outreach doc](https://hackmd.io/@acezure/GD-Mod-Outreach) —
re-check it periodically since the mod roster and handles can change.

## How YouTube detection works

There's no cheap, quota-friendly way to ask "is this channel live right
now" via the official YouTube Data API — a single live-check call costs
~100 of the free tier's 10,000 daily quota units, which can't support
polling more than a handful of channels on anything shorter than a very
long interval.

Instead, this tool requests each channel's public `/live` URL
(`youtube.com/channel/<id>/live`) and checks whether the page's embedded
data marks a broadcast as currently live. This needs no API key and has no
quota limit, but it depends on YouTube's current page markup rather than a
stable, versioned API — if YouTube changes that markup, YouTube detection
may stop working until the tool is updated (Twitch detection is unaffected
either way, since it uses Twitch's official Helix API).

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

- Twitch/YouTube only report what's actually live and its title (plus
  category, for Twitch) — neither can tell you a streamer's GD moderator
  status, so `moderators` / `youtube_channels` are the source of truth for
  *who* to watch.
- Rerunning with `--once` on a schedule (cron/systemd/Task Scheduler) avoids
  keeping a process running all the time, at the cost of only checking on
  that schedule.
