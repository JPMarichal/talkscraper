@echo off
REM TalkScraper Setup Script for Windows

echo =================================
echo     TalkScraper Setup
echo =================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

echo Installing required packages...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo =================================
echo     Setup Complete!
echo =================================
echo.
echo Next steps:
echo 1. Copy config_template.ini to config.ini
echo 2. Adjust settings in config.ini if needed
echo 3. Run: python main.py --phase 1
echo.
echo To activate virtual environment manually:
echo   venv\Scripts\activate.bat
echo.
pause
