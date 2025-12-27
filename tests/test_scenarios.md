# PDF RAG Chatbot System - 테스트 시나리오

## 테스트 환경 준비

### 1. 시스템 시작

```bash
# Docker Compose로 전체 시스템 시작
docker-compose up -d

# 모든 서비스가 healthy 상태인지 확인
docker-compose ps

# 로그 확인
docker-compose logs -f backend
```

### 2. API 접근 확인

```bash
# Health check
curl http://localhost:8000/health

# API 문서 확인
# 브라우저에서 http://localhost:8000/docs 접속
```

### 3. Streamlit UI 확인

```bash
# 브라우저에서 http://localhost:8501 접속
```

## 테스트 시나리오

### 시나리오 1: Local Parser를 사용한 PDF 업로드 및 검색

#### 목적
로컬 파서의 기본적인 PDF 파싱 및 검색 기능을 테스트

#### 단계

1. **PDF 준비**
   - 간단한 텍스트 PDF 파일 준비 (10-20페이지)
   - 예: 기술 문서, 논문, 교재 등

2. **업로드**
   ```bash
   curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@sample.pdf" \
     -F "title=테스트 문서 1" \
     -F "parse_provider=local"
   ```

3. **상태 확인**
   - 응답에서 `doc_id`와 `version_id` 확인
   - 상태 조회:
   ```bash
   curl "http://localhost:8000/documents/{doc_id}/versions/{version_id}/status"
   ```
   - 상태가 `uploaded → parsing → parsed → indexing → indexed`로 변경되는지 확인

4. **검색 테스트**
   - 문서 내용 중 특정 키워드로 검색:
   ```bash
   curl -X POST "http://localhost:8000/search/" \
     -H "Content-Type: application/json" \
     -d '{"query": "키워드", "top_k": 5}'
   ```

5. **챗봇 테스트**
   ```bash
   curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{"query": "문서의 주요 내용을 요약해주세요", "top_k": 5}'
   ```

#### 예상 결과
- 파싱 시간: 10페이지 기준 10-30초
- 검색 결과: 관련 문단 5개 반환
- 챗봇 답변: 검색된 내용 기반 요약 제공

---

### 시나리오 2: Upstage Parser를 사용한 고급 파싱

#### 목적
Upstage API를 사용한 비동기 파싱 및 polling 메커니즘 테스트

#### 단계

1. **PDF 준비**
   - 복잡한 레이아웃의 PDF (표, 그림 포함)
   - 예: 보험 약관, 법률 문서 등

2. **업로드**
   ```bash
   curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@complex_document.pdf" \
     -F "title=복잡한 문서" \
     -F "parse_provider=upstage"
   ```

3. **비동기 처리 모니터링**
   - Celery parse worker 로그 확인:
   ```bash
   docker-compose logs -f celery-parse
   ```
   - Polling 진행 상황 확인
   - Upstage API 응답 시간 측정

