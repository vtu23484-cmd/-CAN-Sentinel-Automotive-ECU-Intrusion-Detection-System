@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo    CAN-SENTINEL WEEK 2 - START PROJECT
echo ========================================
echo Uses Ubuntu WSL2 to run the original C and SocketCAN source.
where wsl.exe >nul 2>nul
if errorlevel 1 (
 echo ERROR: WSL not found. In Administrator PowerShell run:
 echo wsl --install -d Ubuntu
 echo Then restart if asked and open Ubuntu once to create a username.
 pause
 exit /b 1
)
wsl.exe -d Ubuntu --cd "%~dp0." --exec bash ./START_WEEK2.sh
if errorlevel 1 (
 echo.
 echo RUN FAILED. Read the error above. The Ubuntu WSL2 kernel must support vcan0.
) else (
 echo.
 echo SUCCESS: Open week2\results\LIVE_MID_REVIEW.html
 start "" "%~dp0week2\results"
)
pause
