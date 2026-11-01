"""Build the pathroute v2 extra cache on top of a pathroute (v1) cache.

    python course_data/zero_tap/pathroute/prep.py  --cache C1 --split all
    python course_data/zero_tap/pathroute_v2/prep2.py --cache C1 --out C2 [--jobs 3]
"""
from __future__ import annotations

import argparse
import os
import pickle
import sys
import traceback
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute"), ZT]
import bench as B  # noqa: E402
import scene as S  # noqa: E402
import features2 as F2  # noqa: E402


def _props(fc, sc):
    by = {}
    for f in fc.get("features", []):
        p = f["properties"]
        by[f"{p.get('osm_type', 'x')}/{p.get('osm_id', '')}"] = p
    return dict(tees=[by.get(t["id"], {}) for t in sc.tees], greens=[by.get(g["id"], {}) for g in sc.greens])


def one(args):
    slug, c1, out = args
    o = os.path.join(out, slug + ".pkl")
    if os.path.exists(o):
        return slug, "cached"
    d = pickle.load(open(os.path.join(c1, slug + ".pkl"), "rb"))
    if d.get("error"):
        pickle.dump(dict(error=d["error"]), open(o, "wb"))
        return slug, "v1 error"
    try:
        row = next(r for r in B.courses() if r["slug"] == slug)
        x = B.inputs(row, "nocard")
        sc = S.Scene(x["fc"], x["course"])
        assert len(sc.tees) == len(d["tees"]) and len(sc.greens) == len(d["greens"])
        pr = _props(x["fc"], sc)
        hX2 = F2.hole2_feats(sc, d["hp"], pr)
        pp, pX = F2.tee_pairs(sc, pr)
        e = dict(hX2=hX2, tpp=pp, tpX=pX)
        if d.get("lab"):
            th = d["lab"]["tee_h"]
            e["tpy"] = [int(bool(th[a] & th[b])) for a, b in pp]
        pickle.dump(e, open(o, "wb"))
        return slug, "ok"
    except Exception:
        pickle.dump(dict(error=traceback.format_exc().splitlines()[-1]), open(o, "wb"))
        return slug, "ERR " + traceback.format_exc().splitlines()[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    slugs = [r["slug"] for r in B.courses() if os.path.exists(os.path.join(a.cache, r["slug"] + ".pkl"))]
    with Pool(a.jobs) as p:
        for slug, st in p.imap_unordered(one, [(s, a.cache, a.out) for s in slugs]):
            print(slug, st, flush=True)


if __name__ == "__main__":
    main()
