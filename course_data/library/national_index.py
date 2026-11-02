"""National course index: every named US golf course on OpenStreetMap, with how completely OSM maps it.

Runs on GitHub Actions (.github/workflows/national_index.yml; the sandbox cannot reach Overpass):

  python course_data/library/national_index.py fetch [ST ...] --shard i/n --out DIR   Overpass cells -> DIR/cells/
  python course_data/library/national_index.py oga IA MO ... --out DIR     OpenGolfAPI state listings (best effort)
  python course_data/library/national_index.py merge DIR --oga D1,D2       -> us_courses.json.gz + us_readiness.json
  python course_data/library/national_index.py readme                      us_readiness.json -> README counts block

Fetch: the US is cut into a grid of 1 x 1 degree cells (2 x 2 in Alaska) touching some state's bbox (STATE_BBOX),
about 1,400 cells. One bbox-only Overpass query per cell (course outlines, golf=hole / green / tee / fairway / pin,
place names), CELL_TIMEOUT_S server timeout and a client cap 30 s above it; each cell is tried once on each mirror
(osm_guard.MIRRORS: the three platform_common mirrors + one more; a mirror failing 3 times in a row rests 15 min),
and a cell no mirror answers is split in four and retried, down to MIN_CELL_DEG. Every cell is written the moment
it lands (DIR/cells/c_<s>_<w>_<n>_<e>.json) and a cell already on disk is not fetched again, so a time-out or a
cancelled job loses at most the cell in flight, and a re-run seeded with an earlier run's cells only fetches what
is missing. `--shard i/n` takes every n-th cell. Merge assigns each course to a state by the Census 1:500k state
outlines (point in polygon; the nearest outline within 3 km for coastal points; courses outside every outline, in
Canada or Mexico, are dropped).

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
CELL_TIMEOUT_S = 90           # Overpass [timeout:] per cell; the client gives up 30 s later
MIN_CELL_DEG = 0.25           # a cell no mirror answers is split in four until this size
MIRROR_REST_S = 900           # a mirror that failed 3 times in a row is skipped this long
OSM_TYPE = {"w": "way", "r": "relation", "n": "node"}
GOLF_KINDS = ("hole", "green", "tee", "fairway", "pin")
FIELDS = ["name", "city", "state", "lat", "lon", "osm", "holes", "osm_holes", "greens", "tees", "fairways", "pins",
          "outline", "card", "tier", "closed"]
# state outlines for assigning a course to a state (Census 1:500k cartographic boundaries; a coarse GeoJSON as a
# fallback). Downloaded by the merge job, not committed.
STATE_SHAPES = ["https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_500k.zip",
                "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"]


def log(*a):
    print(*a, flush=True, file=sys.stderr)


# ------------------------------------------------------------------------------------------------ fetch (Actions)
def cell_deg(st):
    return 2.0 if st == "AK" else 1.0


def state_cells(st):
    """Grid cells (s, w, n, e), aligned to whole multiples of the cell size, that touch the state's bbox."""
    s, w, n, e = STATE_BBOX[st]
    d = cell_deg(st)
    out = []
    la = math.floor(s / d) * d
    while la < n:
        lo = math.floor(w / d) * d
        while lo < e:
            out.append((round(la, 4), round(lo, 4), round(la + d, 4), round(lo + d, 4)))
            lo += d
        la += d
    return out


def cells_for(states):
    seen, out = set(), []
    for st in states:
        for c in state_cells(st):
            if c not in seen:
                seen.add(c)
                out.append(c)
    return sorted(out)


def cell_name(t):
    return "c_%.4f_%.4f_%.4f_%.4f.json" % t


def cell_query(t, timeout=CELL_TIMEOUT_S):
    """Bbox-only (no area filter: the state-area test cost 30-60 s a tile on overpass-api.de in the pilot run)."""
    b = "(%.4f,%.4f,%.4f,%.4f)" % t
    return f"""[out:json][timeout:{timeout}][maxsize:536870912];
(way["leisure"="golf_course"]{b}; relation["leisure"="golf_course"]{b}; node["leisure"="golf_course"]["name"]{b};)->.c;
.c out tags center;
.c out ids bb;
way["golf"~"^(hole|green|tee|fairway)$"]{b};
out tags center;
node["golf"~"^(green|tee|pin)$"]{b};
out body;
node["place"~"^(city|town|village)$"]{b};
out body;"""


