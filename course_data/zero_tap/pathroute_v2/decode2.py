"""pathroute v2 decoder: the v1 tour beam (clubhouse -> T1 -> G1 -> walk -> T2 ... -> clubhouse) with GLOBAL pairing
constraints carried in each beam state:

- tee exclusivity: a tee complex (tee boxes of one hole, see complexes.py) serves one hole; reusing a complex /
  a tee already inside another hole's box set costs `reuse` nats;
- hole corridors do not cross: two chosen tee -> green segments that intersect cost `cross` nats each.

Each green keeps its K best tees as candidates (hole cost), so a state can carry, for every candidate pair p, the
running count of earlier pairs that cross / share a complex with p (beam x (ng*K) matrix, updated incrementally).
"""
from __future__ import annotations

import numpy as np

import decode as DC


def _seg_cross(A, B, C, D):
    """[n, m] proper intersection of segments A[i]B[i] and C[j]D[j]."""
    def orient(P, Q, R):
        return (Q[..., 0] - P[..., 0]) * (R[..., 1] - P[..., 1]) - (Q[..., 1] - P[..., 1]) * (R[..., 0] - P[..., 0])
    A, B = A[:, None, :], B[:, None, :]
    C, D = C[None, :, :], D[None, :, :]
    o1, o2 = orient(A, B, C), orient(A, B, D)
    o3, o4 = orient(C, D, A), orient(C, D, B)
    return (o1 * o2 < 0) & (o3 * o4 < 0)


def candidates(H, K, avail_t, avail_g, force_t=None):
    """[ng, K] best tees per green by hole cost (unavailable tees / greens -> inf cost). force_t: a tee that must
    be a candidate of every green (the golfer's "this tee is hole 1"): it replaces the K-th slot where absent."""
    Hm = H.copy()
    Hm[~avail_t, :] = np.inf
    Hm[:, ~avail_g] = np.inf
    K = min(K, H.shape[0])
    top = np.argsort(Hm, axis=0, kind="stable")[:K].T          # ng, K
    if force_t is not None and K >= 2:
        miss = ~(top == force_t).any(1)
        top[miss, K - 1] = force_t
    hc = np.take_along_axis(Hm.T, top, 1)                       # ng, K
    return top, hc


def pair_mats(top, tc, gc, comp, boxes_of, shrink=0.12):
    """Crossing (X) and sharing (R) matrices over candidate pairs p = g*K + k."""
    ng, K = top.shape
    t = top.ravel()
    g = np.repeat(np.arange(ng), K)
    A, Bp = tc[t], gc[g]
    v = Bp - A
    # shrink both ends a little so pairs that merely touch at a shared tee / near-green do not count
    A2, B2 = A + shrink * v, Bp - shrink * v
    X = _seg_cross(A2, B2, A2, B2).astype(np.float32)
    same_g = g[:, None] == g[None, :]
    X[same_g] = 0
    cp = comp[t]
    R = (cp[:, None] == cp[None, :]).astype(np.float32)
    if boxes_of is not None:
        bx = boxes_of[t]                                         # [P, nt] bool: tee t2 in box set of t
        R = np.maximum(R, bx[:, t].astype(np.float32))
        R = np.maximum(R, R.T)
    R[same_g] = 0
    return X, R, t, g


