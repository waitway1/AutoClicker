@echo off
echo ========================================
echo   AutoClicker Pro - Build Script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
pyinstaller --onefile --windowed ^
    --name "AutoClickerPro" ^
    --add-data "ui;ui" ^
    --add-data "core;core" ^
    --hidden-import PySide6.QtWidgets ^
    --hidden-import PySide6.QtCore ^
    --hidden-import PySide6.QtGui ^
    --hidden-import pynput ^
    --hidden-import pynput.keyboard ^
    --hidden-import pynput.mouse ^
    main.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build successful!
echo   Output: dist\AutoClickerPro.exe
echo ========================================
pause