def _post(url, q, timeout):
    req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class Mirrors:
    """Mirror order for one job: start at a job-specific offset; a mirror that fails goes to the back, and one that
    failed 3 times in a row rests MIRROR_REST_S (the pilot: two of four mirrors timed out on nearly every tile)."""

    def __init__(self, offset=0, post=_post, now=time.time, sleep=time.sleep):
        self.order = OVERPASS[offset % len(OVERPASS):] + OVERPASS[:offset % len(OVERPASS)]
        self.post, self.now, self.sleep = post, now, sleep
        self.stats = {u: {"ok": 0, "fail": 0} for u in OVERPASS}
        self.streak = {u: 0 for u in OVERPASS}
        self.rest_until = {u: 0.0 for u in OVERPASS}

    def ask(self, q, timeout):
        """One try on each mirror not resting -> (json, mirror) or raises with the errors."""
        errs = []
        live = [u for u in self.order if self.rest_until[u] <= self.now()] or list(self.order)
        for url in live:
            try:
                js = self.post(url, q, timeout)
                bad = overpass_remark_problem(js)
                if bad:
                    raise RuntimeError("remark: " + bad)
                self.stats[url]["ok"] += 1
                self.streak[url] = 0
                return js, url
            except Exception as e:                                  # noqa: BLE001
                self.stats[url]["fail"] += 1
                self.streak[url] += 1
                if self.streak[url] >= 3:
                    self.rest_until[url] = self.now() + MIRROR_REST_S
                    self.streak[url] = 0
                errs.append(f"{url.split('/')[2]}: {e!r}"[:200])
                self.order.remove(url)
                self.order.append(url)
                self.sleep(2)
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
        rows.append(slim_row(e["type"][0], e["id"], c["lat"], c["lon"], t, bbs.get((e["type"][0], e["id"]))))
    return rows


KEEP_TAGS = ("name", "leisure", "golf", "ref", "holes", "addr:city", "addr:state", "place", "disused", "abandoned",
             "disused:leisure", "abandoned:leisure")


def slim_row(t, oid, lat, lon, tags, bb=None):
    """One compact element row (the cell-file format both the Overpass and the Geofabrik paths write)."""
    row = {"t": t, "id": oid, "lat": round(lat, 6), "lon": round(lon, 6),
           "g": {k: tags[k] for k in KEEP_TAGS if k in tags}}
    if bb:
        row["bb"] = bb
    return row


def split4(t):
    s, w, n, e = t
    ms, mw = round((s + n) / 2, 4), round((w + e) / 2, 4)
    return [(s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e)]


def fetch_cell(t, d, mirrors, deadline, now=time.time):
    """Fetch one cell (splitting it when no mirror answers) -> list of (sub)cells that still failed."""
    path = os.path.join(d, cell_name(t))
    if os.path.exists(path):
        return []
    if now() > deadline:
        return [t]
    t0 = now()
    try:
        if has_parts(t, d):             # split on an earlier pass: asking for the whole cell again only times out
            raise RuntimeError("split earlier, parts on disk")
        js, url = mirrors.ask(cell_query(t), CELL_TIMEOUT_S + 30)
    except Exception as e:                                          # noqa: BLE001
        log(f"  cell {t} failed on every mirror ({e})"[:500])
        if (t[2] - t[0]) / 2 < MIN_CELL_DEG:
            return [t]
        bad = []
        for sub in split4(t):
            bad += fetch_cell(sub, d, mirrors, deadline, now)
        if not bad:                     # the parent is covered by its four quarters: record that
            with open(path, "w") as fh:
                json.dump({"cell": list(t), "split": [list(x) for x in split4(t)], "elements": []}, fh)
        return bad
    rows = slim_elements(js)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump({"cell": list(t), "fetched": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "mirror": url,
                   "osm_base": (js.get("osm3s") or {}).get("timestamp_osm_base"), "elements": rows},
                  fh, separators=(",", ":"))
    os.replace(tmp, path)               # a half-written cell never looks fetched
    log(f"  {cell_name(t)} {len(rows)} el {now() - t0:.0f}s {url.split('/')[2]}")
    return []


