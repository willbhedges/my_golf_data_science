"""Perception scene in the fast path: NAIP RGB + NIR, the 3DEP DEM and Meta canopy height -> course_scene/1.

The slow pipeline's perception scene (course_data/perception/, perceive.py) reads a stack whose `seg` layer is the
NAIP U-Net (segment/model.py, ariadgolf/golf-course-segmentation, torch). The fast path has no torch and no
Hugging Face access, so here `seg` comes from a small per-pixel LightGBM classifier (6 classes: background, green,
tee, fairway, bunker, water) on the green_auto-style NAIP / texture / context / canopy / DEM features below, trained
on the course_data/packages courses' OSM polygons (train_pixel.py). Everything after `seg` is the perception code,
unchanged: perceive.run (greens, tee boxes + lidar pads, complexes, fairways, bunkers, water, trees, ...) and
scene.build_scene.

    st  = grid_stack(pkg_dir)                  # perception Stack on the 1 m DEM grid (seg empty)
    F   = features(st)                         # (len(FEATURES), H, W) float32
    P   = predict(model, F, mask)              # (6, H, W) class probabilities
    scene, info = build(pkg_dir)               # the whole thing -> pkg_dir/scene.json

Kernels: features() and the tree-ensemble predict have C versions (course_data/platform/fastc/perception/,
`impl="c"`), numpy / LightGBM references kept here (`impl="py"`); test_fastscene.py asserts they agree.
"""
from __future__ import annotations

import os as _os
_os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")   # before any OpenMP runtime loads (lightgbm, sklearn,
# fastc): spinning OpenMP threads otherwise steal the cores OpenBLAS needs in the U-Net (31 s -> 62 s on Yorba Linda)
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
PERC = os.path.join(CD, "perception")
MODEL_DIR = os.path.join(HERE, "fastscene_model")
CLASSES = ("background", "green", "tee", "fairway", "bunker", "water")
SEG_ORDER = ("green", "tee", "fairway", "bunker", "water")          # perception stack.SEG
GREEN_P = 0.5               # green candidate threshold on the seg layer (perception detect.GREEN_P)
FAIRWAY_P, BUNKER_P, TEE_P = 0.3, 0.4, 0.4      # seg thresholds for detect (perception's: 0.5 / 0.5 / 0.4; chosen on
                                                # VAL 51 for our U-Net: fairway F1 0.862 -> 0.875; FASTSCENE_* to sweep)
COMPLEX_GAP_M, COMPLEX_MERGE_M = 10.0, 70.0     # tee boxes -> complexes (perception detect's)
PAD_M = 40.0                   # the classifier runs inside the course outline + this


# perception/ has modules named like other folders' (scene: structure/scene.py; truth: zero_tap/truth.py; features,
# paths, geo, ...). They are imported and called only inside perception_ns(): the names point at perception's
# modules there and at whatever they were before outside it (stage_select's structure solver imports `scene`).
PERC_NAMES = ("stack", "detect", "features", "paths", "perceive", "scene", "geo", "truth", "evaluate", "split",
              "train", "fetch_stack", "report", "route_check")
_PERC_MODS = {}
_DEPTH = [0]


class perception_ns:
    def __enter__(self):
        _DEPTH[0] += 1
        if _DEPTH[0] > 1:
            return self
        self.saved = {n: sys.modules.pop(n) for n in PERC_NAMES if n in sys.modules}
        sys.modules.update(_PERC_MODS)
        sys.path.insert(0, PERC)
        return self

    def __exit__(self, *exc):
        _DEPTH[0] -= 1
        if _DEPTH[0] > 0:
            return False
        try:
            sys.path.remove(PERC)
        except ValueError:
            pass
        for n in PERC_NAMES:
            if n in sys.modules:
                _PERC_MODS[n] = sys.modules.pop(n)
        sys.modules.update(self.saved)
        return False


def _perc():
    """perception's stack module (the Stack class needs no other perception module at call time)."""
    with perception_ns():
        import stack as S
    return S


# ----------------------------------------------------------------------------- grid
def find_inputs(pkg_dir):
    img = os.path.join(pkg_dir, "imagery")
    out = dict(rgb=os.path.join(img, "naip_rgb.tif"), nir=os.path.join(img, "naip_nir.tif"),
               dem=os.path.join(img, "dem.tif"), chm=os.path.join(pkg_dir, "canopy", "chm_meta.tif"))
    return {k: v for k, v in out.items() if os.path.exists(v)}


