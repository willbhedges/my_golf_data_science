"""Long-grass + tree-edge model v2 for any course: train / evaluate / infer (runs on GitHub Actions).

  python course_data/vision_any/v2_model.py --eval            # LOHO on Spirit Hollow + Mozingo, cross-course,
                                                               # v1 vs v2 tables, strategy impact, model_v2/
  python course_data/vision_any/v2_model.py --infer spirit_hollow mozingo veenker [--integrate auto]

Labels: hand maps (v2_labels): Spirit Hollow hand_zones_ll.json (GPS, hand-checked), Mozingo tee_strategy.HOLES
registered by register_mozingo.py. Features: v2_features (multi-year NAIP, texture, lidar point statistics,
terrain, distances to OSM turf, canopy edge), all relative to each course's own mown turf.

Native (long grass): LightGBM (sklearn HistGradientBoosting if lightgbm is missing), native vs mown/rough
cells of the hand map (trees, water, sand, OB excluded), boundary cells dropped. Probability smoothed 3x3,
threshold, opened 1 m / closed 2 m, >= 150 yd2, never on canopy / water / OSM turf / bunkers / roads.
Trees: lidar canopy (HAG > h) with a learned edge buffer k m (negative = erode toward the trunks) and a
minimum clump area, chosen to maximise agreement with the golfer's "trees" line; a LightGBM tree classifier
on the same features is the alternative, kept only if it beats the buffer rule out of sample.

Evaluation (every number out of sample):
  * leave-one-HOLE-out within a course (groups = hole ref; 2B/2F one group); training cells inside the held-out
    hole's footprint + 20 m are dropped (adjacent holes share tree lines); thresholds / buffers for hole h are
    chosen on the other holes' out-of-fold results;
  * cross-course: train on all of one course, apply with that course's chosen settings to the other;
  * landing corridors: 190-335 yds along the tee line, +/-55 yds, 1 m cells inside the screenshot footprint;
    `composed` = the hand map with its trees + native replaced by the model's (fairway / first cut / water /
    sand / OB stay as traced) - what tee_strategy would see; `raw` = the layer alone;
  * edges: for every 5 yds from 190 to 335 and each side, the first lateral distance (0-55 yds, 1-yd steps) at
    which the class starts, hand vs model; agree = both absent or within 5 yds;
  * decision impact: evaluate.strategy_impact (best club / aim for Driver, 2-wood, 4-wood) on the hand map vs the
    hand map with trees + native replaced by v1 / v2 / nothing (OSM-only).
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import layers as L                                           # noqa: E402
import v2_labels as LB                                       # noqa: E402

YD = 0.9144
MODEL_DIR = os.path.join(HERE, "model_v2")
MODEL_ID = "vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)"
THRS = np.round(np.r_[np.arange(0.04, 0.20, 0.02), np.arange(0.20, 0.951, 0.05)], 2)
TREE_K = [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 8, 10, 12]
TREE_AREA = [30, 100, 250]
TREE_HAG = [2.5, 4.0]
EXCL_M = 20
N_PER_CLASS = 70000
EVAL_COURSES = ("spirit_hollow", "mozingo")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# =========================================================================== data
def prepare(slug, course_dir=None):
    import run_any as RA
    import v2_features as VF
    t0 = time.time()
    cdir = course_dir or RA.course_dir_for(slug)
    S = VF.load_stack(slug, cdir)
    fc = json.load(open(os.path.join(cdir, "osm.geojson")))
    M, Ly = L.osm_masks(S, fc)
    canopy = {}
    how = None
    for h in TREE_HAG:
        canopy[h], hw, _ = L.tree_mask(S, M, hag_min=h, min_area_m2=10.0)
        how = how or hw
    F = VF.Features(S, M, canopy[2.5])
    water0, _ = L.water_mask(S, Ly, M)
    import native as N
    elig = N.eligible(S, M, canopy[2.5], water0)
    # relaxed: long grass may run under / up to scattered canopy (the golfer's native line often does)
    elig_rel = N.eligible(S, M, np.zeros_like(canopy[2.5]), water0)
    course = M["course"] if M["course"].any() else np.ones_like(elig)
    course = ndimage.binary_dilation(course, L.disk(30))
    log(f"[{slug}] prepared {len(F.names)} features in {time.time() - t0:.0f}s")
    return dict(slug=slug, S=S, M=M, Ly=Ly, fc=fc, canopy=canopy, trees_how=how, F=F, water0=water0, elig=elig,
                elig_rel=elig_rel,
                course=course, cdir=cdir)


def crop_box(m, pad):
    r, c = np.nonzero(m)
    return (slice(max(r.min() - pad, 0), r.max() + pad + 1), slice(max(c.min() - pad, 0), c.max() + pad + 1))


def hole_data(D):
    """Per hole: cropped label rasters + training cells (flat global indices)."""
    S = D["S"]
    holes = []
    for h in LB.load_holes(D["slug"]):
        r = LB.rasterize_hole(S, h)
        if not r["foot"].any():
            continue
        sl = crop_box(r["foot"], 40)
        cls = r["cls"][sl]
        tm = LB.train_mask(cls)
        rr, cc = np.nonzero(tm)
        gidx = (rr + sl[0].start) * S.W + (cc + sl[1].start)
        excl = ndimage.binary_dilation(r["foot"][sl], L.disk(EXCL_M))
        holes.append(dict(h=h, key=h["key"], ref=h["ref"], sl=sl, cls=cls, foot=r["foot"][sl], corr=r["corr"][sl],
                          along=r["along"][sl], lat=r["lat"][sl], tidx=gidx, tcls=cls[tm], excl=excl))
    log(f"[{D['slug']}] {len(holes)} labelled holes, {sum(len(x['tidx']) for x in holes)} training cells")
    return holes


def excluded(D, holes, ref):
    """Flat indices (bool over the grid) of cells near the held-out ref's footprints."""
    S = D["S"]
    m = np.zeros((S.H, S.W), bool)
    for x in holes:
        if x["ref"] == ref:
            m[x["sl"]] |= x["excl"]
    return m.ravel()


def task_xy(holes, task, skip=None, flat_excl=None):
    """Training (idx, y) for 'native' or 'trees', deduplicated over overlapping footprints."""
    idx, y = [], []
    for x in holes:
        if skip is not None and x["ref"] == skip:
            continue
        c = x["tcls"]
        if task == "native":
            pos = c == LB.CI["native"]
            neg = np.isin(c, [LB.CI["rough"], LB.CI["first_cut"], LB.CI["fairway"]])
        else:
            pos = c == LB.CI["recovery"]
            neg = (c >= 0) & (c != LB.CI["recovery"]) & (c != LB.CI["ob"])
        keep = pos | neg
        idx.append(x["tidx"][keep])
        y.append(pos[keep].astype(np.int8))
    idx, y = np.concatenate(idx), np.concatenate(y)
    idx, first = np.unique(idx, return_index=True)
    y = y[first]
    if flat_excl is not None:
        k = ~flat_excl[idx]
        idx, y = idx[k], y[k]
    return idx, y


