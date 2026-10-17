"""Canopy recency: drop lidar canopy that the newest NAIP no longer shows as trees (and, optionally, add trees).

The product's trees line is 3DEP lidar canopy (HAG > 2.5 m). The lidar can be years older than the imagery:
Ellis (Cedar Rapids) was flown in 2019, before the August 2020 derecho flattened much of its canopy, so
fallen trees are still hazards; Mozingo's lidar is from 2013/14. This module checks the lidar canopy against
every NAIP year flown AFTER the lidar (R, G, B, NIR at 1 m on the analysis grid):

  1. a per-course, self-supervised tree / not-tree classifier on NAIP spectra + texture (NDVI, brightness,
     NIR, local standard deviation of brightness / NIR at 3 and 7 m, shadow fraction), labels from the lidar
     itself: core canopy (canopy eroded 2 m) vs open ground (HAG < 0.5 m, >= 4 m from canopy), inside the
     course area. Spatial-block cross-fitting (4 folds of 48 m blocks): every cell is scored by a model that
     never saw its block, so a fallen stand cannot teach the model that it is a tree.
  2. per post-lidar year y, p_y(tree). A canopy cell is GONE when p_y < P_GONE in every post-lidar year (a
     tree has to be missing in all of them, so one bad image or a leaf-off date cannot delete canopy); gone
     cells are opened (1 m), and only clumps >= MIN_GONE_M2 are removed.
  3. optional ADD: a non-canopy cell is NEW when p_y > P_NEW in every post-lidar year, outside OSM fairway /
     green / tee / water / buildings and >= 3 m from canopy, clumps >= MIN_NEW_M2 (new or missed canopy).

  python3 course_data/vision_any/canopy_recency.py --slug ellis      # map-level report vs the hand maps
"""
import argparse
import json
import os
import re
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import layers as L                                           # noqa: E402

P_GONE, MIN_GONE_M2 = 0.4, 25.0
P_NEW, MIN_NEW_M2 = 0.85, 50.0
BLOCK_M, FOLDS = 48, 4
NTRAIN = 120_000


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def lidar_year(S):
    """Acquisition year of the lidar the canopy comes from (EPT project name / PC item date), else None."""
    m = S.meta or {}
    ept = m.get("ept") if isinstance(m.get("ept"), dict) else {}
    for u in (ept.get("used") or []):
        if u.get("year"):
            return int(u["year"])
        mm = re.search(r"(20\d\d)", u.get("name", ""))
        if mm:
            return int(mm.group(1))
    lid = m.get("lidar") if isinstance(m.get("lidar"), dict) else {}
    for it in ((lid.get("hag") or {}).get("items") or []):
        mm = re.search(r"_(20\d\d)_", it.get("id", "")) or re.search(r"(20\d\d)", it.get("when", ""))
        if mm:
            return int(mm.group(1))
    return None


def features(b):
    """(H, W, F) float32 features of one NAIP year (b: H x W x 4 in 0..1), course-relative later."""
    nd = L.ndvi(b)
    br = b[..., :3].mean(-1)
    nir = b[..., 3]
    F = [b[..., 0], b[..., 1], b[..., 2], nir, nd, br]
    for w in (3, 7):
        for x in (br, nir):
            m1 = ndimage.uniform_filter(x, w)
            F.append(np.sqrt(np.maximum(ndimage.uniform_filter(x * x, w) - m1 * m1, 0)))
    dark = (br < np.nanpercentile(br, 25)).astype(np.float32)
    F.append(ndimage.uniform_filter(dark, 7))
    F.append(ndimage.uniform_filter(nd, 7))
    F.append(ndimage.uniform_filter(br, 7))
    return np.nan_to_num(np.stack(F, -1).astype(np.float32))


def _norm(X, ref):
    v = X[ref]
    med = np.median(v, 0)
    iqr = np.percentile(v, 75, 0) - np.percentile(v, 25, 0) + 1e-4
    return (X - med) / iqr


