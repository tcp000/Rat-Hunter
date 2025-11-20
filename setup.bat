@echo off
title Rat Hunter - Setup
echo ===============================
echo   Installing Requirements...
echo ===============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not added to PATH.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b
)

REM Upgrade pip
echo Updating pip...
python -m pip install --upgrade pip

REM Install required packages
echo Installing libraries...
pip install -r requirements.txt

echo.
echo ===============================
echo   Setup Completed Successfully!
echo ===============================
pause
