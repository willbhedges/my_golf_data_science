"""pathroute v2 extra features (on top of pathroute/features.py), all card-blind and geometry-only.

- hole candidates (tee t -> green g, same order as features.hole_feats):
  fairway *components* (fairways unioned when they touch) linking both ends, how shared that component is,
  landing-zone / approach-zone geometry of the linking fairway (dogleg-aware tee-axis alignment, approach angle),
  corridor contents (other greens / tees inside the tee-green ellipse), green / tee practice cues
  (driving range, clubhouse, fairway reach, tees around a green).
- tee pairs (a, b) within TEE_PAIR_D yds: features for "same hole" (tee complex) grouping.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Point
from shapely.ops import unary_union

HOLE2_F = ["c_link", "c_tee", "c_green", "c_ng", "c_nt", "c_area", "ell_frac", "land_align", "land_lat",
           "app_cos", "ell_greens", "ell_tees", "g_area", "g_fw", "g_club", "g_range", "g_ntees", "t_fw", "t_club",
           "t_range", "t_inside", "g_inside", "t_ntees40", "path_lat"]
TPAIR_F = ["d", "e", "al_a", "al_b", "ax_ab", "area_r", "lat", "ng_a", "ng_b", "same_ng", "fw_a", "fw_b",
           "t_inside_same"]
TEE_PAIR_D = 130.0


def _grid_points(poly, step=12.0):
    minx, miny, maxx, maxy = poly.bounds
    xs = np.arange(minx + step / 2, maxx, step)
    ys = np.arange(miny + step / 2, maxy, step)
    if not len(xs) or not len(ys):
        c = poly.representative_point()
        return np.array([[c.x, c.y]])
    X, Y = np.meshgrid(xs, ys)
    X, Y = X.ravel(), Y.ravel()
    m = shapely.contains_xy(poly, X, Y)
    if not m.any():
        c = poly.representative_point()
        return np.array([[c.x, c.y]])
    return np.c_[X[m], Y[m]]


def _flag(f, key="inside_course"):
    v = f.get(key)
    return 1.0 if v in (True, "yes", "true", 1) else (0.0 if v in (False, "no", "false", 0) else 0.5)


def hole2_feats(sc, pairs, props=None):
    """-> X2 [len(pairs), len(HOLE2_F)]."""
    tc, gc = sc.tc, sc.gc
    nt, ng = len(tc), len(gc)
    tg = [t["g"] for t in sc.tees]
    gg = [g["g"] for g in sc.greens]
    comps = []
    if sc.fairways:
        u = unary_union([f.buffer(5) for f in sc.fairways])
        comps = list(u.geoms) if u.geom_type == "MultiPolygon" else [u]
        comps = [c for c in comps if c.area > 200]
    nc = len(comps)
    if nc:
        dT = shapely.distance(np.array(tg, dtype=object)[:, None], np.array(comps, dtype=object)[None, :])
        dG = shapely.distance(np.array(gg, dtype=object)[:, None], np.array(comps, dtype=object)[None, :])
        cpts = [_grid_points(c) for c in comps]
        c_ng = (dG < 15).sum(0)
        c_nt = (dT < 15).sum(0)
        carea = np.array([c.area for c in comps])
        tfw, gfw = dT.min(1), dG.min(1)
    else:
        tfw = np.full(nt, 999.0)
        gfw = np.full(ng, 999.0)
    club = np.array(sc.club)
    g_club = np.hypot(*(gc - club).T)
    t_club = np.hypot(*(tc - club).T)
    if sc.range_:
        ru = unary_union(sc.range_).buffer(0)
        g_range = shapely.distance(np.array(gg, dtype=object), ru)
        t_range = shapely.distance(np.array(tg, dtype=object), ru)
    else:
        g_range = np.full(ng, 999.0)
        t_range = np.full(nt, 999.0)
    DTG = np.hypot(tc[:, None, 0] - gc[None, :, 0], tc[:, None, 1] - gc[None, :, 1])
    g_ntees = ((DTG > 60) & (DTG < 600)).sum(0)
    DTT = np.hypot(tc[:, None, 0] - tc[None, :, 0], tc[:, None, 1] - tc[None, :, 1])
    t_ntees40 = (DTT < 40).sum(1) - 1
    g_area = np.array([g["g"].area for g in sc.greens])
    tin = np.array([_flag(p) for p in (props or {}).get("tees", [{}] * nt)]) if props else np.full(nt, 0.5)
    gin = np.array([_flag(p) for p in (props or {}).get("greens", [{}] * ng)]) if props else np.full(ng, 0.5)
    X = []
    for ti, gi in pairs:
        a, b = tc[ti], gc[gi]
        L = max(DTG[ti, gi], 1.0)
        u = (b - a) / L
        ax = np.array(sc.tees[ti]["ax"])
        if nc:
            link = np.maximum(dT[ti], dG[gi])
            k = int(np.argmin(link))
            P = cpts[k]
            s = np.hypot(*(P - a).T) + np.hypot(*(P - b).T)
            inell = s <= L + 60
            ell_frac = float(inell.mean())
            Q = P[inell] if inell.any() else P
            da = np.hypot(*(Q - a).T)
            land = Q[(da > 140) & (da < 290)]
            if len(land):
                lc = land.mean(0)
                v = lc - a
                land_align = abs(float(ax @ v) / max(np.hypot(*v), 1.0))
                land_lat = abs(float(v[0] * u[1] - v[1] * u[0])) / L
            else:
                land_align, land_lat = abs(float(ax @ u)), 0.0
            db = np.hypot(*(Q - b).T)
            appz = Q[(db > 30) & (db < 140)]
            if len(appz):
                w = b - appz.mean(0)
                app_cos = float(w @ u) / max(np.hypot(*w), 1.0)
            else:
                app_cos = 1.0
            # the hole's "path": tee -> landing centroid -> green: lateral offset of the elbow
            path_lat = land_lat
            row = [float(link[k]), float(dT[ti, k]), float(dG[gi, k]), float(c_ng[k]), float(c_nt[k]),
                   float(carea[k]), ell_frac, land_align, land_lat, app_cos]
        else:
            path_lat = 0.0
            row = [999.0, 999.0, 999.0, 0.0, 0.0, 0.0, 0.0, abs(float(ax @ u)), 0.0, 1.0]
        sg = np.hypot(*(gc - a).T) + np.hypot(*(gc - b).T)
        eg = sg <= L + 40
        eg[gi] = False
        st = np.hypot(*(tc - a).T) + np.hypot(*(tc - b).T)
        et = (st <= L + 40) & (np.hypot(*(tc - a).T) > 60) & (np.hypot(*(tc - b).T) > 40)
        row += [float(eg.sum()), float(et.sum()), g_area[gi], gfw[gi], g_club[gi], g_range[gi], float(g_ntees[gi]),
                tfw[ti], t_club[ti], t_range[ti], tin[ti], gin[gi], float(t_ntees40[ti]), path_lat]
        X.append(row)
    return np.array(X, float).reshape(-1, len(HOLE2_F))


def tee_pairs(sc, props=None):
    """-> (pairs [(a, b)] a < b, X [n, len(TPAIR_F)]) for tee boxes within TEE_PAIR_D yds."""
    tc, gc = sc.tc, sc.gc
    nt = len(tc)
    D = np.hypot(tc[:, None, 0] - tc[None, :, 0], tc[:, None, 1] - tc[None, :, 1])
    DG = np.hypot(tc[:, None, 0] - gc[None, :, 0], tc[:, None, 1] - gc[None, :, 1])
    DG = np.where(DG < 60, np.inf, DG)
    ng_ = np.argmin(DG, 1) if gc.shape[0] else np.zeros(nt, int)
    tg = [t["g"] for t in sc.tees]
    if sc.fairways:
        fu = unary_union(sc.fairways)
        tfw = shapely.distance(np.array(tg, dtype=object), fu)
    else:
        tfw = np.full(nt, 999.0)
    tin = np.array([_flag(p) for p in props["tees"]]) if props else np.full(nt, 0.5)
    pairs, X = [], []
    for a, b in zip(*np.nonzero(np.triu(D < TEE_PAIR_D, 1))):
        ta, tb = sc.tees[a], sc.tees[b]
        v = tc[b] - tc[a]
        d = max(D[a, b], 1e-3)
        u = v / d
        axa, axb = np.array(ta["ax"]), np.array(tb["ax"])
        e = ta["g"].distance(tb["g"])
        # lateral offset of b from a's axis line
        lat = abs(float(v[0] * axa[1] - v[1] * axa[0]))
        pairs.append((int(a), int(b)))
        X.append([d, e, abs(float(axa @ u)), abs(float(axb @ u)), abs(float(axa @ axb)),
                  min(ta["area"], tb["area"]) / max(ta["area"], tb["area"], 1.0), lat,
                  DG[a, ng_[a]], DG[b, ng_[b]], float(ng_[a] == ng_[b]), tfw[a], tfw[b], float(tin[a] == tin[b])])
    return pairs, np.array(X, float).reshape(-1, len(TPAIR_F))
