import sqlite3

conn = sqlite3.connect("backend/database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    county_id INTEGER NOT NULL,
    constituency_id INTEGER NOT NULL,
    ward_id INTEGER NOT NULL,
    polling_station TEXT NOT NULL,
    has_voted INTEGER NOT NULL DEFAULT 0,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (county_id) REFERENCES counties(county_id),
    FOREIGN KEY (constituency_id) REFERENCES constituencies(constituency_id),
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
);
""")

conn.commit()
conn.close()

print("✅ Voters table created successfully.")