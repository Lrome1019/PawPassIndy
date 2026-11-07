"""Hand-written demo data for PawPass Indy (no CSV needed).

Run from the repo root:   python -m Backend.seed_demo
Safe to run again: it only adds the demo rows if they are not there yet.

Adds 9 pets (8 lost, 1 safe "demo pet" for the NFC tag) and 15 sightings
around Indianapolis, Fishers and Muncie. Field names follow the README contract.
"""
from datetime import datetime, timedelta, timezone

from Backend.db import get_conn, init_db

NOW = datetime.now(timezone.utc)


def ago(hours):
    """ISO 8601 UTC timestamp for `hours` hours ago."""
    return (NOW - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


# Area centers from the README: Indianapolis, Fishers, Muncie
INDY = (39.7684, -86.1581)
FISHERS = (39.9568, -86.0134)
MUNCIE = (40.1934, -85.3864)

# (tag_code, name, previous_names, species, breed, color, size, markings,
#  chip, registry, shelter, adoption_date, adoption_id, owner, phone, email,
#  is_lost, (lat, lng), hours_since_seen, lost_notes)
PETS = [
    ("biscuit1", "Biscuit", "Cookie", "dog", "Terrier mix", "brown", "small", "white chest",
     "985112345678901", "HomeAgain", "Indy Humane", "2023-04-02", "A1234",
     "Sam Carter", "555-0101", "sam@example.com", 1, (39.9568, -86.0134), 48, "Slipped out the back gate"),
    ("whisker2", "Whiskers", "", "cat", "Tabby", "orange", "medium", "striped tail",
     "985198765432100", "PetLink", "Muncie Animal Shelter", "2022-05-10", "M77",
     "Dana Reed", "555-0102", "dana@example.com", 1, (40.1934, -85.3864), 168, "Missing since last week"),
    ("luna0003", "Luna", "Midnight", "cat", "Domestic Shorthair", "black", "small", "white paws",
     "985100000000003", "AKC Reunite", "Indy Humane", "2021-08-14", "A2201",
     "Priya Nair", "555-0103", "priya@example.com", 1, (39.7684, -86.1581), 30, "Indoor cat, got out the front door"),
    ("max00004", "Max", "", "dog", "Golden Retriever", "golden", "large", "",
     "985100000000004", "HomeAgain", "Humane Society of Indianapolis", "2020-03-21", "H889",
     "Tom Alvarez", "555-0104", "tom@example.com", 1, (39.78, -86.14), 12, "Wearing a red collar"),
    ("daisy005", "Daisy", "", "dog", "Maltese", "white", "small", "gray ear",
     "985100000000005", "PetLink", "Fishers Animal Rescue", "2022-11-30", "F310",
     "Jen Wu", "555-0105", "jen@example.com", 1, (39.95, -86.02), 72, "Ran off during a walk"),
    ("shadow06", "Shadow", "", "dog", "Labrador", "black", "large", "",
     "985100000000006", "HomeAgain", "Indy Humane", "2019-06-01", "A1002",
     "Lee Brooks", "555-0106", "lee@example.com", 1, (39.76, -86.17), 96, "Very friendly, answers to Shadow"),
    ("pepper07", "Pepper", "Smokey", "cat", "Russian Blue", "gray", "medium", "green eyes",
     "985100000000007", "PetLink", "Muncie Animal Shelter", "2021-02-12", "M310",
     "Carla Diaz", "555-0107", "carla@example.com", 1, (40.2, -85.4), 120, "Shy, may hide under porches"),
    ("charlie8", "Charlie", "", "dog", "Beagle mix", "tan", "medium", "white tip tail",
     "985100000000008", "HomeAgain", "Muncie Animal Shelter", "2020-09-09", "M455",
     "Ben Ortiz", "555-0108", "ben@example.com", 1, (40.19, -85.39), 24, "Slipped his harness"),
    # The demo pet: NOT lost. Write this tag to the NFC sticker for the live demo.
    ("goku0001", "Goku", "Mr Meows Alot", "cat", "American Shorthair", "white and grey", "large", "pink and black nose",
     "985100000000009", "HomeAgain", "Northbay Humane", "2020-07-10", "N222",
     "Laura Romero", "555-0109", "laura@example.com", 0, (None, None), None, ""),
]

# (description, species, color, size, markings, lat, lng, hours_ago, reporter)
SIGHTINGS = [
    ("small brown dog with white chest near Fishers library", "dog", "brown", "small", "white chest", 39.9601, -86.0102, 3, "Pat"),
    ("brown terrier trotting down Allisonville Rd", "dog", "tan", "small", "", 39.9450, -86.0300, 20, "Mia"),
    ("orange tabby cat in an alley behind a bakery", "cat", "orange", "medium", "striped tail", 40.1900, -85.3900, 10, "Jo"),
    ("ginger cat hiding under a porch", "cat", "orange", "medium", "", 40.2050, -85.3700, 60, "Chris"),
    ("big black dog near downtown, friendly", "dog", "black", "large", "", 39.7700, -86.1600, 2, "Al"),
    ("black lab by the canal, no collar", "dog", "black", "large", "", 39.7550, -86.1700, 40, "Rosa"),
    ("small black cat with white paws on Mass Ave", "cat", "black", "small", "white paws", 39.7750, -86.1450, 5, "Dev"),
    ("golden retriever wearing a red collar", "dog", "golden", "large", "red collar", 39.7850, -86.1350, 4, "Tess"),
    ("little white dog by the Fishers splash pad", "dog", "white", "small", "", 39.9500, -86.0200, 8, "Kim"),
    ("gray cat with green eyes near the university", "cat", "gray", "medium", "green eyes", 40.2000, -85.4100, 30, "Sam"),
    ("tan beagle sniffing around a park", "dog", "tan", "medium", "white tip tail", 40.1850, -85.3950, 6, "Omar"),
    ("white and gray cat on a porch in Broad Ripple", "cat", "white", "large", "pink nose", 39.8700, -86.1400, 15, "Nia"),
    ("brown dog by a school in Noblesville", "dog", "brown", "medium", "", 40.0450, -86.0100, 90, "Lou"),
    ("black cat crossing the street at night", "cat", "black", "small", "", 39.7800, -86.1500, 26, "Ivy"),
    ("small white dog with a gray ear in a yard", "dog", "white", "small", "gray ear", 39.9550, -86.0250, 50, "Ed"),
]


def seed_demo():
    init_db()
    conn = get_conn()
    try:
        already = conn.execute(
            "SELECT COUNT(*) FROM pets WHERE source_system = 'demo_seed'"
        ).fetchone()[0]
        if already:
            print("Demo data already loaded. Nothing to do.")
            return

        for (tag, name, prev, species, breed, color, size, markings, chip, registry,
             shelter, a_date, a_id, owner, phone, email, is_lost, (lat, lng),
             hrs, notes) in PETS:
            conn.execute(
                """INSERT INTO pets
                   (tag_code, name, previous_names, species, breed, color, size, markings,
                    microchip_number, chip_registry, adoption_shelter, adoption_date, adoption_id,
                    owner_name, owner_phone, owner_email, is_lost,
                    last_seen_lat, last_seen_lng, last_seen_at, lost_notes,
                    created_at, source_system, source_pet_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (tag, name, prev, species, breed, color, size, markings, chip, registry,
                 shelter, a_date, a_id, owner, phone, email, is_lost,
                 lat, lng, ago(hrs) if hrs is not None else None, notes,
                 ago(24 * 90), "demo_seed", tag),
            )

        for (desc, species, color, size, markings, lat, lng, hrs, reporter) in SIGHTINGS:
            conn.execute(
                """INSERT INTO sightings
                   (pet_id, description, species, color, size, breed, markings,
                    lat, lng, photo_url, reporter_name, created_at)
                   VALUES (NULL,?,?,?,?,'',?,?,?, '',?,?)""",
                (desc, species, color, size, markings, lat, lng, reporter, ago(hrs)),
            )

        conn.commit()
        print(f"Added {len(PETS)} pets and {len(SIGHTINGS)} sightings.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_demo()
