"""Score a fast-path perception scene against OSM (the course's own polygons are the truth; never a detector input).

    python3 evaluate_scene.py b20_crow_canyon [...]          # pixel IoU per class + perception/evaluate.py objects

Object metrics are perception/evaluate.py's (the numbers in perception/REPORT.md): hole greens precision / recall
(match within GREEN_MATCH_M), tee complexes (recall at OSM hole-line starts, 30 m), fairways / bunkers / water
(30 % overlap). Only elements OSM maps completely enough are counted (evaluate.py's `eligible`).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastscene as FS  # noqa: E402

KEYS = ("greens_hole", "greens_any", "tee_complexes", "tee_boxes", "fairways", "bunkers", "water")


def score_course(pkg_dir, model=None, impl="py", paths=False, P=None, keep_D=False):
    """P: precomputed U-Net probabilities (perc_bench.py caches them); keep_D: also return the detections"""
    import train_pixel as TP
    fc = json.load(open(os.path.join(pkg_dir, "raw", "osm.geojson")))
    sc, info = FS.build(pkg_dir, model, out=False, impl=impl, paths=paths, labels=fc, P=P)
    st, D, P = info["stack"], info["D"], info["P"]
    lab = FS.label_raster(st, fc)
    mask = FS.course_mask(st)
    out = dict(pixel=TP.pixel_scores(P, lab, mask), seconds=info["seconds"], summary=sc.get("summary"))
    with FS.perception_ns():
        import evaluate as EV
        import truth as TR
        T = TR.Truth(st)
        ev = EV.evaluate(st, None, D, T)
    for k in KEYS:
        v = ev.get(k) or {}
        out[k] = {kk: v.get(kk) for kk in ("precision", "recall", "tp_pred", "n_pred", "tp_true", "n_true", "eligible")
                  if kk in v}
    out["mapped_holes"] = ev.get("mapped_holes")
    if keep_D:
        out["_D"], out["_st"], out["_T"] = D, st, T
    return out


def pooled(res, key):
    """Pooled precision / recall over the eligible courses (perception REPORT.md convention)."""
    tp_p = n_p = tp_t = n_t = 0
    n = 0
    for r in res.values():
        v = r.get(key) or {}
        if not v.get("eligible"):
            continue
        n += 1
        tp_p += v.get("tp_pred") or 0
        n_p += v.get("n_pred") or 0
        tp_t += v.get("tp_true") or 0
        n_t += v.get("n_true") or 0
    return dict(courses=n, precision=round(tp_p / max(n_p, 1), 3), recall=round(tp_t / max(n_t, 1), 3))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("courses", nargs="+")
    ap.add_argument("--model")
    ap.add_argument("--out")
    a = ap.parse_args()
    model = FS.load_model(a.model) if a.model else None
    res = {}
    for s in a.courses:
        d = s if os.path.isdir(s) else os.path.join(HERE, "cache", "packages", s)
        res[os.path.basename(s.rstrip("/"))] = r = score_course(d, model)
        print(s, json.dumps({k: r[k] for k in KEYS}, default=float)[:900], flush=True)
    pool = {k: pooled(res, k) for k in KEYS}
    for k in KEYS:
        print(k, pool[k])
    if a.out:
        json.dump(dict(courses=res, pooled=pool), open(a.out, "w"), indent=1, default=float)
