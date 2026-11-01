@echo off
setlocal
cd /d "%~dp0"
echo =====================================================
echo CAN-Sentinel Windows Edition - setup and launch
echo =====================================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher not found. Install Python 3.11 or 3.12 from python.org.
  echo During installation, enable "Add python.exe to PATH".
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  py -3.11 -m venv .venv 2>nul
  if errorlevel 1 py -3.12 -m venv .venv 2>nul
  if errorlevel 1 py -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto fail
python -m pip install -r requirements.txt
if errorlevel 1 goto fail
python python\train_model.py --output models\isolation_forest.joblib
if errorlevel 1 goto fail
echo.
echo Starting dashboard in Windows simulation mode...
echo After the dashboard opens, use the included traffic batch files to test it.
python python\dashboard.py --interface sim --model models\isolation_forest.joblib
if errorlevel 1 goto fail
goto end
:fail
echo.
echo Setup or launch failed. Check the error above. Recommended Python: 3.11 or 3.12.
pause
exit /b 1
:end
endlocal
