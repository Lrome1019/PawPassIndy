from Backend.matching import find_matches, match_pet
from Backend.matching import find_matches
from datetime import timedelta
import io
import os
import qrcode
from fastapi.responses import StreamingResponse
import secrets
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from Backend.db import get_conn, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="PawPass Indy API",
    description="Pet registration and lost pet recovery system",
    version="1.0.0",
    lifespan=lifespan
)


class PetCreate(BaseModel):
    name: str = Field(min_length=1)
    previous_names: str | None = None
    species: str = Field(min_length=1)
    breed: str | None = None
    color: str | None = None
    size: str | None = None
    markings: str | None = None
    photo_url: str | None = None
    microchip_number: str | None = None
    chip_registry: str | None = None
    adoption_shelter: str | None = None
    adoption_date: str | None = None
    adoption_id: str | None = None
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_email: str | None = None


class PetLostUpdate(BaseModel):
    is_lost: bool
    last_seen_lat: float | None = Field(default=None, ge=-90, le=90)
    last_seen_lng: float | None = Field(default=None, ge=-180, le=180)
    lost_notes: str | None = None



class SightingCreate(BaseModel):
    description: str = Field(min_length=1)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    reporter_name: str | None = None
    pet_id: int | None = None
    photo_url: str | None = None
    species: str | None = None
    color: str | None = None
    size: str | None = None





@app.get("/")
def home():
    return {
        "message": "Welcome to PawPass Indy!",
        "status": "running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "database": "SQLite"
    }


@app.post("/api/pets", status_code=201)
def create_pet(pet: PetCreate):
    created_at = datetime.now(timezone.utc).isoformat()
    data = pet.model_dump()

    conn = get_conn()

    try:
        for attempt in range(5):
            tag_code = secrets.token_hex(4)

            pet_data = {
                **data,
                "tag_code": tag_code,
                "created_at": created_at
            }

            columns = ", ".join(pet_data.keys())
            placeholders = ", ".join(
                "?" for _ in pet_data
            )

            try:
                cursor = conn.execute(
                    f"""
                    INSERT INTO pets ({columns})
                    VALUES ({placeholders})
                    """,
                    tuple(pet_data.values())
                )

                conn.commit()

                result = conn.execute(
                    "SELECT * FROM pets WHERE id = ?",
                    (cursor.lastrowid,)
                ).fetchone()

                return dict(result)

            except sqlite3.IntegrityError as error:
                conn.rollback()

                if "tag_code" in str(error):
                    continue

                raise HTTPException(
                    status_code=409,
                    detail="Pet registration conflict"
                )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate unique pet tag"
        )

    finally:
        conn.close()


@app.get("/api/pets/{pet_id}")
def get_pet(pet_id: int):
    conn = get_conn()

    try:
        pet = conn.execute(
            "SELECT * FROM pets WHERE id = ?",
            (pet_id,)
        ).fetchone()

        if pet is None:
            raise HTTPException(
                status_code=404,
                detail="Pet not found"
            )

        return dict(pet)

    finally:
        conn.close()


@app.get("/api/pets/{pet_id}/qr.png")
def generate_pet_qr(pet_id: int):
    conn = get_conn()

    try:
        pet = conn.execute(
            "SELECT tag_code FROM pets WHERE id = ?",
            (pet_id,)
        ).fetchone()

        if pet is None:
            raise HTTPException(
                status_code=404,
                detail="Pet not found"
            )

        base_url = os.getenv(
            "BASE_URL",
            "http://127.0.0.1:8000"
        ).rstrip("/")

        pet_url = f"{base_url}/t/{pet['tag_code']}"

        qr = qrcode.make(pet_url)

        image_buffer = io.BytesIO()
        qr.save(image_buffer, format="PNG")
        image_buffer.seek(0)

        return StreamingResponse(
            image_buffer,
            media_type="image/png"
        )

    finally:
        conn.close()


@app.get("/api/tag/{tag_code}")
def get_public_pet(tag_code: str):
    conn = get_conn()

    try:
        pet = conn.execute(
            """
            SELECT
                id,
                tag_code,
                name,
                previous_names,
                species,
                breed,
                color,
                size,
                markings,
                photo_url,
                is_lost
            FROM pets
            WHERE tag_code = ?
            """,
            (tag_code,)
        ).fetchone()

        if pet is None:
            raise HTTPException(
                status_code=404,
                detail="Pet not found"
            )

        return dict(pet)

    finally:
        conn.close()



