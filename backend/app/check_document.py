"""Check document status in database."""
import sqlite3

conn = sqlite3.connect('/app/data/app.db')
cursor = conn.cursor()

# 현재 상태 확인
cursor.execute('SELECT doc_id, version_id, status, parse_request_id, parse_provider, last_error FROM document_versions WHERE doc_id = ?',
               ('0771fdf6-f664-4298-a81e-3ca3a93a4044',))

result = cursor.fetchone()
if result:
    print("Document found:")
    print(f"  doc_id: {result[0]}")
    print(f"  version_id: {result[1]}")
    print(f"  status: {result[2]}")
    print(f"  parse_request_id: {result[3]}")
    print(f"  parse_provider: {result[4]}")
    print(f"  last_error: {result[5]}")
else:
    print("Document not found!")

conn.close()