4. **파싱 완료 확인**
   - 최종 상태가 `indexed`가 될 때까지 대기
   - MinIO에서 결과 JSON 확인:
     - MinIO Console (http://localhost:9001) 접속
     - `parsed-json` 버킷 확인

5. **품질 검증**
   - 검색 테스트로 표 데이터가 제대로 추출되었는지 확인
   - 그림 캡션이 포함되었는지 확인

#### 예상 결과
- 파싱 시간: 100페이지 기준 2-5분
- Upstage 배치별 JSON 다운로드 성공
- 정규화된 JSON 저장 확인

---

### 시나리오 3: 하이브리드 검색 성능 비교

#### 목적
BM25, Vector, Hybrid 검색의 성능 차이 확인

#### 단계

1. **동일 쿼리로 3가지 검색 실행**

   a. BM25 검색:
   ```bash
   curl -X POST "http://localhost:8000/search/bm25" \
     -H "Content-Type: application/json" \
     -d '{"query": "보험 윤리", "top_k": 10}'
   ```

   b. Vector 검색:
   ```bash
   curl -X POST "http://localhost:8000/search/vector" \
     -H "Content-Type: application/json" \
     -d '{"query": "보험 윤리", "top_k": 10}'
   ```

   c. Hybrid 검색:
   ```bash
   curl -X POST "http://localhost:8000/search/" \
     -H "Content-Type: application/json" \
     -d '{"query": "보험 윤리", "top_k": 10}'
   ```

2. **결과 비교**
   - 각 검색 방법의 상위 5개 결과 비교
   - Score 차이 분석
   - 관련성 평가

#### 예상 결과
- BM25: 키워드 정확히 일치하는 문단 우선
- Vector: 의미적으로 유사한 문단 포함
- Hybrid: 균형잡힌 결과

---

### 시나리오 4: 임베딩 모델 교체 테스트

#### 목적
임베딩 제공자 변경 및 재색인 테스트

#### 단계

1. **현재 임베딩 확인**
   - `.env`에서 `EMBEDDING_PROVIDER=kure` 확인

2. **OpenAI 임베딩으로 변경**
   ```bash
   # .env 파일 수정
   EMBEDDING_PROVIDER=openai
   EMBEDDING_MODEL=text-embedding-3-small
   EMBEDDING_DIMENSION=1536
   ```

3. **서비스 재시작**
   ```bash
   docker-compose restart backend celery-index
   ```

4. **Elasticsearch 인덱스 재생성**
   ```bash
   # 기존 인덱스 삭제
   curl -X DELETE "http://localhost:9200/textbook_chunks"

   # Backend 재시작하여 새 인덱스 생성
   docker-compose restart backend
   ```

5. **문서 재색인**
   - 기존 문서를 다시 업로드하거나
   - API를 통해 재색인 트리거

6. **검색 성능 비교**
   - 동일 쿼리로 검색
   - KURE vs OpenAI 결과 비교

#### 예상 결과
- 임베딩 차원 변경 확인
- 검색 결과 차이 확인

---

### 시나리오 5: 대용량 문서 처리

#### 목적
200페이지 이상 대용량 문서의 처리 성능 테스트

#### 단계

1. **대용량 PDF 준비**
   - 200-300페이지 교재 PDF

2. **업로드 및 타이머 시작**
   ```bash
   time curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@large_textbook.pdf" \
     -F "title=대용량 교재" \
     -F "parse_provider=upstage"
   ```

3. **처리 단계별 시간 측정**
   - 업로드 시간
   - 파싱 시간 (Upstage API)
   - 청킹 시간
   - 임베딩 생성 시간
   - Elasticsearch 색인 시간

4. **리소스 모니터링**
   ```bash
   docker stats
   ```

5. **최종 검증**
   - 모든 청크가 색인되었는지 확인:
   ```bash
   curl "http://localhost:9200/textbook_chunks/_count"
   ```

#### 예상 결과
- 200페이지 기준 전체 처리 시간: 5-15분
- 메모리 사용량 모니터링
- 청크 개수: 약 400-800개

---

### 시나리오 6: 멱등성 테스트

#### 목적
동일 문서 중복 업로드 시 멱등성 보장 확인

#### 단계

1. **첫 번째 업로드**
   ```bash
   curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@test.pdf" \
     -F "title=멱등성 테스트" \
     -F "doc_id=idempotent-test-1" \
     -F "version_id=v1" \
     -F "parse_provider=local"
   ```

2. **완료 대기**
   - 상태가 `indexed`가 될 때까지 대기

3. **동일 파일 재업로드**
   ```bash
   curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@test.pdf" \
     -F "title=멱등성 테스트" \
     -F "doc_id=idempotent-test-1" \
     -F "version_id=v1" \
     -F "parse_provider=local"
   ```

4. **응답 확인**
   - "Document already exists" 메시지 확인
   - 중복 처리가 발생하지 않았는지 확인

5. **데이터베이스 확인**
   ```bash
   # document_versions 테이블에 중복 레코드가 없는지 확인
   docker exec -it pdf-rag-backend sqlite3 /app/data/app.db \
     "SELECT * FROM document_versions WHERE doc_id='idempotent-test-1';"
   ```

#### 예상 결과
- 두 번째 업로드 시 즉시 응답
- 중복 파싱/색인 작업 없음

---

### 시나리오 7: RAG 답변 품질 테스트

#### 목적
챗봇의 답변 품질 및 출처 추적 검증

#### 단계

1. **문서 내용 기반 질문**
   ```bash
   curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "보험설계사의 윤리강령에 대해 설명해주세요",
       "top_k": 5
     }'
   ```

2. **응답 검증**
   - `has_answer`: true 확인
   - `answer`: 내용이 교재 기반인지 확인
   - `sources`: 페이지 번호와 출처 확인

3. **교재 외 질문**
   ```bash
   curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "오늘 날씨가 어때?",
       "top_k": 5
     }'
   ```

4. **응답 검증**
   - `has_answer`: false 또는
   - "교재에서 관련 내용을 찾을 수 없습니다" 메시지 확인

5. **출처 검증**
   - 반환된 페이지 번호가 실제 PDF와 일치하는지 확인
   - 출처 문단이 답변과 관련있는지 확인

#### 예상 결과
- 교재 기반 질문: 정확한 답변 + 출처
- 교재 외 질문: 명확한 거부 응답

---

### 시나리오 8: 에러 처리 및 복구

#### 목적
시스템 장애 시 복구 메커니즘 테스트

#### 단계

1. **Elasticsearch 다운 시뮬레이션**
   ```bash
   docker-compose stop elasticsearch
   ```

2. **검색 요청**
   - 적절한 에러 메시지 반환 확인

3. **Elasticsearch 복구**
   ```bash
   docker-compose start elasticsearch
   # 헬스체크 대기
   sleep 30
   ```

4. **검색 재개**
   - 정상 작동 확인

5. **Celery Worker 다운 시뮬레이션**
   ```bash
   docker-compose stop celery-parse
   ```

6. **PDF 업로드**
   - 업로드는 성공하지만 파싱이 진행되지 않음 확인

7. **Worker 복구**
   ```bash
   docker-compose start celery-parse
   ```

8. **파싱 재개**
   - Worker가 큐에 있던 작업 처리 확인

#### 예상 결과
- 각 컴포넌트 장애 시 적절한 에러 처리
- 복구 후 정상 작동

---

## 성능 벤치마크

### 측정 항목

1. **파싱 속도**
   - Local: 페이지당 평균 시간
   - Upstage: 페이지당 평균 시간

2. **색인 속도**
   - 청크당 임베딩 생성 시간
   - Elasticsearch bulk 색인 속도

3. **검색 응답 시간**
   - BM25: p50, p95, p99
   - Vector: p50, p95, p99
   - Hybrid: p50, p95, p99

4. **RAG 응답 시간**
   - 검색 시간
   - LLM 생성 시간
   - 총 응답 시간

### 목표 성능

- 파싱 (Local): 1-3초/페이지
- 파싱 (Upstage): 2-5초/페이지
- 검색 응답: < 500ms
- RAG 응답: < 5초

---

## 자동 테스트 스크립트

### 전체 시나리오 실행

```bash
#!/bin/bash

echo "=== PDF RAG System Test ==="

# 1. Health Check
echo "1. Health Check..."
curl -s http://localhost:8000/health | jq

# 2. Upload Test
echo "2. Uploading test document..."
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/documents/upload" \
  -F "file=@tests/test_data/sample.pdf" \
  -F "title=Test Document" \
  -F "parse_provider=local")

DOC_ID=$(echo $UPLOAD_RESPONSE | jq -r '.doc_id')
VERSION_ID=$(echo $UPLOAD_RESPONSE | jq -r '.version_id')

echo "Document ID: $DOC_ID"
echo "Version ID: $VERSION_ID"

# 3. Wait for indexing
echo "3. Waiting for indexing..."
while true; do
  STATUS=$(curl -s "http://localhost:8000/documents/$DOC_ID/versions/$VERSION_ID/status" | jq -r '.status')
  echo "Current status: $STATUS"

  if [ "$STATUS" = "indexed" ]; then
    echo "Indexing completed!"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Indexing failed!"
    exit 1
  fi

  sleep 5
done

# 4. Search Test
echo "4. Testing search..."
curl -s -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"test\", \"top_k\": 3}" | jq

# 5. Chat Test
echo "5. Testing chat..."
curl -s -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"이 문서의 주요 내용은?\", \"top_k\": 3}" | jq

echo "=== Test Completed ==="
```

---

## 테스트 체크리스트

- [ ] 시스템 시작 및 모든 서비스 healthy
- [ ] Local parser 업로드 및 파싱
- [ ] Upstage parser 업로드 및 파싱
- [ ] BM25 검색 작동
- [ ] Vector 검색 작동
- [ ] Hybrid 검색 작동
- [ ] RAG 챗봇 답변 생성
- [ ] 출처 추적 정확성
- [ ] 멱등성 보장
- [ ] 임베딩 모델 교체
- [ ] 대용량 문서 처리
- [ ] 에러 처리 및 복구
- [ ] Streamlit UI 작동
- [ ] API 문서 접근
- [ ] 성능 벤치마크
