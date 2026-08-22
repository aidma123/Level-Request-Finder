# Automatic setup for the GD Level Request Finder notifier, on THIS Windows machine.
#
# Usage (from PowerShell, in the repo root):
#   .\scripts\install-windows.ps1
#
# What this does:
#   - checks for Python 3
#   - creates a venv in the repo and installs requirements.txt
#   - copies config.example.json -> config.json if one doesn't already exist
#   - registers a Scheduled Task that starts the notifier at log on and
#     restarts it automatically if it crashes
#
# It does NOT fill in your Twitch/Discord/ntfy credentials - edit config.json
# yourself after this runs, then restart the task (see the printed message
# at the end).
#
# DISCLAIMER: this only works while this machine is powered on and you are
# logged in. It will NOT check for streams (or notify you) while the
# machine is off, asleep, or logged out.

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $PSScriptRoot
Set-Location $RepoDir

$TaskName = "GD Level Request Notifier"

Write-Host "==> Checking for Python 3"
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python 3 not found on PATH. Install it from https://python.org/downloads (check 'Add python.exe to PATH' during install), then re-run this script."
    exit 1
}

Write-Host "==> Setting up Python virtual environment"
if (-not (Test-Path "venv")) {
    python -m venv venv
}
& .\venv\Scripts\python.exe -m pip install --upgrade pip | Out-Null
& .\venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "==> Setting up config.json"
$configIsNew = $false
if (-not (Test-Path "config.json")) {
    Copy-Item "config.example.json" "config.json"
    $configIsNew = $true
}

Write-Host "==> Registering Scheduled Task"
$pythonwPath = Join-Path $RepoDir "venv\Scripts\pythonw.exe"
$action = New-ScheduledTaskAction -Execute $pythonwPath -Argument "main.py" -WorkingDirectory $RepoDir
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Description "Watches GD moderator Twitch/YouTube channels for level-request streams" | Out-Null
Start-ScheduledTask -TaskName $TaskName

Write-Host ""
Write-Host "Installed and started as a Scheduled Task ('$TaskName')."
Write-Host "Check status with:"
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo"
Write-Host "Stop it with:"
Write-Host "  Stop-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
if ($configIsNew) {
    Write-Host "IMPORTANT: edit $RepoDir\config.json with your Twitch/Discord/ntfy credentials,"
    Write-Host "then run:"
    Write-Host "  Stop-ScheduledTask -TaskName '$TaskName'; Start-ScheduledTask -TaskName '$TaskName'"
} else {
    Write-Host "config.json already existed - left untouched. Task is running with it."
}
Write-Host ""
Write-Host "DISCLAIMER: this only works while this machine is powered on and you are"
Write-Host "logged in. It will NOT check for streams (or notify you) while the"
Write-Host "machine is off, asleep, or logged out."
