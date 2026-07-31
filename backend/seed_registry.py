import csv
from pathlib import Path
from database import get_connection

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "iebc_registry.csv"


def safe_int(value):
    """
    Convert a value to int.
    Returns None if the value is blank or invalid.
    """
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.upper() == "#N/A":
        return None

    try:
        return int(float(value))
    except ValueError:
        return None


def seed_registry():
    conn = get_connection()
    cursor = conn.cursor()

    counties = set()
    constituencies = set()

    county_count = 0
    constituency_count = 0
    ward_count = 0
    skipped = 0

    with open(CSV_FILE, mode="r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        print("Importing IEBC Registry...\n")

        for line_no, row in enumerate(reader, start=2):

            county_id = safe_int(row.get("COUNTY ID"))
            constituency_id = safe_int(row.get("CONSTITUENCY ID"))
            ward_id = safe_int(row.get("WARD ID"))

            county_name = str(row.get("COUNTY NAME", "")).strip()
            constituency_name = str(row.get("CONSTITUENCY NAME", "")).strip()
            ward_name = str(row.get("WARD NAME", "")).strip()

            # Skip invalid rows
            if (
                county_id is None
                or constituency_id is None
                or ward_id is None
                or county_name == ""
                or constituency_name == ""
                or ward_name == ""
            ):
                skipped += 1
                print(f"Skipped row {line_no}: {row}")
                continue

            # Counties
            if county_id not in counties:
                cursor.execute("""
                    INSERT OR IGNORE INTO counties
                    (county_id, county_name)
                    VALUES (?, ?)
                """, (county_id, county_name))

                counties.add(county_id)
                county_count += 1

            # Constituencies
            if constituency_id not in constituencies:
                cursor.execute("""
                    INSERT OR IGNORE INTO constituencies
                    (constituency_id, county_id, constituency_name)
                    VALUES (?, ?, ?)
                """, (
                    constituency_id,
                    county_id,
                    constituency_name
                ))

                constituencies.add(constituency_id)
                constituency_count += 1

            # Wards
            cursor.execute("""
                INSERT OR IGNORE INTO wards
                (ward_id, constituency_id, ward_name)
                VALUES (?, ?, ?)
            """, (
                ward_id,
                constituency_id,
                ward_name
            ))

            ward_count += 1

    conn.commit()
    conn.close()

    print("\n========================================")
    print("IEBC Registry Import Complete")
    print("========================================")
    print(f"Counties       : {county_count}")
    print(f"Constituencies : {constituency_count}")
    print(f"Wards          : {ward_count}")
    print(f"Skipped Rows   : {skipped}")
    print("========================================")


if __name__ == "__main__":
    seed_registry()