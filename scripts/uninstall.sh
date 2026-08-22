#!/usr/bin/env bash
# Removes the systemd service installed by install.sh. Does not delete
# config.json, state.json, or the venv - remove those manually if wanted.
#
# Usage:
#   ./scripts/uninstall.sh --desktop   # remove the user service
#   ./scripts/uninstall.sh --server    # remove the system service

set -euo pipefail

SERVICE_NAME="gd-level-request-notifier.service"

MODE="${1:-}"
case "$MODE" in
    --desktop)
        systemctl --user disable --now "$SERVICE_NAME" 2>/dev/null || true
        rm -f "$HOME/.config/systemd/user/$SERVICE_NAME"
        systemctl --user daemon-reload
        echo "Removed user service."
        ;;
    --server)
        sudo systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true
        sudo rm -f "/etc/systemd/system/$SERVICE_NAME"
        sudo systemctl daemon-reload
        echo "Removed system service."
        ;;
    *)
        echo "Usage: $0 [--desktop|--server]" >&2
        exit 1
        ;;
esac
