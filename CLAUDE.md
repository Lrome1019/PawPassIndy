# CLAUDE.md — PawPass Indy

Hackathon project (Indy Init 2026, ~5 hours). A lost-pet community app with exactly 4 features: Pet Passport, NFC/QR Tap Tag, Live Map, and AI Sighting Matcher. **README.md is the spec, and its API contract is the source of truth.** Do NOT build owner alerts/messaging or shelter lookup (cut by the mentor).

## Who you're working with
Two junior CS students. **Only Laura uses Claude Code.** Laura owns `frontend/`. Her classmate writes `backend/` by hand in VS Code.
- Default to working only in `frontend/`.
- Touch `backend/` only when Laura asks. If you do, have her `git pull` first, keep changes small, and add short comments so her classmate can follow the code.
- Until the backend is ready, the frontend runs on mock data (`USE_MOCK` in `api.js`) that matches the contract exactly.

## Priorities (in order)
1. **A demo that works end to end** beats more features. Ship the smallest working version first.
2. It must work on an **iPhone in Safari** (mobile-first, 44px+ tap targets, HTTPS needed for geolocation).
3. Keep it free: SQLite only, no paid services. The AI must always have an offline fallback.

## Stack rules
- Backend: Python 3.11+, FastAPI, stdlib `sqlite3` (no ORM). DB file `pawpass.db` at the repo root.
- Frontend: plain HTML + vanilla JS + Tailwind via CDN + Leaflet via CDN. **No npm, no React, no build step.**
- FastAPI serves `frontend/` as static files and maps `/t/{tag_code}` to `tag.html`.
- Never change an endpoint path or response shape without updating the README contract and saying so.
- Public endpoints (`/api/tag/*`, `/api/feed`) must never return `owner_phone`, `owner_email`, or `microchip_number`.
- `BASE_URL` comes from `.env` (the ngrok URL), so QR codes point to the right host.

## AI (`backend/ai.py`)
- `parse_description(text) -> dict` with keys `species, color, size, breed, markings`.
- Try Claude (model from the `CLAUDE_MODEL` env var, Haiku-class) with a 5s timeout and a JSON-only prompt. On any error or missing key, fall back to keyword matching. **Never let an AI failure break a request.**

## Matching (`backend/matching.py`)
Weighted score + `reasons[]` exactly as described in the README. Use haversine for distance. Treat close color words as similar (brown ≈ chocolate ≈ tan; black ≈ dark; orange ≈ ginger ≈ tabby).

## Commands
```bash
pip install -r requirements.txt
python -m backend.seed
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
ngrok http 8000
```

## Conventions
- Timestamps: ISO 8601 UTC strings.
- Seed coordinates: Indianapolis (39.7684, -86.1581), Fishers (39.9568, -86.0134), Muncie (40.1934, -85.3864).
- Frontend: all fetch calls go through `frontend/js/api.js`. Keep a `USE_MOCK` flag with mock data matching the contract.
- Before saying a feature is done, run the server and hit the endpoint (or the `/docs` page) to confirm it works.
