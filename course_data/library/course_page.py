"""One request, one page: any US course -> a checked wind and club-pick page (.github/workflows/course_page.yml).

Request (course_data/requests/course_page_<slug>.json, schema course_page/1):
  {"name": "Swope Memorial Golf Course", "city": "Kansas City", "state": "MO",
   "near": "lat,lon" | "osm": "way/123"      (optional disambiguation),
   "tees": ["Blue", "White"]                 (optional tee sets of interest; default: the two longest sets),
   "days": ["2026-11-07", "2026-11-08"]       (optional event days; default the next Saturday + Sunday),
   "tee_hour": 9.0, "slug": "...", "group": "library" | "gate", "compute": {"draws": 48, "swings": 2500},
   "rev": 1}
Batch: course_data/requests/course_batch_<name>.json {"requests": [paths], "rev": n} rebuilds the listed requests.

Stages (each a subcommand, run by the workflow; README.md in this folder has the whole picture):
  plan REQ...          -> job matrices (skips any target whose config says "hand_checked": true, and every
                          slug that is a tournament page in course_data/courses/)
  pkgreq REQ           -> <out>/package_request.json (platform/package.py request: name, town, state, tees)
  configure REQ        -> bases (two longest sets of interest), <out>/config.json (v2_course format), weather,
                          sharpest leaf-on NAIP year for display -> <out>/sharp.json
  prepare REQ [--imagery DIR]  -> v2_course prepare for each base, the hole images rendered from DIR
  compute REQ SLOT KIND PARTS  -> wind grids (base SLOT, its offsets) or the calm-day Bayesian decide
  finish REQ PARTS     -> merge, page (data gzip-inlined), picture checks, qa_page.js, qa_report.md, status.json
  index                -> course_data/library/index.json
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
    return q


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
    for k in ("near", "osm", "typed_card", "yardages", "pars"):
        if q.get(k):
            r[k] = q[k]
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
        name=name, title=f"{name} Caddie", auto=True, hand_checked=False, main_which="auto", slug=slug,
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
            groups = [holes[i::np_] for i in range(np_) if holes[i::np_]]
            procs = []
            for i, g in enumerate(groups):
                e = dict(env, WIND_ONLY=",".join(g))
                lf = open(os.path.join(parts, f"log_wind_{b}_{i}.txt"), "w")
                procs.append(subprocess.Popen([sys.executable, VC_PY, "wind", "--slug", q["slug"], "--which", w,
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
                running.append(subprocess.Popen([sys.executable, VC_PY, "decide", "--slug", q["slug"], "--which", w,
                                                 "--holes", h, "--draws", str(cfg.get("draws", DEFAULT_DRAWS)),
                                                 "--out", os.path.join(parts, f"v2dec_{h}.json")],
                                                env=env, stdout=lf, stderr=subprocess.STDOUT))
            running[0].wait()
            running = [p for p in running if p.poll() is None]
        log(f"decide {w}: {len(holes)} holes")
    wj(os.path.join(parts, "which.json"), dict(which=w, kind=kind))


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


def pack_page(head, data, code, tail):
    code = code.replace("hand-checked against USGS 3DEP lidar", "mapped automatically (not hand checked) from OSM, "
                        "NAIP and USGS 3DEP lidar")
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


def run_qa_page(q, page, sets):
    out = {}
    for s in sets:
        d = f"/tmp/qa_{q['slug']}_{slugify(s)}"
        r = subprocess.run(["node", os.path.join(CD, "courses", "qa_page.js"), page, d, s], capture_output=True,
                           text=True, timeout=900)
        log(r.stdout[-1500:], r.stderr[-1500:])
        out[s] = dict(rc=r.returncode, report=rj(os.path.join(d, "qa.json")), stdout=r.stdout[-1500:], stderr=r.stderr[-800:])
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
            if vr.get("errors"):
                reasons.append(f"page console errors ({v}, {s})")
            for i, hr in enumerate(vr["holes"]):
                if hr["problems"]:
                    page_bad.setdefault(i, []).append(f"{s} {v}: {'; '.join(hr['problems'])}")
    if check_holes:
        reasons.append(f"{len(check_holes)} hole(s) with a CHECK")
    reasons = list(dict.fromkeys(reasons))
    status = "auto-OK" if not reasons and not page_bad else "needs confirm"
    return status, reasons, sorted(check_holes, key=lambda x: (isinstance(x, str), x)), page_bad


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
    if reasons:
        L += ["Course-level reasons:", ""] + [f"* {r}" for r in reasons] + [""]
    L += ["Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick "
          "lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the "
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
    vc(q, "page", "--which", "auto", "--out", raw)
    head, data, code, tail = split_page(open(raw).read())
    page = out_dir(q, "page.html")
    open(page, "w").write(pack_page(head, data, code, tail))
    pkg = rj(out_dir(q, "package.json"))
    checks = run_checks(q, cfg)
    qa = run_qa_page(q, page, [cfg["tees"]] + list(cfg.get("alt_bases") or {}))
    status, reasons, check_holes, page_bad = course_gate(pkg, checks, qa, cfg)
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
    open(page, "w").write(pack_page(head, data, code, tail))
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
                built=cfg["built"], request=q["path"])


def failed(q, stage, msg):
    """A course that did not reach a page: status.json says where it stopped (the index lists it as failed)."""
    os.makedirs(out_dir(q), exist_ok=True)
    rc = rj(os.path.join(CD, "packages", q["slug"], "raw", "course.json")) or {}
    st = dict(slug=q["slug"], name=q["name"], request_name=q["name"], city=q.get("city"), state=q["state"],
              group=q["group"], status="failed", reasons=[f"{stage}: {msg}"], check_holes=[], tee_sets=[],
              page=None, page_bytes=None, request=q["path"],
              resolve=dict(status=rc.get("status"), candidates=[{k: x.get(k) for k in ("name", "town", "holes", "osm")}
                                                               for x in (rc.get("candidates") or [])[:5]]),
              built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"))
    wj(out_dir(q, "status.json"), st)
    open(out_dir(q, "qa_report.md"), "w").write(f"# {q['name']}: no page\n\n**Status: failed** at {stage}: {msg}\n\n"
                                                 f"Resolve: {json.dumps(st['resolve'])}\n")


# ------------------------------------------------------------------------------------------------ index
def index():
    rows = []
    for p in sorted(glob.glob(os.path.join(HERE, "*", "status.json"))):
        s = rj(p)
        if s:
            rows.append({k: s.get(k) for k in ("slug", "name", "city", "state", "status", "check_holes", "reasons",
                                               "tee_sets", "solved_sets", "page", "page_bytes", "qa_report", "center",
                                               "osm", "holes", "days", "weather", "built")} | {"group": "library"})
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
    order = {"hand-checked": 0, "auto-OK": 1, "needs confirm": 2, "failed": 3}
    rows.sort(key=lambda r: (order.get(r["status"], 9), r["state"] or "", r["name"] or ""))
    idx = dict(schema="course_library/1", doc="course_data/library/README.md",
               updated=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
               counts={k: sum(1 for r in rows if r["status"] == k) for k in order}, courses=rows)
    wj(os.path.join(HERE, "index.json"), idx)
    print(json.dumps(idx["counts"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["plan", "pkgreq", "configure", "prepare", "compute", "finish", "failed", "index", "slug"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--imagery")
    a = ap.parse_args()
    if a.cmd == "plan":
        print(json.dumps(plan(a.args)))
    elif a.cmd == "index":
        index()
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
        elif a.cmd == "compute":
            compute(q, int(a.args[1]), a.args[2], a.args[3])
        elif a.cmd == "finish":
            finish(q, a.args[1])
        elif a.cmd == "failed":
            failed(q, a.args[1], " ".join(a.args[2:]))


if __name__ == "__main__":
    main()
