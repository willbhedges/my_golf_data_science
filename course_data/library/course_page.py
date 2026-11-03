"""One request, one page: any US course -> a checked wind and club-pick page (.github/workflows/course_page.yml).

Request (course_data/requests/course_page_<slug>.json, schema course_page/1):
  {"name": "Swope Memorial Golf Course", "city": "Kansas City", "state": "MO",
   "near": "lat,lon" | "address": "street, town, ST zip" | "osm": "way/123"   (optional disambiguation),
   "osm_supplement" / "no_osm_ok" / "website" / "scorecard" / "hole_method" ... (optional package-request data
                                              fixes, passed through by pkgreq),
   "agent_layers": "course_data/mapper/<slug>/" (optional: the mapper agent's layers, course_data/mapper/BRIEF.md;
                                              applied by platform/package.py after vision + OB),
   "tees": ["Blue", "White"]                 (optional tee sets of interest; default: the two longest sets),
   "days": ["2026-11-07", "2026-11-08"]       (optional event days; default the next Saturday + Sunday),
   "tee_hour": 9.0, "slug": "...", "group": "library" | "gate", "compute": {"draws": 48, "swings": 2500},
   "rev": 1}
Batch: course_data/requests/course_batch_<name>.json {"requests": [paths], "rev": n} rebuilds the listed requests.
Review fixes: the output folder's review files (review.json, card_*.json, osm_supplement.geojson; review_fixes.py)
are read into the request (scorecard, tees, osm_supplement, tee / yardage / par overrides) unless the request has
its own value for a key or says "library_fixes": false.

Stages (each a subcommand, run by the workflow; README.md in this folder has the whole picture):
  plan REQ...          -> job matrices (skips any target whose config says "hand_checked": true, and every
                          slug that is a tournament page in course_data/courses/)
  pkgreq REQ           -> <out>/package_request.json (platform/package.py request: name, town, state, tees)
  configure REQ        -> bases (two longest sets of interest), <out>/config.json (v2_course format), weather,
                          sharpest leaf-on NAIP year for display -> <out>/sharp.json
  prepare REQ [--imagery DIR]  -> v2_course prepare for each base, the hole images rendered from DIR
  compute REQ SLOT KIND PARTS  -> wind grids (base SLOT, its offsets) or the calm-day Bayesian decide
  native REQ           -> <out>/native.json: the golfer native-grass taps ("Native grass along this hole's landing
                          area?" Left / Right / Both / None, product/native_confirm.py via verify.native_for) when the
                          request has "agent_layers" and that folder has the mapper's frames.json + edits.json +
                          agent_zones.geojson ("native": false turns it off), else (no mapper layer) when the package
                          carries product/native_auto.py's per-side p (priors; cap NATIVE_AUTO_CAP = 2, the mapper
                          layer always wins); up to NATIVE_SPARE x native_confirm.CAP
                          candidates by value, the four answers' plans precomputed. Run in the package job (the DEM and
                          lidar canopy the planner reads are on disk there); finish keeps at most CAP whose planner
                          plan is the page's own calm-day pick (native_reconcile); app/build_library_play.py turns
                          them into check cards
  finish REQ PARTS     -> merge, page (data gzip-inlined; the page stage runs through v2_adaptive.py, which widens a
                          hole picture's crop to a wide aim's landing), picture checks + the wide-aim CHECK
                          (wide_aims.py: any printed tee-shot aim past +/-40 yds), native_reconcile, qa_page.js,
                          qa_report.md, status.json; publish_gate makes a page too wrong to publish "blocked" (hole
                          count not the card's, pars off by more than 2, a weak resolve far from `near`, holes out of
                          order by the green -> next-tee walks): the page
                          stays in the folder, the index keeps it off the course list. No card: the page labels the
                          package's "osm_back" set "Back tees (from the map)" and drops "on the card" (label_no_card)
  index                -> course_data/library/index.json
  regate [DIR...] [--apply]  -> publish_gate over the pages on disk; lists (or, --apply, writes) the blocked ones
A failed re-run of a course that already has a page keeps that page's status.json (status, page, reasons, the good
qa_report.md) and records the failure beside it as "last_attempt": {status, stage, error, when}; the index lists the
page with that last_attempt. A package whose imagery is not USDA NAIP (Alaska, Hawaii, outside the US: the package
falls back to 10 m Sentinel-2 and the hole pictures come out gray) stops at configure with status "unsupported".
Output folder: course_data/library/<slug>/ (group "library"), course_data/library/gate/<slug>/ (group "gate").
"""
import argparse
import base64
import datetime as dt
import glob
import gzip
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
VC_PY = os.path.join(CD, "courses", "v2_course.py")
# decide / wind run through library/v2_adaptive.py: v2_course.py unchanged, with the adaptive aim bound (+/-40 widened
# to 60 / 80 yds where the best aim sits on it, guarded by lie and line of play; library QA: picks pinned at +/-40)
VC_ADAPT_PY = os.path.join(HERE, "v2_adaptive.py")
TOURNAMENT = os.path.join(CD, "courses")
WHICH = ["auto", "auto_b"]
DEFAULT_DRAWS = 48
DEFAULT_SWINGS = 2500
MIN_SET_TOTAL = 5000
JPEG_Q = "66"
COLOURS = {"black": "#111", "blue": "#2a5bd7", "white": "#f2f2f2", "gold": "#d4a017", "yellow": "#e8c547",
           "red": "#d22", "green": "#2a9d4a", "silver": "#b8bcc2", "grey": "#9aa0a6", "gray": "#9aa0a6",
           "orange": "#e07a3a", "purple": "#7b3fc4", "copper": "#b87333", "tips": "#111", "champ": "#111",
           "back": "#111", "middle": "#2a5bd7", "forward": "#d22", "teal": "#1f9e9a", "maroon": "#7a1f2b",
           "jade": "#3aa37a", "tan": "#c9a46b", "brown": "#7b4a2a", "pink": "#e88fb4", "platinum": "#cfd3d8"}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def rj(p, default=None):
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return default


def wj(p, d, **kw):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    json.dump(d, open(p, "w"), **({"indent": 1} | kw))


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def request(path):
    q = rj(os.path.join(ROOT, path) if not os.path.isabs(path) else path)
    if q is None:
        raise SystemExit(f"cannot read {path}")
    q.setdefault("group", "library")
    base = q.get("slug") or slugify(re.sub(r"\b(golf|course|club|links|country|gc|cc)\b", " ", q["name"], flags=re.I))
    q["slug"] = ("gate_" + base if q["group"] == "gate" and not base.startswith("gate_") else base)
    q["out"] = os.path.join("course_data", "library", *(["gate"] if q["group"] == "gate" else []), q["slug"])
    q["path"] = os.path.relpath(os.path.abspath(path), ROOT)
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import review_fixes
    return review_fixes.merge(q, out_dir(q), ROOT)


def out_dir(q, *p):
    return os.path.join(ROOT, q["out"], *p)


def v2env(q):
    return dict(os.environ, V2_COURSES_DIR=os.path.dirname(out_dir(q)), V2_JPEG_Q=JPEG_Q, PYTHONWARNINGS="ignore")


def vc(q, *args, check=True, **kw):
    cmd = [sys.executable, VC_PY, *args, "--slug", q["slug"]]
    log("$", " ".join(cmd))
    return subprocess.run(cmd, env=v2env(q), check=check, **kw)


def hand_checked(q):
    """True when the target must not be written: a hand-checked config there, or a tournament-page slug."""
    for c in (out_dir(q, "config.json"), os.path.join(TOURNAMENT, q["slug"], "config.json")):
        if (rj(c) or {}).get("hand_checked"):
            return True
    return os.path.isdir(os.path.join(TOURNAMENT, q["slug"])) or q["slug"] in ("spirit_hollow", "mozingo", "mozingo_lake")


# ------------------------------------------------------------------------------------------------ plan
def plan(paths):
    reqs, seen = [], set()
    for p in paths:
        p = p.strip()
        if not p or not os.path.exists(os.path.join(ROOT, p)):
            continue
        if os.path.basename(p).startswith("course_batch_"):
            reqs += rj(os.path.join(ROOT, p))["requests"]
        elif os.path.basename(p).startswith("course_page_"):
            reqs.append(p)
    courses, compute, skipped = [], [], []
    for p in reqs:
        if p in seen:
            continue
        seen.add(p)
        q = request(p)
        if hand_checked(q):
            skipped.append(q["slug"])
            log(f"SKIP {q['slug']}: hand-checked page (config hand_checked / tournament page); never overwritten")
            continue
        courses.append(dict(req=p, slug=q["slug"]))
        for slot in (0, 1):
            for kind in ("wind", "decide"):
                compute.append(dict(req=p, slug=q["slug"], slot=slot, kind=kind))
    return dict(courses=courses, compute=compute, skipped=skipped)


