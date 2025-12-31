@echo off
REM PDF Translation System - Windows Setup Script
REM This script sets up the virtual environment and installs dependencies

echo ========================================
echo PDF Translation System - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.10 or higher from:
    echo - Microsoft Store: Search for "Python 3.12"
    echo - Or: https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [STEP 1/4] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [SKIP] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [STEP 2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment!
    echo.
    echo Try running this in Command Prompt (cmd) instead of PowerShell
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [STEP 3/4] Upgrading pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip, continuing...
) else (
    echo [OK] pip upgraded
)
echo.

REM Install dependencies
echo [STEP 4/4] Installing dependencies...
echo This may take 1-3 minutes...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Try running as Administrator or check your internet connection
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [SETUP] Creating .env file...
    copy .env.example .env >nul
    echo [OK] .env file created
    echo.
    echo ========================================
    echo IMPORTANT: Configure your API key!
    echo ========================================
    echo.
    echo Please edit the .env file and add your OpenAI API key:
    echo.
    echo 1. Open .env file (will open now in Notepad)
    echo 2. Replace "your_openai_api_key_here" with your actual API key
    echo 3. Save and close the file
    echo.
    echo Get your API key from: https://platform.openai.com/api-keys
    echo.
    pause
    notepad .env
) else (
    echo [SKIP] .env file already exists
)
echo.

REM Create output directory
if not exist "output" (
    mkdir output
    echo [OK] Created output directory
)

echo ========================================
echo Setup Complete! ^_^
echo ========================================
echo.
echo You can now run the application using:
echo   - Double-click "run.bat"
echo   - Or run: run.bat
echo.
echo Make sure you have configured your OpenAI API key in the .env file!
echo.
pause
