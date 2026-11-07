# 🐾 PawPass Indy

**A community lost-pet network for Hoosiers: one tap on a collar tag brings a pet home.**

Built at **Indy Init 2026** for the **Community Problems** award by two Ball State CS juniors.

---

## The problem

Your pet gets microchipped. Years later it goes missing. Then you're digging through old paperwork for a chip number, trying to remember which registry you signed up with, and calling a shelter that has no record because you renamed the pet after adoption. Meanwhile, neighbors who spot your pet have no fast way to help.

The data that reunites families exists, but it's scattered and stale. **PawPass puts it in one place, attached to the pet.**

## What we're building (4 features)

1. **Pet Passport.** One profile per pet: photo, current and previous names, microchip number, chip registry, adoption shelter, adoption date and ID, and identifying features.
2. **Tap-to-Help Tag.** Each passport gets a unique URL, encoded into a **QR code** and a **~$0.30 NFC sticker** on the collar. Any iPhone opens it with a tap or a camera scan, with no app install. The tag page shows the pet and a **"Report a sighting"** button.
3. **Live Community Map.** Lost pets and sightings appear on an Indianapolis map that refreshes every 5 seconds.
4. **AI Sighting Matcher.** Someone types *"small brown dog with white chest near Fishers library."* AI turns that into structured features, then ranks matches against lost pets by species, color, size, distance, and time, and explains *why* each one matched.

> **Judges' note:** the hardware is commodity on purpose: an NFC sticker is just a URL. All of the intelligence lives in the software: the data model, the AI parsing, the matching, and the real-time map.

**Out of scope:** owner messaging/alerts and shelter lookup. Don't build them.

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | **Python 3.11+, FastAPI, Uvicorn** | Fast to write, auto docs at `/docs` |
| Database | **SQLite** (one file, `pawpass.db`) | Free, zero setup |
| Frontend | **Plain HTML + JS + Tailwind (CDN)** | No npm, works on any phone |
| Map | **Leaflet + OpenStreetMap** | Free, no API key |
| QR codes | `qrcode` Python lib | PNG generated server-side |
| AI | Claude API (Haiku) **with a keyword fallback** | The demo still works with no key or no Wi-Fi |
| Real-time | Frontend polls `/api/feed` every 5s | Simple and reliable |
| Phone demo | `ngrok http 8000` | HTTPS URL that iPhones need for GPS |

---

## Setup (VS Code, about 5 minutes)

