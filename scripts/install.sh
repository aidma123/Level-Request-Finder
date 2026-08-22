#!/usr/bin/env bash
# Automatic setup for the GD Level Request Finder notifier.
#
# Usage:
#   ./scripts/install.sh --desktop   # this machine will show desktop popups (default if a display is detected)
#   ./scripts/install.sh --server    # headless box; runs as a system service, no desktop notifications
#
# What this does:
#   - installs python3/venv/pip/git via apt or pacman (whichever is present)
#   - creates a venv in the repo and installs requirements.txt
#   - copies config.example.json -> config.json if one doesn't already exist
#   - installs and starts a systemd service (user service for --desktop, system service for --server)
#
# It does NOT fill in your Twitch/Discord/ntfy credentials - edit config.json
# yourself after this runs, then `systemctl restart` (or `--user restart`)
# the service.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="gd-level-request-notifier.service"

MODE=""
for arg in "$@"; do
    case "$arg" in
        --desktop) MODE="desktop" ;;
        --server) MODE="server" ;;
        *)
            echo "Unknown argument: $arg" >&2
            echo "Usage: $0 [--desktop|--server]" >&2
            exit 1
            ;;
    esac
done

if [ -z "$MODE" ]; then
    if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
        MODE="desktop"
    else
        MODE="server"
    fi
    echo "No mode given, auto-detected: --$MODE (pass --desktop or --server to override)"
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

if [ "$MODE" = "server" ] && [ "$CONFIG_IS_NEW" = "1" ]; then
    python3 - "$REPO_DIR/config.json" <<'PYEOF'
import json
import sys

path = sys.argv[1]
with open(path) as f:
    config = json.load(f)
config.setdefault("notifications", {})["desktop"] = False
with open(path, "w") as f:
    json.dump(config, f, indent=2)
    f.write("\n")
PYEOF
    echo "Headless server detected - disabled desktop notifications in config.json"
fi

echo "==> Installing systemd service ($MODE)"
VENV_PYTHON="$REPO_DIR/venv/bin/python"

if [ "$MODE" = "desktop" ]; then
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
else
    RUN_USER="$(id -un)"
    cat <<EOF | sudo tee "/etc/systemd/system/$SERVICE_NAME" >/dev/null
[Unit]
Description=GD Level Request Stream Notifier
After=network-online.target
Wants=network-online.target

[Service]
User=$RUN_USER
WorkingDirectory=$REPO_DIR
ExecStart=$VENV_PYTHON main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable --now "$SERVICE_NAME"
    echo
    echo "Installed as a system service. Check status with:"
    echo "  sudo systemctl status $SERVICE_NAME"
    echo "Watch logs with:"
    echo "  journalctl -u ${SERVICE_NAME%.service} -f"
fi

echo
if [ "$CONFIG_IS_NEW" = "1" ]; then
    echo "IMPORTANT: edit $REPO_DIR/config.json with your Twitch/Discord/ntfy credentials,"
    echo "then restart the service (see command above) for them to take effect."
else
    echo "config.json already existed - left untouched. Service is running with it."
fi
