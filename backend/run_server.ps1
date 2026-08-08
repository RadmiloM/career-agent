Set-StrictMode -Version Latest

$backendRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $backendRoot ".venv/Scripts/python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Python virtual environment was not found at $pythonExe"
    exit 1
}

Set-Location $backendRoot

Write-Host "Starting backend from $backendRoot"
& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
