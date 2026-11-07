
from datetime import datetime, timezone
from math import radians, sin, cos, asin, sqrt


COLOR_GROUPS = [
    {"brown", "tan", "chocolate"},
    {"orange", "ginger"},
    {"black", "dark"},
    {"gray", "grey", "silver"}
]

SIZES = ["small", "medium", "large"]


def haversine(lat1, lon1, lat2, lon2):
    radius = 3958.8

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 2 * radius * asin(sqrt(min(1, a)))


def color_score(first, second):
    if not first or not second:
        return 0

    first = first.lower().strip()
    second = second.lower().strip()

    if first == second:
        return 1

    for group in COLOR_GROUPS:
        if first in group and second in group:
            return 0.6

    return 0


def size_score(first, second):
    if not first or not second:
        return 0

    first = first.lower().strip()
    second = second.lower().strip()

    if first == second:
        return 1

    if first in SIZES and second in SIZES:
        difference = abs(
            SIZES.index(first) - SIZES.index(second)
        )

        if difference == 1:
            return 0.5

    return 0


def distance_score(distance):
    if distance <= 0.5:
        return 1

    if distance >= 10:
        return 0

    return (10 - distance) / 9.5


def recency_score(last_seen_at, sighting_at):
    if not last_seen_at or not sighting_at:
        return 0

    try:
        last_seen = datetime.fromisoformat(
            last_seen_at.replace("Z", "+00:00")
        )

        sighting = datetime.fromisoformat(
            sighting_at.replace("Z", "+00:00")
        )

        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(
                tzinfo=timezone.utc
            )

        if sighting.tzinfo is None:
            sighting = sighting.replace(
                tzinfo=timezone.utc
            )

        days = (
            sighting - last_seen
        ).total_seconds() / 86400

        if days < 0:
            return 0

        if days <= 1:
            return 1

        if days >= 30:
            return 0

        return (30 - days) / 29

    except (ValueError, TypeError):
        return 0


def match_pet(pet, sighting):
    pet = dict(pet)
    sighting = dict(sighting)

    pet_species = (pet.get("species") or "").lower().strip()
    sighting_species = (
        sighting.get("species") or ""
    ).lower().strip()

    if not pet_species or pet_species != sighting_species:
        return None

    reasons = ["Same species"]

    color = color_score(
        pet.get("color"),
        sighting.get("color")
    )

    if color > 0:
        reasons.append("Color match")

    size = size_score(
        pet.get("size"),
        sighting.get("size")
    )

    if size > 0:
        reasons.append("Size match")

    distance = 10
    if all(
        value is not None
        for value in [
            pet.get("last_seen_lat"),
            pet.get("last_seen_lng"),
            sighting.get("lat"),
            sighting.get("lng")
        ]
    ):
        distance = haversine(
            pet["last_seen_lat"],
            pet["last_seen_lng"],
            sighting["lat"],
            sighting["lng"]
        )

        if distance < 10:
            reasons.append(
                f"{distance:.1f} miles from last seen"
            )

    recency = recency_score(
        pet.get("last_seen_at"),
        sighting.get("created_at")
    )

    if recency > 0:
        reasons.append("Recent sighting")

    score = (
        0.35
        + 0.25 * color
        + 0.15 * size
        + 0.15 * distance_score(distance)
        + 0.10 * recency
    )

    return {
        "pet": {
            "id": pet["id"],
            "name": pet["name"],
            "species": pet["species"],
            "breed": pet.get("breed"),
            "color": pet.get("color"),
            "size": pet.get("size"),
            "photo_url": pet.get("photo_url")
        },
        "score": round(score, 3),
        "reasons": reasons
    }


def find_matches(sighting, pets, limit=3):
    matches = []

    for pet in pets:
        if not pet["is_lost"]:
            continue

        result = match_pet(pet, sighting)

        if result is not None:
            matches.append(result)

    matches.sort(
        key=lambda match: match["score"],
        reverse=True
    )

    return matches[:limit]
