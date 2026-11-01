"""National course index: every named US golf course on OpenStreetMap, with how completely OSM maps it.

Runs on GitHub Actions (.github/workflows/national_index.yml; the sandbox cannot reach Overpass):

  python course_data/library/national_index.py fetch IA MO ... --out DIR   Overpass, per state in tiles -> DIR/<ST>/
  python course_data/library/national_index.py oga IA MO ... --out DIR     OpenGolfAPI state listings (best effort)
  python course_data/library/national_index.py merge DIR --oga D1,D2       -> us_courses.json.gz + us_readiness.json
  python course_data/library/national_index.py readme                      us_readiness.json -> README counts block

Fetch: each state's bbox (STATE_BBOX, padded) is cut into tiles of about 1 x 1 degree (larger for the big western
states and Alaska). One Overpass query per tile, filtered to the state's area, with a server timeout of
TILE_TIMEOUT_S and a client cap a little above it; each tile is tried once on each mirror (osm_guard.MIRRORS: the
three platform_common mirrors + one more), and a tile no mirror answers is split in four and retried, down to
MIN_TILE_DEG. Every tile is written as soon as it lands (DIR/<ST>/<tile>.json) and a tile already on disk is not
fetched again, so a time-out or a cancelled job loses at most the tile in flight, and a re-run (the workflow can
seed DIR from an earlier run's artifacts) only fetches what is missing. DIR/<ST>/_status.json says whether the state
is complete (every tile answered) or which tiles failed.

Per course (schema us_courses/2, columnar: "fields" + "rows"):
  name, city, state, lat, lon, osm ("way/123"), holes (the course's `holes` tag, else inferred),
  osm_holes (golf=hole ways: distinct refs, plus ways without a ref), greens, tees, fairways, pins (golf=green / tee
  / fairway / pin features whose centre is inside the course outline's bbox; a feature in two bboxes goes to the
  smaller course), outline (1 when the course is a way / relation, 0 for a bare node), card ("" unknown,
  "library" a library build found a web card, "oga" OpenGolfAPI lists it with a course par (its detail call
  usually returns the card), "oga?" listed without a par), tier (readiness, below), closed (1 when the name / tags
  say former / disused / abandoned).

Readiness tiers (what the course_page pipeline does with the course, course_data/library/README.md):
  A  complete OSM holes (a golf=hole per hole, a green per hole, tees on at least as many holes) and a known card:
     the case the pipeline handles best (auto-OK candidates)
  B  complete OSM holes, no known card (the page solves from OSM tees; a typed card moves it to A)
  C  partial OSM golf mapping (some holes / greens / tees): routed by routing v2, often short of holes
  D  outline only (no holes, greens or tees on OSM): no page without someone mapping it
"""
import argparse
import glob
import gzip
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_GZ = os.path.join(HERE, "us_courses.json.gz")
OUT_READY = os.path.join(HERE, "us_readiness.json")
LIB_INDEX = os.path.join(HERE, "index.json")
README = os.path.join(HERE, "README.md")
UA = "my_golf_data_science national course index (github.com/willbhedges/my_golf_data_science)"
try:                                    # the mirror list every other Overpass caller uses (platform/osm_guard.py)
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "platform"))
    from osm_guard import MIRRORS as OVERPASS                       # noqa: E402
    from platform_common import overpass_remark_problem             # noqa: E402
