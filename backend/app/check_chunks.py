"""Check actual chunks in Elasticsearch to verify chunking."""
import sys
import os
sys.path.insert(0, '/app')

from elasticsearch import Elasticsearch
from app.config import settings

# Connect to Elasticsearch
es = Elasticsearch([settings.elasticsearch_url])

# Get latest document's chunks
try:
    # Search for chunks (limit to 5 for preview)
    response = es.search(
        index=settings.elasticsearch_index,
        body={
            "size": 5,
            "sort": [{"_id": "desc"}],
            "_source": ["chunk_id", "doc_id", "text", "page_start"]
        }
    )

    print(f"Found {response['hits']['total']['value']} total chunks\n")
    print("="*80)

    for i, hit in enumerate(response['hits']['hits'], 1):
        source = hit['_source']
        text = source.get('text', '')

        print(f"\n청크 #{i}")
        print(f"chunk_id: {source.get('chunk_id')}")
        print(f"doc_id: {source.get('doc_id')}")
        print(f"page: {source.get('page_start')}")
        print(f"글자 수: {len(text)}")
        print(f"미리보기 (처음 200자):")
        print(f"{text[:200]}...")
        print("-"*80)

except Exception as e:
    print(f"Error: {e}")
    print("\nElasticsearch에 데이터가 없거나 연결 실패")
