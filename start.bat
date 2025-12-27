@echo off
setlocal enabledelayedexpansion

echo ================================================
echo   PDF RAG Chatbot System - Quick Start (Windows)
echo ================================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Copying from .env.example...
    copy .env.example .env
    echo [SUCCESS] .env file created.
    echo.
    echo Please edit .env file to add your API keys:
    echo   - OPENAI_API_KEY ^(required^)
    echo   - UPSTAGE_API_KEY ^(optional, for Upstage parser^)
    echo.
    echo Opening .env file in notepad...
    start notepad .env
    echo.
    pause
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [INFO] Starting all services...
docker-compose up -d

echo.
echo [INFO] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service health
echo.
echo [INFO] Checking service health...

REM Check MinIO
curl -s http://localhost:9000/minio/health/live >nul 2>&1
if errorlevel 1 (
    echo [WARNING] MinIO is not ready yet
) else (
    echo [SUCCESS] MinIO is ready
)

REM Check Redis
docker exec pdf-rag-redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis is not ready yet
) else (
    echo [SUCCESS] Redis is ready
)

REM Check Elasticsearch
curl -s http://localhost:9200/_cluster/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Elasticsearch is not ready yet ^(may take 1-2 minutes^)
) else (
    echo [SUCCESS] Elasticsearch is ready
)

REM Check Backend
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend API is not ready yet
) else (
    echo [SUCCESS] Backend API is ready
)

REM Check Frontend
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Frontend is not ready yet
) else (
    echo [SUCCESS] Frontend is ready
)

echo.
echo ================================================
echo   System Started!
echo ================================================
echo.
echo Access the services:
echo   Streamlit UI:    http://localhost:8501
echo   API Docs:        http://localhost:8000/docs
echo   MinIO Console:   http://localhost:9001
echo      ^(minioadmin / minioadmin^)
echo.
echo Opening Streamlit UI in your browser...
timeout /t 3 /nobreak >nul
start http://localhost:8501
echo.
echo Useful commands:
echo   View logs:          docker-compose logs -f
echo   Stop system:        docker-compose down
echo   Restart service:    docker-compose restart ^<service^>
echo.
echo For detailed documentation, see README.md or WINDOWS_SETUP.md
echo ================================================
echo.
pause