def has_parts(t, d):
    """True when some smaller cell inside t is on disk (t failed and was split on an earlier pass)."""
    for f in os.listdir(d):
        if not (f.startswith("c_") and f.endswith(".json")):
            continue
        try:
            s, w, n, e = (float(x) for x in f[2:-5].split("_"))
        except ValueError:
            continue
        if (s, w, n, e) != tuple(t) and t[0] <= s and n <= t[2] and t[1] <= w and e <= t[3]:
            return True
    return False


def shard_cells(states, shard=0, n_shards=1):
    """This job's cells: every n-th cell of the sorted list (neighbouring dense cells land on different jobs)."""
    return cells_for(states)[shard::n_shards]


def fetch(states, out, shard=0, n_shards=1, budget_min=None, offset=None, now=time.time, mirrors=None,
          sleep=time.sleep):
    """Fetch every cell of this shard not already on disk (out/cells/); returns the cells still missing."""
    budget = float(budget_min if budget_min is not None else os.environ.get("NATIDX_BUDGET_MIN", "100")) * 60
    deadline = now() + budget
    mirrors = mirrors or Mirrors(int(offset if offset is not None else shard))
    d = os.path.join(out, "cells")
    os.makedirs(d, exist_ok=True)
    mine = shard_cells(states, shard, n_shards)
    bad = []
    for pass_ in (1, 2, 3):
        todo = [t for t in mine if not os.path.exists(os.path.join(d, cell_name(t)))]
        log(f"pass {pass_}: {len(todo)} of {len(mine)} cells to fetch")
        bad = []
        for i, t in enumerate(todo):
            bad += fetch_cell(t, d, mirrors, deadline, now)
            if i % 50 == 49:
                log(f"  {i + 1}/{len(todo)} done, {len(bad)} failed, {(deadline - now()) / 60:.0f} min left")
            sleep(0.5)
        if not bad or now() > deadline:
            break
        log(f"{len(bad)} cells failed; pass {pass_ + 1} after 60 s")
        sleep(60)
    log("mirrors:", json.dumps(mirrors.stats))
    left = [t for t in mine if not os.path.exists(os.path.join(d, cell_name(t)))]
    log(f"shard {shard}/{n_shards}: {len(mine) - len(left)} of {len(mine)} cells fetched; missing {len(left)}")
    return left


def load_cells(raw, states=None):
    """-> (elements deduplicated by OSM id over every cell and state file on disk, set of cells present). A
    Geofabrik state file (s_<ST>.json) adds its state to `states` (a set, when given), not cells: its border cells
    hold only that state's side."""
    seen, els, have = set(), [], set()
    paths = sorted(glob.glob(os.path.join(raw, "**", "s_*.json"), recursive=True)) + \
        sorted(glob.glob(os.path.join(raw, "**", "c_*.json"), recursive=True))
    for p in paths:
        try:
            js = json.load(open(p))
        except Exception:                                           # noqa: BLE001
            continue
        if "state" in js:
            if states is not None:
                states.add(js["state"])
        else:
            have.add(tuple(js["cell"]))
        for e in js.get("elements", []):
            k = (e["t"], e["id"])
            if k in seen:
                continue
            seen.add(k)
            els.append(e)
    return els, have


# ------------------------------------------------------------------------------------------------ Geofabrik
# The same elements from Geofabrik's daily per-state OSM extracts instead of Overpass: one download per state
# (about 10 GB for the whole US), `osmium tags-filter` keeps the golf / place objects plus the nodes and member
# ways they reference, and osm_xml_rows turns that into cell-file rows. No public Overpass mirror in the loop.
GEOFABRIK = "https://download.geofabrik.de/north-america/us/{}-latest.osm.pbf"
TAGS_FILTER = ["nwr/leisure=golf_course", "w/golf=hole,green,tee,fairway", "n/golf=green,tee,pin",
               "n/place=city,town,village"]
