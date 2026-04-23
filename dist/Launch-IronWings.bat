@echo off
setlocal enabledelayedexpansion

title Iron Wings - WWII Flight Simulator
color 0A
cls

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║          IRON WINGS - WWII Flight Simulator              ║
echo  ║                    IL-2 Style                          ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

:: ============================================
:: AUTO-DOWNLOAD PYTHON + PANDAS + RUN GAME
:: ============================================

set "SCRIPT_DIR=%~dp0"
set "PYTHON_DIR=%SCRIPT_DIR%python-embed"

:: Check if portable Python exists
if exist "%PYTHON_DIR%\python.exe" (
    set "PYTHON=%PYTHON_DIR%\python.exe"
    echo [OK] Using bundled Python
) else (
    :: Try system Python
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON=python"
    ) else (
        where python3 >nul 2>&1
        if !errorlevel! equ 0 set "PYTHON=python3"
    )
    
    if "!PYTHON!"=="" (
        echo [DOWNLOAD] Portable Python not found. Downloading...
        echo.
        
        :: Download Python Embeddable
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-embed-amd64.zip' -OutFile 'python-embed.zip'}"
        
        if exist "%SCRIPT_DIR%python-embed.zip" (
            echo [EXTRACT] Extracting Python...
            powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath 'python-embed-temp' -Force"
            move /y "%SCRIPT_DIR%python-embed-temp" "%PYTHON_DIR%" >nul 2>&1
            del "%SCRIPT_DIR%python-embed.zip"
            
            :: Fix pip configuration
            echo import sys >> "%PYTHON_DIR%\python312._pth"
            echo import site >> "%PYTHON_DIR%\python312._pth"
            
            set "PYTHON=%PYTHON_DIR%\python.exe"
            echo [OK] Python downloaded and extracted
        ) else (
            echo [ERROR] Failed to download Python!
            echo Please install Python manually from https://python.org
            pause
            exit /b 1
        )
    )
)

:: Show Python version
echo.
!PYTHON! --version

:: ============================================
:: Install Panda3D
:: ============================================
echo.
echo [CHECK] Checking Panda3D...

!PYTHON! -c "import panda3d" 2>nul
if !errorlevel! neq 0 (
    echo [INSTALL] Installing Panda3D...
    echo This may take a few minutes...
    echo.
    
    !PYTHON! -m pip install panda3d --quiet --no-warn-script-location
    if !errorlevel! neq 0 (
        echo.
        echo [ERROR] Failed to install Panda3D!
        echo.
        echo Try running this command manually:
        echo   !PYTHON! -m pip install panda3d
        echo.
        pause
        exit /b 1
    )
    echo [OK] Panda3D installed successfully!
)

:: ============================================
:: RUN THE GAME
:: ============================================
echo.
echo ════════════════════════════════════════════════════
echo [START] Launching Iron Wings...
echo ════════════════════════════════════════════════════
echo.

cd /d "%SCRIPT_DIR%"
start "" /wait !PYTHON! main.py
set "EXITCODE=!errorlevel!"

if !EXITCODE! neq 0 (
    echo.
    echo Game exited with error code: !EXITCODE!
)

echo.
echo Press any key to exit...
pause >nul
exit /b !EXITCODE!
