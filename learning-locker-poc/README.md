# Learning Locker LRS - POC 환경 구축 가이드

Learning Locker는 오픈소스 Learning Record Store (LRS)로, xAPI (Experience API) 표준을 준수하는 학습 활동 데이터를 수집, 저장, 분석할 수 있는 플랫폼입니다.

이 POC 환경은 Docker Compose를 사용하여 Learning Locker를 로컬에서 쉽게 설치하고 테스트할 수 있도록 구성되었습니다.

## 📋 목차

- [사전 요구사항](#사전-요구사항)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [초기 설정](#초기-설정)
- [xAPI Statement 전송 테스트](#xapi-statement-전송-테스트)
- [데이터 백업 및 복원](#데이터-백업-및-복원)
- [트러블슈팅](#트러블슈팅)
- [보안 설정](#보안-설정)
- [참고 자료](#참고-자료)

## 🔧 사전 요구사항

이 프로젝트를 실행하기 위해 다음 소프트웨어가 필요합니다:

- **Docker**: 20.10 이상
- **Docker Compose**: 2.0 이상
- **Python**: 3.7 이상 (테스트 스크립트 실행 시)
- **Git**: (선택사항)

### 설치 확인

```bash
docker --version
docker-compose --version
python3 --version
```

## 📁 프로젝트 구조

```
learning-locker-poc/
├── docker-compose.yml          # Docker Compose 설정
├── .env                         # 환경 변수 설정 (생성 필요)
├── .env.example                 # 환경 변수 예시
├── README.md                    # 이 파일
├── nginx/
│   └── nginx.conf              # Nginx 리버스 프록시 설정
├── scripts/
│   ├── setup.sh                # 초기 설정 스크립트
│   ├── test-statements.py      # xAPI Statement 테스트 스크립트
│   ├── backup.sh               # 데이터 백업 스크립트
│   └── restore.sh              # 데이터 복원 스크립트
├── sample-data/
│   └── xapi-statements.json    # 샘플 xAPI Statement
├── storage/
│   ├── mongo/                  # MongoDB 데이터 (자동 생성)
│   ├── redis/                  # Redis 데이터 (자동 생성)
│   └── app/                    # 애플리케이션 데이터 (자동 생성)
└── backups/                    # 백업 저장소 (자동 생성)
```

## 🚀 설치 및 실행

### 1단계: 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# 필요시 .env 파일 수정 (에디터로 열어서 편집)
nano .env
```

**중요**: 프로덕션 환경에서는 반드시 다음 값들을 변경하세요:
- `MONGO_ROOT_PASSWORD`
- `REDIS_PASSWORD`
- `APP_SECRET`
- `ADMIN_PASSWORD`

### 2단계: Docker 서비스 시작

```bash
# Docker Compose로 모든 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인 (문제 발생 시)
docker-compose logs -f
```

### 3단계: 서비스 준비 대기

모든 서비스가 완전히 시작될 때까지 2-3분 정도 기다립니다.

```bash
# 서비스 헬스체크
curl http://localhost/health

# Learning Locker API 확인
curl http://localhost:8080/health

# Learning Locker UI 확인
curl http://localhost:3000
```

## ⚙️ 초기 설정

### 관리자 계정 및 Organization 생성

Learning Locker UI에 처음 접속하면 수동으로 다음을 설정해야 합니다:

#### 1. Learning Locker UI 접속

```
URL: http://localhost
```

브라우저에서 위 주소로 접속합니다.

#### 2. 회원가입 및 로그인

- "Sign up" 버튼 클릭
- 이메일, 비밀번호 입력하여 관리자 계정 생성
- 생성한 계정으로 로그인

#### 3. Organization 생성

로그인 후 자동으로 Organization 생성 화면이 나타납니다:
- Organization Name: 예) "My Organization"
- 생성 버튼 클릭

#### 4. Store (LRS) 생성

1. 좌측 메뉴에서 "Settings" 클릭
2. "Stores" 탭 선택
3. "Add new" 버튼 클릭
4. Store 정보 입력:
   - Title: 예) "POC Store"
   - Description: 예) "POC Test Store for xAPI"
5. "Submit" 버튼 클릭

#### 5. Client 인증 정보 생성

xAPI Statement를 전송하려면 인증 정보가 필요합니다:

1. "Settings" > "Clients" 메뉴 선택
2. "Add new" 버튼 클릭
3. Client 정보 입력:
   - Title: 예) "Test Client"
   - Authority: 생성된 Store 선택
   - Scopes: "All" 또는 필요한 권한 선택
4. "Submit" 버튼 클릭
5. **생성된 Key와 Secret을 복사하여 안전하게 보관**
   - ⚠️ Secret은 생성 시 한 번만 표시되므로 반드시 저장하세요!

#### 접속 정보

| 서비스 | URL | 포트 |
|--------|-----|------|
| Learning Locker UI | http://localhost | 80 |
| Learning Locker API | http://localhost:8080 | 8080 |
| xAPI Endpoint | http://localhost/data/xAPI | 80 |
| MongoDB | localhost | 27017 |
| Redis | localhost | 6379 |

## 📤 xAPI Statement 전송 테스트

### Python 테스트 스크립트 사용

생성한 Client Key와 Secret을 사용하여 테스트 데이터를 전송합니다.

#### 1. Python 패키지 설치

```bash
pip install requests
```

#### 2. 테스트 스크립트 실행

```bash
# 환경 변수로 인증 정보 설정
export LRS_KEY="your_client_key_here"
export LRS_SECRET="your_client_secret_here"

# 테스트 스크립트 실행 (100개 Statement 생성)
python3 scripts/test-statements.py

# 또는 명령행 인자로 전달
python3 scripts/test-statements.py \
  --key "your_client_key_here" \
  --secret "your_client_secret_here" \
  --count 100 \
  --verify
```

#### 3. 옵션 설명

- `--endpoint`: LRS API 엔드포인트 (기본값: http://localhost/data/xAPI)
- `--key`: Client Key (필수)
- `--secret`: Client Secret (필수)
- `--count`: 생성할 Statement 개수 (기본값: 100)
- `--verify`: 전송 후 조회 테스트 실행

### cURL로 직접 전송

```bash
# 단일 Statement 전송 예시
curl -X POST http://localhost/data/xAPI/statements \
  -u "YOUR_KEY:YOUR_SECRET" \
  -H "X-Experience-API-Version: 1.0.3" \
  -H "Content-Type: application/json" \
  -d @sample-data/xapi-statements.json
```

### Statement 확인

1. Learning Locker UI에서 로그인
2. 좌측 메뉴에서 "Data" > "Statements" 선택
3. 전송된 Statement 목록 확인
4. "Visualisations" 메뉴에서 그래프와 차트로 데이터 시각화

## 💾 데이터 백업 및 복원

### 백업

```bash
# 전체 데이터 백업 (MongoDB + Redis)
./scripts/backup.sh
```

백업 파일은 `backups/backup_YYYYMMDD_HHMMSS.tar.gz` 형식으로 저장됩니다.

### 복원

```bash
# 백업 파일로부터 복원
./scripts/restore.sh backups/backup_20250115_143000.tar.gz
```

**경고**: 복원 시 현재 데이터가 모두 삭제됩니다!

### 자동 백업 설정 (선택사항)

cron을 사용하여 매일 자동 백업:

```bash
# crontab 편집
crontab -e

# 매일 새벽 2시에 백업 실행
0 2 * * * cd /path/to/learning-locker-poc && ./scripts/backup.sh >> backups/backup.log 2>&1
```

## 🔍 트러블슈팅

### 서비스가 시작되지 않는 경우

```bash
# 로그 확인
docker-compose logs ll_api
docker-compose logs ll_ui
docker-compose logs mongodb

# 서비스 재시작
docker-compose restart

# 완전히 재설치
docker-compose down -v
docker-compose up -d
```

### MongoDB 연결 오류

```bash
# MongoDB 컨테이너 상태 확인
docker-compose exec mongodb mongo \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin \
  --eval "db.adminCommand('ping')"
```

### Redis 연결 오류

```bash
# Redis 연결 테스트
docker-compose exec redis redis-cli -a redis123 ping
```

### Learning Locker API가 응답하지 않는 경우

```bash
# API 로그 확인
docker-compose logs -f ll_api

# API 컨테이너 재시작
docker-compose restart ll_api
```

### Statement 전송이 실패하는 경우

1. Client Key와 Secret이 올바른지 확인
2. Store가 활성화되어 있는지 확인
3. xAPI 엔드포인트 URL이 올바른지 확인 (`http://localhost/data/xAPI`)
4. Statement JSON 형식이 유효한지 확인

### 포트 충돌

기본 포트가 이미 사용 중인 경우 `docker-compose.yml`에서 포트를 변경:

```yaml
ports:
  - "8080:80"  # 80 대신 8080 사용
```

### 디스크 공간 부족

```bash
# 사용하지 않는 Docker 리소스 정리
docker system prune -a

# 오래된 백업 삭제 (30일 이상)
find backups/ -name "backup_*.tar.gz" -mtime +30 -delete
```

## 🔐 보안 설정

### 프로덕션 환경 체크리스트

- [ ] `.env` 파일의 모든 기본 비밀번호 변경
- [ ] `APP_SECRET`을 강력한 랜덤 문자열로 변경 (최소 32자)
- [ ] MongoDB 루트 비밀번호 변경
- [ ] Redis 비밀번호 변경
- [ ] 관리자 계정 비밀번호를 강력하게 설정
- [ ] HTTPS 설정 (SSL/TLS 인증서)
- [ ] 방화벽 설정 (필요한 포트만 개방)
- [ ] 정기적인 백업 스케줄 설정
- [ ] 로그 모니터링 설정

### 비밀번호 생성 예시

```bash
# 강력한 랜덤 비밀번호 생성
openssl rand -base64 32
```

### HTTPS 설정 (선택사항)

프로덕션 환경에서는 Let's Encrypt를 사용하여 SSL 인증서를 발급받고 Nginx에서 HTTPS를 설정하세요.

```bash
# Let's Encrypt Certbot 설치
apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급
certbot --nginx -d yourdomain.com
```

## 📊 성능 최적화

### MongoDB 인덱스 생성

```bash
# MongoDB 컨테이너 접속
docker-compose exec mongodb mongo \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin

# Learning Locker 데이터베이스 선택
use learninglocker;

# Statement 조회 성능 향상을 위한 인덱스 생성
db.statements.createIndex({"statement.timestamp": -1});
db.statements.createIndex({"statement.actor.mbox": 1});
db.statements.createIndex({"statement.verb.id": 1});
```

### Redis 메모리 설정

대량의 데이터를 처리하는 경우 Redis 메모리 제한을 늘리세요:

```yaml
# docker-compose.yml
redis:
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

## 📚 참고 자료

### Learning Locker

- [Learning Locker 공식 GitHub](https://github.com/LearningLocker/learninglocker)
- [Learning Locker 문서](https://docs.learninglocker.net/)

### xAPI (Experience API)

- [xAPI 공식 스펙](https://github.com/adlnet/xAPI-Spec)
- [xAPI 한국어 가이드](https://xapi.com/overview/)
- [ADL xAPI 공식 사이트](https://adlnet.gov/projects/xapi/)

### xAPI Statement 예시

- [xAPI 레시피](https://registry.tincanapi.com/)
- [xAPI Statement 생성기](https://xapi.com/statements-101/)

### Docker

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)

## 🤝 기여 및 문의

이 POC 환경에 대한 문의사항이나 개선 제안이 있으시면 이슈를 등록해 주세요.

## 📄 라이선스

이 POC 환경은 MIT 라이선스로 제공됩니다.
Learning Locker는 GPL-3.0 라이선스를 따릅니다.

---

**Learning Locker POC 환경 구축 완료!**

문제가 발생하거나 도움이 필요하시면 위의 트러블슈팅 섹션을 참고하거나 이슈를 등록해 주세요.