```bash
git clone <REPO_URL>
cd pawpass-indy
python -m venv .venv
# Mac/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # optional: add ANTHROPIC_API_KEY
python -m backend.seed        # loads demo pets and sightings around Indy
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- App: http://localhost:8000
- **API docs (test every endpoint here): http://localhost:8000/docs**
- On an iPhone: run `ngrok http 8000`, then put the HTTPS URL in `.env` as `BASE_URL`.

---

## Repo structure

```
pawpass-indy/
├── README.md               # the spec (this file)
├── CLAUDE.md               # instructions for Laura's Claude Code
├── requirements.txt
├── .env.example
├── backend/
│   ├── main.py             # FastAPI app, routes, static file serving
│   ├── db.py               # SQLite connection and schema creation
│   ├── matching.py         # scoring: features + distance + time
│   ├── ai.py               # Claude parsing with keyword fallback
│   └── seed.py             # demo data (Indianapolis-area coordinates)
├── frontend/
│   ├── index.html          # live map + feed (home)
│   ├── passport.html       # create a pet passport and show its QR code
│   ├── pet.html            # owner page: mark lost, see AI matches
│   ├── tag.html            # what a finder sees after tapping a tag (/t/{code})
│   ├── report.html         # report a sighting (with or without a tag)
│   ├── js/api.js           # shared fetch helpers (+ USE_MOCK flag)
│   └── css/app.css
└── uploads/                # pet photos (gitignored)
```

---

## Database schema (SQLite)

```sql
CREATE TABLE IF NOT EXISTS pets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tag_code TEXT UNIQUE,           -- 8-char random code used in /t/{code}
  name TEXT, previous_names TEXT, -- comma-separated
  species TEXT, breed TEXT, color TEXT, size TEXT,  -- size: small|medium|large
  markings TEXT, photo_url TEXT,
  microchip_number TEXT, chip_registry TEXT,
  adoption_shelter TEXT, adoption_date TEXT, adoption_id TEXT,
  owner_name TEXT, owner_phone TEXT, owner_email TEXT,
  is_lost INTEGER DEFAULT 0,
  last_seen_lat REAL, last_seen_lng REAL, last_seen_at TEXT, lost_notes TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS sightings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pet_id INTEGER,                 -- set when reported from a tag page, else NULL
  description TEXT,
  species TEXT, color TEXT, size TEXT, breed TEXT, markings TEXT,  -- filled by AI parse
  lat REAL, lng REAL, photo_url TEXT,
  reporter_name TEXT,
  created_at TEXT
);
```

---



All JSON. **Public endpoints (`/api/tag/*`, `/api/feed`) never return `owner_phone`, `owner_email`, or `microchip_number`.**

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/pets` | pet fields as JSON | full pet incl. `id`, `tag_code` |
| GET | `/api/pets/{id}` | — | full pet (owner view) |
| GET | `/api/pets/{id}/qr.png` | — | PNG QR code → `{BASE_URL}/t/{tag_code}` |
| PATCH | `/api/pets/{id}/lost` | `{is_lost, last_seen_lat, last_seen_lng, lost_notes}` | pet |
| GET | `/api/tag/{tag_code}` | — | public pet view |
| POST | `/api/sightings` | `{description, lat, lng, reporter_name, pet_id?}` | `{sighting, matches: [top 3]}` |
| GET | `/api/pets/{id}/matches` | — | `[{sighting, score, reasons[]}]`, best first |
| GET | `/api/feed` | — | `{lost_pets: [...], sightings: [...]}` (sightings from the last 30 days) |
| POST | `/api/ai/parse` | `{text}` | `{species, color, size, breed, markings}` |

Page routes: `/` → `index.html`, `/t/{tag_code}` → `tag.html`, and other pages served from `/frontend`.

### Example: `POST /api/sightings` response
```json
{
  "sighting": {"id": 12, "description": "small brown dog white chest", "species": "dog",
               "color": "brown", "size": "small", "lat": 39.95, "lng": -86.01,
               "created_at": "2026-11-07T17:30:00Z"},
  "matches": [
    {"pet": {"id": 3, "name": "Biscuit", "species": "dog", "color": "brown"},
     "score": 0.87,
     "reasons": ["Same species", "Color match: brown", "Same size", "0.8 mi from last seen", "Lost 2 days ago"]}
  ]
}
```

### Match scoring (`matching.py`)

```
score = 0.35*species + 0.25*color + 0.15*size + 0.15*distance + 0.10*recency
species: 1 if equal, else 0 (if species is 0, skip the pet entirely)
color:   1 exact, 0.6 similar (brown≈tan≈chocolate, orange≈ginger, black≈dark, gray≈grey≈silver), else 0
size:    1 equal, 0.5 one step apart (small↔medium), else 0
distance (haversine miles from pet's last_seen): 1.0 if ≤ 0.5 mi, falls linearly to 0 at 10 mi
recency  (sighting time vs last_seen_at):        1.0 if ≤ 1 day, falls linearly to 0 at 30 days
reasons[]: one readable string per factor that scored > 0
```

### AI parse (`ai.py`)
- If `ANTHROPIC_API_KEY` is set, ask Claude to return JSON only with the 5 keys, with a 5s timeout.
- **Otherwise, or on any error:** keyword fallback. Lowercase the text and look for word lists
  (`dog/puppy/pup` → dog, `cat/kitten/kitty` → cat; color words; `small/tiny/little` → small, etc.).
- It must never crash a request.

---

**Jovan Dukes: backend (`backend/`)**
- [ ] **B1** `db.py`: `get_conn()` (with `row_factory = sqlite3.Row`) and `init_db()` running the schema above. Then `seed.py` with about 8 lost pets and about 15 sightings around Indy, Fishers, and Muncie.
- [ ] **B2** `main.py`: `POST/GET /api/pets`, `tag_code` via `secrets.token_urlsafe(6)`, the QR endpoint, and `GET /api/tag/{code}` (strip private fields).
- [ ] **B3** `PATCH /lost`, `POST /api/sightings`, `GET /api/feed`. Serve `frontend/` with `StaticFiles` and add the `/t/{code}` route.
- [ ] **B4** `matching.py` with the formula above, plus `GET /api/pets/{id}/matches`, and top 3 matches in the sightings response.
- [ ] **B5** `ai.py` keyword fallback first, then the Claude call if time allows. Wire it into `POST /api/sightings` and `/api/ai/parse`.

**Laura Romero: frontend (`frontend/`), demo, data**
- [ ] **F1** `api.js` with a `USE_MOCK = true` flag and mock data that follows the contract, plus a shared mobile-first nav.
- [ ] **F2** `index.html`: Leaflet map centered on Indy, red pins for lost pets and yellow for sightings, a feed list, and polling every 5s.
- [ ] **F3** `passport.html`: form → POST → show the QR code and the tag URL ("write this to your NFC tag").
- [ ] **F4** `tag.html`: read the code from the URL → show photo, name, and features → **"Report a sighting"** button → `report.html?pet_id=…`
- [ ] **F5** `report.html`: description box + "Use my location" (`navigator.geolocation`) → POST → show AI-parsed features and top matches.
- [ ] **F6** `pet.html`: "Mark as lost" toggle (uses current location) and a match list with score bars and reasons.
- [ ] **F7** Program a real NFC sticker, write the demo script, rehearse.





- 📄 **Paperwork scanner:** upload a photo of old adoption papers, and Claude vision fills in the chip number, registry, and shelter.

## Privacy

- Public pages never show owner contact info or the microchip number.
- A finder's location is shared only when they tap "Use my location."
