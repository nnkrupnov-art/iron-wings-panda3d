@echo off
setlocal enabledelayedexpansion

title Iron Wings - WWII Flight Simulator
color 0A

echo.
echo  ================================================
echo     IRON WINGS - WWII Flight Simulator  
echo  ================================================
echo.

:: Find Python
set PYTHON=
where python >nul 2>&1
if %errorlevel% equ 0 set PYTHON=python

where python3 >nul 2>&1
if %errorlevel% equ 0 set PYTHON=python3

if "!PYTHON!"=="" (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.8+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo After installation, run this script again.
    echo.
    pause
    exit /b 1
)

echo [OK] Found: !PYTHON!
!PYTHON! --version

:: Check and install Panda3D
echo.
echo Checking Panda3D...
!PYTHON! -c "import panda3d; print('[OK] Panda3D installed')" 2>nul
if %errorlevel% neq 0 (
    echo Installing Panda3D...
    !PYTHON! -m pip install panda3d --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Panda3D!
        echo.
        echo Try running this command manually:
        echo   !PYTHON! -m pip install panda3d
        echo.
        pause
        exit /b 1
    )
)

:: Run the game
echo.
echo Starting Iron Wings...
echo ================================================
echo.
!PYTHON! main.py
set EXITCODE=%errorlevel%

if %EXITCODE% neq 0 (
    echo.
    echo Game exited with error code: %EXITCODE%
)

echo.
pause
