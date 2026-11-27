"""Hole / walk evidence learned on REAL detection candidates, with corridor features read from the pixel maps.

The joint router's hole model (zero_tap/joint model_scene.pkl) was fitted on oracle-noised OSM candidates and sees
the fairway only as the scene's fairway polygons. Here the hole (tee complex t -> green g) and walk (green g -> next
tee t) models are refitted on the routing bench's real fastscene candidates (validation-train courses, labels from
the hidden OSM hole ways), with features read along the tee -> green line from the per-pixel maps the scene was
built from:

    fair / turf      U-Net P(fairway), P(fairway + green + tee)       (fastscene's probabilities, 1 m grid)
    tree             Meta canopy height >= 3 m                         (the package's chm_meta.tif)
    water / bunker   U-Net P(water), P(bunker)

    python3 route_learn.py table --split train|test    per-course feature / label tables (cache/val/learn/)
    python3 route_learn.py cv                          5-fold (by state) out-of-fold scores on train -> sc overrides
    python3 route_learn.py fit                         all-train fit -> route_learn_model.pkl; test sc overrides

The bench reads the overrides with ROUTE_BENCH_SC=<dir> (route_bench.run_one). In production route_scene.run passes
fastscene.build's P and canopy to `corridor_maps` and scores with the saved model (`rescore`).
"""
from __future__ import annotations

import json
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
CACHE = os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache")
PEAKS0 = float(os.environ.get("ROUTE_LEARN_PEAKS", "0.2") or 0)   # (PEAK_P below) the bench tables per candidate set
ROUTER = os.environ.get("ROUTE_LEARN_ROUTER", "v2")          # the bench prep the tables are built on
VER = os.environ.get("ROUTE_LEARN_VER", "2ef0018e4_d0")         # bench scene version (detector commit _ probs variant)
LEARN = os.environ.get("ROUTE_LEARN_DIR") or (
    os.path.join(CACHE, "val", "learn", ROUTER + ("" if VER == "2ef0018e4_d0" else "_" + VER))
    if os.environ.get("ROUTE_SPLIT_TEES", "1") == "0" else os.path.join(CACHE, "val", "learn", "split" if PEAKS0 == 0 else "pk20"))
import detector as _DET  # noqa: E402
MODEL = _DET.routing_file("route_learn_model.pkl", "ROUTE_LEARN_MODEL")
CLASSES = ("background", "green", "tee", "fairway", "bunker", "water")
TREE_M = 3.0


# ----------------------------------------------------------------------------- pixel maps
class Maps:
    """uint8 maps on the scene grid (1 m UTM) + local-yd -> (row, col) affine for a Course projection"""

    def __init__(self, fair, turf, water, bunker, tree, crs, transform):
        self.fair, self.turf, self.water, self.bunker, self.tree = fair, turf, water, bunker, tree
        self.crs, self.tf = crs, transform
        self.H, self.W = fair.shape
        self.A = None
        self.green = self.tee = None          # optional U-Net P(green) / P(tee) (uint8): solve2.refine_virtual

    def bind(self, pj):
        """affine local yd (x, y) -> (row, col), fitted on a grid of points through pj.inv + the UTM transform"""
        from pyproj import Transformer
        tr = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
        xs, ys = np.meshgrid(np.linspace(-1500, 1500, 7), np.linspace(-1500, 1500, 7))
        lo, la = pj.inv(xs.ravel(), ys.ravel())
        ex, ny = tr.transform(lo, la)
        a, _, c, _, e, f = self.tf[:6]
        col = (np.asarray(ex) - c) / a
        row = (np.asarray(ny) - f) / e
        M = np.c_[xs.ravel(), ys.ravel(), np.ones(xs.size)]
        self.A = np.linalg.lstsq(M, np.c_[row, col], rcond=None)[0]          # [3, 2]
        return self

    def rc(self, P):
        P = np.asarray(P, float)
        q = P[..., 0:1] * self.A[0] + P[..., 1:2] * self.A[1] + self.A[2]
        r = np.clip(np.round(q[..., 0]).astype(np.int64), 0, self.H - 1)
        c = np.clip(np.round(q[..., 1]).astype(np.int64), 0, self.W - 1)
        inside = (q[..., 0] >= 0) & (q[..., 0] < self.H) & (q[..., 1] >= 0) & (q[..., 1] < self.W)
        return r, c, inside

    def sample(self, P, which):
        r, c, ins = self.rc(P)
        m = getattr(self, which)
        return np.where(ins, m[r, c], 0).astype(np.float32) / (1.0 if which == "tree" else 255.0)


def corridor_maps(P, grid, chm=None, hag=None):
    """P: [6, H, W] U-Net probabilities (float 0..1 or uint8 0..255) on the scene grid; grid: scene['grid'];
    chm: canopy height (m) on the same grid, or hag (fastscene stack, 0.25 m units, 255 none)."""
    P = np.asarray(P)
    k = 1.0 if P.dtype == np.uint8 else 255.0

    def u8(a):
        return np.clip(np.round(a * k), 0, 255).astype(np.uint8)
    g, t, f = (P[CLASSES.index(c)].astype(np.float32) for c in ("green", "tee", "fairway"))
    turf = u8(np.minimum(g + t + f, 255.0 / k))
    if hag is not None:
        tree = ((hag != 255) & (hag >= TREE_M * 4)).astype(np.uint8)
    elif chm is not None:
        tree = (np.nan_to_num(chm, nan=0.0) >= TREE_M).astype(np.uint8)
    else:
        tree = np.zeros(f.shape, np.uint8)
    M = Maps(u8(f), turf, u8(P[CLASSES.index("water")].astype(np.float32)),
             u8(P[CLASSES.index("bunker")].astype(np.float32)), tree, grid["crs"], grid["transform"])
    M.green, M.tee = u8(g), u8(t)
    return M


def warp_chm(path, grid):
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import Affine
    from rasterio.warp import reproject
    H, W = grid["height"], grid["width"]
    out = np.full((H, W), np.nan, np.float32)
    a, b, c, d, e, f = grid["transform"][:6]
    with rasterio.open(path) as s:
        reproject(rasterio.band(s, 1), out, src_nodata=255, dst_nodata=np.nan, dst_transform=Affine(a, b, c, d, e, f),
                  dst_crs=grid["crs"], resampling=Resampling.nearest)
    return out


def bench_maps(slug, scene, probs="d0"):
    """the routing bench's maps of a validation course (cached, compressed uint8; per probs variant)"""
    p = os.path.join(CACHE, "val", "maps", *([] if probs == "d0" else [probs]), slug + ".npz")
    if slug.startswith("tb_"):                   # TRAIN-BIG (route_big.py): written with the scene
        import route_big
        p = os.path.join(route_big.BIG, "maps", slug + ".npz")
    if os.path.exists(p):
        z = np.load(p)
        return Maps(z["fair"], z["turf"], z["water"], z["bunker"], z["tree"], scene["grid"]["crs"],
                    scene["grid"]["transform"])
    import route_bench as RB
    P = RB.bench_probs(slug, probs)
    cp = os.path.join(CACHE, "heldout", slug, "canopy", "chm_meta.tif")
    chm = warp_chm(cp, scene["grid"]) if os.path.exists(cp) else None
    m = corridor_maps(P, scene["grid"], chm=chm)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    np.savez_compressed(p, fair=m.fair, turf=m.turf, water=m.water, bunker=m.bunker, tree=m.tree)
    return m


# ----------------------------------------------------------------------------- extra candidates from the maps
AUG_P = 128            # P(green) >= 0.5
AUG_AREA = (120, 2500)  # m2
AUG_SEP_M = 22.0


def augment_scene(scene, P, min_area=AUG_AREA[0], max_area=AUG_AREA[1], peaks=None, n_holes=None):
    """greens the scene left out (below its hole-green threshold or never extracted) but the U-Net's P(green) map
    holds as a solid blob: added as scene greens kind 'map' (p_hole 0.36 + 0.3 * blob mean, so they pass route_scene's
    threshold), unless within AUG_SEP_M of a green that is a routing candidate already. -> (scene copy, n added)"""
    import cv2
    from pyproj import Transformer
    from route_scene import P_GREEN
    P = np.asarray(P)
    pg = P[CLASSES.index("green")]
    if pg.dtype != np.uint8:
        pg = np.clip(np.round(pg * 255), 0, 255).astype(np.uint8)
    m = (pg >= AUG_P).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, cents = cv2.connectedComponentsWithStats(m, connectivity=8)
    g = scene["grid"]
    a, _, c, _, e, f = g["transform"][:6]
    inv = Transformer.from_crs(g["crs"], "EPSG:4326", always_xy=True)
    fwd = Transformer.from_crs("EPSG:4326", g["crs"], always_xy=True)
    have = [np.array(fwd.transform(*gg["centroid"])) for gg in scene.get("greens") or []
            if gg.get("kind") != "practice" and float(gg.get("p_hole", gg.get("p", 0))) >= P_GREEN]
    out = []
    for k in range(1, n):
        area = stats[k, cv2.CC_STAT_AREA] * abs(a * e)
        if not (min_area <= area <= max_area):
            continue
        cx, cy = cents[k]
        x, y = c + a * (cx + 0.5), f + e * (cy + 0.5)
        if have and min(np.hypot(x - h[0], y - h[1]) for h in have) < AUG_SEP_M:
            continue
        pm = float(pg[lab == k].mean()) / 255.0
        cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ring = max(cs, key=cv2.contourArea).reshape(-1, 2).astype(float)
        lo, la = inv.transform(c + a * (ring[:, 0] + 0.5), f + e * (ring[:, 1] + 0.5))
        clo, cla = inv.transform(x, y)
        out.append(dict(id="m%d" % k, p=round(pm, 3), p_hole=round(0.36 + 0.3 * pm, 3), kind="map",
                        centroid=[float(clo), float(cla)], area_m2=float(area),
                        polygon=[[float(u), float(v)] for u, v in zip(lo, la)]))
        have.append(np.array([x, y]))
    peaks = PEAK_P if peaks is None else peaks
    if peaks and peaks > 0:
        out += _peak_greens(pg, g, have, inv, peaks)
    sc = dict(scene, greens=list(scene.get("greens") or []) + out)
    pads_on = tee_pads_on() or tee_pads_cond(scene, n_holes)    # counted on the raw scene, before the peaks
    tp = tee_peak_p()
    if tp > 0 and P.shape[0] > CLASSES.index("tee"):
        gx = [(np.array(fwd.transform(*gg["centroid"])), math.sqrt(max(float(gg.get("area_m2") or 300.0), 30.0) / math.pi))
              for gg in sc["greens"] if gg.get("kind") != "practice" and float(gg.get("p_hole", gg.get("p", 0))) >= P_GREEN]
        tc = _peak_tees(P[CLASSES.index("tee")], scene, gx, fwd, inv, tp, n_holes or 18)
        if tc:
            sc["tee_complexes"] = list(scene.get("tee_complexes") or []) + tc
    if pads_on:
        pads = scene.get("dem_pads")
        if pads is None:
            pads = bench_pads(scene)
        if pads:
            gx = [(np.array(fwd.transform(*gg["centroid"])), math.sqrt(max(float(gg.get("area_m2") or 300.0), 30.0) / math.pi))
                  for gg in sc["greens"] if gg.get("kind") != "practice" and float(gg.get("p_hole", gg.get("p", 0))) >= P_GREEN]
            try:                                         # degrade to no pads (missing model, bad pad data), never fail
                tc = _pad_tees(pads, sc, gx, fwd, n_holes or 18)
            except Exception as ex:                      # noqa: BLE001
                print("DEM pads skipped:", repr(ex)[:200])
                tc = []
            if tc:
                sc["tee_complexes"] = list(sc.get("tee_complexes") or []) + tc
    return sc, len(out)