def grid_stack(pkg_dir, chm=None, course=None, labels=None):
    """A perception Stack (1 m, the DEM's UTM grid) from the fast-path imagery: naip = NAIP 0.6 m area-averaged,
    hag = Meta canopy height (0.25 m units, 255 none), dtm = the 3DEP DEM, seg zeros (filled by build()).
    cls / inten are empty (no point cloud in the fast path)."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    S = _perc()
    src = find_inputs(pkg_dir)
    if chm:
        src["chm"] = chm
    if "rgb" not in src:
        raise FileNotFoundError("no NAIP in " + pkg_dir)
    course = course or json.load(open(os.path.join(pkg_dir, "raw", "course.json")))
    with rasterio.open(src["dem"] if "dem" in src else src["rgb"]) as d:
        crs, tr = d.crs, d.transform
        H, W = d.height, d.width
        if "dem" not in src:                                     # a 1 m grid over the NAIP bounds
            b = d.bounds
            tr = rasterio.transform.from_origin(math.floor(b.left), math.ceil(b.top), 1.0, 1.0)
            W, H = int(b.right - b.left), int(b.top - b.bottom)
            dem = None
        else:
            dem = d.read(1).astype(np.float32)
            if d.nodata is not None and np.isfinite(d.nodata):
                dem[dem == d.nodata] = np.nan
            dem[dem < -1000] = np.nan

    def warp(path, band, how, nodata, dtype=np.float32):
        out = np.full((H, W), np.nan, np.float32)
        with rasterio.open(path) as s:
            reproject(rasterio.band(s, band), out, src_nodata=nodata, dst_nodata=np.nan, dst_transform=tr,
                      dst_crs=crs, resampling=how)
        return out
    naip = np.zeros((4, H, W), np.uint8)
    for b in range(3):
        a = warp(src["rgb"], b + 1, Resampling.average, 0)
        naip[b] = np.nan_to_num(a, nan=0).round().clip(0, 255).astype(np.uint8)
    if "nir" in src:
        a = warp(src["nir"], 1, Resampling.average, 0)
        naip[3] = np.nan_to_num(a, nan=0).round().clip(0, 255).astype(np.uint8)
    hag = np.full((H, W), 255, np.uint8)
    if "chm" in src:
        a = warp(src["chm"], 1, Resampling.nearest, 255)
        hag = np.where(np.isfinite(a), np.clip(np.round(a * 4), 0, 254), 255).astype(np.uint8)
    dtm = np.full((H, W), 65535, np.uint16)
    base = None
    if dem is not None and np.isfinite(dem).any():
        base = float(np.floor(np.nanmin(dem)))
        dtm = np.where(np.isfinite(dem), np.clip(np.round((dem - base) * 100), 0, 65534), 65535).astype(np.uint16)
    from pyproj import Transformer
    inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    x0, y1 = tr.c, tr.f
    lo, la = inv.transform([x0, x0 + W], [y1 - H, y1])
    meta = dict(schema="perception_stack/1", slug=course.get("slug"), name=course.get("name"), state=course.get("state"),
                bbox_wsen=course.get("bbox"), dtm_base_m=base,
                grid=dict(crs=str(crs), res_m=1.0, width=W, height=H, transform=[1.0, 0, x0, 0, -1.0, y1],
                          bounds=[x0, y1 - H, x0 + W, y1], ll_bbox_wsen=[lo[0], la[0], lo[1], la[1]]),
                course={k: course.get(k) for k in ("name", "osm", "center", "bbox", "state", "town")},
                boundary=course.get("boundary"), source="fastpath (NAIP + 3DEP DEM + Meta canopy)",
                hag_source="Meta/WRI canopy height 1 m" if "chm" in src else None)
    arr = dict(naip=naip, seg=np.zeros((5, H, W), np.uint8), hag=hag, cls=np.zeros((H, W), np.uint8),
               inten=np.zeros((H, W), np.uint8), dtm=dtm)
    return S.Stack(arr, meta, labels)


def course_mask(st, pad_m=PAD_M):
    """Pixels inside the OSM course outline(s) + pad_m (the whole grid when there is no outline)."""
    import cv2
    b = st.meta.get("boundary")
    m = np.zeros((st.H, st.W), np.uint8)
    rings = []
    if b:
        polys = b["coordinates"] if b["type"] == "MultiPolygon" else [b["coordinates"]] if b["type"] == "Polygon" else []
        for p in polys:
            if p:
                rings.append(p[0])
    if not rings:
        return np.ones((st.H, st.W), bool)
    for r in rings:
        rr, cc = st.ll_to_rc(np.array([q[0] for q in r]), np.array([q[1] for q in r]))
        pts = np.round(np.c_[cc, rr]).astype(np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(m, [pts], 1)
    if pad_m > 0:
        k = int(round(pad_m / st.res))
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    return m.astype(bool) & st.valid()


# ----------------------------------------------------------------------------- features
FEATURES = ["r", "g", "b", "nir", "ndvi", "exg", "bright", "ndvi_d", "bright_d", "nir_d", "exg_d",
            "sd_g3", "sd_g5", "sd_n3", "sd_n5", "grad",
            "sd_g5_c4", "sd_g5_c10", "ndvi_c4", "ndvi_c10", "ndvi_c25", "bright_c4", "bright_c10", "bright_c25",
            "ndvi_ring", "bright_ring", "sd_ring", "sand_c6", "sand_c15",
            "hag", "tree_c3", "tree_c8", "tree_c20", "slope", "rough", "relief6", "relief15", "relief40"]


def turf_ref(r, g, b, nir, hag, valid):
    """The course's own mown-turf reference (medians over the greener half of low, open ground): NAIP radiometry
    differs between states / years, so the _d features are relative to it. -> dict of medians + IQRs."""
    bright = (r + g + b) / 3.0
    ndvi = (nir - r) / np.maximum(nir + r, 1.0)
    low = valid & ((hag < 1.0) | ~np.isfinite(hag))
    v = ndvi[low]
    if v.size < 500:
        low, v = valid, ndvi[valid]
    thr = np.percentile(v, 50) if v.size else 0.0
    m = low & (ndvi >= thr)
    if m.sum() < 200:
        m = valid
    ex = 2 * g - r - b

    def q(a):
        x = a[m]
        return (float(np.median(x)) if x.size else 0.0,
                max(float(np.percentile(x, 75) - np.percentile(x, 25)), 1e-3) if x.size else 1.0)
    return dict(ndvi=q(ndvi), bright=q(bright), nir=q(nir), exg=q(ex))


def _g(a, s):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(a, s, mode="nearest", truncate=3.0)


def _lstd(a, k):
    from scipy.ndimage import uniform_filter
    m = uniform_filter(a, k, mode="nearest")
    m2 = uniform_filter(a * a, k, mode="nearest")
    return np.sqrt(np.maximum(m2 - m * m, 0.0))


def features_py(st, ref=None):
    """numpy reference of the feature stack: (len(FEATURES), H, W) float32. NaN-free: missing NIR / canopy / DEM
    become 0 / 0 / flat (the model sees the course as it is fetched)."""
    n = st.a["naip"].astype(np.float32)
    r, g, b, nir = n[0], n[1], n[2], n[3]
    valid = st.valid()
    hag = st.a["hag"].astype(np.float32) * 0.25
    hag[st.a["hag"] == 255] = 0.0
    zr = st.a["dtm"]
    z = zr.astype(np.float32) / 100.0
    if (zr != 65535).any():
        z[zr == 65535] = float(np.median(z[zr != 65535]))
    else:
        z[:] = 0.0
    ref = ref or turf_ref(r, g, b, nir, np.where(st.a["hag"] == 255, np.nan, hag), valid)
    bright = (r + g + b) / 3.0
    ndvi = (nir - r) / np.maximum(nir + r, 1.0)
    exg = 2 * g - r - b
    F = dict(r=r, g=g, b=b, nir=nir, ndvi=ndvi, exg=exg, bright=bright,
             ndvi_d=ndvi - ref["ndvi"][0], bright_d=bright - ref["bright"][0], nir_d=nir - ref["nir"][0],
             exg_d=exg - ref["exg"][0])
    F["sd_g3"], F["sd_g5"] = _lstd(g, 3), _lstd(g, 5)
    F["sd_n3"], F["sd_n5"] = _lstd(nir, 3), _lstd(nir, 5)
    bs = _g(bright, 1.0)
    gy, gx = np.gradient(bs)
    F["grad"] = _g(np.hypot(gx, gy), 1.0)
    for s in (4, 10):
        F[f"sd_g5_c{s}"] = _g(F["sd_g5"], s)
    for s in (4, 10, 25):
        F[f"ndvi_c{s}"] = _g(ndvi, s)
        F[f"bright_c{s}"] = _g(bright, s)
    F["ndvi_ring"] = F["ndvi_c4"] - F["ndvi_c10"]
    F["bright_ring"] = F["bright_c4"] - F["bright_c10"]
    F["sd_ring"] = F["sd_g5_c4"] - F["sd_g5_c10"]
    sand = (((bright - ref["bright"][0]) / ref["bright"][1] - (ndvi - ref["ndvi"][0]) / ref["ndvi"][1]) > 2.5).astype(np.float32)
    F["sand_c6"], F["sand_c15"] = _g(sand, 6), _g(sand, 15)
    tree = (hag > 2.5).astype(np.float32)
    F["hag"] = hag
    F["tree_c3"], F["tree_c8"], F["tree_c20"] = _g(tree, 3), _g(tree, 8), _g(tree, 20)
    zs = _g(z, 1.0)
    zy, zx = np.gradient(zs)
    F["slope"] = _g(np.hypot(zx, zy), 1.0)
    F["rough"] = _g(np.abs(zs - _g(zs, 3)), 2)
    F["relief6"] = zs - _g(zs, 6)
    F["relief15"] = zs - _g(zs, 15)
    F["relief40"] = zs - _g(zs, 40)
    return np.stack([np.asarray(F[k], np.float32) for k in FEATURES])


def features(st, impl="auto", ref=None):
    if impl in ("auto", "c"):
        try:
            sys.path.insert(0, os.path.join(PLAT, "fastc", "perception"))
            import fastperc
            return fastperc.features(st, ref)
        except Exception:                                        # noqa: BLE001
            if impl == "c":
                raise
    return features_py(st, ref)


# ----------------------------------------------------------------------------- labels (training / evaluation only)
WATER_GOLF = ("water_hazard", "lateral_water_hazard")


def label_raster(st, fc):
    """OSM polygons -> int8 (H, W): 0 background, 1 green, 2 tee, 3 fairway, 4 bunker, 5 water, -1 unknown
    (a 1.5 m band round every labelled edge, where NAIP and OSM disagree by a pixel or two)."""
    import cv2
    lab = np.zeros((st.H, st.W), np.int8)
    order = (("fairway", 3), ("water", 5), ("tee", 2), ("bunker", 4), ("green", 1))   # later wins
    edge = np.zeros((st.H, st.W), np.uint8)
    for name, k in order:
        m = np.zeros((st.H, st.W), np.uint8)
        for f in fc["features"]:
            p, geom = f.get("properties") or {}, f.get("geometry") or {}
            golf = p.get("golf")
            hit = golf == name or (name == "water" and (golf in WATER_GOLF or p.get("natural") == "water"
                                                        or p.get("water") is not None))
            if name == "fairway" and golf == "driving_range":
                hit = False
            if not hit or geom.get("type") not in ("Polygon", "MultiPolygon"):
                continue
            polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
            for poly in polys:
                for j, ring in enumerate(poly):
                    rr, cc = st.ll_to_rc(np.array([q[0] for q in ring]), np.array([q[1] for q in ring]))
                    pts = np.round(np.c_[cc, rr]).astype(np.int32).reshape(-1, 1, 2)
                    cv2.fillPoly(m, [pts], 0 if j else 1)
                    cv2.polylines(edge, [pts], True, 1, thickness=3)
        lab[m > 0] = k
    lab[edge > 0] = -1
    return lab


# ----------------------------------------------------------------------------- model
def load_model(d=MODEL_DIR):
    import lightgbm as lgb
    p = os.path.join(d, "model.txt")
    if not os.path.exists(p):
        return None
    meta = json.load(open(os.path.join(d, "model.json"))) if os.path.exists(os.path.join(d, "model.json")) else {}
    return dict(booster=lgb.Booster(model_file=p), meta=meta, path=p)


def _rows_predict(model, F, idx, impl):
    C = F.shape[0]
    if impl in ("auto", "c"):
        try:
            sys.path.insert(0, os.path.join(PLAT, "fastc", "perception"))
            import fastperc
            return fastperc.gbm_predict(model, fastperc.gather(F, idx))
        except Exception:                                        # noqa: BLE001
            if impl == "c":
                raise
    X = np.ascontiguousarray(F.reshape(C, -1)[:, idx].T)
    return model["booster"].predict(X, num_threads=os.cpu_count() or 4)


CASCADE_STEP = 2            # coarse pass on every 2nd pixel of every 2nd row
CASCADE_BG = 0.97           # ... a pixel whose 3 x 3 coarse neighbours are all this sure of background keeps the
                            # coarse answer; every other pixel in the mask is classified at 1 m


def predict(model, F, mask, impl="auto", cascade=False):
    P = _predict(model, F, mask, impl, cascade)
    w = os.environ.get("FASTSCENE_PRIOR")
    w = [float(x) for x in w.split(",")] if w else (model.get("meta") or {}).get("prior_scale")
    if w:                                        # training used class-balanced weights: shift back toward the
        w = np.asarray(w, np.float32)[:, None, None]      # course's real class frequencies (model.json, chosen on
        P *= w                                   # the validation courses, train_pixel.py calib)
        P /= P.sum(0, keepdims=True)
    return P


def _predict(model, F, mask, impl="auto", cascade=False):
    """(6, H, W) float32 class probabilities inside mask (background = 1 outside). cascade: classify a 2 m grid
    first; pixels whose coarse neighbourhood is confidently background (> CASCADE_BG) take the coarse answer, the
    rest (turf, sand, water and their edges) are classified at 1 m. cascade=False classifies every pixel."""
    C, H, W = F.shape
    K = len(CLASSES)
    P = np.zeros((K, H, W), np.float32)
    P[0] = 1.0
    if not mask.any():
        return P
    Pf = P.reshape(K, -1)
    if not cascade:
        idx = np.flatnonzero(mask.ravel())
        Pf[:, idx] = _rows_predict(model, F, idx, impl).T.astype(np.float32)
        return P
    from scipy import ndimage as ndi
    s = CASCADE_STEP
    sub = np.zeros_like(mask)
    sub[::s, ::s] = True
    # coarse cells: every grid node within (the mask dilated by one coarse step)
    near = ndi.binary_dilation(mask, iterations=s) & sub
    idx = np.flatnonzero(near.ravel())
    pr = _rows_predict(model, F, idx, impl).astype(np.float32)
    Pc = np.zeros((K, (H + s - 1) // s, (W + s - 1) // s), np.float32)
    Pc[0] = 1.0
    rr, cc = np.divmod(idx, W)
    Pc[:, rr // s, cc // s] = pr.T
    sure = ndi.minimum_filter(Pc[0], size=3, mode="nearest") > CASCADE_BG
    up = np.repeat(np.repeat(Pc, s, axis=1), s, axis=2)[:, :H, :W]
    fine = mask & ~np.repeat(np.repeat(sure, s, axis=0), s, axis=1)[:H, :W]
    keep = mask & ~fine
    P[:, keep] = up[:, keep]
    idx = np.flatnonzero(fine.ravel())
    if len(idx):
        Pf[:, idx] = _rows_predict(model, F, idx, impl).T.astype(np.float32)
    return P


# ----------------------------------------------------------------------------- scene
def build(pkg_dir, model=None, out=None, impl="auto", paths=False, log=None, labels=None, P=None):
    """pkg_dir (fast-path package: imagery/, canopy/, raw/course.json) -> (course_scene/1, info). Writes
    pkg_dir/scene.json (and scene.geojson). paths=False skips the cart-path graph (25-70 s in the perception code;
    the joint router's walk model does not need it). P: precomputed (6, H, W) U-Net probabilities on the stack grid
    (unet_probs; the detection benchmark caches them)."""
    t0 = time.time()
    T = {}

    def lap(k, t):
        T[k] = round(time.time() - t, 2)
        return time.time()
    model = model or load_model()
    if model is None:
        raise FileNotFoundError("no fastscene pixel model (train_pixel.py)")
    t = time.time()
    st = grid_stack(pkg_dir, labels=labels)
    st.meta["package"] = os.path.basename(os.path.normpath(pkg_dir))
    t = lap("grid", t)
    mask = course_mask(st)
    neg = osm_negative_mask(st, pkg_dir)
    uw = unet_weights()
    if P is not None or uw:                      # the segment U-Net (perception's own input), when its weights exist
        if P is None:
            P = unet_probs_years(pkg_dir, st, uw, mask & ~neg, T=T)
        t = lap("unet", t)
        for i, c in enumerate(SEG_ORDER):
            st.a["seg"][i] = np.clip(np.round(P[CLASSES.index(c)] * 255), 0, 255).astype(np.uint8)
        objm = None                              # perception/models: trained on U-Net candidates
        st.meta["seg_source"] = "unet"
    else:
        F = features(st, impl)
        t = lap("features", t)
        P = predict(model, F, mask & ~neg, impl)
        t = lap("classify", t)
        fill_seg(st, P, model)
        objm = object_models(model)
    sc, D = perceive(st, paths=paths, T=T, models=objm,
                     keep=course_mask(st, float(os.environ.get("FASTSCENE_KEEP_PAD", KEEP_PAD_M))) & ~neg)
    T["total"] = round(time.time() - t0, 2)
    sc["fastscene"] = dict(model=os.path.basename(os.path.dirname(model["path"])), seconds=T,
                           pixel_model=model.get("meta", {}).get("id"))
    if out is not False:
        out = out or pkg_dir
        json.dump(sc, open(os.path.join(out, "scene.json"), "w"), separators=(",", ":"))
    return sc, dict(seconds=T, stack=st, D=D, P=P)


UNET_GSD_M = 0.6
UNET_DEFAULT = os.path.join(CD, "segment", "models", "golfseg_own", "model.safetensors")   # ours (README there)


def unet_weights():
    """The segment U-Net's weights (FASTSCENE_UNET=<file.safetensors>, else our own segment/models/golfseg_own;
    FASTSCENE_UNET=0 turns it off). None -> the pixel classifier."""
    p = os.environ.get("FASTSCENE_UNET", UNET_DEFAULT)
    return p if p and p != "0" and os.path.exists(p) else None


_NET = {}


def unet_probs(pkg_dir, st, weights, keep, augs=None, naip=None, tile=None, stride=None):
    """U-Net class probabilities on the stack grid: NAIP 0.6 m in its own CRS (as segment/model.py runs it), tiles
    touching the course outline only, area-averaged onto the 1 m grid. -> (6, H, W) float32. augs: dihedral TTA
    codes (unet.predict_raster); naip: (rgb.tif, nir.tif) of another NAIP year in place of the package's."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    sys.path.insert(0, os.path.join(PLAT, "fastc", "perception"))
    import unet
    net = _NET.get(weights)
    if net is None:
        net = _NET[weights] = unet.UNet(unet.load_safetensors(weights), impl="c")
    src = find_inputs(pkg_dir)
    if naip:
        src = dict(src, rgb=naip[0], nir=naip[1])
    with rasterio.open(src["rgb"]) as d:
        rgb, tr, crs = d.read(), d.transform, d.crs
    with rasterio.open(src["nir"]) as d:
        nir = d.read(1)
    img = np.concatenate([rgb[:3], nir[None]], 0).astype(np.uint8)
    res = abs(tr.a)
    if abs(res - UNET_GSD_M) > 0.05:             # newer NAIP is 0.3 m in some states: the U-Net was trained at 0.6 m
        from rasterio.transform import Affine as _A
        f = UNET_GSD_M / res
        H6, W6 = int(round(img.shape[1] / f)), int(round(img.shape[2] / f))
        tr6 = tr * _A.scale(img.shape[2] / W6, img.shape[1] / H6)
        im6 = np.zeros((4, H6, W6), np.float32)
        for k in range(4):
            reproject(img[k].astype(np.float32), im6[k], src_transform=tr, src_crs=crs, dst_transform=tr6, dst_crs=crs,
                      resampling=Resampling.average)
        img, tr = np.clip(np.round(im6), 0, 255).astype(np.uint8), tr6
    # the keep mask (stack grid) onto the NAIP grid (nearest), dilated by a tile margin implicitly by the tiling
    k6 = np.zeros(img.shape[1:], np.float32)
    g = st.meta["grid"]
    from affine import Affine
    reproject(keep.astype(np.float32), k6, src_transform=Affine(*g["transform"][:6]), src_crs=g["crs"], dst_transform=tr,
              dst_crs=crs, resampling=Resampling.nearest)
    pre = os.path.join(os.path.dirname(weights), "preprocessor_config.json")
    norm = json.load(open(pre)) if os.path.exists(pre) else dict(image_mean=unet.MEAN, image_std=unet.STD)
    kw = {k: v for k, v in dict(augs=augs, tile=tile, stride=stride).items() if v is not None}
    P6 = unet.predict_raster(net, img, keep=k6 > 0.5, mean=norm["image_mean"], std=norm["image_std"], **kw)
    out = np.zeros((len(CLASSES), st.H, st.W), np.float32)
    for k in range(len(CLASSES)):
        reproject(P6[k], out[k], src_transform=tr, src_crs=crs, dst_transform=Affine(*g["transform"][:6]),
                  dst_crs=g["crs"], resampling=Resampling.average)
    return out


