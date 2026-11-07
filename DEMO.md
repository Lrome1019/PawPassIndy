# PawPass Indy: Demo Script (3–5 min)

Laura presents. The classmate drives the big-screen laptop (map open on `/`). Rehearse twice.

## Before you go on (setup checklist)

- [ ] Backend running: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`, seeded with `python -m backend.seed`
- [ ] `ngrok http 8000` running, HTTPS URL copied into `.env` as `BASE_URL`, server restarted
- [ ] `USE_MOCK = false` in `frontend/js/api.js`
- [ ] Laptop on the big screen showing the map at `<ngrok URL>/`
- [ ] iPhone: Safari location allowed for the ngrok site (tap "Use my location" once to grant it)
- [ ] NFC sticker already written (see below) and stuck on a collar or prop
- [ ] Backup: screen recording of the full flow saved on the laptop desktop
- [ ] Wi-Fi/hotspot tested in the room. Have a phone hotspot ready as plan B.

## The script

### 1. Hook (30s)
> "A family's cat went missing in May. The microchip number was buried in old adoption papers, the shelter had her under a different name, and neighbors who saw her had no way to help. The data to bring her home existed, but it was scattered. PawPass puts it in one place, attached to the pet."

### 2. Pet Passport (45s) · `passport.html`
- Open **New Pet** on the phone. Fill in: name, **previous name** (for example "Cookie"), species, color, size, chip number, registry, shelter.
- Tap **Create passport**. Show the **QR code** and the tag URL.
> "One passport per pet: current and previous names, chip number, registry, adoption details. Each one gets its own link."

### 3. The tap (60s) · the wow moment
- Have a judge **tap the NFC sticker** with their own iPhone (or scan the QR code with the camera).
- The tag page opens in Safari, no app. Point out: photo, name, features, and **no owner phone or chip number** shown publicly.
- Judge taps **Report a sighting** → **Use my location** → submits.
- Turn to the big screen: **a new yellow pin appears on the live map** within 5 seconds.
> "A tap on a $0.30 sticker, no app install, and the whole neighborhood sees it."

### 4. AI match (60s) · `report.html` then `pet.html`
- Mark the demo pet as lost first (owner page → **Mark as lost**). Do this before the demo so it's already on the map as a red pin.
- On **Report**, type in plain English, with no tag: *"small brown dog with white chest near Fishers library"*. Submit.
- Show the parsed chips (species, color, size, markings) and the **ranked matches with reasons**.
- Open the owner page: sightings ranked with score bars.
> "Anyone can describe a pet in their own words. AI turns it into structured features, then ranks matches by species, color, size, distance and time, and tells you why."

### 5. Close (30s)
> "Free, works on any phone, $0.30 a tag, no hardware to build. Built for Hoosier neighbors and shelters."

## Programming the NFC sticker (F7)

1. Buy NTAG213 or NTAG215 stickers (any iPhone 7 or newer can read them).
2. Install the free **NFC Tools** app on the iPhone.
3. In `passport.html`, create the pet and copy the **tag URL** (it starts with your ngrok `BASE_URL` and ends with `/t/<code>`).
4. NFC Tools → **Write** → **Add a record** → **URL/URI** → paste the URL → **Write** → hold the iPhone to the sticker until it confirms.
5. Test it: lock the phone, tap the sticker, and confirm Safari opens the tag page.
6. **Important:** the ngrok URL changes every time you restart ngrok. Write the sticker *after* the URL is final on demo day, or use a paid fixed domain. Rewrite the sticker if the URL changes.

## If something breaks

| Problem | Fix |
|---|---|
| NFC doesn't open | Scan the QR code on screen instead |
| Location denied | Tap the Safari "aA" menu → Website Settings → Location → Allow |
| Backend down | Set `USE_MOCK = true` and demo from the mock data (flow is identical) |
| No Wi-Fi | Phone hotspot, and restart ngrok, then rewrite the sticker |
| AI slow or no API key | Keyword fallback runs automatically. Nothing to do. |
| Everything fails | Play the backup recording |

## Likely judge questions

- **"How is this different from microchip registries?"** The passport follows the pet through renames and shelters, and the tag works for anyone without an app.
- **"What about privacy?"** Public pages never show owner contact info or the chip number, and location is shared only when the finder taps "Use my location."
- **"What does it cost?"** Software is free to run (SQLite, OpenStreetMap, free AI fallback). The only hardware is the sticker.
- **"What's next?"** Owner alerts, shelter lookup, and a paperwork scanner that reads old adoption papers with Claude vision.
