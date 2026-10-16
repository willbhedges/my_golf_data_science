"""Hazard gap-fill from NAIP (RGB + NIR) + 3DEP: trees / long grass / water masks for the whole course.

  python3 course_data/imagery/classify.py              # train on the hand-traced holes, LOHO eval, predict
  python3 course_data/imagery/classify.py --eval-only

Pipeline
  1. Grid: the NAIP mosaic area-averaged to GRID_M (1.2 m) pixels, in the imagery CRS (EPSG:26915).
  2. Features per pixel: R, G, B, NIR, NDVI, brightness, excess green, NIR/red, each smoothed at two
     scales; texture (local std of NIR and of brightness at 3 windows, gradient energy); context (texture
     averaged over ~20 m); DEM slope and relative elevation (elev - its 30 m Gaussian mean: creeks sit in
     ravines) from 3DEP.
  3. Labels: the hand-traced zones of spirit_hollow/course.py, georeferenced by traced_align.py
     (traced_registration.json), rasterised onto the grid inside each screenshot's footprint. Same rules
     as spirit_hollow/vision.py: recovery -> trees, untraced -> rough only within 25 yds of fairway,
     OB not trained on, boundaries eroded.
  4. ExtraTrees (40 trees), evaluated leave-one-hole-out (train on every other hole's pixels, predict the
     held-out one). Note: screenshot footprints overlap, so neighbouring holes share some ground; the
     LOHO number is optimistic by that overlap.
  5. Predict the whole grid; write
       classes.tif / classes.png   per-pixel class; p_hazards.tif = p(trees), p(native), p(water) x 20
       gapfill.geojson             WGS84 polygons of trees (lie 'recovery'), native, water with mean p,
                                   min 150 yd2, simplified to ~2 yds (ARCHITECTURE.md 3.6). Pixels need
                                   p >= 0.5 (ExtraTrees votes are under-confident; at 0.7 most woods
                                   drop out); each polygon carries its mean p, so filter p >= 0.7 if wanted
       naip_trees.geojson          the recovery polygons only (course_data/geometry/build_holes.py --trees)
       gapfill_loho/<k>.geojson    the same polygons over hole k's footprint from the model that did not
                                   see hole k (ARCHITECTURE.md 7, circularity rule (a))
       classify_report.md / .json  LOHO accuracy, per-class IoU / precision / recall per hole
"""
import argparse
import json
import math
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "spirit_hollow"), os.path.join(ROOT, "mozingo")]

import render as R                                     # noqa: E402
import traced_align as TA                              # noqa: E402

IMG_DIR = os.path.join(HERE, "spirit_hollow")
GRID_M = 1.2
CLASSES = ["fairway", "rough", "trees", "native", "water", "sand"]
TRACE_TO_CLASS = {"fairway": "fairway", "recovery": "trees", "native": "native", "water": "water",
                  "sand": "sand", "rough": "rough"}
LIE_OF = {"trees": "recovery", "native": "native", "water": "water"}
FOOT_Y = (560, 1830)                                   # screenshot rows that show ground
BAD_REG = {"2B"}                                       # registration failed (scale at the search bound)
YD = 0.9144


# --------------------------------------------------------------------------- grid + features
def load_grid():
    import rasterio
    meta = json.load(open(os.path.join(IMG_DIR, "georef.json")))
    im = meta["imagery"]
    with rasterio.open(os.path.join(IMG_DIR, im["files"]["rgb"])) as src:
        k = GRID_M / abs(src.transform.a)
        Wg, Hg = int(src.width / k), int(src.height / k)
        rgb = src.read(out_shape=(3, Hg, Wg), resampling=rasterio.enums.Resampling.average)
        tr = src.transform * src.transform.scale(src.width / Wg, src.height / Hg)
        crs = src.crs
    with rasterio.open(os.path.join(IMG_DIR, im["files"]["nir"])) as src:
        nir = src.read(1, out_shape=(Hg, Wg), resampling=rasterio.enums.Resampling.average)
    dem = None
    dp = os.path.join(IMG_DIR, "dem.tif")
    if os.path.exists(dp):
        from rasterio.warp import reproject, Resampling
        dem = np.full((Hg, Wg), np.nan, np.float32)
        with rasterio.open(dp) as src:
            reproject(src.read(1), dem, src_transform=src.transform, src_crs=src.crs,
                      dst_transform=tr, dst_crs=crs, resampling=Resampling.bilinear)
    return dict(rgb=np.moveaxis(rgb, 0, -1).astype(np.float32) / 255.0, nir=nir.astype(np.float32) / 255.0,
                dem=dem, transform=tr, crs=crs, shape=(Hg, Wg), meta=meta)