YEARS_DEFAULT = 2           # FASTSCENE_YEARS: extra NAIP years averaged into the U-Net probabilities


def unet_probs_years(pkg_dir, st, weights, keep, k=None, T=None):
    """unet_probs on the package's NAIP and on k other NAIP years (fast_imagery.fetch_years: fetched once, cached
    in imagery/years/), probabilities averaged. A year whose fetch fails is skipped."""
    k = int(os.environ.get("FASTSCENE_YEARS", YEARS_DEFAULT)) if k is None else k
    P = unet_probs(pkg_dir, st, weights, keep)
    if k <= 0:
        return P
    t = time.time()
    img = os.path.join(pkg_dir, "imagery")
    try:
        sys.path.insert(0, HERE)
        import fast_imagery as fim
        ys = fim.fetch_years(img, k)
    except Exception:                                                # noqa: BLE001
        ys = []
    if T is not None:
        T["years_fetch"] = round(time.time() - t, 2)
    n = 1
    for y in ys[-k:]:
        d = os.path.join(img, "years", str(y))
        try:
            P += unet_probs(pkg_dir, st, weights, keep, naip=(os.path.join(d, "naip_rgb.tif"),
                                                              os.path.join(d, "naip_nir.tif")))
            n += 1
        except Exception:                                            # noqa: BLE001
            continue
    if T is not None:
        T["unet_years"] = [int(y) for y in ys[-k:]]
    return P / n


