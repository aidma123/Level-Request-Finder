#!/usr/bin/env bash
# Removes the systemd user service installed by install-linux.sh. Does not delete
# config.json, state.json, or the venv - remove those manually if wanted.
#
# Usage:
#   ./scripts/uninstall-linux.sh

set -euo pipefail

SERVICE_NAME="gd-level-request-notifier.service"

if [ "$#" -gt 0 ]; then
    echo "Usage: $0 (no arguments)" >&2
    exit 1
fi

systemctl --user disable --now "$SERVICE_NAME" 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/$SERVICE_NAME"
systemctl --user daemon-reload
echo "Removed user service."
