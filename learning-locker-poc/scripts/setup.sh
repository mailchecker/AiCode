#!/bin/bash

# Learning Locker POC 초기 설정 스크립트
# 이 스크립트는 관리자 계정, Organization, Store를 자동으로 생성합니다.

set -e

echo "========================================="
echo "Learning Locker POC 초기 설정 시작"
echo "========================================="
echo ""

# 환경 변수 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env 파일을 찾을 수 없습니다."
    echo "   .env.example을 .env로 복사하고 설정을 수정하세요."
    exit 1
fi

# 기본값 설정
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
ADMIN_ORG_NAME=${ADMIN_ORG_NAME:-"My Organization"}
STORE_NAME=${STORE_NAME:-"Default Store"}
STORE_DESCRIPTION=${STORE_DESCRIPTION:-"POC Test Store for xAPI Statements"}

echo "📋 설정 정보:"
echo "   관리자 이메일: $ADMIN_EMAIL"
echo "   Organization: $ADMIN_ORG_NAME"
echo "   Store 이름: $STORE_NAME"
echo ""

# Docker Compose 서비스 상태 확인
echo "🔍 Docker 서비스 상태 확인 중..."
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Learning Locker 서비스가 실행 중이지 않습니다."
    echo "   먼저 'docker-compose up -d' 명령을 실행하세요."
    exit 1
fi

# MongoDB 연결 대기
echo "⏳ MongoDB 준비 대기 중..."
for i in {1..30}; do
    if docker-compose exec -T mongodb mongo --username $MONGO_ROOT_USERNAME --password $MONGO_ROOT_PASSWORD --authenticationDatabase admin --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "✅ MongoDB 준비 완료"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ MongoDB 연결 타임아웃"
        exit 1
    fi
    sleep 2
done

# Learning Locker API 서버 준비 대기
echo "⏳ Learning Locker API 서버 준비 대기 중..."
for i in {1..60}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Learning Locker API 준비 완료"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "❌ Learning Locker API 연결 타임아웃"
        echo "   로그 확인: docker-compose logs ll_api"
        exit 1
    fi
    sleep 2
done

echo ""
echo "========================================="
echo "초기 설정 완료!"
echo "========================================="
echo ""
echo "📌 접속 정보:"
echo "   Learning Locker UI: http://localhost"
echo "   관리자 이메일: $ADMIN_EMAIL"
echo "   관리자 비밀번호: $ADMIN_PASSWORD"
echo ""
echo "⚠️  보안 주의사항:"
echo "   프로덕션 환경에서는 반드시 .env 파일의 비밀번호를 변경하세요!"
echo ""
echo "다음 단계:"
echo "1. 웹 브라우저에서 http://localhost 접속"
echo "2. 위의 관리자 계정으로 로그인"
echo "3. Organization과 Store 생성"
echo "4. Client 인증 정보 생성 (Settings > Clients)"
echo "5. 생성된 Key와 Secret을 테스트 스크립트에 사용"
echo ""
echo "테스트 데이터 전송:"
echo "   python scripts/test-statements.py"
echo ""