except Exception:                                                   # noqa: BLE001
    OVERPASS = ["https://overpass-api.de/api/interpreter",
                "https://overpass.kumi.systems/api/interpreter",
                "https://overpass.private.coffee/api/interpreter",
                "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]

    def overpass_remark_problem(js):
        rm = str((js or {}).get("remark") or "")
        return rm[:240] if re.search(r"runtime error|timed out|timeout|out of memory|maxsize|too busy|rate_limited",
                                     rm, re.I) else None
OPENGOLFAPI = "https://api.opengolfapi.org"
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
          "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
          "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
# (south, west, north, east), rounded outward; tiles outside the state's area come back empty and cheap.
# Alaska stops at -179.2 (the Aleutians west of the antimeridian have no golf course), Hawaii at the main islands.
STATE_BBOX = {
    "AL": (30.1, -88.5, 35.05, -84.85), "AK": (51.2, -179.2, 71.4, -129.9), "AZ": (31.3, -114.85, 37.05, -109.0),
    "AR": (33.0, -94.65, 36.5, -89.6), "CA": (32.5, -124.45, 42.05, -114.1), "CO": (36.95, -109.1, 41.05, -102.0),
    "CT": (40.95, -73.75, 42.05, -71.75), "DE": (38.45, -75.8, 39.85, -75.0), "DC": (38.79, -77.12, 39.0, -76.9),
    "FL": (24.4, -87.65, 31.05, -79.95), "GA": (30.35, -85.65, 35.05, -80.8), "HI": (18.9, -160.3, 22.25, -154.75),
    "ID": (41.95, -117.25, 49.05, -111.0), "IL": (36.95, -91.55, 42.55, -87.0), "IN": (37.75, -88.1, 41.8, -84.75),
    "IA": (40.35, -96.65, 43.55, -90.1), "KS": (36.95, -102.1, 40.05, -94.55), "KY": (36.45, -89.6, 39.15, -81.95),
    "LA": (28.9, -94.05, 33.05, -88.8), "ME": (42.95, -71.1, 47.5, -66.9), "MD": (37.9, -79.5, 39.75, -75.0),
    "MA": (41.2, -73.55, 42.9, -69.9), "MI": (41.65, -90.45, 48.3, -82.4), "MN": (43.45, -97.25, 49.4, -89.45),
    "MS": (30.15, -91.7, 35.05, -88.05), "MO": (35.95, -95.8, 40.65, -89.1), "MT": (44.35, -116.1, 49.05, -104.0),
    "NE": (39.95, -104.1, 43.05, -95.3), "NV": (34.95, -120.05, 42.05, -114.0), "NH": (42.65, -72.6, 45.35, -70.6),
    "NJ": (38.9, -75.6, 41.4, -73.85), "NM": (31.3, -109.1, 37.05, -103.0), "NY": (40.45, -79.8, 45.05, -71.8),
    "NC": (33.8, -84.35, 36.6, -75.4), "ND": (45.9, -104.1, 49.05, -96.5), "OH": (38.4, -84.85, 42.0, -80.5),
    "OK": (33.6, -103.05, 37.05, -94.4), "OR": (41.95, -124.6, 46.3, -116.45), "PA": (39.7, -80.55, 42.3, -74.65),
    "RI": (41.1, -71.9, 42.05, -71.1), "SC": (32.0, -83.4, 35.25, -78.5), "SD": (42.45, -104.1, 45.95, -96.4),
    "TN": (34.95, -90.35, 36.7, -81.6), "TX": (25.8, -106.7, 36.55, -93.5), "UT": (36.95, -114.1, 42.05, -109.0),
    "VT": (42.7, -73.45, 45.05, -71.45), "VA": (36.5, -83.7, 39.5, -75.2), "WA": (45.5, -124.85, 49.05, -116.9),
    "WV": (37.2, -82.7, 40.65, -77.7), "WI": (42.45, -92.9, 47.35, -86.2), "WY": (40.95, -111.1, 45.05, -104.0)}
TILE_TIMEOUT_S = 150          # Overpass [timeout:] per tile; the client gives up TILE_TIMEOUT_S + 30 s later
MIN_TILE_DEG = 0.2            # a tile no mirror answers is split in four until this size
OSM_TYPE = {"w": "way", "r": "relation", "n": "node"}
GOLF_KINDS = ("hole", "green", "tee", "fairway", "pin")
FIELDS = ["name", "city", "state", "lat", "lon", "osm", "holes", "osm_holes", "greens", "tees", "fairways", "pins",
          "outline", "card", "tier", "closed"]


def log(*a):
    print(*a, flush=True, file=sys.stderr)


# ------------------------------------------------------------------------------------------------ fetch (Actions)
def tile_deg(st):
    s, w, n, e = STATE_BBOX[st]
    area = (n - s) * (e - w)
    top = 4.0 if st == "AK" else 1.5     # dense metros in a 2-degree tile are slow; Alaska is mostly empty
    return min(top, max(0.5, round(math.sqrt(area / 40.0) * 4) / 4))      # ~40 tiles a state


def tiles(st):
    s, w, n, e = STATE_BBOX[st]
    d = tile_deg(st)
    out = []
    la = s
    while la < n - 1e-9:
        lo = w
        while lo < e - 1e-9:
            out.append((round(la, 4), round(lo, 4), round(min(la + d, n), 4), round(min(lo + d, e), 4)))
            lo += d
        la += d
    return out


def tile_name(t):
    return "t_%.4f_%.4f_%.4f_%.4f.json" % t


def tile_query(st, t, timeout=TILE_TIMEOUT_S):
    b = "(%.4f,%.4f,%.4f,%.4f)" % t
    return f"""[out:json][timeout:{timeout}][maxsize:536870912];
area["ISO3166-2"="US-{st}"]["admin_level"="4"]->.st;
.st out ids;
(way["leisure"="golf_course"]{b}(area.st); relation["leisure"="golf_course"]{b}(area.st);
 node["leisure"="golf_course"]["name"]{b}(area.st);)->.c;
.c out tags center;
.c out ids bb;
way["golf"~"^(hole|green|tee|fairway)$"]{b};
out tags center;
node["golf"~"^(green|tee|pin|hole)$"]{b};
out body;
node["place"~"^(city|town|village)$"]{b}(area.st);
out body;"""


def _post(url, q, timeout):
    req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class Mirrors:
    """Mirror order for one job: start at a job-specific offset, move a mirror that fails to the back."""

    def __init__(self, offset=0, post=_post, need_area=True):
        self.need_area = need_area
        self.order = OVERPASS[offset % len(OVERPASS):] + OVERPASS[:offset % len(OVERPASS)]
        self.post = post
        self.stats = {u: {"ok": 0, "fail": 0} for u in OVERPASS}

    def ask(self, q, timeout):
        """One try on each mirror -> (json, mirror) or raises with the errors."""
        errs = []
        for url in list(self.order):
            try:
                js = self.post(url, q, timeout)
                bad = overpass_remark_problem(js)
                if bad:
                    raise RuntimeError("remark: " + bad)
                if self.need_area and not any(e.get("type") == "area" for e in js.get("elements", [])):
                    # a mirror without the state's area answers every tile with nothing: not an answer
                    raise RuntimeError("no state area on this mirror")
                self.stats[url]["ok"] += 1
                return js, url
            except Exception as e:                                  # noqa: BLE001
                self.stats[url]["fail"] += 1
                errs.append(f"{url.split('/')[2]}: {e!r}"[:200])
                self.order.remove(url)
                self.order.append(url)
                time.sleep(3)
        raise RuntimeError("; ".join(errs))


def slim_elements(js):
    """Overpass elements -> compact rows; the ids+bb output of the course set is joined back onto its tags."""
    bbs, rows = {}, []
    for e in js.get("elements", []):
        if e.get("bounds") and not e.get("tags"):
            b = e["bounds"]
            bbs[(e["type"][0], e["id"])] = [b["minlat"], b["minlon"], b["maxlat"], b["maxlon"]]
    for e in js.get("elements", []):
        t = e.get("tags") or {}
        if not t:
            continue
        c = e.get("center") or ({"lat": e["lat"], "lon": e["lon"]} if "lat" in e else None)
        if not c:
            continue
        keep = {k: t[k] for k in ("name", "leisure", "golf", "ref", "holes", "addr:city", "addr:state", "place",
                                  "disused", "abandoned", "disused:leisure", "abandoned:leisure", "operator",
                                  "website", "access", "golf:course", "golf:course:name") if k in t}
        row = {"t": e["type"][0], "id": e["id"], "lat": round(c["lat"], 6), "lon": round(c["lon"], 6), "g": keep}
        if (e["type"][0], e["id"]) in bbs:
            row["bb"] = bbs[(e["type"][0], e["id"])]
        rows.append(row)
    return rows


def split4(t):
    s, w, n, e = t
    ms, mw = round((s + n) / 2, 4), round((w + e) / 2, 4)
    return [(s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e)]


def fetch_tile(st, t, d, mirrors, deadline, now=time.time):
    """Fetch one tile (splitting it when no mirror answers) -> list of tiles that still failed."""
    path = os.path.join(d, tile_name(t))
    if os.path.exists(path):
        return []
    if now() > deadline:
        return [t]
    t0 = now()
    try:
        js, url = mirrors.ask(tile_query(st, t), TILE_TIMEOUT_S + 30)
    except Exception as e:                                          # noqa: BLE001
        size = t[2] - t[0]
        log(f"  {st} tile {t} failed on every mirror ({e})"[:600])
        if size / 2 < MIN_TILE_DEG:
            return [t]
        log(f"  {st} tile {t}: splitting in four")
        bad = []
        for sub in split4(t):
            bad += fetch_tile(st, sub, d, mirrors, deadline, now)
        if not bad:                     # the parent is covered by its four quarters: record that
            json.dump({"state": st, "tile": t, "split": [list(x) for x in split4(t)], "elements": []},
                      open(path, "w"))
        return bad
    rows = slim_elements(js)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump({"state": st, "tile": list(t), "fetched": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()),
                   "mirror": url, "osm_base": (js.get("osm3s") or {}).get("timestamp_osm_base"), "elements": rows},
                  fh, separators=(",", ":"))
    os.replace(tmp, path)               # a half-written tile never looks fetched
    log(f"  {st} {tile_name(t)} {len(rows)} el {now() - t0:.0f}s {url.split('/')[2]}")
    return []


