"""National course index: every named US golf course on OpenStreetMap, with how completely OSM maps it.

Runs on GitHub Actions (.github/workflows/national_index.yml; the sandbox cannot reach Overpass):

  python course_data/library/national_index.py fetch IA MO ... --out DIR   one Overpass query per state -> DIR/<ST>.json
  python course_data/library/national_index.py oga IA MO ... --out DIR     OpenGolfAPI state listings (best effort)
  python course_data/library/national_index.py merge DIR                   -> us_courses.json.gz + us_readiness.json

Per course (schema us_courses/1, columnar: "fields" + "rows"):
  name, city, state, lat, lon, osm ("way/123"), holes (the course's `holes` tag, else inferred),
  osm_holes (golf=hole ways: distinct refs, else count), greens, tees (golf=green / golf=tee features whose centre is
  inside the course outline's bbox; a feature in two bboxes goes to the smaller course), card ("" unknown,
  "library" a library build found a web card, "oga" OpenGolfAPI lists it with a course par (its detail call
  usually returns the card), "oga?" listed without a par),
  tier (readiness, below), closed (1 when the name / tags say former / disused / abandoned).

Readiness tiers (what the course_page pipeline does with the course, course_data/library/README.md):
  A  complete OSM holes (a golf=hole per hole, a green per hole, tees on at least as many holes) and a known card:
     the case the pipeline handles best (auto-OK candidates)
  B  complete OSM holes, no known card (the page solves from OSM tees; a typed card moves it to A)
  C  partial OSM golf mapping (some holes / greens): routed by routing v2, often short of holes
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
UA = "my_golf_data_science national course index (github.com/willbhedges/my_golf_data_science)"
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter"]
OPENGOLFAPI = "https://api.opengolfapi.org"
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
          "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
          "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
OSM_TYPE = {"w": "way", "r": "relation", "n": "node"}
FIELDS = ["name", "city", "state", "lat", "lon", "osm", "holes", "osm_holes", "greens", "tees", "card", "tier",
          "closed"]


def log(*a):
    print(*a, flush=True, file=sys.stderr)


# ------------------------------------------------------------------------------------------------ fetch (Actions)
def overpass(q, tries=4, timeout=700):
    last = None
    for attempt in range(tries):
        for url in OVERPASS:
            try:
                req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(),
                                             headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    js = json.loads(r.read().decode())
                rem = (js.get("remark") or "")
                if "runtime error" in rem or "timed out" in rem:
                    raise RuntimeError("remark: " + rem[:200])
                return js
            except Exception as e:                                  # noqa: BLE001
                last = f"{url}: {e!r}"[:300]
                log("  overpass failed:", last)
        time.sleep(min(30 * (attempt + 1), 120))
    raise RuntimeError(f"all Overpass endpoints failed: {last}")


def state_query(st):
    return f"""[out:json][timeout:650][maxsize:1073741824];
