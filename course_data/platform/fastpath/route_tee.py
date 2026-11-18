"""Per-hole tee refinement for router v2 (route_scene), after the routing is fixed.

The solver picks, per hole, a tee complex (or a virtual tee on the card ring) and route_scene a box inside it (the one
whose play length fits the card's geometric-mean set). On the routing bench the largest block of wrong holes left is
the tee end: the green is right but the line starts at a box that is no hole tee (a back tee the scorer does not count,
a complex the detector merged with a neighbour's, a virtual tee where a weak P(tee) pad exists) or at another hole's
tee (shared / merged complexes). routing.score counts a tee as right when it lies within 40 yd of the first 60 % of
the hole's line, so any real tee box of the hole counts (back, middle or forward).

This module, per hole with its green fixed:
  * candidates (`candidates`): every box of every tee complex (all complexes, including those other holes use, so
    two holes can share a complex and a merged complex is split per hole by which box each takes), local maxima of
    the U-Net P(tee) map (pads the detector did not group into a complex) and the incumbent tee, within card reach of
    the green;
  * features (`FEATS`): play length vs each card set (relative residuals), offset from the incumbent along / across
    the hole axis, P(tee) at the spot, detector p / size of its complex and the box's place in it, whether another hole
    of the routing tees off there (and in which direction), fairway / turf / trees along the line to the green, the
    walk from the previous green, the hole model's pair score;
  * a gradient-boosted classifier (route_tee_model.pkl) gives P(candidate is a hole tee of this hole); the best one
    replaces the incumbent when it beats it by the model's margin.

Env ROUTE_TEE (default 1 when route_tee_model.pkl exists): 0 turns it off. The bench's ROUTE_TEE_PICKS (json {slug:
{position: [x, y] local yd}}) gives out-of-fold choices instead (route_bench).
"""
from __future__ import annotations

import os
import pickle

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "route_tee_model.pkl")
_M = {}

FEATS = ("src", "is_inc", "D", "r_min", "r_back", "r_front", "r_geom", "r_geom_inc", "dD", "d_inc", "along", "lat",
         "ang", "pt", "pt_inc", "pt_mean", "c_p", "c_nbox", "c_len", "c_rank", "c_rank_rel", "same_c", "used_other",
         "d_other_tee", "ang_other", "d_other_green", "walk", "walk_inc", "dwalk", "fr_mean", "fr_start", "turf_mean",
         "tree_mean", "tree_run", "turf_gap", "water", "ph", "ph_inc", "g_virtual", "t_virtual", "par", "start",
         "n_cand", "pt_rank", "D_rank")
SRC = dict(inc=0, box_inc=1, box=2, peak=3)


def _ang(u, v):
    a = np.arctan2(u[..., 1], u[..., 0]) - np.arctan2(v[..., 1], v[..., 0])
    return np.abs((a + np.pi) % (2 * np.pi) - np.pi)


def tee_peaks(M, th=0.25, win_m=15.0):
    """local maxima of P(tee) (smoothed, sigma 2 px) >= th in a win_m window -> ([n, 2] local yd, [n] value)"""
    if M is None or getattr(M, "tee", None) is None or M.A is None:
        return np.zeros((0, 2)), np.zeros(0)
    import cv2
    sm = cv2.GaussianBlur(M.tee.astype(np.float32) / 255.0, (0, 0), 2.0)
    w = max(3, int(round(win_m)) | 1)
    mx = cv2.dilate(sm, np.ones((w, w), np.uint8))
    rr, cc = np.where((sm >= mx - 1e-6) & (sm >= th))
    if not len(rr):
        return np.zeros((0, 2)), np.zeros(0)
    A = M.A                                         # [x, y, 1] @ A = [row, col]
    B = np.linalg.inv(A[:2].T)                      # [row, col] - A[2] -> [x, y]
    xy = (np.c_[rr, cc].astype(float) - A[2]) @ B.T
    return xy, sm[rr, cc].astype(float)


def _pt(M, P, r=4.0):
    """max / mean P(tee) within r yd of each point"""
    if M is None or getattr(M, "tee", None) is None:
        z = np.zeros(len(P))
        return z, z
    off = np.stack(np.meshgrid(np.arange(-r, r + 0.1, 2.0), np.arange(-r, r + 0.1, 2.0)), -1).reshape(-1, 2)
    S = M.sample(np.asarray(P, float)[:, None, :] + off[None], "tee")
    return S.max(1), S.mean(1)


