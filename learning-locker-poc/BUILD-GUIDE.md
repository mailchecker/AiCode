# Learning Locker v2 빌드 가이드

이 가이드는 Learning Locker v2를 GitHub 소스코드에서 직접 빌드하는 방법을 설명합니다.

## 왜 직접 빌드해야 하나요?

Learning Locker v2의 공식 Docker 이미지가 Docker Hub에서 더 이상 제공되지 않습니다.
따라서 GitHub 저장소에서 소스코드를 받아 직접 빌드해야 합니다.

## 사전 요구사항

- **Docker Desktop**: 실행 중이어야 함
- **디스크 공간**: 최소 10GB 여유 공간
- **RAM**: 최소 8GB (빌드 시 4GB 사용)
- **인터넷 연결**: 소스코드 다운로드 및 패키지 설치

## 빌드 시간

- **최초 빌드**: 20-30분 소요 (인터넷 속도에 따라 다름)
- **재빌드**: 5-10분 (캐시 사용)

---

## Windows에서 빌드

### 방법 1: 자동 빌드 스크립트 (권장)

```powershell
# PowerShell 관리자 권한으로 실행
cd D:\dev\AiCode\AiCode\AiCode\learning-locker-poc

# 빌드 및 시작 스크립트 실행
.\build-and-start.bat
```

### 방법 2: 수동 빌드

```powershell
# 1. learning-locker-poc 폴더로 이동
cd D:\dev\AiCode\AiCode\AiCode\learning-locker-poc

# 2. 기존 컨테이너 정리 (있다면)
docker-compose down -v

# 3. Docker 이미지 빌드 (20-30분 소요)
docker-compose build

# 4. 서비스 시작
docker-compose up -d

# 5. 빌드 진행 상황 확인
docker-compose logs -f ll_api
```

---

## Linux/Mac에서 빌드

```bash
# 1. learning-locker-poc 폴더로 이동
cd learning-locker-poc

# 2. 기존 컨테이너 정리 (있다면)
docker-compose down -v

# 3. Docker 이미지 빌드
docker-compose build

# 4. 서비스 시작
docker-compose up -d

# 5. 로그 확인
docker-compose logs -f
```

---

## 빌드 과정 설명

### 1단계: 소스코드 다운로드
```
Downloading Learning Locker v2.8.0 from GitHub...
```
- GitHub에서 Learning Locker v2.8.0 소스코드 클론
- 약 200MB 다운로드

### 2단계: 의존성 설치
```
Installing dependencies...
- xapi-service
- cli
- api
- ui
- worker
```
- Node.js 패키지 설치 (yarn)
- 약 500MB 패키지 다운로드

### 3단계: 빌드
```
Building components...
- xapi-service: Compiling TypeScript...
- api: Compiling TypeScript...
- ui: Compiling React app...
- worker: Compiling TypeScript...
```
- TypeScript → JavaScript 컴파일
- React UI 빌드

### 4단계: Docker 이미지 생성
```
Creating Docker image: learninglocker-custom:latest
Size: ~1.5GB
```

---

## 빌드 진행 상황 확인

### PowerShell/CMD (Windows)

```powershell
# 빌드 로그 실시간 확인
docker-compose build --progress=plain

# 특정 서비스만 빌드
docker-compose build ll_api

# 캐시 없이 처음부터 다시 빌드
docker-compose build --no-cache
```

### 빌드 완료 확인

```powershell
# 이미지 확인
docker images | findstr learninglocker

# 예상 출력:
# learninglocker-custom   latest   abc123def456   5 minutes ago   1.5GB
```

---

## 빌드 후 실행

### 1. 서비스 시작

```powershell
docker-compose up -d
```

### 2. 상태 확인

```powershell
# 컨테이너 상태
docker-compose ps

# 로그 확인
docker-compose logs -f ll_api
docker-compose logs -f ll_ui
```

### 3. 브라우저 접속

```
http://localhost
```

---

## 문제 해결

### 빌드 실패: "out of memory"

**원인**: Docker 메모리 부족

**해결**:
1. Docker Desktop 설정
2. Resources > Memory 증가 (최소 6GB)
3. 다시 빌드

### 빌드 실패: "yarn install failed"

**원인**: 네트워크 오류 또는 패키지 서버 문제

**해결**:
```powershell
# 캐시 삭제 후 재시도
docker-compose build --no-cache
```

### 빌드 실패: "git clone failed"

**원인**: GitHub 접속 불가 또는 방화벽

**해결**:
1. 인터넷 연결 확인
2. 방화벽 설정 확인
3. GitHub 접속 가능 여부 확인:
```powershell
ping github.com
```

### 빌드가 너무 느림

**원인**: 인터넷 속도 또는 Docker 성능

**최적화**:
1. Docker Desktop 설정
   - Resources > CPUs: 4개 이상
   - Resources > Memory: 6GB 이상
2. WSL 2 사용 (Windows)
3. SSD 사용

### 디스크 공간 부족

**확인**:
```powershell
docker system df
```

**정리**:
```powershell
# 사용하지 않는 이미지/컨테이너 삭제
docker system prune -a

# 빌드 캐시 삭제
docker builder prune
```

---

## 빌드 캐시 활용

Docker는 빌드 캐시를 사용하여 재빌드 시간을 단축합니다.

### 캐시 사용 (빠름)
```powershell
docker-compose build
```

### 캐시 무시 (느림, 깨끗한 빌드)
```powershell
docker-compose build --no-cache
```

### 특정 단계부터 재빌드
```powershell
# Dockerfile 수정 후 해당 단계부터 재빌드
docker-compose build
```

---

## 빌드된 이미지 관리

### 이미지 확인
```powershell
docker images learninglocker-custom
```

### 이미지 삭제
```powershell
# 컨테이너 먼저 중지
docker-compose down

# 이미지 삭제
docker rmi learninglocker-custom:latest
```

### 이미지 백업/공유

```powershell
# 이미지를 tar 파일로 저장
docker save learninglocker-custom:latest -o learninglocker-custom.tar

# 다른 PC에서 로드
docker load -i learninglocker-custom.tar
```

---

## 커스터마이징

### Learning Locker 버전 변경

`Dockerfile` 수정:
```dockerfile
# v2.8.0 대신 다른 버전
RUN git clone --depth 1 --branch v2.7.0 https://github.com/LearningLocker/learninglocker.git .
```

### Node.js 버전 변경

`Dockerfile` 수정:
```dockerfile
# Node.js 14 대신 16 사용
FROM node:16-alpine
```

---

## 빌드 시간 단축 팁

1. **멀티스테이지 빌드**: 이미 적용됨
2. **BuildKit 사용**: Docker 19.03 이상에서 자동 활성화
3. **.dockerignore**: 불필요한 파일 제외 (이미 설정됨)
4. **레이어 캐싱**: 자주 변경되지 않는 명령을 앞에 배치 (이미 최적화됨)

---

## 참고 자료

- [Learning Locker GitHub](https://github.com/LearningLocker/learninglocker)
- [Docker Build 문서](https://docs.docker.com/engine/reference/commandline/build/)
- [Docker Compose Build 문서](https://docs.docker.com/compose/reference/build/)

---

## 도움이 필요하신가요?

빌드 중 문제가 발생하면:
1. 로그 전체 복사: `docker-compose build > build.log 2>&1`
2. `build.log` 파일 확인
3. 오류 메시지와 함께 이슈 등록

---

**빌드가 완료되면 `docker-compose up -d`로 서비스를 시작하세요!** 🚀