@app.patch("/api/pets/{pet_id}/lost")
def update_pet_lost(pet_id: int, update: PetLostUpdate):
    conn = get_conn()

    try:
        pet = conn.execute(
            "SELECT * FROM pets WHERE id = ?",
            (pet_id,)
        ).fetchone()

        if pet is None:
            raise HTTPException(
                status_code=404,
                detail="Pet not found"
            )

        last_seen_at = (
            datetime.now(timezone.utc).isoformat()
            if update.is_lost else None
        )

        conn.execute(
            """
            UPDATE pets
            SET is_lost = ?,
                last_seen_lat = ?,
                last_seen_lng = ?,
                last_seen_at = ?,
                lost_notes = ?
            WHERE id = ?
            """,
            (
                int(update.is_lost),
                update.last_seen_lat if update.is_lost else None,
                update.last_seen_lng if update.is_lost else None,
                last_seen_at,
                update.lost_notes if update.is_lost else None,
                pet_id
            )
        )

        conn.commit()

        updated_pet = conn.execute(
            "SELECT * FROM pets WHERE id = ?",
            (pet_id,)
        ).fetchone()

        return dict(updated_pet)

    finally:
        conn.close()



@app.post("/api/sightings", status_code=201)
def create_sighting(sighting: SightingCreate):
    conn = get_conn()

    try:
        if sighting.pet_id is not None:
            pet = conn.execute(
                "SELECT id FROM pets WHERE id = ?",
                (sighting.pet_id,)
            ).fetchone()

            if pet is None:
                raise HTTPException(
                    status_code=404,
                    detail="Referenced pet not found"
                )

        created_at = datetime.now(timezone.utc).isoformat()

        cursor = conn.execute(
            """
            INSERT INTO sightings (pet_id,
                                   description,
                                   lat,
                                   lng,
                                   reporter_name,
                                   photo_url,
                                   species,
                                   color,
                                   size,
                                   created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sighting.pet_id,
                sighting.description,
                sighting.lat,
                sighting.lng,
                sighting.reporter_name,
                sighting.photo_url,
                sighting.species,
                sighting.color,
                sighting.size,
                created_at
            )
        )

        conn.commit()

        saved_sighting = conn.execute(
            "SELECT * FROM sightings WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        lost_pets = conn.execute(
            "SELECT * FROM pets WHERE is_lost = 1"
        ).fetchall()

        matches = find_matches(
            saved_sighting,
            lost_pets,
            limit=3
        )

        return {
            "sighting": dict(saved_sighting),
            "matches": matches
        }

    finally:
        conn.close()



@app.get("/api/feed")
def get_feed():
    conn = get_conn()

    try:
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=30)
        ).isoformat()

        lost_pets = conn.execute(
            """
            SELECT
                id,
                tag_code,
                name,
                species,
                breed,
                color,
                size,
                markings,
                photo_url,
                last_seen_lat,
                last_seen_lng,
                last_seen_at,
                lost_notes
            FROM pets
            WHERE is_lost = 1
            AND last_seen_lat IS NOT NULL
            AND last_seen_lng IS NOT NULL
            ORDER BY last_seen_at DESC
            """
        ).fetchall()

        sightings = conn.execute(
            """
            SELECT
                id,
                pet_id,
                description,
                species,
                color,
                size,
                breed,
                markings,
                lat,
                lng,
                photo_url,
                created_at
            FROM sightings
            WHERE created_at >= ?
            ORDER BY created_at DESC
            """,
            (cutoff,)
        ).fetchall()

        return {
            "lost_pets": [dict(pet) for pet in lost_pets],
            "sightings": [dict(sighting) for sighting in sightings]
        }

    finally:
        conn.close()


@app.get("/api/pets/{pet_id}/matches")
def get_pet_matches(pet_id: int):
    conn = get_conn()

    try:
        pet = conn.execute(
            "SELECT * FROM pets WHERE id = ?",
            (pet_id,)
        ).fetchone()

        if pet is None:
            raise HTTPException(
                status_code=404,
                detail="Pet not found"
            )

        if not pet["is_lost"]:
            return []

        sightings = conn.execute(
            """
            SELECT *
            FROM sightings
            WHERE created_at >= ?
            ORDER BY created_at DESC
            """,
            (
                (
                    datetime.now(timezone.utc)
                    - timedelta(days=30)
                ).isoformat(),
            )
        ).fetchall()

        matches = []

        for sighting in sightings:
            result = match_pet(pet, sighting)

            if result is not None:
                matches.append({
                    "sighting": {
                        "id": sighting["id"],
                        "description": sighting["description"],
                        "species": sighting["species"],
                        "color": sighting["color"],
                        "size": sighting["size"],
                        "lat": sighting["lat"],
                        "lng": sighting["lng"],
                        "photo_url": sighting["photo_url"],
                        "created_at": sighting["created_at"]
                    },
                    "score": result["score"],
                    "reasons": result["reasons"]
                })

        matches.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return matches

    finally:
        conn.close()