def candidates(d, pr, holes, TQ, GQ, peaks=None, lo=0.4, hi=1.5, dedupe=4.0):
    """per position i with a green: dict(P=[m, 2] local yd, F=[m, len(FEATS)], inc=0) (row 0 = the incumbent tee),
    None where the hole has no tee or green. holes: [(t, g)] (-1 = virtual); TQ / GQ: tee / green spots (local yd)"""
    import route_learn as RL
    co, geo = d["co"], d["geo"]
    M = d.get("_maps")
    N = len(holes)
    Y = pr.Y if pr is not None else None
    yg = pr.ygeom() if Y is not None else None
    loop = pr.loop if pr is not None else (9 if N % 9 == 0 else N)
    ta = d.get("_tattr")
    pars = getattr(pr, "card_par", None)
    if peaks is None:
        peaks = tee_peaks(M)
    pk_xy, pk_v = peaks
    # all boxes: (xy, complex, rank from the back for its complex)
    bx, bc = [], []
    for t, tc in enumerate(co["T"]):
        if "/" in str(tc.get("id", "")):               # split halves repeat the whole complex's boxes
            continue
        for p in tc["pts"]:
            bx.append(p)
            bc.append(t)
    bx = np.asarray(bx, float).reshape(-1, 2)
    bc = np.asarray(bc, int)
    clen = np.zeros(len(co["T"]))
    for t, tc in enumerate(co["T"]):
        q = np.asarray(tc["pts"], float)
        clen[t] = float(np.max(np.hypot(*(q[:, None] - q[None]).transpose(2, 0, 1)))) if len(q) > 1 else 0.0
    base = [t for t, _ in holes]
    out = []
    for i, (t, g) in enumerate(holes):
        if TQ[i] is None or GQ[i] is None:
            out.append(None)
            continue
        gq, inc = np.asarray(GQ[i], float), np.asarray(TQ[i], float)
        ys = Y[:, i].astype(float) if Y is not None else None
        ymax = float(np.max(ys)) if ys is not None else 600.0
        ymin = float(np.min(ys)) if ys is not None else 100.0
        P, src, cpx = [inc], [SRC["inc"]], [t if t >= 0 else -1]
        Db = np.hypot(*(bx - gq).T) if len(bx) else np.zeros(0)
        for j in np.where((Db >= lo * ymin) & (Db <= hi * ymax + 20))[0]:
            P.append(bx[j])
            ct = bc[j]
            same = t >= 0 and (ct == t or str(co["T"][t].get("id", "")).split("/")[0] == str(co["T"][ct].get("id", "")))
            src.append(SRC["box_inc"] if same else SRC["box"])
            cpx.append(ct)
        if len(pk_xy):
            Dp = np.hypot(*(pk_xy - gq).T)
            for j in np.where((Dp >= lo * ymin) & (Dp <= hi * ymax + 20))[0]:
                P.append(pk_xy[j])
                src.append(SRC["peak"])
                cpx.append(-1)
        P = np.asarray(P, float)
        keep = [0]
        for j in range(1, len(P)):                      # drop near-duplicates (keep the first: inc, boxes, peaks)
            if min(np.hypot(*(P[keep] - P[j]).T)) >= dedupe:
                keep.append(j)
        P, src, cpx = P[keep], np.asarray(src)[keep], np.asarray(cpx)[keep]
        m = len(P)
        D = np.hypot(*(P - gq).T)
        F = np.zeros((m, len(FEATS)))
        f = {k: F[:, n] for n, k in enumerate(FEATS)}
        f["src"][:] = src
        f["is_inc"][0] = 1
        f["D"][:] = D
        if ys is not None:
            R = (D[:, None] - ys[None]) / ys[None]
            f["r_min"][:] = np.min(np.abs(R), 1)
            f["r_back"][:] = (D - ymax) / ymax
            f["r_front"][:] = (D - ymin) / ymin
            f["r_geom"][:] = (D - yg[i]) / yg[i]
            f["r_geom_inc"][:] = (D[0] - yg[i]) / yg[i]
        f["dD"][:] = D - D[0]
        u = gq - inc
        L0 = max(float(np.hypot(*u)), 1.0)
        u = u / L0
        rel = P - inc
        f["d_inc"][:] = np.hypot(*rel.T)
        f["along"][:] = rel @ u                     # > 0: toward the green
        f["lat"][:] = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
        f["ang"][:] = _ang(gq - P, gq - inc[None])
        mx, mn = _pt(M, P)
        f["pt"][:], f["pt_mean"][:], f["pt_inc"][:] = mx, mn, mx[0]
        for j in range(m):
            ct = cpx[j]
            if ct >= 0:
                f["c_p"][j] = float(ta[ct][0]) if ta is not None and ta[ct][0] == ta[ct][0] else 0.9
                q = np.asarray(co["T"][ct]["pts"], float)
                f["c_nbox"][j] = len(q)
                f["c_len"][j] = clen[ct]
                dq = np.hypot(*(q - gq).T)
                f["c_rank"][j] = int(np.sum(dq > D[j] + 1.0))          # boxes of its complex farther from the green
                f["c_rank_rel"][j] = f["c_rank"][j] / max(len(q) - 1, 1)
                f["same_c"][j] = float(t >= 0 and str(co["T"][t].get("id", "")).split("/")[0]
                                       == str(co["T"][ct].get("id", "")).split("/")[0])
                f["used_other"][j] = float(any(b >= 0 and k != i and str(co["T"][b].get("id", "")).split("/")[0]
                                               == str(co["T"][ct].get("id", "")).split("/")[0]
                                               for k, b in enumerate(base)))
                if g >= 0:
                    f["ph"][j] = float(pr.ph.get((int(ct), int(g)), 0.0)) if pr is not None else 0.0
            else:
                f["c_p"][j] = -1
        if t >= 0 and g >= 0 and pr is not None:
            f["ph_inc"][:] = float(pr.ph.get((int(t), int(g)), 0.0))
        oth = [k for k in range(N) if k != i and TQ[k] is not None]
        if oth:
            OT = np.asarray([TQ[k] for k in oth], float)
            dd = np.hypot(*(P[:, None] - OT[None]).transpose(2, 0, 1))      # [m, n_other]
            jn = np.argmin(dd, 1)
            f["d_other_tee"][:] = dd[np.arange(m), jn]
            for j in range(m):
                k = oth[jn[j]]
                if GQ[k] is not None:
                    f["ang_other"][j] = _ang(np.asarray(GQ[k], float) - np.asarray(TQ[k], float), gq - P[j])
        og = [GQ[k] for k in range(N) if k != i and GQ[k] is not None]
        if og:
            OG = np.asarray(og, float)
            f["d_other_green"][:] = np.min(np.hypot(*(P[:, None] - OG[None]).transpose(2, 0, 1)), 1)
        if i % loop != 0 and GQ[i - 1] is not None:
            w = np.hypot(*(P - np.asarray(GQ[i - 1], float)).T)
            f["walk"][:], f["walk_inc"][:], f["dwalk"][:] = w, w[0], w - w[0]
        else:
            f["walk"][:] = f["walk_inc"][:] = -1
        if M is not None:
            st = RL.line_stats(M, P, np.broadcast_to(gq, P.shape).copy(), 0.08, 0.92, 25)
            for k in ("fr_mean", "fr_start", "turf_mean", "tree_mean", "tree_run", "turf_gap", "water"):
                f[k][:] = st[k]
        f["g_virtual"][:] = float(g < 0)
        f["t_virtual"][:] = float(t < 0)
        f["par"][:] = float(pars[i]) if pars and pars[i] else 0.0
        f["start"][:] = float(i % loop == 0)
        f["n_cand"][:] = m
        f["pt_rank"][:] = np.argsort(np.argsort(-mx))
        f["D_rank"][:] = np.argsort(np.argsort(f["r_min"][:])) if ys is not None else 0
        out.append(dict(P=P, F=F, inc=0, src=src, cpx=cpx))
    return out


def model():
    if "m" not in _M:
        _M["m"] = pickle.load(open(MODEL, "rb")) if os.path.exists(MODEL) else None
    return _M["m"]


def enabled():
    return os.environ.get("ROUTE_TEE", "1") != "0" and model() is not None


def refine(d, pr, holes, TQ, GQ, m=None, cands=None):
    """-> (new TQ list, info {position: dict(p_inc, p_new)}) for the switched holes"""
    m = m or model()
    if m is None:
        return TQ, {}
    cs = cands if cands is not None else candidates(d, pr, holes, TQ, GQ)
    TQ = list(TQ)
    info = {}
    for i, c in enumerate(cs):
        if c is None or len(c["P"]) < 2:
            continue
        p = m["model"].predict_proba(c["F"][:, m.get("keep", slice(None))])[:, 1]
        j = int(np.argmax(p))
        if j != 0 and p[j] - p[0] > m["delta"]:
            TQ[i] = tuple(c["P"][j])
            info[i] = dict(p_inc=round(float(p[0]), 3), p_new=round(float(p[j]), 3), src=int(c["src"][j]))
    return TQ, info
