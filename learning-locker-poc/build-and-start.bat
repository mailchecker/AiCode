@echo off
chcp 65001 >nul
REM Learning Locker - 빌드 및 시작 스크립트
REM GitHub 소스코드에서 직접 빌드합니다

echo ============================================================
echo Learning Locker POC - 빌드 및 시작
echo ============================================================
echo.
echo 이 스크립트는 Learning Locker를 GitHub에서 빌드합니다.
echo 최초 빌드 시 20-30분이 소요될 수 있습니다.
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [경고] 관리자 권한으로 실행하는 것을 권장합니다.
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

echo [1/5] Docker 확인 완료
echo.

REM 디스크 공간 확인
echo [2/5] 시스템 요구사항 확인 중...
echo.
echo 필요한 디스크 공간: 최소 10GB
echo 빌드 시간: 20-30분 (최초 빌드)
echo.

set /p CONTINUE=계속하시겠습니까? (Y/N):
if /i not "%CONTINUE%"=="Y" (
    echo.
    echo 빌드 취소됨
    pause
    exit /b 0
)

echo.

REM .env 파일 확인
if not exist .env (
    echo [3/5] .env 파일 생성 중...
    copy .env.example .env >nul
    echo .env 파일이 생성되었습니다.
) else (
    echo [3/5] .env 파일 확인 완료
)
echo.

REM 기존 컨테이너 정리
echo [4/5] 기존 컨테이너 정리 중...
docker-compose down >nul 2>&1
echo 정리 완료
echo.

REM Docker 이미지 빌드
echo [5/5] Learning Locker 빌드 시작...
echo.
echo ⚠️  주의: 이 과정은 20-30분이 걸릴 수 있습니다!
echo.
echo 빌드 단계:
echo   1. GitHub에서 소스코드 다운로드 (~200MB)
echo   2. Node.js 패키지 설치 (~500MB)
echo   3. TypeScript 컴파일
echo   4. React UI 빌드
echo   5. Docker 이미지 생성 (~1.5GB)
echo.
echo 빌드 진행 상황을 확인하려면 별도 터미널에서:
echo   docker-compose build --progress=plain
echo.

REM 빌드 시작 시간 기록
echo 빌드 시작 시간: %time%
echo.

REM Docker Compose 빌드
docker-compose build

if errorlevel 1 (
    echo.
    echo ============================================================
    echo [오류] 빌드 실패
    echo ============================================================
    echo.
    echo 문제 해결:
    echo   1. 인터넷 연결 확인
    echo   2. 디스크 공간 확인 (최소 10GB 필요)
    echo   3. Docker Desktop 메모리 설정 (최소 6GB 권장)
    echo   4. 로그 확인: docker-compose build --progress=plain
    echo.
    echo 자세한 가이드: BUILD-GUIDE.md 참고
    echo.
    pause
    exit /b 1
)

echo.
echo 빌드 완료 시간: %time%
echo.

REM 빌드된 이미지 확인
echo ============================================================
echo 빌드 완료!
echo ============================================================
echo.

docker images learninglocker-custom

echo.
echo 이제 서비스를 시작합니다...
echo.

REM 서비스 시작
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

REM 서비스 준비 대기
echo.
echo 서비스 준비 중... (60초 대기)
echo.
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
echo   4. Client 인증 정보 생성
echo   5. test-statements.bat 실행
echo.
echo 상세 가이드:
echo   - README.md: 사용 가이드
echo   - BUILD-GUIDE.md: 빌드 가이드
echo   - WINDOWS_GUIDE.md: Windows 전용 가이드
echo.

REM 브라우저 자동 열기
set /p OPEN_BROWSER=브라우저를 여시겠습니까? (Y/N):
if /i "%OPEN_BROWSER%"=="Y" (
    start http://localhost
)

echo.
echo 유용한 명령어:
echo   서비스 중지: docker-compose stop
echo   서비스 재시작: docker-compose restart
echo   로그 확인: docker-compose logs -f
echo   빌드 재시작: docker-compose build --no-cache
echo.
pause
