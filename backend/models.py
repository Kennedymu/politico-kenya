from database import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Counties table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS counties (
        county_id INTEGER PRIMARY KEY,
        county_name TEXT NOT NULL UNIQUE
    )
    """)

    # Constituencies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS constituencies (
        constituency_id INTEGER PRIMARY KEY,
        county_id INTEGER NOT NULL,
        constituency_name TEXT NOT NULL,
        FOREIGN KEY (county_id) REFERENCES counties(county_id)
    )
    """)

    # Wards table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wards (
        ward_id INTEGER PRIMARY KEY,
        constituency_id INTEGER NOT NULL,
        ward_name TEXT NOT NULL,
        FOREIGN KEY (constituency_id) REFERENCES constituencies(constituency_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()