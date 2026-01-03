@echo off
REM Learning Locker xAPI Statement 테스트 스크립트 (Windows 배치 파일)
REM
REM 사용법:
REM   1. 환경 변수 설정 후 실행:
REM      set LRS_KEY=your_key_here
REM      set LRS_SECRET=your_secret_here
REM      test-statements.bat
REM
REM   2. 또는 아래 배치 파일을 수정하여 KEY와 SECRET 직접 입력

setlocal

REM ===== 여기에 Learning Locker Client Key와 Secret을 입력하세요 =====
REM (환경 변수가 설정되지 않은 경우에만 사용됨)
if "%LRS_KEY%"=="" set LRS_KEY=여기에_Client_Key_입력
if "%LRS_SECRET%"=="" set LRS_SECRET=여기에_Client_Secret_입력
if "%LRS_ENDPOINT%"=="" set LRS_ENDPOINT=http://localhost/data/xAPI

REM Statement 개수 설정 (기본값: 100)
if "%STATEMENT_COUNT%"=="" set STATEMENT_COUNT=100

echo ============================================================
echo Learning Locker xAPI Statement 테스트 (Windows)
echo ============================================================
echo.
echo 엔드포인트: %LRS_ENDPOINT%
echo Statement 개수: %STATEMENT_COUNT%
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다.
    echo Python 3.7 이상을 설치하세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM requests 패키지 확인
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [알림] requests 패키지를 설치합니다...
    pip install requests
    if errorlevel 1 (
        echo [오류] requests 패키지 설치 실패
        pause
        exit /b 1
    )
)

REM 테스트 스크립트 실행
echo.
echo 테스트 스크립트 실행 중...
echo.

python scripts\test-statements.py ^
    --endpoint %LRS_ENDPOINT% ^
    --key "%LRS_KEY%" ^
    --secret "%LRS_SECRET%" ^
    --count %STATEMENT_COUNT% ^
    --verify

if errorlevel 1 (
    echo.
    echo [오류] 테스트 실패
    echo.
    echo 문제 해결:
    echo   1. Learning Locker가 실행 중인지 확인: docker-compose ps
    echo   2. Client Key와 Secret이 올바른지 확인
    echo   3. 브라우저에서 http://localhost 접속 확인
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 테스트 완료!
echo ============================================================
echo.
echo 다음 단계:
echo   1. 브라우저에서 http://localhost 접속
echo   2. Data ^> Statements 메뉴에서 데이터 확인
echo   3. Visualisations에서 그래프 생성
echo.
pause