def fetch(states, out, budget_min=None, offset=None, now=time.time, mirrors=None):
    """Fetch every tile of every state not already on disk; returns {state: [failed tiles]}."""
    budget = float(budget_min if budget_min is not None else os.environ.get("NATIDX_BUDGET_MIN", "100")) * 60
    deadline = now() + budget
    mirrors = mirrors or Mirrors(int(offset if offset is not None else os.environ.get("NATIDX_MIRROR_OFFSET", "0")))
    result = {}
    for pass_ in (1, 2):
        for st in states:
            d = os.path.join(out, st)
            os.makedirs(d, exist_ok=True)
            ts = tiles(st)
            todo = [t for t in ts if not os.path.exists(os.path.join(d, tile_name(t)))]
            if not todo:
                result[st] = []
                write_status(d, st, ts, [])
                continue
            log(f"{st} pass {pass_}: {len(todo)} of {len(ts)} tiles to fetch ({tile_deg(st)} deg)")
            bad = []
            for t in todo:
                bad += fetch_tile(st, t, d, mirrors, deadline, now)
                time.sleep(1)
            result[st] = bad
            write_status(d, st, ts, bad)
            log(f"{st}: {'complete' if not bad else f'{len(bad)} tiles missing'}")
        if not any(result.values()) or now() > deadline:
            break
        log("pass 2 for", [s for s, b in result.items() if b], "after 60 s")
        time.sleep(60)
    log("mirrors:", json.dumps(mirrors.stats))
    return result