# Tee complexes from 3DEP DEM pads (NOTES_ROUTING.md 2026-11-20 "DEM pads"): a tee is a small level, slightly raised
# platform with banked sides (tees/lidar_pads.components on the 1 m DEM: slope < 5 %, top-hat > 0.05 m, mean >= 0.1 m,
# >= 30 % banked ring, 30-2000 m2). Where the U-Net sees no tee (P(tee) ~ 0 on whole courses), the scene has no
# candidate; pads are geometry. A pad >= TEE_PAD_SEP_M from every scene complex / P(tee) peak and clear of the greens
# is scored by a small classifier (route_pad_model.pkl: pad shape, U-Net class means under it, distance to the nearest
# complex / green edge; label = within 30 m of a hole start no other complex covers) and added as a one-box complex
# kind 'pad' (p = that score; t_src 2 in the tee attributes of a fit made with pads) when the score >= tee_pad_min(),
# best first, until the course holds tee_pad_fill() complexes a hole. Opt-in: ROUTE_TEE_PADS=1 (fits must match).
TEE_PAD_SEP_M, TEE_PAD_GREEN_M = 25.0, 6.0
PAD_FEATS = ("area_m2", "tophat_m", "slope_pct", "bank_frac", "p_bg", "p_green", "p_tee", "p_fair", "p_bunker", "p_water",
             "p_tee_max", "dT", "dG")
PAD_MODEL = _DET.routing_file("route_pad_model.pkl", "ROUTE_PAD_MODEL")
_PADM = {}


def tee_pads_on():
    return _DET.route_tee_pads()


# Conditional pads (NOTES_ROUTING.md 2026-11-20 "conditional DEM pads"): with the default fits, pads are added only on a
# tee-blind scene, one whose raw scene tee complexes (before P(tee) peaks; OSM tees in fc not counted) number fewer
# than PAD_COND_FRAC x n. Peaks fill every scene to 2 n, so the count must be taken before augment_scene adds them.
# Opt-in ROUTE_PADS_COND=1, not the default: measured fully out of fold it does not raise OOF 643 (choice -6 on 40
# courses, never-used +5 on 17). Off with every rollback that turns ROUTE_TEE_PADS off, and when ROUTE_TEE_PADS is
# set (=1: pads everywhere with their own fits; =0: no pads).
PAD_COND_FRAC = float(os.environ.get("ROUTE_PADS_COND_FRAC", "0.75") or 0.75)


def tee_pads_cond(scene, n_holes):
    """pads on for this (raw) scene under the conditional rule"""
    if os.environ.get("ROUTE_PADS_COND", "0") != "1" or os.environ.get("ROUTE_TEE_PADS") not in (None, ""):
        return False
    if _DET.unet_model() != "v2" or _DET.tee_rollback() or _DET.select_rollback() or _DET.route_tee_peaks() == 0:
        return False
    n_real = sum(1 for t in (scene or {}).get("tee_complexes") or [] if not t.get("virtual"))
    return n_real < PAD_COND_FRAC * float(n_holes or 18)


def tee_pad_fill():
    return float(os.environ.get("ROUTE_TEE_PAD_FILL", "3") or 3)


def tee_pad_min():
    return float(os.environ.get("ROUTE_TEE_PAD_MIN", "0.05") or 0.0)


def pad_x(p):
    return [min(float(p[k]), 500.0) if k in ("dT", "dG") else float(p.get(k, np.nan)) for k in PAD_FEATS]


def pad_scores(pads):
    """route_pad_model.pkl scores of pads carrying dT / dG; a pad with a precomputed 'score' (the bench's out-of-fold
    score) keeps it"""
    if PAD_MODEL not in _PADM:
        _PADM[PAD_MODEL] = pickle.load(open(PAD_MODEL, "rb")) if os.path.exists(PAD_MODEL) else None
    m = _PADM[PAD_MODEL]
    todo = [i for i, p in enumerate(pads) if p.get("score") is None]
    out = [p.get("score") for p in pads]
    if todo:
        if m is None:
            raise FileNotFoundError("ROUTE_TEE_PADS=1 needs " + PAD_MODEL)
        pr = m["model"].predict_proba(np.asarray([pad_x(pads[i]) for i in todo], float))[:, 1]
        for i, v in zip(todo, pr):
            out[i] = float(v)
    return out


def dem_pads(z, grid, P):
    """pad components of a DEM on the scene grid (z [H, W] m, NaN no data; P: U-Net uint8 [6, H, W] or None) ->
    [dict(centroid, polygon (lon / lat), area_m2, tophat_m, slope_pct, bank_frac, p_<class> means, p_tee_max)]"""
    import sys as _sys
    tees = os.path.join(os.path.dirname(os.path.dirname(HERE)), "tees")
    if tees not in _sys.path:
        _sys.path.append(tees)
    import lidar_pads as LP
    from pyproj import Transformer
    z = np.asarray(z, np.float64)
    if not np.isfinite(z).any() or np.isfinite(z).mean() <= 0.5:
        return []
    inv = Transformer.from_crs(grid["crs"], "EPSG:4326", always_xy=True)
    a, _, c, _, e, f = grid["transform"][:6]
    out = []
    for cp in LP.components(z, 1.0):
        rr, cc = cp["rows"], cp["cols"]
        x, y = c + a * (cc.mean() + 0.5), f + e * (rr.mean() + 0.5)
        lo, la = inv.transform(x, y)
        ft = {}
        if P is not None:
            for k, nm in enumerate(("bg", "green", "tee", "fair", "bunker", "water")):
                v = P[k][np.clip(rr, 0, P.shape[1] - 1), np.clip(cc, 0, P.shape[2] - 1)].astype(np.float32) / 255
                ft["p_" + nm] = round(float(v.mean()), 3)
                if nm == "tee":
                    ft["p_tee_max"] = round(float(v.max()), 3)
        hull = LP._hull(np.c_[c + a * (cc + 0.5), f + e * (rr + 0.5)])
        hl, ha = inv.transform([q[0] for q in hull], [q[1] for q in hull])
        out.append(dict(centroid=[float(lo), float(la)], polygon=[[float(u), float(v)] for u, v in zip(hl, ha)],
                        **{k: cp[k] for k in ("area_m2", "tophat_m", "slope_pct", "bank_frac")}, **ft))
    return out


def dem_pads_file(dem_path, grid, P):
    """dem_pads on a GeoTIFF that is the scene grid (fastscene builds its grid from the package DEM); [] otherwise"""
    import rasterio
    if not dem_path or not os.path.exists(dem_path):
        return []
    with rasterio.open(dem_path) as s:
        if (s.height, s.width) != (grid["height"], grid["width"]) or abs(s.transform.c - grid["transform"][2]) > 0.01 \
                or abs(s.transform.f - grid["transform"][5]) > 0.01:
            return []
        z = s.read(1).astype(np.float64)
        if s.nodata is not None and np.isfinite(s.nodata):
            z[z == s.nodata] = np.nan
    z[z < -1000] = np.nan
    return dem_pads(z, grid, P)


def _grid_key(grid):
    t = grid["transform"]
    return "%s_%d_%d_%d_%d" % (str(grid["crs"]).replace(":", ""), round(t[2]), round(t[5]), grid["width"], grid["height"])


def bench_pads(scene):
    """the bench's precomputed pads of a scene (ROUTE_PADS_DIR/<grid key>.json, written by the bench pad job)"""
    d = os.environ.get("ROUTE_PADS_DIR")
    if not d or not scene or not scene.get("grid"):
        return None
    p = os.path.join(d, _grid_key(scene["grid"]) + ".json")
    if not os.path.exists(p):
        return None
    return json.load(open(p)).get("pads") or []


