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
ROUTER = os.environ.get("ROUTE_LEARN_ROUTER", "v2")          # the bench prep the tables are built on
VER = os.environ.get("ROUTE_LEARN_VER", "2ef0018e4_d0")         # bench scene version (detector commit _ probs variant)
LEARN = os.environ.get("ROUTE_LEARN_DIR") or (
    os.path.join(CACHE, "val", "learn", ROUTER + ("" if VER == "2ef0018e4_d0" else "_" + VER))
    if os.environ.get("ROUTE_SPLIT_TEES", "1") == "0" else os.path.join(CACHE, "val", "learn", "split"))
MODEL = os.path.join(HERE, "route_learn_model.pkl")
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


def augment_scene(scene, P, min_area=AUG_AREA[0], max_area=AUG_AREA[1]):
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
    sc = dict(scene, greens=list(scene.get("greens") or []) + out)
    return sc, len(out)


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
    ta = np.full((len(Tc), 3), np.nan) if ta is None else ta
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
                   float(g.get("kind") == "map"), float(M.sample(xy[None], "turf")[0])])
    ta = []
    for t in co["T"]:
        o = ts.get(t["id"].split("/")[0]) or {}
        ta.append([float(o.get("p", np.nan) or np.nan), float(len(t["pts"])), float(o.get("length_m") or np.nan)])
    return np.asarray(ga, float).reshape(-1, 4), np.asarray(ta, float).reshape(-1, 3)


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
    scene, _ = augment_scene(scene, RB.bench_probs(slug, ver.split("_", 1)[1]))
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
        scene, _ = augment_scene(scene, RB.bench_probs(slug, ver.split("_", 1)[1]))
    Y = S.card_sets(x["card"], int(x["n"]))
    d["_Y"] = Y
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


def _X(t, kind):
    if kind == "h":
        return np.c_[t["hx"], t["hx2"]]
    if kind in ("s", "e"):
        return t[kind + "x"]
    return np.c_[t["wx"], t["wx2"]]


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
    pickle.dump(dict(models=ms, XF=XF, WXF=WXF, n_train=len(ts)), open(MODEL, "wb"))
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
    d["_gattr"], d["_tattr"] = obj_attrs(d, scene, M)
    t = dict(hx=d["hx"], hx2=pair_features(d, M), wx=d["wx"], wx2=walk_features(d, M), sx=loop_x(d, "start"),
             ex=loop_x(d, "end"))
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
    elif a.cmd == "prac":
        cmd_prac(a.out)