def write_status(d, st, ts, bad):
    have = [t for t in ts if os.path.exists(os.path.join(d, tile_name(t)))]
    json.dump({"state": st, "complete": len(have) == len(ts), "tiles": len(ts), "have": len(have),
               "missing": [list(t) for t in ts if t not in have], "failed_subtiles": [list(t) for t in bad]},
              open(os.path.join(d, "_status.json"), "w"))


def load_state_tiles(d):
    """-> (elements deduplicated by OSM id, status dict). Sub-tiles (from a split) are read like any tile."""
    seen, els = set(), []
    for p in sorted(glob.glob(os.path.join(d, "t_*.json"))):
        try:
            js = json.load(open(p))
        except Exception:                                           # noqa: BLE001
            continue
        for e in js.get("elements", []):
            k = (e["t"], e["id"])
            if k in seen:
                continue
            seen.add(k)
            els.append(e)
    st = os.path.basename(d.rstrip("/"))
    ts = tiles(st) if st in STATE_BBOX else []
    have = [t for t in ts if os.path.exists(os.path.join(d, tile_name(t)))]
    return els, {"tiles": len(ts), "have": len(have), "complete": bool(ts) and len(have) == len(ts)}


# ------------------------------------------------------------------------------------------------ OpenGolfAPI
def oga(states, out, max_calls=700):
    """OpenGolfAPI listing per state (1,000 anonymous calls / day): paged search; whatever comes back is kept."""
    os.makedirs(out, exist_ok=True)
    calls = 0
    for st in states:
        rows, page = [], 0
        while calls < max_calls and page < 40:
            url = f"{OPENGOLFAPI}/v1/courses/search?state={st}&limit=100&offset={page * 100}&page={page + 1}"
            js = None
            for attempt in range(3):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        js = json.loads(r.read().decode())
                    break
                except Exception as e:                              # noqa: BLE001
                    log(st, "oga failed:", repr(e)[:200])
                    time.sleep(10 * (attempt + 1))
            if js is None:
                break
            calls += 1
            cs = js.get("courses") if isinstance(js, dict) else js
            if not cs:
                break
            new = [c for c in cs if c.get("id") not in {r.get("id") for r in rows}]
            if not new:
                break
            rows += new
            if len(cs) < 100:
                break
            page += 1
            time.sleep(1.0)
        if rows:                        # an empty answer must not hide an earlier run's listing for the state
            with open(os.path.join(out, f"oga_{st}.json"), "w") as fh:
                json.dump({"state": st, "courses": rows}, fh, separators=(",", ":"))
        log(st, "oga", len(rows), "courses; calls so far", calls)
        if calls >= max_calls:
            break


