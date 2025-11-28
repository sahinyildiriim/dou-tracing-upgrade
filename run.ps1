$ErrorActionPreference = 'Stop'

# Always run from this script's directory to avoid Unicode path issues
Set-Location -LiteralPath $PSScriptRoot

$python = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host "Virtualenv python not found at: $python" -ForegroundColor Red
    Write-Host "Please create venv or adjust path." -ForegroundColor Yellow
    exit 1
}

& $python .\main.py
exit $LASTEXITCODE


