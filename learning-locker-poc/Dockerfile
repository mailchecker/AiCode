# Learning Locker v2 Dockerfile
# GitHub 저장소에서 직접 빌드

# Learning Locker v2는 Node.js 8을 요구합니다
# Node.js 10-alpine을 사용하고 --ignore-engines로 호환성 우회
FROM node:10-alpine

LABEL maintainer="Learning Locker POC"
LABEL description="Learning Locker LRS - xAPI Learning Record Store"

# 작업 디렉토리 설정
WORKDIR /opt/learninglocker

# 필수 패키지 설치
RUN apk add --no-cache \
    git \
    python2 \
    make \
    g++ \
    bash \
    curl \
    wget

# Learning Locker v2 소스코드 클론 (특정 버전)
# v2.8.0이 마지막 안정 버전
RUN git clone --depth 1 --branch v2.8.0 https://github.com/LearningLocker/learninglocker.git . || \
    git clone --depth 1 https://github.com/LearningLocker/learninglocker.git .

# Yarn 버전 확인 및 설정
RUN yarn --version

# xAPI 서비스 설치
WORKDIR /opt/learninglocker/xapi-service
RUN yarn install --production --frozen-lockfile --ignore-engines && \
    yarn build

# 메인 애플리케이션으로 돌아가기
WORKDIR /opt/learninglocker

# 의존성 설치 (--ignore-engines 추가)
RUN yarn install --production --frozen-lockfile --ignore-engines

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

# 스토리지 디렉토리 생성
RUN mkdir -p /opt/learninglocker/storage

# 포트 설정
EXPOSE 3000 8080

# 헬스체크 (curl 대신 wget 사용)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --spider -q http://localhost:8080/health || exit 1

# 기본 명령어 (docker-compose에서 override)
CMD ["node", "api/dist/server.js"]
