
import csv
import secrets
from datetime import datetime, timezone
from pathlib import Path

from Backend.db import get_conn, init_db


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "pet_ownership_database.csv"


def to_bool(value):
    if value is None or value == "":
        return None
    return 1 if value.strip().lower() == "true" else 0


def to_float(value):
    if value is None or value.strip() == "":
        return None
    return float(value)


def create_tag_code():
    return secrets.token_hex(4)


def seed_pets():
    init_db()

    if not CSV_PATH.exists():
        print(f"CSV file not found: {CSV_PATH}")
        return

    conn = get_conn()
    added = 0
    skipped = 0

    try:
        with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                pet_id = row["pet_id"].strip()

                if not pet_id:
                    skipped += 1
                    continue

                existing = conn.execute(
                    """
                    SELECT id FROM pets
                    WHERE source_system = ?
                    AND source_pet_id = ?
                    """,
                    ("csv_demo", pet_id)
                ).fetchone()

                if existing:
                    skipped += 1
                    continue

                conn.execute(
                    """
                    INSERT INTO pets (
                        tag_code,
                        name,
                        species,
                        breed,
                        size,
                        adoption_date,
                        source_system,
                        source_pet_id,
                        age_years,
                        gender,
                        weight_kg,
                        microchipped,
                        behavior_issues,
                        funny_habit,
                        owner_location_type,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        create_tag_code(),
                        row["pet_name"],
                        row["species"],
                        row["breed"],
                        row["size_class"].lower(),
                        row["adoption_date"],
                        "csv_demo",
                        pet_id,
                        to_float(row["age_years"]),
                        row["gender"],
                        to_float(row["weight_kg"]),
                        to_bool(row["microchipped"]),
                        to_bool(row["behavior_issues"]),
                        row["funny_habit"],
                        row["owner_location_type"],
                        datetime.now(timezone.utc).isoformat()
                    )
                )

                added += 1

        conn.commit()

        total = conn.execute(
            "SELECT COUNT(*) FROM pets"
        ).fetchone()[0]

        print("PawPass database seeded successfully!")
        print(f"New pets added: {added}")
        print(f"Existing records skipped: {skipped}")
        print(f"Total pets in database: {total}")

    finally:
        conn.close()


if __name__ == "__main__":
    seed_pets()