def pad_context(pads, scene, greens, fwd):
    """copies of the pads with dT (m to the nearest real complex box) / dG (m to the nearest green edge) and xy"""
    real = [t for t in scene.get("tee_complexes") or [] if not t.get("virtual")]
    have = np.asarray([fwd.transform(*q) for t in real
                       for q in ([b["centroid"] for b in t.get("boxes") or [] if b.get("centroid")] or [t["centroid"]])],
                      float).reshape(-1, 2)
    gq = np.asarray([g for g, _ in greens], float).reshape(-1, 2)
    gr = np.asarray([r for _, r in greens], float)
    out = []
    for p in pads:
        q = np.array(fwd.transform(*p["centroid"]))
        dT = float(np.min(np.hypot(*(have - q).T))) if len(have) else 1e9
        dG = float(np.min(np.hypot(*(gq - q).T) - gr)) if len(gq) else 1e9
        out.append(dict(p, dT=dT, dG=dG, _xy=q))
    return out, len(real)


def _pad_tees(pads, scene, greens, fwd, n_holes):
    P, n_real = pad_context(pads, scene, greens, fwd)
    P = [p for p in P if p["dT"] >= TEE_PAD_SEP_M and p["dG"] >= TEE_PAD_GREEN_M]
    if not P:
        return []
    sc = pad_scores(P)
    budget = max(0, int(round(tee_pad_fill() * n_holes)) - n_real)
    mn = tee_pad_min()
    out, have = [], []
    for i in sorted(range(len(P)), key=lambda i: -sc[i]):
        if len(out) >= budget or sc[i] < mn:
            break
        p, q = P[i], P[i]["_xy"]
        if have and min(float(np.hypot(*(q - h))) for h in have) < TEE_PAD_SEP_M:
            continue
        v = round(float(sc[i]), 4)
        cid = "kd%d_%d" % (round(q[0]), round(q[1]))
        out.append(dict(id=cid, p=v, p_range_tee=0.0, centroid=list(p["centroid"]), polygon=p["polygon"],
                        axis_deg=None, length_m=None, src=["dem_pad"], virtual=False, kind="pad",
                        boxes=[dict(id=cid + ".1", p=v, centroid=list(p["centroid"]), area_m2=float(p["area_m2"]),
                                    polygon=p["polygon"], src=["dem_pad"])]))
        have.append(q)
    return out


# Tee complexes from the U-Net's P(tee) map (detector.route_tee_peaks, v2 default 0.1; NOTES_ROUTING.md 2026-11-19
# tee detection): tee boxes below the scene's box threshold never form complexes, so a hole start the scene missed has
# no tee candidate at all. Local maxima of P(tee) (smoothed, sigma TEE_PEAK_SIG_M) >= the threshold in a
# TEE_PEAK_WIN_M window, at least TEE_PEAK_SEP_M from every scene complex box and from an earlier peak, and clear of
# every green (radius + TEE_PEAK_GREEN_M), are added as one-box complexes kind 'peak' with p = the smoothed peak,
# strongest first, until the course holds tee_peak_fill() complexes a hole.
TEE_PEAK_SIG_M, TEE_PEAK_WIN_M, TEE_PEAK_SEP_M, TEE_PEAK_GREEN_M = 2.0, 15.0, 25.0, 6.0


def tee_peak_p():
    """P(tee) peak threshold (detector.route_tee_peaks: v2 default 0.1, env ROUTE_TEE_PEAKS, 0 = off)"""
    return _DET.route_tee_peaks()


def tee_peak_fill():
    """peaks are added until the course has this many complexes a hole (ROUTE_TEE_PEAK_FILL, default 2)"""
    return float(os.environ.get("ROUTE_TEE_PEAK_FILL", "2") or 2)


def _peak_tees(pt, scene, greens, fwd, inv, th, n_holes):
    import cv2
    g = scene["grid"]
    a, _, c, _, e, f = g["transform"][:6]
    pt = np.asarray(pt)
    pt = pt.astype(np.float32) / (255.0 if pt.dtype == np.uint8 else 1.0)
    sm = cv2.GaussianBlur(pt, (0, 0), TEE_PEAK_SIG_M / abs(a))
    w = max(3, int(round(TEE_PEAK_WIN_M / abs(a))) | 1)
    mx = cv2.dilate(sm, np.ones((w, w), np.uint8))
    rr, cc = np.where((sm >= mx - 1e-6) & (sm >= th))
    real = [t for t in scene.get("tee_complexes") or [] if not t.get("virtual")]
    have = [np.array(fwd.transform(*q)) for t in real
            for q in ([b["centroid"] for b in t.get("boxes") or [] if b.get("centroid")] or [t["centroid"]])]
    budget = max(0, int(tee_peak_fill() * n_holes) - len(real))     # course-adaptive: few complexes, more peaks
    out = []
    H, W = sm.shape
    for i in np.argsort(-sm[rr, cc]):
        if len(out) >= budget:
            break
        r0, c0 = int(rr[i]), int(cc[i])
        x, y = c + a * (c0 + 0.5), f + e * (r0 + 0.5)
        q = np.array([x, y])
        if have and min(float(np.hypot(*(q - h))) for h in have) < TEE_PEAK_SEP_M:
            continue
        if any(float(np.hypot(*(q - gq))) < gr + TEE_PEAK_GREEN_M for gq, gr in greens):
            continue
        v = float(sm[r0, c0])
        k = int(round(15.0 / abs(a)))
        ra, rb, ca, cb = max(0, r0 - k), min(H, r0 + k + 1), max(0, c0 - k), min(W, c0 + k + 1)
        m = (sm[ra:rb, ca:cb] >= 0.5 * v).astype(np.uint8)
        _, lab = cv2.connectedComponents(m)
        mk = (lab == lab[r0 - ra, c0 - ca]).astype(np.uint8)
        area = float(mk.sum() * abs(a * e))
        cs, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cs and 20 <= area <= 1500:
            ring = max(cs, key=cv2.contourArea).reshape(-1, 2).astype(float) + [ca, ra]
            px, py = c + a * (ring[:, 0] + 0.5), f + e * (ring[:, 1] + 0.5)
        else:
            t_ = np.linspace(0, 2 * np.pi, 12, endpoint=False)
            px, py = x + 5 * np.cos(t_), y + 5 * np.sin(t_)
            area = float(np.pi * 25)
        lo, la = inv.transform(px, py)
        clo, cla = inv.transform(x, y)
        poly = [[float(u), float(z)] for u, z in zip(lo, la)]
        cid = "kp%d_%d" % (r0, c0)
        out.append(dict(id=cid, p=round(v, 3), p_range_tee=0.0, centroid=[float(clo), float(cla)], polygon=poly,
                        axis_deg=None, length_m=None, src=["peak"], virtual=False, kind="peak",
                        boxes=[dict(id=cid + ".1", p=round(v, 3), centroid=[float(clo), float(cla)], area_m2=area,
                                    polygon=poly, src=["peak"])]))
        have.append(q)
    return out


PEAK_P = float(os.environ.get("ROUTE_LEARN_PEAKS", "0.2") or 0)  # > 0: also P(green) local maxima >= this (0: off)
PEAK_SEP_M = 24.0


def _peak_greens(pg, g, have, inv, th):
    """weak greens (under trees, small, low contrast): local maxima of P(green) smoothed (sigma 3 m) >= th, in a
    25 m window, not within PEAK_SEP_M of a green already offered; kind 'peak', p = the smoothed peak, outline = the
    pixels >= half the peak around it (else a 9 m circle)"""
    import cv2
    a, _, c, _, e, f = g["transform"][:6]
    sm = cv2.GaussianBlur(pg.astype(np.float32) / 255.0, (0, 0), 3.0 / abs(a))
    w = max(3, int(round(25.0 / abs(a))) | 1)
    mx = cv2.dilate(sm, np.ones((w, w), np.uint8))
    rr, cc = np.where((sm >= mx - 1e-6) & (sm >= th))
    order = np.argsort(-sm[rr, cc])
    out = []
    H, W = sm.shape
    for i in order:
        r0, c0 = int(rr[i]), int(cc[i])
        x, y = c + a * (c0 + 0.5), f + e * (r0 + 0.5)
        if have and min(np.hypot(x - h[0], y - h[1]) for h in have) < PEAK_SEP_M:
            continue
        v = float(sm[r0, c0])
        k = int(round(18.0 / abs(a)))
        ra, rb, ca, cb = max(0, r0 - k), min(H, r0 + k + 1), max(0, c0 - k), min(W, c0 + k + 1)
        m = (sm[ra:rb, ca:cb] >= 0.5 * v).astype(np.uint8)
        n_, lab = cv2.connectedComponents(m)
        mk = (lab == lab[r0 - ra, c0 - ca]).astype(np.uint8)
        area = float(mk.sum() * abs(a * e))
        cs, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cs and 60 <= area <= 2500:
            ring = max(cs, key=cv2.contourArea).reshape(-1, 2).astype(float) + [ca, ra]
            px, py = c + a * (ring[:, 0] + 0.5), f + e * (ring[:, 1] + 0.5)
        else:
            t_ = np.linspace(0, 2 * np.pi, 12, endpoint=False)
            px, py = x + 9 * np.cos(t_), y + 9 * np.sin(t_)
            area = float(np.pi * 81)
        lo, la = inv.transform(px, py)
        clo, cla = inv.transform(x, y)
        out.append(dict(id="k%d_%d" % (r0, c0), p=round(v, 3), p_hole=round(0.36 + 0.3 * v, 3), kind="peak",
                        centroid=[float(clo), float(cla)], area_m2=area,
                        polygon=[[float(u), float(q)] for u, q in zip(lo, la)]))
        have.append(np.array([x, y]))
    return out


