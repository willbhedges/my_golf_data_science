"""Automatic greens for holes OSM has no golf=green for (national tier C / D, e.g. Old Works MT: 0 greens).

Without a green the package assumes a 24-yd round green at the hole line's end: the par-3 target box and every
approach aim sit on that guess. Greens are the most distinctive surface from the air (mown to a few mm: smooth,
uniform, brighter / darker green than the fairway, 400-900 sq yds, often ringed by sand), so this module finds the
putting surface near the hole line's end from the package imagery, label-free at build time:

  window    +/-WIN_M m around the prior (the hole line's end), resampled to RES_M (NAIP CRS)
  pixels    a LightGBM pixel model (FEATURES): NAIP RGB + NIR (NDVI, ExG, brightness, each also minus the window's
            median: the course's own turf reference), texture (local std of grey / NIR at 1.5 and 3.5 m, gradient),
            context means at 4 and 10 m (a green is smooth inside, rougher around), sand-likeness around (bunkers
            ring greens), lidar HAG (trees, when vision_any/<slug>/raw/hag.tif exists) and the DEM (slope, roughness,
            relief vs 15 m: greens are flat-topped pads). No position feature: the prior enters only in the pick.
  pick      connected components of the smoothed P >= P_THR with area AREA_M2; score = mean P x the area prior x a
            Gaussian in the distance to the prior (PRIOR_SIGMA_M); the best component, cleaned (close / fill), is the
            green when its score >= SCORE_THR and it moves the centre <= MAX_MOVE_YD (calibrated leave-one-course-out,
            eval_green_auto.py), else nothing: the estimate stays.

Evaluation (course_data/product/eval_green_auto.py, EVAL_green_auto.md): leave-one-course-out on the package
courses that have OSM greens (the OSM greens are only the labels / the truth, never a detector input), with the
prior as built (the OSM hole-line end) and moved 10-25 yds off it (what a greenless course's line end can be).

    import green_auto as GA
    m = GA.load_model()
    det = GA.detect_course(slug, pkg, m)              # {ref: {poly_ll, green_ll, score, area_yd2, moved_yd}}
    pkg2, info = GA.build_layer(slug, pkg)            # the package stage (only holes without a mapped green)
CLI: python3 course_data/product/green_auto.py <slug> [--package P] [--out P]
"""
from __future__ import annotations

import copy
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
MODEL_TXT = os.path.join(HERE, "green_auto_model", "model.txt")
MODEL_JSON = os.path.join(HERE, "green_auto_model", "model.json")
SRC = "detector:green_auto"
YD = 0.9144

WIN_M = 70.0            # half window around the prior (m)
RES_M = 0.5             # raster resampling (texture is read at this scale)
STEP = 2                # features / P on every STEP-th pixel (1 m)
P_THR = 0.5
AREA_M2 = (120.0, 1600.0)
AREA_PRIOR_M2 = (300.0, 800.0)   # full credit inside, falls off outside
PRIOR_SIGMA_M = 22.0
SCORE_THR = 0.40        # pick threshold (held-out: 91 % found, 90 % <= 5 yds; the model json may override)
# a detection may move the green's centre at most this far from the estimate: on an OSM hole way (mappers end it on
# the green; held-out, detections moving >= 12 yds off such a line end were <= 5 yds right 19 % of the time vs 62 %
# for the line end) / on a routed or inferred hole line (its end can be 10-25 yds off)
MAX_MOVE_YD = dict(osm=12.0, routed=30.0)
ENABLED = True


