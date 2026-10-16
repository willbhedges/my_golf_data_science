"""Landing-zone QA: where the hand map's hazard edges disagree with independent evidence.

  python3 spirit_hollow/qa_landing/disagree.py              # rank -> disagree.json / disagree.md
  python3 spirit_hollow/qa_landing/disagree.py --render 20  # + evidence crops for the top 20
  python3 spirit_hollow/qa_landing/disagree.py --impact     # + EV with / without proposed_patches.py
  python3 spirit_hollow/qa_landing/disagree.py --all        # all three (re-run after every map change)
  options: --holes 14,11   restrict;  --n 3000  shots per club/aim

What is compared (per hole, on a 1-yd grid of the tee-shot corridor, 190-335 yds along the
app's tee line, +/-55 yds of it; 10 extra yards of padding so edge distances are right):

  hand map   course.HOLES (AUDIT_FIXES + first_cut included), lie_at() as the simulation sees it.
             Penal = recovery (trees), native (long grass), water, sand, ob.
  evidence   all independent of the hand trace, georeferenced through the screenshot -> NAIP
             registration in course_data/spirit_hollow/hand_zones_ll.json (geo_zones.ShotGeo):
    trees    USGS 3DEP lidar canopy, height above ground > 2.5 m (vision_any layers.tif class 2,
             which fills lidar gaps with the Meta CHM, OR raw/hag.tif > 2.5 m). Straight-down,
             summer: this is where the canopy really is on the ground.
    native   vision_any long-grass layer (NAIP self-supervised from OSM seeds) AND the vision2
             screenshot classifier (out-of-sample LOHO probabilities) agreeing.
    water    >= 2 of: OSM water, vision_any water, NAIP rule (NDVI < 0.05 and dark NIR),
             vision2 p(water) > 0.5.
    sand     OSM bunker, or the NAIP rule (bright, NDVI < 0.15) with vision2 p(sand) > 0.4.
    ob       no independent evidence: never scored.

  Kinds of disagreement (each needs > TOL = 4 yds of edge position, to absorb registration error
  and trunk-vs-canopy tracing):
    missing  hand says playable (fairway / first_cut / rough), evidence says hazard c, and the
             cell is > TOL from every hand hazard cell (the evidence edge sits > TOL further in).
    phantom  hand says hazard c, no source sees c (or any other hazard) there, and the cell is
             > TOL from every evidence-c cell (the hand edge sits > TOL too far out).
    swap     hand says hazard c1, evidence says c2 (trees <-> long grass <-> water), > TOL from
             hand-c2 and with no evidence of c1. Weighted 0.5 (both are trouble, only the cost differs).

  Ranking = decision impact: share of simulated tee shots (final_decision.json pick 2/3 + runner-up
  1/3, at their aims; each = 1/2 landing spot + 1/2 resting spot, tee_strategy.simulate, central
  prior: driver width 70, depth x1.25, roll 0.975, trees 0.8, lost ball 0.5) in the disputed
  cells, times an edge weight exp(-d / 12 yds), d = distance from the hand fairway / first cut:
  a 5-yd error at the fairway edge counts far more than one deep in the woods.

Outputs (this folder): disagree.json (every component, with an auto-drafted polygon patch in
screenshot px), disagree.md (ranked table), crops/NN_<hole>.png (screenshot | NAIP 2023 |
lidar + layers + OSM | vision2 | hand map, with the disputed cells outlined), impact.json/.md
(expected strokes per club, best aim, with and without each proposed patch; N shots, common z).
"""
import argparse
import copy
import json
import os
import sys
import types

import numpy as np
from matplotlib.path import Path
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
ROOT = os.path.dirname(SH)
# qa_landing/render.py (an older script) would shadow course_data/imagery/render.py: keep this
# folder off sys.path and the imagery package first.
_IMG = os.path.join(ROOT, "course_data", "imagery")
sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.getcwd()) != HERE]
for _p in (os.path.join(ROOT, "mozingo"), SH, _IMG):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import course                                    # noqa: E402
import tee_strategy as t                         # noqa: E402

ALONG = (190.0, 335.0)
HALF = 55.0
PAD = 10.0
TOL = 4.0
EDGE_SCALE = 12.0
MIN_CELLS = 6
PLAYABLE = ("fairway", "first_cut", "rough")
HAZ = ("recovery", "native", "water", "sand")      # hazards with independent evidence
KIND_W = {"missing": 1.0, "phantom": 1.0, "swap": 0.5}
LABEL = {"recovery": "trees", "native": "long grass", "water": "water", "sand": "sand", "ob": "OB"}

VA = os.path.join(ROOT, "course_data", "vision_any", "spirit_hollow")
NAIP_DIR = os.path.join(ROOT, "course_data", "imagery", "spirit_hollow")
HAND_LL = os.path.join(ROOT, "course_data", "spirit_hollow", "hand_zones_ll.json")
PROBS = os.path.join(SH, "output", "vision2", "probs_loho")
FINAL = os.path.join(SH, "output", "final_decision.json")
V2_CLASSES = ["fairway", "rough", "trees", "native", "water", "sand"]
V2_TOP, V2_BOTTOM, V2_SCALE = 545, 1830, 2          # vision.py: UI header/footer, feature px = 2 screen px


def _key(k):
    return int(k) if str(k).isdigit() else str(k)


# ----------------------------------------------------------------------------- geometry
def grid(h, along=ALONG, half=HALF, pad=PAD, step=1.0):
    """(a, l, px): along / lateral yd axes and the (na, nl, 2) screenshot px of every cell."""
    a = np.arange(along[0] - pad, along[1] + pad + 1e-6, step)
    l = np.arange(-half - pad, half + pad + 1e-6, step)
    tee, f, r, ppy = t.hole_frame(h)
    A, L = np.meshgrid(a, l, indexing="ij")
    px = tee + (A[..., None] * f + L[..., None] * r) * ppy
    return a, l, px


