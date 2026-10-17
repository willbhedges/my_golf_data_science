"""Formation v2 on the zero-tap benchmark (course_data/zero_tap/BENCH.md): zero_tap_result/1 files per tier.

    python course_data/zero_tap/formation/bench_run.py --split dev --out course_data/zero_tap/results/formation_v2
    python course_data/zero_tap/bench.py score course_data/zero_tap/results/formation_v2/<tier> --split dev

Formation only: each result holds the N most confident MAP (green, tee complex) pairs of hole_pairs/1 (N = the
facility's hole count from the manifest when 9 / 18, else the card's); hole numbers are NOT inferred here (they are
1..N in an arbitrary order), so read the `formed` column, not `hole number` / `fully right`. `certain` is always
false. Unmapped tiers use the blind perception scene (skipped when the course has none).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ZT]
import bench as B                                                    # noqa: E402
import data as D                                                     # noqa: E402
import hole_pairs as HP                                              # noqa: E402
import scene as S                                                    # noqa: E402  (structure/scene.py)

TIERS = ("nocard", "osm_card", "unmapped_nocard", "unmapped_card")


def run_one(row, tier, version):
    inp = B.inputs(row, tier)
    if tier.startswith("unmapped"):
        obj = inp.get("scene") or D.perception_scene_obj(row["slug"])      # + blind scenes built for this study
        if not obj:
            return None
        sc = S.scene_from_perception(obj)
    else:
        sc = S.scene_from_osm(inp["fc"], (inp.get("course") or {}).get("boundary"))
    aux = os.path.join(D.INPUTS, row["slug"], "aux.npz")
    hp = HP.hole_pairs(sc, inp.get("card"), aux if os.path.exists(aux) else None, slug=row["slug"])
    N = row.get("kind") if row.get("kind") in (9, 18) else None
    if N is None and inp.get("card"):
        _, Y, _ = D.card_sets(inp["card"])
        N = len(Y) if Y is not None else None
    m = sorted(hp["map"], key=lambda h: -h["p_corridor"])
    if N:
        m = m[:N]
    holes = [dict(number=i + 1, par=None, green_ll=h["green_ll"], tee_ll=h["tee_ll"], tee_boxes_ll=h["tee_boxes_ll"],
                  green_id=h["green"], tee_id=h["tee"], confidence=h["p_corridor"]) for i, h in enumerate(m)]
    conf = float(np.prod([h["confidence"] for h in holes])) if holes else 0.0
    return dict(schema="zero_tap_result/1", method="formation_v2", version=version, tier=tier, slug=row["slug"],
                card_kind=inp.get("card_kind"), certain=False, confidence=round(conf, 6), holes=holes, error=None,
                note="formation only: hole numbers are arbitrary")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    ap.add_argument("--tiers", default=",".join(TIERS))
    ap.add_argument("--out")
    ap.add_argument("--version", default="formation-v2")
    ap.add_argument("--strip-rows", help="drop per-course rows from the bench.py score jsons in this dir")
    a = ap.parse_args()
    if a.strip_rows:
        for f in sorted(os.listdir(a.strip_rows)):
            p = os.path.join(a.strip_rows, f)
            o = json.load(open(p))
            o.pop("rows", None)
            json.dump(o, open(p, "w"), indent=1)
            print(f, {sp: (o[sp]["formed_acc"], o[sp]["n"]) for sp in ("dev", "test") if o.get(sp)})
        return
    rows = B.courses(a.split)
    t0 = time.time()
    for tier in a.tiers.split(","):
        od = os.path.join(a.out, tier)
        n = 0
        for row in rows:
            try:
                res = run_one(row, tier, a.version)
            except Exception as e:                                   # noqa: BLE001
                traceback.print_exc()
                res = dict(schema="zero_tap_result/1", method="formation_v2", version=a.version, tier=tier,
                           slug=row["slug"], certain=False, confidence=0.0, holes=[], error=repr(e)[:300])
            if res is None:
                continue
            B.write_result(res, od)
            n += 1
        print(tier, n, "courses", round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
