@echo off
setlocal enabledelayedexpansion

REM Change to this script's directory (avoids Unicode path issues)
cd /d %~dp0

set PY=%CD%\venv\Scripts\python.exe
if not exist "%PY%" (
  echo Virtualenv python not found at: %PY%
  echo Please create venv or adjust path.
  exit /b 1
)

"%PY%" "%CD%\main.py"
exit /b %errorlevel%