def _opt(model, key, env, default):
    v = os.environ.get(env)
    if v is not None:
        return type(default)(v) if not isinstance(default, bool) else v not in ("0", "", "false")
    return (model.get("meta") or {}).get(key, default)


WATER_DEFAULT = "unet"      # FASTSCENE_WATER: "rule" (perception's NIR rule) or "unet[:p[:nir_p]]" (perc_objects)
KEEP_PAD_M = 25.0           # detections (incl. DEM pads, which perception finds on the whole grid) are kept only
                            # inside the course outline + this, and never on an OSM building / road


def osm_negative_mask(st, pkg_dir):
    """OSM buildings, sports pitches / playgrounds / pools / tracks, car parks and schools (+2 m) and roads (4-6 m
    wide) on the grid: not golf, whatever the pixels look like. These are
    non-golf OSM features, available for every course (the golf features themselves are never read here)."""
    import cv2
    m = np.zeros((st.H, st.W), np.uint8)
    p = os.path.join(pkg_dir, "raw", "osm.geojson")
    if not os.path.exists(p):
        return m.astype(bool)
    fc = json.load(open(p))
    roads = ("motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street",
             "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "service")
    for f in fc.get("features", []):
        pr, g = f.get("properties") or {}, f.get("geometry") or {}
        if pr.get("golf") or pr.get("origin") == "fastscene":
            continue
        if (pr.get("building") or pr.get("leisure") in ("pitch", "playground", "swimming_pool", "track")
                or pr.get("amenity") in ("parking", "school")) and g.get("type") in ("Polygon", "MultiPolygon"):
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                if poly:
                    r, c = st.ll_to_rc(np.array([q[0] for q in poly[0]]), np.array([q[1] for q in poly[0]]))
                    q = np.round(np.c_[c, r]).astype(np.int32).reshape(-1, 1, 2)
                    cv2.fillPoly(m, [q], 1)
                    cv2.polylines(m, [q], True, 1, thickness=5)
        elif pr.get("highway") in roads and g.get("type") == "LineString" and pr.get("service") != "parking_aisle":
            co = g["coordinates"]
            r, c = st.ll_to_rc(np.array([q[0] for q in co]), np.array([q[1] for q in co]))
            q = np.round(np.c_[c, r]).astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(m, [q], False, 1, thickness=4 if pr["highway"] == "service" else 7)
    return m.astype(bool)


def object_models(model):
    """Object models for perceive(): fastscene_model/objects/ (green / tee box / complex models trained on THIS
    pixel model's out-of-fold candidates, train_pixel.py objects) when present, else perception/models/ (trained on
    U-Net candidates) when model.json "object_models" is true, else rules only ({})."""
    if not use_object_models(model):
        return {}
    d = os.path.join(os.path.dirname(model["path"]), "objects")
    if os.path.isdir(d):
        with perception_ns():
            import perceive as PV
            m, _ = PV.load_models(d)
        return m
    return None


def use_object_models(model):
    """perception/models/*.pkl (green / tee box / complex / parking / clubhouse / edge object models) were trained
    on U-Net candidates; model.json "object_models" (chosen on the validation courses) says whether they help here."""
    return _opt(model, "object_models", "FASTSCENE_OBJECT_MODELS", True)


def fill_seg(st, P, model):
    """seg layer (the U-Net's place in the perception stack) from the class probabilities, smoothed by
    model.json "smooth_m" (per-pixel trees are noisier than a U-Net; a green must come out as one blob)."""
    from scipy.ndimage import gaussian_filter
    sg = _opt(model, "smooth_m", "FASTSCENE_SMOOTH", 0.0)
    tee_w = _opt(model, "green_plus_tee", "FASTSCENE_GREEN_PLUS_TEE", 0.0)
    for i, c in enumerate(SEG_ORDER):
        p = P[CLASSES.index(c)]
        if c == "green" and tee_w > 0:          # short-mown surfaces: a green the classifier half-calls tee
            p = np.minimum(p + tee_w * P[CLASSES.index("tee")], 1.0)
        if sg > 0:
            p = gaussian_filter(p, sg / st.res)
        st.a["seg"][i] = np.clip(np.round(p * 255), 0, 255).astype(np.uint8)


def objects2_dir():
    """FASTSCENE_OBJECTS2: unset -> fastscene_model/objects_unet (our second-stage models, perc_objects.py) when it
    exists; '0' -> off (perception's models); 'features' -> the extra candidate features only (row collection);
    a directory -> its green / tee_box / tee_complex models; a .json -> {package: dir} (cross-fitted folds)"""
    d = os.path.join(MODEL_DIR, "objects_unet")
    v = os.environ.get("FASTSCENE_OBJECTS2", d if os.path.isdir(d) else "")
    return v if v and v != "0" else None


def _keep(D, keep, st):
    """drop detections whose centre is outside `keep` (bool grid)"""
    def ok(o):
        r, c = st.xy_to_rc(*o["xy"])
        r, c = int(round(float(r))), int(round(float(c)))
        return 0 <= r < st.H and 0 <= c < st.W and bool(keep[r, c])
    for k in ("greens", "boxes", "complexes", "fairways", "bunkers", "water"):
        if D.get(k):
            D[k] = [o for o in D[k] if ok(o)]
    ids = {b["lab"] for b in D.get("boxes") or []}
    for c in D.get("complexes") or []:
        c["boxes"] = [b for b in c["boxes"] if b.get("lab") in ids] or c["boxes"]


def perceive(st, paths=False, T=None, models=None, keep=None):
    """perception/perceive.run + scene.build_scene on a filled stack (rules + the perception object models)."""
    with perception_ns():
        return _perceive(st, paths, T, models, keep)


def _c_hooks():
    """C kernels under perception's own functions (identical results, test_fastperc.py); GOLF_FASTC=0 keeps numpy."""
    import geo
    if os.environ.get("GOLF_FASTC", "1") == "0" or hasattr(geo, "_comp_stats_py"):
        return
    try:
        sys.path.insert(0, os.path.join(PLAT, "fastc", "perception"))
        import fastperc
        fastperc.lib()
    except Exception:                                            # noqa: BLE001
        return
    py = geo._comp_stats_py = geo.comp_stats

    def comp_stats(lab, n, arrays):
        try:
            return fastperc.comp_stats(lab, n, arrays)
        except TypeError:                                        # a float64 plane: numpy keeps it exact
            return py(lab, n, arrays)
    geo.comp_stats = comp_stats


def _perceive(st, paths, T, models, keep):
    _c_hooks()
    import detect as DT
    import features as PF
    import networkx as nx
    import paths as PT
    import perceive as PV
    import scene as SC
    T = T if T is not None else {}
    t = time.time()
    DT.GREEN_P = float(os.environ.get("FASTSCENE_GREEN_P", GREEN_P))
    DT.FAIRWAY_P = float(os.environ.get("FASTSCENE_FAIRWAY_P", FAIRWAY_P))
    DT.BUNKER_P = float(os.environ.get("FASTSCENE_BUNKER_P", BUNKER_P))
    DT.TEE_P = float(os.environ.get("FASTSCENE_TEE_P", TEE_P))
    DT.COMPLEX_GAP_M = float(os.environ.get("FASTSCENE_COMPLEX_GAP", COMPLEX_GAP_M))
    DT.COMPLEX_MERGE_M = float(os.environ.get("FASTSCENE_COMPLEX_MERGE", COMPLEX_MERGE_M))
    if models is None:
        models, _ = PV.load_models()
        models = {k: v for k, v in models.items() if k not in ("path_px",)}
    wm = os.environ.get("FASTSCENE_WATER", WATER_DEFAULT if st.meta.get("seg_source") == "unet" else "rule")
    sys.path.insert(0, HERE)
    import perc_objects as PO
    if wm.startswith("unet"):                    # water from the U-Net's water class (perc_objects.install_water)
        a = [float(x) for x in wm.split(":")[1:]]
        PO.install_water(DT, *a)
    elif getattr(DT, "_water_rule", None):
        DT.water = DT._water_rule
    gs = os.environ.get("FASTSCENE_GREEN_SPLIT")
    if gs is not None or getattr(DT, "_green_split", None):
        a = [float(x) for x in (gs or "0").split(":")]
        PO.install_green_split(DT, *a)
    o2 = objects2_dir() if st.meta.get("seg_source") == "unet" else None
    if o2 and o2.endswith(".json"):              # {slug: models dir, "*": default}: cross-fitted folds (perc_objects)
        fm = json.load(open(o2))
        o2 = fm.get(st.meta.get("package") or "", fm.get("*", "features"))
    if o2:                                       # second-stage object models on our U-Net's candidates (perc_objects)
        PO.install(DT)
        if o2 != "features":
            models = dict(models, **PO.load(o2))
    if not paths:
        saved = PT.build_graph
        PT.build_graph = lambda L, m=None: (nx.Graph(), np.zeros((st.H, st.W), np.float32),
                                            np.zeros((st.H, st.W), np.float32))
    try:
        from threadpoolctl import threadpool_limits
        with threadpool_limits(1):          # sklearn's per-tree OpenMP start-up dominated (16 s on 1000 tiny calls)
            L, D = PV.run(st, models, log=lambda *a: None)
    finally:
        if not paths:
            PT.build_graph = saved
    if keep is not None:
        _keep(D, keep, st)
    D["_layers"] = L
    T["perceive"] = round(time.time() - t, 2)
    T["perceive_parts"] = D.get("seconds")
    t = time.time()
    sc = SC.build_scene(st, L, D, mode="blind", models_id="fastscene", models=models)
    T["scene"] = round(time.time() - t, 2)
    _ = (DT, PF)
    return sc, D


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg_dir")
    ap.add_argument("--impl", default="auto")
    ap.add_argument("--paths", action="store_true")
    a = ap.parse_args()
    sc, info = build(a.pkg_dir, impl=a.impl, paths=a.paths)
    print(json.dumps(sc.get("summary")), json.dumps(info["seconds"]))