# ----------------------------------------------------------------------------- rasters
def sources(slug, root=ROOT, pkg=None):
    """{name: path} of the package imagery (NAIP RGB, NIR, DEM) + the lidar HAG (vision_any raw)."""
    out = {}
    dirs = []
    img = ((pkg or {}).get("imagery") or {}).get("dir")
    if img:
        dirs.append(img if os.path.isabs(img) else os.path.join(root, img))
    dirs += [os.path.join(root, "course_data", "packages", slug, "imagery"), os.path.join(root, "course_data", "imagery", slug)]
    for d in dirs:
        if os.path.exists(os.path.join(d, "naip_rgb.tif")):
            out["rgb"] = os.path.join(d, "naip_rgb.tif")
            for k, f in (("nir", "naip_nir.tif"), ("dem", "dem.tif")):
                if os.path.exists(os.path.join(d, f)):
                    out[k] = os.path.join(d, f)
            break
    raw = [os.path.join(root, "course_data", "vision_any", slug, "raw")] + [
        d if os.path.isabs(d) else os.path.join(root, d) for d in (((pkg or {}).get("sources") or {}).get("vision_raw") or [])]
    for d in raw:
        if os.path.exists(os.path.join(d, "hag.tif")):
            out["hag"] = os.path.join(d, "hag.tif")
            break
    return out


