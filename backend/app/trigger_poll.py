"""Manually trigger Upstage polling for a document."""
from app.tasks.parse_tasks import parse_upstage_poll

doc_id = "0771fdf6-f664-4298-a81e-3ca3a93a4044"
version_id = "v1"  # 기본값, 실제 값이 다르면 수정 필요
request_id = "4e693179-baa6-4374-b093-45549cd5622c"

print(f"Triggering polling for doc_id={doc_id}, version_id={version_id}, request_id={request_id}")

# Celery 태스크 호출
result = parse_upstage_poll.delay(doc_id, version_id, request_id, attempt=0)

print(f"Task submitted: {result.id}")
print("Check logs with: docker-compose logs -f celery-parse")
