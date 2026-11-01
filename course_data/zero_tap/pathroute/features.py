"""pathroute features: hole (tee -> green) and transition (green -> next tee) candidates of one Scene."""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.prepared import prep

HOLE_F = ["L", "cover", "fw_link", "fw_tee", "fw_green", "align", "el", "greens_x", "tees_x", "bld", "water",
          "rank_g", "rank_t", "near_g", "t_area"]
TRANS_F = ["d_eu", "d_path", "conn", "ratio", "rank_t", "rank_g", "d_club_t", "d_club_g", "behind"]
LMIN, LMAX = 60.0, 720.0


def _contains(geom, xs, ys):
    if geom is None:
        return np.zeros(len(xs), bool)
    return shapely.contains_xy(geom, xs, ys)


def hole_feats(sc):
    """-> (pairs [(ti, gi)], X [n, len(HOLE_F)])."""
    tc, gc = sc.tc, sc.gc
    D = np.hypot(tc[:, None, 0] - gc[None, :, 0], tc[:, None, 1] - gc[None, :, 1])
    fbuf = sc.fair_u.buffer(8) if sc.fair_u is not None else None
    if fbuf is not None:
        shapely.prepare(fbuf)
    bbuf = sc.bld_u.buffer(4) if sc.bld_u is not None else None
    if bbuf is not None:
        shapely.prepare(bbuf)
    wu = sc.water_u
    if wu is not None:
        shapely.prepare(wu)
    fws = sc.fairways
    fw_dt = np.array([[t["g"].distance(f) for f in fws] for t in sc.tees]) if fws else None
    fw_dg = np.array([[g["g"].distance(f) for f in fws] for g in sc.greens]) if fws else None
    gr = [g["r"] for g in sc.greens]
    pairs, X = [], []
    ok = (D >= LMIN) & (D <= LMAX)
    rank_g = np.argsort(np.argsort(np.where(ok, D, np.inf), axis=1), axis=1)
    rank_t = np.argsort(np.argsort(np.where(ok, D, np.inf), axis=0), axis=0)
    near_g = np.sort(D, axis=1)[:, 0]
    s = np.linspace(0.12, 0.88, 16)
    for ti, gi in zip(*np.nonzero(ok)):
        t, g = sc.tees[ti], sc.greens[gi]
        a, b = np.array(t["c"]), np.array(g["c"])
        L = D[ti, gi]
        u = (b - a) / L
        xs = a[0] + s * (b[0] - a[0])
        ys = a[1] + s * (b[1] - a[1])
        cover = float(_contains(fbuf, xs, ys).mean()) if fbuf is not None else 0.0
        bld = float(_contains(bbuf, xs, ys).mean()) if bbuf is not None else 0.0
        water = float(_contains(wu, xs, ys).mean()) if wu is not None else 0.0
        if fws:
            link = np.maximum(fw_dt[ti], np.maximum(0, fw_dg[gi]))
            k = int(np.argmin(link))
            fw_link, fw_tee, fw_green = float(link[k]), float(fw_dt[ti].min()), float(fw_dg[gi].min())
        else:
            fw_link = fw_tee = fw_green = 999.0
        # other greens / far tees the straight line runs over
        dg = np.abs((gc[:, 0] - a[0]) * u[1] - (gc[:, 1] - a[1]) * u[0]) - np.array(gr)
        along = (gc[:, 0] - a[0]) * u[0] + (gc[:, 1] - a[1]) * u[1]
        m = (dg < 10) & (along > 0.1 * L) & (along < L - 25)
        m[gi] = False
        greens_x = int(m.sum())
        dt = np.abs((tc[:, 0] - a[0]) * u[1] - (tc[:, 1] - a[1]) * u[0])
        alt = (tc[:, 0] - a[0]) * u[0] + (tc[:, 1] - a[1]) * u[1]
        tees_x = int(((dt < 10) & (alt > 150) & (alt < L - 30)).sum())
        align = abs(t["ax"][0] * u[0] + t["ax"][1] * u[1])
        pairs.append((int(ti), int(gi)))
        X.append([L, cover, fw_link, fw_tee, fw_green, align, t["el"], greens_x, tees_x, bld, water,
                  rank_g[ti, gi], rank_t[ti, gi], near_g[ti], t["area"]])
    return pairs, np.array(X, float).reshape(-1, len(HOLE_F))


def trans_feats(sc, dmax=650.0):
    """-> (pairs [(gi, ti)], X [n, len(TRANS_F)]) for green -> tee walks shorter than dmax (edge to edge)."""
    ng, nt = len(sc.greens), len(sc.tees)
    E = np.array([[g["g"].distance(t["g"]) for t in sc.tees] for g in sc.greens])
    P = sc.path_dist()
    cl = np.array(sc.club)
    dct = np.hypot(*(sc.tc - cl).T)
    dcg = np.hypot(*(sc.gc - cl).T)
    rank_t = np.argsort(np.argsort(E, axis=1), axis=1)
    rank_g = np.argsort(np.argsort(E, axis=0), axis=0)
    pairs, X = [], []
    for gi, ti in zip(*np.nonzero(E <= dmax)):
        conn = np.isfinite(P[gi, ti])
        dp = P[gi, ti] if conn else 2000.0
        # is the tee 'behind' the green (walks back toward where the hole came from)? proxy: tee closer to the
        # clubhouse than the green.
        behind = dct[ti] - dcg[gi]
        pairs.append((int(gi), int(ti)))
        X.append([E[gi, ti], dp, float(conn), dp / max(E[gi, ti], 20.0), rank_t[gi, ti], rank_g[gi, ti],
                  dct[ti], dcg[gi], behind])
    return pairs, np.array(X, float).reshape(-1, len(TRANS_F))


def club_feats(sc):
    cl = np.array(sc.club)
    dct = np.hypot(*(sc.tc - cl).T)
    dcg = np.hypot(*(sc.gc - cl).T)
    rt = np.argsort(np.argsort(dct))
    rg = np.argsort(np.argsort(dcg))
    return np.c_[dct, rt], np.c_[dcg, rg]