# ------------------------------------------------------------------------------------------------ merge
def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(golf|course|club|country|cc|gc|the|links|and|of|at)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)


def dist_km(a, b, c, d):
    return math.hypot((a - c) * 111.0, (b - d) * 111.0 * math.cos(math.radians(a)))


def hole_ref(ref):
    """'7', 'Hole 7', '07' -> '7'; 'Red 3', 'N3' -> 'red3' (qualified: a 27 / 36-hole facility); else None."""
    r = (ref or "").strip().lower()
    m = re.fullmatch(r"(?:hole\s*)?0*(\d{1,2})", r)
    if m:
        return m.group(1)
    m = re.fullmatch(r"([a-z][a-z ]{0,15}?)[\s\-#]*0*(\d{1,2})", r)
    if m:
        return m.group(1).strip() + m.group(2)
    return None


def build_state(st, els):
    courses = [e for e in els if e["g"].get("leisure") == "golf_course" and e["g"].get("name")]
    feats = [e for e in els if e["g"].get("golf") in GOLF_KINDS]
    places = [e for e in els if e["g"].get("place") and e["g"].get("name")]
    # bbox containment, smallest course wins
    withbb = sorted([c for c in courses if c.get("bb")],
                    key=lambda c: (c["bb"][2] - c["bb"][0]) * (c["bb"][3] - c["bb"][1]))
    cell = {}
    for i, c in enumerate(withbb):
        b = c["bb"]
        for gx in range(int(math.floor(b[0] * 10)), int(math.floor(b[2] * 10)) + 1):
            for gy in range(int(math.floor(b[1] * 10)), int(math.floor(b[3] * 10)) + 1):
                cell.setdefault((gx, gy), []).append(i)
    acc = {}
    for f in feats:
        cand = cell.get((int(math.floor(f["lat"] * 10)), int(math.floor(f["lon"] * 10))), [])
        for i in sorted(cand):
            b = withbb[i]["bb"]
            pad = 0.0005
            if b[0] - pad <= f["lat"] <= b[2] + pad and b[1] - pad <= f["lon"] <= b[3] + pad:
                a = acc.setdefault(i, {"hole": 0, "refs": set(), "noref": 0, "green": 0, "tee": 0, "fairway": 0,
                                       "pin": 0})
                g = f["g"]["golf"]
                if g == "hole":
                    if f["t"] != "w":           # a golf=hole node is a mislabelled pin / marker, not a hole
                        break
                    a["hole"] += 1
                    r = hole_ref(f["g"].get("ref"))
                    if r:
                        a["refs"].add(r)
                    else:
                        a["noref"] += 1
                else:
                    a[g] += 1
                break
    idx = {id(c): i for i, c in enumerate(withbb)}
    pcell = {}
    for p in places:
        pcell.setdefault((int(p["lat"] * 4), int(p["lon"] * 4)), []).append(p)

    def city_of(lat, lon):
        best, bd = None, 25.0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for p in pcell.get((int(lat * 4) + dx, int(lon * 4) + dy), []):
                    w = {"city": 1.0, "town": 1.3, "village": 1.8}.get(p["g"]["place"], 2)
                    d = dist_km(lat, lon, p["lat"], p["lon"]) * w
                    if d < bd:
                        best, bd = p["g"]["name"], d
        return best

    rows = {}
    for c in courses:
        g = c["g"]
        a = acc.get(idx.get(id(c)), {"hole": 0, "refs": set(), "noref": 0, "green": 0, "tee": 0, "fairway": 0,
                                     "pin": 0})
        osm_holes = min(a["hole"], len(a["refs"]) + a["noref"])
        try:
            holes = int(re.match(r"\d+", g.get("holes", "")).group(0))
        except Exception:                                           # noqa: BLE001
            holes = 0
        if not holes or holes > 72:
            holes = 18 if osm_holes > 9 or a["green"] > 12 else (9 if osm_holes or a["green"] else 0)
        name = g["name"].strip()
        closed = int(bool(re.search(r"\b(former|closed|abandoned|defunct)\b", name, re.I)
                          or g.get("disused") or g.get("abandoned") or g.get("disused:leisure")
                          or g.get("abandoned:leisure")))
        row = dict(name=name, city=g.get("addr:city") or city_of(c["lat"], c["lon"]) or "",
                   state=st, lat=round(c["lat"], 5), lon=round(c["lon"], 5),
                   osm=OSM_TYPE[c["t"]] + "/" + str(c["id"]), holes=holes, osm_holes=osm_holes,
                   greens=a["green"], tees=a["tee"], fairways=a["fairway"], pins=a["pin"],
                   outline=int(bool(c.get("bb")) and c["t"] != "n"), card="", closed=closed)
        # the same course twice (an outline way and a relation, or an outline plus a name node): keep the richer
        key = (norm(name), round(c["lat"], 2), round(c["lon"], 2))
        old = rows.get(key)
        score = (row["osm_holes"] + row["greens"] + row["tees"], row["outline"])
        if old is None or score > (old["osm_holes"] + old["greens"] + old["tees"], old["outline"]):
            rows[key] = row
    return list(rows.values())


