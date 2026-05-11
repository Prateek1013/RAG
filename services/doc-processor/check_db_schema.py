import psycopg2
try:
    conn = psycopg2.connect("postgresql://user:password@localhost:5432/rag")
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='file';")
    print([row[0] for row in cur.fetchall()])
except Exception as e:
    print("Error:", e)