# ------------------------------------------------------------------------------------------------ package
def pkgreq(q):
    r = {"schema": "request/1", "kind": "package", "course": q["name"], "state": q["state"], "slug": q["slug"],
         "tees": (q.get("tees") or ["Black"])[0], "allow_substitute": True, "builder": "course-page",
         "requested": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
         "note": f"course-page workflow, from {q['path']} (only what a golfer types: name, town, state, tees)"}
    if q.get("city"):
        r["town"] = q["city"]
    # the package request's data fixes pass straight through (platform/package.py + fetch_package.py read them): a
    # course OSM maps badly is fixed in its course-page request, never by hand-editing package_request.json
    for k in ("near", "address", "osm", "typed_card", "yardages", "pars", "scorecard", "website", "opengolfapi_id",
              "osm_supplement", "boundary_ll", "no_osm_ok", "no_osm_course", "near_radius_m", "ignore_osm_holes",
              "hole_method", "routing", "naip_year", "tee_overrides", "yardage_overrides", "par_overrides",
              "green_overrides", "hole_renumber", "agent_layers", "native_auto"):
        if q.get(k) not in (None, "", [], {}):            # "routing": false passes too
            r[k] = q[k]
    if q.get("library_fixes"):
        r["note"] += "; review fixes from " + ", ".join(f"{q['out']}/{f}" for f in q["library_fixes"])
    wj(out_dir(q, "package_request.json"), r)
    print(q["slug"])


def is_combo(name):
    return bool(re.search(r"/|combo|hybrid|\bmix|-\s*\w+\s*$|&", name, re.I))


def choose_bases(pkg, want):
    """-> (bases [longest first, at most 2], extra sets, note). want = tee sets of interest (names or colours)."""
    sets = {s: v for s, v in (pkg.get("tee_sets") or {}).items() if v.get("total")}
    if not sets:
        return [pkg["tee_set"]], [], "no scorecard: the package's own tee set"
    def match(w):
        w0 = w.strip().lower()
        for s, v in sets.items():
            if s.lower() == w0 or (v.get("colour") or "").lower() == w0 or w0 in [a.lower() for a in v.get("aliases") or []]:
                return s
        part = [s for s in sets if "/" in s and w0 in [x.strip() for x in s.lower().split("/")]]
        if part:                                # "Black" -> "Black/Blue" (colbert_hills: else "Web" was substituted)
            return max(part, key=lambda s: sets[s]["total"])
        return None
    pool = sorted([s for s in sets if not is_combo(s) and sets[s]["total"] >= MIN_SET_TOTAL],
                  key=lambda s: -sets[s]["total"]) or sorted(sets, key=lambda s: -sets[s]["total"])
    # one name per length (a card often lists "Red (M)" and "Red (L)" with the same yardages)
    uniq = []
    for s in pool:
        if all(sets[s]["yards"] != sets[u]["yards"] for u in uniq):
            uniq.append(s)
    if want:
        got = [m for m in (match(w) for w in want) if m]
        missing = [w for w in want if not match(w)]
        pick = sorted(set(got), key=lambda s: -sets[s]["total"])
        note = "tee sets of interest" + (f" (not on the card: {', '.join(missing)})" if missing else "")
        if len(pick) == 1:                      # one set named: also solve the longest other set
            other = [s for s in uniq if s != pick[0] and sets[s]["yards"] != sets[pick[0]]["yards"]]
            if other:
                return [pick[0], other[0]], [], note + f" + the longest other set ({other[0]})"
        if pick:
            return pick[:2], pick[2:], note
    return uniq[:2], [], "the two longest sets on the card (combination sets skipped)"


def colour_of(name, v):
    for key in ((v.get("colour") or "").lower(), name.lower()):
        for c, css in COLOURS.items():
            if c in key:
                return css
    return "#888"


def next_weekend(today):
    d = today + dt.timedelta(days=1)
    while d.weekday() != 5:
        d += dt.timedelta(days=1)
    return [d.isoformat(), (d + dt.timedelta(days=1)).isoformat()]


def temps_from(weather):
    T = [r["temp_f"] for r in weather["hourly"] if 8 <= r["hour"] <= 16] or [r["temp_f"] for r in weather["hourly"]]
    lo, hi = min(T), max(T)
    a, b = 5 * math.floor(lo / 5), 5 * math.ceil(hi / 5)
    if b - a < 20:
        m = (a + b) / 2
        a, b = 5 * math.floor((m - 10) / 5), 5 * math.ceil((m + 10) / 5)
    mid = 5 * round((a + b) / 10)
    return sorted({a, mid, b})


def sharp_choice(pkg):
    """Sharpest leaf-on NAIP year among the package's scored candidates (finest gsd, then newest)."""
    im = pkg.get("imagery") or {}
    sel = im.get("selection") or {}
    cands = [c for c in sel.get("candidates") or [] if c.get("score") is not None and c.get("coverage", 1) >= 0.99
             and not c.get("greens_bare_n") and "leaf-off flight" not in (c.get("notes") or [])]
    if not cands:
        return None
    best = min(cands, key=lambda c: (float(c.get("gsd_m") or 1.0), -int(c["year"])))
    cur_gsd = float(im.get("resolution_m") or 1.0)
    if int(best["year"]) == int(im.get("year") or 0) or float(best.get("gsd_m") or 1.0) >= cur_gsd - 1e-6:
        return None
    return dict(year=int(best["year"]), gsd_m=best.get("gsd_m"), dates=best.get("dates"),
                reason=f"NAIP {best['year']} at {best.get('gsd_m')} m is sharper than the package's {im.get('year')} "
                       f"({cur_gsd} m): used for the hole pictures only")


def page_name(pkg, q):
    """The page's course name: the OSM course name, except on a multi-course facility whose split kept one course
    the OSM name does not name ("TPC Sawgrass" kept 'stadium'): then the request's name when it names that course
    ("TPC Sawgrass Stadium", "Troon North Monument"), else the OSM name + the kept course. A split that kept an
    unnamed group (largest / nearest the near point) uses the request's name when it says more than the OSM name."""
    name = (pkg.get("course") or {}).get("name") or q.get("name") or ""
    kept = None
    for w in pkg.get("warnings") or []:
        m = re.search(r"multi-course facility:.*?; kept '([^']+)'", w) or re.search(r"hole refs: kept the '([^']+)' holes", w)
        if m:
            kept = m.group(1).strip()
            break
    words = lambda t: set(re.findall(r"[a-z0-9]+", t.lower()))          # noqa: E731
    if not kept:
        # a split that kept a course by size or by the near point ("kept the largest group", "kept the course nearest
        # the request's near point") does not name it: the request's name when it names more than the facility
        # ("Sand Hollow Championship Course" on "Sand Hollow Resort", "Grand National Links Course" on "RTJ Grand
        # National Golf"), since the request names the course the user plays
        multi = any(re.search(r"multi-course facility:.*\bkept\b", w) for w in pkg.get("warnings") or [])
        generic = {"course", "golf", "club", "the", "resort", "gc", "cc", "country", "and", "at", "of"}
        rq = q.get("name") or ""
        if multi and rq and words(rq) - words(name) - generic:
            return rq
        return name
    key = words(kept) - {"course", "golf", "club", "the", "no", "links"}
    if not key or key <= words(name):
        # a resort named after its flagship ("Bandon Dunes Golf Resort", kept 'bandon dunes' of 3 courses): the OSM
        # name is the facility, so the request's name when it names the kept course and not the resort
        rq = words(q.get("name") or "")
        if "resort" in words(name) and "resort" not in rq and key and key <= rq:
            return q["name"]
        return name
    if q.get("name") and key <= words(q["name"]):
        return q["name"]
    return f"{name} {kept if kept != kept.lower() else kept.title()}"


