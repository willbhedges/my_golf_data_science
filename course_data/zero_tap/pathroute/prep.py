"""Build and cache per-course pathroute features (+ dev-only labels from truth).

    python course_data/zero_tap/pathroute/prep.py --cache DIR [--split dev|test|all] [--jobs 4]
"""
from __future__ import annotations

import argparse
import os
import pickle
import sys
import time
import traceback
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ZT]
import bench as B  # noqa: E402
import scene as S  # noqa: E402
import features as F  # noqa: E402


def labels(sc, t):
    """Truth labels for a DEV course: tee -> set(true hole idx), green -> true hole idx, and next-hole map."""
    M = B.Matcher(t)
    # our frame and the matcher's frame differ: go through lon/lat
    def ll(p):
        return sc.pj.inv(*p)
    tee_h = []
    for tt in sc.tees:
        pts = [M.pj.fwd(*ll(tt["c"]))]
        tee_h.append({j for j in range(len(M.holes)) if M.tee_ok(j, pts)})
    green_h = []
    for g in sc.greens:
        p = M.pj.fwd(*ll(g["c"]))
        js = [j for j in range(len(M.holes)) if M.green_ok(j, p)]
        green_h.append(js[0] if js else None)
    hs = t["holes"]
    nxt = {}
    for j, h in enumerate(hs):
        for k, h2 in enumerate(hs):
            if h2.get("course") == h.get("course") and h2["ref"] == h["ref"] + 1:
                if t["kind"] == 36 and h.get("course") is None and abs(k - j) != 1:
                    continue
                nxt[j] = k
    refs = [h["ref"] for h in hs]
    return dict(tee_h=tee_h, green_h=green_h, nxt=nxt, refs=refs, N=t["n_holes"])


def one(args):
    row, cache = args
    out = os.path.join(cache, row["slug"] + ".pkl")
    if os.path.exists(out):
        return row["slug"], "cached"
    t0 = time.time()
    try:
        x = B.inputs(row, "nocard")
        sc = S.Scene(x["fc"], x["course"])
        hp, hX = F.hole_feats(sc)
        tp, tX = F.trans_feats(sc)
        cT, cG = F.club_feats(sc)
        lab = labels(sc, B.truth(row["slug"])) if row["split"] == "dev" else None
        d = dict(slug=row["slug"], split=row["split"], kind=row["kind"], hp=hp, hX=hX, tp=tp, tX=tX, cT=cT, cG=cG,
                 lab=lab, club_src=sc.club_src, n_nodes=len(sc.nodes),
                 greens=[dict(id=g["id"], ll=sc.pj.inv(*g["c"]), r=g["r"]) for g in sc.greens],
                 tees=[dict(id=tt["id"], ll=sc.pj.inv(*tt["c"]), c=tt["c"], ax=tt["ax"], L=tt["L"]) for tt in sc.tees],
                 gc=sc.gc, tc=sc.tc, club=sc.club)
        pickle.dump(d, open(out, "wb"))
        return row["slug"], f"ok {time.time() - t0:.1f}s"
    except Exception as e:
        pickle.dump(dict(slug=row["slug"], split=row["split"], kind=row["kind"], error=repr(e)), open(out, "wb"))
        return row["slug"], "ERR " + traceback.format_exc().splitlines()[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--split", default="dev")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    rows = B.courses(None if a.split == "all" else a.split)
    with Pool(a.jobs) as p:
        for slug, st in p.imap_unordered(one, [(r, a.cache) for r in rows]):
            print(slug, st, flush=True)


if __name__ == "__main__":
    main()
