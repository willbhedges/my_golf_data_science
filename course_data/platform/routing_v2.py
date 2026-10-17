"""Hole routing v2: card-assisted global sequence optimisation with learned weights, golfer constraints and
posterior marginals (for flags and for choosing confirm questions).

    import routing as R, routing_v2 as R2
    inp = R.inputs_from_fc(fc, segment=seg, pads=pads, boundary=course["boundary"], hide_holes=...)
    ctx = R2.context(inp, card, fc=fc)                 # every per-course matrix, built once
    res = R2.solve(ctx)                                 # routing.route-compatible dict (+ posterior, top routings)
    res = R2.solve(ctx, fixed={"1": (t, g)}, exclude={"7": {g}})   # golfer answers -> re-solve the rest
    R2.route(inp, card, fc=fc)                          # one call (context + solve)

What v1 (routing.py) does and v2 keeps: hole n = a (tee box, green) hypothesis or a miss, a beam search in card
order over the whole round (greens / boxes used once, crossing lines penalised, tee boxes on a hole's line
"explained"), the length / tee-set fingerprint / corridor / alignment terms.

What v2 adds
  learned weights   every cost is w . f with f a feature vector (FEATURES); w is fitted by a structured
                    perceptron on the train split (route_eval.py train): the router's best routing vs the cheapest
                    routing that agrees with the hidden OSM holes. Defaults = v1's hand weights.
  loop closure      the beam carries hole 1's tee: green 9 (18-hole card) and the last green pay their distance
                    back to tee 1 (both nines start and end at the clubhouse), whatever the clubhouse guess is:
                    ((d - 150) / 220)^2, capped at 4.
  facilities        all car parks, the clubhouse and big buildings by them: tee 1 / tee 10 / greens 9 / 18 pay the
                    distance to the NEAREST facility point (one wrong clubhouse guess no longer drags hole 1).
  cart paths        OSM cart paths / footways as a graph: a green -> next tee transition joined by a short path
                    (network distance <= 1.6 x straight + 40 yds) is a feature (`cart_link`); a transition whose
                    endpoints are both on the network but far apart along it is `cart_far`.
  practice greens   a green within 120 yds of a facility point with no box in any card hole's yardage window ->
                    `practice` feature (a putting / chipping green); greens within 45 yds of another green (v1).
  facility split    with many more greens than card holes (36-hole facilities, an adjacent course inside the
                    boundary) the greens / boxes are clustered by single-linkage (gap 230 yds); clusters are tried
                    alone and in pairs, each scored by its routing cost + UNUSED_GREEN_W per green of the set the
                    routing leaves unused (a course uses its own area's greens), and the best wins (`facility_split`).
  constraints       fixed {ref: (tee, green)} pins a hole (a golfer's answer), exclude {ref: {green}} forbids greens:
                    one answer re-solves the whole round ("propagation").
  posterior         the final beam's distinct routings, Boltzmann-weighted at temperature TAU: per hole the
                    marginal of its (green, tee-complex) -> `p_hole`; status `check` when p_hole < P_CHECK.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import routing as R  # noqa: E402

FEATURES = ("length", "fingerprint", "corridor", "cross_green", "align", "ch_tee1", "ch_tee10", "ch_green_end",
            "fac_tee1", "fac_tee10", "fac_green_end", "green_cluster", "green_model", "practice",
            "walk", "walk_turn", "cart_link", "cart_far", "loop", "cover", "covered_start", "reused_tee",
            "cross_lines", "miss_tee", "miss_hole")
FI = {k: i for i, k in enumerate(FEATURES)}
NF = len(FEATURES)
# v1's hand weights (routing.py) as the starting point; the new terms start small
W_V1 = dict(length=1.0, fingerprint=1.0, corridor=1.2, cross_green=1.5, align=1.0, ch_tee1=1.0, ch_tee10=0.6,
            ch_green_end=0.5, fac_tee1=0.0, fac_tee10=0.0, fac_green_end=0.0, green_cluster=1.0, green_model=1.0,
            practice=0.0, walk=1.0, walk_turn=0.3, cart_link=0.0, cart_far=0.0, loop=0.0, cover=1.0,
            covered_start=2.0, reused_tee=2.5, cross_lines=1.5, miss_tee=4.0, miss_hole=8.0)
SIGNED = {"cart_link", "cover"}            # features whose weight may take either sign (others are kept >= 0)
WEIGHTS_FILE = os.path.join(HERE, "routing_v2_weights.json")
BEAM = 6000
TOPK = 80
PER_GREEN = 6
TAU = 1.0
P_CHECK = 0.8
FAC_FREE, FAC_SCALE = 110.0, 160.0
LOOP_FREE, LOOP_SCALE = 150.0, 220.0
SPLIT_GAP = 230.0
UNUSED_GREEN_W = 1.0


def load_weights(path=WEIGHTS_FILE):
    """Learned weights (route_eval.py train) merged over W_V1; -> (w vector, tau, p_check)."""
    import json
    w = dict(W_V1)
    tau, pchk = TAU, P_CHECK
    if path and os.path.exists(path):
        js = json.load(open(path))
        w.update(js.get("w", {}))
        tau, pchk = js.get("tau", tau), js.get("p_check", pchk)
    return np.array([w[k] for k in FEATURES], float), tau, pchk


def wvec(d):
    return np.array([d.get(k, 0.0) for k in FEATURES], float)


# ----------------------------------------------------------------------------- facility points / cart paths
def facility_points(fc, inp, boundary_rings=()):
    """[(lon, lat)] of the clubhouse, every car park within 200 yds of the course, and buildings > 300 m2 within
    120 yds of a car park (clubhouse / pro shop / cart barn candidates)."""
    pts = []
    ch = inp.get("clubhouse")
    if ch:
        pts.append((ch[0], ch[1]))
    if not fc:
        return pts
    parks, blds = [], []
    for f in fc.get("features", []):
        p, g = f.get("properties", {}), f.get("geometry")
        if not g:
            continue
        if p.get("amenity") == "parking" or p.get("service") == "parking_aisle":
            ll = R._ll_of(g)
            if ll and (not boundary_rings or R._near_rings(ll, boundary_rings, 200)):
                parks.append(ll)
        elif p.get("building") and p.get("building") not in ("house", "residential", "apartments", "garage", "detached",
                                                             "shed", "roof"):
            rings = R._outer_rings(g)
            ll = R._ll_of(g)
            if rings and ll:
                a = R.poly_area(R.Proj(*ll).ring(rings[0])) * R.YD * R.YD
                if a > 300:
                    blds.append(ll)
    pts += parks
    for b in blds:
        pr = R.Proj(*b)
        if any(math.hypot(*pr.fwd(*pk)) < 120 for pk in parks):
            pts.append(b)
    return pts


def cart_graph(fc, pr):
    """Cart paths / footways (LineStrings that are not golf=hole) -> (node xy (N, 2), csr adjacency) or None."""
    lines = []
    for f in (fc or {}).get("features", []):
        p, g = f.get("properties", {}), f.get("geometry") or {}
        if g.get("type") != "LineString" or p.get("golf") == "hole":
            continue
        if not (p.get("golf") in ("cartpath", "path") or p.get("highway") or p.get("golf_cart")):
            continue
        if p.get("highway") in ("motorway", "trunk", "primary", "secondary", "tertiary", "residential",
                                "unclassified", "motorway_link", "trunk_link", "primary_link"):
            continue
        xy = pr.ring(g["coordinates"])
        if len(xy) >= 2:
            lines.append(xy)
    if not lines:
        return None
    # densify (<= 25 yds per edge) and snap vertices within 3 yds (shared OSM nodes, near-misses)
    pts, edges = [], []
    for xy in lines:
        dense = [xy[0]]
        for a, b in zip(xy[:-1], xy[1:]):
            L = float(np.hypot(*(b - a)))
            k = max(1, int(math.ceil(L / 25.0)))
            for j in range(1, k + 1):
                dense.append(a + (b - a) * j / k)
        base = len(pts)
        pts += dense
        edges += [(base + j, base + j + 1) for j in range(len(dense) - 1)]
    P = np.asarray(pts)
    key = np.round(P / 3.0).astype(np.int64)
    _, inv = np.unique(key[:, 0] * 10_000_019 + key[:, 1], return_inverse=True)
    N = int(inv.max()) + 1
    node = np.zeros((N, 2))
    node[inv] = P
    from scipy.sparse import coo_matrix
    a = np.array([inv[i] for i, _ in edges])
    b = np.array([inv[j] for _, j in edges])
    w = np.hypot(*(node[a] - node[b]).T) + 1e-3
    keep = a != b
    M = coo_matrix((np.r_[w[keep], w[keep]], (np.r_[a[keep], b[keep]], np.r_[b[keep], a[keep]])), shape=(N, N)).tocsr()
    # join dangling ends within 15 yds (OSM paths that stop short of each other)
    from scipy.spatial import cKDTree
    deg = np.diff(M.indptr)
    ends = np.nonzero(deg <= 1)[0]
    if len(ends):
        tr = cKDTree(node)
        add = []
        for e in ends:
            for j in tr.query_ball_point(node[e], 15.0):
                if j != e:
                    add.append((e, j, float(np.hypot(*(node[e] - node[j]))) + 1e-3))
        if add:
            a2, b2, w2 = map(np.array, zip(*add))
            M = M + coo_matrix((np.r_[w2, w2], (np.r_[a2, b2].astype(int), np.r_[b2, a2].astype(int))), shape=(N, N)).tocsr()
    return node, M


def cart_features(fc, pr, gxy, txy):
    """(cart_link, cart_far) (nG, nT): a short path from green g to box t, or both on the network but far apart."""
    nG, nT = len(gxy), len(txy)
    link, far = np.zeros((nG, nT)), np.zeros((nG, nT))
    try:
        cg = cart_graph(fc, pr)
    except Exception:                                            # noqa: BLE001
        cg = None
    if cg is None or nT == 0:
        return link, far, 0
    node, M = cg
    from scipy.sparse.csgraph import dijkstra
    from scipy.spatial import cKDTree
    tr = cKDTree(node)
    dg, ig = tr.query(gxy)
    dt, it = tr.query(txy)
    gon, ton = dg < 45, dt < 45
    if not gon.any() or not ton.any():
        return link, far, len(node)
    src = np.nonzero(gon)[0]
    dist = dijkstra(M, indices=ig[src], limit=1500.0)
    S = np.hypot(gxy[:, None, 0] - txy[None, :, 0], gxy[:, None, 1] - txy[None, :, 1])
    for row, g in enumerate(src):
        nd = dist[row][it] + dg[g] + dt
        ok = ton & (S[g] < 450)
        link[g] = (ok & (nd <= 1.6 * S[g] + 40)).astype(float)
        far[g] = (ok & ~(nd <= 1.6 * S[g] + 40) & (S[g] > 60)).astype(float)
    return link, far, len(node)


# ----------------------------------------------------------------------------- context
def context(inp, card=None, fc=None, n_holes=None, boundary=None, subset=None):
    """Precompute everything that does not depend on the weights. subset=(green idx, tee idx) restricts the
    candidates (facility split)."""
    pr = inp.get("proj")
    G, T = list(inp["greens"]), list(inp["tees"])
    if subset is not None:
        G = [G[i] for i in subset[0]]
        T = [T[i] for i in subset[1]]
    n, pars, yards = R.card_holes(card)
    if n is None:
        n = n_holes or (18 if len(G) >= 13 else 9)
        pars, yards = [None] * n, [[] for _ in range(n)]
    ctx = dict(inp=inp, G=G, T=T, n=n, pars=pars, yards=yards, card=card, proj=pr, ok=bool(pr is not None and G))
    if not ctx["ok"]:
        return ctx
    gxy = np.asarray([pr.fwd(*g["ll"]) for g in G], float).reshape(-1, 2)
    txy = np.asarray([pr.fwd(*t["ll"]) for t in T], float).reshape(-1, 2)
    nG, nT = len(G), len(T)
    D = np.hypot(txy[:, None, 0] - gxy[None, :, 0], txy[:, None, 1] - gxy[None, :, 1]) if nT else np.zeros((0, nG))
    W = D.T.copy()
    walk = np.minimum((np.maximum(W - R.WALK_FREE, 0) / R.WALK_SCALE) ** 2, 9.0)
    loopc = np.minimum((np.maximum(W - LOOP_FREE, 0) / LOOP_SCALE) ** 2, 4.0)     # green 9 / 18 back to tee 1
    GG = np.hypot(gxy[:, None, 0] - gxy[None, :, 0], gxy[:, None, 1] - gxy[None, :, 1])
    gclust = np.minimum((GG < R.PRACTICE_YD).sum(1) - 1, 2).astype(float)
    gmodel = np.array([0.0 if g["src"] == "osm" else 0.6 + 2.0 * (1.0 - float(g.get("p") or 0.8)) for g in G])
    wt = np.array([R.COV_W.get(t["src"], 0.2) for t in T])
    tee_axes = np.array([R.long_axis(pr.ring(t["poly"])) if t.get("poly") and len(t["poly"]) >= 4 else (0.0, 1.0)
                         for t in T]).reshape(-1, 2)
    ch = inp.get("clubhouse")
    chxy = np.asarray(pr.fwd(ch[0], ch[1])) if ch else None

    def dcost(xy, c):
        if c is None:
            return np.zeros(len(xy))
        d = np.hypot(xy[:, 0] - c[0], xy[:, 1] - c[1])
        return np.minimum((np.maximum(d - 150, 0) / 160) ** 2, 6.0)
    ch_t, ch_g = dcost(txy, chxy), dcost(gxy, chxy)
    rings = R._outer_rings(boundary) if isinstance(boundary, dict) else []
    fac = facility_points(fc, inp, rings)
    if fac:
        F = np.asarray([pr.fwd(*p) for p in fac], float).reshape(-1, 2)

        def fcost(xy):
            d = np.hypot(xy[:, None, 0] - F[None, :, 0], xy[:, None, 1] - F[None, :, 1]).min(1)
            return np.minimum((np.maximum(d - FAC_FREE, 0) / FAC_SCALE) ** 2, 6.0), d
        fac_t, _ = fcost(txy)
        fac_g, fac_gd = fcost(gxy)
    else:
        fac_t, fac_g, fac_gd = np.zeros(nT), np.zeros(nG), np.full(nG, np.inf)
    # corridor / crossings / alignment (as routing.route)
    fws = R._fairway_shapes([pr.ring(f["poly"]) for f in inp.get("fairways", [])])
    has_fw = bool(inp.get("fairways"))
    cand = D < 760
    corr = np.zeros_like(D)
    cross = np.zeros_like(D)
    ti, gi = np.nonzero(cand)
    if len(ti):
        fr = np.linspace(0.25, 0.85, 9)
        px = txy[ti, 0][:, None] + (gxy[gi, 0] - txy[ti, 0])[:, None] * fr[None]
        py = txy[ti, 1][:, None] + (gxy[gi, 1] - txy[ti, 1])[:, None] * fr[None]
        if fws:
            bear = np.arctan2(gxy[gi, 1] - txy[ti, 1], gxy[gi, 0] - txy[ti, 0])
            on = np.zeros(px.shape, bool)
            off = np.zeros(px.shape, bool)
            for test, ang, el in fws:
                hit = test(px.ravel(), py.ravel()).reshape(px.shape)
                dang = np.abs((bear - ang + np.pi / 2) % np.pi - np.pi / 2)
                aligned = (dang < math.radians(R.ALIGN_FW_DEG)) | (el < 1.6)
                on |= hit & aligned[:, None]
                off |= hit & ~aligned[:, None]
            corr[ti, gi] = (1.0 - on.mean(1)) + 0.7 * (off & ~on).mean(1)
        fr2 = np.linspace(0.15, 0.92, 24)
        qx = txy[ti, 0][:, None] + (gxy[gi, 0] - txy[ti, 0])[:, None] * fr2[None]
        qy = txy[ti, 1][:, None] + (gxy[gi, 1] - txy[ti, 1])[:, None] * fr2[None]
        for k in range(nG):
            dk = np.hypot(qx - gxy[k, 0], qy - gxy[k, 1]).min(1)
            hit = (dk < 12) & (gi != k)
            cross[ti[hit], gi[hit]] = 1.5
    align = np.zeros_like(D)
    for i, t in enumerate(T):
        if not t.get("poly") or len(t["poly"]) < 4:
            continue
        ang, el = tee_axes[i]
        if el < 1.4:
            continue
        b = np.arctan2(gxy[:, 1] - txy[i, 1], gxy[:, 0] - txy[i, 0])
        d = np.abs((b - ang + np.pi / 2) % np.pi - np.pi / 2)
        align[i] = np.minimum((np.maximum(np.degrees(d) - 20, 0) / 20) ** 2, 1.6) * 0.5
    DB = None
    if nT and nT * nT * nG <= 6_000_000:
        dv = gxy[None, :, :] - txy[:, None, :]
        L = np.maximum(np.hypot(dv[..., 0], dv[..., 1]), 1e-6)
        rel = txy[None, None, :, :] - txy[:, None, None, :]
        u = (rel[..., 0] * dv[:, :, None, 0] + rel[..., 1] * dv[:, :, None, 1]) / L[..., None]
        v = np.abs(rel[..., 0] * dv[:, :, None, 1] - rel[..., 1] * dv[:, :, None, 0]) / L[..., None]
        on = (u >= -R.COV_BACK) & (u <= R.COV_FWD * L[..., None]) & (v <= R.COV_PERP)
        DB = np.where(on, D.T[None, :, :], np.nan)
    # per-hole static feature planes (nT, nG) - stored sparsely as the candidate (t, g) lists
    holes = []
    allY = sorted({y for ys in yards for y in (ys or [])})
    for h in range(n):
        par = pars[h] if pars else None
        Y = yards[h] if yards else None
        if nT:
            lc, which = R.length_cost(D, Y or None, par)
            fp = R.fingerprint(DB, Y, par) if (Y and DB is not None) else np.zeros_like(D)
            ok = (lc < 9.5) & cand
        else:
            lc = which = fp = np.zeros((0, nG))
            ok = np.zeros((0, nG), bool)
        holes.append(dict(lc=lc, which=which, fp=fp, ok=ok, par=par))
    # practice greens: near a facility point and no box within any card hole's yardage window
    practice = np.zeros(nG)
    if nT and allY:
        win = np.zeros((nT, nG), bool)
        for hh in holes:
            win |= hh["ok"] & (hh["lc"] < 1.0)
        practice = ((fac_gd < 120) & ~win.any(0)).astype(float)
    elif nT:
        practice = ((fac_gd < 120) & ~((D > 90) & (D < 640)).any(0)).astype(float)
    link, far, n_cart = cart_features(fc, pr, gxy, txy)
    ctx.update(gxy=gxy, txy=txy, nG=nG, nT=nT, D=D, W=W, walk=walk, loopc=loopc, gclust=gclust, gmodel=gmodel, wt=wt,
               tee_axes=tee_axes, ch_t=ch_t, ch_g=ch_g, fac_t=fac_t, fac_g=fac_g, n_fac=len(fac), corr=corr,
               cross=cross, align=align, has_fw=has_fw, holes=holes, practice=practice, cart_link=link,
               cart_far=far, n_cart_nodes=n_cart, cov_cache={}, clubhouse=ch)
    return ctx


def _cov(ctx, tk, gk):
    key = (tk, gk)
    c = ctx["cov_cache"].get(key)
    if c is None:
        c = R._on_hole(ctx["txy"], ctx["txy"][tk], ctx["gxy"][gk], ctx["tee_axes"]) * ctx["wt"]
        ctx["cov_cache"][key] = c
    return c


def hole_rows(ctx, h, w, fixed=None, exclude=None, allowed=None, topk=TOPK):
    """Hypotheses of hole h: (tees, greens, feature rows (k, NF)). fixed (t, g) pins it; exclude = set of greens;
    allowed = bool (nT + 1, nG + 1) mask over (t | -1, g | -1) (the truth-constrained routing in training)."""
    n, nT, nG = ctx["n"], ctx["nT"], ctx["nG"]
    H = ctx["holes"][h]
    turn = (h == 9 and n >= 18)
    end_g = (h == n - 1) or (h == 8 and n >= 18)

    def feats(ti, gi):
        f = np.zeros((len(ti), NF))
        f[:, FI["length"]] = H["lc"][ti, gi]
        f[:, FI["fingerprint"]] = H["fp"][ti, gi]
        if H["par"] != 3 and ctx["has_fw"]:
            f[:, FI["corridor"]] = ctx["corr"][ti, gi]
        f[:, FI["cross_green"]] = ctx["cross"][ti, gi] / 1.5
        f[:, FI["align"]] = ctx["align"][ti, gi]
        if h == 0:
            f[:, FI["ch_tee1"]] = ctx["ch_t"][ti]
            f[:, FI["fac_tee1"]] = ctx["fac_t"][ti]
        if turn:
            f[:, FI["ch_tee10"]] = ctx["ch_t"][ti]
            f[:, FI["fac_tee10"]] = ctx["fac_t"][ti]
        if end_g:
            f[:, FI["ch_green_end"]] = ctx["ch_g"][gi]
            f[:, FI["fac_green_end"]] = ctx["fac_g"][gi]
        f[:, FI["green_cluster"]] = ctx["gclust"][gi]
        f[:, FI["green_model"]] = ctx["gmodel"][gi]
        f[:, FI["practice"]] = ctx["practice"][gi]
        return f
    if fixed is not None:
        tk, gk = fixed
        if tk >= 0 and gk >= 0:
            f = feats(np.array([tk]), np.array([gk]))
        else:
            f = np.zeros((1, NF))
            if gk >= 0:
                f[0, FI["miss_tee"]] = 1.0
                if end_g:
                    f[0, FI["ch_green_end"]] = ctx["ch_g"][gk]
                    f[0, FI["fac_green_end"]] = ctx["fac_g"][gk]
                f[0, FI["green_model"]] = ctx["gmodel"][gk]
            else:
                f[0, FI["miss_hole"]] = 1.0
        return np.array([tk]), np.array([gk]), f
    ok = H["ok"].copy()
    ex_g = [e for e in (exclude or ()) if not isinstance(e, tuple)]
    ex_k = {e for e in (exclude or ()) if isinstance(e, tuple) and not isinstance(e[0], str)}
    ex_n = [e for e in (exclude or ()) if isinstance(e, tuple) and isinstance(e[0], str)]   # ("near", g, x, y, r)
    if ex_g:
        ok[:, ex_g] = False
    if allowed is not None:
        ok &= allowed[:nT, :nG]
    ti, gi = np.nonzero(ok)
    if ex_k:                               # excluded (green, tee complex) answers: "no, that is not hole n"
        m = np.array([_hole_key(ctx, int(t), int(g)) not in ex_k for t, g in zip(ti, gi)], bool)
        ti, gi = ti[m], gi[m]
    for _, g0, x0, y0, r0 in ex_n:         # "no": that green with any box within r0 yds of the rejected one
        m = ~((gi == g0) & (np.hypot(ctx["txy"][ti, 0] - x0, ctx["txy"][ti, 1] - y0) < r0))
        ti, gi = ti[m], gi[m]
    F = feats(ti, gi)
    k = topk if allowed is None else max(topk, 400)
    if len(ti) > k:
        # the global best k plus the best PER_GREEN boxes of every green (a hole's true tee can rank below
        # many boxes of one well-fitting wrong green)
        c = F @ w
        o = np.argsort(c)
        keep = np.zeros(len(o), bool)
        keep[o[:k]] = True
        cnt = np.zeros(nG, int)
        for j in o:
            if cnt[gi[j]] < PER_GREEN:
                keep[j] = True
                cnt[gi[j]] += 1
        sel = np.nonzero(keep)[0]
        ti, gi, F = ti[sel], gi[sel], F[sel]
    # no tee found (any green) / nothing
    gs = np.array([k for k in range(nG) if k not in ex_g and (k, None) not in ex_k and
                   (allowed is None or allowed[nT, k])], int)
    f2 = np.zeros((len(gs), NF))
    f2[:, FI["miss_tee"]] = 1.0
    if end_g and len(gs):
        f2[:, FI["ch_green_end"]] = ctx["ch_g"][gs]
        f2[:, FI["fac_green_end"]] = ctx["fac_g"][gs]
    if len(gs):
        f2[:, FI["green_model"]] = ctx["gmodel"][gs]
    tees = np.r_[ti, -np.ones(len(gs), int)]
    greens = np.r_[gi, gs]
    F = np.vstack([F, f2])
    if allowed is None or allowed[nT, nG]:
        f3 = np.zeros((1, NF))
        f3[0, FI["miss_hole"]] = 1.0
        tees, greens, F = np.r_[tees, -1], np.r_[greens, -1], np.vstack([F, f3])
    return tees.astype(int), greens.astype(int), F


# ----------------------------------------------------------------------------- solve
def solve(ctx, w=None, fixed=None, exclude=None, allowed=None, beam=BEAM, tau=None, p_check=None, keep_top=200,
          polish=3):
    """Beam search over the whole round. -> result dict (routing.route-compatible `holes`), plus `features` (the
    best routing's feature vector), `top` (distinct routings [(cost, [(t, g)] * n)]), `posterior` per hole."""
    if w is None or tau is None or p_check is None:
        w0, t0, p0 = load_weights()
        w = w0 if w is None else w
        tau = t0 if tau is None else tau
        p_check = p0 if p_check is None else p_check
    if not ctx.get("ok"):
        return dict(status="no greens", n_holes=0, holes={}, cost=None, method="routing/2")
    n, nT, nG = ctx["n"], ctx["nT"], ctx["nG"]
    fixed, exclude, allowed = fixed or {}, exclude or {}, allowed or {}
    hyps = [hole_rows(ctx, h, w, fixed=fixed.get(str(h + 1)), exclude=exclude.get(str(h + 1)),
                      allowed=allowed.get(str(h + 1))) for h in range(n)]
    walk, link, far = ctx["walk"], ctx["cart_link"], ctx["cart_far"]
    # line crossings between every candidate pair
    pairs = sorted({(int(t), int(g)) for ht, hg, _ in hyps for t, g in zip(ht, hg) if t >= 0 and g >= 0})
    pidx = {p: i for i, p in enumerate(pairs)}
    hp = [np.array([pidx.get((int(t), int(g)), -1) for t, g in zip(ht, hg)]) for ht, hg, _ in hyps]
    X = R._crossings(np.array([ctx["txy"][p[0]] for p in pairs]).reshape(-1, 2),
                     np.array([ctx["gxy"][p[1]] for p in pairs]).reshape(-1, 2)) if pairs else np.zeros((0, 0), np.int16)
    NP = len(pairs)
    covs = []
    for ht, hg, _ in hyps:
        cv = np.zeros((len(ht), nT))
        for j, (t, g) in enumerate(zip(ht, hg)):
            if t >= 0 and g >= 0:
                cv[j] = _cov(ctx, int(t), int(g))
        covs.append(cv)
    S_cost = np.zeros(1)
    S_f = np.zeros((1, NF))
    S_g = np.zeros((1, nG + 1), bool)
    S_t = np.zeros((1, nT + 1), bool)
    S_c = np.zeros((1, nT))
    S_x = np.zeros((1, NP + 1), np.int16)
    S_last = np.array([-1])
    S_gap = np.array([False])
    S_first = np.array([-1])
    S_hash = np.zeros(1, np.uint64)
    ZG = np.random.default_rng(12345).integers(1, 2 ** 63, size=max(nG, 1), dtype=np.int64).astype(np.uint64)
    back = []
    for h in range(n):
        ht, hg, HF = hyps[h]
        hc = HF @ w
        ns, nr = len(S_cost), len(ht)
        # transition features (states x rows)
        lastok, teeok = S_last >= 0, ht >= 0
        fw = np.zeros((ns, nr))
        fl = np.zeros((ns, nr))
        ff = np.zeros((ns, nr))
        if lastok.any() and teeok.any():
            ix = np.ix_(np.nonzero(lastok)[0], np.nonzero(teeok)[0])
            gl, tt = S_last[lastok], ht[teeok]
            sub = walk[np.ix_(gl, tt)] * np.where(S_gap[lastok], 0.4, 1.0)[:, None]
            fw[ix] = sub
            fl[ix] = link[np.ix_(gl, tt)]
            ff[ix] = far[np.ix_(gl, tt)]
        turn = h == 9 and n >= 18
        # loop closure: green 9 (18 holes) and the last green back to tee 1
        floop = np.zeros((ns, nr))
        if (h == n - 1 or (h == 8 and n >= 18)) and h > 0:
            fok = S_first >= 0
            gok = hg >= 0
            if fok.any() and gok.any():
                floop[np.ix_(np.nonzero(fok)[0], np.nonzero(gok)[0])] = ctx["loopc"][np.ix_(hg[gok], S_first[fok])].T
        cv = covs[h]
        gain = cv.sum(1)[None, :] - (S_c > 0).astype(float) @ cv.T if nT else np.zeros((ns, nr))
        cstart = np.c_[S_c > 0, np.zeros((ns, 1), bool)][:, ht] * teeok[None, :] if nT else np.zeros((ns, nr))
        reuse = S_t[:, ht] & teeok[None, :]
        xl = S_x[:, hp[h]] * (hp[h] >= 0)[None, :]
        tot = (S_cost[:, None] + hc[None, :] + (w[FI["walk_turn"]] if turn else w[FI["walk"]]) * fw
               + w[FI["cart_link"]] * fl + w[FI["cart_far"]] * ff + w[FI["loop"]] * floop - w[FI["cover"]] * gain
               + w[FI["covered_start"]] * cstart + w[FI["reused_tee"]] * reuse + w[FI["cross_lines"]] * xl)
        bad = S_g[:, hg] & (hg >= 0)[None, :]
        tot = np.where(bad, np.inf, tot)
        flat = tot.ravel()
        k = min(len(flat), beam * 4)
        idx = np.argpartition(flat, k - 1)[:k] if k < len(flat) else np.arange(len(flat))
        idx = idx[np.argsort(flat[idx])]
        idx = idx[np.isfinite(flat[idx])]
        if not len(idx):
            return dict(status="infeasible", n_holes=n, holes={}, cost=None, method="routing/2")
        # dedupe on (this green, hole 1's tee, set of used greens) with a 64-bit hash of the green set
        s_i, r_i = np.divmod(idx, nr)
        gnew = hg[r_i]
        hset = S_hash[s_i] + np.where(gnew >= 0, ZG[np.maximum(gnew, 0)], np.uint64(0))
        first = ht[r_i] if h == 0 else S_first[s_i]
        key = hset ^ (gnew.astype(np.int64).astype(np.uint64) * np.uint64(0x9E3779B97F4A7C15)) ^ \
            (first.astype(np.int64).astype(np.uint64) * np.uint64(0xC2B2AE3D27D4EB4F))
        _, fi = np.unique(key, return_index=True)
        fi = np.sort(fi)[:beam]                   # idx is cost-sorted: the first of each key is its cheapest
        keep = list(zip(s_i[fi].tolist(), r_i[fi].tolist()))
        S_hash = hset[fi]
        ss = np.array([s for s, _ in keep])
        rr = np.array([r for _, r in keep])
        S_cost = flat[ss * nr + rr]
        add = HF[rr].copy()
        add[:, FI["walk_turn" if turn else "walk"]] += fw[ss, rr]
        add[:, FI["cart_link"]] += fl[ss, rr]
        add[:, FI["cart_far"]] += ff[ss, rr]
        add[:, FI["loop"]] += floop[ss, rr]
        add[:, FI["cover"]] -= gain[ss, rr] if nT else 0
        add[:, FI["covered_start"]] += cstart[ss, rr] if nT else 0
        add[:, FI["reused_tee"]] += reuse[ss, rr]
        add[:, FI["cross_lines"]] += xl[ss, rr]
        S_f = S_f[ss] + add
        S_g = S_g[ss].copy()
        S_t = S_t[ss].copy()
        S_c = np.maximum(S_c[ss], cv[rr]) if nT else S_c[ss]
        S_x = S_x[ss].copy()
        pk = hp[h][rr]
        okp = pk >= 0
        if okp.any():
            S_x[np.nonzero(okp)[0], :NP] += X[pk[okp]]
        ok = hg[rr] >= 0
        S_g[np.nonzero(ok)[0], hg[rr][ok]] = True
        ok = ht[rr] >= 0
        S_t[np.nonzero(ok)[0], ht[rr][ok]] = True
        S_first = ht[rr] if h == 0 else S_first[ss]
        S_gap = hg[rr] < 0
        S_last = np.where(hg[rr] >= 0, hg[rr], S_last[ss])
        back.append((ss, rr))

    def trace(i):
        seq = []
        for h in range(n - 1, -1, -1):
            ss, rr = back[h]
            seq.append(int(rr[i]))
            i = int(ss[i])
        return seq[::-1]
    m = min(len(S_cost), keep_top)
    seqs = [trace(i) for i in range(m)]
    assigns = [[(int(hyps[h][0][s[h]]), int(hyps[h][1][s[h]])) for h in range(n)] for s in seqs]
    costs = [float(S_cost[i]) for i in range(m)]
    fbest = S_f[0]
    if polish:
        # the beam merges states that differ only in used boxes / coverage / crossings: polish the best few
        # routings with exact-cost local moves (re-pick a hole, swap two holes)
        for i in range(min(polish, m)):
            a2, c2, f2 = local_search(ctx, w, assigns[i], hyps, fixed)
            if c2 < costs[i] - 1e-9:
                assigns.append(a2)
                costs.append(c2)
                if c2 < min(costs[:-1]) - 1e-9:
                    fbest = f2
        order = np.argsort(costs, kind="stable")
        assigns = [assigns[i] for i in order]
        costs = [costs[i] for i in order]
    # distinct routings by (greens, tee complex): several beam states differ only in a box of the same complex
    top, seen = [], set()
    for i, a in enumerate(assigns):
        k = tuple(_hole_key(ctx, t, g) for t, g in a)
        if k in seen:
            continue
        seen.add(k)
        top.append((costs[i], a, k))
    res = _result(ctx, assigns[0], costs[0], np.asarray(fbest), top, tau, p_check, fixed)
    return res


def reject(ctx, t, g, r=45.0):
    """Exclusion entry for a golfer's "no, that line is not hole n": the green with any box within r yds of the
    shown tee (another box of the same complex is the same wrong answer)."""
    if t < 0:
        return (g, None)
    x, y = ctx["txy"][t]
    return ("near", int(g), float(x), float(y), float(r))


def assign_features(ctx, assign, w=None, rows=None):
    """Exact feature vector of a complete routing [(t, g)] - the terms solve() accumulates, in card order.
    rows: {(h, t, g): feature row} cache. -> (features, cost or None when a green is used twice)."""
    n = ctx["n"]
    rows = {} if rows is None else rows
    f = np.zeros(NF)
    walk, link, far = ctx["walk"], ctx["cart_link"], ctx["cart_far"]
    nT = ctx["nT"]
    S_c = np.zeros(nT)
    used_t, used_g = set(), set()
    last, gap, first = -1, False, -1
    segs = []
    for h, (t, g) in enumerate(assign):
        if g >= 0:
            if g in used_g:
                return f, None
            used_g.add(g)
        key = (h, t, g)
        r = rows.get(key)
        if r is None:
            r = hole_rows(ctx, h, None, fixed=(t, g))[2][0]
            rows[key] = r
        f += r
        if h == 0:
            first = t
        if last >= 0 and t >= 0:
            turn = h == 9 and n >= 18
            f[FI["walk_turn" if turn else "walk"]] += walk[last, t] * (0.4 if gap else 1.0)
            f[FI["cart_link"]] += link[last, t]
            f[FI["cart_far"]] += far[last, t]
        if (h == n - 1 or (h == 8 and n >= 18)) and h > 0 and first >= 0 and g >= 0:
            f[FI["loop"]] += ctx["loopc"][g, first]
        if t >= 0 and nT:
            f[FI["covered_start"]] += float(S_c[t] > 0)
        if t >= 0 and g >= 0 and nT:
            cv = _cov(ctx, t, g)
            f[FI["cover"]] -= cv.sum() - float((S_c > 0) @ cv)
            S_c = np.maximum(S_c, cv)
        if t >= 0:
            f[FI["reused_tee"]] += t in used_t
            used_t.add(t)
        if t >= 0 and g >= 0:
            segs.append((ctx["txy"][t], ctx["gxy"][g]))
        gap = g < 0
        if g >= 0:
            last = g
    if len(segs) > 1:
        X = R._crossings(np.array([a for a, _ in segs]), np.array([b for _, b in segs]))
        f[FI["cross_lines"]] += float(np.triu(X, 1).sum())
    return f, (float(f @ w) if w is not None else 0.0)


def local_search(ctx, w, assign, hyps, fixed, max_rounds=4):
    """First-improvement local search on the exact cost: per hole, every hypothesis row whose green is free;
    then every swap of two holes' (tee, green). -> (assign, cost, features)."""
    rows = ctx.setdefault("_rows_cache", {})
    if len(rows) > 200_000:
        rows.clear()
    a = list(assign)
    f, c = assign_features(ctx, a, w, rows)
    if c is None:
        return a, np.inf, f
    n = len(a)
    valid = [set(zip(map(int, ht), map(int, hg))) for ht, hg, _ in hyps]
    for _ in range(max_rounds):
        improved = False
        for h in range(n):
            if str(h + 1) in fixed:
                continue
            ht, hg, _ = hyps[h]
            usedg = {g for j, (_, g) in enumerate(a) if j != h and g >= 0}
            for t, g in zip(ht, hg):
                t, g = int(t), int(g)
                if (t, g) == a[h] or (g >= 0 and g in usedg):
                    continue
                b = list(a)
                b[h] = (t, g)
                f2, c2 = assign_features(ctx, b, w, rows)
                if c2 is not None and c2 < c - 1e-9:
                    a, f, c, improved = b, f2, c2, True
                    usedg = {gg for j, (_, gg) in enumerate(a) if j != h and gg >= 0}
        for h1 in range(n):
            for h2 in range(h1 + 1, n):
                if str(h1 + 1) in fixed or str(h2 + 1) in fixed:
                    continue
                if a[h2] not in valid[h1] or a[h1] not in valid[h2]:
                    continue
                b = list(a)
                b[h1], b[h2] = a[h2], a[h1]
                f2, c2 = assign_features(ctx, b, w, rows)
                if c2 is not None and c2 < c - 1e-9:
                    a, f, c, improved = b, f2, c2, True
        if not improved:
            break
    return a, c, f


def _hole_key(ctx, t, g):
    """A hole's identity for the posterior: its green and (coarsely) its tee complex - boxes within 40 yds of
    the chosen one's position along the line count as the same answer (scoring tolerance)."""
    if t < 0:
        return (g, None)
    x, y = ctx["txy"][t]
    return (g, int(round(x / 40.0)), int(round(y / 40.0)))


def posterior(ctx, top, tau):
    """Per hole: {hole key: probability} from the distinct top routings, Boltzmann at temperature tau."""
    if not top:
        return []
    c = np.array([t[0] for t in top])
    p = np.exp(-(c - c.min()) / max(tau, 1e-6))
    p /= p.sum()
    n = len(top[0][2])
    out = []
    for h in range(n):
        d = {}
        for pi, t in zip(p, top):
            d[t[2][h]] = d.get(t[2][h], 0.0) + float(pi)
        out.append(d)
    return out, p


def _result(ctx, assign, cost, fvec, top, tau, p_check, fixed):
    G, T, n = ctx["G"], ctx["T"], ctx["n"]
    D, W = ctx["D"], ctx["W"]
    post, ptop = posterior(ctx, top, tau)
    holes = {}
    for h, (tk, gk) in enumerate(assign):
        ref = str(h + 1)
        key = _hole_key(ctx, tk, gk)
        pk = post[h].get(key, 0.0)
        pg = sum(v for k2, v in post[h].items() if k2[0] == gk)
        ent = dict(ref=ref, par=ctx["pars"][h] if ctx["pars"] else None,
                   card_yards=ctx["yards"][h] if ctx["yards"] else [], p_hole=round(pk, 3), p_green=round(pg, 3),
                   fixed=ref in fixed, t_idx=tk, g_idx=gk)
        if gk >= 0:
            ent.update(green_id=G[gk]["id"], green_ll=list(G[gk]["ll"]), green_src=G[gk]["src"])
        if tk >= 0:
            ent.update(tee_id=T[tk]["id"], tee_ll=list(T[tk]["ll"]), tee_src=T[tk]["src"])
        if gk >= 0 and tk >= 0:
            ent["straight_yd"] = round(float(D[tk, gk]), 1)
            onh = np.nonzero(R._on_hole(ctx["txy"], ctx["txy"][tk], ctx["gxy"][gk], ctx["tee_axes"]))[0]
            bk = int(onh[np.argmax(D[onh, gk])]) if len(onh) else tk
            ent.update(back_tee_ll=list(T[bk]["ll"]), back_yd=round(float(D[bk, gk]), 1), boxes_on_hole=int(len(onh)))
        if h > 0:
            pg_ = assign[h - 1][1]
            if pg_ >= 0 and tk >= 0:
                ent["walk_from_prev_green_yd"] = round(float(W[pg_, tk]), 1)
        flags = []
        if gk < 0:
            flags.append("no green found")
        if tk < 0:
            flags.append("no tee found")
        if pk < p_check and ref not in fixed:
            flags.append(f"ambiguous ({pk:.0%} of the posterior)")
        ent["flags"] = flags
        ent["status"] = "ok" if (not flags or ref in fixed) else "check"
        holes[ref] = ent
    used = {g for _, g in assign}
    return dict(method="routing/2", status="ok", n_holes=n, card=bool(ctx["yards"] and any(ctx["yards"])),
                cost=round(cost, 3), holes=holes, features=fvec.tolist(),
                n_check=sum(1 for v in holes.values() if v["status"] != "ok"),
                unused_greens=[G[k]["id"] for k in range(ctx["nG"]) if k not in used],
                clubhouse=list(ctx["clubhouse"]) if ctx.get("clubhouse") else None,
                top=[(round(c, 3), a) for c, a, _ in top[:50]], top_p=[round(float(x), 4) for x in ptop[:50]],
                posterior=[{repr(k): round(v, 4) for k, v in sorted(d.items(), key=lambda kv: -kv[1])[:6]} for d in post],
                inputs=dict(greens=ctx["nG"], tees=ctx["nT"], facility_points=ctx["n_fac"],
                            cart_nodes=ctx["n_cart_nodes"], fairways=len(ctx["inp"].get("fairways", []))))


def features_of(ctx, assign):
    """Feature vector of a complete routing [(t, g)] (the same terms solve() accumulates)."""
    res = solve(ctx, w=np.ones(NF), fixed={str(h + 1): a for h, a in enumerate(assign)}, beam=1, tau=1.0, p_check=0)
    return np.array(res["features"])


# ----------------------------------------------------------------------------- facility split
def components(ctx, gap=SPLIT_GAP):
    """Single-linkage clusters of greens (+ the boxes nearest each) with link distance `gap` yds."""
    from scipy.sparse.csgraph import connected_components
    gxy = ctx["gxy"]
    GG = np.hypot(gxy[:, None, 0] - gxy[None, :, 0], gxy[:, None, 1] - gxy[None, :, 1])
    nc, lab = connected_components(GG < gap, directed=False)
    return nc, lab


def route(inp, card=None, fc=None, boundary=None, w=None, fixed=None, exclude=None, split=True, **kw):
    """context + solve; with many more greens than card holes, also try the facility's clusters and keep the
    cheapest routing per hole (`facility_split`)."""
    ctx = context(inp, card, fc=fc, boundary=boundary)
    res = solve(ctx, w=w, fixed=fixed, exclude=exclude, **kw)
    res["context"] = ctx
    if not split or not ctx.get("ok") or fixed or ctx["nG"] < 1.5 * ctx["n"] + 4:
        return res
    nc, lab = components(ctx)
    sizes = np.bincount(lab)
    G, T = ctx["G"], ctx["T"]

    def score_of(r, n_greens):
        # a course uses (almost) every green of its own area: unused greens of the candidate set count against it
        return r["cost"] + UNUSED_GREEN_W * (n_greens - (r["n_holes"] - sum(1 for h in r["holes"].values()
                                                                             if h.get("g_idx", -1) < 0)))
    best, best_s = res, score_of(res, ctx["nG"])
    cands = [[c] for c in range(nc) if sizes[c] >= 0.75 * ctx["n"]]
    big = [c for c in range(nc) if sizes[c] >= 3]
    cands += [[a, b] for i, a in enumerate(big) for b in big[i + 1:] if 0.75 * ctx["n"] <= sizes[a] + sizes[b] <= 1.6 * ctx["n"] + 4]
    for cs in cands[:8]:
        gsel = [i for i in range(ctx["nG"]) if lab[i] in cs]
        if len(gsel) == ctx["nG"]:
            continue
        gx = ctx["gxy"][gsel]
        tsel = [j for j in range(ctx["nT"]) if np.hypot(*(gx - ctx["txy"][j]).T).min() < 700]
        sub = context(dict(inp, greens=[G[i] for i in gsel], tees=[T[j] for j in tsel]), card, fc=fc, boundary=boundary)
        r2 = solve(sub, w=w, **kw)
        if r2.get("cost") is None:
            continue
        s2 = score_of(r2, len(gsel))
        if s2 < best_s - 0.5:
            r2["context"] = sub
            r2["facility_split"] = dict(clusters=len(cs), greens=len(gsel), of=ctx["nG"])
            best, best_s = r2, s2
    return best


def strip(res):
    """The result without the context / bulky posterior (for JSON)."""
    return {k: v for k, v in res.items() if k not in ("context",)}
