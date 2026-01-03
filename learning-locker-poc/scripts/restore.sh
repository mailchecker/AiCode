#!/bin/bash

# Learning Locker 데이터 복원 스크립트
# 백업된 MongoDB와 Redis 데이터를 복원합니다.

set -e

# 사용법 확인
if [ $# -eq 0 ]; then
    echo "사용법: $0 <백업파일.tar.gz>"
    echo ""
    echo "예시: $0 backups/backup_20250115_143000.tar.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 백업 파일을 찾을 수 없습니다: $BACKUP_FILE"
    exit 1
fi

# 환경 변수 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env 파일을 찾을 수 없습니다."
    exit 1
fi

echo "========================================="
echo "Learning Locker 데이터 복원"
echo "========================================="
echo ""
echo "백업 파일: $BACKUP_FILE"
echo ""

# 경고 메시지
echo "⚠️  경고: 현재 데이터가 모두 삭제되고 백업 데이터로 대체됩니다!"
read -p "계속하시겠습니까? (yes/no): " -r
echo ""
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "복원 취소됨"
    exit 0
fi

# 임시 디렉토리 생성
TEMP_DIR=$(mktemp -d)
echo "📂 임시 디렉토리: $TEMP_DIR"

# 백업 파일 압축 해제
echo "📦 백업 파일 압축 해제 중..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# 압축 해제된 디렉토리 찾기
BACKUP_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "backup_*" | head -n 1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ 백업 디렉토리를 찾을 수 없습니다."
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ 압축 해제 완료: $BACKUP_DIR"

# 백업 정보 표시
if [ -f "$BACKUP_DIR/backup_info.txt" ]; then
    echo ""
    echo "백업 정보:"
    cat "$BACKUP_DIR/backup_info.txt"
    echo ""
fi

# MongoDB 복원
if [ -f "$BACKUP_DIR/mongodb_backup.archive" ]; then
    echo "🔄 MongoDB 복원 중..."

    # 백업 파일을 컨테이너로 복사
    docker cp "$BACKUP_DIR/mongodb_backup.archive" ll_mongodb:/tmp/mongodb_backup.archive

    # MongoDB 복원 실행
    docker-compose exec -T mongodb mongorestore \
        --username "$MONGO_ROOT_USERNAME" \
        --password "$MONGO_ROOT_PASSWORD" \
        --authenticationDatabase admin \
        --db "$MONGO_DB" \
        --archive=/tmp/mongodb_backup.archive \
        --gzip \
        --drop

    # 임시 파일 삭제
    docker-compose exec -T mongodb rm /tmp/mongodb_backup.archive

    echo "✅ MongoDB 복원 완료"
else
    echo "⚠️  MongoDB 백업 파일이 없습니다."
fi

# Redis 복원
if [ -f "$BACKUP_DIR/redis_dump.rdb" ]; then
    echo "🔄 Redis 복원 중..."

    # Redis 서비스 일시 중지
    docker-compose stop redis

    # 백업 파일을 컨테이너 볼륨으로 복사
    docker cp "$BACKUP_DIR/redis_dump.rdb" ll_redis:/data/dump.rdb

    # Redis 서비스 재시작
    docker-compose start redis

    # Redis 준비 대기
    sleep 5

    echo "✅ Redis 복원 완료"
else
    echo "⚠️  Redis 백업 파일이 없습니다."
fi

# 임시 디렉토리 정리
rm -rf "$TEMP_DIR"

echo ""
echo "========================================="
echo "복원 완료!"
echo "========================================="
echo ""
echo "Learning Locker 서비스를 재시작하는 것이 좋습니다:"
echo "  docker-compose restart"
echo ""
