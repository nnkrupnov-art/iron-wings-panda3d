@echo off
title Iron Wings - WWII Flight Simulator
echo.
echo ================================================
echo    IRON WINGS - WWII Flight Simulator
echo ================================================
echo.
echo Controls:
echo   W/S     - Pitch up/down
echo   A/D     - Roll left/right
echo   Q/E     - Yaw
echo   Shift   - Throttle up
echo   Ctrl    - Throttle down
echo   Space   - Air brake
echo   R       - Reset position
echo   ESC     - Quit
echo.
echo ================================================
echo.

cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8+ from https://python.org
    echo.
    echo Alternatively, run: pip install panda3d
    pause
    exit /b 1
)

:: Check if Panda3D is installed
python -c "import panda3d" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Panda3D...
    pip install panda3d
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Panda3D!
        pause
        exit /b 1
    )
)

echo Starting game...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Game exited with error.
    pause
)