def configure(q):
    import weather as W
    slug = q["slug"]
    src = os.path.join(CD, "packages", slug, "package.json")
    pkg = rj(src)
    if not pkg:
        raise SystemExit(f"no package built for {slug}")
    shutil.copy(src, out_dir(q, "package.json"))
    for f in ("qa.md", "coverage.json", "confirm.json"):
        if os.path.exists(os.path.join(CD, "packages", slug, f)):
            shutil.copy(os.path.join(CD, "packages", slug, f), out_dir(q, "package_" + f))
    raw = os.path.join(CD, "packages", slug, "raw")
    os.makedirs(out_dir(q, "raw"), exist_ok=True)
    for f in ("course.json", "summary.json", "scorecard_web.json", "osm.geojson"):
        if os.path.exists(os.path.join(raw, f)):
            shutil.copy(os.path.join(raw, f), out_dir(q, "raw", f))
    check_imagery(q, pkg)
    bases, extra, why = choose_bases(pkg, q.get("tees"))
    days = q.get("days") or next_weekend(dt.date.today())
    c = pkg["course"]
    lon, lat = c["center"]
    w = W.course_weather(lat, lon, days)
    wj(out_dir(q, "weather.json"), w)
    temps = q.get("temps") or temps_from(w)
    sets_info = pkg.get("tee_sets") or {}
    sets = bases + [s for s in extra if s not in bases]
    rel = lambda p: os.path.relpath(p, ROOT)                     # noqa: E731
    name = c.get("name") or q["name"]
    town = c.get("town") or c.get("city") or q.get("city") or ""
    lbl = [dt.date.fromisoformat(d).strftime("%a %-m/%-d") for d in days]
    tot = lambda s: (sets_info.get(s) or {}).get("total")         # noqa: E731
    cfg = dict(
        name=name, title=f"{page_name(pkg, q)} Caddie", auto=True, hand_checked=False, main_which="auto", slug=slug,
        sub=(f"{town}, {q['state']} · automatic page · {' / '.join(f'{s} {tot(s):,}' if tot(s) else s for s in bases)}"
             " · Driver 275/300 · 2-wood 265/280 · 4-wood 255/270 at 70°F"),
        event=q.get("event", ""), package=rel(out_dir(q, "package.json")), truth_package=rel(out_dir(q, "package.json")),
        tees=bases[0], alt_bases=({bases[1]: "auto_b"} if len(bases) > 1 else {}), sets=sets,
        colors={s: colour_of(s, sets_info.get(s) or {}) for s in sets}, days=days, day_labels=lbl,
        tee_hour=float(q.get("tee_hour", 9.0)), temps=temps, draws=int((q.get("compute") or {}).get("draws", DEFAULT_DRAWS)),
        swings=int((q.get("compute") or {}).get("swings", DEFAULT_SWINGS)),
        forecast=rel(out_dir(q, "weather.json")), weather_kind=w["kind"],
        climate=dict(temp_lo=min(r["temp_f"] for r in w["hourly"]), temp_hi=max(r["temp_f"] for r in w["hourly"]),
                     wind_mph=round(sum(r["wind_mph"] for r in w["hourly"]) / len(w["hourly"]), 1),
                     wind_from=w["hourly"][len(w["hourly"]) // 2]["wind_from_deg"], source=w["note"][:200]),
        grid_prune=True, bases_why=why, request=q["path"], rev=q.get("rev"),
        foot=(f"Automatic page (not hand checked): course from OpenStreetMap, card from {(pkg.get('scorecard') or {}).get('source') or 'no card'}"
              f", trees / long grass / water from the vision layer on USDA NAIP + USGS 3DEP lidar, OB inferred from the course "
              f"outline and buildings. Solved tee sets: {', '.join(bases)}" +
              (f"; {', '.join(extra)} move the {bases[0]} tee along the line" if extra else "") +
              ". See qa_report.md for the hole-by-hole checks."),
        built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"))
    wj(out_dir(q, "config.json"), cfg)
    sharp = sharp_choice(pkg)
    g = rj(os.path.join(CD, "packages", slug, "imagery", "georef.json")) or {}
    bbox = g.get("padded_bbox_wgs84_snwe")
    wj(out_dir(q, "sharp.json"), dict(sharp or {}, bbox=bbox, use=bool(sharp and bbox)))
    log(f"{slug}: bases {bases} ({why}); extra {extra}; days {days}; weather {w['kind']}; temps {temps}; sharp {sharp}")
    print("SHARP_YEAR=" + (str(sharp["year"]) if sharp and bbox else ""))
    print("SHARP_BBOX=" + (",".join(f"{x:.6f}" for x in bbox) if bbox else ""))


def whiches(cfg):
    return ["auto"] + list((cfg.get("alt_bases") or {}).values())


def prepare(q, imagery=None):
    cfg = rj(out_dir(q, "config.json"))
    pp = os.path.join(ROOT, cfg["package"])
    orig = open(pp).read()
    try:
        if imagery and os.path.exists(os.path.join(imagery, "georef.json")):
            d = json.loads(orig)
            g = rj(os.path.join(imagery, "georef.json"))["imagery"]
            upd = dict(dir=imagery, year=g.get("year"), naip_date=(g.get("acquired") or [None])[0],
                       acquired=g.get("acquired"), resolution_m=g.get("resolution_m"))
            # product/package.load reads "imagery.dir" before "sources.imagery.dir": point both (bh_sharp lesson)
            d.setdefault("imagery", {}).update(upd)
            d.setdefault("sources", {}).setdefault("imagery", {}).update(upd)
            json.dump(d, open(pp, "w"))
        for w in whiches(cfg):
            vc(q, "prepare", "--which", w)
    finally:
        open(pp, "w").write(orig)
    # offsets for the extra (non-base) sets, on the main base
    meta = rj(out_dir(q, "auto", "meta.json"))
    base = meta["tee_set"]
    offs = {0}
    for s in cfg["sets"]:
        if s in cfg.get("alt_bases", {}) or s == base:
            continue
        for k, m in meta["holes"].items():
            y = m.get("yards") or {}
            if y.get(s) and y.get(base) and m.get("par") != 3:
                offs.add(int(20 * round((y[s] - y[base]) / 20.0)))
    cfg["offsets"] = {"auto": sorted(offs)} | {w: [0] for w in whiches(cfg)[1:]}
    cfg["imagery_display"] = rj(out_dir(q, "auto", "meta.json")).get("imagery_date")
    wj(out_dir(q, "config.json"), cfg)
    log("offsets", cfg["offsets"])


# ------------------------------------------------------------------------------------------------ compute
def tee_shot_holes(q, w):
    import importlib.util
    s = importlib.util.spec_from_file_location("c_" + w, out_dir(q, w, "course.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return [str(k) for k in m.ORDER if k in m.HOLES]


def wind_groups(holes, n):
    """Tee-shot holes split over n wind processes. A card with NO tee-shot holes (an all-par-3 course: Quicksands at
    Gamble Sands, 14 par 3s) still gets one process: the wind grid also carries every par 3's plays-like table, and
    without it the page step died on a missing wind_grid.json (course-page run 41346643978). An empty group means
    "every hole" to wind_grid_v2 (WIND_HOLES unset), which on such a card is just the par 3s."""
    return [holes[i::n] for i in range(n) if holes[i::n]] or [[]]


def compute(q, slot, kind, parts):
    cfg = rj(out_dir(q, "config.json"))
    ws = whiches(cfg)
    if slot >= len(ws):
        log(f"slot {slot}: no second base on this card; nothing to compute")
        return
    w = ws[slot]
    holes = tee_shot_holes(q, w)
    np_ = os.cpu_count() or 2
    os.makedirs(parts, exist_ok=True)
    env = v2env(q)
    procs = []
    if kind == "wind":
        temps = ",".join(f"{t:g}" for t in cfg["temps"])
        for b in cfg.get("offsets", {}).get(w, [0]):
            groups = wind_groups(holes, np_)
            procs = []
            for i, g in enumerate(groups):
                e = dict(env, WIND_ONLY=",".join(g))
                lf = open(os.path.join(parts, f"log_wind_{b}_{i}.txt"), "w")
                procs.append(subprocess.Popen([sys.executable, VC_ADAPT_PY, "wind", "--slug", q["slug"], "--which", w,
                                               "--back", str(b), "--temps", temps, "--swings", str(cfg.get("swings", DEFAULT_SWINGS)),
                                               "--out", os.path.join(parts, f"v2wind_{b}_{i}.json")],
                                              env=e, stdout=lf, stderr=subprocess.STDOUT))
            for p in procs:
                p.wait()
            log(f"wind {w} back {b}: {len(groups)} parts, exit codes {[p.returncode for p in procs]}")
    else:
        pending = list(holes)
        running = []
        while pending or running:
            while pending and len(running) < np_:
                h = pending.pop(0)
                lf = open(os.path.join(parts, f"log_dec_{h}.txt"), "w")
                running.append(subprocess.Popen([sys.executable, VC_ADAPT_PY, "decide", "--slug", q["slug"], "--which", w,
                                                 "--holes", h, "--draws", str(cfg.get("draws", DEFAULT_DRAWS)),
                                                 "--out", os.path.join(parts, f"v2dec_{h}.json")],
                                                env=env, stdout=lf, stderr=subprocess.STDOUT))
            running[0].wait()
            running = [p for p in running if p.poll() is None]
        log(f"decide {w}: {len(holes)} holes")
    wj(os.path.join(parts, "which.json"), dict(which=w, kind=kind))


# ------------------------------------------------------------------------------------------------ native
NATIVE_FILES = ("frames.json", "edits.json", "agent_zones.geojson")
NATIVE_SPARE = 2            # the native stage keeps CAP x this candidates: finish drops the ones the page contradicts
NATIVE_AUTO_CAP = 2         # cards kept on a course whose priors are product/native_auto.py's p (no mapper layer):
#                             mapper/EVAL_BLIND.md "Automatic native sides" measured <= 2 taps (GATED + TAP2)
NATIVE_AIM_TOL = 10.0       # yds: native_confirm.AIM_TOL (a plan change)
PAGE_AIM_MAX = 60.0         # yds: the widest aim a page can print (v2_adaptive: the +/-40 bound + MAX_EXTRA)
NATIVE_LABELS = {"L": "Left", "R": "Right", "both": "Both", "none": "None"}


def native_source(q, pkg=None):
    """-> (mapper folder, None) when the course gets native questions from its mapper layer; ("auto", None) when it
    has no mapper layer but the package carries product/native_auto.py's per-side p (package.native_auto, the
    S4n stage: those are the priors, and its automatic band, if any, is already in the package); else (None, why).
    The mapper layer wins: with agent_layers the auto p is never used."""
    d = q.get("agent_layers")
    if q.get("native") is False:
        return None, "request says \"native\": false"
    if not d:
        na = (pkg or {}).get("native_auto") or {}
        if na.get("p") and na.get("usable"):
            return "auto", None
        return None, "no agent_layers in the request and no native_auto p in the package"
    path = d if os.path.isabs(d) else os.path.join(ROOT, d)
    miss = [f for f in NATIVE_FILES if not os.path.exists(os.path.join(path, f))]
    if miss:
        return None, f"{d}: no {', '.join(miss)}"
    return path, None


def native(q):
    """<out>/native.json (lib_native/1): the native questions for the page's main solved set. Never fails the build:
    an error is recorded as the note with no items."""
    import hashlib
    import time
    t0 = time.time()
    cfg = rj(out_dir(q, "config.json")) or {}
    pkg = rj(out_dir(q, "package.json"))
    path, why = native_source(q, pkg)
    rec = dict(schema="lib_native/1", slug=q["slug"], tee_set=cfg.get("tees"), mapper=q.get("agent_layers"), items=[])
    if path is None:
        rec["note"] = f"not asked: {why}"
    elif path == "auto":
        rec.update(source="native_auto", cap=NATIVE_AUTO_CAP)
        try:
            if not cfg.get("tees"):
                raise RuntimeError("no config.json (configure first)")
            sys.path[:0] = [p for p in (os.path.join(CD, "product"),) if p not in sys.path]
            import verify
            workers = os.cpu_count() if os.environ.get("GITHUB_ACTIONS") else int(os.environ.get("NATIVE_WORKERS", "1"))
            n = int(q.get("native_n") or 4000)
            items, note = verify.native_auto_for(pkg, cfg["tees"], n=n, workers=workers, cap=NATIVE_SPARE * NATIVE_AUTO_CAP,
                                                 cache_path=os.environ.get("NATIVE_CACHE") or f"/tmp/native_cache_{q['slug']}.json")
            rec.update(items=items, note=note, n=n)
        except Exception as e:                                  # noqa: BLE001
            rec["note"] = f"skipped ({type(e).__name__}: {e})"[:400]
    else:
        h = hashlib.sha1()
        for f in NATIVE_FILES:
            h.update(open(os.path.join(path, f), "rb").read())
        rec["mapper_sig"] = h.hexdigest()[:16]
        try:
            if not pkg or not cfg.get("tees"):
                raise RuntimeError("no package.json / config.json (configure first)")
            sys.path[:0] = [p for p in (os.path.join(CD, "product"),) if p not in sys.path]
            import verify
            workers = os.cpu_count() if os.environ.get("GITHUB_ACTIONS") else int(os.environ.get("NATIVE_WORKERS", "1"))
            n = int(q.get("native_n") or 4000)
            import native_confirm
            items, note = verify.native_for(pkg, os.path.basename(os.path.normpath(path)), cfg["tees"], n=n,
                                            workers=workers, mapper_dir=path, cap=NATIVE_SPARE * native_confirm.CAP,
                                            cache_path=os.environ.get("NATIVE_CACHE") or f"/tmp/native_cache_{q['slug']}.json")
            rec.update(items=items, note=note, n=n)
        except Exception as e:                                  # noqa: BLE001
            rec["note"] = f"skipped ({type(e).__name__}: {e})"[:400]
    rec["runtime_s"] = round(time.time() - t0, 1)
    wj(out_dir(q, "native.json"), rec)
    log(f"{q['slug']}: native questions: {rec['note']} -> holes {[it['hole'] for it in rec['items']]} "
        f"({rec['runtime_s']} s)")
    return rec


def _aim_words(a):
    """= product/verify.aim_words"""
    a = float(a)
    return "on the line" if abs(a) < 2.5 else f"{abs(a):.0f} yds {'right' if a > 0 else 'left'}"


def _plan_of(txt):
    club, aim = str(txt).rsplit(" ", 1)
    return club, float(aim)


def native_reconcile(rec, holes, cap=4, regret_red=0.02):
    """native.json (lib_native/1) against the page's own calm-day picks (holes: the page holes of rec's tee set).

    The native stage plans with the error-budget planner (product/decide.quick_hole, its own aim bound), the page
    with the v2 engine: Osage National 15 (2026-11-02) had a card saying "now Driver, 60 yds right ... would cost
    0.27 strokes" while the page plays Long iron 1 left. So each card's "no answer" plan must be the page's pick:
      * the planner's current plan is not the page's calm-day pick (another club, or > NATIVE_AIM_TOL yds off),
        or the hole has no calm-day pick on the page -> the card is dropped (its regrets were measured against a
        plan the page does not show);
      * an answer's re-plan aims past PAGE_AIM_MAX (outside any aim the page can print) -> dropped;
      * else the card is re-based on the page's pick: plans.current, each answer's change / aim shift / text
        relative to it; a card no answer changes is dropped.
    The first `cap` kept cards stay (items arrive sorted by value). -> rec (changed in place): items, dropped
    [{hole, why}], baseline."""
    by = {str(h.get("key")): h for h in holes or [] if h.get("kind") == "tee"}
    keep, dropped = [], []
    for it in rec.get("items") or []:
        ref = str(it.get("hole"))
        calm = (by.get(ref) or {}).get("calm") or {}
        if calm.get("pick") is None or calm.get("aim") is None:
            dropped.append(dict(hole=ref, why="no calm-day pick on the page"))
            continue
        pc, pa = calm["pick"], float(calm["aim"])
        plans = it.get("plans") or {}
        cur = _plan_of(plans["current"]) if plans.get("current") else None
        if cur is None or cur[0] != pc or abs(cur[1] - pa) > NATIVE_AIM_TOL:
            dropped.append(dict(hole=ref, why=f"planner's no-answer plan {plans.get('current')} is not the page's "
                                              f"{pc} {pa:+.1f}"))
            continue
        wide = [a for a, t in plans.items() if a != "current" and abs(_plan_of(t)[1]) > PAGE_AIM_MAX + 1e-6]
        if wide:
            dropped.append(dict(hole=ref, why=f"re-plan past {PAGE_AIM_MAX:.0f} yds ({', '.join(f'{a}: {plans[a]}' for a in wide)})"))
            continue
        opts, moved = [], False
        for o in it.get("options") or []:
            oc = dict(o.get("outcome") or {})
            club, aim = oc.get("pick", pc), float(oc.get("aim", pa))
            changed = club != pc or abs(aim - pa) > NATIVE_AIM_TOL
            reg = float(oc.get("regret") or 0.0)
            moved |= changed
            oc.update(club_changed=club != pc, aim_shift=round(aim - pa, 1),
                      severity="red" if changed and reg >= regret_red else ("amber" if changed else "green"))
            if not changed:
                oc.update(pick=pc, aim=pa, aim_shift=0.0, regret=0.0)
            txt = (f"Re-planned: {club}, {_aim_words(aim)} (now {pc}, {_aim_words(pa)})."
                   + (f" Playing today's plan would cost {reg:.2f} strokes." if reg >= 0.005 else "")
                   if changed else "No change to the plan.")
            opts.append(dict(o, text=txt, outcome=oc))
        if not moved:
            dropped.append(dict(hole=ref, why=f"no answer changes the page's {pc} {pa:+.1f}"))
            continue
        it.update(options=opts, plans=dict(plans, current=f"{pc} {pa:+.0f}", planner=plans.get("current")))
        keep.append(it)
    rec["items"] = keep[:cap]
    dropped += [dict(hole=str(it["hole"]), why=f"over the {cap}-card cap") for it in keep[cap:]]
    rec["dropped"] = dropped
    rec["baseline"] = "page calm-day pick"
    return rec


def native_finish(q, data, cfg):
    """finish: native.json reconciled with the page just built (native_reconcile), rewritten in place."""
    p = out_dir(q, "native.json")
    rec = rj(p)
    if not rec or not rec.get("items"):
        return rec
    S = rec.get("tee_set") or cfg.get("tees")
    holes = data["holes"] if S == data.get("base_set") else (data.get("alt") or {}).get(S)
    sys.path[:0] = [x for x in (os.path.join(CD, "product"),) if x not in sys.path]
    import native_confirm
    native_reconcile(rec, holes or [], cap=int(rec.get("cap") or native_confirm.CAP))
    rec["note"] = (rec.get("note") or "") + f"; {len(rec['items'])} kept on the page's own picks" + \
        (f" ({len(rec['dropped'])} dropped)" if rec["dropped"] else "")
    wj(p, rec)
    for d in rec["dropped"]:
        log(f"{q['slug']}: native card {d['hole']} dropped: {d['why']}")
    return rec


def native_summary(q):
    r = rj(out_dir(q, "native.json"))
    if not r:
        return None
    return dict(holes=[it["hole"] for it in r.get("items") or []], tee_set=r.get("tee_set"), note=r.get("note"))


# ------------------------------------------------------------------------------------------------ page
BOOT = """<script id="pg-boot">
(async () => {
  const b64 = document.getElementById("pg-data").textContent.trim();
  const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const txt = await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"))).text();
  const s = document.createElement("script");
  s.textContent = "const D = " + txt + ";\\n" + document.getElementById("pg-main").textContent;
  document.body.appendChild(s);
})();
</script>"""


def split_page(html):
    """-> (head, data dict, main code, tail) of a v2_course page (const D = {...}; <code>)."""
    i = html.index("const D = ") + len("const D = ")
    data, j = json.JSONDecoder().raw_decode(html, i)
    s0 = html.rfind("<script>", 0, i)
    s1 = html.index("</script>", j)
    return html[:s0], data, html[j:s1].lstrip(";"), html[s1 + len("</script>"):]


# Library-page edits of the shared wind-page template (course_data/courses/wind_page_template_course.html stays as the
# tournament pages use it). Each (old, new) must occur in the template; test_publish_gate.py checks that they all do.
PAGE_PATCHES = [
    ("hand-checked against USGS 3DEP lidar", "mapped automatically (not hand checked) from OSM, NAIP and USGS 3DEP lidar"),
    # the template shows the tee picker only once offset grids exist; a page whose second set is a solved base
    # (D.alt) and has no offsets needs it too
    ('document.getElementById("setRow").hidden = !multi; if(!multi) st.set = D.base_set;',
     'const multiSet = multi || !!(D.alt && Object.keys(D.alt).length); '
     'document.getElementById("setRow").hidden = !multiSet; if(!multiSet) st.set = D.base_set;'),
    # golfer-facing set names: D.set_labels (picker, footer) / D.tee_labels ("from the Back tee"); the set keys stay
    # (a no-card page's set is "osm_back": label_no_card)
    ("const SKEY", "const SETLBL = s => (D.set_labels || {})[s] || s, TEELBL = s => (D.tee_labels || {})[s] || s;\n"
                   "const SKEY"),
    ("from the ${T0.name.replace(", "from the ${TEELBL(T0.name).replace("),
    ("from the ${String(P3.setName).replace(", "from the ${String(TEELBL(P3.setName)).replace("),
    ('r.T.name + " tee"', 'TEELBL(r.T.name) + " tee"'),
    ("Elevation measured from the ${h.base_set} tee", "Elevation measured from the ${TEELBL(h.base_set)} tee"),
    (">${s}${D.set_totals", ">${SETLBL(s)}${D.set_totals"),
    ("[D.base_set].concat(Object.keys(D.alt))", "[D.base_set].concat(Object.keys(D.alt)).map(SETLBL)"),
    ("scorecard difference from ${D.base_set}", "scorecard difference from ${SETLBL(D.base_set)}"),
    # no card: nothing is "on the card" (TPC Louisiana par 3s said "176 on the card")
    ("on the card</span>", '${D.no_card ? "to the middle" : "on the card"}</span>'),
    ('"at the card spot"', '(D.no_card ? "at the mapped tee" : "at the card spot")'),
    ("<td>Card</td>", '<td>${D.no_card ? "Measured" : "Card"}</td>'),
    # the hole note is the calm-day book's (club, aim, landing stats); when the forecast play (or the tee) differs it
    # must say so, not sit under the forecast play's label (St Andrews 15 Blue: Long iron shown, 4-wood stats read)
    ('let note = h.note || "";',
     'let note = h.note || "";\n'
     '    if(note && (calm !== r.pick || r.T.back !== 0)) note = `Calm-day pick (no wind'
     '${r.T.back ? ", from the " + TEELBL(h.base_set) + " tee" : ""}): ${calm}. ${note}${/[.!?]$/.test(note) ? "" : "."} '
     'In this wind the play is ${r.pick}: its numbers are in the club table.`;'),
    # (the landing oval's tee-frame shape, landing_pattern.page_cloud, is drawn by the shared template itself since
    # 2026-11-03: tournament pages use it too)
]


def patch_code(code):
    """-> (code with PAGE_PATCHES applied, the patches whose text was not found)."""
    missed = []
    for old, new in PAGE_PATCHES:
        if old in code:
            code = code.replace(old, new)
        elif new not in code:
            missed.append(old)
    return code, missed


def pack_page(head, data, code, tail):
    code, missed = patch_code(code)
    if missed:
        log(f"page template changed: {len(missed)} library patch(es) not applied: {missed}")
    z = base64.b64encode(gzip.compress(json.dumps(data, separators=(",", ":")).encode(), 9)).decode()
    return (head + f'<script id="pg-data" type="application/octet-stream">{z}</script>\n'
            f'<script id="pg-main" type="text/plain">{code}</script>\n' + BOOT + tail)


def gather_parts(parts, w):
    """Artifacts lib-<slug>-<which>-<kind>/: the folders whose which.json names this which."""
    out = []
    for d in sorted(glob.glob(os.path.join(parts, "*"))):
        m = rj(os.path.join(d, "which.json")) or {}
        if m.get("which") == w:
            out.append(d)
    return out


def run_checks(q, cfg):
    res = {}
    osm = out_dir(q, "raw", "osm.geojson")
    for w in whiches(cfg):
        o = f"/tmp/checks_{q['slug']}_{w}.json"
        r = subprocess.run([sys.executable, os.path.join(HERE, "picture_checks.py"), "--slug", q["slug"], "--which", w,
                            "--osm", osm, "--out", o], env=v2env(q), capture_output=True, text=True)
        log(r.stdout[-2000:], r.stderr[-3000:])
        res[w] = rj(o)
    return res


def wide_aim_checks(checks, data):
    """Add the wide-aim check (wide_aims.py: a printed tee-shot aim past +/-40 yds, product/decide.wide_aim_flags
    words) to the picture checks of each solved set: such a hole is a CHECK whatever its other checks say."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import wide_aims
    flags = wide_aims.page_flags(data)
    for w, c in checks.items():
        if not c:
            continue
        for ref, (why, where) in (flags.get(c.get("set")) or {}).items():
            h = c["holes"].get(ref)
            if h is None:
                continue
            h.setdefault("checks", {})["wide_aim"] = dict(ok=False, why="; ".join(why), where=where)
            h["status"] = "CHECK"
            h["reasons"] = [r for r in h.get("reasons", []) if not r.startswith("wide_aim:")] + \
                [f"wide_aim: {r}" for r in why]
    return flags


def run_qa_page(q, page, sets, cfg_set="page"):
    out = {}
    for s in sets:
        d = f"/tmp/qa_{q['slug']}_{slugify(s or 'page')}"
        r = subprocess.run(["node", os.path.join(CD, "courses", "qa_page.js"), page, d] + ([s] if s else []),
                           capture_output=True, text=True, timeout=900)
        log(r.stdout[-1500:], r.stderr[-1500:])
        out[s or cfg_set] = dict(rc=r.returncode, report=rj(os.path.join(d, "qa.json")), stdout=r.stdout[-1500:], stderr=r.stderr[-800:])
    return out


def course_gate(pkg, checks, qa, cfg):
    """Course-level confidence gate. auto-OK = complete OSM holes + card matched + every check PASS + clean page."""
    reasons = []
    pl = pkg.get("pipeline") or {}
    prof = pl.get("profile") or {}
    n = len(pkg.get("holes") or {})
    if (pl.get("holes") or {}).get("method") != "osm":
        reasons.append(f"holes not all mapped in OSM (hole method: {(pl.get('holes') or {}).get('method')})")
    if (prof.get("osm_greens") or 0) < n:
        reasons.append(f"OSM greens {prof.get('osm_greens')} of {n} holes")
    sc = pkg.get("scorecard") or {}
    card_ok = bool(prof.get("card")) and sc.get("kind") not in (None, "none", "typed") and not sc.get("flags")
    if not card_ok:
        reasons.append(f"scorecard not matched (source {sc.get('source')}, flags {sc.get('flags')})")
    ti = pkg.get("tee_set_info") or {}
    if n not in (9, 18) or (cfg.get("tees") and len((pkg.get("tee_sets") or {}).get(cfg["tees"], {}).get("yards") or []) != n):
        reasons.append(f"{n} holes built vs the card's {len((pkg.get('tee_sets') or {}).get(cfg['tees'], {}).get('yards') or [])}")
    vis = str((pkg.get("stages") or {}).get("vision", "") or "")
    if not vis.startswith("ok: vision_any/2"):        # no product tree layer: trees / water from OSM only
        reasons.append(f"vision layer (trees / water) missing: {vis[:160] or 'no vision stage'}")
    check_holes = set()
    for w, c in checks.items():
        if not c:
            reasons.append(f"picture checks failed to run for {w}")
            continue
        if not c["course"]["pars_ok"]:
            reasons.append(f"pars sum to {c['course']['par_total']}, card {c['course']['card_par_total']}")
        for ref, h in c["holes"].items():
            if h["status"] != "PASS":
                check_holes.add(int(ref) if ref.isdigit() else ref)
    page_bad = {}
    for s, r in qa.items():
        rep = r.get("report")
        if not rep:
            reasons.append(f"qa_page.js did not run for {s} (rc {r.get('rc')})")
            continue
        for v, vr in rep["views"].items():
            errs = [e for e in vr.get("errors") or [] if "Failed to load resource" not in e]   # web fonts offline
            if errs:
                reasons.append(f"page console errors ({v}, {s}): {errs[0][:120]}")
            for i, hr in enumerate(vr["holes"]):
                if hr["problems"]:
                    page_bad.setdefault(i, []).append(f"{s} {v}: {'; '.join(hr['problems'])}")
    if check_holes:
        reasons.append(f"{len(check_holes)} hole(s) with a CHECK")
    reasons = list(dict.fromkeys(reasons))
    status = "auto-OK" if not reasons and not page_bad else "needs confirm"
    return status, reasons, sorted(check_holes, key=lambda x: (isinstance(x, str), x)), page_bad


# publish gate: a page this wrong is not a "needs confirm" page (world_woods 2026-11-03: 16 holes, par 64 vs the
# card's 72, resolved to a course 2.9 km from `near` with match score 0.38). "blocked": the page and its files stay in
# the folder (for the review), status.json says why, and the index keeps it off the course list.
GATE_PAR_TOL = 2              # built pars vs the card's total
# holes out of order (TPC Sawgrass: the Stadium holes renumbered onto Dye's Valley's card, 18 holes and the par total
# equal; green n -> tee n+1 walked 237-1,546 yds). Library pages 2026-11-03: every page in order walks <= 672 yds with
# at most 2 walks over 500; the renumbered Sawgrass, Chambers Bay (1,098) and Memorial Park (4 over 500) do not.
GATE_ROUTE_MAX_YD = 800.0     # one green -> next-tee walk longer than this
GATE_ROUTE_LONG_YD = 500.0
GATE_ROUTE_MAX_LONG = 3       # ... or more walks than this over GATE_ROUTE_LONG_YD
GATE_MIN_SCORE = 0.5          # resolve match score (library builds: 0.65 .. 11.6; world_woods 0.38)
GATE_NEAR_KM = 1.5            # ... and the resolved course centre this far from the request's near point
NO_CARD_SET_LABEL = "Back tees (from the map)"
NO_CARD_TEE_LABEL = "Back"


def has_card(pkg, cfg):
    """True when the solved set has card yardages (a no-card build solves the package's own "osm_back" set)."""
    ts = (pkg.get("tee_sets") or {}).get(cfg.get("tees") or pkg.get("tee_set")) or {}
    return bool(ts.get("yards"))


def request_near(q):
    """The request's near point as "lat,lon" (None when the request names the OSM course itself or gives none)."""
    if q.get("osm"):
        return None
    n = q.get("near")
    if isinstance(n, (list, tuple)) and len(n) >= 2:
        return f"{n[0]},{n[1]}"
    return n or None


def _near_ll(near):
    m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*", str(near or ""))
    return (float(m.group(1)), float(m.group(2))) if m else None


def _km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def _yd_ll(a, b):
    """[lon, lat] -> [lon, lat] yds (equirectangular; hole-to-hole distances)."""
    kx = math.cos(math.radians((a[1] + b[1]) / 2)) * 111320 / 0.9144
    return math.hypot((b[0] - a[0]) * kx, (b[1] - a[1]) * 111320 / 0.9144)


def routing_gaps(pkg, cfg=None):
    """Built holes -> [(n, green n -> tee n+1 walk in yds)] for each consecutive pair of numbered holes with a green and a
    tee (the solved set's tee, else the hole line's start)."""
    holes = pkg.get("holes") or {}
    items = holes.items() if isinstance(holes, dict) else ((h.get("ref"), h) for h in holes)
    by = {int(r): h for k, h in items for r in [h.get("ref", k)] if str(r or "").isdigit()}
    s = (cfg or {}).get("tees") or pkg.get("tee_set")

    def tee(h):
        t = ((h.get("tees") or {}).get(s) or {}).get("tee_ll") if isinstance(h.get("tees"), dict) else None
        return t or h.get("tee_ll") or (h.get("hole_line_ll") or [None])[0]
    out = []
    for r in sorted(by):
        a, b = by[r], by.get(r + 1)
        g, t = a.get("green_ll"), tee(b) if b else None
        if g and t:
            out.append((r, round(_yd_ll(g, t))))
    return out


def publish_gate(pkg, cfg, near=None):
    """-> the reasons this page must not be published (empty: publishable). Blocked when the built hole count is not
    the card's (no card: not 18 or 9), the built pars sum more than GATE_PAR_TOL from the card's, or resolve took a
    weak name match (score < GATE_MIN_SCORE) more than GATE_NEAR_KM from the request's near point, or the holes are
    out of order (a green -> next-tee walk over GATE_ROUTE_MAX_YD, or more than GATE_ROUTE_MAX_LONG over
    GATE_ROUTE_LONG_YD)."""
    out = []
    holes = pkg.get("holes") or {}
    hs = list(holes.values()) if isinstance(holes, dict) else list(holes)
    n = len(hs)
    ts = (pkg.get("tee_sets") or {}).get(cfg.get("tees") or pkg.get("tee_set")) or {}
    card_n = len(ts.get("yards") or [])
    if card_n:
        if n != card_n:
            out.append(f"{n} holes built, the card has {card_n}: holes are missing or mis-routed")
    elif n not in (18, 9):
        out.append(f"{n} holes built with no card (expected 18 or 9): holes are missing, or two courses are mixed")
    card_par = sum(p for p in (ts.get("par") or []) if p) or None
    if card_par:
        built = sum(int(h.get("par") or 0) for h in hs)
        if abs(built - card_par) > GATE_PAR_TOL:
            out.append(f"built pars sum to {built}, the card's to {card_par} (more than {GATE_PAR_TOL} apart): "
                       "holes or pars are wrong")
    walks = routing_gaps(pkg, cfg)
    gaps = [g for _, g in walks]
    if gaps:
        big, long_ = max(gaps), sum(g > GATE_ROUTE_LONG_YD for g in gaps)
        if big > GATE_ROUTE_MAX_YD or long_ > GATE_ROUTE_MAX_LONG:
            out.append(f"holes out of order: green-to-next-tee walks up to {big} yds, {long_} over "
                       f"{GATE_ROUTE_LONG_YD:.0f} (in order: under {GATE_ROUTE_MAX_YD:.0f}, at most {GATE_ROUTE_MAX_LONG} "
                       f"over {GATE_ROUTE_LONG_YD:.0f}); longest: " + ", ".join(
                           f"{r}->{r + 1} {g}" for r, g in sorted(walks, key=lambda w: -w[1])[:3]))
    ll = _near_ll(near)
    c = pkg.get("course") or {}
    if ll and c.get("center"):
        cand = [x for x in c.get("candidates") or [] if x.get("osm") == c.get("osm")]
        score = cand[0].get("score") if cand else None
        km = _km(ll, (c["center"][1], c["center"][0]))
        if score is not None and score < GATE_MIN_SCORE and km > GATE_NEAR_KM:
            out.append(f"resolved to '{c.get('name')}' {km:.1f} km from the request's near point with match score "
                       f"{score:.2f} (< {GATE_MIN_SCORE}): probably not the requested course")
    return out


def label_no_card(data, set_name):
    """A page with no card: golfers see NO_CARD_SET_LABEL / "Back tee", never the package's set key ("osm_back"),
    and no "on the card" wording (the template patches read D.no_card / D.set_labels / D.tee_labels). Strings that
    are exactly the set name are keys (base_set, sets, the app and qa.json use them) and stay."""
    data["no_card"] = True
    data["set_labels"] = {set_name: NO_CARD_SET_LABEL}
    data["tee_labels"] = {set_name: NO_CARD_TEE_LABEL}

    def txt(v):
        v = v.replace(f"{set_name} tee", f"{NO_CARD_TEE_LABEL} tee")
        v = v.replace(f"for {set_name}", "for the back tees (from the map)")
        v = v.replace(set_name, NO_CARD_SET_LABEL)
        return v.replace("on the card", "measured")

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("img",):
                    continue
                o[k] = walk(v)
            return o
        if isinstance(o, list):
            return [walk(v) for v in o]
        if isinstance(o, str) and o != set_name and len(o) < 5000:
            return txt(o)
        return o
    walk(data)
    return data


def report_md(q, cfg, pkg, checks, qa, status, reasons, check_holes, page_bad, page_rel, size):
    sc = pkg.get("scorecard") or {}
    pl = pkg.get("pipeline") or {}
    L = [f"# {cfg['name']}: automatic page QA", "",
         f"**Status: {status}**" + (f" — confirm holes {', '.join(map(str, check_holes))}" if check_holes else ""), "",
         f"* page: `{page_rel}` ({size / 1e6:.1f} MB); request `{q['path']}`; built {cfg['built']}",
         f"* course: {pkg['course'].get('name')} ({pkg['course'].get('town') or ''}, {pkg['course'].get('state')}), OSM "
         f"{(pkg['course'].get('osm') or {}).get('type')}/{(pkg['course'].get('osm') or {}).get('id')}; holes: "
         f"{(pl.get('holes') or {}).get('method')} (tier {pl.get('tier')}); card: {sc.get('source')} ({sc.get('kind')})",
         f"* solved tee sets: {', '.join([cfg['tees']] + list(cfg.get('alt_bases') or {}))} ({cfg.get('bases_why')}); "
         f"page sets: {', '.join(cfg['sets'])}",
         f"* weather: {cfg.get('weather_kind')} for {', '.join(cfg['days'])}; grid temperatures {cfg['temps']} F; "
         f"calm-day picks with {cfg.get('draws')} prior draws",
         f"* imagery on the page: {cfg.get('imagery_display')}; package imagery {(pkg.get('imagery') or {}).get('year')}",
         f"* stages: vision `{(pkg.get('stages') or {}).get('vision', '')[:90]}`; OB `{(pkg.get('stages') or {}).get('ob', '')[:90]}`",
         ""]
    nat = native_summary(q)
    if nat:
        L += [f"* native-grass questions ({nat['tee_set']} tees, library check cards): "
              f"{'holes ' + ', '.join(nat['holes']) if nat['holes'] else 'none'} ({nat['note']})", ""]
    if reasons:
        L += ["Course-level reasons:", ""] + [f"* {r}" for r in reasons] + [""]
    L += ["Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick "
          "lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm "
          "book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the "
          "OSM green; the page renders in a phone and a desktop browser).", ""]
    for w, c in checks.items():
        if not c:
            continue
        L += [f"## {c['set']} tees", "", "| hole | par | result | pick | reasons |", "|---|---|---|---|---|"]
        for ref, h in sorted(c["holes"].items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 99):
            pk = h.get("pick") or {}
            pick = f"{pk['club']} {pk['aim']:+.0f}{' (tie)' if pk.get('tie') else ''}" if pk else ""
            rs = list(h["reasons"])
            idx = list(c["holes"]).index(ref)
            rs += page_bad.get(idx, []) if w == "auto" else []
            L.append(f"| {ref} | {h['par']} | {'PASS' if h['status'] == 'PASS' and not (w == 'auto' and idx in page_bad) else 'CHECK'} | "
                     f"{pick} | {'; '.join(rs)} |")
        L.append("")
    return "\n".join(L) + "\n"


def finish(q, parts):
    cfg = rj(out_dir(q, "config.json"))
    for w in whiches(cfg):
        pd = gather_parts(parts, w)
        tmp = f"/tmp/merge_{q['slug']}_{w}"
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        for d in pd:
            shutil.copytree(d, os.path.join(tmp, os.path.basename(d)))
        vc(q, "merge", tmp, "--which", w)
    raw = f"/tmp/page_{q['slug']}.html"
    # through v2_adaptive.py: a hole whose printed aim is wide gets a hole picture wide enough for its landing
    cmd = [sys.executable, VC_ADAPT_PY, "page", "--slug", q["slug"], "--which", "auto", "--out", raw]
    log("$", " ".join(cmd))
    subprocess.run(cmd, env=v2env(q), check=True)
    head, data, code, tail = split_page(open(raw).read())
    # the new page is built and checked as page.new.html and replaces page.html only once everything passed, so a
    # finish that crashes half way leaves the last good page (and its status.json, failed() below) in place
    final = out_dir(q, "page.html")
    page = out_dir(q, "page.new.html")
    open(page, "w").write(pack_page(head, data, code, tail))
    pkg = rj(out_dir(q, "package.json"))
    checks = run_checks(q, cfg)
    wide_aim_checks(checks, data)
    native_finish(q, data, cfg)
    solved = [cfg["tees"]] + list(cfg.get("alt_bases") or {})
    # the tee picker exists only with more than one set on the page; a single-set page is checked as it opens
    qa = run_qa_page(q, page, solved if len(solved) > 1 else [None], cfg_set=solved[0])
    status, reasons, check_holes, page_bad = course_gate(pkg, checks, qa, cfg)
    blocks = publish_gate(pkg, cfg, request_near(q))
    if blocks:                       # not published: the page stays in the folder, off the index list (index)
        status, reasons = "blocked", blocks + [r for r in reasons if r not in blocks]
    # the page says what was checked: status in the subtitle, the reasons in each CHECK hole's note
    data["sub"] = cfg["sub"].replace("automatic page", f"automatic page: {status.upper()}" +
                                     (f" (confirm {', '.join(map(str, check_holes))})" if check_holes else ""))
    for w, c in checks.items():
        if not c:
            continue
        hs = data["holes"] if w == "auto" else (data.get("alt") or {}).get(c["set"]) or []
        for hd in hs:
            h = c["holes"].get(str(hd.get("key")))
            if h and h["status"] != "PASS":
                hd["note"] = ((hd.get("note") or "") + " Auto-map CHECK: " + "; ".join(h["reasons"])).strip()
    if not has_card(pkg, cfg):
        label_no_card(data, cfg["tees"])
    open(page, "w").write(pack_page(head, data, code, tail))
    os.replace(page, final)
    page = final
    size = os.path.getsize(page)
    page_rel = os.path.relpath(page, ROOT)
    open(out_dir(q, "qa_report.md"), "w").write(
        report_md(q, cfg, pkg, checks, qa, status, reasons, check_holes, page_bad, page_rel, size))
    summ = {s: dict(rc=r["rc"], problems=sum(len(h["problems"]) for v in (r.get("report") or {}).get("views", {}).values()
                                              for h in v["holes"]),
                    errors=sum(len(v.get("errors") or []) for v in (r.get("report") or {}).get("views", {}).values()))
            for s, r in qa.items()}
    wj(out_dir(q, "qa.json"), dict(checks=checks, page=summ))
    st = status_record(q, cfg, pkg, status, reasons, check_holes, page_rel, size)
    wj(out_dir(q, "status.json"), st)
    log(json.dumps(st, indent=1))


def status_record(q, cfg, pkg, status, reasons, check_holes, page_rel, size):
    c = pkg.get("course") or {}
    ts = pkg.get("tee_sets") or {}
    solved = [cfg["tees"]] + list(cfg.get("alt_bases") or {})
    sets = [dict(name=s, yards=v.get("total"), par=sum(v.get("par") or []) or None, rating=v.get("rating"),
                 slope=v.get("slope"), colour=v.get("colour"),
                 on_page=("solved" if s in solved else "offset" if s in cfg["sets"] else None))
            for s, v in sorted(ts.items(), key=lambda kv: -(kv[1].get("total") or 0))]
    lon, lat = c.get("center") or (None, None)
    return dict(slug=q["slug"], name=c.get("name") or q["name"], request_name=q["name"],
                city=q.get("city") or c.get("town"), state=q["state"], group=q["group"], status=status,
                reasons=reasons, check_holes=check_holes, tee_sets=sets, solved_sets=solved, page=page_rel,
                page_bytes=size, qa_report=os.path.relpath(out_dir(q, "qa_report.md"), ROOT),
                center=[lat, lon], osm=f"{(c.get('osm') or {}).get('type')}/{(c.get('osm') or {}).get('id')}",
                holes=len(pkg.get("holes") or {}), days=cfg["days"], weather=cfg.get("weather_kind"),
                built=cfg["built"], request=q["path"], **({"native": native_summary(q)} if native_summary(q) else {}))


ERR_LINE = re.compile(r"^(?:[A-Za-z_][\w.]*\.)?[A-Z]\w*(?:Error|Exception|Exit|Interrupt)\b(?::.*)?$")
TS_PREFIX = re.compile(r"^\d{4}-\d\d-\d\dT[\d:.]+Z\s?")         # an Actions log line's timestamp


def error_lines(text, k=3, width=300):
    """The last k distinct exception lines of a run's output ("FileNotFoundError: ... wind_grid.json"), runner paths
    made repo-relative; with no exception line, the last non-empty lines. status.json "reasons" carries them so a
    failed finish is diagnosable from the repo: "merge / page / checks failed" alone hid real bugs (Bethpage /
    Pinehurst hole refs, Gamble Sands' all-par-3 card)."""
    lines = [TS_PREFIX.sub("", ln).rstrip() for ln in (text or "").splitlines()]
    lines = [ln for ln in lines if ln.strip()]
    hits = [ln.strip() for ln in lines if ERR_LINE.match(ln.strip())]
    pick = hits or [ln.strip() for ln in lines[-k:]]
    out = []
    for ln in reversed(pick):
        ln = re.sub(r"(/[\w.\-]+)*/(course_data|spirit_hollow)/", r"\2/", ln)
        ln = re.sub(r"(/[\w.\-]+)*/bin/python3(\.\d+)?", "python3", ln)
        ln = ln if len(ln) <= width else ln[:width - 3] + "..."
        if ln not in out:
            out.append(ln)
        if len(out) == k:
            break
    return list(reversed(out))


def failed(q, stage, msg, log=None):
    """A course that did not reach a page: status.json says where it stopped (the index lists it as failed).
    log: that stage's captured output; its last exception lines become extra reasons ("finish error: ...")."""
    os.makedirs(out_dir(q), exist_ok=True)
    detail = []
    if log and os.path.exists(log):
        detail = error_lines(open(log, errors="replace").read())
    rc = rj(os.path.join(CD, "packages", q["slug"], "raw", "course.json")) or {}
    st = dict(slug=q["slug"], name=q["name"], request_name=q["name"], city=q.get("city"), state=q["state"],
              group=q["group"], status="failed", reasons=[f"{stage}: {msg}"] + [f"{stage} error: {d}" for d in detail],
              check_holes=[], tee_sets=[],
              page=None, page_bytes=None, request=q["path"],
              resolve=dict(status=rc.get("status"), candidates=[{k: x.get(k) for k in ("name", "town", "holes", "osm")}
                                                               for x in (rc.get("candidates") or [])[:5]]),
              built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"))
    try:
        os.remove(out_dir(q, "page.new.html"))             # a finish that crashed half way: never shipped
    except OSError:
        pass
    prev = rj(out_dir(q, "status.json"))
    if has_good_page(prev):
        # a re-run failed (an Overpass timeout, a crash): the last good page stays listed, its status.json and
        # qa_report.md unchanged; the failure is recorded beside it
        keep = {k: v for k, v in prev.items() if k != "last_attempt"}
        keep["last_attempt"] = dict(status="failed", stage=stage, error=st["reasons"], when=st["built"],
                                    resolve=st["resolve"])
        wj(out_dir(q, "status.json"), keep)
        print(f"{q['slug']}: {stage} failed; keeping the last good page ({prev.get('status')}, built {prev.get('built')})", file=sys.stderr)
        return
    wj(out_dir(q, "status.json"), st)
    open(out_dir(q, "qa_report.md"), "w").write(f"# {q['name']}: no page\n\n**Status: failed** at {stage}: {msg}\n\n"
                                                 + "".join(f"    {d}\n" for d in detail) + ("\n" if detail else "")
                                                 + f"Resolve: {json.dumps(st['resolve'])}\n")


def has_good_page(st):
    """A status.json record of a built page whose page file is still on disk (failed / unsupported records have none)."""
    return bool(st and st.get("status") not in ("failed", "unsupported") and st.get("page")
                and os.path.exists(os.path.join(ROOT, st["page"])))


def imagery_problem(pkg):
    """Why the package's imagery cannot make a library page (None when it is USDA NAIP). NAIP covers the lower 48
    only: elsewhere (Anchorage, AK) the package falls back to 10 m Sentinel-2 and the hole pictures come out gray."""
    im = (pkg or {}).get("imagery") or {}
    src = str(im.get("source") or "")
    if not im or im.get("present") is False:
        return "no imagery in the package"
    if "NAIP" not in src:
        return (f"imagery is {src or 'unknown'} at {im.get('resolution_m')} m, not USDA NAIP (NAIP covers the lower 48 "
                "states only): hole pictures would be gray / unreadable")
    return None


def check_imagery(q, pkg):
    """configure: a course outside NAIP coverage is marked "unsupported" (no page, delisted, even if an earlier build
    shipped one) and the build stops here, loudly, instead of shipping gray pictures."""
    why = imagery_problem(pkg)
    if not why:
        return
    os.makedirs(out_dir(q), exist_ok=True)
    st = dict(slug=q["slug"], name=q["name"], request_name=q["name"], city=q.get("city"), state=q["state"],
              group=q["group"], status="unsupported", reasons=[f"imagery: {why}"], check_holes=[], tee_sets=[],
              page=None, page_bytes=None, request=q["path"],
              built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"))
    wj(out_dir(q, "status.json"), st)
    open(out_dir(q, "qa_report.md"), "w").write(f"# {q['name']}: no page\n\n**Status: unsupported**: {why}\n")
    raise SystemExit(f"{q['slug']}: unsupported: {why}")


# ------------------------------------------------------------------------------------------------ index
INDEX_KEYS = ("slug", "name", "city", "state", "status", "check_holes", "reasons", "tee_sets", "solved_sets", "page",
              "page_bytes", "qa_report", "center", "osm", "holes", "days", "weather", "built")
INDEX_ORDER = {"hand-checked": 0, "auto-OK": 1, "needs confirm": 2, "failed": 3, "unsupported": 4}
BLOCKED_KEYS = ("slug", "name", "city", "state", "status", "reasons", "page", "qa_report", "holes", "osm", "built")


def index_row(s):
    """A library status.json -> its index.json row (with "last_attempt" when a re-run failed after a good build)."""
    return ({k: s.get(k) for k in INDEX_KEYS} | {"group": "library"}
            | ({"last_attempt": s["last_attempt"]} if s.get("last_attempt") else {}))


def index():
    rows = []
    blocked = []
    for p in sorted(glob.glob(os.path.join(HERE, "*", "status.json"))):
        s = rj(p)
        if s and s.get("status") == "blocked":          # publish_gate: kept off the course list, files kept
            blocked.append({k: s.get(k) for k in BLOCKED_KEYS})
        elif s:
            rows.append(index_row(s))
    for d in sorted(glob.glob(os.path.join(TOURNAMENT, "*", "config.json"))):
        slug = os.path.basename(os.path.dirname(d))
        cfg = rj(d) or {}
        page = os.path.join(TOURNAMENT, slug, "wind_page", "index.html")
        if not os.path.exists(page):
            continue
        pk = rj(os.path.join(ROOT, cfg.get("package", ""))) or {}
        c = pk.get("course") or {}
        ts = pk.get("tee_sets") or {}
        solved = [cfg.get("tees")] + list(cfg.get("alt_bases") or {})
        lon, lat = c.get("center") or (None, None)
        rows.append(dict(slug=slug, name=cfg.get("name"), city=c.get("town"), state=c.get("state"),
                         status="hand-checked", check_holes=[], reasons=[], group="tournament",
                         tee_sets=[dict(name=s, yards=(ts.get(s) or {}).get("total"), par=sum((ts.get(s) or {}).get("par") or []) or None,
                                        rating=(ts.get(s) or {}).get("rating"), slope=(ts.get(s) or {}).get("slope"),
                                        colour=(ts.get(s) or {}).get("colour"),
                                        on_page="solved" if s in solved else "offset") for s in cfg.get("sets") or []],
                         solved_sets=solved, page=os.path.relpath(page, ROOT), page_bytes=os.path.getsize(page),
                         qa_report=None, center=[lat, lon], osm=f"{(c.get('osm') or {}).get('type')}/{(c.get('osm') or {}).get('id')}",
                         holes=len(pk.get("holes") or {}) or None, days=cfg.get("days"),
                         weather="forecast" if cfg.get("forecast") else "climate normals", built=None))
    # Spirit Hollow's hand-checked v2 page predates course_data/courses/
    sh = os.path.join(ROOT, "spirit_hollow", "v2", "wind_page", "index.html")
    pk = rj(os.path.join(CD, "packages", "spirit_hollow", "package.json")) or {}
    if os.path.exists(sh):
        ts = pk.get("tee_sets") or {}
        c = pk.get("course") or {}
        rows.append(dict(slug="spirit_hollow", name="Spirit Hollow Golf Course", city="Burlington", state="IA",
                         status="hand-checked", check_holes=[], reasons=[], group="tournament",
                         tee_sets=[dict(name=s, yards=v.get("total"), par=sum(v.get("par") or []) or None,
                                        rating=v.get("rating"), slope=v.get("slope"), colour=v.get("colour"),
                                        on_page="solved" if s == "Black" else "offset" if s in ("Gold", "White", "Rust") else None)
                                   for s, v in sorted(ts.items(), key=lambda kv: -(kv[1].get("total") or 0))],
                         solved_sets=["Black"], page=os.path.relpath(sh, ROOT), page_bytes=os.path.getsize(sh),
                         qa_report=None, center=list(reversed(c.get("center") or [None, None])),
                         osm=f"{(c.get('osm') or {}).get('type')}/{(c.get('osm') or {}).get('id')}",
                         holes=len(pk.get("holes") or {}) or None, days=None, weather="forecast", built=None))
    order = INDEX_ORDER
    rows.sort(key=lambda r: (order.get(r["status"], 9), r["state"] or "", r["name"] or ""))
    idx = dict(schema="course_library/1", doc="course_data/library/README.md",
               updated=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
               counts={k: sum(1 for r in rows if r["status"] == k) for k in order} | {"blocked": len(blocked)},
               courses=rows, blocked=blocked)
    wj(os.path.join(HERE, "index.json"), idx)
    print(json.dumps(idx["counts"]))


def regate(apply=False, dirs=None):
    """Run publish_gate over built library pages on disk (status.json + package.json + config.json + the request's
    near point) -> [(slug, old status, reasons)] of the pages it blocks; apply=True writes "blocked" into their
    status.json (reasons first, the old ones kept, page and files untouched). The next index drops them."""
    flips = []
    for p in sorted(glob.glob(os.path.join(HERE, "*", "status.json")) if dirs is None else
                    [os.path.join(d, "status.json") for d in dirs]):
        st = rj(p)
        if not st or st.get("status") in ("failed", "unsupported", "blocked", "hand-checked") or not st.get("page"):
            continue
        d = os.path.dirname(p)
        pkg, cfg = rj(os.path.join(d, "package.json")), rj(os.path.join(d, "config.json")) or {}
        if not pkg:
            continue
        q = rj(os.path.join(ROOT, st["request"])) if st.get("request") else None
        b = publish_gate(pkg, cfg, request_near(q or {}))
        if not b:
            continue
        flips.append((st["slug"], st["status"], b))
        if apply:
            st.update(status="blocked", reasons=b + [r for r in st.get("reasons") or [] if r not in b],
                      blocked=dict(by="course_page.py regate", when=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                                   was=flips[-1][1]))
            wj(p, st)
    return flips


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["plan", "pkgreq", "configure", "prepare", "native", "compute", "finish", "failed", "index", "slug",
                                    "regate"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--imagery")
    ap.add_argument("--apply", action="store_true", help="regate: write the blocked status (default: list only)")
    ap.add_argument("--log", help="failed: the stage's captured output; its last exception lines go in the reasons")
    a = ap.parse_intermixed_args()
    if a.cmd == "plan":
        print(json.dumps(plan(a.args)))
    elif a.cmd == "index":
        index()
    elif a.cmd == "regate":
        for slug, was, b in regate(apply=a.apply, dirs=a.args or None):
            print(f"{slug}: {was} -> blocked{'' if a.apply else ' (dry run)'}: " + "; ".join(b))
    else:
        q = request(a.args[0])
        if a.cmd == "slug":
            print(q["slug"], q["out"])
        elif a.cmd == "pkgreq":
            os.makedirs(out_dir(q), exist_ok=True)
            pkgreq(q)
        elif a.cmd == "configure":
            configure(q)
        elif a.cmd == "prepare":
            prepare(q, a.imagery)
        elif a.cmd == "native":
            native(q)
        elif a.cmd == "compute":
            compute(q, int(a.args[1]), a.args[2], a.args[3])
        elif a.cmd == "finish":
            finish(q, a.args[1])
        elif a.cmd == "failed":
            failed(q, a.args[1], " ".join(a.args[2:]), log=a.log)


if __name__ == "__main__":
    main()