def features(G):
    rgb, nir = G["rgb"], G["nir"]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    br = rgb.mean(-1)
    ndvi = (nir - r) / (nir + r + 1e-3)
    exg = (2 * g - r - b) / (r + g + b + 1e-3)
    nr = nir / (r + 1e-2)
    base = [r, g, b, nir, ndvi, br, exg, np.log(nr + 1e-2)]
    px_m = GRID_M
    feats, names = [], []
    for sig_m in (1.5, 5.0):
        s = sig_m / px_m
        for nm, x in zip("r g b nir ndvi br exg lognr".split(), base):
            feats.append(ndimage.gaussian_filter(x, s))
            names.append(f"{nm}_s{sig_m:g}")
    tex = []
    for nm, x in (("nir", nir), ("br", br)):
        for win_m in (3.0, 7.0, 15.0):
            w = max(3, int(round(win_m / px_m)) | 1)
            m1 = ndimage.uniform_filter(x, w)
            m2 = ndimage.uniform_filter(x * x, w)
            tex.append(np.sqrt(np.maximum(m2 - m1 * m1, 0)))
            names.append(f"std_{nm}_{win_m:g}m")
    gm = np.hypot(ndimage.sobel(nir, 0), ndimage.sobel(nir, 1))
    tex.append(ndimage.uniform_filter(gm, 5))
    names.append("grad_nir")
    feats += tex
    for x, nm in zip(tex[:3] + [ndvi], ["std_nir_3", "std_nir_7", "std_nir_15", "ndvi"]):
        feats.append(ndimage.uniform_filter(x, int(20 / px_m)))     # ~20 m context
        names.append(f"ctx_{nm}")
    if G["dem"] is not None and np.isfinite(G["dem"]).mean() > 0.9:
        d = np.where(np.isfinite(G["dem"]), G["dem"], np.nanmean(G["dem"]))
        ds = ndimage.gaussian_filter(d, 1.0)
        gy, gx = np.gradient(ds, px_m)
        feats.append(np.degrees(np.arctan(np.hypot(gx, gy))))
        names.append("slope_deg")
        for sig_m in (10.0, 30.0):
            feats.append(ds - ndimage.gaussian_filter(d, sig_m / px_m))
            names.append(f"relz_{sig_m:g}m")
    X = np.stack(feats, -1).astype(np.float32)
    return X, names, ndvi


# --------------------------------------------------------------------------- labels
def ll_to_grid(G, ll):
    from pyproj import Transformer
    t = Transformer.from_crs("EPSG:4326", G["crs"], always_xy=True)
    x, y = t.transform(ll[:, 0], ll[:, 1])
    inv = ~G["transform"]
    c, r = inv * (np.asarray(x), np.asarray(y))
    return np.c_[c, r]


def hole_labels(G, course, key, reg):
    """-> (label raster int16 with -1 = ignore, footprint mask) on the grid."""
    Hg, Wg = G["shape"]
    h = course.HOLES[key]
    ppy = np.linalg.norm(np.subtract(h["dot270"], h["tee"])) / 270.0
    cls = np.full((Hg, Wg), CLASSES.index("rough"), np.int16)
    ob = np.zeros((Hg, Wg), np.uint8)

    def poly_px(pts):
        q = ll_to_grid(G, TA.screenshot_px_to_ll(reg, np.asarray(pts, float)))
        return np.round(q * 8).astype(np.int32)                    # 3 fractional bits

    for name, pts in h["zones"]:
        p = poly_px(pts)
        if name == "ob":
            cv2.fillPoly(ob, [p], 1, shift=3)
        elif name in TRACE_TO_CLASS:
            m = np.zeros((Hg, Wg), np.uint8)
            cv2.fillPoly(m, [p], 1, shift=3)
            cls[m > 0] = CLASSES.index(TRACE_TO_CLASS[name])
            ob[m > 0] = 0
    foot = np.zeros((Hg, Wg), np.uint8)
    cv2.fillPoly(foot, [poly_px([(0, FOOT_Y[0]), (920, FOOT_Y[0]), (920, FOOT_Y[1]), (0, FOOT_Y[1])])], 1, shift=3)
    foot = foot > 0
    lab = cls.copy()
    near_fw = ndimage.binary_dilation(cls == CLASSES.index("fairway"), iterations=int(25 * YD / GRID_M))
    lab[(cls == CLASSES.index("rough")) & ~near_fw] = -1
    # erode each class by ~2 m so boundary errors aren't labels
    keep = np.zeros_like(foot)
    for c in range(len(CLASSES)):
        keep |= ndimage.binary_erosion(cls == c, iterations=2)
    lab[~keep | (ob > 0) | ~foot] = -1
    return lab, foot, cls