def balanced(idx, y, n=N_PER_CLASS, seed=0):
    R = np.random.default_rng(seed)
    out = []
    for v in (0, 1):
        j = np.flatnonzero(y == v)
        out.append(R.choice(j, min(n, len(j)), replace=False) if len(j) else j)
    j = np.concatenate(out)
    return idx[j], y[j]


# =========================================================================== model
def make_clf():
    try:
        import lightgbm as lgb
        return lgb.LGBMClassifier(n_estimators=400, learning_rate=0.05, num_leaves=31, min_child_samples=100,
                                  subsample=0.8, subsample_freq=1, colsample_bytree=0.7, reg_lambda=1.0,
                                  n_jobs=4, verbose=-1, random_state=0)
    except ImportError:
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_leaf_nodes=31,
                                              l2_regularization=1.0, random_state=0)


def usable_names(Ds, names):
    """Features with information on every course used (not all-NaN, not constant)."""
    out = []
    for n in names:
        ok = True
        for D in Ds:
            v = D["F"].get(n)
            f = np.isfinite(v)
            if f.mean() < 0.05 or np.nanstd(v[f][::97]) < 1e-6:
                ok = False
        if ok:
            out.append(n)
    return out


def fit(parts, names):
    """parts: [(D, idx, y)] -> fitted classifier."""
    X = np.concatenate([D["F"].matrix(i, names) for D, i, _ in parts])
    y = np.concatenate([yy for _, _, yy in parts])
    clf = make_clf()
    clf.fit(X, y)
    return clf


def predict_grid(D, clf, names, region):
    """P(class) on cells of a bool region (full-grid), NaN elsewhere -> float32 grid."""
    S = D["S"]
    p = np.full(S.H * S.W, np.nan, np.float32)
    j = np.flatnonzero(region.ravel())
    for i in range(0, len(j), 300000):
        k = j[i:i + 300000]
        p[k] = clf.predict_proba(D["F"].matrix(k, names))[:, 1]
    return p.reshape(S.H, S.W)


def native_mask(p, elig, thr, res=1.0):
    """Post-processing shared by evaluation and the product (p, elig: same-shape arrays)."""
    ps = ndimage.uniform_filter(np.nan_to_num(p), 3)
    m = (ps >= thr) & elig
    m = ndimage.binary_opening(m, L.disk(1))
    m = ndimage.binary_closing(m, L.disk(2)) & elig
    return L.remove_small(m, 150 * YD * YD / res ** 2)


def tree_rule(canopy, k, min_area, res=1.0):
    """Canopy mask -> golfer's trees line: drop clumps < min_area m2, then buffer k m (negative = erode)."""
    m = L.remove_small(canopy, min_area / res ** 2)
    if k > 0:
        m = ndimage.distance_transform_edt(~m) * res <= k
    elif k < 0:
        m = ndimage.distance_transform_edt(m) * res > -k
    return m


def tree_mask_gbm(p, thr, res=1.0):
    ps = ndimage.uniform_filter(np.nan_to_num(p), 3)
    m = ndimage.binary_opening(ps >= thr, L.disk(1))
    m = ndimage.binary_closing(m, L.disk(2))
    return L.remove_small(m, 30 / res ** 2)


# =========================================================================== metrics
KEEP_HAND = ("fairway", "first_cut", "water", "sand", "ob")


def compose(cls, trees, native):
    """Hand lie grid with its trees + native replaced by the model's (int8 class index)."""
    out = np.full(cls.shape, LB.CI["rough"], np.int8)
    out[native] = LB.CI["native"]
    out[trees] = LB.CI["recovery"]
    keep = np.isin(cls, [LB.CI[c] for c in KEEP_HAND])
    out[keep] = cls[keep]
    out[cls < 0] = -1
    return out


def counts(pred, true):
    return np.array([np.sum(pred & true), np.sum(pred & ~true), np.sum(~pred & true)], np.int64)


def iou_of(c):
    u = c.sum()
    return None if u == 0 else float(c[0] / u)


def prec_rec(c):
    return (None if c[0] + c[1] == 0 else float(c[0] / (c[0] + c[1])),
            None if c[0] + c[2] == 0 else float(c[0] / (c[0] + c[2])))


PENAL = ("recovery", "native", "water")


def edges(x, grid, cls_names, a0=190, a1=335, step=5, lat_max=55):
    """First lateral distance (yds) of any of cls_names on each side at every station; NaN = none within
    lat_max or outside the footprint first. grid: cropped class grid of the hole."""
    h = x["h"]
    S = x["S"]
    rc = S.ll_to_rc([h["tee_ll"], h["dot270_ll"]])
    t, d = rc[0], rc[1]
    f = (d - t) / np.linalg.norm(d - t)
    r = np.array([-f[1], f[0]])
    ids = [LB.CI[c] for c in cls_names]
    out = []
    lats = np.arange(0, lat_max + 1, 1.0)
    for a in np.arange(a0, a1 + 1, step):
        for side in (-1, 1):
            p = t[None] + (a * f[None] + side * lats[:, None] * r[None]) * YD / S.res
            cc = np.floor(p[:, 0]).astype(int) - x["sl"][1].start
            rr = np.floor(p[:, 1]).astype(int) - x["sl"][0].start
            ok = (rr >= 0) & (rr < grid.shape[0]) & (cc >= 0) & (cc < grid.shape[1])
            v = np.full(len(lats), -1, np.int16)
            v[ok] = grid[rr[ok], cc[ok]]
            e = np.nan
            for i, val in enumerate(v):
                if val < 0:
                    break
                if val in ids:
                    e = lats[i]
                    break
            out.append(e)
    return np.array(out)


def edge_stats(eh, em, tol=5.0):
    both_none = np.isnan(eh) & np.isnan(em)
    both = np.isfinite(eh) & np.isfinite(em)
    agree = both_none | (both & (np.abs(eh - em) <= tol))
    any_ = ~both_none
    return dict(n=int(len(eh)), agree=int(agree.sum()), n_any=int(any_.sum()), agree_any=int((agree & any_).sum()),
                abs_err=[float(v) for v in np.abs(eh - em)[both]])


def hole_metrics(x, trees, native, clsname=("recovery", "native")):
    """trees / native: cropped bool masks of the model for hole x. -> dict of counts + edges."""
    cls = x["cls"]
    corr = x["corr"]
    g = compose(cls, trees, native)
    out = {}
    for c in ("recovery", "native", "water"):
        out[c] = counts((g == LB.CI[c])[corr], (cls == LB.CI[c])[corr])
    pen = [LB.CI[c] for c in PENAL]
    out["penal"] = counts(np.isin(g, pen)[corr], np.isin(cls, pen)[corr])
    out["recovery_raw"] = counts(trees[corr], (cls == LB.CI["recovery"])[corr])
    out["native_raw"] = counts(native[corr], (cls == LB.CI["native"])[corr])
    for nm, cl in (("trees", ("recovery",)), ("native", ("native",)), ("penal", PENAL)):
        out["edge_" + nm] = edge_stats(edges(x, cls, cl), edges(x, g, cl))
    out["agree"] = float(np.mean((g == cls)[corr])) if corr.any() else None
    return out