# ----------------------------------------------------------------------------- features
NS = 41
XF = ["fr_mean", "fr_mid", "fr_lo", "turf_mean", "turf_gap", "tree_mean", "tree_run", "water", "side_fr",
      "fr_contrast", "fr_end", "fr_start", "g_bunker", "g_turf", "t_turf", "fr_far", "tree_far", "turf_gap_far",
      "dist", "card_fit", "fr_bend", "bend_gain", "g_p", "g_area", "g_map", "g_pg", "t_p", "t_nbox", "t_len"]


def _runs(b, step):
    """longest run of True along the last axis, in yd"""
    best = np.zeros(b.shape[:-1])
    cur = np.zeros(b.shape[:-1])
    for k in range(b.shape[-1]):
        cur = np.where(b[..., k], cur + 1, 0)
        best = np.maximum(best, cur)
    return best * step


def line_stats(M, A, B, lo=0.08, hi=0.92, ns=NS):
    """per segment A -> B ([n, 2] yd): fairway / turf / tree / water stats along it"""
    s = np.linspace(lo, hi, ns)
    P = A[:, None, :] + (B - A)[:, None, :] * s[None, :, None]           # [n, ns, 2]
    L = np.hypot(*(B - A).T)
    step = L * (hi - lo) / (ns - 1)
    fr = M.sample(P, "fair")
    tu = M.sample(P, "turf")
    tr = M.sample(P, "tree")
    wa = M.sample(P, "water")
    mid = (s > 0.25) & (s < 0.85)
    return dict(fr_mean=fr.mean(1), fr_mid=fr[:, mid].mean(1), fr_lo=(fr < 0.25).mean(1), turf_mean=tu.mean(1),
                turf_gap=_runs((tu < 0.25) & (wa < 0.5), step), tree_mean=tr.mean(1),
                tree_run=_runs(tr > 0.5, step), water=(wa > 0.5).mean(1), fr_end=fr[:, s > 0.7].mean(1),
                fr_start=fr[:, s < 0.4].mean(1))


def pair_features(d, M):
    """[n pairs, len(XF)] for d['hp'] (tee complex, green) rows"""
    co, geo = d["co"], d["geo"]
    G = np.asarray(co["G"], float)
    Tc = np.asarray(geo["Tc"], float)
    hp = np.asarray(d["hp"], int).reshape(-1, 2)
    n = len(hp)
    if not n:
        return np.zeros((0, len(XF)))
    A, B = Tc[hp[:, 0]], G[hp[:, 1]]
    st = line_stats(M, A, B)
    # far box of the complex (the play line from the back tee)
    far = np.array([np.asarray(co["T"][t]["pts"])[int(np.argmax(np.hypot(*(np.asarray(co["T"][t]["pts"]) - G[g]).T)))]
                    for t, g in hp])
    sf = line_stats(M, far, B)
    u = (B - A) / np.maximum(np.hypot(*(B - A).T), 1.0)[:, None]
    nrm = np.c_[-u[:, 1], u[:, 0]]
    side = []
    for off in (-25.0, 25.0):
        s2 = line_stats(M, A + nrm * off, B + nrm * off, 0.25, 0.85, 15)
        side.append(s2["fr_mean"])
    side = np.maximum(side[0], side[1])
    # around the green: bunkers / turf in a ring 8-35 yd; around the tee: turf in 10 yd
    ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    ring = np.c_[np.cos(ang), np.sin(ang)]
    gb = np.zeros(len(G))
    gt = np.zeros(len(G))
    for r in (12.0, 22.0, 32.0):
        gb += M.sample(G[:, None, :] + r * ring[None], "bunker").mean(1) / 3
        gt += M.sample(G[:, None, :] + r * ring[None], "turf").mean(1) / 3
    tt = np.array([M.sample(np.asarray(t["pts"], float), "turf").mean() for t in co["T"]])
    # card: the best |play length - card| over the card's positions / sets, relative
    Y = d.get("_Y")
    L = geo["P"][hp[:, 0], hp[:, 1]]
    cf = np.full(n, np.nan) if Y is None else np.min(np.abs(L[:, None] - Y.ravel()[None, :]) / Y.ravel()[None, :], 1)
    # one-bend path: the best bend point on a grid around the line (dogleg corridor), fairway mean of both legs
    fb, bg = bend(M, A, B, st["fr_mean"])
    ga, ta = d.get("_gattr"), d.get("_tattr")
    ga = np.full((len(G), 4), np.nan) if ga is None else ga
    ta = np.full((len(Tc), 4 if d.get("_tsrc") else 3), np.nan) if ta is None else ta
    return np.c_[st["fr_mean"], st["fr_mid"], st["fr_lo"], st["turf_mean"], st["turf_gap"], st["tree_mean"],
                 st["tree_run"], st["water"], side, st["fr_mid"] - side, st["fr_end"], st["fr_start"], gb[hp[:, 1]],
                 gt[hp[:, 1]], tt[hp[:, 0]], sf["fr_mean"], sf["tree_mean"], sf["turf_gap"], np.hypot(*(B - A).T), cf,
                 fb, bg, ga[hp[:, 1]], ta[hp[:, 0]]]


def obj_attrs(d, scene, M):
    """per candidate green: detector p, area m2, from the map (augment_scene), mean P(green)-ish turf at the centre;
    per tee complex: detector p, boxes, length m"""
    co = d["co"]
    gs = {"scene:" + g["id"]: g for g in (scene or {}).get("greens") or []}
    ts = {"scene:" + t["id"]: t for t in (scene or {}).get("tee_complexes") or []}
    ga = []
    for gid, xy in zip(co["Gid"], np.asarray(co["G"], float)):
        g = gs.get(gid) or {}
        ga.append([float(g.get("p_hole", g.get("p", np.nan)) or np.nan), float(g.get("area_m2") or np.nan),
                   {"map": 1.0, "peak": 2.0}.get(g.get("kind"), 0.0), float(M.sample(xy[None], "turf")[0])])
    ta = []
    src = bool(d.get("_tsrc"))              # + t_src (0 scene, 1 P(tee) peak, 2 DEM pad) for fits made with DEM pads
    for t in co["T"]:
        o = ts.get(t["id"].split("/")[0]) or {}
        ta.append([float(o.get("p", np.nan) or np.nan), float(len(t["pts"])), float(o.get("length_m") or np.nan)]
                  + ([float({"peak": 1, "pad": 2}.get(o.get("kind"), 0))] if src else []))
    return np.asarray(ga, float).reshape(-1, 4), np.asarray(ta, float).reshape(-1, 4 if src else 3)


def bend(M, A, B, straight):
    """best one-bend path A -> K -> B with K at 45-80 % along and up to 0.3 * length off the line: the leg-weighted
    fairway mean; -> (best fairway mean, gain over straight)"""
    L = np.maximum(np.hypot(*(B - A).T), 1.0)
    u = (B - A) / L[:, None]
    nrm = np.c_[-u[:, 1], u[:, 0]]
    best = straight.copy()
    for a in (0.5, 0.65, 0.8):
        for o in (-0.3, -0.18, 0.18, 0.3):
            K = A + u * (a * L)[:, None] + nrm * (o * L)[:, None]
            s1 = line_stats(M, A, K, 0.1, 1.0, 21)
            s2 = line_stats(M, K, B, 0.0, 0.85, 15)
            l1, l2 = np.hypot(*(K - A).T), np.hypot(*(B - K).T)
            v = (s1["fr_mean"] * l1 + s2["fr_mean"] * l2) / (l1 + l2) - 0.1 * ((l1 + l2) / L - 1)
            best = np.maximum(best, v)
    return best, best - straight


WXF = ["w_turf", "w_tree", "w_fr_ahead", "w_dist", "w_own", "w_tout", "w_cos_in", "w_rank_x", "w_rel_x",
       "w_back"]


def ph_matrix(d, ph=None):
    nt, ng = len(d["co"]["T"]), len(d["co"]["G"])
    Ph = np.zeros((nt, ng))
    hp = np.asarray(d["hp"], int).reshape(-1, 2)
    if len(hp):
        Ph[hp[:, 0], hp[:, 1]] = d["sc"]["ph"] if ph is None else ph
    return Ph


def walk_features(d, M, ph=None):
    """[n walk pairs, len(WXF)]: the green -> next tee walk (turf, trees), the fairway ahead of that tee, and what the
    hole model says: is t this green's own tee (no walk), does t start a good hole elsewhere, is the walk a step
    forward from the incoming hole's direction, rank / ratio of the walk among tees that start a hole"""
    co, geo = d["co"], d["geo"]
    G = np.asarray(co["G"], float)
    Tc = np.asarray(geo["Tc"], float)
    wp = np.asarray(d["wp"], int).reshape(-1, 2)
    if not len(wp):
        return np.zeros((0, len(WXF)))
    A, B = G[wp[:, 0]], Tc[wp[:, 1]]
    st = line_stats(M, A, B, 0.15, 0.85, 15)
    ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    U = np.c_[np.cos(ang), np.sin(ang)]
    ahead = np.zeros((len(Tc), len(U)))
    for r in (120.0, 170.0, 220.0):
        ahead = ahead + M.sample(Tc[:, None, :] + r * U[None], "fair") / 3
    best = ahead.max(1)
    Ph = ph_matrix(d, ph)
    own = Ph[wp[:, 1], wp[:, 0]]
    Px = Ph.copy()
    Px[wp[:, 1], wp[:, 0]] = 0.0
    tout = np.array([np.max(np.delete(Ph[t], g)) if Ph.shape[1] > 1 else 0.0 for g, t in wp])
    # incoming direction: from the green's best tee
    bt = np.argmax(Ph, axis=0)
    din = G - Tc[bt]
    din = din / np.maximum(np.hypot(*din.T), 1.0)[:, None]
    dw = B - A
    L = np.maximum(np.hypot(*dw.T), 1.0)
    cos_in = np.sum(din[wp[:, 0]] * dw, 1) / L
    W = d["W"]
    rank_x = np.zeros(len(wp))
    rel_x = np.zeros(len(wp))
    gcache = {}
    for j, (g, t) in enumerate(wp):
        if g not in gcache:
            good = np.array([np.max(np.delete(Ph[k], g)) if Ph.shape[1] > 1 else 0.0 for k in range(len(Tc))]) >= 0.3
            gcache[g] = np.where(good, W[g], np.inf)
        dd = gcache[g]
        rank_x[j] = float(np.sum(dd < W[g, t]))
        m = np.min(np.where(np.arange(len(Tc)) != t, dd, np.inf)) if len(Tc) > 1 else np.inf
        rel_x[j] = (W[g, t] + 20.0) / (min(m, 2000.0) + 20.0)
    back = np.sum(din[wp[:, 0]] * dw, 1)
    return np.c_[st["turf_mean"], st["tree_mean"], best[wp[:, 1]], np.hypot(*dw.T), own, tout, cos_in, rank_x,
                 rel_x, back]


