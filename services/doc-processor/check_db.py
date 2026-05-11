import psycopg2
try:
    conn = psycopg2.connect("postgresql://user:password@localhost:5432/rag")
    cur = conn.cursor()
    cur.execute("SELECT id, file_id, user_id FROM document_chunks;")
    print(cur.fetchall())
except Exception as e:
    print("Error:", e)
