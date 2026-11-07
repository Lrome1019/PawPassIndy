// Shared API helpers + mock data. Flip USE_MOCK to false once the backend works.
// Mock responses follow the README API contract exactly.
const USE_MOCK = true;
const BASE = ""; // same origin as FastAPI

// ---------- shared helpers ----------
const $ = (s, r = document) => r.querySelector(s);
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function ago(iso) {
  const m = Math.max(0, Math.round((Date.now() - new Date(iso)) / 60000));
  if (m < 60) return m + " min ago";
  if (m < 1440) return Math.round(m / 60) + " hr ago";
  return Math.round(m / 1440) + " day(s) ago";
}
function getLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject(new Error("Location not supported"));
    navigator.geolocation.getCurrentPosition(
      p => resolve({ lat: p.coords.latitude, lng: p.coords.longitude }),
      () => reject(new Error("Couldn't get location. Check Safari location permission (needs HTTPS).")),
      { enableHighAccuracy: true, timeout: 10000 });
  });
}
function renderNav(active) {
  const links = [["/", "Map"], ["/passport.html", "New Pet"], ["/report.html", "Report"]];
  const nav = document.createElement("nav");
  nav.className = "sticky top-0 z-[1000] bg-amber-500 text-white shadow";
  nav.innerHTML = `<div class="max-w-2xl mx-auto flex items-center justify-between px-3">
    <a href="/" class="font-bold text-lg py-3">🐾 PawPass Indy</a>
    <div class="flex">${links.map(([h, t]) =>
      `<a href="${h}" class="px-3 py-3 min-h-[44px] ${active === t ? "underline font-semibold" : ""}">${t}</a>`).join("")}</div></div>
    ${USE_MOCK ? '<div class="bg-yellow-100 text-yellow-900 text-xs text-center py-1">Demo mode: mock data</div>' : ""}`;
  document.body.prepend(nav);
}

// ---------- mock backend ----------
const PRIVATE = ["owner_phone", "owner_email", "microchip_number"];
const publicPet = p => { const c = { ...p }; PRIVATE.forEach(k => delete c[k]); return c; };
const iso = (minsAgo = 0) => new Date(Date.now() - minsAgo * 60000).toISOString();

function seedMock() {
  return {
    nextPet: 4, nextSighting: 4,
    pets: [
      { id: 1, tag_code: "biscuit1", name: "Biscuit", previous_names: "Cookie", species: "dog", breed: "Terrier mix", color: "brown", size: "small", markings: "white chest", photo_url: "", microchip_number: "985112345678901", chip_registry: "HomeAgain", adoption_shelter: "Indy Humane", adoption_date: "2023-04-02", adoption_id: "A1234", owner_name: "Sam", owner_phone: "555-0101", owner_email: "sam@example.com", is_lost: 1, last_seen_lat: 39.9568, last_seen_lng: -86.0134, last_seen_at: iso(2880), lost_notes: "Slipped out the back gate", created_at: iso(99999) },
      { id: 2, tag_code: "whisker2", name: "Whiskers", previous_names: "", species: "cat", breed: "Tabby", color: "orange", size: "medium", markings: "striped tail", photo_url: "", microchip_number: "985198765432100", chip_registry: "PetLink", adoption_shelter: "Muncie Animal Shelter", adoption_date: "2022-05-10", adoption_id: "M77", owner_name: "Dana", owner_phone: "555-0102", owner_email: "dana@example.com", is_lost: 1, last_seen_lat: 40.1934, last_seen_lng: -85.3864, last_seen_at: iso(7200), lost_notes: "Missing since May", created_at: iso(99999) },
      { id: 3, tag_code: "shadow03", name: "Shadow", previous_names: "", species: "dog", breed: "Lab", color: "black", size: "large", markings: "", photo_url: "", microchip_number: "", chip_registry: "", adoption_shelter: "", adoption_date: "", adoption_id: "", owner_name: "Lee", owner_phone: "555-0103", owner_email: "lee@example.com", is_lost: 0, last_seen_lat: null, last_seen_lng: null, last_seen_at: null, lost_notes: "", created_at: iso(99999) },
    ],
    sightings: [
      { id: 1, pet_id: null, description: "small brown dog with white chest near Fishers library", species: "dog", color: "brown", size: "small", breed: "", markings: "white chest", lat: 39.9601, lng: -86.0102, photo_url: "", reporter_name: "Pat", created_at: iso(120) },
      { id: 2, pet_id: null, description: "orange tabby cat in alley", species: "cat", color: "orange", size: "medium", breed: "", markings: "", lat: 40.19, lng: -85.39, photo_url: "", reporter_name: "Jo", created_at: iso(600) },
      { id: 3, pet_id: null, description: "big black dog downtown", species: "dog", color: "black", size: "large", breed: "", markings: "", lat: 39.7684, lng: -86.1581, photo_url: "", reporter_name: "Al", created_at: iso(60) },
    ],
  };
}
function db() {
  try { const s = JSON.parse(localStorage.getItem("pawpass_mock")); if (s) return s; } catch (e) {}
  const s = seedMock(); saveDb(s); return s;
}
function saveDb(s) { try { localStorage.setItem("pawpass_mock", JSON.stringify(s)); } catch (e) {} }

