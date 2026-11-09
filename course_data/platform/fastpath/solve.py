"""Fast strategy solve of a course package: product/decide quick mode (prior-mean point estimate, common random
numbers) on every tee-shot hole, holes in parallel.

  python3 solve.py <package.json> [--set NAME] [--n 2000] [--workers 4] [--out decision.json]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
sys.path.insert(0, PLAT)
import error_budget as EB  # noqa: E402  (puts product/ + mozingo/ on the path, takes platform/ off it)


_RASTER = {}
RASTER_SCALE = 2.0          # raster cells per model pixel (the model frame is ~3.4-4.4 px / yd: a cell is ~0.13 yd)


def raster_lie_at(h, pts):
    """tee_strategy.lie_at from a label raster of the hole's zone stack (later zone wins, as lie_at): one lookup per
    point instead of one polygon test per zone. Built once per hole; points off the raster are rough."""
    import cv2
    import numpy as np
    key = id(h["zones"])
    R = _RASTER.get(key)
    if R is None or R[0] is not h["zones"]:
        names = ["rough"]
        polys = [(nm, np.asarray(pl, float)) for nm, pl in h["zones"] if len(pl) >= 3]
        if polys:
            lo = np.min([p.min(0) for _, p in polys], axis=0) - 2
            hi = np.max([p.max(0) for _, p in polys], axis=0) + 2
        else:
            lo, hi = np.zeros(2), np.ones(2)
        lo = np.maximum(lo, -4000)
        hi = np.minimum(hi, 6000)
        W, H = int((hi[0] - lo[0]) * RASTER_SCALE) + 1, int((hi[1] - lo[1]) * RASTER_SCALE) + 1
        lab = np.zeros((H, W), np.uint8)
        for nm, P in polys:
            if nm not in names:
                names.append(nm)
            q = np.round((P - lo) * RASTER_SCALE * 16).astype(np.int32)       # 1/16-cell vertices (shift=4)
            cv2.fillPoly(lab, [q.reshape(-1, 1, 2)], names.index(nm), lineType=cv2.LINE_8, shift=4)
        R = _RASTER[key] = (h["zones"], lo, lab, np.array(names, dtype=object))
    _, lo, lab, names = R
    pts = np.asarray(pts, float)
    c = np.round((pts[:, 0] - lo[0]) * RASTER_SCALE).astype(np.int64)
    r = np.round((pts[:, 1] - lo[1]) * RASTER_SCALE).astype(np.int64)
    ok = (c >= 0) & (r >= 0) & (c < lab.shape[1]) & (r < lab.shape[0])
    out = np.zeros(len(pts), np.int64)
    out[ok] = lab[r[ok], c[ok]]
    return names[out]


def use_raster():
    import tee_strategy as t
    t.lie_at = raster_lie_at


def solve(pkg_path, tee_set=None, n=2000, workers=4, raster=True):
    t0 = time.time()
    pkg = json.load(open(pkg_path))
    S = tee_set or pkg.get("tee_set")
    C = EB.PK().load(pkg_path, S)
    holes = C.holes
    t1 = time.time()
    import decide
    use_raster() if raster else EB.use_fast_lie_at()
    res = decide.run(dict(holes), "quick", workers=workers, log=lambda *a: None, n=n) if holes else {}
    out = {}
    for k, v in res.items():
        out[str(k)] = dict(pick=v["pick"], aim=round(v["aim"], 1), ev=round(v["ev"], 4), runner=v["runner"],
                           margin=round(v["margin"], 4), tie=bool(v["tie"]), check=v.get("check") or [],
                           approach=round(v["clubs"][v["pick"]]["approach"], 1),
                           share={a: round(b, 3) for a, b in v["clubs"][v["pick"]]["share"].items() if b >= 0.005},
                           length=holes[k].get("length"), par=holes[k].get("par"),
                           evs={c: round(r["ev"], 4) for c, r in v["clubs"].items()},
                           aims={c: round(r["aim"], 1) for c, r in v["clubs"].items()})
    return dict(set=S, n=n, holes=out, seconds=dict(load=round(t1 - t0, 2), solve=round(time.time() - t1, 2)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--set")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out")
    ap.add_argument("--exact", action="store_true", help="polygon tests instead of the lie raster (cross-check)")
    a = ap.parse_args()
    d = solve(a.package, a.set, a.n, a.workers, raster=not a.exact)
    json.dump(d, open(a.out, "w"), indent=1) if a.out else None
    print(json.dumps(d["seconds"]), len(d["holes"]), "tee shots")