def tier(r):
    h = r["holes"] or 18
    complete = r["osm_holes"] >= h and r["greens"] >= h and r["tees"] >= h
    if complete:
        return "A" if r["card"] in ("library", "oga") else "B"
    if r["osm_holes"] or r["greens"] or r["tees"]:
        return "C"
    return "D"


def load_oga(oga_dirs):
    """{state: [courses]} from the first directory (in the order given) whose listing for the state is non-empty."""
    out = {}
    for d in oga_dirs:
        for path in sorted(glob.glob(os.path.join(d or "/nonexistent", "**", "oga_*.json"), recursive=True)):
            try:
                js = json.load(open(path))
            except Exception:                                       # noqa: BLE001
                continue
            st = (js.get("state") or "").upper()
            if js.get("courses") and st not in out:
                out[st] = js["courses"]
    return out


def attach_cards(rows, oga_dirs):
    """card: library builds that found a web card (by OSM id, else name + state), then OpenGolfAPI listings
    (name + state within 5 km, or a shared name stem within 1.5 km)."""
    by, by_osm = {}, {}
    for r in rows:
        by.setdefault((r["state"], norm(r["name"])), []).append(r)
        by_osm[r["osm"]] = r
    try:
        lib = json.load(open(LIB_INDEX))["courses"]
    except Exception:                                               # noqa: BLE001
        lib = []
    for c in lib:
        has_card = any(t.get("yards") for t in c.get("tee_sets") or []) and c.get("status") != "failed"
        hit = [by_osm[c["osm"]]] if c.get("osm") in by_osm else by.get((c.get("state"), norm(c.get("name"))), [])
        for r in hit:
            if has_card:
                r["card"] = "library"
            r["slug"] = c.get("slug")
    n_oga, n_listed = 0, 0
    grid = {}
    for r in rows:
        grid.setdefault((r["state"], int(r["lat"] * 20), int(r["lon"] * 20)), []).append(r)
    for st0, courses in load_oga(oga_dirs).items():
        for c in courses:
            n_listed += 1
            nm = c.get("course_name") or c.get("name") or c.get("club_name")
            st = (c.get("state") or st0 or "").upper()[:2]
            cands = by.get((st, norm(nm)), [])
            lat, lon = c.get("latitude") or c.get("lat"), c.get("longitude") or c.get("lon") or c.get("lng")
            if not cands and lat and lon:          # fuzzy: an OSM course within 1.5 km whose name shares a stem
                n1 = norm(nm)
                try:
                    la, lo = float(lat), float(lon)
                    near = [r for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                            for r in grid.get((st, int(la * 20) + dx, int(lo * 20) + dy), [])] if n1 else []
                    near = [r for r in near if dist_km(r["lat"], r["lon"], la, lo) <= 1.5]
                    cands = [r for r in near if (n2 := norm(r["name"])) and (n1 in n2 or n2 in n1 or n1[:6] == n2[:6])]
                except (TypeError, ValueError):
                    cands = []
            hit = False
            for r in cands:
                if lat and lon:
                    try:
                        if dist_km(r["lat"], r["lon"], float(lat), float(lon)) > 5:
                            continue
                    except (TypeError, ValueError):
                        pass
                hit = True
                if r["card"] == "library":
                    continue
                rich = bool(c.get("par")) or any(c.get(k) for k in ("tees", "holes_data", "scorecard"))
                r["card"] = "oga" if rich else (r["card"] if r["card"] == "oga" else "oga?")
            n_oga += hit
    log(f"opengolfapi: {n_listed} listed, {n_oga} matched to an OSM course")
    return n_listed, n_oga


