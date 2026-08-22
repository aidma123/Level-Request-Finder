# Running on Windows

The core notifier (Twitch/YouTube checking, desktop popups via `plyer`,
Discord webhook, ntfy) works the same on Windows as on Linux/macOS — the
only real difference is how you keep it running in the background, since
Windows has no `systemd`. This uses Task Scheduler instead.

> **Disclaimer:** just like the Linux setup, this only works while this
> machine is powered on and you're logged in. If it's off, asleep, or
> logged out, nothing is checking for streams and you won't be notified
> during that time.

## Quick automated setup

Open **PowerShell** in the folder where you want the project, then:

```powershell
git clone https://github.com/aidma123/level-request-finder.git
cd level-request-finder
.\scripts\install-windows.ps1
```

This installs the Python dependencies, scaffolds `config.json`, and
registers a Scheduled Task that starts the notifier when you log in and
restarts it automatically if it crashes.

It won't fill in your Twitch/Discord/ntfy credentials for you — edit the
generated `config.json` afterward (see below), then restart the task:
```powershell
Stop-ScheduledTask -TaskName "GD Level Request Notifier"
Start-ScheduledTask -TaskName "GD Level Request Notifier"
```

To remove it later:
```powershell
.\scripts\uninstall-windows.ps1
```

**Note:** `install-windows.ps1` hasn't been tested against a real Windows machine
(this project was built and verified on Linux) — the manual steps below
are the same thing spelled out by hand, useful if the script hits a snag
specific to your setup.

## Manual setup

1. **Install Python 3**, if you don't already have it: download from
   https://python.org/downloads and run the installer. On the first
   screen, check **"Add python.exe to PATH"** before clicking install —
   easy to miss, and things below won't work without it.

2. **Get the code:**
   ```powershell
   git clone https://github.com/aidma123/level-request-finder.git
   cd level-request-finder
   ```
   (If you don't have `git`, you can instead download the ZIP from GitHub
   and extract it.)

3. **Set up a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   If `Activate.ps1` is blocked by PowerShell's execution policy, run this
   once (as your normal user, not admin) and try again:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

4. **Create your config file:**
   ```powershell
   Copy-Item config.example.json config.json
   ```
   Then open `config.json` in Notepad (or any editor) and fill in your
   Twitch/Discord/ntfy details — see the main [README](README.md) for how
   to get Twitch API credentials and what each field means.

5. **Test it:**
   ```powershell
   python main.py --test-notify
   ```
   You should see a Windows toast notification pop up (desktop
   notifications work out of the box on Windows via `plyer` — no extra
   setup needed, unlike Linux).

6. **Run it continuously** (in a terminal you keep open):
   ```powershell
   python main.py
   ```
   Ctrl+C to stop. For something that survives closing the terminal, keep
   reading.

## Running in the background (Task Scheduler)

Since Windows has no `systemd`, use Task Scheduler to start this
automatically at login and keep it running:

1. Open **Task Scheduler** (search for it in the Start menu)
2. **Action → Create Task** (not "Create Basic Task" — this gives more
   control)
3. **General tab:**
   - Name: `GD Level Request Notifier`
   - Select **"Run only when user is logged on"** (needed for desktop
     popups to work at all)
4. **Triggers tab → New:**
   - Begin the task: **At log on**
   - Specific user: your account
5. **Actions tab → New:**
   - Action: **Start a program**
   - Program/script: the full path to `venv\Scripts\pythonw.exe` inside
     your project folder (`pythonw.exe`, not `python.exe`, so it runs
     without popping up a console window) — e.g.
     `C:\Users\you\level-request-finder\venv\Scripts\pythonw.exe`
   - Add arguments: `main.py`
   - Start in: the full path to your project folder, e.g.
     `C:\Users\you\level-request-finder`
6. **Conditions tab:** if this is a laptop, uncheck **"Start the task only
   if the computer is on AC power"** so it keeps running on battery too
7. **Settings tab:** check **"If the task fails, restart every"** and set
   it to something like 1 minute, a few attempts — mirrors the
   auto-restart behavior of the Linux systemd setup
8. Click OK, enter your Windows password if prompted, and the task is now
   active — it'll start automatically next time you log in, or you can
   right-click it → **Run** to start it immediately

To check on it, watch for the desktop notification when a moderator goes
live — since `pythonw.exe` runs with no visible console window, there's no
running-log window to check like `journalctl` on Linux.

To stop or remove it: open Task Scheduler, find the task, right-click →
**Disable** (to stop it without deleting) or **Delete** (to remove it
entirely).
