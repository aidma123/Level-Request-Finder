# Removes the Scheduled Task installed by install.ps1. Does not delete
# config.json, state.json, or the venv - remove those manually if wanted.
#
# Usage:
#   .\scripts\uninstall.ps1

$ErrorActionPreference = "Stop"

$TaskName = "GD Level Request Notifier"

Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Removed scheduled task '$TaskName'."
