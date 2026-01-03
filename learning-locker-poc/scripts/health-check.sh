#!/bin/bash

# Learning Locker 서비스 헬스체크 스크립트
# 모든 서비스의 상태를 확인합니다.

echo "========================================="
echo "Learning Locker 서비스 헬스체크"
echo "========================================="
echo ""

# 색상 코드
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 헬스체크 함수
check_service() {
    local name=$1
    local url=$2
    local timeout=${3:-5}

    echo -n "🔍 $name: "

    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Docker 서비스 상태 확인
echo "📦 Docker 컨테이너 상태:"
docker-compose ps
echo ""

# 각 서비스 헬스체크
total=0
passed=0

# Nginx
check_service "Nginx" "http://localhost/health" && ((passed++))
((total++))

# Learning Locker UI
check_service "Learning Locker UI" "http://localhost:3000" && ((passed++))
((total++))

# Learning Locker API
check_service "Learning Locker API" "http://localhost:8080/health" && ((passed++))
((total++))

# MongoDB
echo -n "🔍 MongoDB: "
if docker-compose exec -T mongodb mongo --quiet --eval "db.adminCommand('ping').ok" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
    ((passed++))
else
    echo -e "${RED}❌ FAILED${NC}"
fi
((total++))

# Redis
echo -n "🔍 Redis: "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
    ((passed++))
else
    echo -e "${RED}❌ FAILED${NC}"
fi
((total++))

echo ""
echo "========================================="
echo "결과: $passed/$total 서비스 정상"
echo "========================================="

if [ $passed -eq $total ]; then
    echo -e "${GREEN}모든 서비스가 정상 작동 중입니다!${NC}"
    exit 0
else
    echo -e "${RED}일부 서비스에 문제가 있습니다.${NC}"
    echo "문제 해결:"
    echo "  1. 로그 확인: docker-compose logs -f"
    echo "  2. 서비스 재시작: docker-compose restart"
    echo "  3. 전체 재시작: docker-compose down && docker-compose up -d"
    exit 1
fi
