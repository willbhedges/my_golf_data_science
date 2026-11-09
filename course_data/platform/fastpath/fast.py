"""Fast path: course name -> package + per-hole strategy, one command, one machine, raw fetches cached on disk.

  python3 course_data/platform/fastpath/fast.py "Crow Canyon Country Club, San Ramon, CA" [--slug S] [--n 2000]
          [--no-imagery] [--refetch]
  -> cache/packages/<slug>/{raw/, imagery/, package.json, decision.json, timing.json}

Stages (timed; timing.json): resolve (national index + OSM API) > OSM features (OSM API bbox) > scorecards ||
imagery (NAIP + 3DEP) > package build (platform/package.py build_package, unchanged) > solve (solve.py).
"""
import argparse
import gzip
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
ROOT = os.path.dirname(CD)
CACHE = os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache")
sys.path[:0] = [HERE, PLAT]
import platform_common as pc  # noqa: E402

pc.PACKAGES = os.path.join(CACHE, "packages")
import osm_api  # noqa: E402

_ROWS = None
CARD_BUDGET_S = 15.0


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"['’]", "", s)
    return [w for w in re.sub(r"[^a-z0-9]+", " ", s).split() if w not in ("the", "golf", "course", "club", "country", "and", "at", "of", "cc", "gc")]


def index_rows():
    global _ROWS
    if _ROWS is None:
        d = json.load(gzip.open(os.path.join(CD, "library", "us_courses.json.gz")))
        _ROWS = [dict(zip(d["fields"], r)) for r in d["rows"]]
    return _ROWS


def lookup(query):
    """'Name, City, ST' (city optional) -> the best national-index row, or None. The app's pick screen does this
    on the phone (course_index.js); here: every name word must match, city breaks ties."""
    parts = [p.strip() for p in query.split(",")]
    st = parts[-1].upper() if len(parts) > 1 and len(parts[-1].strip()) == 2 else None
    if st is None and len(parts) > 1:
        st = pc.state_code(parts[-1])
    name = parts[0]
    city = parts[1] if len(parts) > 2 else ""
    want = set(norm(name))
    best = None
    for r in index_rows():
        if st and r["state"] != st:
            continue
        got = set(norm(r["name"]))
        if not want or not want <= got and not got <= want:
            continue
        sc = len(want & got) / max(len(want | got), 1) + (0.5 if city and norm(city) == norm(r["city"]) else 0) - (0.3 if r["closed"] else 0)
        if best is None or sc > best[0]:
            best = (sc, r)
    return best and best[1]


def build(query, slug=None, n=2000, imagery=True, row=None, log=print, extra=None, year="auto", canopy_trees=True):
    T = {}
    t_all = time.time()

    def lap(name, t0):
        T[name] = round(time.time() - t0, 2)
        log(f"  {name}: {T[name]} s")
    t0 = time.time()
    row = row or lookup(query)
    if row is None:
        return dict(status="not_found", query=query)
    slug = slug or pc.slugify(row["name"]) + "_" + row["state"].lower()
    pkg_dir = os.path.join(pc.PACKAGES, slug)
    raw = os.path.join(pkg_dir, "raw")
    os.makedirs(raw, exist_ok=True)
    course = osm_api.course_from_row(row, CACHE)
    pc.write_json(os.path.join(raw, "course.json"), course)
    lap("resolve", t0)
    if course["status"] != "ok":
        return dict(status=course["status"], slug=slug, why=course.get("closed"))
    req = dict(schema="request/1", kind="package", course=row["name"], state=row["state"], slug=slug, tees="Black",
               allow_substitute=True, builder="fastpath", town=row.get("city"), osm=row["osm"],
               near=f"{row['lat']:.5f},{row['lon']:.5f}", **(extra or {}))
    pc.write_json(os.path.join(pkg_dir, "package_request.json"), req)
    t0 = time.time()
    fc, summ = osm_api.features(course, raw, CACHE, req)
    lap("osm", t0)
    import fetch_package as fp

    def cards():
        t = time.time()
        if not os.path.exists(os.path.join(raw, "scorecard_web.json")):
            fp.fetch_scorecards(req, course, summ, raw)
        T["card"] = round(time.time() - t, 2)

    def img():
        t = time.time()
        if imagery and not os.path.exists(os.path.join(pkg_dir, "imagery", "georef.json")):
            import imagery as fim
            _, ti = fim.fetch(course["bbox"], os.path.join(pkg_dir, "imagery"), fc, year, label=course["name"])
            T.update(ti)
        T["imagery"] = round(time.time() - t, 2)
    def trees():
        t = time.time()
        if canopy_trees:
            import canopy
            canopy.fetch(course["bbox"], os.path.join(pkg_dir, "canopy"))
        T["canopy"] = round(time.time() - t, 2)
    t0 = time.time()
    import threading
    tc = threading.Thread(target=cards, daemon=True)     # the card search never holds the build: CARD_BUDGET_S
    tc.start()
    with ThreadPoolExecutor(4) as ex:
        fs = [ex.submit(img), ex.submit(trees)]
        for f in fs:
            f.result()
    tc.join(max(0.0, CARD_BUDGET_S - (time.time() - t0)))
    if tc.is_alive():
        T["card"] = f"still searching after {CARD_BUDGET_S} s: built without it (a later run reads the cached answer)"
    lap("fetch (card || imagery)", t0)
    t0 = time.time()
    import package as pk
    try:
        package = pk.build_package(req, pkg_dir)
    except SystemExit as e:
        T["total"] = round(time.time() - t_all, 2)
        pc.write_json(os.path.join(pkg_dir, "timing.json"), T)
        return dict(status="failed", stage="package", why=str(e)[:400], slug=slug, timing=T)
    lap("package build", t0)
    if canopy_trees and not str((package.get("stages") or {}).get("vision", "")).startswith("ok"):
        t0 = time.time()
        import canopy
        if canopy.add_trees(package, CACHE):
            st = package.get("stages")
            package = pk.reframe(package)
            package["stages"] = st
        lap("trees (Meta canopy)", t0)
    pk.write(package, pkg_dir)
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(HERE, "solve.py"), os.path.join(pkg_dir, "package.json"), "--n", str(n),
                        "--out", os.path.join(pkg_dir, "decision.json")], capture_output=True, text=True)
    lap("solve", t0)
    if r.returncode:
        log(r.stderr[-1500:])
    T["total"] = round(time.time() - t_all, 2)
    T["stages"] = package.get("stages")
    pc.write_json(os.path.join(pkg_dir, "timing.json"), T)
    return dict(status="ok" if r.returncode == 0 else "failed", stage=None if r.returncode == 0 else "solve", slug=slug,
                holes=len(package["holes"]), timing={k: v for k, v in T.items() if k != "stages"}, dir=pkg_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--slug")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--no-imagery", action="store_true", help="the ~10 s point: OSM + card + solve (no NAIP / DEM)")
    ap.add_argument("--no-trees", action="store_true")
    ap.add_argument("--year", default="auto")
    a = ap.parse_args()
    print(json.dumps(build(a.query, a.slug, a.n, not a.no_imagery, year=a.year, canopy_trees=not a.no_trees), indent=1))