# approximate extract sizes (MB, late 2025) to deal states over jobs by download size
GEOFABRIK_MB = {
    "AL": 110, "AK": 80, "AZ": 230, "AR": 90, "CA": 1200, "CO": 260, "CT": 60, "DE": 20, "DC": 20, "FL": 560,
    "GA": 280, "HI": 30, "ID": 110, "IL": 300, "IN": 160, "IA": 120, "KS": 100, "KY": 110, "LA": 130, "ME": 80,
    "MD": 150, "MA": 180, "MI": 270, "MN": 220, "MS": 80, "MO": 160, "MT": 120, "NE": 70, "NV": 100, "NH": 50,
    "NJ": 180, "NM": 120, "NY": 450, "NC": 290, "ND": 60, "OH": 260, "OK": 140, "OR": 220, "PA": 330, "RI": 20,
    "SC": 140, "SD": 50, "TN": 140, "TX": 700, "UT": 130, "VT": 30, "VA": 220, "WA": 280, "WV": 60, "WI": 210,
    "WY": 50}


def geofabrik_url(st):
    return GEOFABRIK.format(_STATE_NAMES[st].lower().replace(" ", "-"))


def shard_states(states, shard=0, n_shards=1):
    """This job's states: largest extract first onto the job with the least so far (balanced by download size)."""
    load, out = [0.0] * n_shards, [[] for _ in range(n_shards)]
    for st in sorted(states, key=lambda s: (-GEOFABRIK_MB.get(s, 100), s)):
        i = min(range(n_shards), key=lambda k: (load[k], k))
        load[i] += GEOFABRIK_MB.get(st, 100)
        out[i].append(st)
    return out[shard]


def _download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(path + ".part", "wb") as fh:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            fh.write(b)
    os.replace(path + ".part", path)


def _tags_filter(pbf, osm):
    import subprocess
    subprocess.run(["osmium", "tags-filter", pbf, *TAGS_FILTER, "-o", osm, "-f", "osm", "--overwrite"],
                   check=True)


