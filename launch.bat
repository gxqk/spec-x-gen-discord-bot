@echo off
title Spec-X Discord Bot Launcher

echo.
echo / ======================================== \
echo #        Spec-X Discord Bot Launcher       #  
echo \ ======================================== /
echo.

echo [INFO] Checking and installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Dependencies are ready!
    echo [INFO] Starting Spec-X Discord Bot...
    echo.
    py main.py
) else (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo [INFO] Please check your Python installation and try again.
    pause
)

echo.
echo [INFO] Bot has stopped. Press any key to exit...
pause > nul