def core_mask(a, l, along=ALONG, half=HALF):
    return ((a[:, None] >= along[0]) & (a[:, None] <= along[1])) & (np.abs(l)[None, :] <= half)


def to_px(h, along, lat):
    tee, f, r, ppy = t.hole_frame(h)
    return tee + (np.asarray(along, float)[..., None] * f + np.asarray(lat, float)[..., None] * r) * ppy


def to_yd(h, px):
    tee, f, r, ppy = t.hole_frame(h)
    d = (np.asarray(px, float) - tee) / ppy
    return d @ f, d @ r


def hand_lies(h, px):
    shp = px.shape[:2]
    return t.lie_at(h, px.reshape(-1, 2)).reshape(shp)


def dist_to(mask):
    """Yards (1-yd grid) from every cell to the nearest True cell (inf if none)."""
    if not mask.any():
        return np.full(mask.shape, np.inf)
    return ndimage.distance_transform_edt(~mask)


# ----------------------------------------------------------------------------- evidence
class Raster:
    def __init__(self, path, bands=None):
        import rasterio
        from pyproj import Transformer
        with rasterio.open(path) as src:
            self.data = src.read(bands) if bands else src.read()
            self.tr = src.transform
            self.nodata = src.nodata
            self.crs = src.crs.to_string()
        self.ll2 = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)

    def colrow(self, ll):
        x, y = self.ll2.transform(ll[:, 0], ll[:, 1])
        inv = ~self.tr
        c, r = inv * (np.asarray(x), np.asarray(y))
        return np.asarray(c), np.asarray(r)

    def sample(self, ll, band=0, fill=0):
        c, r = self.colrow(ll)
        ci, ri = np.floor(c).astype(int), np.floor(r).astype(int)
        H, W = self.data.shape[1:]
        ok = (ci >= 0) & (ci < W) & (ri >= 0) & (ri < H)
        out = np.full(len(ll), fill, self.data.dtype)
        out[ok] = self.data[band, ri[ok], ci[ok]]
        return out, ok


class NAIP:
    """NAIP 2023 RGB + NIR, sampled with a ~1 m box blur (3 x 3 source px)."""

    def __init__(self, d=NAIP_DIR):
        import rasterio
        from pyproj import Transformer
        self.rgb_path, self.nir_path = os.path.join(d, "naip_rgb.tif"), os.path.join(d, "naip_nir.tif")
        with rasterio.open(self.rgb_path) as src:
            self.tr, self.crs, self.W, self.H = src.transform, src.crs.to_string(), src.width, src.height
        self.ll2 = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
        self._rio = rasterio

    def sample(self, ll):
        from rasterio.windows import Window
        x, y = self.ll2.transform(ll[:, 0], ll[:, 1])
        c, r = (~self.tr) * (np.asarray(x), np.asarray(y))
        c, r = np.asarray(c), np.asarray(r)
        c0, r0 = int(max(np.floor(c.min()) - 3, 0)), int(max(np.floor(r.min()) - 3, 0))
        c1, r1 = int(min(np.ceil(c.max()) + 3, self.W)), int(min(np.ceil(r.max()) + 3, self.H))
        win = Window(c0, r0, c1 - c0, r1 - r0)
        with self._rio.open(self.rgb_path) as s:
            rgb = s.read([1, 2, 3], window=win).astype(np.float32)
        with self._rio.open(self.nir_path) as s:
            nir = s.read(1, window=win).astype(np.float32)
        g = rgb.mean(0)
        m1, m2 = ndimage.uniform_filter(g, 5), ndimage.uniform_filter(g * g, 5)
        tex = np.sqrt(np.maximum(m2 - m1 * m1, 0))                  # canopy is rough, mown grass smooth
        st = np.concatenate([rgb, nir[None]], 0)
        st = ndimage.uniform_filter(st, size=(1, 3, 3))
        st = np.concatenate([st, tex[None]], 0)
        ci = np.clip(np.floor(c).astype(int) - c0, 0, st.shape[2] - 1)
        ri = np.clip(np.floor(r).astype(int) - r0, 0, st.shape[1] - 1)
        ok = (c >= 0) & (c < self.W) & (r >= 0) & (r < self.H)
        v = st[:, ri, ci]
        return v[:3].T, v[3], v[4], ok


def osm_polys():
    import geo_zones as GZ
    o = GZ.osm_features()
    return {"water": o["water"], "bunker": o["bunker"]}


def in_polys_ll(polys, g, px):
    out = np.zeros(len(px), bool)
    for ring in polys:
        q = g.ll_to_px(np.asarray(ring, float))
        bb0, bb1 = q.min(0) - 2, q.max(0) + 2
        m = np.all((px >= bb0) & (px <= bb1), axis=1)
        if m.any():
            out[m] |= Path(q).contains_points(px[m])
    return out