def summarise(rows):
    """rows: [(key, metrics)] -> pooled + per-hole summary."""
    P = {}
    for c in ("recovery", "native", "water", "penal", "recovery_raw", "native_raw"):
        tot = sum((m[c] for _, m in rows), np.zeros(3, np.int64))
        pr, rc = prec_rec(tot)
        vals = [iou_of(m[c]) for _, m in rows if iou_of(m[c]) is not None]
        P[c] = dict(iou=iou_of(tot), prec=pr, rec=rc, mean_iou=float(np.mean(vals)) if vals else None)
    for e in ("edge_trees", "edge_native", "edge_penal"):
        n = sum(m[e]["n"] for _, m in rows)
        a = sum(m[e]["agree"] for _, m in rows)
        na = sum(m[e]["n_any"] for _, m in rows)
        aa = sum(m[e]["agree_any"] for _, m in rows)
        errs = [v for _, m in rows for v in m[e]["abs_err"]]
        P[e] = dict(acc=a / n if n else None, acc_present=aa / na if na else None, n_present=na,
                    median_abs_err_yd=float(np.median(errs)) if errs else None)
    P["agree"] = float(np.mean([m["agree"] for _, m in rows if m["agree"] is not None]))
    per = []
    for k, m in rows:
        per.append(dict(hole=k, trees_iou=iou_of(m["recovery"]), native_iou=iou_of(m["native"]),
                        penal_iou=iou_of(m["penal"]),
                        edge_trees=m["edge_trees"]["agree"] / max(m["edge_trees"]["n"], 1),
                        edge_penal=m["edge_penal"]["agree"] / max(m["edge_penal"]["n"], 1), agree=m["agree"]))
    return dict(pooled=P, holes=per)


# =========================================================================== v1 layers
def v1_masks(D):
    """v1 (current vision_any) trees + native on the grid, from layers.tif."""
    import rasterio
    S = D["S"]
    p = os.path.join(HERE, D["slug"], "layers_v1.tif")
    if not os.path.exists(p):
        p = os.path.join(HERE, D["slug"], "layers.tif")
    with rasterio.open(p) as src:
        a = src.read(1)
        if src.tags().get("schema") == "vision_any/2":
            raise RuntimeError("layers.tif is v2; v1 copy missing")
    if a.shape != (S.H, S.W):
        raise RuntimeError(f"v1 layers.tif shape {a.shape} != grid {(S.H, S.W)}")
    return a == 2, a == 1


def v1_polys(slug):
    from shapely.geometry import shape
    for fn in ("vision_any_v1.geojson", "vision_any.geojson"):
        p = os.path.join(HERE, slug, fn)
        if os.path.exists(p):
            fc = json.load(open(p))
            if fc.get("properties", {}).get("schema", "vision_any/1") != "vision_any/1":
                continue
            out = {}
            for f in fc["features"]:
                out.setdefault(f["properties"]["lie"], []).append(shape(f["geometry"]))
            return out
    return None


# =========================================================================== LOHO
def loho(D, holes, names, task="native", other=None):
    """Out-of-fold P(task) per hole (cropped). other: list of (D2, holes2) added to every training fold
    (not used for the headline numbers). -> {key: p_crop}"""
    S = D["S"]
    refs = sorted({x["ref"] for x in holes}, key=lambda r: (len(r), r))
    oof = {}
    for ref in refs:
        t0 = time.time()
        ex = excluded(D, holes, ref)
        idx, y = task_xy(holes, task, skip=ref, flat_excl=ex)
        if y.sum() < 200:
            log(f"   fold {ref}: only {y.sum()} positives, skipped")
            for x in holes:
                if x["ref"] == ref:
                    oof[x["key"]] = np.zeros(x["cls"].shape, np.float32)
            continue
        idx, y = balanced(idx, y, seed=sum(map(ord, ref)))
        parts = [(D, idx, y)]
        for D2, h2 in other or []:
            i2, y2 = balanced(*task_xy(h2, task))
            parts.append((D2, i2, y2))
        clf = fit(parts, names)
        for x in holes:
            if x["ref"] != ref:
                continue
            reg = np.zeros((S.H, S.W), bool)
            reg[x["sl"]] = True
            oof[x["key"]] = predict_grid(D, clf, names, reg)[x["sl"]]
        log(f"   {task} fold {ref}: {len(y)} cells ({y.mean():.0%} pos) {time.time() - t0:.0f}s")
    return oof


def native_masks_for(D, holes, pmap, thr, mode="strict"):
    out = {}
    for x in holes:
        el = D["elig_rel" if mode == "relaxed" else "elig"][x["sl"]] & ~D["water0"][x["sl"]]
        out[x["key"]] = native_mask(pmap[x["key"]], el, thr, D["S"].res)
    return out


def choose_thr(D, holes, pmap, trees_by_key, per_hole=True, mode="strict"):
    """Native threshold: for hole h, the THRS value maximising pooled composed native IoU on the other
    holes (their own out-of-fold maps). Returns ({key: thr}, global best thr, curve)."""
    C = {}
    for thr in THRS:
        nm = native_masks_for(D, holes, pmap, thr, mode)
        for x in holes:
            tr = trees_by_key[x["key"]] & ~nm[x["key"]] if mode == "relaxed" else trees_by_key[x["key"]]
            g = compose(x["cls"], tr, nm[x["key"]])
            C[(thr, x["key"])] = counts((g == LB.CI["native"])[x["corr"]], (x["cls"] == LB.CI["native"])[x["corr"]])
    curve = {float(t): iou_of(sum((C[(t, x["key"])] for x in holes), np.zeros(3, np.int64))) or 0 for t in THRS}
    best = max(curve, key=curve.get)
    sel = {}
    for x in holes:
        sc = {t: iou_of(sum((C[(t, y["key"])] for y in holes if y["ref"] != x["ref"]), np.zeros(3, np.int64))) or 0
              for t in THRS}
        sel[x["key"]] = float(max(sc, key=sc.get)) if per_hole else best
    return sel, best, curve


def tree_candidates(D, x):
    """{(hag, k, area): cropped mask} for hole x."""
    out = {}
    pad = 12
    sl = x["sl"]
    big = (slice(max(sl[0].start - pad, 0), sl[0].stop + pad), slice(max(sl[1].start - pad, 0), sl[1].stop + pad))
    r0, c0 = sl[0].start - big[0].start, sl[1].start - big[1].start
    hh, ww = x["cls"].shape
    for hag in TREE_HAG:
        can = D["canopy"][hag][big]
        for area in TREE_AREA:
            base = L.remove_small(can, area / D["S"].res ** 2)
            din = ndimage.distance_transform_edt(base) * D["S"].res
            dout = ndimage.distance_transform_edt(~base) * D["S"].res
            for k in TREE_K:
                m = dout <= k if k > 0 else (din > -k if k < 0 else base)
                out[(hag, k, area)] = m[r0:r0 + hh, c0:c0 + ww]
    return out