# ----------------------------------------------------------------------------- x3: richer local features (2026-11-17)
XF3 = (["pf_fr%d" % i for i in range(5)] + ["pf_tu%d" % i for i in range(5)] + ["pf_tr%d" % i for i in range(5)]
       + ["pf_wa%d" % i for i in range(3)] + ["cw_tr8", "cw_tr16", "cw_tr28", "cw_tr40", "cw_fr16", "cw_fr40",
                                              "cw_free", "g_pg0", "g_pg8", "g_pgring", "t_pt0", "t_ptfar",
                                              "c_rk_t", "c_rel_t", "c_rk_g", "c_rel_g", "c_cf_rk", "c_namb",
                                              "c_par3", "bk_end"])
WXF3 = ["wx_tu0", "wx_tu1", "wx_tu2", "wx_trrun", "wx_rk_t", "wx_rk_g", "wx_cos_out", "wx_rel_hole", "wx_ahead_tr",
        "wx_tp", "wx_ph_out_rk"]


def _prof(v, nb):
    """[n, ns] -> [n, nb] bin means along the line"""
    k = np.array_split(np.arange(v.shape[1]), nb)
    return np.stack([v[:, i].mean(1) for i in k], 1)


def _rank_rel(vals, keys):
    """per row: rank (0 = best, high value) of vals within its key group and vals / group max"""
    rk = np.zeros(len(vals))
    rel = np.zeros(len(vals))
    for k in np.unique(keys):
        i = np.where(keys == k)[0]
        o = np.argsort(-vals[i])
        rk[i[o]] = np.arange(len(i))
        rel[i] = vals[i] / max(float(vals[i].max()), 1e-6)
    return rk, rel


def pair_features3(d, M):
    """[n pairs, len(XF3)]: along-path profiles (fairway / turf / trees in 5 bins, water in 3), the tree-free and
    fairway corridor width across the line, U-Net P(green) at / around the green and P(tee) at the tee, and the pair
    in context (rank / ratio of the prior hole score among the tee's greens and the green's tees, card-fit rank among
    the tee's greens, how many card holes the length fits, par-3 length). M.green / M.tee: optional u8 P maps."""
    co, geo = d["co"], d["geo"]
    G = np.asarray(co["G"], float)
    Tc = np.asarray(geo["Tc"], float)
    hp = np.asarray(d["hp"], int).reshape(-1, 2)
    n = len(hp)
    if not n:
        return np.zeros((0, len(XF3)))
    A, B = Tc[hp[:, 0]], G[hp[:, 1]]
    s = np.linspace(0.05, 0.95, 31)
    P = A[:, None, :] + (B - A)[:, None, :] * s[None, :, None]
    fr, tu, tr, wa = (M.sample(P, k) for k in ("fair", "turf", "tree", "water"))
    L = np.maximum(np.hypot(*(B - A).T), 1.0)
    u = (B - A) / L[:, None]
    nrm = np.c_[-u[:, 1], u[:, 0]]
    sm = np.array([0.3, 0.5, 0.7])
    Q = A[:, None, :] + (B - A)[:, None, :] * sm[None, :, None]               # [n, 3, 2]
    cw = {}
    for off in (8.0, 16.0, 28.0, 40.0):
        both = np.concatenate([Q + nrm[:, None, :] * off, Q - nrm[:, None, :] * off], 1)
        cw["tr", off] = M.sample(both, "tree").mean(1)
        cw["fr", off] = M.sample(both, "fair").mean(1)
    # tree-free half-width: the first offset (of 0, 8, 16, 28, 40) where trees take over, mean over the 3 points
    offs = np.array([0.0, 8.0, 16.0, 28.0, 40.0, 55.0])
    free = np.zeros(n)
    for j in range(3):
        w = np.full(n, 55.0)
        for side in (1.0, -1.0):
            ws = np.full(n, 55.0)
            for oi in range(len(offs) - 1, -1, -1):
                pt = Q[:, j] + nrm * offs[oi] * side
                t_ = M.sample(pt[:, None, :], "tree")[:, 0] > 0.5
                ws = np.where(t_, offs[oi], ws)
            w = np.minimum(w, ws) if side < 0 else ws
        free += w / 3
    ang = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    ring = np.c_[np.cos(ang), np.sin(ang)]
    if M.green is not None:
        pg0 = M.sample(B[:, None, :], "green")[:, 0]
        pg8 = M.sample(B[:, None, :] + 8 * ring[None], "green").mean(1)
        pgr = M.sample(B[:, None, :] + 25 * ring[None], "green").mean(1)
    else:
        pg0 = pg8 = pgr = np.full(n, np.nan)
    far = np.array([np.asarray(co["T"][t]["pts"])[int(np.argmax(np.hypot(*(np.asarray(co["T"][t]["pts"]) - G[g]).T)))]
                    for t, g in hp])
    if M.tee is not None:
        pt0 = M.sample(A[:, None, :], "tee")[:, 0]
        ptf = M.sample(far[:, None, :], "tee")[:, 0]
    else:
        pt0 = ptf = np.full(n, np.nan)
    ph0 = np.asarray(d["sc"]["ph"], float)
    rk_t, rel_t = _rank_rel(ph0, hp[:, 0])
    rk_g, rel_g = _rank_rel(ph0, hp[:, 1])
    Y = d.get("_Y")
    Lp = geo["P"][hp[:, 0], hp[:, 1]]
    if Y is None:
        cf = namb = np.full(n, np.nan)
    else:
        yv = np.asarray(Y, float).ravel()
        yv = yv[np.isfinite(yv) & (yv > 0)]
        if len(yv):
            rr = np.abs(Lp[:, None] - yv[None, :]) / yv[None, :]
            cf = rr.min(1)
            namb = (rr < 0.08).sum(1) / max(len(yv), 1)
        else:
            cf = namb = np.full(n, np.nan)
    cf_rk, _ = _rank_rel(-np.nan_to_num(cf, nan=9.0), hp[:, 0])
    bk = M.sample(B[:, None, :] + 15 * ring[None], "bunker").mean(1)
    return np.c_[_prof(fr, 5), _prof(tu, 5), _prof(tr, 5), _prof(wa, 3), cw["tr", 8.0], cw["tr", 16.0],
                 cw["tr", 28.0], cw["tr", 40.0], cw["fr", 16.0], cw["fr", 40.0], free, pg0, pg8, pgr, pt0, ptf,
                 rk_t, rel_t, rk_g, rel_g, cf_rk, namb, (Lp < 260).astype(float), bk]


def walk_features3(d, M):
    """[n walk pairs, len(WXF3)]: turf profile / tree run along the green -> tee walk, distance ranks both ways,
    whether the next hole turns back along the walk, walk length vs the green's hole length, trees ahead of the tee,
    P(tee) at the tee, rank of the tee's best outgoing prior hole score"""
    co, geo = d["co"], d["geo"]
    G = np.asarray(co["G"], float)
    Tc = np.asarray(geo["Tc"], float)
    wp = np.asarray(d["wp"], int).reshape(-1, 2)
    n = len(wp)
    if not n:
        return np.zeros((0, len(WXF3)))
    A, B = G[wp[:, 0]], Tc[wp[:, 1]]
    s = np.linspace(0.1, 0.9, 15)
    P = A[:, None, :] + (B - A)[:, None, :] * s[None, :, None]
    tu = M.sample(P, "turf")
    tr = M.sample(P, "tree")
    Lw = np.maximum(np.hypot(*(B - A).T), 1.0)
    trrun = _runs(tr > 0.5, 1.0) * Lw * 0.8 / 14                     # longest tree run, yd
    Dgt = np.hypot(G[:, None, 0] - Tc[None, :, 0], G[:, None, 1] - Tc[None, :, 1])
    rk_t = np.argsort(np.argsort(Dgt, 1), 1)[wp[:, 0], wp[:, 1]]
    rk_g = np.argsort(np.argsort(Dgt, 0), 0)[wp[:, 0], wp[:, 1]]
    Ph = ph_matrix(d)
    bg = np.argmax(Ph, 1) if Ph.shape[1] else np.zeros(len(Tc), int)        # tee's best green (prior)
    dout = G[bg] - Tc
    dout = dout / np.maximum(np.hypot(*dout.T), 1.0)[:, None]
    dw = (B - A) / Lw[:, None]
    cos_out = np.sum(dout[wp[:, 1]] * dw, 1)
    bt = np.argmax(Ph, 0) if Ph.shape[0] else np.zeros(len(G), int)
    hole_len = np.hypot(*(G - Tc[bt]).T)
    rel_hole = Lw / np.maximum(hole_len[wp[:, 0]], 30.0)
    ahead = M.sample(Tc[:, None, :] + dout[:, None, :] * np.array([60.0, 110.0, 160.0])[None, :, None], "tree").mean(1)
    tp = M.sample(Tc[:, None, :], "tee")[:, 0] if M.tee is not None else np.full(len(Tc), np.nan)
    pmax = Ph.max(1) if Ph.shape[1] else np.zeros(len(Tc))
    prk = np.argsort(np.argsort(-pmax)).astype(float)
    base = np.c_[_prof(tu, 3), trrun, rk_t, rk_g, cos_out, rel_hole, ahead[wp[:, 1]], tp[wp[:, 1]], prk[wp[:, 1]]]
    if not d.get("_wx4"):
        return base
    # wx4 (NOTES_ROUTING.md 2026-11-20 "walk features"): the tee complex's long axis against the walk and against its
    # best outgoing hole, how much nearer the green's nearest tee / the tee's nearest green is than this pair
    ax = np.array([t.get("ax") if t.get("ax") is not None else (np.nan, np.nan) for t in co["T"]], float).reshape(-1, 2)
    an = np.hypot(*ax.T)
    axu = ax / np.where(an > 0, an, np.nan)[:, None]
    ax_walk = np.abs(np.sum(axu[wp[:, 1]] * dw, 1))
    ax_out = np.abs(np.sum(axu * dout, 1))[wp[:, 1]]
    Dw = Dgt[wp[:, 0], wp[:, 1]]
    gap_t = Dw / np.maximum(Dgt.min(1)[wp[:, 0]], 1.0)
    gap_g = Dw / np.maximum(Dgt.min(0)[wp[:, 1]], 1.0)
    return np.c_[base, ax_walk, ax_out, gap_t, gap_g]


