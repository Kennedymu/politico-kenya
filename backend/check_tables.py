import sqlite3

conn = sqlite3.connect("backend/database.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tables = cursor.fetchall()

print("===== TABLES IN DATABASE =====")
for table in tables:
    print(table[0])

conn.close()