def choose_trees(holes, cands):
    """Buffer rule chosen per held-out hole on the other holes (pooled raw trees IoU in corridors)."""
    C = {}
    for x in holes:
        t = (x["cls"] == LB.CI["recovery"])[x["corr"]]
        for p, m in cands[x["key"]].items():
            C[(p, x["key"])] = counts(m[x["corr"]], t)
    params = list(cands[holes[0]["key"]])
    pooled = {p: iou_of(sum((C[(p, x["key"])] for x in holes), np.zeros(3, np.int64))) or 0 for p in params}
    best = max(pooled, key=pooled.get)
    sel = {}
    for x in holes:
        sc = {p: iou_of(sum((C[(p, y["key"])] for y in holes if y["ref"] != x["ref"]), np.zeros(3, np.int64))) or 0
              for p in params}
        sel[x["key"]] = max(sc, key=sc.get)
    return sel, best, pooled


# =========================================================================== strategy
class SHTruth:
    """course.HOLES (screenshot px) + hand_zones_ll transforms, for evaluate.strategy_impact."""

    def __init__(self):
        for p in (os.path.join(ROOT, "spirit_hollow"), os.path.join(ROOT, "mozingo"),
                  os.path.join(ROOT, "course_data", "imagery")):
            if p not in sys.path:
                sys.path.append(p)
        import course
        import geo_zones as GZ
        import tee_strategy as t
        self.t, self.HOLES, self.GZ = t, course.HOLES, GZ
        self.G = GZ.transforms_from_json()
        self.keys = [k for k in course.HOLES if k in self.G]

    def key(self, s):
        return self.GZ._key(s)

    def ll_to_px(self, k, ll):
        return self.G[k].ll_to_px(ll)


def truth_for(slug, S):
    if slug == "spirit_hollow":
        return SHTruth()
    import truth as TR
    T = TR.MozingoTruth(S)
    T.key = lambda s: int(s) if str(s).isdigit() else s
    return T


def polys_from(S, sl, trees, native, foot):
    """Cropped masks -> {lie: [WGS84 polygons]} (inside the footprint + 30 m)."""
    out = {}
    lim = ndimage.binary_dilation(foot, L.disk(30))
    for lie, m in (("recovery", trees), ("native", native)):
        full = np.zeros((S.H, S.W), bool)
        full[sl] = m & lim
        out[lie] = L.mask_to_polys(S, full, min_yd2=150, simplify_yd=2.0)
    return out


def strategy(T, polys_by_key, n=5000):
    """polys_by_key: {key: {lie: polys}} or one dict for all holes -> evaluate.strategy_impact summary."""
    import evaluate as E
    rows = []
    for k in T.keys:
        sk = str(k)
        if isinstance(polys_by_key, dict) and sk in polys_by_key:
            pb = polys_by_key[sk]
        elif isinstance(polys_by_key, dict) and any(isinstance(v, dict) for v in polys_by_key.values()):
            continue
        else:
            pb = polys_by_key
        try:
            r = E.strategy_impact(T, pb, keys=[k], n=n)
            rows += r["holes"]
        except Exception as e:                              # noqa: BLE001
            log(f"   strategy {k} failed: {type(e).__name__} {e}")
    if not rows:
        return None
    aim_d = [abs(r[c]["aim_hand"] - r[c]["aim_vision"]) for r in rows for c in E.WOODS]
    return dict(holes=rows, same_club=float(np.mean([r["same_club"] for r in rows])),
                median_aim_change_yd=float(np.median(aim_d)),
                mean_ev_loss=float(np.mean([r["ev_loss_on_hand_map"] for r in rows])))