def beam_loop2(H, T, S, E, n, avail_g, avail_t, tc, gc, comp, boxes_of=None, K=6, beam=4000, mid=None,
               cross=1.5, reuse=4.0, pins=None, first=None, first_force=None):
    """pins {position k (1-based): (tee, green)}: that exact pair at step k (and its green nowhere else);
    first: a set of tees allowed at step 1 (the golfer's hole-1 tee and its complex); first_force: that tee is made
    a candidate of every green."""
    ng, nt = H.shape[1], H.shape[0]
    pins = {k: v for k, v in (pins or {}).items() if 1 <= k <= n}
    top, hc = candidates(H, K, avail_t, avail_g, force_t=first_force if first else None)
    K = top.shape[1]
    X, R, pt, pg = pair_mats(top, tc, gc, comp, boxes_of)
    PEN = cross * X + reuse * R                                  # [P, P]
    same_t = (pt[:, None] == pt[None, :]) & (pg[:, None] != pg[None, :])
    PEN[same_t] += 50.0                                          # one tee box never serves two holes
    Pn = ng * K
    # step cost from green g (last) to pair p (tee pt[p], green pg[p]): T[g, pt] + hc[p]
    hcf = hc.ravel()
    Tstep = T[:, pt] + hcf[None, :]                              # [ng, P]
    Tmid = (T + S[None, :])[:, pt] + hcf[None, :] + E[:, None]
    s0 = S[pt] + hcf                                             # start pairs
    step_ok = {}                                                 # k -> [P] bool: pairs allowed at step k
    if pins or first:
        pin_p = {}
        for k, (t, g) in pins.items():
            hit = np.nonzero((pt == t) & (pg == g))[0]
            if not len(hit):
                return None
            pin_p[k] = int(hit[0])
        pinned_g = {pins[k][1]: k for k in pins}
        for k in range(1, n + 1):
            ok_k = np.ones(len(pt), bool)
            if k in pin_p:
                ok_k[:] = False
                ok_k[pin_p[k]] = True
            for g, kk in pinned_g.items():
                if kk != k:
                    ok_k[pg == g] = False
            if k == 1 and first:
                ok_k &= np.isin(pt, sorted(first))
            step_ok[k] = ok_k
        if 1 in step_ok:
            s0 = np.where(step_ok[1], s0, np.inf)
    ok = np.isfinite(s0)
    p_last = np.nonzero(ok)[0]
    cost = s0[ok]
    gl = pg[p_last]
    mask = np.int64(1) << gl.astype(np.int64)
    pen = PEN[p_last].copy()                                     # [beam, P]
    hist = [(np.full(len(p_last), -1), p_last.copy())]
    gbit = np.int64(1) << pg.astype(np.int64)
    for k in range(2, n + 1):
        Ts = Tmid if (mid and k == mid + 1) else Tstep
        cand = cost[:, None] + Ts[gl, :] + pen                   # [beam, P]
        used = (mask[:, None] & gbit[None, :]) != 0
        cand[used] = np.inf
        if k in step_ok:
            cand[:, ~step_ok[k]] = np.inf
        # per (state, green) keep only the best of its K tees (dedup over keys does the rest)
        cg = cand.reshape(len(cost), ng, K)
        kb = np.argmin(cg, axis=2)
        cbest = np.take_along_axis(cg, kb[:, :, None], 2)[:, :, 0]   # [beam, ng]
        flat = cbest.ravel()
        keep = np.nonzero(np.isfinite(flat))[0]
        if not len(keep):
            return None
        order = keep[np.argsort(flat[keep], kind="stable")]
        par, g = order // ng, order % ng
        nm = mask[par] | (np.int64(1) << g.astype(np.int64))
        key = nm * 64 + g
        _, first = np.unique(key, return_index=True)
        first = np.sort(first)[:beam]
        par, g = par[first], g[first]
        p = g * K + kb[par, g]
        cost = flat[order[first]]
        mask = nm[first]
        pen = pen[par] + PEN[p]
        gl = g
        hist.append((par, p.copy()))
    fin = cost + E[gl]
    o = np.argsort(fin)
    best = o[0]
    rel = fin[o[:500]] - fin[best]
    conf = float(1.0 / np.sum(np.exp(-rel)))
    seq = []
    i = best
    for par, p in reversed(hist):
        seq.append(int(p[i]))
        i = par[i]
    seq = seq[::-1]
    return [int(pg[p]) for p in seq], [int(pt[p]) for p in seq], float(fin[best]), conf


def box_sets(tc, avail_t=None):
    """v1 box rule as a matrix: boxes_of[t, t2] = t2 within 80 yds of t (lateral test is per hole; here radius 45)."""
    D = np.hypot(tc[:, None, 0] - tc[None, :, 0], tc[:, None, 1] - tc[None, :, 1])
    return D < 45


FIX_BONUS = 30.0          # nats: a golfer-confirmed pair is always worth including