def merge(raw, oga_dirs=None):
    rows, missing, partial, coverage = [], [], [], {}
    old = {}
    try:                                    # a state this run did not fetch keeps its rows from the committed index
        with gzip.open(OUT_GZ, "rt") as fh:
            o = json.load(fh)
        for row in o["rows"]:
            r = dict(zip(o["fields"], row))
            old.setdefault(r["state"], []).append(r)
        old_cov = {}
        with open(OUT_READY) as fh:
            old_cov = json.load(fh).get("coverage") or {}
    except Exception:                                               # noqa: BLE001
        old_cov = {}
    for st in STATES:
        d = os.path.join(raw, st)
        els, status = load_state_tiles(d) if os.path.isdir(d) else ([], {"have": 0})
        if not status["have"]:
            if old.get(st) and old_cov.get(st, {}).get("have"):
                rows += [dict({f: 0 for f in FIELDS}, **dict(r, card="" if r.get("card") == "library"
                                                              else r.get("card", ""))) for r in old[st]]
                coverage[st] = dict(old_cov[st], source="committed index")
                if not old_cov[st].get("complete"):
                    partial.append(st)
            else:
                missing.append(st)
            continue
        coverage[st] = dict(status, source="this run")
        if not status["complete"]:
            partial.append(st)
        rows += build_state(st, els)
    n_listed, n_oga = attach_cards(rows, oga_dirs or [])
    for r in rows:
        r["tier"] = tier(r)
    rows.sort(key=lambda r: (r["state"], r["name"].lower()))
    built = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    doc = {"schema": "us_courses/2", "doc": "course_data/library/README.md", "built": built,
           "source": "OpenStreetMap contributors (ODbL) via Overpass; OpenGolfAPI (ODbL) where it lists the course",
           "missing_states": missing, "partial_states": partial, "fields": FIELDS,
           "rows": [[r[f] for f in FIELDS] for r in rows]}
    with gzip.open(OUT_GZ, "wt", compresslevel=9) as fh:
        json.dump(doc, fh, separators=(",", ":"), ensure_ascii=False)
    write_readiness(rows, built, missing, partial, coverage, dict(listed=n_listed, matched=n_oga))
    log("rows", len(rows), "missing states", missing, "partial", partial, "gz bytes", os.path.getsize(OUT_GZ))
    return rows


def summary(rs):
    open_ = [r for r in rs if not r["closed"]]
    t = {k: sum(1 for r in open_ if r["tier"] == k) for k in "ABCD"}
    n = len(open_)

    def pct(x):
        return round(100 * x / n, 1) if n else 0.0
    return dict(n=n, closed=len(rs) - n, tiers=t,
                complete_osm_holes=t["A"] + t["B"], pct_complete=pct(t["A"] + t["B"]),
                any_osm_golf=t["A"] + t["B"] + t["C"], pct_any=pct(t["A"] + t["B"] + t["C"]),
                card_known=sum(1 for r in open_ if r["card"] in ("library", "oga")),
                oga_listed=sum(1 for r in open_ if r["card"] in ("library", "oga", "oga?")),
                with_outline=sum(1 for r in open_ if r["outline"]),
                with_holes=sum(1 for r in open_ if r["osm_holes"]),
                with_greens=sum(1 for r in open_ if r["greens"]),
                with_tees=sum(1 for r in open_ if r["tees"]),
                with_fairways=sum(1 for r in open_ if r["fairways"]),
                with_pins=sum(1 for r in open_ if r["pins"]),
                osm_holes_total=sum(r["osm_holes"] for r in open_))


def write_readiness(rows, built, missing, partial=(), coverage=None, oga_stats=None):
    states = {}
    for r in rows:
        states.setdefault(r["state"], []).append(r)
    per = {st: summary(rs) for st, rs in sorted(states.items())}
    ranked = sorted((s for s in per if per[s]["n"] >= 20), key=lambda s: -per[s]["pct_complete"])
    doc = {"schema": "us_readiness/2", "built": built, "missing_states": list(missing),
           "partial_states": list(partial),
           "tiers": {"A": "complete OSM holes + greens + tees, card known (pipeline's best case)",
                     "B": "complete OSM holes + greens + tees, no card known",
                     "C": "partial OSM golf mapping (routing v2 fills holes)",
                     "D": "outline only on OSM"},
           "national": summary(rows),
           "opengolfapi": oga_stats or {},
           "states": per,
           "best_states": ranked[:10],
           "worst_states": ranked[::-1][:10],
           "coverage": coverage or {}}
    with open(OUT_READY, "w") as fh:
        json.dump(doc, fh, indent=1)
    log(json.dumps(doc["national"]))
    return doc


