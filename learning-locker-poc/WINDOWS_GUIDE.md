# Windows PC에서 Learning Locker 구동 가이드

이 문서는 Windows 10/11 환경에서 Learning Locker POC 환경을 구축하고 실행하는 방법을 설명합니다.

## 📋 목차

- [사전 요구사항](#사전-요구사항)
- [1단계: Docker Desktop 설치](#1단계-docker-desktop-설치)
- [2단계: 프로젝트 다운로드](#2단계-프로젝트-다운로드)
- [3단계: 환경 설정](#3단계-환경-설정)
- [4단계: Docker 실행](#4단계-docker-실행)
- [5단계: Learning Locker 접속 및 설정](#5단계-learning-locker-접속-및-설정)
- [6단계: 테스트 데이터 전송](#6단계-테스트-데이터-전송)
- [Windows 전용 명령어](#windows-전용-명령어)
- [문제 해결](#문제-해결)

## 🔧 사전 요구사항

### 시스템 요구사항

- **운영체제**: Windows 10 64-bit Pro/Enterprise/Education (Build 19041 이상) 또는 Windows 11
- **하드웨어**:
  - RAM 최소 8GB (권장 16GB)
  - 저장 공간 최소 20GB
  - CPU 가상화 지원 (BIOS에서 활성화 필요)

### 필요한 소프트웨어

1. **Docker Desktop for Windows**
2. **Git for Windows** (선택사항 - 코드 다운로드용)
3. **Python 3.7+** (테스트 스크립트 실행용)
4. **텍스트 에디터** (메모장, VS Code, Notepad++ 등)

## 1단계: Docker Desktop 설치

### 1-1. Docker Desktop 다운로드

1. Docker 공식 사이트 접속: https://www.docker.com/products/docker-desktop
2. "Download for Windows" 버튼 클릭
3. `Docker Desktop Installer.exe` 다운로드

### 1-2. Docker Desktop 설치

1. 다운로드한 `Docker Desktop Installer.exe` 실행
2. 설치 옵션:
   - ✅ "Use WSL 2 instead of Hyper-V" 체크 (권장)
   - ✅ "Add shortcut to desktop" 체크
3. "Ok" 클릭하여 설치 시작
4. 설치 완료 후 재부팅

### 1-3. Docker Desktop 설정

1. Docker Desktop 실행
2. 설정 확인:
   - Settings > General > "Use the WSL 2 based engine" 체크
   - Settings > Resources > 메모리 최소 4GB 할당
3. 설정 저장 후 Docker Desktop 재시작

### 1-4. 설치 확인

**PowerShell** 또는 **명령 프롬프트(CMD)** 실행:

```powershell
docker --version
docker-compose --version
```

출력 예시:
```
Docker version 24.0.7, build afdd53b
Docker Compose version v2.23.0
```

## 2단계: 프로젝트 다운로드

### 방법 1: Git 사용 (권장)

**Git Bash** 또는 **PowerShell**에서 실행:

```powershell
# 원하는 위치로 이동 (예: 내 문서)
cd C:\Users\YourUsername\Documents

# Git 클론 (실제 저장소 URL로 변경)
git clone https://github.com/your-repo/AiCode.git
cd AiCode\learning-locker-poc
```

### 방법 2: ZIP 다운로드

1. GitHub에서 프로젝트 페이지 접속
2. "Code" > "Download ZIP" 클릭
3. 다운로드한 ZIP 파일 압축 해제
4. `learning-locker-poc` 폴더로 이동

## 3단계: 환경 설정

### 3-1. 환경 변수 파일 생성

**PowerShell**에서 실행:

```powershell
# learning-locker-poc 폴더로 이동
cd C:\Users\YourUsername\Documents\AiCode\learning-locker-poc

# .env 파일 생성
copy .env.example .env
```

또는 **파일 탐색기**에서:
1. `learning-locker-poc` 폴더 열기
2. `.env.example` 파일을 복사
3. 이름을 `.env`로 변경

### 3-2. .env 파일 편집

메모장 또는 VS Code로 `.env` 파일 열기:

```powershell
notepad .env
```

**중요: 다음 항목을 반드시 변경하세요!**

```env
# 강력한 비밀번호로 변경
MONGO_ROOT_PASSWORD=여기에_강력한_비밀번호_입력
REDIS_PASSWORD=여기에_강력한_비밀번호_입력
APP_SECRET=여기에_32자_이상의_긴_비밀키_입력
ADMIN_PASSWORD=여기에_관리자_비밀번호_입력

# 관리자 이메일 (실제 이메일로 변경)
ADMIN_EMAIL=your-email@example.com
```

저장 후 닫기 (Ctrl+S)

## 4단계: Docker 실행

### 4-1. Docker Desktop 실행 확인

1. 작업 표시줄에서 Docker 아이콘 확인
2. 초록색이면 실행 중 (회색이면 시작 대기 중)

### 4-2. Learning Locker 서비스 시작

**PowerShell** 또는 **CMD**를 **관리자 권한**으로 실행:

```powershell
# learning-locker-poc 폴더로 이동
cd C:\Users\YourUsername\Documents\AiCode\learning-locker-poc

# Docker Compose로 서비스 시작
docker-compose up -d
```

**출력 예시:**
```
[+] Running 6/6
 ✔ Network ll_network           Created
 ✔ Container ll_mongodb          Started
 ✔ Container ll_redis            Started
 ✔ Container ll_api              Started
 ✔ Container ll_ui               Started
 ✔ Container ll_worker           Started
 ✔ Container ll_nginx            Started
```

### 4-3. 서비스 상태 확인

```powershell
# 실행 중인 컨테이너 확인
docker-compose ps
```

**모든 서비스가 "Up" 상태여야 합니다.**

### 4-4. 서비스 준비 대기

모든 서비스가 완전히 시작될 때까지 2-3분 대기 후:

```powershell
# 웹 브라우저에서 접속 테스트
start http://localhost
```

또는 수동으로 브라우저에서 `http://localhost` 접속

## 5단계: Learning Locker 접속 및 설정

### 5-1. 웹 브라우저 접속

- **URL**: http://localhost
- 추천 브라우저: Chrome, Edge, Firefox

### 5-2. 회원가입

1. "Sign up" 버튼 클릭
2. 정보 입력:
   - Email: `.env`에 설정한 이메일
   - Password: 강력한 비밀번호
   - Confirm Password: 동일한 비밀번호
3. "Sign up" 버튼 클릭

### 5-3. Organization 생성

1. 자동으로 Organization 생성 화면 표시
2. Organization Name 입력 (예: "우리 회사")
3. "Create" 버튼 클릭

### 5-4. Store (LRS) 생성

1. 좌측 메뉴 "Settings" 클릭
2. "Stores" 탭 선택
3. "Add new" 버튼 클릭
4. Store 정보 입력:
   ```
   Title: POC Store
   Description: POC 테스트용 Learning Record Store
   ```
5. "Submit" 버튼 클릭

### 5-5. Client 인증 정보 생성

1. "Settings" > "Clients" 메뉴 선택
2. "Add new" 버튼 클릭
3. Client 정보 입력:
   ```
   Title: Test Client
   Authority: (생성한 Store 선택)
   Scopes: All 선택
   ```
4. "Submit" 버튼 클릭

### 5-6. ⚠️ 중요: Key와 Secret 저장

Client 생성 후 표시되는 **Key**와 **Secret**을 복사하여 메모장에 저장:

```
Key: 아주_긴_키_문자열
Secret: 아주_긴_시크릿_문자열
```

**주의**: Secret은 이 순간에만 표시됩니다! 반드시 저장하세요!

## 6단계: 테스트 데이터 전송

### 6-1. Python 설치 확인

**PowerShell**에서:

```powershell
python --version
```

Python이 설치되지 않은 경우: https://www.python.org/downloads/ 에서 다운로드

### 6-2. Python 패키지 설치

```powershell
# learning-locker-poc 폴더에서
cd C:\Users\YourUsername\Documents\AiCode\learning-locker-poc

# requests 패키지 설치
pip install requests
```

또는 requirements.txt 사용:

```powershell
pip install -r requirements.txt
```

### 6-3. 테스트 스크립트 실행

**방법 1: 환경 변수 사용 (PowerShell)**

```powershell
# 환경 변수 설정
$env:LRS_KEY = "위에서_복사한_Key"
$env:LRS_SECRET = "위에서_복사한_Secret"

# 테스트 스크립트 실행 (100개 Statement 생성)
python scripts\test-statements.py --count 100 --verify
```

**방법 2: 직접 인자 전달**

```powershell
python scripts\test-statements.py `
  --key "위에서_복사한_Key" `
  --secret "위에서_복사한_Secret" `
  --count 100 `
  --verify
```

### 6-4. 결과 확인

성공 시 출력 예시:
```
============================================================
Learning Locker xAPI Statement 테스트
============================================================
엔드포인트: http://localhost/data/xAPI
Key: 1a2b3c4d5e...
생성할 Statement 수: 100
============================================================

📝 100개의 샘플 Statement 생성 중...
✅ 100개의 Statement 생성 완료

📤 Statement 전송 중...
✅ Statement 전송 성공: 12345678-1234-5678-1234-567812345678
✅ Statement 전송 성공: 22345678-1234-5678-1234-567812345678
...
============================================================
전송 완료: 100/100 성공
============================================================
```

### 6-5. Learning Locker UI에서 확인

1. 브라우저에서 http://localhost 접속
2. 좌측 메뉴 "Data" > "Statements" 클릭
3. 전송된 100개의 Statement 확인
4. "Visualisations" 메뉴에서 그래프 생성

## 🪟 Windows 전용 명령어

### PowerShell 명령어 모음

```powershell
# 현재 디렉토리 확인
pwd

# 디렉토리 이동
cd C:\Users\YourUsername\Documents\AiCode\learning-locker-poc

# 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f ll_api

# 서비스 중지
docker-compose stop

# 서비스 재시작
docker-compose restart

# 서비스 완전 삭제 (데이터 포함)
docker-compose down -v

# 서비스 완전 삭제 (데이터 보존)
docker-compose down

# 브라우저에서 열기
start http://localhost
```

### 데이터 백업 (PowerShell)

```powershell
# 백업 디렉토리 생성
mkdir -Force backups

# MongoDB 백업
docker-compose exec mongodb mongodump `
  --username admin `
  --password admin123 `
  --authenticationDatabase admin `
  --db learninglocker `
  --archive=/tmp/backup.archive `
  --gzip

# 백업 파일 복사
docker cp ll_mongodb:/tmp/backup.archive backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').archive
```

### 데이터 복원 (PowerShell)

```powershell
# 백업 파일을 컨테이너로 복사
docker cp backups\backup_20250103_120000.archive ll_mongodb:/tmp/restore.archive

# MongoDB 복원
docker-compose exec mongodb mongorestore `
  --username admin `
  --password admin123 `
  --authenticationDatabase admin `
  --db learninglocker `
  --archive=/tmp/restore.archive `
  --gzip `
  --drop
```

## 🔧 문제 해결

### 문제 1: "Docker daemon이 실행되지 않음" 오류

**증상:**
```
error during connect: This error may indicate that the docker daemon is not running
```

**해결:**
1. Docker Desktop 실행
2. 작업 표시줄에서 Docker 아이콘이 초록색인지 확인
3. Docker Desktop이 완전히 시작될 때까지 대기 (1-2분)

### 문제 2: "포트가 이미 사용 중" 오류

**증상:**
```
Error: bind: address already in use
```

**해결:**
1. 이미 사용 중인 프로그램 확인:
   ```powershell
   netstat -ano | findstr :80
   netstat -ano | findstr :3000
   netstat -ano | findstr :8080
   ```

2. `docker-compose.yml` 파일에서 포트 변경:
   ```yaml
   nginx:
     ports:
       - "8080:80"  # 80 대신 8080 사용
   ```

### 문제 3: WSL 2 관련 오류

**증상:**
```
WSL 2 installation is incomplete
```

**해결:**
1. Windows 기능 켜기/끄기에서 다음 활성화:
   - ✅ Linux용 Windows 하위 시스템
   - ✅ 가상 머신 플랫폼
2. PowerShell (관리자)에서 실행:
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```
3. PC 재부팅

### 문제 4: 서비스가 시작되지 않음

**해결:**

```powershell
# 로그 확인
docker-compose logs -f

# 모든 컨테이너 중지 및 삭제
docker-compose down -v

# 다시 시작
docker-compose up -d
```

### 문제 5: "permission denied" 또는 "access denied" 오류

**해결:**
1. PowerShell을 **관리자 권한**으로 실행
2. Docker Desktop 설정에서 파일 공유 확인:
   - Settings > Resources > File Sharing
   - 프로젝트 폴더의 드라이브(예: C:) 추가

### 문제 6: Python 스크립트 실행 오류

**증상:**
```
ModuleNotFoundError: No module named 'requests'
```

**해결:**
```powershell
pip install requests
# 또는
pip install -r requirements.txt
```

### 문제 7: 방화벽 경고

Windows Defender 방화벽 경고가 표시되면:
- "액세스 허용" 클릭
- 개인 및 공용 네트워크 모두 체크

### 문제 8: 디스크 공간 부족

**해결:**

```powershell
# 사용하지 않는 Docker 이미지/컨테이너 삭제
docker system prune -a

# 디스크 사용량 확인
docker system df
```

## 📊 성능 팁

### Docker Desktop 리소스 최적화

1. Docker Desktop 설정:
   - Settings > Resources
   - **CPUs**: 4개 (또는 CPU 코어의 절반)
   - **Memory**: 6GB (또는 RAM의 절반)
   - **Swap**: 2GB
   - **Disk image size**: 60GB

2. WSL 2 메모리 제한 설정:

   `C:\Users\YourUsername\.wslconfig` 파일 생성:
   ```ini
   [wsl2]
   memory=6GB
   processors=4
   swap=2GB
   ```

## 🎯 다음 단계

1. ✅ Learning Locker UI에서 대시보드 확인
2. ✅ Visualisations 메뉴에서 학습 통계 그래프 생성
3. ✅ xAPI 쿼리로 특정 데이터 조회
4. ✅ 정기 백업 스케줄 설정 (Windows 작업 스케줄러 사용)

## 📚 추가 자료

- [Docker Desktop for Windows 공식 문서](https://docs.docker.com/desktop/windows/)
- [WSL 2 설치 가이드](https://docs.microsoft.com/ko-kr/windows/wsl/install)
- [Learning Locker 공식 문서](https://docs.learninglocker.net/)
- [xAPI 스펙](https://github.com/adlnet/xAPI-Spec)

## 💡 유용한 팁

### 자동 시작 설정

Docker Desktop이 Windows 시작 시 자동 실행되도록 설정:
1. Docker Desktop > Settings > General
2. ✅ "Start Docker Desktop when you log in" 체크

### 단축키 생성

Learning Locker UI 바로가기 만들기:
1. 바탕화면 우클릭 > 새로 만들기 > 바로 가기
2. 위치: `http://localhost`
3. 이름: "Learning Locker"

---

**Windows에서 Learning Locker POC 환경 구축 완료!**

문제가 발생하면 위의 문제 해결 섹션을 참고하거나 이슈를 등록해 주세요.
