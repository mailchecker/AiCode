# PDF RAG Chatbot System

대용량 교재 PDF를 업로드하여 비동기 파싱, 검색, RAG 기반 챗봇을 제공하는 백엔드 중심 시스템입니다.

## 시스템 개요

### 핵심 기능

1. **PDF 업로드 및 파싱**
   - 로컬 파서 (PyMuPDF 기반 빠른 텍스트 추출)
   - Upstage API 파서 (고급 AI 기반 문서 파싱)
   - 비동기 처리 및 상태 추적

2. **검색 엔진**
   - BM25 키워드 검색
   - 벡터 유사도 검색
   - 하이브리드 검색 (BM25 + Vector)

3. **RAG 챗봇**
   - Haystack 기반 RAG 파이프라인
   - 한국어 특화 KURE-v1 임베딩
   - OpenAI GPT-4 기반 답변 생성
   - 출처 추적 및 검증

## 기술 스택

### 고정 기술 스택

- **Backend Framework**: Python 3.10 + FastAPI
- **Object Storage**: MinIO (S3 호환)
- **Task Queue**: Celery + Redis
- **Database**: SQLite
- **Search Engine**: Elasticsearch 8.12
- **RAG Framework**: Haystack
- **LLM**: OpenAI GPT-4
- **Embedding (기본)**: nlpai-lab/KURE-v1 (한국어 특화)
- **PDF Parsing**:
  - Local: PyMuPDF
  - External: Upstage Document AI

### 교체 가능 구성요소

- **Embedding Provider**: KURE-v1, OpenAI, E5, BGE
- **LLM Model**: GPT-4, GPT-3.5, 기타 OpenAI 호환 모델

## 시스템 아키텍처

```
┌─────────────┐
│  Streamlit  │  Frontend (포트 8501)
│     UI      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FastAPI   │  Backend API (포트 8000)
│   Backend   │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
   ┌──────┐      ┌──────┐      ┌──────────┐   ┌────────┐
   │MinIO │      │Redis │      │Elastic-  │   │SQLite  │
   │      │      │      │      │ search   │   │        │
   └──────┘      └──┬───┘      └──────────┘   └────────┘
                    │
           ┌────────┴────────┐
           ▼                 ▼
    ┌─────────────┐   ┌─────────────┐
    │Celery Worker│   │Celery Worker│
    │(Parse Queue)│   │(Index Queue)│
    └─────────────┘   └─────────────┘
```

## 데이터 흐름

### 1. PDF 업로드 및 파싱

```
1. 사용자 PDF 업로드
   ↓
2. MinIO에 원본 PDF 저장
   ↓
3. SQLite에 문서 메타데이터 저장
   ↓
4. Celery Parse Task 실행
   ↓
5-a. [Local] PyMuPDF로 즉시 파싱
5-b. [Upstage] API 요청 → Polling → JSON 다운로드
   ↓
6. 결과를 표준 JSON 스키마로 정규화
   ↓
7. MinIO에 정규화된 JSON 저장
   ↓
8. Celery Index Task 트리거
```

### 2. 색인 파이프라인

```
1. MinIO에서 정규화된 JSON 다운로드
   ↓
2. Header/Footer 제거
   ↓
3. 텍스트 청킹 (500-900 토큰, 10-20% 오버랩)
   ↓
4. KURE-v1로 임베딩 생성
   ↓
5. Elasticsearch에 Bulk 색인
   - Text (BM25용)
   - Embedding (Vector 검색용)
   - Metadata (필터링용)
```

### 3. RAG 검색 및 생성

```
1. 사용자 질문 입력
   ↓
2. Hybrid Search (BM25 + Vector)
   ↓
3. Top-K 문단 검색
   ↓
4. 컨텍스트 구성
   ↓
5. GPT-4에 프롬프트 전송
   ↓
6. 답변 생성 + 출처 반환
```

## 설치 및 실행

### 사전 요구사항

- Docker 및 Docker Compose
- OpenAI API 키
- (선택) Upstage API 키

### 빠른 시작

#### Linux / macOS

```bash
# 1. 저장소 클론
git clone <repository-url>
cd AiCode

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 OpenAI API 키 추가

# 3. 시스템 시작
./start.sh
```