# =========================================================================== evaluation driver
def evaluate_all(strategy_n=5000, do_strategy=True):
    Ds, H = {}, {}
    for slug in EVAL_COURSES:
        Ds[slug] = prepare(slug)
        H[slug] = hole_data(Ds[slug])
    for slug in Ds:
        for x in H[slug]:
            x["S"] = Ds[slug]["S"]
    names = usable_names(list(Ds.values()), Ds["spirit_hollow"]["F"].names)
    import v2_features as VF
    names_nd = [n for n in names if n not in VF.NO_DIST]
    log(f"features used: {len(names)}")
    rep = dict(features=names, courses={}, settings={})
    keep = {}
    for slug in EVAL_COURSES:
        D, holes = Ds[slug], H[slug]
        R = dict(holes=[x["key"] for x in holes], n_train_cells=int(sum(len(x["tidx"]) for x in holes)))
        # ---------------- trees: buffer rule
        cands = {x["key"]: tree_candidates(D, x) for x in holes}
        tsel, tbest, tcurve = choose_trees(holes, cands)
        trees_loho = {x["key"]: cands[x["key"]][tsel[x["key"]]] for x in holes}
        R["trees_rule"] = dict(best=dict(hag=tbest[0], k_m=tbest[1], min_area_m2=tbest[2]),
                               per_hole={k: list(v) for k, v in tsel.items()},
                               curve_k={str(k): tcurve[(tbest[0], k, tbest[2])] for k in TREE_K},
                               curve_hag_area={f"{h}/{a}": tcurve[(h, tbest[1], a)] for h in TREE_HAG for a in TREE_AREA})
        raw0 = {x["key"]: cands[x["key"]][(2.5, 0, 30)] for x in holes}
        # ---------------- trees: GBM alternative
        log(f"[{slug}] LOHO trees GBM")
        pt = loho(D, holes, names, "trees")
        tg = {}
        best_tg = None
        for thr in (0.4, 0.5, 0.6, 0.7):
            m = {x["key"]: tree_mask_gbm(pt[x["key"]], thr) for x in holes}
            c = sum((counts(m[x["key"]][x["corr"]], (x["cls"] == LB.CI["recovery"])[x["corr"]]) for x in holes),
                    np.zeros(3, np.int64))
            tg[thr] = iou_of(c) or 0
        best_tg = max(tg, key=tg.get)
        R["trees_gbm_curve"] = {str(k): v for k, v in tg.items()}
        # ---------------- native LOHO (trees = buffer rule out of fold)
        log(f"[{slug}] LOHO native")
        pn = loho(D, holes, names, "native")
        nsel, nbest, ncurve = choose_thr(D, holes, pn, trees_loho)
        nat_loho = {x["key"]: native_masks_for(D, [x], pn, nsel[x["key"]])[x["key"]] for x in holes}
        R["native_thr"] = dict(best=nbest, per_hole=nsel, curve=ncurve)
        nselr, nbestr, ncurver = choose_thr(D, holes, pn, trees_loho, mode="relaxed")
        nat_rel = {x["key"]: native_masks_for(D, [x], pn, nselr[x["key"]], "relaxed")[x["key"]] for x in holes}
        R["native_thr_relaxed"] = dict(best=nbestr, per_hole=nselr, curve=ncurver)
        log(f"[{slug}] LOHO native without distance features (ablation)")
        pn2 = loho(D, holes, names_nd, "native")
        nsel2, nbest2, _ = choose_thr(D, holes, pn2, trees_loho)
        nat_nd = {x["key"]: native_masks_for(D, [x], pn2, nsel2[x["key"]])[x["key"]] for x in holes}
        # ---------------- v1
        try:
            v1t, v1n = v1_masks(D)
        except Exception as e:                              # noqa: BLE001
            log("v1 layers unavailable:", e)
            v1t = v1n = None
        variants = {}
        z = lambda x: np.zeros(x["cls"].shape, bool)        # noqa: E731
        variants["osm_only"] = {x["key"]: (z(x), z(x)) for x in holes}
        if v1t is not None:
            variants["v1"] = {x["key"]: (v1t[x["sl"]], v1n[x["sl"]]) for x in holes}
            variants["v1_trees+v2_native"] = {x["key"]: (v1t[x["sl"]], nat_loho[x["key"]]) for x in holes}
        variants["canopy_raw+v2_native"] = {x["key"]: (raw0[x["key"]], nat_loho[x["key"]]) for x in holes}
        variants["v2"] = {x["key"]: (trees_loho[x["key"]], nat_loho[x["key"]]) for x in holes}
        variants["v2_relaxed"] = {x["key"]: (trees_loho[x["key"]] & ~nat_rel[x["key"]], nat_rel[x["key"]]) for x in holes}
        variants["v2_trees_gbm"] = {x["key"]: (tree_mask_gbm(pt[x["key"]], best_tg), nat_loho[x["key"]]) for x in holes}
        variants["v2_native_no_dist"] = {x["key"]: (trees_loho[x["key"]], nat_nd[x["key"]]) for x in holes}
        R["variants"] = {}
        for nm, v in variants.items():
            rows = [(x["key"], hole_metrics(x, *v[x["key"]])) for x in holes]
            R["variants"][nm] = summarise(rows)
            P = R["variants"][nm]["pooled"]
            log(f"   {slug} {nm:>22}: trees {P['recovery']['iou']}, native {P['native']['iou']}, "
                f"edge trees {P['edge_trees']['acc']}, penal {P['penal']['iou']}")
        keep[slug] = dict(trees_loho=trees_loho, nat_loho=nat_loho, variants=variants, pt=pt, pn=pn,
                          best_tg=best_tg)
        rep["courses"][slug] = R
    # ---------------- native mode (strict vs relaxed eligibility): pooled composed native IoU, both courses
    pool = {}
    for m, nm in (("strict", "v2_strict"), ("relaxed", "v2_relaxed")):
        num = den = 0.0
        for slug in EVAL_COURSES:
            V = rep["courses"][slug]["variants"]["v2" if m == "strict" else "v2_relaxed"]["pooled"]["native"]
            num += (V["iou"] or 0)
            den += 1
        pool[m] = num / den
    mode = max(pool, key=pool.get)
    rep["native_mode"] = dict(chosen=mode, mean_native_iou=pool)
    log(f"native mode: {mode} {pool}")
    for slug in EVAL_COURSES:
        V = rep["courses"][slug]["variants"]
        V["v2_strict"] = V["v2"]
        if mode == "relaxed":
            V["v2"] = V["v2_relaxed"]
            keep[slug]["variants"]["v2"] = keep[slug]["variants"]["v2_relaxed"]
            rep["courses"][slug]["native_thr"] = rep["courses"][slug]["native_thr_relaxed"]
    # ---------------- cross-course
    rep["cross"] = {}
    xpred = {}
    for a, b in (("spirit_hollow", "mozingo"), ("mozingo", "spirit_hollow")):
        Da, Db, Ha, Hb = Ds[a], Ds[b], H[a], H[b]
        log(f"cross {a} -> {b}")
        idx, y = balanced(*task_xy(Ha, "native"))
        clf = fit([(Da, idx, y)], names)
        thr = rep["courses"][a]["native_thr"]["best"]
        tb = rep["courses"][a]["trees_rule"]["best"]
        rows, nat_x, tr_x = [], {}, {}
        for x in Hb:
            reg = np.zeros((Db["S"].H, Db["S"].W), bool)
            reg[x["sl"]] = True
            p = predict_grid(Db, clf, names, reg)[x["sl"]]
            el = Db["elig_rel" if mode == "relaxed" else "elig"][x["sl"]] & ~Db["water0"][x["sl"]]
            nat_x[x["key"]] = native_mask(p, el, thr)
            tr_x[x["key"]] = tree_candidates(Db, x)[(tb["hag"], tb["k_m"], tb["min_area_m2"])]
            if mode == "relaxed":
                tr_x[x["key"]] = tr_x[x["key"]] & ~nat_x[x["key"]]
            rows.append((x["key"], hole_metrics(x, tr_x[x["key"]], nat_x[x["key"]])))
        rep["cross"][f"{a}->{b}"] = dict(thr=thr, trees=tb, **summarise(rows))
        xpred[b] = dict(trees=tr_x, native=nat_x)
        P = rep["cross"][f"{a}->{b}"]["pooled"]
        log(f"   cross {a}->{b}: trees {P['recovery']['iou']}, native {P['native']['iou']}, penal {P['penal']['iou']}")
    # ---------------- decision impact
    if do_strategy:
        for slug in EVAL_COURSES:
            D, holes = Ds[slug], H[slug]
            try:
                T = truth_for(slug, D["S"])
            except Exception as e:                          # noqa: BLE001
                log("strategy truth failed:", type(e).__name__, e)
                continue
            keymap = {str(T.key(x["key"])): x for x in holes}
            T.keys = [k for k in T.keys if str(k) in keymap]
            st = {}
            K = keep[slug]
            sets = dict(v2={k: polys_from(D["S"], x["sl"], *K["variants"]["v2"][x["key"]], x["foot"])
                            for k, x in keymap.items()})
            v1p = v1_polys(slug)
            if v1p is not None:
                sets["v1"] = v1p
            sets["osm_only"] = {}
            other = "mozingo" if slug == "spirit_hollow" else "spirit_hollow"
            if slug in xpred:
                sets[f"v2_cross_from_{other}"] = {
                    k: polys_from(D["S"], x["sl"], xpred[slug]["trees"][x["key"]], xpred[slug]["native"][x["key"]], x["foot"])
                    for k, x in keymap.items()}
            for nm, pb in sets.items():
                log(f"strategy {slug} {nm}")
                st[nm] = strategy(T, pb, n=strategy_n)
            rep["courses"][slug]["strategy"] = st
    # ---------------- product settings (both courses)
    rep["settings"] = product_settings(rep)
    train_product(Ds, H, names, rep)
    return rep, Ds