def apply_fix(H, comp, fix):
    """Golfer-confirmed facts -> hole-cost matrix. fix = {"pairs": [(number | None, tee, green)], "not_green": [g],
    "first_tee": t | None}. A confirmed pair's tee complex serves only that green, the green only that tee, and the
    pair gets FIX_BONUS so the tour always includes it; a "not a hole" green is removed."""
    H0, H = H, H.copy()
    comp = np.asarray(comp)
    pairs = list((fix or {}).get("pairs") or ())
    fixed_t = {int(t) for _, t, _ in pairs}
    for _, t, g in pairs:                     # two true holes can share a complex: never blank a confirmed tee
        cm = [c for c in np.nonzero(comp == comp[t])[0] if c not in fixed_t or c == t]
        H[cm, :] = np.inf
        H[:, g] = np.inf
    for _, t, g in pairs:
        H[t, :] = np.inf
        H[t, g] = min(H0[t, g], DC.BIG) - FIX_BONUS
    for g in (fix or {}).get("not_green") or ():
        H[:, g] = np.inf
    return H


def decode2(d, pr, w, comp, beam=4000, K=6, cross=1.5, reuse=4.0, box_mode="v1+comp", H=None, return_cost=False,
            fix=None):
    """Joint pairing + order decode. fix (golfer-confirmed facts, see apply_fix): pairs [(number, tee, green)] -
    with a number on a 9 / 18-hole course the pair is pinned to that position of the (first) loop, number None
    = pair only (any position / loop); "first_tee": the tee of hole 1 (fixes the start and the direction)."""
    kind = d["kind"]
    n = 9 if kind in (9, 27) else 18
    loops = {9: 1, 18: 1, 27: 3, 36: 2}.get(kind, max(1, round(kind / n)))
    H0, T, S, E = DC.cost_mats(d, pr, w)
    H = H0 if H is None else H
    comp_a = np.asarray(comp)
    if fix:
        H = apply_fix(H, comp_a, fix)
    pins = {int(k): (int(t), int(g)) for k, t, g in (fix or {}).get("pairs") or () if k is not None and loops == 1}
    first = None
    if fix and fix.get("first_tee") is not None:
        ft = int(fix["first_tee"])
        first = set(np.nonzero(comp_a == comp_a[ft])[0].tolist()) | {ft}
        if 1 in pins:
            first.add(pins[1][0])
    ng, nt = H.shape[1], H.shape[0]
    avail_g, avail_t = np.ones(ng, bool), np.ones(nt, bool)
    tc = np.asarray(d["tc"], float)
    gcs = np.asarray(d["gc"], float)
    comp = np.asarray(comp)
    bo = box_sets(tc)
    out, confs, costs = [], [], []
    for li in range(loops):
        r = beam_loop2(H, T, S, E, n, avail_g, avail_t, tc, gcs, comp, bo, K=K, beam=beam,
                       mid=9 if n == 18 else None, cross=cross, reuse=reuse,
                       pins=pins if li == 0 else None, first=first if li == 0 else None,
                       first_force=int(fix["first_tee"]) if first and li == 0 else None)
        if r is None:
            break
        gs, ts, c, conf = r
        confs.append(conf)
        costs.append(c)
        for k, (g, t) in enumerate(zip(gs, ts)):
            gp, tp = gcs[g], tc[t]
            u = (gp - tp) / max(np.hypot(*(gp - tp)), 1.0)
            rel = tc - tp
            lat = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
            box = set(np.nonzero((np.hypot(*rel.T) < 80) & (lat < 22) & avail_t)[0].tolist()) if "v1" in box_mode \
                else set()
            if "comp" in box_mode:
                box |= set(np.nonzero((comp == comp[t]) & avail_t)[0].tolist())
            box.discard(t)
            box = sorted(int(b) for b in box)
            L = max([float(np.hypot(*(gp - tc[b]))) for b in box + [t]])
            out.append(dict(number=k + 1, g=g, t=t, boxes=box, L=L, loop=li))
            avail_g[g] = False
            avail_t[t] = False
            for b in box:
                avail_t[b] = False
            avail_t[comp == comp[t]] = False
    if return_cost:
        return out, float(np.prod(confs)) if confs else 0.0, float(np.sum(costs)) if costs else np.inf
    return out, float(np.prod(confs)) if confs else 0.0
