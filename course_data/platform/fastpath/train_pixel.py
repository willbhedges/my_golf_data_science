"""Train / evaluate the fast-path pixel classifier (fastscene.py): 6 classes from NAIP + canopy + DEM features.

  python3 train_pixel.py rows  --chm-root DIR --out ROWS.npz        # sample labelled pixels of the TRAIN courses
  python3 train_pixel.py fit   ROWS.npz [--out fastscene_model/]      # LightGBM multiclass -> model.txt + model.json
  python3 train_pixel.py eval  [--courses b20_...]                    # pixel + object scores on the TEST courses

Train: course_data/packages/* (42 courses, MO KS IA IL AR TX MT, OSM greens / tees / fairways / bunkers / water as
labels; Meta canopy fetched with fastpath/canopy.fetch into --chm-root). Test: the blind-loop tier A / B courses
(fastpath/cache/packages/b20_*: CA IA IL MA WA WI NC GA), never read for training or tuning. Labels are OSM, so
"right" means "agrees with OSM". Background rows only come from courses whose OSM fairways and tees are mapped
(unmapped fairways would be background labels on fairway pixels).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastscene as FS  # noqa: E402

CD = FS.CD
TRAIN_GLOB = os.path.join(CD, "packages", "*")
TEST = ["b20_crow_canyon", "b20_pheasant_ridge", "b20_chevy_chase", "b20_cedar_glen", "b20_kittansett",
        "b20_zintel_creek", "b20_at_cedar_creek", "b20_falls_village", "b20_maplewood", "b20_twisted_pine"]
PER_CLASS = {0: 25000, 1: 8000, 2: 6000, 3: 10000, 4: 5000, 5: 5000}


def osm_counts(fc):
    c = {}
    for f in fc["features"]:
        g = (f.get("properties") or {}).get("golf")
        if g and (f.get("geometry") or {}).get("type") in ("Polygon", "MultiPolygon"):
            c[g] = c.get(g, 0) + 1
    return c


def course_rows(pkg_dir, chm=None, rng=None, per_class=PER_CLASS):
    rng = rng or np.random.default_rng(0)
    fc = json.load(open(os.path.join(pkg_dir, "raw", "osm.geojson")))
    c = osm_counts(fc)
    st = FS.grid_stack(pkg_dir, chm=chm)
    F = FS.features_py(st)
    lab = FS.label_raster(st, fc)
    mask = FS.course_mask(st)
    n_green = c.get("green", 0)
    if n_green < 8:
        return None
    full = c.get("fairway", 0) >= 0.5 * n_green and c.get("tee", 0) >= n_green
    X, Y = [], []
    flat = lab.ravel()
    mflat = mask.ravel()
    for k, n in per_class.items():
        if k == 0 and not full:
            continue
        if k == 3 and c.get("fairway", 0) < 0.5 * n_green:
            continue
        idx = np.flatnonzero((flat == k) & mflat)
        if len(idx) > n:
            idx = rng.choice(idx, n, replace=False)
        if len(idx):
            X.append(F.reshape(F.shape[0], -1)[:, idx].T)
            Y.append(np.full(len(idx), k, np.int8))
    return np.vstack(X), np.concatenate(Y)


def cmd_rows(a):
    Xs, Ys, G = [], [], []
    for d in sorted(glob.glob(TRAIN_GLOB)):
        s = os.path.basename(d)
        chm = os.path.join(a.chm_root, s, "chm_meta.tif")
        if not os.path.exists(os.path.join(d, "imagery", "naip_rgb.tif")) or not os.path.exists(chm):
            continue
        t = time.time()
        r = course_rows(d, chm, np.random.default_rng(abs(hash(s)) % 2**32))
        if r is None:
            print(s, "skipped (OSM greens < 8)")
            continue
        Xs.append(r[0])
        Ys.append(r[1])
        G += [s] * len(r[1])
        print(s, len(r[1]), np.bincount(r[1], minlength=6).tolist(), round(time.time() - t, 1), "s", flush=True)
    np.savez_compressed(a.out, X=np.vstack(Xs), y=np.concatenate(Ys), g=np.array(G), features=np.array(FS.FEATURES))


PARAMS = dict(objective="multiclass", num_class=6, learning_rate=0.1, num_leaves=31, min_data_in_leaf=200,
              feature_fraction=0.8, bagging_fraction=0.7, bagging_freq=1, lambda_l2=1.0, verbose=-1, num_threads=4,
              seed=7, max_bin=63)
ROUNDS = 150


def cmd_fit(a):
    import lightgbm as lgb
    z = np.load(a.rows)
    X, y, g = z["X"], z["y"], z["g"]
    if a.extra:                                  # per-course row files (rows_<slug>.npz from more fetched courses)
        Xs, Ys, Gs = [X], [y], [g]
        for p in sorted(glob.glob(os.path.join(a.extra, "*.npz"))):
            e = np.load(p)
            if len(e["y"]):
                Xs.append(e["X"])
                Ys.append(e["y"])
                Gs.append(np.full(len(e["y"]), os.path.basename(p)[:-4]))
        X, y, g = np.vstack(Xs), np.concatenate(Ys), np.concatenate(Gs)
    if a.exclude:                                 # validation courses (held out for calibration)
        keep = ~np.isin(g, a.exclude)
        X, y, g = X[keep], y[keep], g[keep]
    bad = [c for c in set(g.tolist()) if not ((g == c) & (y == 1)).any()]      # labels failed to land (no greens)
    keep = ~np.isin(g, bad)
    X, y, g = X[keep], y[keep], g[keep]
    print("dropped (no green rows):", bad)
    # class weights: every class counts as much as the others in total
    w = np.ones(len(y), np.float32)
    cnt = np.bincount(y, minlength=6).astype(float)
    for k in range(6):
        if cnt[k]:
            w[y == k] = len(y) / (6 * cnt[k])
    w[y == 0] *= 2.0                       # background is most of a course: keep false positives down
    t = time.time()
    params = dict(PARAMS, learning_rate=a.lr, num_leaves=a.leaves)
    b = lgb.train(params, lgb.Dataset(X, y, weight=w, feature_name=list(FS.FEATURES)), a.rounds)
    os.makedirs(a.out, exist_ok=True)
    b.save_model(os.path.join(a.out, "model.txt"))
    imp = dict(zip(FS.FEATURES, b.feature_importance("gain").round(0).tolist()))
    json.dump(dict(schema="fastscene_pixel/1", id=time.strftime("px-%Y%m%d-%H%M"), classes=FS.CLASSES,
                   features=FS.FEATURES, params=params, rounds=a.rounds, rows=int(len(y)),
                   class_rows=np.bincount(y, minlength=6).tolist(), courses=sorted(set(g.tolist())),
                   seconds=round(time.time() - t, 1), gain=imp), open(os.path.join(a.out, "model.json"), "w"), indent=1)
    print("fit", len(y), "rows", round(time.time() - t, 1), "s ->", a.out)


def pixel_scores(P, lab, mask):
    """Per class IoU / precision / recall of argmax(P) vs the OSM label raster, inside mask, edges ignored."""
    pred = P.argmax(0)
    ok = mask & (lab >= 0)
    out = {}
    for k, c in enumerate(FS.CLASSES):
        if k == 0:
            continue
        t, p = (lab == k) & ok, (pred == k) & ok
        tp = float((t & p).sum())
        out[c] = dict(iou=round(tp / max((t | p).sum(), 1), 3), prec=round(tp / max(p.sum(), 1), 3),
                      rec=round(tp / max(t.sum(), 1), 3), true_px=int(t.sum()))
    return out


def cmd_eval(a):
    import evaluate_scene as ES
    model = FS.load_model(a.model) if a.model else FS.load_model()
    res = {}
    for s in a.courses or TEST:
        d = os.path.join(HERE, "cache", "packages", s)
        if not os.path.exists(os.path.join(d, "imagery", "naip_rgb.tif")):
            print(s, "no imagery")
            continue
        r = ES.score_course(d, model, impl=a.impl)
        res[s] = r
        print(s, json.dumps(r)[:900], flush=True)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    p = sp.add_parser("rows")
    p.add_argument("--chm-root", required=True)
    p.add_argument("--out", required=True)
    p = sp.add_parser("fit")
    p.add_argument("rows")
    p.add_argument("--out", default=FS.MODEL_DIR)
    p.add_argument("--extra")
    p.add_argument("--exclude", nargs="*")
    p.add_argument("--rounds", type=int, default=ROUNDS)
    p.add_argument("--lr", type=float, default=PARAMS["learning_rate"])
    p.add_argument("--leaves", type=int, default=PARAMS["num_leaves"])
    p = sp.add_parser("eval")
    p.add_argument("--courses", nargs="*")
    p.add_argument("--model")
    p.add_argument("--impl", default="py")
    p.add_argument("--out")
    a = ap.parse_args()
    dict(rows=cmd_rows, fit=cmd_fit, eval=cmd_eval)[a.cmd](a)
