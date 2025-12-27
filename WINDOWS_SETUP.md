# PDF RAG Chatbot System - Windows 설치 가이드

Windows에서 PDF RAG Chatbot System을 설치하고 실행하는 방법을 안내합니다.

## 사전 요구사항

### 1. Docker Desktop for Windows 설치

#### 시스템 요구사항
- Windows 10 64-bit (Pro, Enterprise, Education) 또는 Windows 11
- WSL 2 기능 활성화
- 최소 4GB RAM (8GB 이상 권장)
- BIOS에서 가상화 활성화

#### Docker Desktop 설치 단계

1. **Docker Desktop 다운로드**
   - [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 접속
   - "Download for Windows" 클릭

2. **설치 파일 실행**
   - 다운로드한 `Docker Desktop Installer.exe` 실행
   - "Use WSL 2 instead of Hyper-V" 옵션 체크 (권장)
   - 설치 완료 후 재부팅

3. **Docker Desktop 실행**
   - 시작 메뉴에서 "Docker Desktop" 실행
   - 초기 설정 완료 (로그인은 선택사항)
   - 하단 상태 표시줄에서 "Docker Desktop is running" 확인

4. **설치 확인**
   ```cmd
   docker --version
   docker-compose --version
   ```

### 2. Git for Windows 설치 (선택사항)

코드를 Git으로 받으려면:
- [Git for Windows](https://git-scm.com/download/win) 다운로드 및 설치

### 3. API 키 준비

- **OpenAI API 키** (필수)
  - [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급

- **Upstage API 키** (선택사항)
  - [Upstage Console](https://console.upstage.ai/)에서 발급
  - 고급 PDF 파싱 기능 사용 시 필요

## 설치 방법

### 방법 1: Git Clone (권장)

1. **저장소 클론**
   ```cmd
   git clone <repository-url>
   cd AiCode
   ```

### 방법 2: ZIP 다운로드

1. GitHub에서 "Code" → "Download ZIP" 클릭
2. ZIP 파일 압축 해제
3. 명령 프롬프트에서 해당 폴더로 이동
   ```cmd
   cd C:\path\to\AiCode
   ```

## 환경 설정

### 1. 환경 변수 파일 생성

프로젝트 루트 폴더에서:

```cmd
copy .env.example .env
```

### 2. API 키 설정

메모장이나 VSCode로 `.env` 파일 열기:

```cmd
notepad .env
```

다음 항목 수정:

```env
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Upstage API 키 (선택사항)
UPSTAGE_API_KEY=up_your-actual-upstage-api-key-here

# 기타 설정은 기본값 사용 가능
```

저장 후 닫기 (Ctrl+S)

## 실행 방법

### 빠른 시작 (추천)

1. **Docker Desktop이 실행 중인지 확인**

2. **시작 스크립트 실행**

   파일 탐색기에서 `start.bat` 더블클릭

   또는 명령 프롬프트에서:
   ```cmd
   start.bat
   ```

3. **자동으로 브라우저가 열리면 사용 시작**
   - Streamlit UI: http://localhost:8501

### 수동 시작

```cmd
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 재시작
docker-compose restart backend
```

## 접속 주소

시스템이 시작되면 다음 주소로 접속 가능:

- **📱 Streamlit UI**: http://localhost:8501
- **📚 API 문서**: http://localhost:8000/docs
- **🗄️ MinIO 콘솔**: http://localhost:9001
  - ID: `minioadmin`
  - PW: `minioadmin`

## 사용 방법

### 1. PDF 업로드

1. Streamlit UI (http://localhost:8501) 접속
2. "📤 업로드" 탭 클릭
3. PDF 파일 선택
4. 문서 제목 입력
5. 파서 선택:
   - **local**: 빠른 기본 파서
   - **upstage**: 고급 AI 파서 (Upstage API 키 필요)
6. "업로드 및 처리 시작" 클릭
7. 처리 상태 실시간 확인

### 2. 문서 검색

1. "🔍 검색" 탭 클릭
2. 검색어 입력
3. (선택) 사이드바에서 특정 문서 선택
4. "검색" 버튼 클릭
5. 결과 확인

### 3. AI 챗봇

1. "💬 챗봇" 탭 클릭
2. 질문 입력 (예: "이 문서의 주요 내용은?")
3. AI 답변 및 출처 확인

## 문제 해결

### Docker Desktop이 시작되지 않는 경우

1. **WSL 2 설치 확인**
   ```powershell
   wsl --list --verbose
   ```

2. **WSL 2 업데이트**
   ```powershell
   wsl --update
   ```

3. **Windows 업데이트 확인**
   - 설정 → 업데이트 및 보안 → 최신 상태 확인

### "Virtualization is not enabled" 오류

1. BIOS 설정에서 가상화 활성화
   - 재부팅 → BIOS 진입 (F2, Del, F10 등)
   - Intel: VT-x 활성화
   - AMD: AMD-V 활성화

### "Docker daemon is not running" 오류

1. Docker Desktop 실행
2. 시스템 트레이에서 Docker 아이콘 확인
3. 초록불 확인 (실행 중)

### 포트 충돌 오류

다른 프로그램이 포트를 사용 중인 경우:

1. **사용 중인 포트 확인**
   ```cmd
   netstat -ano | findstr :8000
   netstat -ano | findstr :8501
   netstat -ano | findstr :9200
   ```

2. **프로세스 종료**
   ```cmd
   taskkill /PID <프로세스ID> /F
   ```

3. 또는 `docker-compose.yml`에서 포트 변경

### Elasticsearch 메모리 부족

1. Docker Desktop 설정
   - 설정 → Resources
   - Memory를 6GB 이상으로 증가
   - Apply & Restart

### 한글 파일명 문제

1. 파일명은 영문으로 변경 권장
2. 문서 제목은 한글 사용 가능

## 시스템 관리

### 로그 확인

```cmd
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f celery-parse
docker-compose logs -f elasticsearch
```

### 서비스 재시작

```cmd
# 전체 재시작
docker-compose restart

# 특정 서비스만
docker-compose restart backend
docker-compose restart frontend
```

### 시스템 중지

```cmd
# 서비스만 중지 (데이터 유지)
docker-compose down

# 데이터까지 모두 삭제
docker-compose down -v
```

### 디스크 공간 정리

```cmd
# 사용하지 않는 Docker 이미지/컨테이너 삭제
docker system prune -a

# 볼륨까지 삭제
docker system prune -a --volumes
```

## 성능 최적화 (Windows)

### Docker Desktop 리소스 할당

1. Docker Desktop 설정 열기
2. Resources → Advanced
3. 권장 설정:
   - **CPU**: 4 cores 이상
   - **Memory**: 8GB 이상
   - **Swap**: 2GB
   - **Disk image size**: 60GB 이상

### WSL 2 성능 최적화

1. **`.wslconfig` 파일 생성** (C:\Users\<사용자명>\.wslconfig)
   ```ini
   [wsl2]
   memory=8GB
   processors=4
   swap=2GB
   ```

2. **WSL 재시작**
   ```powershell
   wsl --shutdown
   ```

## 개발 환경 설정 (선택사항)

### Visual Studio Code 설정

1. **VSCode 설치**
   - [Visual Studio Code](https://code.visualstudio.com/) 다운로드

2. **확장 프로그램 설치**
   - Docker
   - Python
   - Remote - WSL

3. **프로젝트 열기**
   ```cmd
   code .
   ```

### Python 개발 환경 (로컬 개발용)

1. **Python 3.10 설치**
   - [Python.org](https://www.python.org/downloads/) 다운로드
   - "Add Python to PATH" 체크

2. **가상환경 생성**
   ```cmd
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 백업 및 복원

### 데이터 백업

```cmd
# Docker 볼륨 백업
docker run --rm -v aicode_minio_data:/data -v %CD%:/backup ubuntu tar czf /backup/minio_backup.tar.gz /data
docker run --rm -v aicode_backend_data:/data -v %CD%:/backup ubuntu tar czf /backup/backend_backup.tar.gz /data
```

### 데이터 복원

```cmd
# Docker 볼륨 복원
docker run --rm -v aicode_minio_data:/data -v %CD%:/backup ubuntu tar xzf /backup/minio_backup.tar.gz -C /
docker run --rm -v aicode_backend_data:/data -v %CD%:/backup ubuntu tar xzf /backup/backend_backup.tar.gz -C /
```

## 업데이트

### 코드 업데이트

```cmd
# Git Pull
git pull origin main

# 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Docker 이미지 업데이트

```cmd
docker-compose pull
docker-compose up -d
```

## 자주 묻는 질문 (FAQ)

### Q: Windows 10 Home에서 사용 가능한가요?
A: 네, WSL 2를 사용하면 가능합니다. Docker Desktop 최신 버전을 설치하세요.

### Q: 오프라인에서 사용 가능한가요?
A: 일부 가능합니다. PDF 파싱과 검색은 오프라인 가능하지만, OpenAI API는 인터넷 연결이 필요합니다.

### Q: GPU를 사용할 수 있나요?
A: WSL 2에서 NVIDIA GPU 사용 가능합니다. CUDA 설정이 필요합니다.

### Q: 한국어 PDF도 잘 작동하나요?
A: 네, KURE-v1 임베딩은 한국어 특화 모델입니다.

## 추가 도움말

- 상세 문서: `README.md`
- 테스트 가이드: `tests/test_scenarios.md`
- 이슈 제보: GitHub Issues

## 라이선스

MIT License

---

Windows 환경에서 문제가 발생하면 이슈를 등록해주세요!
