"""joint routing: pair geometry (play length with doglegs, hole / walk / loop features) for a Course (cands.py)."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point

HOLE_MIN, HOLE_MAX = 55.0, 720.0          # straight tee -> green distance of a candidate hole, yd
WALK_MAX = 900.0
HF = ["d", "dfar", "dnear", "nbox", "play", "dog", "cover", "cover_mid", "fair_tee", "fair_green", "over_green",
      "over_tee", "axis", "tp", "gp", "rk_t", "rk_g", "rk_t_len", "club_t", "club_g", "ngreen_d", "back_green"]
WF = ["d", "rk_t", "rk_g", "ratio2", "pnext", "tp", "gp", "club_t", "club_g", "on_fair", "self_d", "n150"]


def play_length(co, p, q, S=None):
    """Tee point p -> green centre q play length in yards: straight, or through the centreline of the fairway that
    leads to the green when that is longer (a dogleg). -> (length, fairway index or -1)."""
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    S = float(np.hypot(*(q - p))) if S is None else S
    if S < 150 or not co["fair"]:
        return S, -1
    u = (q - p) / S
    best = (S, -1, 1e9)
    qp = Point(q[0], q[1])
    for fi, f in enumerate(co["fair"]):
        cl = f["cl"]
        s = (cl - p) @ u / S
        keep = (s > 0.12) & (s < 0.93)
        if not keep.any():
            continue
        lat = np.abs((cl - p) @ np.array([-u[1], u[0]]))
        if lat[keep].max() > 0.45 * S:
            continue
        dg = f["poly"].distance(qp)
        if dg > 75:
            continue
        pts = cl[keep][np.argsort(s[keep])]
        path = np.vstack([p, pts, q])
        L = float(np.sum(np.hypot(*np.diff(path, axis=0).T)))
        if L > 1.25 * S:
            continue
        if dg < best[2] - 5 or (abs(dg - best[2]) <= 5 and L < best[0]):
            best = (max(L, S), fi, dg)
    return best[0], best[1]


def geometry(co):
    """Pairwise geometry tables for a Course. D[t, g] centre distance, Dfar / Dnear over boxes, P play length from
    the far box, Pbox[t][g] = play length from every box."""
    G, T = co["G"], co["T"]
    ng, nt = len(G), len(T)
    Tc = np.array([t["c"] for t in T]).reshape(-1, 2)
    D = np.hypot(Tc[:, None, 0] - G[None, :, 0], Tc[:, None, 1] - G[None, :, 1])
    Dfar = np.zeros((nt, ng))
    Dnear = np.zeros((nt, ng))
    P = np.zeros((nt, ng))
    Pbox = [[None] * ng for _ in range(nt)]
    ok = np.zeros((nt, ng), bool)
    for ti, t in enumerate(T):
        db = np.hypot(t["pts"][:, None, 0] - G[None, :, 0], t["pts"][:, None, 1] - G[None, :, 1])   # [box, g]
        Dfar[ti] = db.max(0)
        Dnear[ti] = db.min(0)
        for gi in range(ng):
            if not (HOLE_MIN <= Dfar[ti, gi] and Dnear[ti, gi] <= HOLE_MAX and D[ti, gi] >= 45):
                P[ti, gi] = Dfar[ti, gi]
                continue
            ok[ti, gi] = True
            b = int(np.argmax(db[:, gi]))
            L, fi = play_length(co, t["pts"][b], G[gi], db[b, gi])
            P[ti, gi] = L
            extra = L - db[b, gi]
            # the other boxes of the complex play the same dogleg: same extra, scaled by their distance
            Pbox[ti][gi] = db[:, gi] + extra * np.clip(db[:, gi] / max(db[b, gi], 1.0), 0, 1)
    return dict(D=D, Dfar=Dfar, Dnear=Dnear, P=P, Pbox=Pbox, ok=ok, Tc=Tc)


def _cover(co, a, b):
    """Share of the segment a-b on fairway: whole, middle (25-85 %), and fairway within 60 yd of tee / 40 of green."""
    fu = co["fair_u"]
    if fu is None:
        return 0.0, 0.0, 0.0, 0.0
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ln = LineString([a, b])
    L = ln.length or 1.0
    m0, m1 = a + 0.25 * (b - a), a + 0.85 * (b - a)
    mid = LineString([m0, m1])
    try:
        c = ln.intersection(fu).length / L
        cm = mid.intersection(fu).length / (mid.length or 1.0)
    except Exception:
        c = cm = 0.0
    return c, cm, float(fu.distance(Point(a[0], a[1])) < 110), float(fu.distance(Point(b[0], b[1])) < 45)


def hole_features(co, geo):
    """Rows for every plausible (tee complex, green) pair. -> (pairs [n, 2] (t, g), X [n, len(HF)])."""
    G, T = co["G"], co["T"]
    D, Tc = geo["D"], geo["Tc"]
    club = co.get("club")
    ct = np.hypot(Tc[:, 0] - club[0], Tc[:, 1] - club[1]) if club is not None else np.full(len(T), np.nan)
    cg = np.hypot(G[:, 0] - club[0], G[:, 1] - club[1]) if club is not None else np.full(len(G), np.nan)
    Dm = np.where(geo["ok"], D, np.inf)
    rk_t = np.argsort(np.argsort(Dm, axis=0), axis=0)        # rank of the tee among the green's tees
    rk_g = np.argsort(np.argsort(Dm, axis=1), axis=1)        # rank of the green among the tee's greens
    Dgg = np.hypot(G[:, None, 0] - G[None, :, 0], G[:, None, 1] - G[None, :, 1])
    pairs, X = [], []
    for ti, t in enumerate(T):
        for gi in range(len(G)):
            if not geo["ok"][ti, gi]:
                continue
            d = D[ti, gi]
            a, b = Tc[ti], G[gi]
            u = (b - a) / max(d, 1.0)
            c, cm, ft, fg = _cover(co, a, b)
            # other greens / tees under the line (a hole does not play over another green or tee)
            og = 0
            for k in range(len(G)):
                if k == gi:
                    continue
                s = (G[k] - a) @ u
                if 30 < s < d - 30 and abs((G[k] - a) @ np.array([-u[1], u[0]])) < 18:
                    og += 1
            ot = 0
            for k in range(len(T)):
                if k == ti:
                    continue
                s = (Tc[k] - a) @ u
                if 70 < s < d - 40 and abs((Tc[k] - a) @ np.array([-u[1], u[0]])) < 12:
                    ot += 1
            ax = np.nan
            if t.get("ax") is not None:
                ax = abs(t["ax"][0] * u[0] + t["ax"][1] * u[1])
            # a green close behind the tee (the previous hole's green) supports the tee
            sb = (G - a) @ u
            lb = np.abs((G - a) @ np.array([-u[1], u[0]]))
            back = float(np.min(np.where((sb < 20) & (np.arange(len(G)) != gi), np.hypot(sb, lb), 999.0)))
            near_g = np.sort(Dgg[gi])[1] if len(G) > 1 else 999.0
            # rank of this tee among the green's tees whose length is a plausible hole (>= 95 yd)
            pl = np.where(geo["ok"][:, gi] & (D[:, gi] >= 95), D[:, gi], np.inf)
            rkl = float(np.sum(pl < d))
            pairs.append((ti, gi))
            X.append([d, geo["Dfar"][ti, gi], geo["Dnear"][ti, gi], len(t["pts"]), geo["P"][ti, gi],
                      geo["P"][ti, gi] - geo["Dfar"][ti, gi], c, cm, ft, fg, og, ot, ax, t["p"], co["Gp"][gi],
                      rk_t[ti, gi], rk_g[ti, gi], rkl, ct[ti], cg[gi], near_g, back])
    return np.array(pairs, int).reshape(-1, 2), np.array(X, float).reshape(-1, len(HF))


def walk_features(co, geo):
    """Rows for every (green, tee complex) pair within WALK_MAX: the walk from a green to the next tee.
    Distance is from the green's edge to the nearest box of the complex."""
    G, T = co["G"], co["T"]
    Tc = geo["Tc"]
    W = np.zeros((len(G), len(T)))
    for ti, t in enumerate(T):
        db = np.hypot(t["pts"][:, None, 0] - G[None, :, 0], t["pts"][:, None, 1] - G[None, :, 1]).min(0)
        dc = np.hypot(Tc[ti, 0] - G[:, 0], Tc[ti, 1] - G[:, 1])
        W[:, ti] = np.maximum(np.minimum(db, dc) - co["Gr"], 0.0)
    club = co.get("club")
    ct = np.hypot(Tc[:, 0] - club[0], Tc[:, 1] - club[1]) if club is not None else np.full(len(T), np.nan)
    cg = np.hypot(G[:, 0] - club[0], G[:, 1] - club[1]) if club is not None else np.full(len(G), np.nan)
    rk_t = np.argsort(np.argsort(W, axis=1), axis=1)
    rk_g = np.argsort(np.argsort(W, axis=0), axis=0)
    fu = co["fair_u"]
    pairs, X = [], []
    for gi in range(len(G)):
        srt = np.sort(W[gi])
        for ti in range(len(T)):
            d = W[gi, ti]
            if d > WALK_MAX:
                continue
            first = srt[0] if rk_t[gi, ti] > 0 else (srt[1] if len(srt) > 1 else 999.0)
            onf = 0.0
            if fu is not None and d > 40:
                ln = LineString([G[gi], Tc[ti]])
                try:
                    onf = ln.intersection(fu).length / (ln.length or 1.0)
                except Exception:
                    onf = 0.0
            pairs.append((gi, ti))
            X.append([d, rk_t[gi, ti], rk_g[gi, ti], (d + 20.0) / (first + 20.0), co["pnext"].get((gi, ti), np.nan),
                      T[ti]["p"], co["Gp"][gi], ct[ti], cg[gi], onf, geo["D"][ti, gi], float(np.sum(W[gi] < 150))])
    return np.array(pairs, int).reshape(-1, 2), np.array(X, float).reshape(-1, len(WF)), W
