
import sqlite3
from pathlib import Path


import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "pawpass.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()

    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_code TEXT UNIQUE,

                name TEXT,
                previous_names TEXT,
                species TEXT,
                breed TEXT,
                color TEXT,
                size TEXT,
                markings TEXT,
                photo_url TEXT,

                microchip_number TEXT,
                chip_registry TEXT,

                adoption_shelter TEXT,
                adoption_date TEXT,
                adoption_id TEXT,

                owner_name TEXT,
                owner_phone TEXT,
                owner_email TEXT,

                is_lost INTEGER DEFAULT 0,
                last_seen_lat REAL,
                last_seen_lng REAL,
                last_seen_at TEXT,
                lost_notes TEXT,

                created_at TEXT,

                source_system TEXT,
                source_pet_id TEXT,
                age_years REAL,
                gender TEXT,
                weight_kg REAL,
                microchipped INTEGER DEFAULT 0,
                behavior_issues INTEGER,
                funny_habit TEXT,
                owner_location_type TEXT
            );

            CREATE TABLE IF NOT EXISTS sightings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER,
                description TEXT,

                species TEXT,
                color TEXT,
                size TEXT,
                breed TEXT,
                markings TEXT,

                lat REAL,
                lng REAL,
                photo_url TEXT,
                reporter_name TEXT,
                created_at TEXT,

                FOREIGN KEY (pet_id) REFERENCES pets(id)
            );
        """)

        additional_columns = {
            "source_system": "TEXT",
            "source_pet_id": "TEXT",
            "age_years": "REAL",
            "gender": "TEXT",
            "weight_kg": "REAL",
            "microchipped": "INTEGER DEFAULT 0",
            "behavior_issues": "INTEGER",
            "funny_habit": "TEXT",
            "owner_location_type": "TEXT"
        }

        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(pets)")
        }

        for column, data_type in additional_columns.items():
            if column not in existing_columns:
                conn.execute(
                    f"ALTER TABLE pets ADD COLUMN {column} {data_type}"
                )

        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_pets_source
            ON pets(source_system, source_pet_id)
        """)

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("PawPass database initialized successfully!")
