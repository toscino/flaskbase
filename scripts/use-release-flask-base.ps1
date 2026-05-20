# Install flask-base from the pinned GitHub Release (same as App Engine).
# Run from repo root with venv active.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& .\.venv\Scripts\python.exe -m pip install -r example\requirements.txt
Write-Host "Using GitHub Release wheel (see example/requirements.txt)"