WXF4 = ["wx_ax_walk", "wx_ax_out", "wx_gap_t", "wx_gap_g"]


def wx4_on():
    """walk features wx4 in the tables (ROUTE_LEARN_WX4=1); production reads the model key wx4"""
    return os.environ.get("ROUTE_LEARN_WX4", "0") == "1"


LXF3 = ["lp_bld_big", "lp_bld_big_rk", "lp_bld250", "lp_nbld150", "lp_hub200", "lp_hub350", "lp_other", "lp_pmap",
        "lp_hub_rk"]


def loop_features3(d, scene, M, which):
    """loop start (tee complex) / end (green): buildings of the scene (distance to the largest and to the nearest
    >= 250 m2, how many within 150 yd), hub counts (tees + greens within 200 / 350 yd: the clubhouse is where both
    nines start and end), the nearest other end (a start tee: the nearest green; an end green: the nearest tee),
    P(tee) / P(green) at the point"""
    co, geo = d["co"], d["geo"]
    G = np.asarray(co["G"], float).reshape(-1, 2)
    Tc = np.asarray(geo["Tc"], float).reshape(-1, 2)
    P = Tc if which == "start" else G
    n = len(P)
    if not n:
        return np.zeros((0, len(LXF3)))
    pj = co["pj"]
    bl = [(pj.fwd(*b["centroid"][:2]), float(b.get("area_m2") or 0)) for b in (scene or {}).get("buildings") or []
          if b.get("centroid")]
    if bl:
        B = np.asarray([b[0] for b in bl], float).reshape(-1, 2)
        A = np.asarray([b[1] for b in bl], float)
        D = np.hypot(P[:, None, 0] - B[None, :, 0], P[:, None, 1] - B[None, :, 1])
        big = D[:, int(np.argmax(A))]
        b250 = np.min(np.where(A[None, :] >= 250, D, 9999.0), 1)
        nb = ((D < 150) & (A[None, :] >= 40)).sum(1)
    else:
        big = b250 = np.full(n, 9999.0)
        nb = np.zeros(n)
    allp = np.r_[G, Tc]
    Dp = np.hypot(P[:, None, 0] - allp[None, :, 0], P[:, None, 1] - allp[None, :, 1])
    hub2, hub3 = (Dp < 200).sum(1), (Dp < 350).sum(1)
    O = G if which == "start" else Tc
    other = np.min(np.hypot(P[:, None, 0] - O[None, :, 0], P[:, None, 1] - O[None, :, 1]), 1) if len(O) else np.full(n, 999.0)
    key = "tee" if which == "start" else "green"
    pm = M.sample(P[:, None, :], key)[:, 0] if getattr(M, key) is not None else np.full(n, np.nan)
    return np.c_[np.minimum(big, 3000), np.argsort(np.argsort(big)).astype(float), np.minimum(b250, 3000), nb, hub2,
                 hub3, other, pm, np.argsort(np.argsort(-hub2)).astype(float)]


def x3_table(slug, split, ver=None):
    """hx3 / wx3 of a bench course (LEARN/x3/<slug>.pkl), from the prep pickle + maps + P(green) / P(tee)"""
    import route_bench as RB
    import route_scene as RS
    C, F, Mo, S = RS._mods()
    p = os.path.join(LEARN, "x3", slug + ".pkl")
    if os.path.exists(p):
        o = pickle.load(open(p, "rb"))
        if "sx3" in o:
            return o
    ver = ver or VER
    x, pd = _prep(slug, split, ver)
    if pd is None:
        return None
    d, _ = pd
    pv = ver.split("_", 1)[1]
    scene = RB.rd(RB.scene_path(slug, ver))
    M = bench_maps(slug, scene, pv).bind(d["co"]["pj"])
    Pb = RB.bench_probs(slug, pv)
    if Pb is not None:
        M.green, M.tee = Pb[1], Pb[2]
    d["_Y"] = S.card_sets(x["card"], int(x["n"]))
    d["_wx4"] = wx4_on()
    out = dict(slug=slug, hx3=pair_features3(d, M), wx3=walk_features3(d, M), sx3=loop_features3(d, scene, M, "start"),
               ex3=loop_features3(d, scene, M, "end"))
    import holefield
    if holefield.on():                    # ROUTE_HOLEFIELD: the learned hole field's line integral per pair
        out["hx4"] = holefield.pair_x(slug, d)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    pickle.dump(out, open(p, "wb"))
    return out


def _x3_safe(slug, split):
    try:
        return x3_table(slug, split) is not None
    except Exception as e:                                           # noqa: BLE001
        import traceback
        print(slug, "FAIL", repr(e)[:200], traceback.format_exc()[-400:], flush=True)
        return None


def cmd_x3(split, procs=2):
    import route_bench as RB
    args = [(c["slug"], c["split"]) for c in RB.courses(split) if c.get("card")]
    from multiprocessing import Pool
    with Pool(procs) as pool:
        rs = pool.starmap(_x3_safe, args, chunksize=1)
    print("x3 tables", sum(bool(r) for r in rs), "of", len(rs))


# ----------------------------------------------------------------------------- practice greens
PXF = ["pr_club", "pr_club_rk", "pr_park", "pr_area", "pr_p", "pr_map", "pr_ph1", "pr_ph2", "pr_ng60", "pr_ng120",
       "pr_nt60", "pr_dgreen", "pr_pe", "pr_appr", "pr_bunker", "pr_turf", "pr_cen_rk"]


def prac_features(d, M):
    """[ng, len(PXF)] per candidate green: what a practice / putting green looks like (near the clubhouse and car
    parks, small, next to other greens, no tee playing into it, no fairway corridor leading in, few bunkers)"""
    co, geo = d["co"], d["geo"]
    G = np.asarray(co["G"], float)
    ng = len(G)
    if not ng:
        return np.zeros((0, len(PXF)))
    club = co.get("club")
    dc = np.hypot(*(G - np.asarray(club, float)).T) if club is not None else np.full(ng, np.nan)
    rk = np.argsort(np.argsort(np.where(np.isnan(dc), 1e9, dc))).astype(float)
    pk = np.asarray(co.get("park"), float).reshape(-1, 2)
    dp = np.min(np.hypot(G[:, None, 0] - pk[None, :, 0], G[:, None, 1] - pk[None, :, 1]), 1) if len(pk) \
        else np.full(ng, np.nan)
    ga = d.get("_gattr")
    ga = np.full((ng, 4), np.nan) if ga is None else ga
    Ph = ph_matrix(d)
    srt = -np.sort(-Ph, axis=0) if Ph.shape[0] else np.zeros((2, ng))
    ph1 = srt[0] if len(srt) else np.zeros(ng)
    ph2 = srt[1] if len(srt) > 1 else np.zeros(ng)
    Dgg = np.hypot(G[:, None, 0] - G[None, :, 0], G[:, None, 1] - G[None, :, 1])
    np.fill_diagonal(Dgg, np.inf)
    Tc = np.asarray(geo["Tc"], float).reshape(-1, 2)
    Dgt = np.hypot(G[:, None, 0] - Tc[None, :, 0], G[:, None, 1] - Tc[None, :, 1]) if len(Tc) else np.full((ng, 1), np.inf)
    pe = np.asarray(d["sc"].get("pe", np.zeros(ng)), float)
    # approach corridor: best fairway mean on a line 40 -> 160 yd out from the green, over 16 bearings
    ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    U = np.c_[np.cos(ang), np.sin(ang)]
    s = np.linspace(40, 160, 9)
    Q = G[:, None, None, :] + U[None, :, None, :] * s[None, None, :, None]
    appr = M.sample(Q, "fair").mean(-1).max(-1)
    ring = np.c_[np.cos(ang), np.sin(ang)]
    bk = np.mean([M.sample(G[:, None, :] + r * ring[None], "bunker").mean(1) for r in (12.0, 22.0)], 0)
    tu = np.mean([M.sample(G[:, None, :] + r * ring[None], "turf").mean(1) for r in (15.0, 30.0)], 0)
    cen = G.mean(0)
    crk = np.argsort(np.argsort(-np.hypot(*(G - cen).T))).astype(float)
    return np.c_[dc, rk, dp, ga[:, 1], ga[:, 0], ga[:, 2], ph1, ph2, (Dgg < 60).sum(1), (Dgg < 120).sum(1),
                 (Dgt < 60).sum(1), Dgg.min(1) if ng > 1 else np.full(ng, 999.0), pe, appr, bk, tu, crk]