#### Windows

```cmd
REM 1. 저장소 클론
git clone <repository-url>
cd AiCode

REM 2. 환경 변수 설정
copy .env.example .env
REM .env 파일을 편집하여 OpenAI API 키 추가

REM 3. 시스템 시작 (더블클릭 또는)
start.bat
```

**Windows 사용자**: 자세한 설치 가이드는 [`WINDOWS_SETUP.md`](WINDOWS_SETUP.md)를 참고하세요.

### 상세 설치 단계

#### 1. 저장소 클론

```bash
git clone <repository-url>
cd AiCode
```

#### 2. 환경 변수 설정

`.env` 파일을 수정하여 필수 API 키를 설정하세요:

**Linux/macOS:**
```bash
cp .env.example .env
nano .env  # 또는 원하는 에디터 사용
```

**Windows:**
```cmd
copy .env.example .env
notepad .env
```

**필수 설정:**
```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=your_openai_api_key_here

# Upstage API 키 (Upstage 파서 사용 시 필수)
UPSTAGE_API_KEY=your_upstage_api_key_here
```

#### 3. Docker Compose 실행

**Linux/macOS:**
```bash
# 전체 시스템 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스만 재시작
docker-compose restart backend
```

**Windows:**
```cmd
REM 전체 시스템 시작
docker-compose up -d

REM 로그 확인
docker-compose logs -f

REM 특정 서비스만 재시작
docker-compose restart backend
```

#### 4. 서비스 접속

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Elasticsearch**: http://localhost:9200

## 사용 방법

### Streamlit UI 사용

1. **PDF 업로드**
   - "📤 업로드" 탭 선택
   - PDF 파일 선택 및 제목 입력
   - 파서 선택 (local 또는 upstage)
   - 업로드 버튼 클릭
   - 처리 상태 실시간 모니터링

2. **문서 검색**
   - "🔍 검색" 탭 선택
   - 검색어 입력
   - 사이드바에서 특정 문서 선택 (선택사항)
   - 검색 결과 확인

3. **AI 챗봇**
   - "💬 챗봇" 탭 선택
   - 질문 입력
   - AI 답변 및 출처 확인

### API 사용

#### 문서 업로드

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@sample.pdf" \
  -F "title=샘플 교재" \
  -F "parse_provider=local"
```

#### 검색

```bash
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "보험윤리란?", "top_k": 5}'
```

#### 챗봇

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"query": "보험설계사의 윤리강령에 대해 설명해주세요", "top_k": 5}'
```

## 디렉토리 구조

```
AiCode/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── documents.py    # 문서 관리 API
│   │   │   ├── search.py       # 검색 API
│   │   │   └── chat.py         # 챗봇 API
│   │   ├── services/
│   │   │   ├── minio_service.py
│   │   │   ├── elasticsearch_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── chunking.py
│   │   │   ├── pdf_parser/
│   │   │   │   ├── local_parser.py
│   │   │   │   └── upstage_parser.py
│   │   │   └── rag/
│   │   │       └── haystack_pipeline.py
│   │   ├── tasks/
│   │   │   ├── celery_app.py
│   │   │   ├── parse_tasks.py
│   │   │   └── index_tasks.py
│   │   ├── models.py           # SQLAlchemy 모델
│   │   ├── schemas.py          # Pydantic 스키마
│   │   ├── database.py         # DB 연결
│   │   ├── config.py           # 설정
│   │   └── main.py             # FastAPI 앱
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── tests/
│   ├── test_data/
│   ├── test_scenarios.md
│   └── create_sample_pdf.py
├── docker-compose.yml
├── start.sh              # Linux/macOS 시작 스크립트
├── start.bat             # Windows 시작 스크립트
├── .env
├── .env.example
├── .gitignore
├── README.md
└── WINDOWS_SETUP.md      # Windows 전용 설치 가이드
```

## 주요 설정

### 임베딩 모델 변경

`.env` 파일에서 설정:

```bash
# KURE-v1 (기본, 한국어 특화)
EMBEDDING_PROVIDER=kure
EMBEDDING_MODEL=nlpai-lab/KURE-v1
EMBEDDING_DIMENSION=768

# OpenAI
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# E5
EMBEDDING_PROVIDER=e5
EMBEDDING_MODEL=intfloat/multilingual-e5-large
EMBEDDING_DIMENSION=1024

# BGE
EMBEDDING_PROVIDER=bge
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024
```

**주의**: 임베딩 모델 변경 시 Elasticsearch 인덱스 재생성 필요

### 청킹 설정

```bash
CHUNK_SIZE=700          # 청크 크기 (토큰)
CHUNK_OVERLAP=140       # 오버랩 (토큰)
```

### RAG 설정

```bash
TOP_K_RETRIEVAL=5       # 검색 시 상위 K개
LLM_MODEL=gpt-4         # LLM 모델
LLM_TEMPERATURE=0.1     # 생성 온도
LLM_MAX_TOKENS=1000     # 최대 토큰
```

## 데이터베이스 스키마

### documents 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| doc_id | String (PK) | 문서 ID |
| title | String | 문서 제목 |
| created_at | DateTime | 생성 시각 |
| latest_version_id | String | 최신 버전 ID |

### document_versions 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer (PK) | 자동 증가 ID |
| doc_id | String (FK) | 문서 ID |
| version_id | String | 버전 ID |
| pdf_uri | String | PDF MinIO URI |
| pdf_hash | String | PDF SHA256 해시 |
| parse_provider | String | 파서 종류 (local/upstage) |
| parse_request_id | String | 외부 파싱 요청 ID |
| status | String | 상태 (uploaded/parsing/parsed/indexing/indexed/failed) |
| result_json_uri | String | 결과 JSON MinIO URI |
| attempt_count | Integer | 시도 횟수 |
| last_error | String | 마지막 오류 |
| created_at | DateTime | 생성 시각 |
| updated_at | DateTime | 수정 시각 |

## 트러블슈팅

### Elasticsearch 메모리 부족

```bash
# docker-compose.yml에서 힙 크기 조정
ES_JAVA_OPTS=-Xms2g -Xmx2g
```

**Windows**: Docker Desktop 설정에서 메모리를 6GB 이상으로 증가
- Docker Desktop → Settings → Resources → Memory

### Celery Worker 재시작

```bash
docker-compose restart celery-parse celery-index
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스
docker-compose logs -f backend
docker-compose logs -f celery-parse
```

### 데이터 초기화

```bash
# 모든 데이터 삭제 (주의!)
docker-compose down -v

# 재시작
docker-compose up -d
```

### Windows 전용 문제 해결

#### Docker Desktop이 시작되지 않는 경우
1. WSL 2 설치 확인: `wsl --list --verbose`
2. WSL 2 업데이트: `wsl --update`
3. Windows 업데이트 확인

#### 포트 충돌 오류
```cmd
REM 사용 중인 포트 확인
netstat -ano | findstr :8000
netstat -ano | findstr :8501

REM 프로세스 종료
taskkill /PID <프로세스ID> /F
```

자세한 Windows 문제 해결은 [`WINDOWS_SETUP.md`](WINDOWS_SETUP.md)를 참고하세요.

## 성능 최적화

### Celery Worker 동시성 증가

`docker-compose.yml`에서 `--concurrency` 값 조정:

```yaml
command: celery -A app.tasks.celery_app worker --loglevel=info --queues=parse_queue --concurrency=4
```

### Elasticsearch 샤드 설정

대용량 데이터의 경우 샤드 수 조정 필요

### 배치 크기 조정

`elasticsearch_service.py`에서 bulk 배치 크기 조정

## 보안 고려사항

1. **프로덕션 환경**
   - MinIO 기본 자격증명 변경
   - Elasticsearch 보안 활성화
   - API 인증 추가

2. **API 키 관리**
   - `.env` 파일을 절대 커밋하지 말 것
   - 환경별로 다른 키 사용

3. **네트워크**
   - 필요한 포트만 외부 노출
   - 내부 서비스 간 통신은 Docker 네트워크 사용

## 라이선스

MIT License

## 문의

이슈가 있으면 GitHub Issues를 통해 문의해주세요.