class Evidence:
    def __init__(self):
        import geo_zones as GZ
        self.G = GZ.transforms_from_json(json.load(open(HAND_LL)))
        self.layers = Raster(os.path.join(VA, "layers.tif"))
        hp = os.path.join(VA, "raw", "hag.tif")
        self.hag = Raster(hp) if os.path.exists(hp) else None
        self.naip = NAIP()
        self.osm = osm_polys()
        self._v2 = {}

    def v2(self, k):
        if k not in self._v2:
            p = os.path.join(PROBS, f"{k}.npz")
            self._v2[k] = np.load(p)["probs"].astype(np.float32) if os.path.exists(p) else None
        return self._v2[k]

    def sample(self, k, px):
        """Per-cell evidence dict (flattened arrays) for screenshot px (n, 2) of hole k."""
        g = self.G[_key(k)]
        ll = g.px_to_ll(px)
        L, okL = self.layers.sample(ll, 0)
        pn, _ = self.layers.sample(ll, 1)
        e = dict(ll_ok=okL)
        e["lay_native"] = (L == 1) & okL
        e["lay_trees"] = (L == 2) & okL
        e["lay_water"] = (L == 3) & okL
        e["lay_pnative"] = pn.astype(np.float32) / 255.0
        if self.hag is not None:
            hv, okh = self.hag.sample(ll, 0, fill=255)
            hm = np.where((hv == 255) | ~okh, np.nan, hv.astype(np.float32) * 0.25)
        else:
            hm = np.full(len(px), np.nan)
        e["hag_m"] = hm
        e["lidar_trees"] = e["lay_trees"] | (np.nan_to_num(hm, nan=0.0) > 2.5)
        rgb, nir, tex, okn = self.naip.sample(ll)
        red = rgb[:, 0]
        ndvi = (nir - red) / (nir + red + 1e-6)
        bright = rgb.mean(1)
        e["ndvi"], e["bright"] = ndvi, bright
        e["naip_tex"] = tex
        e["naip_tree"] = okn & (tex > 11) & (ndvi > 0.2)
        e["naip_water"] = okn & (ndvi < 0.05) & (nir < 90)
        e["naip_sand"] = okn & (ndvi < 0.15) & (bright > 150)
        e["osm_water"] = in_polys_ll(self.osm["water"], g, px)
        e["osm_bunker"] = in_polys_ll(self.osm["bunker"], g, px)
        P = self.v2(k)
        x, y = px[:, 0], px[:, 1]
        okv = (P is not None) & (x >= 0) & (x < 920) & (y >= V2_TOP) & (y < V2_BOTTOM)
        okv = np.asarray(okv, bool) & np.ones(len(px), bool)
        probs = np.zeros((len(px), 6), np.float32)
        if P is not None:
            ri = np.clip((y // V2_SCALE).astype(int), 0, P.shape[0] - 1)
            ci = np.clip((x // V2_SCALE).astype(int), 0, P.shape[1] - 1)
            probs[okv] = P[ri[okv], ci[okv]]
        e["v2_ok"] = okv
        for i, c in enumerate(V2_CLASSES):
            e["v2_" + c] = probs[:, i]
        return e


def strong_weak(e):
    """{class: (strong, weak, absent)} evidence masks. strong = confident hazard; weak = any source
    sees it (used for tolerance); absent = no source sees it."""
    v = lambda c: e["v2_" + c] * e["v2_ok"]                                        # noqa: E731
    out = {}
    nt = e.get("naip_tree_s", e["naip_tree"].astype(float))
    lid = e["lidar_trees"]
    tr = lid & ((nt > 0.25) | (v("trees") > 0.4))       # 2019 lidar, confirmed by 2023 NAIP or the photo
    out["recovery"] = (tr, lid | (v("trees") > 0.5), ~lid & (v("trees") < 0.3) & (nt < 0.35))
    nat_s = e["lay_native"] & (v("native") > 0.35)
    nat_w = e["lay_native"] | (e["lay_pnative"] > 0.4) | (v("native") > 0.5)
    out["native"] = (nat_s, nat_w, ~e["lay_native"] & (e["lay_pnative"] < 0.3) & (v("native") < 0.2))
    wv = (e["osm_water"].astype(int) + e["lay_water"] + e["naip_water"] + (v("water") > 0.5))
    out["water"] = (wv >= 2, wv >= 1, (wv == 0) & (v("water") < 0.2))
    sand_s = e["osm_bunker"] | (e["naip_sand"] & (v("sand") > 0.4))
    sand_w = e["osm_bunker"] | e["naip_sand"] | (v("sand") > 0.4)
    out["sand"] = (sand_s, sand_w, ~sand_w & (v("sand") < 0.2))
    return out


# ----------------------------------------------------------------------------- shot density
def central_model():
    """Prior-median version of final_decision.py's model (no map jitter)."""
    import decision as D
    wd = D.BASE["clubs"]["Driver"][2] * 70.0 / 65.0
    ratio = {"Driver": 1.0, "2-wood": 0.94, "4-wood": 0.85}
    roll, depth = 0.975, 1.25
    t.CLUBS = {k: (c, c + (tot - c) * roll, wd * ratio[k], d * depth)
               for k, (c, tot, w, d) in D.BASE["clubs"].items()}
    w4 = wd * ratio["4-wood"]
    t.IRONS = {k: (c, c + (tot - c) * roll, w4 * w / D.BASE["clubs"]["4-wood"][2], d * depth)
               for k, (c, tot, w, d) in D.BASE["irons"].items()}
    t.TREE_SEVERITY, t.NATIVE_LOST = 0.8, 0.5
    t.MISHIT_RATE = {k: 0.15 for k in D.BASE["mis"]}
    t.ROUGH_ROLL, t.HCP_BASELINE = 0.325, False


def common_z(n, seed=2027):
    rng = np.random.default_rng(seed)
    return np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])


def picks(k):
    fd = json.load(open(FINAL)) if os.path.exists(FINAL) else {}
    r = fd.get(str(k))
    if not r:
        return [("Driver", 0.0, 1.0)]
    out = [(r["pick"], float(r["aim"]), 2 / 3)]
    run = r.get("runner")
    if run and run in r.get("clubs", {}):
        out.append((run, float(r["clubs"][run]["aim"]), 1 / 3))
    else:
        out[0] = (out[0][0], out[0][1], 1.0)
    return out


def shot_density(k, a, l, z, holes=None):
    """Share of shots per 1-yd cell: picked club 2/3 + runner-up 1/3; each half landing, half rest."""
    holes = holes if holes is not None else course.HOLES
    saved = t.HOLES
    t.HOLES = dict(holes)
    h = holes[k]
    stop = dict(h, zones=[("sand", [(-5000, -5000), (6000, -5000), (6000, 7000), (-5000, 7000)])])
    dens = np.zeros((len(a), len(l)))
    ea = np.r_[a - 0.5, a[-1] + 0.5]
    el = np.r_[l - 0.5, l[-1] + 0.5]
    try:
        for club, aim, w in picks(k):
            for zones_h, half in ((stop, 0.5), (h, 0.5)):
                t.HOLES[k] = zones_h
                pts = t.simulate(k, club, aim, z=z)[0]
                al, la = to_yd(h, pts)
                H2, _, _ = np.histogram2d(al, la, bins=[ea, el])
                dens += w * half * H2 / z.shape[1]
            t.HOLES[k] = h
    finally:
        t.HOLES = saved
    return ndimage.gaussian_filter(dens, 1.0)


# ----------------------------------------------------------------------------- disagreement
def classify_cells(hand, ev, core, tol=TOL):
    """-> list of (kind, cls, mask, edge_dist) disagreement masks (pure: hand lie array + evidence
    {class: (strong, weak, absent)} masks on the same 2-D grid)."""
    hand_haz = np.isin(hand, HAZ + ("ob",))
    playable = np.isin(hand, PLAYABLE)
    d_hand_haz = dist_to(hand_haz)
    any_strong = np.zeros(hand.shape, bool)
    for c in HAZ:
        any_strong |= ev[c][0]
    out = []
    for c in HAZ:
        strong, weak, absent = ev[c]
        m = playable & strong & (d_hand_haz > tol) & core
        out.append(("missing", c, m, d_hand_haz))
        d_ev = dist_to(weak)
        others = any_strong & ~strong
        m = (hand == c) & absent & ~others & (d_ev > tol) & core
        out.append(("phantom", c, m, d_ev))
    for c1 in ("recovery", "native", "water"):
        for c2 in ("recovery", "native", "water"):
            if c1 == c2:
                continue
            d_h2 = dist_to(hand == c2)
            m = (hand == c1) & ev[c2][0] & ev[c1][2] & (d_h2 > tol) & core
            out.append(("swap", c1 + ">" + c2, m, d_h2))
    return out


def components(kind, cls, mask, dist, a, l, dens, w_edge, min_cells=MIN_CELLS, tol=TOL):
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    res = []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < min_cells:
            continue
        ii, jj = np.nonzero(m)
        rows = {}
        for r_, d_ in zip(ii, dist[m]):
            rows[r_] = max(rows.get(r_, 0.0), float(d_))
        shift = np.array(list(rows.values()))
        if shift.max() < tol + 1:
            continue
        share = float(dens[m].sum())
        score = float((dens * w_edge)[m].sum()) * KIND_W[kind]
        res.append(dict(kind=kind, cls=cls, cells=int(m.sum()), mask=m,
                        along=(float(a[ii].min()), float(a[ii].max())),
                        lat=(float(l[jj].min()), float(l[jj].max())),
                        centre=(float(a[ii].mean()), float(l[jj].mean())),
                        edge_shift_med=float(np.median(shift)), edge_shift_max=float(shift.max()),
                        share=share, score=score, d_fw_min=None))
    return res


def patch_mask(comp, hand, ev, tol=TOL):
    """Grid cells the patch should cover: the component grown back across the tolerance band to
    the hand edge, limited to where the evidence agrees."""
    m = comp["mask"]
    grow = ndimage.binary_dilation(m, iterations=int(tol) + 2)
    kind, cls = comp["kind"], comp["cls"]
    if kind == "missing":
        keep = ev[cls][0] & np.isin(hand, PLAYABLE)
    elif kind == "phantom":
        keep = (hand == cls) & ev[cls][2]
    else:
        c1, c2 = cls.split(">")
        keep = (hand == c1) & ev[c2][0]
    pm = m | (grow & keep)
    pm = ndimage.binary_closing(pm, iterations=1) | m
    return ndimage.binary_opening(pm, iterations=1) | m


def mask_polygon(h, mask, a, l, eps=1.2):
    import cv2
    # the contour runs through cell centres: grow one cell so the polygon reaches the cell edges
    m8 = ndimage.binary_dilation(mask, iterations=1).astype(np.uint8)
    cs, _ = cv2.findContours(m8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs:
        return None
    c = max(cs, key=cv2.contourArea)
    c = cv2.approxPolyDP(c, eps, True)[:, 0, :]            # (x = lat index, y = along index)
    if len(c) < 3:
        return None
    step_a, step_l = a[1] - a[0], l[1] - l[0]
    px = to_px(h, a[0] + c[:, 1] * step_a, l[0] + c[:, 0] * step_l)
    return [(int(round(x)), int(round(y))) for x, y in px]


def osm_bunkers_px(k, near_px, radius_px=40, G=None):
    """OSM bunker outlines (screenshot px, simplified to ~1 px) whose centre is near `near_px`."""
    import geo_zones as GZ
    from shapely.geometry import Polygon
    G = G or GZ.transforms_from_json(json.load(open(HAND_LL)))
    out = []
    for ring in GZ.osm_features()["bunker"]:
        q = G[_key(k)].ll_to_px(np.asarray(ring, float))
        if np.hypot(*(q.mean(0) - np.asarray(near_px, float))) < radius_px:
            P = Polygon(q).simplify(1.0)
            out.append([(int(round(x)), int(round(y))) for x, y in list(P.exterior.coords)[:-1]])
    return out


def sand_patch(k, rings, holes=None):
    """Replace the hand sand boxes that overlap `rings` by the rings: the parts of the boxes outside
    the rings get back the lie the hand map has there without the sand (fairway / first_cut /
    rough), then the rings are drawn as sand. AUDIT_FIXES format."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    holes = holes if holes is not None else course.HOLES
    h = holes[_key(k)]
    R_ = unary_union([Polygon(r) for r in rings])
    boxes = [Polygon(p) for nm, p in h["zones"] if nm == "sand" and Polygon(p).intersects(R_)]
    out = []
    if boxes:
        rest = unary_union(boxes).difference(R_)
        geoms = getattr(rest, "geoms", [rest])
        nosand = dict(h, zones=[z for z in h["zones"] if z[0] != "sand"])
        for gm in geoms:
            if gm.is_empty or gm.area < 20:
                continue
            gm = gm.simplify(1.0)
            pt = gm.representative_point()
            lie = t.lie_at(nosand, np.array([[pt.x, pt.y]]))[0]
            out.append((str(lie), [(int(round(x)), int(round(y))) for x, y in list(gm.exterior.coords)[:-1]]))
    out += [("sand", r) for r in rings]
    return out


def patch_lie(comp):
    if comp["kind"] == "missing":
        return comp["cls"]
    if comp["kind"] == "phantom":
        return "rough"
    return comp["cls"].split(">")[1]


def describe(comp):
    k, c = comp["kind"], comp["cls"]
    if k == "missing":
        return f"evidence {LABEL[c]}, map playable"
    if k == "phantom":
        return f"map {LABEL[c]}, evidence playable"
    c1, c2 = c.split(">")
    return f"map {LABEL[c1]}, evidence {LABEL[c2]}"


def evidence_summary(comp, e2):
    m = comp["mask"]
    keys = ["lidar_trees", "naip_tree_s", "lay_native", "lay_water", "naip_water", "naip_sand", "osm_water", "osm_bunker"]
    s = {kk: round(float(e2[kk][m].mean()), 2) for kk in keys}
    for c in V2_CLASSES:
        s["v2_" + c] = round(float(e2["v2_" + c][m].mean()), 2)
    hm = e2["hag_m"][m]
    s["hag_med_m"] = round(float(np.nanmedian(hm)), 1) if np.isfinite(hm).any() else None
    s["ndvi_med"] = round(float(np.median(e2["ndvi"][m])), 2)
    return s


def analyse_hole(k, E, z, holes=None):
    holes = holes if holes is not None else course.HOLES
    h = holes[k]
    a, l, px = grid(h)
    shp = px.shape[:2]
    hand = hand_lies(h, px)
    e = E.sample(k, px.reshape(-1, 2))
    e2 = {kk: (v.reshape(shp) if isinstance(v, np.ndarray) and v.shape[:1] == (shp[0] * shp[1],) else v)
          for kk, v in e.items()}
    e["naip_tree_s"] = ndimage.uniform_filter(e2["naip_tree"].astype(float), 3).ravel()
    e2["naip_tree_s"] = e["naip_tree_s"].reshape(shp)
    ev = {c: tuple(x.reshape(shp) for x in v) for c, v in strong_weak(e).items()}
    core = core_mask(a, l) & e2["ll_ok"]
    dens = shot_density(k, a, l, z, holes)
    d_fw = dist_to(np.isin(hand, ("fairway", "first_cut")))
    w_edge = np.exp(-d_fw / EDGE_SCALE)
    comps = []
    for kind, cls, m, dist in classify_cells(hand, ev, core):
        for cp in components(kind, cls, m, dist, a, l, dens, w_edge):
            cp["d_fw_min"] = float(d_fw[cp["mask"]].min())
            cp["hole"] = str(k)
            cp["evidence"] = evidence_summary(cp, e2)
            pm = patch_mask(cp, hand, ev)
            cp["patch"] = (patch_lie(cp), mask_polygon(h, pm, a, l))
            cp["patch_cells"] = int(pm.sum())
            cp["what"] = describe(cp)
            cp["bbox_px"] = _bbox_px(h, cp["mask"], a, l)
            comps.append(cp)
    ctx = dict(a=a, l=l, px=px, hand=hand, e=e2, ev=ev, dens=dens, core=core)
    return comps, ctx


def _bbox_px(h, m, a, l):
    ii, jj = np.nonzero(m)
    q = to_px(h, a[ii], l[jj])
    return [float(q[:, 0].min()), float(q[:, 1].min()), float(q[:, 0].max()), float(q[:, 1].max())]


def side(lat):
    return "R" if lat > 0 else "L"


def run(holes_sel=None, n=3000, holes=None):
    central_model()
    holes = holes if holes is not None else course.HOLES
    t.HOLES = holes
    E = Evidence()
    z = common_z(n)
    allc, ctxs = [], {}
    for k in holes:
        if holes_sel and str(k) not in holes_sel:
            continue
        comps, ctx = analyse_hole(k, E, z, holes)
        allc += comps
        ctxs[str(k)] = ctx
        print(f"{str(k):>3}: {len(comps)} components, top score "
              f"{max([c['score'] for c in comps], default=0):.4f}", flush=True)
    allc.sort(key=lambda c: -c["score"])
    for i, c in enumerate(allc):
        c["id"] = f"{c['hole']}-{c['kind'][0]}{c['cls'][:3]}-{int(c['centre'][0])}{side(c['centre'][1])}{abs(int(c['centre'][1]))}"
        c["rank"] = i + 1
    return allc, ctxs, E


def duplicate_keys(src=None, name="AUDIT_FIXES"):
    """Keys that appear more than once in the `name = {...}` dict literal of course.py (a later
    duplicate silently replaces the earlier entry's zones)."""
    import ast
    import collections
    src = src if src is not None else open(os.path.join(SH, "course.py")).read()
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name and isinstance(node.value, ast.Dict)):
            keys = [ast.literal_eval(k) for k in node.value.keys if k is not None]
            return [k for k, c in collections.Counter(keys).items() if c > 1]
    return []


def write_outputs(allc, out=HERE):
    rows = [{kk: v for kk, v in c.items() if kk != "mask"} for c in allc]
    json.dump(dict(doc=__doc__.split("\n\n")[0], tol_yd=TOL, along=ALONG, half=HALF, findings=rows),
              open(os.path.join(out, "disagree.json"), "w"), indent=1, default=float)
    md = ["# Landing-zone disagreements: hand map vs independent evidence", "",
          f"Generated by `python3 spirit_hollow/qa_landing/disagree.py`. Corridor {ALONG[0]:.0f}-{ALONG[1]:.0f} yds, "
          f"+/-{HALF:.0f} yds; tolerance {TOL:.0f} yds of edge position. Score = share of simulated tee shots "
          "(pick 2/3 + runner-up 1/3) in the disputed cells x edge weight exp(-d/12), d = yds from the "
          "hand fairway / first cut. Evidence columns: mean over the disputed cells (lidar = canopy > 2.5 m; "
          "lay = vision_any layers; v2 = vision2 LOHO probability).", ""]
    dup = duplicate_keys()
    if dup:
        md += [f"**WARNING: course.py AUDIT_FIXES has duplicate keys {dup}: the earlier entries for these holes "
               "are silently dropped (a dict literal keeps the last one). Merge them.**", ""]
    md += [
          "| # | id | reviewed | hole | kind | what | along | lat | edge shift med/max | d from fw | shots % | score | lidar | naip canopy | lay nat | v2 trees/nat/water/sand | osm w/b |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    reviewed = {}
    try:
        for fid, f in load_proposed().PROPOSED.items():
            for i in f.get("ids", []):
                reviewed[i] = f"{fid}: {f['verdict']}"
    except Exception:                                          # noqa: BLE001 (no review file yet)
        pass
    for c in rows[:60]:
        ev = c["evidence"]
        md.append(f"| {c['rank']} | {c['id']} | {reviewed.get(c['id'], '')} | {c['hole']} | {c['kind']} | {c['what']} | "
                  f"{c['along'][0]:.0f}-{c['along'][1]:.0f} | {c['lat'][0]:+.0f}..{c['lat'][1]:+.0f} | "
                  f"{c['edge_shift_med']:.0f}/{c['edge_shift_max']:.0f} | {c['d_fw_min']:.0f} | "
                  f"{100 * c['share']:.2f} | {1000 * c['score']:.2f} | {ev['lidar_trees']:.2f} | {ev['naip_tree_s']:.2f} | {ev['lay_native']:.2f} | "
                  f"{ev['v2_trees']:.2f}/{ev['v2_native']:.2f}/{ev['v2_water']:.2f}/{ev['v2_sand']:.2f} | "
                  f"{ev['osm_water']:.2f}/{ev['osm_bunker']:.2f} |")
    open(os.path.join(out, "disagree.md"), "w").write("\n".join(md) + "\n")


# ----------------------------------------------------------------------------- crops
LIE_COL = dict(fairway="#00ff66", first_cut="#b6ff00", recovery="#ff00ff", water="#00b7ff", sand="#ffffff",
               native="#ffae00", rough="#bbbbbb", ob="#ff0000")


def render_crops(allc, ctxs, E, top=20, out=os.path.join(HERE, "crops"), holes=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.image import imread
    import geo_zones as GZ
    import render as R
    os.makedirs(out, exist_ok=True)
    img = R.Imagery(NAIP_DIR)
    naip_cache = {}
    for c in allc[:top]:
        k = _key(c["hole"])
        h = (holes if holes is not None else course.HOLES)[k]
        g = E.G[k]
        if k not in naip_cache:
            naip_cache[k] = GZ.naip_in_shot(g, img)
        shot = imread(os.path.join(SH, "screenshots_clean", h["image"]))
        x0, y0, x1, y1 = c["bbox_px"]
        ppy = t.hole_frame(h)[3]
        padp = 30 * ppy
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        half = max((x1 - x0) / 2 + padp, (y1 - y0) / 2 + padp, 45 * ppy)
        X0, X1, Y0, Y1 = cx - half, cx + half, cy - half, cy + half
        # layer image sampled per screenshot px over the crop
        xs = np.arange(int(max(X0, 0)), int(min(X1, 920)))
        ys = np.arange(int(max(Y0, 0)), int(min(Y1, 2000)))
        XX, YY = np.meshgrid(xs + 0.5, ys + 0.5)
        pts = np.c_[XX.ravel(), YY.ravel()]
        ll = g.px_to_ll(pts)
        L, _ = E.layers.sample(ll, 0)
        hv, okh = (E.hag.sample(ll, 0, fill=255) if E.hag else (np.zeros(len(pts)), np.zeros(len(pts), bool)))
        hm = np.where((hv == 255) | ~okh, 0, hv * 0.25).reshape(XX.shape)
        lay = np.zeros(XX.shape + (3,))
        lay[..., :] = np.clip(hm / 15.0, 0, 1)[..., None] * np.array([0.2, 0.9, 0.2])   # canopy height green
        L = L.reshape(XX.shape)
        lay[L == 1] = [0.95, 0.65, 0.1]
        lay[L == 3] = [0.1, 0.5, 1.0]
        lay[(L == 2) & (hm < 2.5)] = [0.1, 0.5, 0.1]
        ext = (xs[0], xs[-1] + 1, ys[-1] + 1, ys[0])
        P = E.v2(c["hole"])
        fig, axs = plt.subplots(2, 3, figsize=(18, 12.5))
        axs = axs.ravel()
        axs[5].axis("off")
        axs[0].imshow(shot, extent=(0, 920, 2000, 0))
        axs[0].set_title("screenshot (winter, oblique)", fontsize=9)
        axs[1].imshow(naip_cache[k], extent=(0, 920, 2000, 0))
        axs[1].set_title("NAIP 2023 (summer, straight down)", fontsize=9)
        axs[2].imshow(lay, extent=ext)
        axs[2].set_title("lidar canopy (green=height, >2.5 m), orange=long grass layer, blue=water", fontsize=8)
        osm = E.osm
        for ring in osm["water"] + osm["bunker"]:
            q = g.ll_to_px(np.asarray(ring, float))
            for ax in axs[1:3]:
                ax.plot(q[:, 0], q[:, 1], color="cyan", lw=1.0, ls="--")
        if P is not None:
            rgb = np.zeros(P.shape[:2] + (3,))
            cols = np.array([[0, .8, .3], [.75, .75, .75], [.9, 0, .9], [1, .65, 0], [0, .6, 1], [1, 1, 1]])
            rgb = P @ cols
            axs[3].imshow(np.clip(rgb, 0, 1), extent=(0, 920, 2000, 0))
            axs[3].axhline(V2_TOP, color="k"); axs[3].axhline(V2_BOTTOM, color="k")
        axs[3].set_title("vision2 LOHO (magenta trees, orange native, blue water, white sand)", fontsize=8)
        axs[4].imshow(shot, extent=(0, 920, 2000, 0))
        for nm, poly in h["zones"]:
            Q = np.array(list(poly) + [poly[0]], float)
            axs[4].fill(Q[:, 0], Q[:, 1], color=LIE_COL.get(nm, "k"), alpha=0.25)
            axs[4].plot(Q[:, 0], Q[:, 1], color=LIE_COL.get(nm, "k"), lw=1.0)
        axs[4].set_title("hand map (magenta trees, orange long grass, lime 1st cut)", fontsize=8)
        ctx = ctxs[c["hole"]]
        a, l = ctx["a"], ctx["l"]
        mpx = to_px(h, *np.meshgrid(a, l, indexing="ij"))
        lie, poly = c["patch"]
        for ax in axs[:5]:
            ax.contour(mpx[..., 0], mpx[..., 1], c["mask"].astype(float), levels=[0.5], colors="red", linewidths=1.6)
            if poly:
                Q = np.array(list(poly) + [poly[0]], float)
                ax.plot(Q[:, 0], Q[:, 1], color="yellow", lw=1.0, ls=":")
            for d in range(190, 341, 10):
                q = to_px(h, np.array([d, d]), np.array([-HALF, HALF]))
                ax.plot(q[:, 0], q[:, 1], color="w", lw=0.5, alpha=0.6)
                tp = to_px(h, d, c["centre"][1] - 18)
                ax.text(tp[0], tp[1], f"{d}", color="yellow", fontsize=8, clip_on=True)
            for lat in (-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50):
                tq = to_px(h, c["centre"][0] - 12, lat)
                ax.text(tq[0], tq[1], f"{lat:+d}", color="yellow", fontsize=8, clip_on=True)
                q = to_px(h, np.array([ALONG[0], ALONG[1]]), np.array([lat, lat]))
                ax.plot(q[:, 0], q[:, 1], color="y" if lat == 0 else "w", lw=0.7 if lat == 0 else 0.3, alpha=0.7)
            ax.set_xlim(X0, X1); ax.set_ylim(Y1, Y0); ax.set_xticks([]); ax.set_yticks([])
        fig.suptitle(f"#{c['rank']} {c['id']}  hole {c['hole']}: {c['what']}  along {c['along'][0]:.0f}-{c['along'][1]:.0f}, "
                     f"lat {c['lat'][0]:+.0f}..{c['lat'][1]:+.0f}, edge shift {c['edge_shift_med']:.0f}/{c['edge_shift_max']:.0f} yds, "
                     f"shots {100 * c['share']:.2f}%  (red = disputed cells, yellow dotted = auto patch -> {lie})", fontsize=10)
        fig.tight_layout()
        fn = os.path.join(out, f"{c['rank']:02d}_{c['hole']}.png")
        fig.savefig(fn, dpi=70)
        plt.close(fig)
        c["crop"] = os.path.relpath(fn, ROOT)
        print("crop", fn, flush=True)


# ----------------------------------------------------------------------------- impact
def course_with_patches(patches):
    """A fresh course module with `patches` (AUDIT_FIXES format) appended to AUDIT_FIXES before
    they are applied, so first_cut bands are rebuilt exactly as course.py would."""
    path = os.path.join(SH, "course.py")
    src = open(path).read()
    anchor = "for _k, _extra in AUDIT_FIXES.items():"
    assert src.count(anchor) == 1, "course.py AUDIT_FIXES loop not found"
    inj = ("for _pk, _pv in __PATCHES__.items():\n"
           "    AUDIT_FIXES[_pk] = list(AUDIT_FIXES.get(_pk, [])) + list(_pv)\n")
    src = src.replace(anchor, inj + anchor, 1)
    mod = types.ModuleType("course_patched")
    mod.__file__ = path
    mod.__dict__["__PATCHES__"] = copy.deepcopy(patches)
    exec(compile(src, path, "exec"), mod.__dict__)
    return mod


def load_proposed(path=os.path.join(HERE, "proposed_patches.py")):
    import importlib.util
    spec = importlib.util.spec_from_file_location("proposed_patches", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ev_table(holes, k, z):
    """{club: (best aim, EV)} under the central model with common random numbers z."""
    saved = t.HOLES
    t.HOLES = holes
    try:
        out = {}
        clubs = list(t.CLUBS) + (list(t.IRONS) if holes[k].get("irons") else [])
        for c in clubs:
            aims = np.arange(-25, 25.01, 2.5) if c not in t.IRONS else np.arange(-25, 45.01, 2.5)
            evs = np.array([t.simulate(k, c, a, z=z)[3].mean() for a in aims])
            i = int(np.argmin(evs))
            out[c] = (float(aims[i]), float(evs[i]))
        return out
    finally:
        t.HOLES = saved


def impact(n=3000, out=HERE):
    PPm = load_proposed()
    central_model()
    z = common_z(n)
    res = {}
    base_holes = course.HOLES
    for fid, f in PPm.PROPOSED.items():
        if f.get("verdict") != "map wrong" or not f.get("patches"):
            continue
        k = _key(f["hole"])
        mod = course_with_patches({k: f["patches"]})
        res[fid] = _compare(k, base_holes, mod.HOLES, z)
        print(fid, res[fid]["summary"], flush=True)
    for k, plist in PPm.PATCHES.items():
        if sum(1 for f in PPm.PROPOSED.values() if _key(f["hole"]) == k and f.get("verdict") == "map wrong") > 1:
            mod = course_with_patches({k: plist})
            res[f"{k}-all"] = _compare(k, base_holes, mod.HOLES, z)
            print(f"{k}-all", res[f"{k}-all"]["summary"], flush=True)
    json.dump(res, open(os.path.join(out, "impact.json"), "w"), indent=1)
    md = ["# Decision impact of the proposed patches", "",
          f"Central prior (driver width 70, 2w/4w 0.94/0.85 of it, depth x1.25, roll 0.975, rough roll 0.325, "
          f"trees 0.8, lost 0.5, mishit 0.15), {n} common-random-number swings, aims -25..+25 by 2.5 "
          "(irons to +45). EV = expected strokes for the hole at each club's best aim.", "",
          "| finding | hole | club | aim before -> after | EV before -> after (change) | pick before -> after |",
          "|---|---|---|---|---|---|"]
    for fid, r in res.items():
        for c in r["before"]:
            ab, eb = r["before"][c]
            aa, ea = r["after"][c]
            md.append(f"| {fid} | {r['hole']} | {c} | {ab:+.1f} -> {aa:+.1f} | {eb:.3f} -> {ea:.3f} ({ea - eb:+.3f}) | "
                      f"{r['pick_before']} -> {r['pick_after']} |")
    open(os.path.join(out, "impact.md"), "w").write("\n".join(md) + "\n")
    return res


def _compare(k, before_holes, after_holes, z):
    b = ev_table(before_holes, k, z)
    a = ev_table(after_holes, k, z)
    pb = min(b, key=lambda c: b[c][1])
    pa = min(a, key=lambda c: a[c][1])
    s = f"pick {pb} {b[pb][0]:+.1f} ({b[pb][1]:.3f}) -> {pa} {a[pa][0]:+.1f} ({a[pa][1]:.3f})"
    return dict(hole=str(k), before=b, after=a, pick_before=pb, pick_after=pa,
                margin_before=float(sorted(v[1] for v in b.values())[1] - b[pb][1]),
                margin_after=float(sorted(v[1] for v in a.values())[1] - a[pa][1]), summary=s)


def zoom(k, box, out=None, zones=True):
    """Full-resolution screenshot | NAIP pulled into the screenshot grid for a px box (x0 y0 x1 y1),
    with the hand zones outlined: for checking an edge by eye."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.image import imread
    import geo_zones as GZ
    import render as R
    k = _key(k)
    h = course.HOLES[k]
    G = GZ.transforms_from_json(json.load(open(HAND_LL)))
    naip = GZ.naip_in_shot(G[k], R.Imagery(NAIP_DIR))
    shot = imread(os.path.join(SH, "screenshots_clean", h["image"]))
    x0, y0, x1, y1 = box
    fig, axs = plt.subplots(1, 2, figsize=(16, 8.5 * (y1 - y0) / max(x1 - x0, 1)))
    for ax, im in zip(axs, (shot, naip)):
        ax.imshow(im, extent=(0, 920, 2000, 0))
        if zones:
            for nm, poly in h["zones"]:
                Q = np.array(list(poly) + [poly[0]], float)
                ax.plot(Q[:, 0], Q[:, 1], color=LIE_COL.get(nm, "k"), lw=1.0)
        for d in range(150, 400, 10):
            q = to_px(h, np.array([d, d]), np.array([-70, 70]))
            ax.plot(q[:, 0], q[:, 1], color="w", lw=0.4, alpha=0.5)
            for lat in range(-60, 61, 10):
                p = to_px(h, d, lat)
                if x0 < p[0] < x1 and y0 < p[1] < y1 and d % 20 == 0:
                    ax.text(p[0], p[1], f"{d}/{lat:+d}", color="yellow", fontsize=6, clip_on=True)
        ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
    fig.tight_layout()
    out = out or os.path.join(HERE, "crops", f"zoom_{k}_{int(x0)}_{int(y0)}.png")
    fig.savefig(out, dpi=80)
    plt.close(fig)
    print(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--holes", default="")
    ap.add_argument("--render", type=int, default=0)
    ap.add_argument("--impact", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--zoom", nargs=5, metavar=("HOLE", "X0", "Y0", "X1", "Y1"))
    ap.add_argument("--nozones", action="store_true")
    ap.add_argument("--patched", action="store_true", help="analyse the map with proposed_patches.py applied")
    args = ap.parse_args(argv)
    if args.zoom:
        zoom(args.zoom[0], [float(v) for v in args.zoom[1:]], zones=not args.nozones)
        return
    sel = [s.strip() for s in args.holes.split(",") if s.strip()]
    if args.all:
        args.render = args.render or 20
        args.impact = True
    if args.patched:                    # what would remain after applying proposed_patches.py
        holes = course_with_patches(load_proposed().PATCHES).HOLES
        allc, ctxs, E = run(sel, args.n, holes)
        out = os.path.join(HERE, "patched")
        os.makedirs(out, exist_ok=True)
        write_outputs(allc, out)
        if args.render:
            render_crops(allc, ctxs, E, args.render, os.path.join(out, "crops"), holes)
        print(open(os.path.join(out, "disagree.md")).read()[:6000])
        return
    allc, ctxs, E = run(sel, args.n)
    if args.render:
        render_crops(allc, ctxs, E, args.render)
    write_outputs(allc)
    print(open(os.path.join(HERE, "disagree.md")).read()[:6000])
    if args.impact:
        impact(args.n)


if __name__ == "__main__":
    main()