def prac_labels(d, fc):
    """1 for a candidate green within 20 yd of an OSM golf=green that ends no hole way (+ 30 yd), i.e. a practice /
    putting green (or a green of another course on the site); fc: the course's full OSM feature collection"""
    import routing as R
    pj = d["co"]["pj"]
    G = np.asarray(d["co"]["G"], float)
    truth = R.truth_from_fc(fc)
    ends = np.array([pj.fwd(*np.asarray(t["line"], float)[-1, :2]) for t in truth.values()]).reshape(-1, 2)
    og = []
    for f in fc.get("features", []):
        p = f.get("properties") or {}
        if p.get("golf") != "green":
            continue
        g = f["geometry"]
        rings = [g["coordinates"][0]] if g["type"] == "Polygon" else \
            ([q[0] for q in g["coordinates"]] if g["type"] == "MultiPolygon" else [])
        for r in rings:
            a = np.asarray(r, float)
            og.append(pj.fwd(a[:, 0].mean(), a[:, 1].mean()))
    og = np.asarray(og, float).reshape(-1, 2)
    if len(ends):
        og = og[np.min(np.hypot(og[:, None, 0] - ends[None, :, 0], og[:, None, 1] - ends[None, :, 1]), 1) > 30]
    if not len(og) or not len(G):
        return np.zeros(len(G), int)
    return (np.min(np.hypot(G[:, None, 0] - og[None, :, 0], G[:, None, 1] - og[None, :, 1]), 1) < 20).astype(int)


def prac_table(slug, split, ver=None, sc_dir=None):
    """practice-green feature / label table of a bench course (cache/val/learn/.../prac/<slug>.pkl); the learned
    pe / ph of sc_dir (out-of-fold for train) are used when given"""
    import route_bench as RB
    p = os.path.join(LEARN, "prac", slug + ".pkl")
    if os.path.exists(p):
        return pickle.load(open(p, "rb"))
    ver = ver or VER
    x, pd = _prep(slug, split, ver)
    if pd is None:
        return None
    d, _ = pd
    if sc_dir and os.path.exists(os.path.join(sc_dir, slug + ".pkl")):
        d = dict(d, sc=dict(d["sc"], **pickle.load(open(os.path.join(sc_dir, slug + ".pkl"), "rb"))))
    scene = RB.rd(RB.scene_path(slug, ver))
    M = bench_maps(slug, scene, ver.split("_", 1)[1]).bind(d["co"]["pj"])
    scene, _ = augment_scene(scene, RB.bench_probs(slug, ver.split("_", 1)[1]), n_holes=x["n"])
    d["_tsrc"] = tee_pads_on()
    d["_gattr"], d["_tattr"] = obj_attrs(d, scene, M)
    fc, _, _ = RB.course_files(slug)
    out = dict(slug=slug, px=prac_features(d, M), yp=prac_labels(d, fc), yh=np.asarray(labels(d, x["truth"])["g2h"]) > 0)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    pickle.dump(out, open(p, "wb"))
    return out


# ----------------------------------------------------------------------------- labels
def labels(d, truth):
    """hole pair / walk pair / loop start / loop end labels of real candidates vs the hidden OSM ways (routing.score's
    tolerances: green within 20 yd of the line's end, a tee box within 40 yd of its first 60 %)"""
    import routing as R
    co = d["co"]
    pj = co["pj"]
    G = np.asarray(co["G"], float)
    refs = sorted(truth, key=int)
    lines = []
    for r in refs:
        ln = np.c_[pj.fwd(*np.asarray(truth[r]["line"], float)[:, :2].T)]
        cum = np.r_[0, np.cumsum(np.hypot(*np.diff(ln, axis=0).T))]
        lines.append((ln, ln[:max(2, int(np.searchsorted(cum, 0.6 * cum[-1])) + 1)]))
    g2h = np.full(len(G), -1)
    for gi in range(len(G)):
        dd = [np.hypot(*(G[gi] - ln[-1])) for ln, _ in lines]
        j = int(np.argmin(dd))
        if dd[j] <= 20:
            g2h[gi] = int(refs[j])
    t2h = []
    for t in co["T"]:
        s = set()
        for r, (ln, first) in zip(refs, lines):
            if min(R._seg_dist(np.asarray(p, float), first) for p in t["pts"]) <= 40:
                s.add(int(r))
        t2h.append(s)
    n = d["kind"]
    loop = 9
    yh = np.array([int(g2h[g] > 0 and g2h[g] in t2h[t]) for t, g in d["hp"]], int)
    yw = np.array([int(g2h[g] > 0 and g2h[g] % loop != 0 and (g2h[g] + 1) in t2h[t]) for g, t in d["wp"]], int)
    ys = np.array([int(any((r - 1) % loop == 0 for r in s)) for s in t2h], int)
    ye = np.array([int(g > 0 and g % loop == 0) for g in g2h], int)
    return dict(yh=yh, yw=yw, ys=ys, ye=ye, g2h=g2h, t2h=t2h, n=n)


# ----------------------------------------------------------------------------- tables
def _prep(slug, split, ver):
    import route_bench as RB
    import route_scene as RS
    RS._mods()
    pp = RB.prep_path(slug, "fast", 0, ROUTER, ver)
    x, pd = pickle.load(open(pp, "rb"))
    return x, pd


def table(slug, split, ver=None):
    import route_bench as RB
    import route_scene as RS
    C, F, Mo, S = RS._mods()
    p = os.path.join(LEARN, slug + ".pkl")
    if os.path.exists(p):
        return pickle.load(open(p, "rb"))
    ver = ver or VER
    x, pd = _prep(slug, split, ver)
    if pd is None:
        return None
    d, info = pd
    scene = RB.rd(RB.scene_path(slug, ver))
    M = bench_maps(slug, scene, ver.split("_", 1)[1]).bind(d["co"]["pj"])
    if ROUTER == "v2":
        scene, _ = augment_scene(scene, RB.bench_probs(slug, ver.split("_", 1)[1]), n_holes=x["n"])
    Y = S.card_sets(x["card"], int(x["n"]))
    d["_Y"] = Y
    d["_tsrc"] = tee_pads_on()
    d["_gattr"], d["_tattr"] = obj_attrs(d, scene, M)
    hx2 = pair_features(d, M)
    wx2 = walk_features(d, M)
    lab = labels(d, x["truth"])
    out = dict(slug=slug, split=split, state=None, hx=d["hx"], hx2=hx2, wx=d["wx"], wx2=wx2, lab=lab,
               sx=loop_x(d, "start"), ex=loop_x(d, "end"),
               sc=d["sc"])
    os.makedirs(LEARN, exist_ok=True)
    pickle.dump(out, open(p, "wb"))
    return out


def _state(slug):
    import route_bench as RB
    return next(c["state"] for c in RB.courses() if c["slug"] == slug)


def cmd_table(split, slugs=None, procs=2):
    import route_bench as RB
    cs = [c for c in RB.courses(split) if c.get("card") and (not slugs or c["slug"] in slugs)]
    args = [(c["slug"], c["split"]) for c in cs]
    if procs > 1:
        from multiprocessing import Pool
        with Pool(procs) as pool:
            rs = pool.starmap(_table_safe, args, chunksize=1)
    else:
        rs = [_table_safe(*a) for a in args]
    print("tables", sum(r is not None for r in rs), "of", len(rs))


def _table_safe(slug, split):
    try:
        return table(slug, split) is not None
    except Exception as e:                                           # noqa: BLE001
        print(slug, "FAIL", repr(e)[:200], flush=True)
        return None


# ----------------------------------------------------------------------------- models
HPAR = dict(n_estimators=300, learning_rate=0.04, num_leaves=15, min_child_samples=20, subsample=0.8,
            subsample_freq=1, colsample_bytree=0.8, reg_lambda=2.0, verbose=-1, n_jobs=2)
HPAR.update(json.loads(os.environ.get("ROUTE_LEARN_HPAR") or "{}"))


X3 = os.environ.get("ROUTE_LEARN_X3", "1") == "1"      # + pair_features3 / walk_features3 / loop_features3 (LEARN/x3)


def _X(t, kind):
    if kind == "h":
        X = np.c_[t["hx"], t["hx2"], t["hx3"]] if "hx3" in t else np.c_[t["hx"], t["hx2"]]
        return np.c_[X, t["hx4"]] if "hx4" in t else X
    if kind in ("s", "e"):
        return np.c_[t[kind + "x"], t[kind + "x3"]] if kind + "x3" in t else t[kind + "x"]
    return np.c_[t["wx"], t["wx2"], t["wx3"]] if "wx3" in t else np.c_[t["wx"], t["wx2"]]


def loop_x(d, which):
    """loop start (tee complex) / end (green) features: joint models.loop_features (clubhouse / car park / centre
    distances and ranks) + how many tees / greens are close by (1 / 10 tees and 9 / 18 greens gather at the
    clubhouse) + the old hole model's best hole from / into it"""
    import route_scene as RS
    C, F, Mo, S = RS._mods()
    co, geo = d["co"], d["geo"]
    base = Mo.loop_features(co, geo, which)
    G = np.asarray(co["G"], float)
    Tc = np.asarray(geo["Tc"], float)
    P = Tc if which == "start" else G
    nt = np.sum(np.hypot(P[:, None, 0] - Tc[None, :, 0], P[:, None, 1] - Tc[None, :, 1]) < 120, 1)
    ng = np.sum(np.hypot(P[:, None, 0] - G[None, :, 0], P[:, None, 1] - G[None, :, 1]) < 120, 1)
    Ph = ph_matrix(d)
    best = Ph.max(1) if which == "start" else Ph.max(0)
    return np.c_[base, nt, ng, best]