def osm_xml_rows(path):
    """An OSM XML file (osmium tags-filter output: tagged objects plus referenced nodes / member ways) -> the rows
    the Overpass cell query returns: courses (ways / relations with bb; nodes only when named), golf=hole / green /
    tee / fairway ways, golf=green / tee / pin nodes, city / town / village nodes; centre = bbox centre."""
    import xml.etree.ElementTree as ET
    loc, wbb, rows = {}, {}, []

    def tags_of(el):
        return {t.get("k"): t.get("v") for t in el.findall("tag")}

    def union(bbs):
        bbs = [b for b in bbs if b]
        if not bbs:
            return None
        return [min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs), max(b[3] for b in bbs)]

    def add(t, oid, tags, bb=None, lat=None, lon=None):
        if lat is None:
            lat, lon = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        rows.append(slim_row(t, oid, lat, lon, tags, bb))
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "node":
            oid, lat, lon = int(el.get("id")), float(el.get("lat")), float(el.get("lon"))
            loc[oid] = (lat, lon)
            tg = tags_of(el)
            if (tg.get("leisure") == "golf_course" and tg.get("name")) or tg.get("golf") in ("green", "tee", "pin") \
                    or tg.get("place") in ("city", "town", "village"):
                add("n", oid, tg, lat=lat, lon=lon)
            el.clear()
        elif el.tag == "way":
            oid = int(el.get("id"))
            pts = [loc[int(n.get("ref"))] for n in el.findall("nd") if int(n.get("ref")) in loc]
            bb = union([[p[0], p[1], p[0], p[1]] for p in pts])
            wbb[oid] = bb
            tg = tags_of(el)
            if bb and tg.get("leisure") == "golf_course":
                add("w", oid, tg, bb)
            elif bb and tg.get("golf") in ("hole", "green", "tee", "fairway"):
                c = [(bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2]
                add("w", oid, tg, lat=c[0], lon=c[1])
            el.clear()
        elif el.tag == "relation":
            tg = tags_of(el)
            if tg.get("leisure") == "golf_course":
                bb = union([wbb.get(int(m.get("ref"))) if m.get("type") == "way" else
                            ([*loc[int(m.get("ref"))], *loc[int(m.get("ref"))]] if int(m.get("ref")) in loc else None)
                            for m in el.findall("member") if m.get("type") in ("way", "node")])
                if bb:
                    add("r", int(el.get("id")), tg, bb)
            el.clear()
    return rows


def geofabrik(states, out, shard=0, n_shards=1, download=_download, tags_filter=_tags_filter, sleep=time.sleep,
              work=None):
    """Write out/cells/s_<ST>.json for each of this job's states not on disk yet -> states that failed."""
    d = os.path.join(out, "cells")
    os.makedirs(d, exist_ok=True)
    work = work or os.path.join(out, "_gf")
    os.makedirs(work, exist_ok=True)
    mine = shard_states(states, shard, n_shards)
    log(f"geofabrik shard {shard}/{n_shards}: {' '.join(mine)}")
    failed = []
    for st in mine:
        path = os.path.join(d, f"s_{st}.json")
        if os.path.exists(path):
            continue
        pbf, osm = os.path.join(work, st + ".osm.pbf"), os.path.join(work, st + ".osm")
        t0 = time.time()
        try:
            for k in range(3):
                try:
                    download(geofabrik_url(st), pbf)
                    break
                except Exception as e:                              # noqa: BLE001
                    log(f"  {st}: download try {k + 1} failed: {e!r}"[:300])
                    if k == 2:
                        raise
                    sleep(30 * (k + 1))
            mb = os.path.getsize(pbf) / 1e6
            tags_filter(pbf, osm)
            rows = osm_xml_rows(osm)
            with open(path + ".tmp", "w") as fh:
                json.dump({"state": st, "source": "geofabrik", "url": geofabrik_url(st), "cells": state_cells(st),
                           "fetched": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "elements": rows},
                          fh, separators=(",", ":"))
            os.replace(path + ".tmp", path)
            log(f"  {st}: {mb:.0f} MB, {len(rows)} el, {time.time() - t0:.0f}s")
        except Exception as e:                                      # noqa: BLE001
            log(f"  {st}: failed: {e!r}"[:300])
            failed.append(st)
        finally:
            for f in (pbf, pbf + ".part", osm):
                if os.path.exists(f):
                    os.remove(f)
    try:
        os.rmdir(work)
    except OSError:
        pass
    log(f"geofabrik shard {shard}/{n_shards}: {len(mine) - len(failed)} of {len(mine)} states; failed {failed}")
    return failed


# ------------------------------------------------------------------------------------------------ state outlines
def load_state_shapes(path=None):
    """{state: prepared shapely geometry}. path: a Census cb_*_state_*.zip (pyshp) or a GeoJSON FeatureCollection;
    none given -> download STATE_SHAPES in order."""
    from shapely.geometry import shape
    from shapely.prepared import prep
    names = {v.lower(): k for k, v in _STATE_NAMES.items()}
    paths = [path] if path else []
    if not paths:
        import tempfile
        for url in STATE_SHAPES:
            try:
                p = os.path.join(tempfile.gettempdir(), os.path.basename(url))
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as r, open(p, "wb") as fh:
                    fh.write(r.read())
                paths.append(p)
                break
            except Exception as e:                                  # noqa: BLE001
                log("state shapes:", url, repr(e)[:200])
    for p in paths:
        out = {}
        try:
            if p.endswith(".zip"):
                import shapefile                                    # pyshp
                with shapefile.Reader(p) as rd:
                    for sr in rd.iterShapeRecords():
                        st = sr.record.as_dict().get("STUSPS")
                        if st in STATE_BBOX:
                            out[st] = shape(sr.shape.__geo_interface__)
            else:
                for f in json.load(open(p))["features"]:
                    st = names.get(str(f["properties"].get("name", "")).lower())
                    if st:
                        out[st] = shape(f["geometry"])
        except Exception as e:                                      # noqa: BLE001
            log("state shapes unreadable:", p, repr(e)[:200])
            continue
        if len(out) >= 51:
            log("state shapes:", p, len(out))
            res = {k: (prep(g), g) for k, g in out.items()}
            res["_tol_km"] = 3.0 if p.endswith(".zip") else 12.0   # the GeoJSON fallback is ~10 km coarse at coasts
            return res
    raise RuntimeError("no state outlines")


_STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}


