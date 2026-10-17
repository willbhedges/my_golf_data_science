"""Zero-tap benchmark data (workstream D): state split, surveys, course selection and per-course fetch.

Network steps run on GitHub Actions only (workflow zero_tap_data.yml, request files
course_data/requests/ztbench_data_<name>.json). Offline:

  python course_data/zero_tap/fetch.py split                 -> the dev / test state split (prints JSON)
  python course_data/zero_tap/fetch.py select                -> selection.json (needs the new-state surveys)

Actions:
  python course_data/zero_tap/fetch.py survey NY --out surveys/survey_NY.json      (one state per job)
  python course_data/zero_tap/fetch.py fetch --chunk 0 --of 6 [--what osm,card,imagery] [--missing-only]

State split (`split()`, frozen; never re-drawn):
  dev   the 12 generalize tuning states (CA GA IL KY MA ME MN MS NH UT WI WY): routing v2 and the structure solver
        were tuned on them. The 31 generalize/validation_set.json *test* courses in these states keep split "test"
        (they were held out course by course before this benchmark existed) - the only exception to split by state.
  test  the 12 structure held-out states (IA MO NE CT NJ PA AR DE NC ID NV WA): nothing was tuned on them.
  new   the other 24 lower-48 states, per Census region shuffled with random.Random(SEED + region index):
        the first ceil(n / 2) are test, the rest dev.
Selection (`select()`, seed SEED): from each new state's survey 5 courses with 18 <= golf=hole ways <= 22 and
>= 17 greens, one 9-hole (9-11 ways, 8-12 greens) and one 27/36-hole facility (27-40 ways); from each of the 12
dev states' committed generalize surveys one 9-hole and one 27/36-hole facility (those were missing there). Every
course already in generalize/sample.json or structure/sets.json is skipped (those are reused as they are).

Per course (data/<slug>/): course.json (resolve.py), osm.geojson.gz (structure/fetch.py subset: golf=*, boundary,
buildings, car parks, paths, water, woods; ODbL (c) OpenStreetMap contributors; hole ways kept: they are the truth),
scorecard.json (web cards: golfify / club site / opengolfapi, normalised scorecard/1, as run_course.py),
segment.geojson.gz + pads.json (`imagery`: NAIP U-Net greens / tees / fairways and 3DEP lidar tee pads, as
run_course.py) for the unmapped tier.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(CD, "platform"), os.path.join(CD, "generalize"), CD]

DATA = os.path.join(HERE, "data")
SURVEYS = os.path.join(HERE, "surveys")
SELECTION = os.path.join(HERE, "selection.json")
SEED = 20261019
GEN_STATES = ["CA", "GA", "IL", "KY", "MA", "ME", "MN", "MS", "NH", "UT", "WI", "WY"]
STRUCT_TEST = ["AR", "CT", "DE", "IA", "ID", "MO", "NC", "NE", "NJ", "NV", "PA", "WA"]


def split():
    import sample as S
    out = {s: "dev" for s in GEN_STATES}
    out.update({s: "test" for s in STRUCT_TEST})
    new = []
    for i, reg in enumerate(sorted(S.REGIONS)):
        pool = sorted(s for s in S.REGIONS[reg] if s not in out)
        random.Random(SEED + i).shuffle(pool)
        k = math.ceil(len(pool) / 2)
        for j, s in enumerate(pool):
            out[s] = "test" if j < k else "dev"
            new.append(s)
    return dict(seed=SEED, states=dict(sorted(out.items())), new_states=sorted(new))


def select(per_state=5):
    import sample as S
    sp = split()
    have = {c["osm"] for c in json.load(open(os.path.join(CD, "generalize", "sample.json")))["courses"]}
    have |= {c["osm"] for c in json.load(open(os.path.join(CD, "structure", "sets.json")))["courses"]}
    used = set()
    out = []
    srcs = [(st, os.path.join(SURVEYS, f"survey_{st}.json"), True) for st in sp["new_states"]]
    srcs += [(st, os.path.join(CD, "generalize", "surveys", f"survey_{st}.json"), False) for st in GEN_STATES]
    missing = []
    for st, path, is_new in srcs:
        if not os.path.exists(path):
            missing.append(st)
            continue
        sv = json.load(open(path))
        pop = sorted([r for r in sv["courses"] if S.eligible(r) and r["osm"] not in have and r["tier"] == "full"],
                     key=lambda r: r["osm"])
        rnd = random.Random(f"{SEED}-{st}")
        h = lambda r: r["counts"].get("hole", 0)                     # noqa: E731
        g = lambda r: r["counts"].get("green", 0)                    # noqa: E731
        h18 = [r for r in pop if 18 <= h(r) <= 22 and g(r) >= 17]
        h9 = [r for r in pop if 9 <= h(r) <= 11 and 8 <= g(r) <= 12]
        hbig = [r for r in pop if 27 <= h(r) <= 40]
        pick = [(r, 18) for r in rnd.sample(h18, min(per_state, len(h18)))] if is_new else []
        pick += [(r, 9) for r in rnd.sample(h9, min(1, len(h9)))]
        pick += [(r, 27) for r in rnd.sample(hbig, min(1, len(hbig)))]
        for r, kind in pick:
            out.append(dict(slug=S.slug_for(r, used), name=r["name"], state=st, osm=r["osm"], center=r["center"],
                            counts=r["counts"], kind=kind, region=S.region_of(st), split=sp["states"][st],
                            source="zero_tap"))
    json.dump(dict(seed=SEED, made_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), missing_surveys=missing,
                   courses=out), open(SELECTION, "w"), indent=1)
    from collections import Counter
    print(len(out), Counter((c["split"], c["kind"]) for c in out), "missing surveys:", missing)
    return out


def todo_courses():
    """Every course this workflow fetches for: the selection (all steps) + the structure sets (card, imagery)."""
    out = []
    if os.path.exists(SELECTION):
        out += json.load(open(SELECTION))["courses"]
    for c in json.load(open(os.path.join(CD, "structure", "sets.json")))["courses"]:
        out.append(dict(c, source="structure"))
    return out


def _w(path, obj, gz=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if gz:
        with gzip.open(path, "wt") as fh:
            json.dump(obj, fh, separators=(",", ":"))
    else:
        json.dump(obj, open(path, "w"), separators=(",", ":"))


def _r(path):
    if not os.path.exists(path):
        return None
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return json.load(fh)


def course_files(c):
    """(course.json path, osm path) for a todo course: structure courses keep their committed files."""
    if c.get("source") == "structure":
        d = os.path.join(CD, "structure", "data", c["slug"])
        return os.path.join(d, "course.json"), os.path.join(d, "osm.geojson.gz")
    d = os.path.join(DATA, c["slug"])
    return os.path.join(d, "course.json"), os.path.join(d, "osm.geojson.gz")


def fetch_one(c, what, missing_only=False):
    import fetch_package as fp
    import platform_common as pc
    out = os.path.join(DATA, c["slug"])
    raw = os.path.join(HERE, "work", c["slug"])
    os.makedirs(out, exist_ok=True)
    os.makedirs(raw, exist_ok=True)
    cpath, opath = course_files(c)
    log = dict(slug=c["slug"], seconds={})
    course, fc = _r(cpath), _r(opath)
    if "osm" in what and c.get("source") != "structure" and not (missing_only and course and fc):
        import resolve as rs
        sys.path.insert(0, os.path.join(CD, "structure"))
        import fetch as SF                                   # structure/fetch.py (its subset of OSM features)
        t0 = time.time()
        course = rs.resolve(c["name"], c["state"], osm=c["osm"], with_towns=False)
        if not course or course.get("status") != "ok":
            raise RuntimeError(f"resolve failed: {course and course.get('status')}")
        pc.write_json(cpath, course)
        fc, summ = fp.fetch_osm(course, raw)
        pc.write_json(os.path.join(raw, "summary.json"), summ)
        sub = SF.subset(fc)
        _w(opath, sub, gz=True)
        fc = sub
        log["seconds"]["osm"] = round(time.time() - t0, 1)
        log["holes"] = sum(1 for f in sub["features"] if f["properties"].get("golf") == "hole")
    if not course or not fc:
        raise RuntimeError("no course.json / osm file (run the osm step first)")
    if "card" in what and not (missing_only and os.path.exists(os.path.join(out, "scorecard.json"))):
        import scorecard as scm
        t0 = time.time()
        summ = _r(os.path.join(raw, "summary.json"))
        if not summ:
            summ = dict(holes=[])
            for f in fc["features"]:
                p = f["properties"]
                if p.get("golf") == "hole" and p.get("ref") and f["geometry"]["type"] == "LineString":
                    co = f["geometry"]["coordinates"]
                    L = sum(_hav(co[i], co[i + 1]) for i in range(len(co) - 1))
                    summ["holes"].append(dict(ref=p["ref"], length_yd=round(L / 0.9144)))
        req = dict(schema="request/1", kind="package", course=c["name"], state=c["state"], osm=c["osm"], tees="back")
        sw = fp.fetch_scorecards(req, course, summ, raw) or {}
        cards = [dict(source=k["source"], url=k.get("url"), card=scm.normalise(k["card"])) for k in sw.get("cards", [])]
        pick = scm.choose_card([(k["source"], k["card"], k.get("url")) for k in cards]) if cards else None
        pc.write_json(os.path.join(out, "scorecard.json"), dict(cards=cards, chosen=pick[0] if pick else None,
                                                                 tried=sw.get("tried")))
        log["seconds"]["card"] = round(time.time() - t0, 1)
        log["card"] = pick[0] if pick else None
    if "imagery" in what and not (missing_only and os.path.exists(os.path.join(out, "segment.geojson.gz"))):
        import run_course as RC
        t0 = time.time()
        work = os.path.join(HERE, "work", c["slug"])
        ok = fp.fetch_imagery(course, work)
        img = os.path.join(work, "imagery")
        if ok and os.path.exists(os.path.join(img, "naip_nir.tif")):
            n4 = os.path.join(work, "naip4_06m.tif")
            RC.naip4(img, n4)
            seg = RC.run_segment(n4, course.get("boundary"))
            _w(os.path.join(out, "segment.geojson.gz"), seg, gz=True)
            log["segment"] = len(seg["features"])
        dem = os.path.join(img, "dem.tif")
        if os.path.exists(dem):
            import package as pk
            lp = pk.load(os.path.join(CD, "tees", "lidar_pads.py"), "cdp_lidar_pads")
            _, _, greens = pk.osm_tee_inputs(fc)
            pads = lp.detect_pads(dem, greens=greens, lines=None)
            pc.write_json(os.path.join(out, "pads.json"), [dict(id=p["id"], centroid=p["centroid"], coords=[
                [round(x, 7), round(y, 7)] for x, y in p["coords"]], area_m2=p["area_m2"]) for p in pads])
            log["pads"] = len(pads)
        log["imagery_meta"] = (_r(os.path.join(img, "georef.json")) or {}).get("imagery")
        log["seconds"]["imagery"] = round(time.time() - t0, 1)
    prev = _r(os.path.join(out, "fetch_log.json")) or {}
    prev.update({k: v for k, v in log.items() if k != "seconds"})
    prev.setdefault("seconds", {}).update(log["seconds"])
    prev["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(prev, open(os.path.join(out, "fetch_log.json"), "w"), indent=1, default=str)
    print(json.dumps(log, default=str)[:600], flush=True)


def _hav(a, b):
    R = 6371008.8
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    dla, dlo = la2 - la1, math.radians(b[0] - a[0])
    h = math.sin(dla / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlo / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["split", "survey", "select", "fetch"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--what", default="osm,card")
    ap.add_argument("--source", default="", help="only courses of this source (zero_tap / structure)")
    ap.add_argument("--slugs", default="")
    ap.add_argument("--missing-only", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "split":
        sp = split()
        json.dump(sp, open(os.path.join(HERE, "state_split.json"), "w"), indent=1)
        print(json.dumps(sp))
    elif a.cmd == "survey":
        import sample as S
        for st in a.args:
            res = S.survey(st)
            os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
            json.dump(res, open(a.out, "w"))
            print(st, res["n_elements"])
    elif a.cmd == "select":
        select()
    else:
        what = set(a.what.split(","))
        todo = todo_courses()
        if a.source:
            todo = [c for c in todo if c.get("source") in a.source.split(",")]
        if a.slugs:
            todo = [c for c in todo if c["slug"] in a.slugs.split(",")]
        todo = [c for j, c in enumerate(todo) if j % a.of == a.chunk]
        bad = []
        for c in todo:
            try:
                fetch_one(c, what, a.missing_only)
            except Exception as e:                                 # noqa: BLE001
                traceback.print_exc()
                bad.append((c["slug"], repr(e)[:200]))
            time.sleep(1)
        print("done", len(todo), "failed:", bad)


if __name__ == "__main__":
    main()
