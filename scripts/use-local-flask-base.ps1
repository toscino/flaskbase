# Editable install of flask_base/ for library development.
# Run from repo root with venv active.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Write-Host "Using editable flask_base/ (maintainers only)"
