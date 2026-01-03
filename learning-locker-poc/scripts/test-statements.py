#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Learning Locker xAPI Statement 테스트 스크립트

이 스크립트는 Learning Locker LRS에 xAPI Statement를 전송하여
학습 활동 데이터를 기록합니다.

사용법:
    python test-statements.py --key YOUR_KEY --secret YOUR_SECRET

또는 환경 변수 사용:
    export LRS_KEY="your_key"
    export LRS_SECRET="your_secret"
    python test-statements.py
"""

import requests
import json
import uuid
import argparse
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random


class LearningLockerClient:
    """Learning Locker LRS 클라이언트"""

    def __init__(self, endpoint: str, key: str, secret: str):
        """
        Args:
            endpoint: Learning Locker API 엔드포인트 (예: http://localhost/data/xAPI)
            key: Basic Auth Key
            secret: Basic Auth Secret
        """
        self.endpoint = endpoint.rstrip('/')
        self.auth = (key, secret)
        self.headers = {
            'X-Experience-API-Version': '1.0.3',
            'Content-Type': 'application/json'
        }

    def send_statement(self, statement: Dict[str, Any]) -> bool:
        """
        단일 Statement를 LRS에 전송

        Args:
            statement: xAPI Statement 객체

        Returns:
            성공 여부
        """
        try:
            response = requests.post(
                f"{self.endpoint}/statements",
                auth=self.auth,
                headers=self.headers,
                json=statement,
                timeout=10
            )

            if response.status_code in [200, 204]:
                print(f"✅ Statement 전송 성공: {statement['id']}")
                return True
            else:
                print(f"❌ Statement 전송 실패: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 오류: {e}")
            return False

    def send_statements(self, statements: List[Dict[str, Any]]) -> int:
        """
        여러 Statement를 배치로 전송

        Args:
            statements: xAPI Statement 객체 리스트

        Returns:
            성공한 Statement 개수
        """
        success_count = 0

        for statement in statements:
            if self.send_statement(statement):
                success_count += 1

        return success_count

    def get_statements(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        LRS에서 Statement 조회

        Args:
            params: 쿼리 파라미터 (agent, verb, limit 등)

        Returns:
            Statement 결과 객체
        """
        try:
            response = requests.get(
                f"{self.endpoint}/statements",
                auth=self.auth,
                headers=self.headers,
                params=params or {},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Statement 조회 실패: {response.status_code}")
                return {}

        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 오류: {e}")
            return {}


def generate_sample_statements(num_statements: int = 100) -> List[Dict[str, Any]]:
    """
    샘플 xAPI Statement 생성

    다양한 학습 활동을 시뮬레이션합니다:
    - 강의 영상 시청 (viewed, played, completed)
    - 퀴즈/시험 응시 (attempted, passed, failed)
    - 과정 등록/완료 (registered, completed)
    - 문서 다운로드 (downloaded)
    - 포럼 활동 (posted, commented)

    Args:
        num_statements: 생성할 Statement 개수

    Returns:
        xAPI Statement 리스트
    """
    statements = []

    # 샘플 학습자 목록
    learners = [
        {"name": "김철수", "email": "kim.cs@example.com"},
        {"name": "이영희", "email": "lee.yh@example.com"},
        {"name": "박민수", "email": "park.ms@example.com"},
        {"name": "정수진", "email": "jung.sj@example.com"},
        {"name": "최지훈", "email": "choi.jh@example.com"},
    ]

    # 샘플 과정 목록
    courses = [
        {"id": "course-001", "name": "Python 프로그래밍 기초"},
        {"id": "course-002", "name": "데이터 분석 입문"},
        {"id": "course-003", "name": "머신러닝 실전"},
        {"id": "course-004", "name": "웹 개발 종합"},
    ]

    # 활동 유형별 동사 (Verb)
    verbs = {
        "video": [
            {"id": "http://adlnet.gov/expapi/verbs/played", "display": "재생"},
            {"id": "http://adlnet.gov/expapi/verbs/paused", "display": "일시정지"},
            {"id": "http://adlnet.gov/expapi/verbs/completed", "display": "완료"},
        ],
        "assessment": [
            {"id": "http://adlnet.gov/expapi/verbs/attempted", "display": "시도"},
            {"id": "http://adlnet.gov/expapi/verbs/passed", "display": "통과"},
            {"id": "http://adlnet.gov/expapi/verbs/failed", "display": "실패"},
        ],
        "course": [
            {"id": "http://adlnet.gov/expapi/verbs/registered", "display": "등록"},
            {"id": "http://adlnet.gov/expapi/verbs/completed", "display": "완료"},
        ],
        "interaction": [
            {"id": "http://adlnet.gov/expapi/verbs/answered", "display": "답변"},
            {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": "상호작용"},
        ],
    }

    # 현재 시간 기준으로 최근 30일간의 활동 생성
    base_time = datetime.now()

    for i in range(num_statements):
        learner = random.choice(learners)
        course = random.choice(courses)
        activity_type = random.choice(["video", "assessment", "course", "interaction"])
        verb = random.choice(verbs[activity_type])

        # 타임스탬프 (최근 30일 내 랜덤)
        timestamp = base_time - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # 기본 Statement 구조
        statement = {
            "id": str(uuid.uuid4()),
            "timestamp": timestamp.isoformat() + "Z",
            "actor": {
                "objectType": "Agent",
                "name": learner["name"],
                "mbox": f"mailto:{learner['email']}"
            },
            "verb": {
                "id": verb["id"],
                "display": {"ko-KR": verb["display"], "en-US": verb["display"]}
            },
        }

        # 활동 유형별 Object 및 Result 추가
        if activity_type == "video":
            lesson_num = random.randint(1, 10)
            statement["object"] = {
                "objectType": "Activity",
                "id": f"http://example.com/courses/{course['id']}/videos/lesson-{lesson_num}",
                "definition": {
                    "name": {"ko-KR": f"{course['name']} - 강의 {lesson_num}"},
                    "description": {"ko-KR": f"{course['name']}의 {lesson_num}번째 강의 영상"},
                    "type": "http://adlnet.gov/expapi/activities/video"
                }
            }

            if verb["display"] == "완료":
                statement["result"] = {
                    "completion": True,
                    "duration": f"PT{random.randint(5, 60)}M"  # ISO 8601 duration
                }

        elif activity_type == "assessment":
            quiz_num = random.randint(1, 5)
            score = random.randint(0, 100)
            passed = score >= 70

            statement["object"] = {
                "objectType": "Activity",
                "id": f"http://example.com/courses/{course['id']}/assessments/quiz-{quiz_num}",
                "definition": {
                    "name": {"ko-KR": f"{course['name']} - 퀴즈 {quiz_num}"},
                    "description": {"ko-KR": f"{course['name']}의 {quiz_num}번 퀴즈"},
                    "type": "http://adlnet.gov/expapi/activities/assessment"
                }
            }

            statement["result"] = {
                "score": {
                    "scaled": score / 100,
                    "raw": score,
                    "min": 0,
                    "max": 100
                },
                "success": passed,
                "completion": True
            }

        elif activity_type == "course":
            statement["object"] = {
                "objectType": "Activity",
                "id": f"http://example.com/courses/{course['id']}",
                "definition": {
                    "name": {"ko-KR": course['name']},
                    "description": {"ko-KR": f"{course['name']} 전체 과정"},
                    "type": "http://adlnet.gov/expapi/activities/course"
                }
            }

            if verb["display"] == "완료":
                statement["result"] = {
                    "completion": True,
                    "success": True
                }

        else:  # interaction
            statement["object"] = {
                "objectType": "Activity",
                "id": f"http://example.com/courses/{course['id']}/discussions/topic-{random.randint(1, 20)}",
                "definition": {
                    "name": {"ko-KR": f"{course['name']} - 토론"},
                    "description": {"ko-KR": "과정 토론 게시판 활동"},
                    "type": "http://adlnet.gov/expapi/activities/interaction"
                }
            }

        # Context 추가 (선택사항이지만 추가 정보 제공)
        statement["context"] = {
            "platform": "Learning Locker POC",
            "language": "ko-KR",
            "contextActivities": {
                "parent": [{
                    "objectType": "Activity",
                    "id": f"http://example.com/courses/{course['id']}",
                    "definition": {
                        "name": {"ko-KR": course['name']},
                        "type": "http://adlnet.gov/expapi/activities/course"
                    }
                }]
            }
        }

        statements.append(statement)

    # 시간순 정렬
    statements.sort(key=lambda x: x['timestamp'])

    return statements


def main():
    """메인 실행 함수"""

    parser = argparse.ArgumentParser(
        description='Learning Locker LRS에 xAPI Statement 테스트 데이터 전송'
    )
    parser.add_argument(
        '--endpoint',
        default=os.getenv('LRS_ENDPOINT', 'http://localhost/data/xAPI'),
        help='LRS API 엔드포인트 (기본값: http://localhost/data/xAPI)'
    )
    parser.add_argument(
        '--key',
        default=os.getenv('LRS_KEY'),
        required=not os.getenv('LRS_KEY'),
        help='Basic Auth Key (또는 환경변수 LRS_KEY)'
    )
    parser.add_argument(
        '--secret',
        default=os.getenv('LRS_SECRET'),
        required=not os.getenv('LRS_SECRET'),
        help='Basic Auth Secret (또는 환경변수 LRS_SECRET)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=100,
        help='생성할 Statement 개수 (기본값: 100)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='전송 후 Statement 조회 테스트 실행'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Learning Locker xAPI Statement 테스트")
    print("=" * 60)
    print(f"엔드포인트: {args.endpoint}")
    print(f"Key: {args.key[:10]}..." if args.key else "Key: (없음)")
    print(f"생성할 Statement 수: {args.count}")
    print("=" * 60)
    print()

    # LRS 클라이언트 생성
    client = LearningLockerClient(args.endpoint, args.key, args.secret)

    # 샘플 Statement 생성
    print(f"📝 {args.count}개의 샘플 Statement 생성 중...")
    statements = generate_sample_statements(args.count)
    print(f"✅ {len(statements)}개의 Statement 생성 완료\n")

    # Statement 전송
    print(f"📤 Statement 전송 중...")
    success_count = client.send_statements(statements)
    print()
    print(f"{'=' * 60}")
    print(f"전송 완료: {success_count}/{len(statements)} 성공")
    print(f"{'=' * 60}")
    print()

    # 검증 테스트
    if args.verify and success_count > 0:
        print("🔍 Statement 조회 테스트 중...")
        result = client.get_statements({"limit": 10})

        if result and "statements" in result:
            print(f"✅ 조회 성공: {len(result['statements'])}개의 Statement 조회됨")
            print(f"   전체 Statement 수: {result.get('more', 'N/A')}")
        else:
            print("❌ 조회 실패")
        print()

    # 다음 단계 안내
    print("📌 다음 단계:")
    print("   1. Learning Locker UI (http://localhost)에 접속")
    print("   2. 대시보드에서 Statement 확인")
    print("   3. Visualisations 메뉴에서 학습 통계 확인")
    print()


if __name__ == "__main__":
    main()
