"""Course list for the national U-Net training set (v2): well-mapped OSM courses from all lower-48 states, drawn
from the national course index (course_data/library/us_courses.json.gz), with every evaluation course kept out.

    python course_data/segment/train/pick_v2.py [--per-state 45] [--n 1500]
        -> course_data/segment/train/v2_courses.json (committed; build_dataset.py --courses reads it on Actions)

Run locally (it needs the routing side's TRAIN-BIG manifest, cache/big/manifest.json, which is not committed).

Exclusions (osm id, and anything whose centre is within 1.5 km of one of them: other courses of one facility):
  * every generalize validation-set course (train and test: the routing bench and perception VAL / TEST-40),
  * the blind-loop list (blind20.json, which holds TEST-40's b20 courses),
  * the perception stacks_meta pool (perception TRAIN), the three segment evaluation courses,
  * every TRAIN-BIG course in the manifest, built or not (the routing models are fitted on their scenes).
The v1 U-Net index (IA / MO) is allowed: those courses are outside every evaluation set already.

Label filter (index counts; build_dataset.py checks bunkers / areas again on the real polygons): an outline, not
closed, not a node, holes 9 / 18 / 27 / 36, greens >= holes, tees >= holes, fairways >= 0.6 x holes. Drawn per state
(seeded), at most --per-state each, interleaved so a cap keeps every state; courses within 1 km of a drawn one are
skipped (one facility, one course).
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = os.path.dirname(HERE)
CD = os.path.dirname(SEG)
FP = os.path.join(CD, "platform", "fastpath")
sys.path[:0] = [FP, os.path.join(CD, "platform"), os.path.join(CD, "generalize")]
SEED = 20261118
OUT = os.path.join(HERE, "v2_courses.json")
LOWER48_NOT = {"AK", "HI", "PR", "GU", "VI", "AS", "MP"}
SEG_EVAL = {"relation/13353211", "way/44804299", "way/385067034"}      # Spirit Hollow, Veenker, Mozingo Lake


def hav_m(a, b):
    k = math.cos(math.radians((a[1] + b[1]) / 2))
    return math.hypot((a[0] - b[0]) * k, a[1] - b[1]) * 111320.0


def exclusions():
    """(ids, centres [lon, lat], counts by source)"""
    import route_big as RB
    ids, cen = set(), []
    n = {}
    # validation set (train + test)
    vs = json.load(open(os.path.join(CD, "generalize", "validation_set.json")))["courses"]
    for c in vs:
        ids.add(c["osm"])
        p = os.path.join(os.path.dirname(CD), c["dir"], "course.json")
        if os.path.exists(p) and json.load(open(p)).get("center"):
            cen.append(json.load(open(p))["center"])
    n["validation_set"] = len(vs)
    b20 = json.load(open(os.path.join(CD, "platform", "blind20", "blind20.json")))["courses"]
    for c in b20:
        ids.add(c["osm"])
        cen.append([c["lon"], c["lat"]])
    n["blind20"] = len(b20)
    k = 0
    for p in glob.glob(os.path.join(CD, "perception", "stacks_meta", "*.json")):
        c = (json.load(open(p)).get("course") or {})
        o = c.get("osm")
        if isinstance(o, dict):
            ids.add(f"{o.get('type')}/{o.get('id')}")
        if c.get("center"):
            cen.append(c["center"])
        k += 1
    n["perception_stacks_meta"] = k
    ids |= SEG_EVAL
    man = json.load(open(RB.MANIFEST))["courses"]
    for c in man:
        ids.add(c["osm"])
        cen.append([c["lon"], c["lat"]])
    n["train_big_manifest"] = len(man)
    # the heldout sets as perc_bench reads them (TEST-40 / VAL / TRAIN): same sources, checked for completeness
    import heldout
    for split, es in heldout.sets().items():
        for e in es:
            try:
                c = heldout.course_dict(e)
            except Exception:                                  # noqa: BLE001
                continue
            o = c.get("osm")
            if o:
                ids.add(heldout._osm_id(o))
            if c.get("center"):
                cen.append(c["center"])
        n[f"heldout_{split}"] = len(es)
    # locally fetched heldout packages (the b20 TEST packages carry their own course.json)
    for p in glob.glob(os.path.join(FP, "cache", "heldout", "*", "raw", "course.json")) + \
            glob.glob(os.path.join(FP, "cache", "packages", "b20_*", "raw", "course.json")):
        c = json.load(open(p))
        if c.get("osm"):
            ids.add(heldout._osm_id(c["osm"]))
        if c.get("center"):
            cen.append(c["center"])
    return ids, cen, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-state", type=int, default=45)
    ap.add_argument("--n", type=int, default=1500)
    a = ap.parse_args()
    import sample as SM
    ids, cen, nex = exclusions()
    d = json.load(gzip.open(os.path.join(CD, "library", "us_courses.json.gz"), "rt"))
    F = d["fields"]
    by = {}
    drop = dict(excluded_id=0, near_excluded=0, filter=0)
    for row in d["rows"]:
        r = dict(zip(F, row))
        if r["state"] in LOWER48_NOT or not r["outline"] or r["closed"] or r["osm"].startswith("node/"):
            drop["filter"] += 1
            continue
        h = r["osm_holes"] if r["osm_holes"] in (9, 18, 27, 36) else r["holes"]
        if h not in (9, 18, 27, 36) or (r["greens"] or 0) < h or (r["tees"] or 0) < h or (r["fairways"] or 0) < 0.6 * h:
            drop["filter"] += 1
            continue
        if not SM.eligible(dict(name=r["name"], osm=r["osm"], area_ha=99.0, tags={})):
            drop["filter"] += 1
            continue
        if r["osm"] in ids:
            drop["excluded_id"] += 1
            continue
        if any(hav_m([r["lon"], r["lat"]], c) < 1500 for c in cen):
            drop["near_excluded"] += 1
            continue
        by.setdefault(r["state"], []).append(dict(r, holes_used=h))
    rnd = random.Random(SEED)
    for s in sorted(by):
        by[s].sort(key=lambda r: r["osm"])
        rnd.shuffle(by[s])
    out, cen2 = [], []
    taken = {s: 0 for s in by}
    while len(out) < a.n and any(by.values()):
        for s in sorted(by):
            while by[s] and taken[s] < a.per_state:
                r = by[s].pop(0)
                c = [r["lon"], r["lat"]]
                if any(hav_m(c, q) < 1000 for q in cen2):
                    continue
                cen2.append(c)
                out.append(dict(osm=r["osm"], name=r["name"], state=s, lon=r["lon"], lat=r["lat"], holes=r["holes_used"],
                                greens=r["greens"], tees=r["tees"], fairways=r["fairways"]))
                taken[s] += 1
                break
            else:
                by[s] = []
            if len(out) >= a.n:
                break
    states = {}
    for r in out:
        states[r["state"]] = states.get(r["state"], 0) + 1
    json.dump(dict(schema="segment_v2_courses/1", seed=SEED, per_state=a.per_state, source="library/us_courses.json.gz",
                   exclusions=dict(sources=nex, ids=len(ids), centres=len(cen), buffer_m=1500),
                   dropped=drop, n=len(out), states=states, courses=out), open(OUT, "w"), indent=0)
    print(len(out), "courses,", len(states), "states", drop, nex)
    print(states)


if __name__ == "__main__":
    main()