def _fit(ts, kind):
    import lightgbm as lgb
    X = np.vstack([_X(t, kind) for t in ts])
    y = np.concatenate([t["lab"]["y" + kind] for t in ts])
    m = lgb.LGBMClassifier(**HPAR)
    m.fit(X, y)
    return m


def predict(models, t):
    out = {}
    for kind, key in (("h", "ph"), ("w", "pw"), ("s", "ps"), ("e", "pe")):
        m = models.get(kind)
        X = _X(t, kind)
        if m is not None and len(X):
            out[key] = m.predict_proba(X)[:, 1]
    return out


def load_tables(split):
    import route_bench as RB
    ts = []
    for c in RB.courses(split):
        p = os.path.join(LEARN, c["slug"] + ".pkl")
        if os.path.exists(p):
            t = pickle.load(open(p, "rb"))
            t["state"] = c["state"]
            q = os.path.join(LEARN, "x3", c["slug"] + ".pkl")
            if X3:
                if not os.path.exists(q):
                    continue
                t.update({k: v for k, v in pickle.load(open(q, "rb")).items() if k != "slug"})
            ts.append(t)
    return ts


KINDS = tuple(os.environ.get("ROUTE_LEARN_KINDS", "h,w").split(","))
TRAIN = os.environ.get("ROUTE_LEARN_TRAIN", "train")      # 'train+big': + TRAIN-BIG (route_big.py)


def cmd_cv(out_dir, k=5, kinds=KINDS):
    """out-of-fold sc overrides for the train courses (folds by state), written to out_dir/<slug>.pkl"""
    ts = load_tables(TRAIN)
    states = sorted({t["state"] for t in ts})
    fold = {s: i % k for i, s in enumerate(states)}
    os.makedirs(out_dir, exist_ok=True)
    for i in range(k):
        tr = [t for t in ts if fold[t["state"]] != i]
        te = [t for t in ts if fold[t["state"]] == i]
        if not te:
            continue
        ms = {kind: _fit(tr, kind) for kind in kinds}
        for t in te:
            pickle.dump(predict(ms, t), open(os.path.join(out_dir, t["slug"] + ".pkl"), "wb"))
    print("cv", len(ts), "courses ->", out_dir)


def cmd_fit(out_dir, kinds=KINDS):
    ts = load_tables(TRAIN)
    ms = {kind: _fit(ts, kind) for kind in kinds}
    pickle.dump(dict(models=ms, XF=XF + ["t_src"] * tee_pads_on(), WXF=WXF, n_train=len(ts), x3=X3, tsrc=tee_pads_on(),
                     x4=any("hx4" in t for t in ts),
                     wx4=wx4_on(),
                     **(dict(XF3=XF3, WXF3=WXF3, LXF3=LXF3) if X3 else {})), open(MODEL, "wb"))
    os.makedirs(out_dir, exist_ok=True)
    for t in load_tables("test"):
        pickle.dump(predict(ms, t), open(os.path.join(out_dir, t["slug"] + ".pkl"), "wb"))
    print("fit on", len(ts), "train courses ->", MODEL)


PPAR = dict(n_estimators=200, learning_rate=0.05, num_leaves=7, min_child_samples=15, subsample=0.8, subsample_freq=1,
            colsample_bytree=0.8, reg_lambda=2.0, verbose=-1, n_jobs=2)


def _prac_rows(split):
    import route_bench as RB
    out = []
    for c in RB.courses(split):
        q = os.path.join(LEARN, "prac", c["slug"] + ".pkl")
        if os.path.exists(q):
            t = pickle.load(open(q, "rb"))
            t["state"] = c["state"]
            out.append(t)
    return out


def _pmask(t):
    """rows the practice model trains on: OSM non-hole greens that a detected tee plays into well (ph >= 0.5) are
    greens of another course on the site (27 / 36-hole sites), not practice greens: left out"""
    return ~((t["yp"] == 1) & (t["px"][:, PXF.index("pr_ph1")] >= 0.5))


def _pfit(ts):
    import lightgbm as lgb
    m = lgb.LGBMClassifier(**PPAR)
    m.fit(np.vstack([t["px"][_pmask(t)] for t in ts]), np.concatenate([t["yp"][_pmask(t)] for t in ts]))
    return m


def _merge_sc(out_dir, slug, extra):
    q = os.path.join(out_dir, slug + ".pkl")
    cur = pickle.load(open(q, "rb")) if os.path.exists(q) else {}
    cur.update(extra)
    pickle.dump(cur, open(q, "wb"))


def cmd_prac(out_dir, k=5):
    """practice-green model: out-of-fold P(practice) per train green -> out_dir/cv, all-train fit -> the model file
    (models['p']) and out_dir/test. The sc override pickles there gain 'pp' (copy sc5's first)."""
    from sklearn.metrics import roc_auc_score
    ts = _prac_rows("train")
    states = sorted({t["state"] for t in ts})
    fold = {s: i % k for i, s in enumerate(states)}
    ys, ps = [], []
    for i in range(k):
        tr = [t for t in ts if fold[t["state"]] != i]
        m = _pfit(tr)
        for t in ts:
            if fold[t["state"]] == i and len(t["px"]):
                p = m.predict_proba(t["px"])[:, 1]
                _merge_sc(os.path.join(out_dir, "cv"), t["slug"], dict(pp=p))
                ys.append(t["yp"][_pmask(t)])
                ps.append(p[_pmask(t)])
    print("practice AUC (train out-of-fold)", round(roc_auc_score(np.concatenate(ys), np.concatenate(ps)), 4))
    m = _pfit(ts)
    if os.path.exists(MODEL):
        mm = pickle.load(open(MODEL, "rb"))
        mm["models"]["p"] = m
        mm["PXF"] = PXF
        pickle.dump(mm, open(MODEL, "wb"))
    for t in _prac_rows("test"):
        if len(t["px"]):
            _merge_sc(os.path.join(out_dir, "test"), t["slug"], dict(pp=m.predict_proba(t["px"])[:, 1]))


_MODEL = {}


def rescore(d, scene, M, card=None, n_holes=None, path=MODEL):
    """production: replace d['sc'] ph / pw with the learned models' scores (route_learn_model.pkl, fitted on the
    bench's train split). scene: the (augmented) scene the candidates came from; M: Maps bound to d's projection.
    -> True when rescored (False without a model file)"""
    import route_scene as RS
    C, F, Mo, S = RS._mods()
    if path not in _MODEL:
        _MODEL[path] = pickle.load(open(path, "rb")) if os.path.exists(path) else None
    m = _MODEL[path]
    if m is None:
        return False
    d["_Y"] = S.card_sets(card if card is not None else d.get("card"), int(n_holes or d["kind"]))
    d["_tsrc"] = bool(m.get("tsrc"))
    d["_wx4"] = bool(m.get("wx4"))
    d["_gattr"], d["_tattr"] = obj_attrs(d, scene, M)
    t = dict(hx=d["hx"], hx2=pair_features(d, M), wx=d["wx"], wx2=walk_features(d, M), sx=loop_x(d, "start"),
             ex=loop_x(d, "end"))
    if m.get("x3"):                       # the richer local features (pair_features3 ...), read before ph is replaced
        t.update(hx3=pair_features3(d, M), wx3=walk_features3(d, M), sx3=loop_features3(d, scene, M, "start"),
                 ex3=loop_features3(d, scene, M, "end"))
    if m.get("x4"):                       # the hole-field features: the course's field when one is at hand
        import holefield
        t["hx4"] = holefield.pair_x(d.get("_slug") or "", d)
    d["sc"] = dict(d["sc"], **predict(m["models"], t))
    if m["models"].get("p") is not None and len(d["co"]["G"]):
        d["sc"]["pp"] = m["models"]["p"].predict_proba(prac_features(d, M))[:, 1]
    d["_maps"] = M
    d.pop("_pw", None)
    return True


def auc_report(split, sc_dir):
    """pair-level AUC / top-1 accuracy of the old vs new hole scores"""
    from sklearn.metrics import roc_auc_score
    ts = load_tables(split)
    yo, po, pn = [], [], []
    for t in ts:
        p = os.path.join(sc_dir, t["slug"] + ".pkl")
        if not os.path.exists(p):
            continue
        new = pickle.load(open(p, "rb"))
        yo.append(t["lab"]["yh"])
        po.append(t["sc"]["ph"])
        pn.append(new.get("ph", t["sc"]["ph"]))
    y = np.concatenate(yo)
    print(split, "pairs", len(y), "pos", int(y.sum()), "AUC old", round(roc_auc_score(y, np.concatenate(po)), 4),
          "new", round(roc_auc_score(y, np.concatenate(pn)), 4))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--split", default="train")
    ap.add_argument("--slugs", default="")
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(CACHE, "val", "sc"))
    a = ap.parse_args()
    if a.cmd == "table":
        cmd_table(a.split, a.slugs.split(",") if a.slugs else None, a.procs)
    elif a.cmd == "cv":
        cmd_cv(os.path.join(a.out, "cv"))
        auc_report("train", os.path.join(a.out, "cv"))
    elif a.cmd == "fit":
        cmd_fit(os.path.join(a.out, "test"))
    elif a.cmd == "x3":
        cmd_x3(a.split, a.procs)
    elif a.cmd == "prac":
        cmd_prac(a.out)
