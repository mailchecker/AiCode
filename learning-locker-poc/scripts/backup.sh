#!/bin/bash

# Learning Locker 데이터 백업 스크립트
# MongoDB 데이터베이스와 Redis 데이터를 백업합니다.

set -e

# 환경 변수 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env 파일을 찾을 수 없습니다."
    exit 1
fi

# 백업 디렉토리 설정
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

echo "========================================="
echo "Learning Locker 데이터 백업"
echo "========================================="
echo ""
echo "백업 경로: $BACKUP_PATH"
echo ""

# 백업 디렉토리 생성
mkdir -p "$BACKUP_PATH"

# MongoDB 백업
echo "📦 MongoDB 백업 중..."
docker-compose exec -T mongodb mongodump \
    --username "$MONGO_ROOT_USERNAME" \
    --password "$MONGO_ROOT_PASSWORD" \
    --authenticationDatabase admin \
    --db "$MONGO_DB" \
    --archive=/tmp/mongodb_backup.archive \
    --gzip

# 백업 파일 컨테이너에서 호스트로 복사
docker cp ll_mongodb:/tmp/mongodb_backup.archive "$BACKUP_PATH/mongodb_backup.archive"
docker-compose exec -T mongodb rm /tmp/mongodb_backup.archive

echo "✅ MongoDB 백업 완료: $BACKUP_PATH/mongodb_backup.archive"

# Redis 백업 (RDB 파일)
echo "📦 Redis 백업 중..."
docker-compose exec -T redis redis-cli -a "$REDIS_PASSWORD" SAVE > /dev/null 2>&1 || true
docker cp ll_redis:/data/dump.rdb "$BACKUP_PATH/redis_dump.rdb" 2>/dev/null || echo "⚠️  Redis 백업 파일이 없습니다."

if [ -f "$BACKUP_PATH/redis_dump.rdb" ]; then
    echo "✅ Redis 백업 완료: $BACKUP_PATH/redis_dump.rdb"
fi

# 백업 정보 저장
cat > "$BACKUP_PATH/backup_info.txt" << EOF
Learning Locker 백업 정보
========================
백업 일시: $(date)
MongoDB 데이터베이스: $MONGO_DB
MongoDB 사용자: $MONGO_ROOT_USERNAME
Learning Locker 도메인: $DOMAIN_NAME
EOF

echo "✅ 백업 정보 저장 완료: $BACKUP_PATH/backup_info.txt"

# 백업 파일 압축
echo "🗜️  백업 파일 압축 중..."
cd "$BACKUP_DIR"
tar -czf "backup_$TIMESTAMP.tar.gz" "backup_$TIMESTAMP"
rm -rf "backup_$TIMESTAMP"
cd - > /dev/null

echo "✅ 백업 압축 완료: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# 백업 파일 크기 표시
BACKUP_SIZE=$(du -h "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" | cut -f1)
echo ""
echo "========================================="
echo "백업 완료!"
echo "========================================="
echo "파일: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
echo "크기: $BACKUP_SIZE"
echo ""
echo "복원 방법:"
echo "  ./scripts/restore.sh $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
echo ""

# 오래된 백업 정리 (30일 이상 된 백업 삭제)
echo "🧹 오래된 백업 정리 중..."
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete 2>/dev/null || true
echo "✅ 정리 완료"
echo ""