// keyword fallback, same idea as backend/ai.py
function mockParse(text) {
  const t = (text || "").toLowerCase(), has = ws => ws.some(w => new RegExp("\\b" + w + "\\b").test(t));
  const out = { species: "", color: "", size: "", breed: "", markings: "" };
  if (has(["dog", "puppy", "pup"])) out.species = "dog"; else if (has(["cat", "kitten", "kitty"])) out.species = "cat";
  out.color = ["brown", "black", "white", "tan", "chocolate", "orange", "ginger", "gray", "grey", "silver", "golden", "yellow"].find(c => has([c])) || "";
  if (has(["small", "tiny", "little"])) out.size = "small"; else if (has(["large", "big", "huge"])) out.size = "large"; else if (has(["medium"])) out.size = "medium";
  const m = t.match(/(white|black|brown) (chest|paws|tail|spot|patch|collar)/); if (m) out.markings = m[0];
  return out;
}
const SIMILAR = [["brown", "tan", "chocolate"], ["orange", "ginger"], ["black", "dark"], ["gray", "grey", "silver"]];
const colorScore = (a, b) => !a || !b ? 0 : a === b ? 1 : SIMILAR.some(g => g.includes(a) && g.includes(b)) ? 0.6 : 0;
function miles(a, b, c, d) {
  const r = x => x * Math.PI / 180, h = Math.sin(r(c - a) / 2) ** 2 + Math.cos(r(a)) * Math.cos(r(c)) * Math.sin(r(d - b) / 2) ** 2;
  return 3958.8 * 2 * Math.asin(Math.sqrt(h));
}
function mockScore(pet, s) { // formula from README
  if (!pet.species || pet.species !== s.species) return null;
  const reasons = ["Same species"]; let score = 0.35;
  const c = colorScore(pet.color, s.color);
  if (c) { score += 0.25 * c; reasons.push(c === 1 ? "Color match: " + pet.color : "Similar color: " + s.color + " ≈ " + pet.color); }
  const o = ["small", "medium", "large"], d = Math.abs(o.indexOf(pet.size) - o.indexOf(s.size));
  if (pet.size && s.size && d <= 1) { score += 0.15 * (d === 0 ? 1 : 0.5); reasons.push(d === 0 ? "Same size" : "Similar size"); }
  if (pet.last_seen_lat != null && s.lat != null) {
    const mi = miles(pet.last_seen_lat, pet.last_seen_lng, s.lat, s.lng), ds = mi <= 0.5 ? 1 : Math.max(0, 1 - (mi - 0.5) / 9.5);
    if (ds > 0) { score += 0.15 * ds; reasons.push(mi.toFixed(1) + " mi from last seen"); }
  }
  if (pet.last_seen_at) {
    const days = Math.abs(new Date(s.created_at) - new Date(pet.last_seen_at)) / 864e5, rs = days <= 1 ? 1 : Math.max(0, 1 - (days - 1) / 29);
    if (rs > 0) { score += 0.10 * rs; reasons.push("Lost " + Math.round(days) + " day(s) before sighting"); }
  }
  return { score: Math.round(score * 100) / 100, reasons };
}
const ok = v => Promise.resolve(JSON.parse(JSON.stringify(v)));
const fail = m => Promise.reject(new Error(m));

