import sqlite3

conn = sqlite3.connect("database/exam.db")
cur = conn.cursor()

# Add password column if it doesn't exist
try:
    cur.execute("ALTER TABLE students ADD COLUMN password TEXT")
    print("✅ Password column added successfully")
except sqlite3.OperationalError as e:
    print("⚠️", e)

conn.commit()
conn.close()
