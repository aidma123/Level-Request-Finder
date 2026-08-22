#!/usr/bin/env bash
# Automatic setup for the GD Level Request Finder notifier, on THIS machine.
#
# Usage:
#   ./scripts/install.sh
#
# What this does:
#   - installs python3/venv/pip/git via apt or pacman (whichever is present)
#   - creates a venv in the repo and installs requirements.txt
#   - copies config.example.json -> config.json if one doesn't already exist
#   - installs and starts a per-user systemd service with desktop notifications on
#
# It does NOT fill in your Twitch/Discord/ntfy credentials - edit config.json
# yourself after this runs, then `systemctl --user restart` the service.
#
# DISCLAIMER: this only runs while THIS machine is powered on and you're
# logged in. It is a per-user systemd service, not a system-wide daemon - if
# the laptop is off, asleep, or logged out, it is not checking for streams
# and you will not be notified during that time.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="gd-level-request-notifier.service"

if [ "$#" -gt 0 ]; then
    echo "Usage: $0 (no arguments)" >&2
    exit 1
fi

echo "==> Installing system packages"
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip git
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --needed --noconfirm python python-pip git
else
    echo "Unsupported package manager. Install python3, python3-venv, pip, and git manually, then re-run this script." >&2
    exit 1
fi

echo "==> Setting up Python virtual environment"
cd "$REPO_DIR"
if [ ! -d venv ]; then
    python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "==> Setting up config.json"
CONFIG_IS_NEW=0
if [ ! -f config.json ]; then
    cp config.example.json config.json
    CONFIG_IS_NEW=1
fi

echo "==> Installing systemd user service"
VENV_PYTHON="$REPO_DIR/venv/bin/python"
UNIT_DIR="$HOME/.config/systemd/user"
mkdir -p "$UNIT_DIR"
cat > "$UNIT_DIR/$SERVICE_NAME" <<EOF
[Unit]
Description=GD Level Request Stream Notifier
After=graphical-session.target
PartOf=graphical-session.target

[Service]
WorkingDirectory=$REPO_DIR
ExecStart=$VENV_PYTHON main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now "$SERVICE_NAME"

echo
echo "Installed as a user service. Check status with:"
echo "  systemctl --user status $SERVICE_NAME"
echo "Watch logs with:"
echo "  journalctl --user -u ${SERVICE_NAME%.service} -f"
echo
if [ "$CONFIG_IS_NEW" = "1" ]; then
    echo "IMPORTANT: edit $REPO_DIR/config.json with your Twitch/Discord/ntfy credentials,"
    echo "then run: systemctl --user restart $SERVICE_NAME"
else
    echo "config.json already existed - left untouched. Service is running with it."
fi
echo
echo "DISCLAIMER: this only works while this machine is powered on and you are"
echo "logged in. It will NOT check for streams (or notify you) while the"
echo "machine is off, asleep, or logged out."
