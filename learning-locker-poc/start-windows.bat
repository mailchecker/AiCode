@echo off
REM Learning Locker POC - Windows 빠른 시작 스크립트
REM 이 배치 파일은 Windows에서 Learning Locker를 쉽게 시작할 수 있도록 도와줍니다.

echo ============================================================
echo Learning Locker POC - Windows 빠른 시작
echo ============================================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [경고] 이 스크립트는 관리자 권한으로 실행하는 것을 권장합니다.
    echo.
    timeout /t 3 >nul
)

REM Docker 설치 확인
docker --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Docker가 설치되지 않았습니다.
    echo.
    echo Docker Desktop을 설치하세요:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Docker 실행 확인
docker info >nul 2>&1
if errorlevel 1 (
    echo [오류] Docker가 실행 중이지 않습니다.
    echo.
    echo Docker Desktop을 실행한 후 다시 시도하세요.
    echo.
    pause
    exit /b 1
)

echo [1/4] Docker 확인 완료
echo.

REM .env 파일 확인
if not exist .env (
    echo [2/4] .env 파일 생성 중...
    copy .env.example .env >nul
    echo.
    echo [중요] .env 파일이 생성되었습니다.
    echo 메모장으로 .env 파일을 열어 비밀번호를 변경하세요.
    echo.
    notepad .env
    echo.
    echo 비밀번호를 변경했나요? (Y/N)
    set /p CONFIRM=
    if /i not "%CONFIRM%"=="Y" (
        echo.
        echo 보안을 위해 .env 파일의 비밀번호를 변경한 후 다시 실행하세요.
        pause
        exit /b 1
    )
) else (
    echo [2/4] .env 파일 확인 완료
)
echo.

REM Docker Compose로 서비스 시작
echo [3/4] Learning Locker 서비스 시작 중...
echo (이 과정은 최초 실행 시 수 분이 걸릴 수 있습니다)
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo [오류] 서비스 시작 실패
    echo.
    echo 로그 확인: docker-compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo [4/4] 서비스 준비 대기 중...
echo.

REM 서비스 준비 대기 (60초)
timeout /t 60 /nobreak >nul

REM 서비스 상태 확인
docker-compose ps

echo.
echo ============================================================
echo Learning Locker 서비스 시작 완료!
echo ============================================================
echo.
echo 접속 정보:
echo   Learning Locker UI: http://localhost
echo   API 엔드포인트: http://localhost/data/xAPI
echo.
echo 다음 단계:
echo   1. 브라우저에서 http://localhost 접속
echo   2. 회원가입 및 로그인
echo   3. Organization과 Store 생성
echo   4. Client 인증 정보 생성 (Key와 Secret 저장)
echo   5. test-statements.bat 실행하여 테스트 데이터 전송
echo.
echo 상세 가이드: WINDOWS_GUIDE.md 참고
echo.

REM 브라우저 자동 열기
set /p OPEN_BROWSER=브라우저를 여시겠습니까? (Y/N):
if /i "%OPEN_BROWSER%"=="Y" (
    start http://localhost
)

echo.
echo 서비스 중지: docker-compose stop
echo 서비스 재시작: docker-compose restart
echo 로그 확인: docker-compose logs -f
echo.
pause
