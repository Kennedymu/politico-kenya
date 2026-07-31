from database import get_connection

conn = get_connection()
cursor = conn.cursor()

tables = ["counties", "constituencies", "wards"]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count}")

conn.close()