# --------------------------------------------------------------------------- model
def make_model():
    # ExtraTrees: HistGradientBoosting was >100x slower in the sandbox (OpenMP contention) for similar skill
    from sklearn.ensemble import ExtraTreesClassifier
    return ExtraTreesClassifier(n_estimators=40, max_depth=18, min_samples_leaf=5, max_features="sqrt",
                                class_weight="balanced_subsample", n_jobs=1, random_state=0)


def sample(lab, n, rng):
    idx = np.flatnonzero(lab.ravel() >= 0)
    if len(idx) > n:
        # stratified-ish: cap the common classes so water/sand/native aren't drowned
        y = lab.ravel()[idx]
        out = []
        per = n // len(CLASSES)
        for c in range(len(CLASSES)):
            ic = idx[y == c]
            if len(ic):
                out.append(rng.choice(ic, min(len(ic), max(per, n * len(ic) // len(idx) // 2)), replace=False))
        idx = np.concatenate(out)
    return idx


def scores(pred, truth, mask):
    out = {}
    p, t = pred[mask], truth[mask]
    out["acc"] = float((p == t).mean()) if mask.any() else float("nan")
    for c, nm in enumerate(CLASSES):
        tp = int(((p == c) & (t == c)).sum())
        fp = int(((p == c) & (t != c)).sum())
        fn = int(((p != c) & (t == c)).sum())
        out[nm] = dict(iou=tp / (tp + fp + fn) if tp + fp + fn else None,
                       prec=tp / (tp + fp) if tp + fp else None, rec=tp / (tp + fn) if tp + fn else None,
                       n_true=tp + fn)
    return out


def polygons(G, prob, cls_map, c, p_min=0.5, min_yd2=150, simplify_yd=2.0):
    """Class c regions with p >= p_min -> WGS84 polygons (via the grid CRS)."""
    from pyproj import Transformer
    import shapely
    from shapely.geometry import Polygon, mapping
    m = ((cls_map == c) & (prob >= p_min)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cnts, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    tr = G["transform"]
    to_ll = Transformer.from_crs(G["crs"], "EPSG:4326", always_xy=True)
    feats = []
    if hier is None:
        return feats
    hier = hier[0]
    px_yd2 = (GRID_M / YD) ** 2
    for i, cnt in enumerate(cnts):
        if hier[i][3] != -1 or len(cnt) < 3:
            continue
        holes = []
        j = hier[i][2]
        while j != -1:
            if len(cnts[j]) >= 3 and cv2.contourArea(cnts[j]) * px_yd2 >= min_yd2:
                holes.append(cnts[j][:, 0, :])
            j = hier[j][0]
        ext = cnt[:, 0, :]

        def w(pts):
            pts = pts.astype(float) + 0.0
            x, y = tr * (pts[:, 0], pts[:, 1])
            return np.c_[x, y]
        poly = Polygon(w(ext), [w(hh) for hh in holes]).buffer(0)
        if poly.is_empty or poly.area / YD ** 2 < min_yd2:
            continue
        poly = poly.simplify(simplify_yd * YD)
        mm = np.zeros_like(m)
        cv2.drawContours(mm, [cnt], -1, 1, -1)
        pm = float(prob[mm > 0].mean())
        g = shapely.transform(poly, lambda xy: np.c_[to_ll.transform(xy[:, 0], xy[:, 1])])
        feats.append(dict(type="Feature", geometry=mapping(g),
                          properties=dict(lie=LIE_OF[CLASSES[c]], cls=CLASSES[c], p=round(pm, 3),
                                          area_yd2=round(poly.area / YD ** 2))))
    return feats


def write_loho(G, model, Xf, foot, key, margin_m=40):
    """Predict the held-out hole's screenshot footprint (+margin) with the model that never saw it."""
    Hg, Wg = G["shape"]
    m = ndimage.binary_dilation(foot, iterations=int(margin_m / GRID_M))
    idx = np.flatnonzero(m.ravel())
    P = np.zeros((Hg * Wg, len(CLASSES)), np.float32)
    P[idx] = model.predict_proba(Xf[idx])
    P = P.reshape(Hg, Wg, -1)
    cls_map = np.where(m, P.argmax(-1), 255).astype(np.uint8)
    feats = []
    for c in ("trees", "native", "water"):
        ci = CLASSES.index(c)
        feats += polygons(G, P[..., ci], cls_map, ci)
    for f in feats:
        f["properties"]["holdout"] = str(key)
    d = os.path.join(IMG_DIR, "gapfill_loho")
    os.makedirs(d, exist_ok=True)
    json.dump(dict(type="FeatureCollection", features=feats,
                   properties=dict(holdout=str(key), model="classify.py extratrees LOHO (hole %s unseen)" % key)),
              open(os.path.join(d, f"{key}.geojson"), "w"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--n-per-hole", type=int, default=20000)
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    course = TA.load_course()
    regs = json.load(open(os.path.join(IMG_DIR, "traced_registration.json")))
    G = load_grid()
    X, names, ndvi = features(G)
    Hg, Wg = G["shape"]
    Xf = X.reshape(-1, X.shape[-1])
    print("grid", G["shape"], "features", len(names))

    keys = [k for k in course.HOLES if str(k) in regs and str(k) not in BAD_REG]
    labs, foots, full = {}, {}, {}
    for k in keys:
        labs[k], foots[k], full[k] = hole_labels(G, course, k, regs[str(k)])
    samples = {k: sample(labs[k], a.n_per_hole, rng) for k in keys}

    # leave-one-hole-out
    report = dict(grid_m=GRID_M, features=names, holes={}, excluded=sorted(BAD_REG),
                  registration={str(k): dict(corr=regs[str(k)]["corr"], scale=regs[str(k)]["scale"],
                                             rot_deg=regs[str(k)]["rot_deg"]) for k in keys})
    tot_conf = np.zeros((len(CLASSES), len(CLASSES)), np.int64)
    for k in keys:
        tr_idx = np.concatenate([samples[j] for j in keys if j != k])
        ytr = np.concatenate([labs[j].ravel()[samples[j]] for j in keys if j != k])
        m = make_model().fit(Xf[tr_idx], ytr)
        ev = np.flatnonzero(labs[k].ravel() >= 0)
        pred = m.predict(Xf[ev])
        truth = labs[k].ravel()[ev]
        np.add.at(tot_conf, (truth, pred), 1)
        if not a.eval_only:                    # held-out gap-fill polygons for acceptance (circularity rule)
            write_loho(G, m, Xf, foots[k], k)
        sc = scores(pred, truth, np.ones(len(ev), bool))
        report["holes"][str(k)] = sc
        print(flush=True); print(f"{str(k):>3} acc {sc['acc']:.3f}  " + "  ".join(
            f"{nm[:5]} {sc[nm]['iou']:.2f}" if sc[nm]["iou"] is not None else f"{nm[:5]}  -  " for nm in CLASSES))
    tot = {}
    for c, nm in enumerate(CLASSES):
        tp = tot_conf[c, c]
        fp = tot_conf[:, c].sum() - tp
        fn = tot_conf[c, :].sum() - tp
        tot[nm] = dict(iou=float(tp / max(tp + fp + fn, 1)), prec=float(tp / max(tp + fp, 1)),
                       rec=float(tp / max(tp + fn, 1)), n_true=int(tp + fn))
    tot["acc"] = float(np.trace(tot_conf) / tot_conf.sum())
    report["pooled"] = tot
    report["confusion"] = dict(classes=CLASSES, rows_truth_cols_pred=tot_conf.tolist())
    # merged hazard check: is a penal class (trees/native/water) found where traced, ignoring which
    pen = [CLASSES.index(c) for c in ("trees", "native", "water")]
    tp = tot_conf[np.ix_(pen, pen)].sum()
    fn = tot_conf[pen, :].sum() - tp
    fp = tot_conf[:, pen].sum() - tp
    report["penal_any"] = dict(prec=float(tp / (tp + fp)), rec=float(tp / (tp + fn)), iou=float(tp / (tp + fp + fn)))
    print("pooled LOHO acc", round(tot["acc"], 3), {nm: round(tot[nm]["iou"], 2) for nm in CLASSES},
          "penal-any", {k2: round(v, 2) for k2, v in report["penal_any"].items()})
    json.dump(report, open(os.path.join(IMG_DIR, "classify_report.json"), "w"), indent=1)
    if a.eval_only:
        return

    # final model on every hole -> whole-course prediction
    tr_idx = np.concatenate([samples[j] for j in keys])
    ytr = np.concatenate([labs[j].ravel()[samples[j]] for j in keys])
    m = make_model().fit(Xf[tr_idx], ytr)
    P = np.zeros((Hg * Wg, len(CLASSES)), np.float32)
    for i in range(0, Hg * Wg, 500_000):
        P[i:i + 500_000] = m.predict_proba(Xf[i:i + 500_000])
    P = P.reshape(Hg, Wg, -1)
    cls_map = P.argmax(-1).astype(np.uint8)
    pmax = P.max(-1)
    import rasterio
    prof = dict(driver="GTiff", height=Hg, width=Wg, crs=G["crs"], transform=G["transform"],
                tiled=True, blockxsize=256, blockysize=256, compress="deflate")
    with rasterio.open(os.path.join(IMG_DIR, "classes.tif"), "w", count=1, dtype="uint8", **prof) as dst:
        dst.write(cls_map[None])
        dst.update_tags(classes=",".join(CLASSES))
    with rasterio.open(os.path.join(IMG_DIR, "p_hazards.tif"), "w", count=3, dtype="uint8", **prof) as dst:
        for i, c in enumerate(("trees", "native", "water")):
            dst.write(np.round(P[..., CLASSES.index(c)] * 20).astype(np.uint8), i + 1)
        dst.update_tags(bands="p_trees,p_native,p_water in 0.05 steps (value / 20)")
    pal = np.array([[60, 170, 60], [150, 200, 110], [20, 80, 20], [210, 180, 110], [40, 90, 220],
                    [245, 235, 190]], np.uint8)
    from PIL import Image
    Image.fromarray(pal[cls_map]).save(os.path.join(IMG_DIR, "classes.png"), optimize=True)
    feats = []
    for c in ("trees", "native", "water"):
        ci = CLASSES.index(c)
        feats += polygons(G, P[..., ci], cls_map, ci)
    fc = dict(type="FeatureCollection", features=feats,
              properties=dict(source="NAIP " + ",".join(G["meta"]["imagery"]["acquired"]) + " + 3DEP",
                              model="classify.py extratrees ndvi-texture-dem v1", classes=CLASSES,
                              loho_iou={c: round(tot[c]["iou"], 3) for c in CLASSES}))
    json.dump(fc, open(os.path.join(IMG_DIR, "gapfill.geojson"), "w"))
    trees = dict(fc, features=[f for f in feats if f["properties"]["lie"] == "recovery"])
    json.dump(trees, open(os.path.join(IMG_DIR, "naip_trees.geojson"), "w"))
    print("polygons:", {c: sum(f["properties"]["cls"] == c for f in feats) for c in ("trees", "native", "water")})
    write_md(report, os.path.join(IMG_DIR, "classify_report.md"))


def write_md(rep, path):
    L = ["# NAIP hazard classifier: leave-one-hole-out vs the hand-traced maps", "",
         f"Grid {rep['grid_m']} m, {len(rep['features'])} features (NAIP RGB+NIR, NDVI, texture, 3DEP slope / "
         "relative elevation). Labels = spirit_hollow/course.py zones georeferenced by traced_align.py. "
         f"Excluded (registration failed): {', '.join(rep['excluded'])}.", "",
         f"Pooled pixel accuracy **{rep['pooled']['acc']:.3f}**; any-penal-class (trees/native/water) "
         f"precision {rep['penal_any']['prec']:.2f}, recall {rep['penal_any']['rec']:.2f}, IoU {rep['penal_any']['iou']:.2f}.", "",
         "| class | IoU | precision | recall | labelled px |", "|---|---|---|---|---|"]
    for c in CLASSES:
        d = rep["pooled"][c]
        L.append(f"| {c} | {d['iou']:.2f} | {d['prec']:.2f} | {d['rec']:.2f} | {d['n_true']} |")
    L += ["", "Per hole (held out): accuracy and IoU", "",
          "| hole | reg corr | acc | " + " | ".join(CLASSES) + " |", "|---" * (len(CLASSES) + 3) + "|"]
    for k, sc in rep["holes"].items():
        L.append(f"| {k} | {rep['registration'][k]['corr']:.2f} | {sc['acc']:.2f} | " + " | ".join(
            f"{sc[c]['iou']:.2f}" if sc[c]["iou"] is not None else "-" for c in CLASSES) + " |")
    L += ["", "Confusion (rows = traced, cols = predicted): " + ", ".join(CLASSES), "", "```"]
    for c, row in zip(CLASSES, rep["confusion"]["rows_truth_cols_pred"]):
        L.append(f"{c:>8} " + " ".join(f"{v:>8d}" for v in row))
    L += ["```", "",
          "Caveats: the screenshots are winter imagery with tilted canopies and trees traced at the trunks; "
          "NAIP is leaf-on (September) and orthorectified, so tree canopies are legitimately wider than the "
          "traced 'recovery'. Footprints of neighbouring holes overlap, so LOHO is somewhat optimistic."]
    open(path, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
