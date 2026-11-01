@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo First run run_windows.bat to install the dependencies.
  pause
  exit /b 1
)
.venv\Scripts\python.exe python\traffic.py --interface sim --mode normal --duration 60
pause