const mock = {
  createPet(body) {
    const s = db(), pet = { is_lost: 0, last_seen_lat: null, last_seen_lng: null, last_seen_at: null, lost_notes: "", photo_url: "", ...body, id: s.nextPet++, tag_code: Math.random().toString(36).slice(2, 10), created_at: iso() };
    s.pets.push(pet); saveDb(s); return ok(pet);
  },
  getPet(id) { const p = db().pets.find(p => p.id == id); return p ? ok(p) : fail("Pet not found"); },
  setLost(id, b) {
    const s = db(), p = s.pets.find(p => p.id == id); if (!p) return fail("Pet not found");
    Object.assign(p, { is_lost: b.is_lost ? 1 : 0, last_seen_lat: b.last_seen_lat, last_seen_lng: b.last_seen_lng, lost_notes: b.lost_notes || "", last_seen_at: b.is_lost ? iso() : p.last_seen_at });
    saveDb(s); return ok(p);
  },
  getTag(code) { const p = db().pets.find(p => p.tag_code === code); return p ? ok(publicPet(p)) : fail("Unknown tag"); },
  createSighting(b) {
    const s = db(), parsed = mockParse(b.description);
    const sighting = { id: s.nextSighting++, pet_id: b.pet_id ?? null, description: b.description, ...parsed, lat: b.lat, lng: b.lng, photo_url: "", reporter_name: b.reporter_name || "", created_at: iso() };
    s.sightings.push(sighting); saveDb(s);
    const matches = s.pets.filter(p => p.is_lost).map(p => ({ p, m: mockScore(p, sighting) })).filter(x => x.m)
      .sort((a, b) => b.m.score - a.m.score).slice(0, 3)
      .map(({ p, m }) => ({ pet: { id: p.id, name: p.name, species: p.species, color: p.color }, score: m.score, reasons: m.reasons }));
    return ok({ sighting, matches });
  },
  getMatches(id) {
    const s = db(), p = s.pets.find(p => p.id == id); if (!p) return fail("Pet not found");
    return ok(s.sightings.map(x => ({ sighting: x, ...(mockScore(p, x) || {}) })).filter(x => x.score != null).sort((a, b) => b.score - a.score));
  },
  getFeed() {
    const s = db(), cut = Date.now() - 30 * 864e5;
    return ok({ lost_pets: s.pets.filter(p => p.is_lost).map(publicPet), sightings: s.sightings.filter(x => new Date(x.created_at) > cut) });
  },
  parse(text) { return ok(mockParse(text)); },
};

// ---------- real calls ----------
async function http(method, path, body) {
  const r = await fetch(BASE + path, { method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined });
  if (!r.ok) throw new Error((await r.text().catch(() => "")) || r.statusText);
  return r.json();
}

// ---------- public API: ALL pages use this ----------
const api = {
  createPet: b => USE_MOCK ? mock.createPet(b) : http("POST", "/api/pets", b),
  getPet: id => USE_MOCK ? mock.getPet(id) : http("GET", `/api/pets/${id}`),
  qrUrl: id => USE_MOCK ? null : `${BASE}/api/pets/${id}/qr.png`, // mock mode: pages show a placeholder
  setLost: (id, b) => USE_MOCK ? mock.setLost(id, b) : http("PATCH", `/api/pets/${id}/lost`, b),
  getTag: c => USE_MOCK ? mock.getTag(c) : http("GET", `/api/tag/${encodeURIComponent(c)}`),
  createSighting: b => USE_MOCK ? mock.createSighting(b) : http("POST", "/api/sightings", b),
  getMatches: id => USE_MOCK ? mock.getMatches(id) : http("GET", `/api/pets/${id}/matches`),
  getFeed: () => USE_MOCK ? mock.getFeed() : http("GET", "/api/feed"),
  aiParse: text => USE_MOCK ? mock.parse(text) : http("POST", "/api/ai/parse", { text }),
};
