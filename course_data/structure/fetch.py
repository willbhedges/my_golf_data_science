"""Evaluation data for course-structure inference (GitHub Actions: Overpass; never run locally).

  python course_data/structure/fetch.py states --seed 20261018         -> held-out states (none of the tuning ones)
  python course_data/structure/fetch.py survey TX --out work/survey_TX.json        (one job per state)
  python course_data/structure/fetch.py select work/survey_*.json --seed 20261018  -> sets.json
  python course_data/structure/fetch.py fetch --chunk 0 --of 6                     -> data/<slug>/

Sets (`sets.json`):
  dev      fully mapped courses from the generalize tuning states (CA GA IL KY MA ME MN MS NH UT WI WY), drawn
           from the committed surveys (course_data/generalize/surveys), excluding every course already in
           generalize/sample.json (routing v2's sets). The solver is tuned on these only.
  heldout  fully mapped courses from 12 *other* states (three per Census region, seeded), surveyed here. Never
           looked at while tuning: eval.py scores them once per solver version.
Per state: `per_state` 18-hole courses (18 <= golf=hole ways <= 22), plus one 9-hole and one 27/36-hole facility
when the state has them (reported separately).

Per course (`data/<slug>/`): course.json (resolve.py: name, boundary, bbox) and osm.geojson.gz: golf=* features,
the course boundary, buildings, car parks, paths / roads, water, woods (ODbL, (c) OpenStreetMap contributors).
The hole ways stay in the file (they are the truth); scene.py hides them and every ref before the solver sees it.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(CD, "platform"), os.path.join(CD, "generalize"), CD]

DATA = os.path.join(HERE, "data")
SETS = os.path.join(HERE, "sets.json")
TUNING_STATES = ["CA", "GA", "IL", "KY", "MA", "ME", "MN", "MS", "NH", "UT", "WI", "WY"]
KEEP = ("golf", "ref", "par", "name", "osm_id", "osm_type", "amenity", "service", "building", "leisure", "handicap",
        "dist", "distance", "length", "tee", "golf:tee", "colour", "color", "parking", "club", "landuse", "natural",
        "water", "waterway", "highway", "golf_cart", "motor_vehicle", "access", "surface", "footway", "shop",
        "sport", "golf:par", "golf:course", "barrier")


def heldout_states(seed):
    import sample as S
    rnd = random.Random(seed)
    out = []
    for reg in sorted(S.REGIONS):
        pool = [s for s in S.REGIONS[reg] if s not in TUNING_STATES]
        out += sorted(rnd.sample(pool, 3))
    return out


def select(paths, seed, per_state=5, dev_per_state=4):
    import sample as S
    import platform_common as pc
    smp = json.load(open(os.path.join(CD, "generalize", "sample.json")))
    have = {c["osm"] for c in smp["courses"]}
    used = set()
    gen = sorted(os.path.join(CD, "generalize", "surveys", f) for f in os.listdir(os.path.join(CD, "generalize", "surveys")))
    out = dict(seed=seed, made_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), courses=[])
    for split, files, k in (("dev", gen, dev_per_state), ("heldout", paths, per_state)):
        for f in files:
            sv = json.load(open(f))
            st = sv["state"]
            if (split == "dev") != (st in TUNING_STATES):
                continue
            pop = [r for r in sv["courses"] if S.eligible(r) and r["osm"] not in have and r["tier"] == "full"]
            pop.sort(key=lambda r: r["osm"])
            rnd = random.Random(f"{seed}-{split}-{st}")
            h18 = [r for r in pop if 18 <= r["counts"].get("hole", 0) <= 22 and r["counts"].get("green", 0) >= 17]
            h9 = [r for r in pop if 9 <= r["counts"].get("hole", 0) <= 11 and 8 <= r["counts"].get("green", 0) <= 12]
            hbig = [r for r in pop if 27 <= r["counts"].get("hole", 0) <= 40]
            pick = [(r, 18) for r in rnd.sample(h18, min(k, len(h18)))]
            if split == "heldout":
                pick += [(r, 9) for r in rnd.sample(h9, min(1, len(h9)))]
                pick += [(r, 27) for r in rnd.sample(hbig, min(1, len(hbig)))]
            for r, kind in pick:
                out["courses"].append(dict(slug=S.slug_for(r, used), name=r["name"], state=st, osm=r["osm"],
                                           center=r["center"], counts=r["counts"], split=split, kind=kind,
                                           region=S.region_of(st)))
    json.dump(out, open(SETS, "w"), indent=1)
    from collections import Counter
    print(Counter((c["split"], c["kind"]) for c in out["courses"]))
    return out


def subset(fc):
    keep = []
    for f in fc["features"]:
        p, g = f["properties"], f.get("geometry")
        if not g:
            continue
        ok = (p.get("golf") or p.get("leisure") == "golf_course" or p.get("amenity") == "parking" or
              p.get("building") or p.get("highway") or p.get("water") or p.get("waterway") or
              p.get("natural") in ("water", "wood", "tree_row", "scrub", "wetland", "tree", "sand", "beach") or
              p.get("landuse") in ("forest", "reservoir", "basin", "pond", "grass", "recreation_ground") or
              p.get("leisure") in ("pitch",) or p.get("barrier") in ("fence", "wall"))
        if p.get("highway") and g["type"] == "Point":
            ok = False
        if p.get("natural") == "tree" and g["type"] == "Point":
            ok = True
        if ok:
            keep.append(dict(type="Feature", geometry=dict(g, coordinates=_round(g["coordinates"])),
                             properties={k: v for k, v in p.items() if k in KEEP}))
    return dict(type="FeatureCollection", features=keep)


def _round(c):
    if isinstance(c, (int, float)):
        return round(c, 6)
    return [_round(x) for x in c]


def fetch_one(entry):
    import fetch_package as fp
    import platform_common as pc
    import resolve as rs
    out = os.path.join(DATA, entry["slug"])
    os.makedirs(out, exist_ok=True)
    raw = os.path.join(HERE, "work", entry["slug"])
    os.makedirs(raw, exist_ok=True)
    course = rs.resolve(entry["name"], entry["state"], osm=entry["osm"], with_towns=False)
    if not course or course.get("status") != "ok":
        raise RuntimeError(f"resolve failed: {course and course.get('status')}")
    pc.write_json(os.path.join(out, "course.json"), course)
    fc, _ = fp.fetch_osm(course, raw)
    sub = subset(fc)
    with gzip.open(os.path.join(out, "osm.geojson.gz"), "wt") as fh:
        json.dump(sub, fh, separators=(",", ":"))
    n_holes = sum(1 for f in sub["features"] if f["properties"].get("golf") == "hole")
    print(entry["slug"], "features", len(sub["features"]), "holes", n_holes, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["states", "survey", "select", "fetch"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--seed", type=int, default=20261018)
    ap.add_argument("--per-state", type=int, default=5)
    ap.add_argument("--dev-per-state", type=int, default=4)
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--missing-only", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "states":
        print(json.dumps(heldout_states(a.seed)))
    elif a.cmd == "survey":
        import sample as S
        for st in a.args:
            res = S.survey(st)
            os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
            json.dump(res, open(a.out, "w"))
            print(st, res["n_elements"])
    elif a.cmd == "select":
        select(a.args, a.seed, a.per_state, a.dev_per_state)
    else:
        sets = json.load(open(SETS))["courses"]
        todo = [c for j, c in enumerate(sets) if j % a.of == a.chunk]
        if a.missing_only:
            todo = [c for c in todo if not os.path.exists(os.path.join(DATA, c["slug"], "osm.geojson.gz"))]
        bad = []
        for c in todo:
            try:
                fetch_one(c)
            except Exception as e:                                 # noqa: BLE001
                traceback.print_exc()
                bad.append((c["slug"], repr(e)[:200]))
            time.sleep(2)
        print("failed:", bad)


if __name__ == "__main__":
    main()