area["ISO3166-2"="US-{st}"]["admin_level"="4"]->.st;
(way["leisure"="golf_course"](area.st); relation["leisure"="golf_course"](area.st););
out tags center bb;
node["leisure"="golf_course"]["name"](area.st);
out body;
way["golf"~"^(hole|green|tee)$"](area.st);
out tags center;
node["golf"~"^(green|tee)$"](area.st);
out body;
node["place"~"^(city|town|village)$"](area.st);
out body;"""


def fetch(states, out):
    os.makedirs(out, exist_ok=True)
    bad = []
    t_start = time.time()
    budget = float(os.environ.get("NATIDX_BUDGET_MIN", "100")) * 60   # the job must still upload what it has
    for st in states:
        path = os.path.join(out, f"{st}.json")
        if os.path.exists(path):
            continue
        if time.time() - t_start > budget:
            log(st, "skipped: time budget used (re-run this state)")
            bad.append(st)
            continue
        t0 = time.time()
        try:
            js = overpass(state_query(st))
        except Exception as e:                                      # noqa: BLE001
            log(st, "FAILED:", e)
            bad.append(st)
            continue
        els = js.get("elements", [])
        slim = []
        for e in els:
            t = e.get("tags") or {}
            c = e.get("center") or ({"lat": e["lat"], "lon": e["lon"]} if "lat" in e else None)
            if not c:
                continue
            keep = {k: t[k] for k in ("name", "leisure", "golf", "ref", "holes", "addr:city", "addr:state", "place",
                                      "disused", "abandoned", "disused:leisure", "abandoned:leisure", "operator",
                                      "website", "access") if k in t}
            row = {"t": e["type"][0], "id": e["id"], "lat": round(c["lat"], 6), "lon": round(c["lon"], 6), "g": keep}
            if e.get("bounds"):
                b = e["bounds"]
                row["bb"] = [b["minlat"], b["minlon"], b["maxlat"], b["maxlon"]]
            slim.append(row)
        with open(path, "w") as fh:
            json.dump({"state": st, "fetched": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "elements": slim}, fh,
                      separators=(",", ":"))
        log(st, len(slim), "elements", f"{time.time() - t0:.0f}s")
        time.sleep(5)
    if bad:
        log("failed states:", " ".join(bad))
    return bad


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
            if page == 0:
                log(st, "oga keys:", list(js)[:12] if isinstance(js, dict) else type(js).__name__,
                    "first:", json.dumps((cs or [None])[0])[:400])
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


def build_state(js):
    els = js["elements"]
    courses = [e for e in els if e["g"].get("leisure") == "golf_course" and e["g"].get("name")]
    feats = [e for e in els if e["g"].get("golf") in ("hole", "green", "tee")]
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
    acc = {id(c): {"hole": 0, "refs": set(), "green": 0, "tee": 0, "tee_refs": set()} for c in withbb}
    for f in feats:
        cand = cell.get((int(math.floor(f["lat"] * 10)), int(math.floor(f["lon"] * 10))), [])
        for i in sorted(cand):
            b = withbb[i]["bb"]
            pad = 0.0005
            if b[0] - pad <= f["lat"] <= b[2] + pad and b[1] - pad <= f["lon"] <= b[3] + pad:
                a = acc[id(withbb[i])]
                g = f["g"]["golf"]
                a[g] += 1
                if g == "hole" and f["g"].get("ref"):
                    a["refs"].add(f["g"]["ref"].strip())
                break
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

    rows = []
    seen = set()
    for c in courses:
        g = c["g"]
        a = acc.get(id(c), {"hole": 0, "refs": set(), "green": 0, "tee": 0})
        refs = {r for r in a["refs"] if re.fullmatch(r"\d{1,2}", r)}
        osm_holes = max(len(refs), 0) if refs else a["hole"]
        try:
            holes = int(re.match(r"\d+", g.get("holes", "")).group(0))
        except Exception:                                           # noqa: BLE001
            holes = 0
        if not holes or holes > 72:
            holes = 18 if osm_holes > 9 else (9 if osm_holes > 0 else 0)
        name = g["name"].strip()
        closed = int(bool(re.search(r"\b(former|closed|abandoned|defunct)\b", name, re.I)
                          or g.get("disused") or g.get("abandoned") or g.get("disused:leisure")
                          or g.get("abandoned:leisure")))
        key = (norm(name), round(c["lat"], 2), round(c["lon"], 2))
        if key in seen:
            continue
        seen.add(key)
        rows.append(dict(name=name, city=g.get("addr:city") or city_of(c["lat"], c["lon"]) or "",
                         state=js["state"], lat=round(c["lat"], 5), lon=round(c["lon"], 5),
                         osm=OSM_TYPE[c["t"]] + "/" + str(c["id"]),
                         holes=holes, osm_holes=osm_holes, greens=a["green"], tees=a["tee"], card="", closed=closed))
    return rows


def tier(r):
    h = r["holes"] or 18
    complete = r["osm_holes"] >= h and r["greens"] >= h and r["tees"] >= h
    if complete:
        return "A" if r["card"] in ("library", "oga") else "B"
    if r["osm_holes"] or r["greens"] or r["tees"]:
        return "C"
    return "D"


def attach_cards(rows, oga_dir):
    """card: library builds that found a web card, then OpenGolfAPI listings (name + state, within 5 km)."""
    by = {}
    for r in rows:
        by.setdefault((r["state"], norm(r["name"])), []).append(r)
    try:
        lib = json.load(open(LIB_INDEX))["courses"]
    except Exception:                                               # noqa: BLE001
        lib = []
    for c in lib:
        has_card = any(t.get("yards") for t in c.get("tee_sets") or []) and c.get("status") != "failed"
        for r in by.get((c.get("state"), norm(c.get("name"))), []):
            if has_card:
                r["card"] = "library"
            r["slug"] = c.get("slug")
    n_oga = 0
    grid = {}
    for r in rows:
        grid.setdefault((r["state"], int(r["lat"] * 20), int(r["lon"] * 20)), []).append(r)
    for path in sorted(glob.glob(os.path.join(oga_dir or "/nonexistent", "oga_*.json"))):
        js = json.load(open(path))
        for c in js.get("courses") or []:
            nm = c.get("course_name") or c.get("name") or c.get("club_name")
            st = (c.get("state") or js["state"] or "").upper()[:2]
            cands = by.get((st, norm(nm)), [])
            lat, lon = c.get("latitude") or c.get("lat"), c.get("longitude") or c.get("lon") or c.get("lng")
            if not cands and lat and lon:          # fuzzy: an OSM course within 1.5 km whose name shares a stem
                n1 = norm(nm)
                try:
                    la, lo = float(lat), float(lon)
                    cell = grid.get((st, int(la * 20), int(lo * 20)), [])
                    near = [r for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                            for r in grid.get((st, int(la * 20) + dx, int(lo * 20) + dy), [])] if n1 else cell
                    near = [r for r in near if dist_km(r["lat"], r["lon"], la, lo) <= 1.5]
                    n2s = [(r, norm(r["name"])) for r in near]
                    cands = [r for r, n2 in n2s if n2 and (n1 in n2 or n2 in n1 or n1[:6] == n2[:6])]
                except (TypeError, ValueError):
                    cands = []
            for r in cands:
                if lat and lon:
                    try:
                        if dist_km(r["lat"], r["lon"], float(lat), float(lon)) > 5:
                            continue
                    except (TypeError, ValueError):
                        pass
                if r["card"] == "library":
                    continue
                rich = bool(c.get("par")) or any(c.get(k) for k in ("tees", "holes_data", "scorecard"))
                r["card"] = "oga" if rich else (r["card"] or "oga?")
                n_oga += 1
    log("opengolfapi matches:", n_oga)


def merge(raw, oga_dir=None):
    rows, missing = [], []
    old = {}
    try:                                    # a state this run did not fetch keeps its rows from the committed index
        with gzip.open(OUT_GZ, "rt") as fh:
            o = json.load(fh)
        for row in o["rows"]:
            r = dict(zip(o["fields"], row))
            old.setdefault(r["state"], []).append(r)
    except Exception:                                               # noqa: BLE001
        pass
    for st in STATES:
        p = os.path.join(raw, f"{st}.json")
        if not os.path.exists(p):
            if old.get(st):
                rows += [dict(r, card="" if r.get("card") == "library" else r.get("card", "")) for r in old[st]]
            else:
                missing.append(st)
            continue
        rows += build_state(json.load(open(p)))
    attach_cards(rows, oga_dir)
    for r in rows:
        r["tier"] = tier(r)
    rows.sort(key=lambda r: (r["state"], r["name"].lower()))
    built = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    doc = {"schema": "us_courses/1", "doc": "course_data/library/README.md", "built": built,
           "source": "OpenStreetMap contributors (ODbL) via Overpass; OpenGolfAPI (ODbL) where it lists the course",
           "missing_states": missing, "fields": FIELDS, "rows": [[r[f] for f in FIELDS] for r in rows]}
    with gzip.open(OUT_GZ, "wt", compresslevel=9) as fh:
        json.dump(doc, fh, separators=(",", ":"), ensure_ascii=False)
    write_readiness(rows, built, missing)
    log("rows", len(rows), "missing states", missing, "gz bytes", os.path.getsize(OUT_GZ))


def write_readiness(rows, built, missing):
    def summary(rs):
        open_ = [r for r in rs if not r["closed"]]
        t = {k: sum(1 for r in open_ if r["tier"] == k) for k in "ABCD"}
        n = len(open_)
        return dict(n=n, closed=len(rs) - n, tiers=t,
                    complete_osm_holes=t["A"] + t["B"],
                    pct_complete=round(100 * (t["A"] + t["B"]) / n, 1) if n else 0.0,
                    any_osm_golf=t["A"] + t["B"] + t["C"],
                    pct_any=round(100 * (t["A"] + t["B"] + t["C"]) / n, 1) if n else 0.0,
                    card_known=sum(1 for r in open_ if r["card"] in ("library", "oga")),
                    osm_holes_total=sum(r["osm_holes"] for r in open_))
    states = {}
    for r in rows:
        states.setdefault(r["state"], []).append(r)
    per = {st: summary(rs) for st, rs in sorted(states.items())}
    doc = {"schema": "us_readiness/1", "built": built, "missing_states": missing,
           "tiers": {"A": "complete OSM holes + greens + tees, card known (pipeline's best case)",
                     "B": "complete OSM holes + greens + tees, no card known",
                     "C": "partial OSM golf mapping (routing v2 fills holes)",
                     "D": "outline only on OSM"},
           "national": summary(rows),
           "states": per,
           "best_states": sorted(per, key=lambda s: -per[s]["pct_complete"])[:10]}
    with open(OUT_READY, "w") as fh:
        json.dump(doc, fh, indent=1)
    log(json.dumps(doc["national"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "oga", "merge"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--out", default="/tmp/natidx")
    ap.add_argument("--oga", default=None)
    a = ap.parse_args()
    if a.cmd == "fetch":
        bad = fetch([s.upper() for s in a.args] or STATES, a.out)
        sys.exit(0 if not bad else 0)
    if a.cmd == "oga":
        oga([s.upper() for s in a.args] or STATES, a.out)
    if a.cmd == "merge":
        merge(a.args[0] if a.args else a.out, a.oga)


if __name__ == "__main__":
    main()