def p_tree(S, canopy, hag, area, year_img, rng):
    """Cross-fitted P(tree) of every cell in `area` for one NAIP year."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    X = features(year_img)
    valid = np.isfinite(year_img).all(-1) & (year_img.sum(-1) > 0)
    core = ndimage.distance_transform_edt(canopy) * S.res > 2.0
    open_ = (np.nan_to_num(hag, nan=9.0) < 0.5) & (ndimage.distance_transform_edt(~canopy) * S.res >= 4.0)
    ref = area & valid
    Xn = _norm(X.reshape(-1, X.shape[-1]), ref.ravel()).reshape(X.shape)
    rr, cc = np.mgrid[0:S.H, 0:S.W]
    nb = int(BLOCK_M / S.res)
    blk = ((rr // nb) * 7919 + (cc // nb) * 104729) % FOLDS
    out = np.full((S.H, S.W), np.nan, np.float32)
    for f in range(FOLDS):
        tr = ref & (blk != f)
        pos, neg = np.flatnonzero((tr & core).ravel()), np.flatnonzero((tr & open_).ravel())
        if len(pos) < 200 or len(neg) < 200:
            continue
        k = min(NTRAIN // 2, len(pos), len(neg))
        idx = np.r_[rng.choice(pos, k, replace=False), rng.choice(neg, k, replace=False)]
        y = np.r_[np.ones(k), np.zeros(k)]
        clf = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.1, max_leaf_nodes=31,
                                             l2_regularization=1.0, random_state=0)
        clf.fit(Xn.reshape(-1, X.shape[-1])[idx], y)
        te = np.flatnonzero((ref & (blk == f)).ravel())
        out.ravel()[te] = clf.predict_proba(Xn.reshape(-1, X.shape[-1])[te])[:, 1]
    return out


def recency(S, canopy, M=None, area=None, add=False, seed=0):
    """canopy (bool, lidar) -> dict(removed, added, years, lidar_year, p={year: P(tree)}, stats)."""
    ly = lidar_year(S)
    post = [(y, b) for y, b in S.naip if ly is None or y > ly]
    info = dict(lidar_year=ly, naip_years=[y for y, _ in S.naip], post_years=[y for y, _ in post])
    removed = np.zeros_like(canopy)
    added = np.zeros_like(canopy)
    if not post:
        info["note"] = "no NAIP year after the lidar: canopy kept"
        return dict(removed=removed, added=added, p={}, **info)
    if area is None:
        area = np.ones_like(canopy)
    hag = S.layers.get("hag")
    if hag is None:
        hag = np.where(canopy, 9.0, 0.0)
    rng = np.random.default_rng(seed)
    P = {}
    for y, b in post:
        P[y] = p_tree(S, canopy, hag, area, b, rng)
        log(f"  [{S.slug}] P(tree) NAIP {y}: canopy mean {np.nanmean(P[y][canopy & area]):.2f}, "
            f"open mean {np.nanmean(P[y][~canopy & area]):.2f}")
    stack = np.stack([P[y] for y in P])
    seen = np.isfinite(stack).all(0)
    gone = canopy & area & seen & (np.nan_to_num(stack, nan=1.0) < P_GONE).all(0)
    gone = ndimage.binary_opening(gone, L.disk(1))
    removed = L.remove_small(gone, MIN_GONE_M2 / S.res ** 2) & canopy
    if add:
        excl = np.zeros_like(canopy)
        if M is not None:
            for k in ("fairway", "green", "tee", "water", "building"):
                if k in M:
                    excl |= M[k]
        new = ~canopy & area & seen & (np.nan_to_num(stack, nan=0.0) > P_NEW).all(0) & ~excl
        new &= ndimage.distance_transform_edt(~canopy) * S.res >= 3.0
        new = ndimage.binary_opening(new, L.disk(1))
        added = L.remove_small(new, MIN_NEW_M2 / S.res ** 2)
    info.update(canopy_m2=float(canopy.sum() * S.res ** 2), removed_m2=float(removed.sum() * S.res ** 2),
                added_m2=float(added.sum() * S.res ** 2))
    log(f"  [{S.slug}] lidar {ly}, post-lidar NAIP {info['post_years']}: canopy {info['canopy_m2']:.0f} m2, "
        f"removed {info['removed_m2']:.0f} m2 ({info['removed_m2'] / max(info['canopy_m2'], 1):.1%}), added {info['added_m2']:.0f} m2")
    return dict(removed=removed, added=added, p=P, **info)


# ----------------------------------------------------------------------------- map-level check vs a hand map
def hand_trees(S, slug):
    """(footprint mask, hand recovery mask) on the grid from the hand map (truth/<slug> or the SH one), or None."""
    from shapely.geometry import Polygon
    P = {"spirit_hollow": os.path.join(ROOT, "course_data", "spirit_hollow", "hand_zones_ll.json")}
    p = P.get(slug) or os.path.join(ROOT, "course_data", "truth", slug, "hand_zones_ll.json")
    if not os.path.exists(p):
        return None
    hz = json.load(open(p))["holes"]
    foot = np.zeros((S.H, S.W), bool)
    rec = np.zeros((S.H, S.W), bool)
    for h in hz.values():
        if not h.get("footprint_ll"):
            continue
        fp = S.rasterize([Polygon(h["footprint_ll"])])
        foot |= fp
        hm = np.zeros_like(fp)
        for z in h["zones"]:                          # layer order as traced: later zones win
            if len(z["poly_ll"]) < 3:
                continue
            m = S.rasterize([Polygon(np.asarray(z["poly_ll"])[:, :2])]) & fp
            hm[m] = z["lie"] == "recovery"
        rec |= hm & fp
    return foot, rec


def map_check(S, canopy, R, slug):
    """Of the removed / added area inside the hand maps' footprints: how much is (not) hand-traced trees."""
    ht = hand_trees(S, slug)
    if ht is None:
        return None
    foot, rec = ht
    out = dict(footprint_m2=float(foot.sum() * S.res ** 2))
    for nm, m in (("removed", R["removed"]), ("added", R["added"])):
        a = m & foot
        out[f"{nm}_in_footprint_m2"] = float(a.sum() * S.res ** 2)
        out[f"{nm}_hand_trees_share"] = float((a & rec).sum() / max(a.sum(), 1))
    for nm, m in (("lidar", canopy), ("recency", (canopy & ~R["removed"]) | R["added"])):
        A, B = m & foot, rec
        out[f"iou_{nm}"] = float((A & B).sum() / max((A | B).sum(), 1))
        out[f"precision_{nm}"] = float((A & B).sum() / max(A.sum(), 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--p-gone", type=float)
    a = ap.parse_args()
    import run_any as RA
    cdir = RA.course_dir_for(a.slug)
    S = L.Stack.load(a.slug, cdir)
    M, _ = L.osm_masks(S, json.load(open(os.path.join(cdir, "osm.geojson"))))
    canopy = L.tree_mask(S, M, hag_min=2.5, min_area_m2=10.0)[0]
    area = ndimage.binary_dilation(M["course"], L.disk(30)) if M["course"].any() else np.ones_like(canopy)
    global P_GONE
    P_GONE = a.p_gone or P_GONE
    R = recency(S, canopy, M, area, add=a.add)
    print(json.dumps({k: v for k, v in R.items() if k not in ("removed", "added", "p")}, indent=1))
    print(json.dumps(map_check(S, canopy, R, a.slug), indent=1))


if __name__ == "__main__":
    main()