class Course:
    """Open rasters of one course; windows in the NAIP CRS."""

    def __init__(self, paths):
        import rasterio
        from pyproj import Transformer
        self.paths = paths
        self.ds = {k: rasterio.open(p) for k, p in paths.items()}
        self.crs = self.ds["rgb"].crs
        self.tf = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
        self.inv = Transformer.from_crs(self.crs, "EPSG:4326", always_xy=True)

    def close(self):
        for d in self.ds.values():
            d.close()

    def fwd(self, ll):
        ll = np.asarray(ll, float).reshape(-1, 2)
        x, y = self.tf.transform(ll[:, 0], ll[:, 1])
        return np.c_[x, y]

    def back(self, xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        x, y = self.inv.transform(xy[:, 0], xy[:, 1])
        return np.c_[x, y]

    def window(self, cx, cy, half=WIN_M, res=RES_M):
        """{name: array (H, W[, bands])} on a north-up grid centred at (cx, cy), plus the grid transform."""
        from rasterio.transform import from_origin
        from rasterio.warp import Resampling, reproject
        n = int(round(2 * half / res))
        T = from_origin(cx - half, cy + half, res, res)
        out = dict(T=T, n=n, res=res, x0=cx - half, y0=cy + half)
        for k, d in self.ds.items():
            bands = d.count if k == "rgb" else 1
            arr = np.full((bands, n, n), np.nan, np.float32)
            for b in range(bands):
                src_nodata = d.nodata
                if k == "hag":
                    src_nodata = 255
                reproject(source=__import__("rasterio").band(d, b + 1), destination=arr[b], dst_transform=T,
                          dst_crs=self.crs, src_nodata=src_nodata, dst_nodata=np.nan,
                          resampling=Resampling.nearest if k == "hag" else Resampling.bilinear)
            if k == "hag":
                arr = arr * 0.25
            out[k] = arr if bands > 1 else arr[0]
        return out

    def to_px(self, w, xy):
        """map xy -> (col, row) float pixel of window w."""
        xy = np.asarray(xy, float).reshape(-1, 2)
        return np.c_[(xy[:, 0] - w["x0"]) / w["res"], (w["y0"] - xy[:, 1]) / w["res"]]

    def to_xy(self, w, cr):
        cr = np.asarray(cr, float).reshape(-1, 2)
        return np.c_[w["x0"] + cr[:, 0] * w["res"], w["y0"] - cr[:, 1] * w["res"]]


# ----------------------------------------------------------------------------- features
FEATURES = ["r", "g", "b", "nir", "ndvi", "exg", "bright", "ndvi_d", "bright_d", "nir_d", "exg_d",
            "sd_g3", "sd_g7", "sd_n3", "sd_n7", "grad", "sd_g7_c4", "sd_g7_c10", "ndvi_c4", "ndvi_c10",
            "bright_c4", "bright_c10", "ndvi_ring", "bright_ring", "sd_ring", "sand_c6", "sand_c15",
            "hag", "tree_c3", "tree_c8", "slope", "rough", "relief15", "relief6"]


def _g(a, s):
    from scipy.ndimage import gaussian_filter
    m = np.isfinite(a)
    if m.all():
        return gaussian_filter(a, s, mode="nearest")
    v = gaussian_filter(np.where(m, a, 0.0), s, mode="nearest")
    wgt = gaussian_filter(m.astype(float), s, mode="nearest")
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(wgt > 0.05, v / np.maximum(wgt, 1e-6), np.nan)


def _lstd(a, k):
    from scipy.ndimage import uniform_filter
    a = np.nan_to_num(a, nan=float(np.nanmedian(a)) if np.isfinite(a).any() else 0.0)
    m = uniform_filter(a, k, mode="nearest")
    m2 = uniform_filter(a * a, k, mode="nearest")
    return np.sqrt(np.maximum(m2 - m * m, 0.0))


def features(w):
    """(F (n/STEP, n/STEP, len(FEATURES)) float32) for a window from Course.window."""
    res = w["res"]
    rgb = w["rgb"].astype(np.float64)
    r, g, b = rgb[0], rgb[1], rgb[2]
    nir = w["nir"].astype(np.float64) if "nir" in w else np.full_like(r, np.nan)
    bright = (r + g + b) / 3.0
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (nir - r) / np.maximum(nir + r, 1.0)
    exg = 2 * g - r - b
    med = lambda a: float(np.nanmedian(a)) if np.isfinite(a).any() else 0.0      # noqa: E731
    iqr = lambda a: max(float(np.nanpercentile(a, 75) - np.nanpercentile(a, 25)), 1e-3) if np.isfinite(a).any() else 1.0  # noqa: E731
    k3, k7 = max(3, int(round(1.5 / res))) | 1, max(5, int(round(3.5 / res))) | 1
    sd_g3, sd_g7 = _lstd(g, k3), _lstd(g, k7)
    sd_n3, sd_n7 = (_lstd(nir, k3), _lstd(nir, k7)) if np.isfinite(nir).any() else (np.full_like(r, np.nan),) * 2
    gy, gx = np.gradient(_g(bright, 0.6 / res))
    grad = _g(np.hypot(gx, gy), 1.0 / res)
    s4, s10 = 4.0 / res, 10.0 / res
    sand = ((bright - med(bright)) / iqr(bright) - (np.nan_to_num(ndvi, nan=med(ndvi)) - med(ndvi)) / iqr(ndvi)) > 2.5
    sand = sand.astype(float)
    F = dict(r=r, g=g, b=b, nir=nir, ndvi=ndvi, exg=exg, bright=bright,
             ndvi_d=ndvi - med(ndvi), bright_d=bright - med(bright), nir_d=nir - med(nir), exg_d=exg - med(exg),
             sd_g3=sd_g3, sd_g7=sd_g7, sd_n3=sd_n3, sd_n7=sd_n7, grad=grad,
             sd_g7_c4=_g(sd_g7, s4), sd_g7_c10=_g(sd_g7, s10), ndvi_c4=_g(ndvi, s4), ndvi_c10=_g(ndvi, s10),
             bright_c4=_g(bright, s4), bright_c10=_g(bright, s10))
    F["ndvi_ring"] = F["ndvi_c4"] - F["ndvi_c10"]
    F["bright_ring"] = F["bright_c4"] - F["bright_c10"]
    F["sd_ring"] = F["sd_g7_c4"] - F["sd_g7_c10"]
    F["sand_c6"], F["sand_c15"] = _g(sand, 6.0 / res), _g(sand, 15.0 / res)
    if "hag" in w and np.isfinite(w["hag"]).any():
        hag = w["hag"].astype(np.float64)
        tree = np.where(np.isfinite(hag), (hag > 2.5).astype(float), np.nan)
        F["hag"], F["tree_c3"], F["tree_c8"] = hag, _g(tree, 3.0 / res), _g(tree, 8.0 / res)
    else:
        F["hag"] = F["tree_c3"] = F["tree_c8"] = np.full_like(r, np.nan)
    if "dem" in w and np.isfinite(w["dem"]).any():
        z = _g(w["dem"].astype(np.float64), 1.0 / res)
        zy, zx = np.gradient(z, res)
        F["slope"] = _g(np.hypot(zx, zy), 1.0 / res)
        F["rough"] = _g(np.abs(z - _g(z, 3.0 / res)), 2.0 / res)
        F["relief15"] = z - _g(z, 15.0 / res)
        F["relief6"] = z - _g(z, 6.0 / res)
    else:
        F["slope"] = F["rough"] = F["relief15"] = F["relief6"] = np.full_like(r, np.nan)
    o = STEP // 2
    return np.stack([F[k][o::STEP, o::STEP] for k in FEATURES], -1).astype(np.float32)


def grid_xy(w):
    """Map xy of the feature grid cells (n/STEP)^2 x 2."""
    o = STEP // 2
    idx = np.arange(o, w["n"], STEP) + 0.5
    cc, rr = np.meshgrid(idx, idx)
    return np.c_[w["x0"] + cc.ravel() * w["res"], w["y0"] - rr.ravel() * w["res"]]


# ----------------------------------------------------------------------------- model
def load_model(path=MODEL_TXT):
    import lightgbm as lgb
    if not os.path.exists(path):
        return None
    meta = {}
    if os.path.exists(MODEL_JSON):
        meta = json.load(open(MODEL_JSON))
    return dict(booster=lgb.Booster(model_file=path), meta=meta, score_thr=float(meta.get("score_thr", SCORE_THR)))


def predict_p(model, F):
    b = model["booster"] if isinstance(model, dict) else model
    sh = F.shape
    return b.predict(F.reshape(-1, sh[-1])).reshape(sh[:2])


# ----------------------------------------------------------------------------- pick
def components(P, step_m):
    """[(mask, mean P, area m2)] of the smoothed P >= P_THR."""
    import cv2
    from scipy.ndimage import gaussian_filter
    Ps = gaussian_filter(P, 1.0)
    m = (Ps >= P_THR).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab = cv2.connectedComponents(m, connectivity=4)
    out = []
    for i in range(1, n):
        mk = lab == i
        a = float(mk.sum()) * step_m * step_m
        if a < AREA_M2[0] * 0.5:
            continue
        out.append((mk, float(Ps[mk].mean()), a))
    return out, Ps


def area_prior(a):
    lo, hi = AREA_PRIOR_M2
    if a < AREA_M2[0] or a > AREA_M2[1]:
        return 0.0
    if a < lo:
        return float(math.exp(-((lo - a) / 120.0) ** 2))
    if a > hi:
        return float(math.exp(-((a - hi) / 350.0) ** 2))
    return 1.0


def split_big(mk, Ps, step_m):
    """A component bigger than a green (green + collar + fairway): the component itself plus the pieces left at
    higher P thresholds (the pick scores them all; the green-sized, high-P piece usually wins) -> list of masks."""
    import cv2
    a = mk.sum() * step_m * step_m
    out = [mk]
    if a <= AREA_PRIOR_M2[1]:
        return out
    for t in (0.6, 0.7, 0.8, 0.88, 0.94):
        m2 = (mk & (Ps >= t)).astype(np.uint8)
        n, lab = cv2.connectedComponents(m2, connectivity=4)
        parts = [lab == i for i in range(1, n) if (lab == i).sum() * step_m * step_m >= AREA_M2[0]]
        out += parts
        if not parts:
            break
    return out


def clean(mk):
    import cv2
    from scipy.ndimage import binary_fill_holes
    m = cv2.morphologyEx(mk.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    return binary_fill_holes(m > 0)


def pick(P, w, prior_xy, sigma=PRIOR_SIGMA_M):
    """Best green component near the prior -> dict(mask, score, p, area_m2, cx, cy) or None."""
    step_m = w["res"] * STEP
    comps, Ps = components(P, step_m)
    o = STEP // 2
    best = None
    for mk0, _, _ in comps:
        for mk in split_big(mk0, Ps, step_m):
            mk = clean(mk)
            a = float(mk.sum()) * step_m * step_m
            ap = area_prior(a)
            if ap <= 0:
                continue
            rr, cc = np.nonzero(mk)
            cx = w["x0"] + (cc.mean() * STEP + o + 0.5) * w["res"]
            cy = w["y0"] - (rr.mean() * STEP + o + 0.5) * w["res"]
            d = math.hypot(cx - prior_xy[0], cy - prior_xy[1])
            pm = float(Ps[mk].mean())
            s = pm * ap * math.exp(-0.5 * (d / sigma) ** 2)
            if best is None or s > best["score"]:
                best = dict(mask=mk, score=s, p=pm, area_m2=a, cx=cx, cy=cy, d_prior_m=d)
    return best


def mask_polygon(mk, w):
    """Mask on the feature grid -> shapely polygon in map xy (largest ring, simplified)."""
    import cv2
    from shapely.geometry import Polygon
    cs, _ = cv2.findContours(mk.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs:
        return None
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(float)
    o = STEP // 2
    xy = np.c_[w["x0"] + (c[:, 0] * STEP + o + 0.5) * w["res"], w["y0"] - (c[:, 1] * STEP + o + 0.5) * w["res"]]
    if len(xy) < 3:
        return None
    p = Polygon(xy).buffer(0.5 * STEP * w["res"], join_style=1).simplify(0.4)
    if p.geom_type != "Polygon":
        p = max(getattr(p, "geoms", [p]), key=lambda q: q.area)
    return p


def prior_of(h):
    """The prior green position (lon, lat): the package green when it is only an estimate, else the line end."""
    if h.get("green_ll"):
        return [float(v) for v in h["green_ll"][:2]]
    line = h.get("hole_line_ll") or []
    return [float(v) for v in line[-1][:2]] if line else None


def detect_hole(course, model, prior_ll, sigma=PRIOR_SIGMA_M, return_p=False):
    """-> dict(poly_ll, green_ll, score, p, area_yd2, moved_yd) | None for one hole."""
    pxy = course.fwd([prior_ll])[0]
    w = course.window(pxy[0], pxy[1])
    F = features(w)
    P = predict_p(model, F)
    best = pick(P, w, pxy, sigma)
    if best is None:
        return (None, P, w) if return_p else None
    poly = mask_polygon(best["mask"], w)
    if poly is None or poly.is_empty:
        return (None, P, w) if return_p else None
    ring = course.back(np.asarray(poly.exterior.coords)[:-1])
    c = course.back([[poly.centroid.x, poly.centroid.y]])[0]
    out = dict(poly_ll=[[round(float(x), 7), round(float(y), 7)] for x, y in ring],
               green_ll=[round(float(c[0]), 7), round(float(c[1]), 7)], score=round(best["score"], 3),
               p=round(best["p"], 3), area_yd2=round(poly.area / (YD * YD)), moved_yd=round(best["d_prior_m"] / YD, 1))
    return (out, P, w) if return_p else out


def detect_course(slug, pkg, model=None, holes=None, root=ROOT):
    """{ref: detection | None} for the holes asked (default: every hole without a mapped green)."""
    model = model or load_model()
    paths = sources(slug, root, pkg)
    if model is None or "rgb" not in paths:
        return {}
    co = Course(paths)
    out = {}
    try:
        for ref, h in pkg["holes"].items():
            if holes is not None and ref not in holes:
                continue
            if holes is None and mapped_green(h):
                continue
            pr = prior_of(h)
            if pr is None:
                continue
            out[ref] = detect_hole(co, model, pr)
    finally:
        co.close()
    return out


def routed_line(h):
    """The hole line is the router's / an inference (not an OSM golf=hole way)."""
    return bool(h.get("inferred")) or str((h.get("provenance") or {}).get("hole", "")).startswith("routing")


def estimated_green(h):
    """The hole's green is only the hole-line-end estimate (no OSM / review / segment / mapper outline)."""
    return str((h.get("provenance") or {}).get("green") or "hole_line_end") == "hole_line_end" or not h.get("green_polygon_ll")


def mapped_green(h):
    src = str((h.get("provenance") or {}).get("green") or "")
    return bool(h.get("green_polygon_ll")) and (src.startswith("osm") or src.startswith("review") or src.startswith("agent"))


# ----------------------------------------------------------------------------- package stage
def build_layer(slug, pkg, model=None, root=ROOT, force=False):
    """The package stage: holes with no mapped green (OSM / review / mapper) get the detector's green when its score
    clears the calibrated threshold (mapper/apply.green_op: outline, centre, tee lengths / aims / elevation).
    Holes below the threshold keep the assumed green; every detection is recorded in hole.green_detected.
    -> (package, info)."""
    if not ENABLED and not force:
        return pkg, dict(status="off (green_auto.ENABLED = False)")
    model = model or load_model()
    if model is None:
        return pkg, dict(status="missing (no green_auto_model/model.txt)")
    todo = [ref for ref, h in pkg["holes"].items() if estimated_green(h)]
    if not todo:
        return pkg, dict(status="not needed: no hole has only the estimated green")
    if "rgb" not in sources(slug, root, pkg):
        return pkg, dict(status="not run (no NAIP imagery)")
    det = detect_course(slug, pkg, model, holes=set(todo), root=root)
    sys.path.insert(0, os.path.join(CD, "mapper"))
    import apply as AP
    PK = AP.platform_package()
    p = copy.deepcopy(pkg)
    sample = None
    if p.get("elevation"):
        try:
            sample = PK.dem_sampler(os.path.join(root, p["elevation"]["file"]))
        except Exception:                                          # noqa: BLE001
            sample = None
    used, low = [], []
    thr = model["score_thr"]
    for ref in todo:
        d = det.get(ref)
        h = p["holes"][ref]
        if d is None:
            h["green_detected"] = None
            continue
        cap = MAX_MOVE_YD["routed" if routed_line(h) else "osm"]
        ok = d["score"] >= thr and d["moved_yd"] <= cap
        h["green_detected"] = dict(d, used=ok, thr=thr, max_move_yd=cap)
        if not ok:
            low.append(ref)
            continue
        f = dict(type="Feature", properties=dict(op="green", lie="green", score=d["score"], evidence=(
            f"green_auto: P {d['p']:.2f}, {d['area_yd2']} sq yds, {d['moved_yd']:.0f} yds from the estimate")),
            geometry=dict(type="Polygon", coordinates=[d["poly_ll"] + [d["poly_ll"][0]]]))
        AP.green_op(h, f, PK, sample, src=SRC)
        used.append(ref)
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        out = PK.reframe(p)
    info = dict(status=f"ok: {len(used)} of {len(todo)} hole(s) without a mapped green got a detected green "
                       f"(score >= {thr:.2f}, centre moved <= {MAX_MOVE_YD['osm']:g} / {MAX_MOVE_YD['routed']:g} yds on OSM / routed "
                       f"lines)" + (f"; not used (score / move): {', '.join(low)}" if low else "")
                       + (f"; none found: {', '.join(r for r in todo if det.get(r) is None)}"
                          if any(det.get(r) is None for r in todo) else ""),
                used=used, low=low, todo=todo)
    return out, info


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--package")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    src = a.package or os.path.join(CD, "packages", a.slug, "package.json")
    pkg = json.load(open(src))
    out, info = build_layer(a.slug, pkg, force=True)
    print(info["status"])
    for ref in info.get("todo", []):
        d = out["holes"][ref].get("green_detected")
        print(f"  {ref}: " + (f"score {d['score']:.2f} p {d['p']:.2f} {d['area_yd2']} sq yds moved {d['moved_yd']} yds"
                               f"{' USED' if d['used'] else ''}" if d else "none"))
    if a.out:
        json.dump(out, open(a.out, "w"))
        print("->", a.out)


if __name__ == "__main__":
    main()