def state_locator(shapes):
    """(lat, lon, addr_state) -> state or None (outside the US). Inside one outline -> that state; else (coast,
    generalised border) the nearest outline within 3 km, preferring the course's addr:state."""
    from shapely.geometry import Point

    def find(lat, lon, addr=None):
        pt = Point(lon, lat)
        cands = [st for st, (s, w, n, e) in STATE_BBOX.items() if s - 0.1 <= lat <= n + 0.1 and w - 0.1 <= lon <= e + 0.1]
        inside = [st for st in cands if st in shapes and shapes[st][0].contains(pt)]
        if len(inside) == 1:
            return inside[0]
        if addr and addr.upper() in (inside or cands):
            return addr.upper()
        if inside:
            return inside[0]
        near = sorted((shapes[st][1].distance(pt), st) for st in cands if st in shapes)
        if near and near[0][0] * 111.0 <= shapes.get("_tol_km", 3.0):
            return near[0][1]
        return None
    return find
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


def build_rows(els, locate):
    """Course rows from deduplicated elements; locate(lat, lon, addr_state) -> state or None (dropped)."""
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
        st = locate(c["lat"], c["lon"], g.get("addr:state"))
        if not st:
            continue
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


def merge(raw, oga_dirs=None, shapes=None):
    """Cells on disk -> rows per state. A state is used when all its cells are on disk (complete) or at least half
    (partial_states); otherwise it keeps its rows from the committed index if those were complete, else missing."""
    rows, missing, partial, coverage = [], [], [], {}
    old, old_cov = {}, {}
    try:                                    # a state this run did not fetch keeps its rows from the committed index
        with gzip.open(OUT_GZ, "rt") as fh:
            o = json.load(fh)
        for row in o["rows"]:
            r = dict(zip(o["fields"], row))
            old.setdefault(r["state"], []).append(r)
        with open(OUT_READY) as fh:
            old_cov = json.load(fh).get("coverage") or {}
    except Exception:                                               # noqa: BLE001
        pass
    gf = set()
    els, have = load_cells(raw, gf)
    log(f"{len(have)} cells, {len(gf)} Geofabrik states, {len(els)} elements")
    locate = state_locator(shapes if shapes is not None else load_state_shapes())
    new = {}
    for r in build_rows(els, locate):
        new.setdefault(r["state"], []).append(r)
    for st in STATES:
        cs = state_cells(st)
        n_have = sum(1 for c in cs if c in have)
        cov = {"cells": len(cs), "have": n_have, "complete": n_have == len(cs)}
        if st in gf:
            rows += new.get(st, [])
            coverage[st] = dict(cov, have=len(cs), complete=True, source="geofabrik")
        elif cov["complete"] or n_have * 2 >= len(cs):
            rows += new.get(st, [])
            coverage[st] = dict(cov, source="this run")
            if not cov["complete"]:
                partial.append(st)
        elif old.get(st) and old_cov.get(st, {}).get("complete"):
            rows += [dict({f: 0 for f in FIELDS}, **dict(r, card="" if r.get("card") == "library"
                                                          else r.get("card", ""))) for r in old[st]]
            coverage[st] = dict(old_cov[st], source="committed index")
        else:
            missing.append(st)
            coverage[st] = dict(cov, source="none")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "geofabrik", "oga", "merge", "readme", "cells"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--out", default="/tmp/natidx")
    ap.add_argument("--oga", default="", help="comma-separated OpenGolfAPI listing dirs, first wins per state")
    ap.add_argument("--shard", default="0/1", help="i/n: this job fetches every n-th cell from the i-th")
    ap.add_argument("--shapes", default=None, help="state outlines (Census zip or GeoJSON); default: download")
    a = ap.parse_args()
    sts = [s.upper() for s in a.args] or STATES
    i, n = (int(x) for x in a.shard.split("/"))
    if a.cmd == "fetch":
        left = fetch(sts, a.out, i, n)
        log("cells missing:", len(left))
    if a.cmd == "geofabrik":
        failed = geofabrik(sts, a.out, i, n)
        log("states failed:", " ".join(failed) or "none")
    if a.cmd == "oga":
        oga(sts, a.out)
    if a.cmd == "merge":
        merge(a.args[0] if a.args else a.out, [d for d in a.oga.split(",") if d],
              load_state_shapes(a.shapes) if a.shapes else None)
        write_readme()
    if a.cmd == "readme":
        write_readme()
    if a.cmd == "cells":
        print(len(cells_for(sts)))


if __name__ == "__main__":
    main()
