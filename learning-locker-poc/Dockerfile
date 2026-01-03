# Learning Locker v2 Dockerfile
# GitHub 저장소에서 직접 빌드

# Debian Buster가 EOL되어 archive 저장소 사용
FROM node:10-buster-slim

LABEL maintainer="Learning Locker POC"
LABEL description="Learning Locker LRS - xAPI Learning Record Store"

# 작업 디렉토리 설정
WORKDIR /opt/learninglocker

# Debian Buster가 EOL되어 archive 저장소로 변경
# security 업데이트는 EOL 이후 제공되지 않으므로 제거
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/buster\/updates/d' /etc/apt/sources.list && \
    sed -i '/buster-updates/d' /etc/apt/sources.list && \
    echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/99no-check-valid-until

# 필수 패키지 및 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python \
    python-dev \
    build-essential \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Learning Locker v2 소스코드 클론
# v2.8.0이 마지막 안정 버전
RUN git clone --depth 1 --branch v2.8.0 https://github.com/LearningLocker/learninglocker.git . || \
    git clone --depth 1 https://github.com/LearningLocker/learninglocker.git .

# Yarn 버전 확인
RUN yarn --version

# node-gyp 전역 설치
RUN npm install -g node-gyp

# xAPI 서비스 설치 및 빌드
WORKDIR /opt/learninglocker/xapi-service
RUN yarn install --production --frozen-lockfile --ignore-engines && \
    yarn build

# 메인 애플리케이션으로 돌아가기
WORKDIR /opt/learninglocker

# 의존성 설치 (--ignore-engines 추가)
RUN yarn install --production --frozen-lockfile --ignore-engines --network-timeout 600000

# CLI 빌드
WORKDIR /opt/learninglocker/cli
RUN yarn install --production --frozen-lockfile --ignore-engines && \
    yarn build

# API 빌드
WORKDIR /opt/learninglocker/api
RUN yarn install --production --frozen-lockfile --ignore-engines && \
    yarn build

# UI 빌드
WORKDIR /opt/learninglocker/ui
RUN yarn install --production --frozen-lockfile --ignore-engines && \
    yarn build-all

# Worker 빌드
WORKDIR /opt/learninglocker/worker
RUN yarn install --production --frozen-lockfile --ignore-engines && \
    yarn build

# 루트로 돌아가기
WORKDIR /opt/learninglocker

# 빌드 도구 정리 (이미지 크기 감소)
RUN apt-get purge -y --auto-remove \
    python-dev \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 스토리지 디렉토리 생성
RUN mkdir -p /opt/learninglocker/storage

# 포트 설정
EXPOSE 3000 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --spider -q http://localhost:8080/health || exit 1

# 기본 명령어 (docker-compose에서 override)
CMD ["node", "api/dist/server.js"]