def readme_block(doc):
    n = doc["national"]
    t = n["tiers"]
    per = doc["states"]

    def line(s):
        p = per[s]
        return f"{s} {p['pct_complete']} % ({p['tiers']['A'] + p['tiers']['B']} / {p['n']})"
    gaps = (f" Missing states: {', '.join(doc['missing_states'])}." if doc["missing_states"] else "") + \
        (f" Partly fetched (some tiles failed): {', '.join(doc['partial_states'])}." if doc["partial_states"] else "")
    return "\n".join([
        "<!-- NATIONAL_COUNTS -->",
        f"Counts from `us_readiness.json` (built {doc['built']}, {len(per)} states + DC with rows).{gaps}",
        "",
        "| | courses | share |",
        "|---|---|---|",
        f"| open named courses | {n['n']:,} | 100 % |",
        f"| tier A (complete OSM holes + card known) | {t['A']:,} | {round(100 * t['A'] / max(n['n'], 1), 1)} % |",
        f"| tier B (complete OSM holes, no card) | {t['B']:,} | {round(100 * t['B'] / max(n['n'], 1), 1)} % |",
        f"| tier C (partial OSM golf mapping) | {t['C']:,} | {round(100 * t['C'] / max(n['n'], 1), 1)} % |",
        f"| tier D (outline / name only) | {t['D']:,} | {round(100 * t['D'] / max(n['n'], 1), 1)} % |",
        f"| any golf=hole way | {n['with_holes']:,} | {round(100 * n['with_holes'] / max(n['n'], 1), 1)} % |",
        f"| any green | {n['with_greens']:,} | {round(100 * n['with_greens'] / max(n['n'], 1), 1)} % |",
        f"| any fairway | {n['with_fairways']:,} | {round(100 * n['with_fairways'] / max(n['n'], 1), 1)} % |",
        f"| any pin | {n['with_pins']:,} | {round(100 * n['with_pins'] / max(n['n'], 1), 1)} % |",
        f"| card known (library card or OpenGolfAPI par) | {n['card_known']:,} | "
        f"{round(100 * n['card_known'] / max(n['n'], 1), 1)} % |",
        "",
        "Complete OSM holes (A + B), states with at least 20 courses: best " +
        ", ".join(line(s) for s in doc["best_states"][:5]) + "; worst " +
        ", ".join(line(s) for s in doc["worst_states"][:5]) + ".",
        "<!-- /NATIONAL_COUNTS -->"])


def write_readme(path=README, ready=OUT_READY):
    doc = json.load(open(ready))
    txt = open(path).read()
    block = readme_block(doc)
    if "<!-- /NATIONAL_COUNTS -->" in txt:
        txt = re.sub(r"<!-- NATIONAL_COUNTS -->.*?<!-- /NATIONAL_COUNTS -->", lambda m: block, txt, flags=re.S)
    else:
        txt = txt.replace("<!-- NATIONAL_COUNTS -->", block)
    open(path, "w").write(txt)


def shards(states, n=6):
    """Greedy split of states over n jobs by tile count (dense states count a bit more)."""
    dense = {"CA": 1.8, "FL": 1.8, "TX": 1.3, "NY": 1.5, "MI": 1.3, "OH": 1.4, "PA": 1.4, "IL": 1.4, "NJ": 2.0,
             "MA": 2.0, "NC": 1.4, "GA": 1.3, "WI": 1.3, "MN": 1.3, "CT": 2.0, "MD": 1.6, "VA": 1.3, "SC": 1.3}
    w = {s: len(tiles(s)) * dense.get(s, 1.0) for s in states}
    out = [[] for _ in range(min(n, len(states)) or 1)]
    load = [0.0] * len(out)
    for s in sorted(states, key=lambda s: -w[s]):
        i = load.index(min(load))
        out[i].append(s)
        load[i] += w[s]
    return [" ".join(x) for x in out if x]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "oga", "merge", "readme", "shards"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--out", default="/tmp/natidx")
    ap.add_argument("--oga", default="", help="comma-separated OpenGolfAPI listing dirs, first wins per state")
    ap.add_argument("--n", type=int, default=6)
    a = ap.parse_args()
    sts = [s.upper() for s in a.args] or STATES
    if a.cmd == "fetch":
        res = fetch(sts, a.out)
        log("failed tiles:", {s: len(b) for s, b in res.items() if b})
    if a.cmd == "oga":
        oga(sts, a.out)
    if a.cmd == "merge":
        merge(a.args[0] if a.args else a.out, [d for d in a.oga.split(",") if d])
        write_readme()
    if a.cmd == "readme":
        write_readme()
    if a.cmd == "shards":
        print(json.dumps(shards(sts, a.n)))


if __name__ == "__main__":
    main()
