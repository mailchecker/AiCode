import sqlite3

conn = sqlite3.connect('/app/data/app.db')
cursor = conn.cursor()

# 현재 상태 확인
cursor.execute('SELECT id, status, parse_request_id, error_message FROM documents WHERE id = ?',
               ('0771fdf6-f664-4298-a81e-3ca3a93a4044',))
print('Before:', cursor.fetchone())

# 상태를 pending으로 변경
cursor.execute('''
UPDATE documents
SET status = ?,
    parse_request_id = ?,
    error_message = NULL
WHERE id = ?
''', ('pending', '4e693179-baa6-4374-b093-45549cd5622c', '0771fdf6-f664-4298-a81e-3ca3a93a4044'))
conn.commit()

# 변경 후 확인
cursor.execute('SELECT id, status, parse_request_id FROM documents WHERE id = ?',
               ('0771fdf6-f664-4298-a81e-3ca3a93a4044',))
print('After:', cursor.fetchone())

conn.close()
print('Updated successfully!')