def product_settings(rep):
    sh, mz = rep["courses"]["spirit_hollow"], rep["courses"]["mozingo"]
    # trees: the SH-chosen rule (SH map is the hand-checked GPS one); native thr: mean of the two LOHO bests
    tb = sh["trees_rule"]["best"]
    thr = round(float(np.mean([sh["native_thr"]["best"], mz["native_thr"]["best"]])), 2)
    return dict(trees=tb, native_thr=thr, native_mode=rep.get("native_mode", {}).get("chosen", "strict"))


def train_product(Ds, H, names, rep):
    """Final native (and trees-GBM) model on all labelled cells of both courses -> model_v2/."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    parts = [(Ds[s], *balanced(*task_xy(H[s], "native"))) for s in Ds]
    clf = fit(parts, names)
    save_model(clf, names, rep)


def save_model(clf, names, rep):
    import pickle
    settings = dict(rep["settings"])
    prev = os.path.join(MODEL_DIR, "model.json")
    dc = None
    if os.path.exists(prev):
        old = json.load(open(prev))
        dc = old.get("decision_calibration")
        if dc:          # decision-level settings (v2_calibrate.py, merge-gated) win over the map-IoU choice
            settings = old["settings"]
    meta = dict(model_id=MODEL_ID, features=names, settings=settings, map_level_settings=rep["settings"],
                decision_calibration=dc,
                trained_on={s: rep["courses"][s]["holes"] for s in rep["courses"]},
                built=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()))
    try:
        clf.booster_.save_model(os.path.join(MODEL_DIR, "native_lgbm.txt"))
        meta["format"] = "lightgbm"
    except AttributeError:
        with open(os.path.join(MODEL_DIR, "native_hgb.pkl"), "wb") as fh:
            pickle.dump(clf, fh)
        meta["format"] = "sklearn_hgb_pickle"
    json.dump(meta, open(os.path.join(MODEL_DIR, "model.json"), "w"), indent=1)


class _Booster:
    def __init__(self, b):
        self.b = b

    def predict_proba(self, X):
        p = self.b.predict(X)
        return np.c_[1 - p, p]


def load_model():
    meta = json.load(open(os.path.join(MODEL_DIR, "model.json")))
    if meta["format"] == "lightgbm":
        import lightgbm as lgb
        clf = _Booster(lgb.Booster(model_file=os.path.join(MODEL_DIR, meta.get("native_model_file", "native_lgbm.txt"))))
    else:
        import pickle
        clf = pickle.load(open(os.path.join(MODEL_DIR, "native_hgb.pkl"), "rb"))
    return clf, meta


# =========================================================================== inference / integration
def infer(slug, integrate=False):
    import run_any as RA
    clf, meta = load_model()
    D = prepare(slug)
    S, M = D["S"], D["M"]
    names = meta["features"]
    missing = [n for n in names if n not in D["F"].names]
    if missing:
        raise RuntimeError(f"features missing for {slug}: {missing}")
    st = meta["settings"]
    relaxed = st.get("native_mode") == "relaxed"
    E = D["elig_rel"] if relaxed else D["elig"]
    region = E & D["course"]
    p = predict_grid(D, clf, names, region)
    p = np.where(np.isfinite(p), p, 0).astype(np.float32)
    tb = st["trees"]
    trees = tree_rule(D["canopy"][tb["hag"]], tb["k_m"], tb["min_area_m2"], S.res)
    el = E & D["course"] & ~D["water0"] & (np.ones_like(trees) if relaxed else ~trees)
    if st.get("native_dmin_yd"):          # decision-level calibration (v2_calibrate.py): no long grass this close to OSM fairway
        el &= ndimage.distance_transform_edt(~M["fairway"]) * S.res >= st["native_dmin_yd"] * YD
    if st.get("native_thr") is None:
        el &= False
    nat = native_mask(p, el, st["native_thr"] if st.get("native_thr") is not None else 1.0, S.res)
    gate = st.get("native_gate_share") or 0
    if gate:              # v2_longgrass_cv.py: long grass only where it covers >= gate of the OSM course outline
        c = M["course"] if M["course"].any() else D["course"]
        if (nat & c).sum() < gate * max(c.sum(), 1):
            nat[:] = False
    if relaxed:
        trees = trees & ~nat
    water, wparts = L.water_mask(S, D["Ly"], M, mown_p=1 - p, trees=trees)
    nat &= ~water
    R = dict(S=S, M=M, Ly=D["Ly"], trees=trees, native=nat, water=water, p_native=p, trees_how=D["trees_how"],
             native_info=dict(model=meta["model_id"], thr=st["native_thr"]))
    fc = dict(type="FeatureCollection", features=polygons_v2(R, meta), properties=meta_v2(R, D, meta))
    d = os.path.join(HERE, slug)
    n = {}
    for f in fc["features"]:
        n[f["properties"]["lie"]] = n.get(f["properties"]["lie"], 0) + 1
    json.dump(fc, open(os.path.join(d, "vision_any_v2.geojson"), "w"), separators=(",", ":"))
    RA.preview(R, os.path.join(d, "classes_v2.jpg"))
    write_raster_v2(R, os.path.join(d, "layers_v2.tif"))
    log(f"[{slug}] v2: trees {trees.mean():.1%}, native {nat.mean():.1%}, water {water.mean():.1%}; polygons {n}")
    if integrate:
        cur = os.path.join(d, "vision_any.geojson")
        if os.path.exists(cur):
            old = json.load(open(cur))
            if old.get("properties", {}).get("schema", "vision_any/1") == "vision_any/1":
                json.dump(old, open(os.path.join(d, "vision_any_v1.geojson"), "w"), separators=(",", ":"))
        json.dump(fc, open(cur, "w"), separators=(",", ":"))
        log(f"[{slug}] integrated: vision_any.geojson is now v2 (v1 kept as vision_any_v1.geojson)")
    return fc


def polygons_v2(R, meta):
    from shapely.geometry import mapping
    from shapely.ops import transform
    S = R["S"]
    tb = meta["settings"]["trees"]
    ev = meta.get("eval", {})
    feats = []
    p_tree = ev.get("trees_precision") or 0.8
    for g in L.mask_to_polys(S, R["trees"], min_yd2=150, simplify_yd=2.0):
        feats.append(("recovery", g, f"vision2:lidar_canopy_hag>{tb['hag']}m_buffer{tb['k_m']:+d}m", p_tree))
    lab, _ = ndimage.label(R["native"])
    means = ndimage.mean(R["p_native"], lab, np.arange(1, lab.max() + 1)) if lab.max() else []
    for g in L.mask_to_polys(S, R["native"], min_yd2=150, simplify_yd=2.0):
        rc = S.ll_to_rc(np.asarray(g.representative_point().coords))
        c, r = int(rc[0, 0]), int(rc[0, 1])
        li = lab[r, c] if 0 <= r < S.H and 0 <= c < S.W else 0
        p = float(means[li - 1]) if li else meta["settings"]["native_thr"]
        feats.append(("native", g, "vision2:lgbm_naip_multiyear+lidar", p))
    vw = R["water"] & ~R["M"]["water"]
    for g in L.mask_to_polys(S, vw, min_yd2=150, simplify_yd=2.0):
        feats.append(("water", g, "vision:naip_ndwi+dtm+osm_stream", 0.8))
    out = []
    S.ll_to_rc([[0, 0]])
    for lie, g, src, p in feats:
        gm = transform(lambda x, y: S._fwd.transform(x, y), g)
        out.append(dict(type="Feature", geometry=mapping(g),
                        properties=dict(lie=lie, src=src, p=round(float(p), 3), area_yd2=round(gm.area / YD ** 2),
                                        model="vision_any/2")))
    return out


def meta_v2(R, D, meta):
    S = R["S"]
    yrs = [y for y, _ in S.naip]
    tb = meta["settings"]["trees"]
    return dict(schema="vision_any/2", model_id=meta["model_id"], slug=D["slug"],
                built=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()),
                trees_how=f"{R['trees_how']}; golfer trees line = canopy (HAG > {tb['hag']} m, clumps >= "
                          f"{tb['min_area_m2']} m2) buffered {tb['k_m']:+d} m (learned on the hand maps)",
                native_how=f"LightGBM P(native) >= {meta['settings']['native_thr']} on multi-year NAIP {yrs} + lidar "
                           "point statistics + texture + terrain + OSM distances (course-relative), trained on the "
                           f"Spirit Hollow + Mozingo hand maps ({meta.get('built')})",
                water_how="OSM water + NDWI open water near OSM water/streams + DTM channel of OSM streams + unmown banks",
                trained_on="hand maps of Spirit Hollow (hand_zones_ll.json) and Mozingo Lake (tee_strategy.HOLES)",
                eval=meta.get("eval"), lidar=S.src.get("lidar_v2") or S.src.get("hag"), naip_years=yrs,
                sources=S.src, grid=dict(crs=S.crs, res_m=S.res, bounds=S.bounds),
                rules="ARCHITECTURE.md 3.6: >= 150 yd2, simplified to 2 yds, never over OSM fairway/green/tee/bunker")


def write_raster_v2(R, path):
    import rasterio
    S = R["S"]
    cls = np.zeros((S.H, S.W), np.uint8)
    cls[R["native"]] = 1
    cls[R["trees"]] = 2
    cls[R["water"]] = 3
    prof = dict(driver="GTiff", height=S.H, width=S.W, count=2, dtype="uint8", crs=S.crs, transform=S.transform,
                compress="deflate", tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(cls, 1)
        dst.write((np.clip(R["p_native"], 0, 1) * 255).astype(np.uint8), 2)
        dst.update_tags(band1="0 none, 1 native, 2 trees (golfer line), 3 water", band2="p_native x255",
                        schema="vision_any/2")


# =========================================================================== report
def _f(v, n=2):
    return "-" if v is None else f"{v:.{n}f}"


def _pct(v):
    return "-" if v is None else f"{v:.0%}"


def decide(rep):
    """v2 replaces v1 if (a) on both courses composed native IoU and penal IoU are higher (LOHO), (b) cross-course
    SH -> Mozingo native IoU is higher than v1 on Mozingo, (c) pooled over both courses' tee shots the mean EV cost
    of following the layer's pick is not higher than v1's, and (d) pooled same-club agreement is at most one tee
    shot below v1's (one shot = noise at n = 27). (c, d replace the first run's per-course same-club rule, which
    flipped on single holes.)"""
    why, ok = [], True
    ev, same, n = {"v1": 0.0, "v2": 0.0}, {"v1": 0, "v2": 0}, {"v1": 0, "v2": 0}
    for slug in EVAL_COURSES:
        V = rep["courses"][slug]["variants"]
        if "v1" not in V:
            return False, ["v1 layers missing"]
        for c in ("native", "penal"):
            a, b = V["v2"]["pooled"][c]["iou"] or 0, V["v1"]["pooled"][c]["iou"] or 0
            why.append(f"{slug} {c} IoU v2 {a:.2f} vs v1 {b:.2f}")
            ok &= a > b
        st = rep["courses"][slug].get("strategy") or {}
        for k in ("v1", "v2"):
            if st.get(k):
                ev[k] += sum(r["ev_loss_on_hand_map"] for r in st[k]["holes"])
                same[k] += sum(r["same_club"] for r in st[k]["holes"])
                n[k] += len(st[k]["holes"])
    X = rep["cross"].get("spirit_hollow->mozingo")
    if X and "v1" in rep["courses"]["mozingo"]["variants"]:
        a, b = X["pooled"]["native"]["iou"] or 0, rep["courses"]["mozingo"]["variants"]["v1"]["pooled"]["native"]["iou"] or 0
        why.append(f"cross SH->Mozingo native IoU {a:.2f} vs v1 {b:.2f}")
        ok &= a > b
    if n["v1"] and n["v2"]:
        e1, e2 = ev["v1"] / n["v1"], ev["v2"] / n["v2"]
        why.append(f"pooled mean EV cost v2 {e2:+.3f} vs v1 {e1:+.3f} strokes per tee shot")
        why.append(f"pooled same club v2 {same['v2']}/{n['v2']} vs v1 {same['v1']}/{n['v1']}")
        ok &= e2 <= e1 + 1e-9 and same["v2"] >= same["v1"] - 1
    return bool(ok), why


def write_report(rep, path_md, path_json):
    json.dump(rep, open(path_json, "w"), indent=1, default=float)
    Lm = ["# vision_any v2: long grass + tree edges vs v1", "",
          "Generated by `course_data/vision_any/v2_model.py --eval` (GitHub Actions, vision_any_v2.yml). Every number "
          "is out of sample: leave-one-HOLE-out within a course (2B/2F one group; training cells within 20 m of the "
          "held-out footprint dropped; native threshold and tree buffer for a hole chosen on the other holes), or "
          "cross-course (train on one course, apply with its settings to the other).", "",
          "Landing corridors: 190-335 yds along the tee line, +/-55 yds, 1 m cells inside the screenshot footprint. "
          "`composed` = hand map with its trees + native replaced by the layer (fairway / first cut / water / sand / "
          "OB as traced). Edge accuracy: every 5 yds from 190 to 335 on each side, the first lateral distance at "
          "which the class starts (0-55 yds); agree = both absent or within 5 yds. `present` = only the rays where "
          "either map has the class.", "",
          f"Features ({len(rep['features'])}): " + ", ".join(rep["features"]), "",
          f"Native eligibility mode: **{rep.get('native_mode', {}).get('chosen')}** (mean LOHO composed native IoU over "
          f"both courses: {json.dumps(rep.get('native_mode', {}).get('mean_native_iou'))}); `v2` below is that mode, "
          "`v2_strict` = native never on lidar canopy and the tree buffer wins, `v2_relaxed` = native may run under "
          "canopy and wins over the tree buffer.", ""]
    for slug in EVAL_COURSES:
        R = rep["courses"][slug]
        Lm += [f"## {slug} (LOHO, {len(R['holes'])} holes)", "",
               "| layer | trees IoU | trees P / R | trees raw IoU | native IoU | native P / R | native raw IoU | penal IoU | "
               "trees edge acc (present) | native edge acc (present) | penal edge acc (present) | trees edge med err yd | cell agree |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for nm, V in R["variants"].items():
            P = V["pooled"]
            Lm.append(f"| {nm} | {_f(P['recovery']['iou'])} | {_f(P['recovery']['prec'])} / {_f(P['recovery']['rec'])} | "
                      f"{_f(P['recovery_raw']['iou'])} | {_f(P['native']['iou'])} | {_f(P['native']['prec'])} / "
                      f"{_f(P['native']['rec'])} | {_f(P['native_raw']['iou'])} | {_f(P['penal']['iou'])} | "
                      f"{_pct(P['edge_trees']['acc'])} ({_pct(P['edge_trees']['acc_present'])}) | "
                      f"{_pct(P['edge_native']['acc'])} ({_pct(P['edge_native']['acc_present'])}) | "
                      f"{_pct(P['edge_penal']['acc'])} ({_pct(P['edge_penal']['acc_present'])}) | "
                      f"{_f(P['edge_trees']['median_abs_err_yd'], 1)} | {_pct(P['agree'])} |")
        tr = R["trees_rule"]
        Lm += ["", f"Tree line rule chosen on all {slug} holes: canopy HAG > {tr['best']['hag']} m, clumps >= "
               f"{tr['best']['min_area_m2']} m2, buffer {tr['best']['k_m']:+d} m. Raw trees IoU by buffer k (m): " +
               ", ".join(f"{k}: {_f(v)}" for k, v in tr["curve_k"].items()) + ". By HAG / min area: " +
               ", ".join(f"{k}: {_f(v)}" for k, v in tr["curve_hag_area"].items()) + ".",
               f"Trees GBM alternative, raw IoU by threshold: " + ", ".join(f"{k}: {_f(v)}" for k, v in R["trees_gbm_curve"].items()) + ".",
               f"Native threshold (pooled best {R['native_thr']['best']}); composed native IoU by threshold: " +
               ", ".join(f"{k}: {_f(v)}" for k, v in R["native_thr"]["curve"].items()) + ".", "",
               "| hole | v1 trees | v2 trees | v1 native | v2 native | v1 penal | v2 penal | v2 trees edge | v2 penal edge |",
               "|---|---|---|---|---|---|---|---|---|"]
        v1h = {r["hole"]: r for r in R["variants"].get("v1", {}).get("holes", [])}
        for r in R["variants"]["v2"]["holes"]:
            a = v1h.get(r["hole"], {})
            Lm.append(f"| {r['hole']} | {_f(a.get('trees_iou'))} | {_f(r['trees_iou'])} | {_f(a.get('native_iou'))} | "
                      f"{_f(r['native_iou'])} | {_f(a.get('penal_iou'))} | {_f(r['penal_iou'])} | {_pct(r['edge_trees'])} | "
                      f"{_pct(r['edge_penal'])} |")
        st = R.get("strategy")
        if st:
            Lm += ["", f"### Decision impact, {slug}", "",
                   "tee_strategy best club / aim (Driver, 2-wood, 4-wood) on the hand map vs the hand map with its trees + "
                   "native replaced by each layer; EV cost = strokes lost on the hand map by following the layer's pick.", "",
                   "| layer | same club | median aim change yd | mean EV cost |", "|---|---|---|---|"]
            for nm, s in st.items():
                if s:
                    Lm.append(f"| {nm} | {_pct(s['same_club'])} ({sum(r['same_club'] for r in s['holes'])}/{len(s['holes'])}) | "
                              f"{_f(s['median_aim_change_yd'], 1)} | {s['mean_ev_loss']:+.3f} |")
            names = [n for n in st if st[n]]
            Lm += ["", "| hole | club hand | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
            for i, r in enumerate(st[names[0]]["holes"]):
                cells = []
                for n in names:
                    rr = next((q for q in st[n]["holes"] if q["hole"] == r["hole"]), None)
                    cells.append("-" if rr is None else f"{rr['club_vision']} ({rr['ev_loss_on_hand_map']:+.3f})")
                Lm.append(f"| {r['hole']} | {r['club_hand']} | " + " | ".join(cells) + " |")
        Lm.append("")
    Lm += ["## Cross-course", "", "| train -> test | thr | trees rule | trees IoU | native IoU | native P / R | penal IoU | "
           "trees edge acc | penal edge acc |", "|---|---|---|---|---|---|---|---|---|"]
    for k, X in rep["cross"].items():
        P = X["pooled"]
        Lm.append(f"| {k} | {X['thr']} | k {X['trees']['k_m']:+d} m | {_f(P['recovery']['iou'])} | {_f(P['native']['iou'])} | "
                  f"{_f(P['native']['prec'])} / {_f(P['native']['rec'])} | {_f(P['penal']['iou'])} | "
                  f"{_pct(P['edge_trees']['acc'])} | {_pct(P['edge_penal']['acc'])} |")
    ok, why = decide(rep)
    rep["decision"] = dict(integrate=ok, why=why)
    Lm += ["", "## Decision", "", f"**{'Integrate v2' if ok else 'Keep v1'}**: " + "; ".join(why) + ".", "",
           f"Product settings: {json.dumps(rep['settings'])}. Model: `course_data/vision_any/model_v2/` (native "
           "LightGBM trained on both hand maps)."]
    open(path_md, "w").write("\n".join(Lm) + "\n")
    json.dump(rep, open(path_json, "w"), indent=1, default=float)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--no-strategy", action="store_true")
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--infer", nargs="*")
    ap.add_argument("--integrate", default="no", help="yes | no | auto (= the report's decision)")
    a = ap.parse_args()
    if a.eval:
        rep, _ = evaluate_all(strategy_n=a.n, do_strategy=not a.no_strategy)
        ok = write_report(rep, os.path.join(HERE, "v2_report.md"), os.path.join(HERE, "v2_report.json"))
        meta = json.load(open(os.path.join(MODEL_DIR, "model.json")))
        P = rep["courses"]["spirit_hollow"]["variants"]["v2"]["pooled"]
        meta["eval"] = dict(trees_precision=P["recovery"]["prec"], native_precision=P["native"]["prec"],
                            native_iou_sh_loho=P["native"]["iou"], trees_iou_sh_loho=P["recovery"]["iou"],
                            decision=rep["decision"])
        json.dump(meta, open(os.path.join(MODEL_DIR, "model.json"), "w"), indent=1)
        print(open(os.path.join(HERE, "v2_report.md")).read())
    if a.infer:
        integ = a.integrate == "yes"
        if a.integrate == "auto":
            p = os.path.join(HERE, "v2_report.json")
            integ = bool(json.load(open(p)).get("decision", {}).get("integrate")) if os.path.exists(p) else False
        for slug in a.infer:
            try:
                infer(slug, integrate=integ)
            except Exception as e:                          # noqa: BLE001
                import traceback
                log(f"infer {slug} failed: {type(e).__name__} {e}")
                traceback.print_exc()


if __name__ == "__main__":
    main()
