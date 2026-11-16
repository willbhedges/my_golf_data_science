"""joint routing: fit the hole / walk / start / end models on DETECTION-LIKE candidates (model_scene.pkl).

model_osm.pkl was fitted on complete OSM greens / tee boxes; a detected scene misses 15 % of greens and 30 % of tee
complexes and has false ones, which shifts every rank / neighbour feature (hole AUC 0.97 -> 0.91 on noisy oracle
scenes). Here the training candidates are the routing bench's oracle scenes (platform/fastpath/route_bench.py
oracle_scene: OSM objects with detection noise), built through route_scene.candidates exactly as routing sees them,
on the zero_tap bench DEV courses that are not in the generalize validation set (so the validation train split stays
clean for tuning and its test split clean for reporting), several noise seeds each.

    python3 course_data/zero_tap/joint/fit_scene.py [--seeds 3] [--procs 3]   -> joint/model_scene.pkl
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
CD = os.path.dirname(ZT)
FP = os.path.join(CD, "platform", "fastpath")
sys.path[:0] = [HERE, ZT, FP, os.path.join(CD, "platform")]
OUT = os.path.join(HERE, "model_scene.pkl")


def build(a):
    row, seed = a
    import bench as B
    import cands as C
    import feats as F
    import route_bench as RB
    import route_scene as RS
    fc = B._rd(row["files"]["osm"])
    t = B.truth(row["slug"])
    if not t or not t.get("holes"):
        return None
    sc = RB.oracle_scene(fc, seed=seed * 1000 + sum(map(ord, row["slug"])))
    try:
        co, _ = RS.candidates(RB.strip_golf(fc), sc, n_holes=row["kind"])
    except Exception:                                                # noqa: BLE001
        return None
    geo = F.geometry(co)
    hp, hx = F.hole_features(co, geo)
    wp, wx, W = F.walk_features(co, geo)
    return dict(row=row, co=co, geo=geo, hp=hp, hx=hx, wp=wp, wx=wx, kind=row["kind"], lab=C.label(co, t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--procs", type=int, default=3)
    a = ap.parse_args()
    import bench as B
    import models as M
    val = {c["slug"] for c in json.load(open(os.path.join(CD, "generalize", "validation_set.json")))["courses"]}
    rows = [r for r in B.courses("dev") if r["slug"] not in val and r["kind"] in (9, 18)]
    jobs = [(r, s) for s in range(a.seeds) for r in rows]
    from multiprocessing import Pool
    with Pool(a.procs) as pool:
        ds = [d for d in pool.map(build, jobs, chunksize=2) if d is not None]
    print("courses", len(rows), "instances", len(ds), flush=True)
    ms = M.fit(ds)
    pickle.dump(ms, open(OUT, "wb"))
    print("->", OUT, round(os.path.getsize(OUT) / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
