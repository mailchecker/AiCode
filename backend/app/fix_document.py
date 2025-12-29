import sqlite3

conn = sqlite3.connect('/app/data/app.db')
cursor = conn.cursor()

# 현재 상태 확인
cursor.execute('SELECT doc_id, version_id, status, parse_request_id, last_error FROM document_versions WHERE doc_id = ?',
               ('0771fdf6-f664-4298-a81e-3ca3a93a4044',))
print('Before:', cursor.fetchone())

# 상태를 parsing으로 변경 (pending이 아니라 parsing - Celery가 polling을 시작하도록)
cursor.execute('''
UPDATE document_versions
SET status = ?,
    parse_request_id = ?,
    last_error = NULL
WHERE doc_id = ?
''', ('parsing', '4e693179-baa6-4374-b093-45549cd5622c', '0771fdf6-f664-4298-a81e-3ca3a93a4044'))
conn.commit()

# 변경 후 확인
cursor.execute('SELECT doc_id, version_id, status, parse_request_id FROM document_versions WHERE doc_id = ?',
               ('0771fdf6-f664-4298-a81e-3ca3a93a4044',))
print('After:', cursor.fetchone())

conn.close()
print('Updated successfully!')
