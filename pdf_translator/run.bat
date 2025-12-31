@echo off
REM PDF Translation System - Windows Run Script
REM This script runs the Streamlit application

echo ========================================
echo PDF Translation System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run "setup.bat" first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo.
    echo Please edit .env file and add your OpenAI API key!
    echo Opening .env file in Notepad...
    echo.
    pause
    notepad .env
)

REM Activate virtual environment
echo [STEP 1/2] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment!
    echo.
    echo Try running "setup.bat" again.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Run Streamlit app
echo [STEP 2/2] Starting Streamlit app...
echo.
echo ========================================
echo Opening browser...
echo ========================================
echo.
echo If browser doesn't open automatically,
echo go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run app.py

REM Deactivate virtual environment on exit
call deactivate

echo.
echo ========================================
echo Application stopped
echo ========================================
pause
