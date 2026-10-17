"""Course structure from first principles: every hole (tee complex -> corridor -> green) and the playing order.

    from scene import scene_from_osm
    from solver import solve
    res = solve(scene, card=None)          # card (scorecard/1) is an optional prior; works without one

Model (all terms are log-likelihoods, fitted on the dev courses only; see REPORT.md):

1. Hole hypotheses. For every green g and every tee box t 70-700 yds away, the hole (t -> g) explains the tee boxes
   in its corridor (from 12 % behind t to 62 % of the way, <= 22 yds off the line); its back tee is the farthest of
   them. Its formation score `form(g, t)` (logistic model, `FORM_W`) uses: the length likelihood under a par 3/4/5
   mixture, tee-box long axes vs the line, the share of the line on fairway, a fairway whose two ends sit at the
   tee and the green (dog-legs), the line crossing another green, and the number of boxes explained.
2. Sequence. A round is a path through N of the M greens (N in 9 / 18 / 27 / 36). Moving from green i to the hole
   (t, j) costs the walk green i -> nearest box of the hole (log-normal, median ~65 yds, with a broad tail); the
   hole formation is summed out (soft-min over j's tee hypotheses). Anchors: tee 1 and green N near the clubhouse
   H; with 18 holes also green 9 and tee 10 (returning nines), the 9 -> 10 walk then goes through H. H is latent:
   tagged / detected clubhouse candidates, car-park buildings and "hubs" where greens and tees meet, each with a
   prior, marginalised.
3. Inference. Exact forward-backward over subsets (Held-Karp in log space; one BLAS matmul per layer) gives the
   partition function, the MAP route (Viterbi) and exact marginals P(green j is hole k). Per hole the confidence is
   that marginal times the posterior of its tee hypothesis. Practice greens are the greens the route skips (each
   green carries a "not a hole" score).
4. Par from the corridor length (par-mixture posterior with a 70-72 total / ~4 par-3 prior); hole numbers from the
   route; direction of play from tee -> green.
A card (pars / yards per hole) adds a position term: the hole at position k vs card hole k.
"""
from __future__ import annotations

import math
from itertools import combinations

import numpy as np

try:
    from shapely import contains_xy, prepare
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
except Exception:                                                   # noqa: BLE001
    Polygon = None

# ----------------------------------------------------------------------------- parameters (fitted on dev)
PAR_MU = {3: 168.0, 4: 375.0, 5: 505.0}
PAR_SD = {3: 35.0, 4: 48.0, 5: 45.0}
PAR_PI = {3: 0.22, 4: 0.56, 5: 0.22}
L_MIN, L_MAX = 70.0, 700.0
WALK_MED, WALK_SIG, WALK_TAIL = 62.0, 0.55, 0.06      # green -> next tee: log-normal + tail (uniform to 800 yds)
CH_MED, CH_SIG, CH_TAIL = 70.0, 0.75, 0.15            # anchor (tee 1, green 9 / 18, tee 10) to the clubhouse
CORR_BACK, CORR_FWD, CORR_PERP = 0.12, 0.62, 22.0
TOPK = 8
NOT_HOLE_BASE = 5.0                                   # cost of declaring a green "not a hole" (practice)
FORM_W = dict(length=1.0, align=1.0, fw_cov=2.5, fw_end=2.0, cross_green=3.0, boxes=0.35, bias=0.0,
              fw_missing=0.0, far_box=0.7)
TEMP = 1.0                                            # posterior temperature (calibrated on dev)


def _ln_lognorm(d, med, sig, tail, tmax=800.0):
    d = np.maximum(np.asarray(d, float), 1.0)
    core = np.exp(-0.5 * ((np.log(d) - math.log(med)) / sig) ** 2) / (d * sig * math.sqrt(2 * math.pi))
    return np.log((1 - tail) * core + tail / tmax)


def length_loglik(L):
    """log p(L | hole) - log p(L | random pair) (uniform over L_MIN..L_MAX) and the par posterior."""
    L = np.asarray(L, float)
    comps = np.stack([PAR_PI[p] * np.exp(-0.5 * ((L - PAR_MU[p]) / PAR_SD[p]) ** 2) / (PAR_SD[p] * math.sqrt(2 * math.pi))
                      for p in (3, 4, 5)])
    dens = comps.sum(0) + 0.02 / (L_MAX - L_MIN)
    return np.log(dens * (L_MAX - L_MIN)), comps / np.maximum(comps.sum(0), 1e-300)


def walk_ll(d):
    return _ln_lognorm(d, WALK_MED, WALK_SIG, WALK_TAIL)


def anchor_ll(d):
    return _ln_lognorm(d, CH_MED, CH_SIG, CH_TAIL, 1500.0)


def _angdiff(a, b):
    """Undirected angle difference in [0, pi/2]."""
    return abs((a - b + math.pi / 2) % math.pi - math.pi / 2)


# ----------------------------------------------------------------------------- geometry prep
class Geo:
    def __init__(self, sc):
        self.sc = sc
        self.G = np.array([g["c"] for g in sc.greens], float).reshape(-1, 2)
        self.T = np.array([t["c"] for t in sc.tees], float).reshape(-1, 2)
        self.fw = None
        self.gr = []
        self.fw_ends = []
        if Polygon is not None:
            polys = []
            for f in sc.fairways:
                if f.get("ring") is not None and len(f["ring"]) >= 4:
                    p = Polygon(f["ring"]).buffer(0)
                    if p.area > 50:
                        polys.append(p)
                        self.fw_ends.append(_poly_ends(f["ring"]))
                elif f.get("line") is not None:
                    ln = np.asarray(f["line"])
                    from shapely.geometry import LineString
                    polys.append(LineString(ln).buffer(18))
                    self.fw_ends.append((ln[0], ln[-1]))
            if polys:
                self.fw = unary_union(polys).buffer(8)
                prepare(self.fw)
            for g in sc.greens:
                if g.get("ring") is not None and len(g["ring"]) >= 4:
                    p = Polygon(g["ring"]).buffer(4)
                else:
                    from shapely.geometry import Point
                    p = Point(*g["c"]).buffer(max(8.0, math.sqrt(g.get("area", 400) / math.pi)))
                prepare(p)
                self.gr.append(p)
        self.has_fw = self.fw is not None and len(sc.fairways) >= 5
        self.fw_ends = np.array(self.fw_ends, float).reshape(-1, 2, 2)

    def on_fairway(self, xy):
        if self.fw is None:
            return np.zeros(len(xy), bool)
        return contains_xy(self.fw, xy[:, 0], xy[:, 1])


def _poly_ends(ring):
    """The two extreme points of a polygon along its long axis (approximate centreline ends)."""
    r = np.asarray(ring, float)
    c = r.mean(0)
    u, s, vt = np.linalg.svd(r - c, full_matrices=False)
    ax = vt[0]
    pr = (r - c) @ ax
    i, j = int(np.argmin(pr)), int(np.argmax(pr))
    # pull the ends a little inside (centreline, not the tip vertex)
    return c + (r[i] - c) * 0.85, c + (r[j] - c) * 0.85


# ----------------------------------------------------------------------------- hole hypotheses
def hypotheses(sc, geo=None, topk=TOPK, w=None):
    """Per green: up to `topk` hole hypotheses (dicts) sorted by formation log-score (higher is better)."""
    w = dict(FORM_W, **(w or {}))
    geo = geo or Geo(sc)
    G, T = geo.G, geo.T
    nG, nT = len(G), len(T)
    out = []
    if nT == 0:
        return [[] for _ in range(nG)], geo
    axes = np.array([t["axis"] if t.get("axis") is not None else np.nan for t in sc.tees])
    elong = np.array([t.get("elong", 1.0) or 1.0 for t in sc.tees])
    tconf = np.array([t.get("conf", 1.0) for t in sc.tees])
    s_line = np.linspace(0.25, 0.85, 13)
    s_cross = np.linspace(0.08, 0.9, 24)
    for gi in range(nG):
        g = G[gi]
        d = np.hypot(*(T - g).T)
        cand = np.nonzero((d >= L_MIN) & (d <= L_MAX))[0]
        hy = {}
        for ti in cand:
            t = T[ti]
            v = g - t
            D = float(np.hypot(*v))
            u = v / D
            rel = T - t
            s = rel @ u / D
            perp = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
            on = np.nonzero((s >= -CORR_BACK) & (s <= CORR_FWD) & (perp <= CORR_PERP))[0]
            back = int(on[np.argmin(s[on])])
            if back in hy and hy[back]["ti"] != ti:
                continue
            hy[back] = dict(gi=gi, ti=int(ti), back=back, boxes=on, D=D)
        res = []
        for back, h in hy.items():
            t = T[h["back"]]
            v = g - t
            D = float(np.hypot(*v))
            if D < L_MIN:
                continue
            u = v / D
            ang = math.atan2(u[1], u[0])
            # tee-box alignment: elongated boxes point along the line of play
            al = 0.0
            for b in h["boxes"]:
                if not np.isnan(axes[b]) and elong[b] > 1.3:
                    dd = _angdiff(axes[b], ang)
                    pc = 0.85 * math.exp(-0.5 * (dd / math.radians(9)) ** 2) / (math.radians(9) * math.sqrt(math.pi / 2)) \
                        + 0.15 / (math.pi / 2)
                    lr = math.log(pc * (math.pi / 2))
                    al += lr * min(1.0, (elong[b] - 1.3) / 0.7) * tconf[b]
            al = max(-6.0, min(4.0, al))
            ll_len, ppar = length_loglik(np.array([D]))
            pts = t + np.outer(s_line, v)
            cov = float(geo.on_fairway(pts).mean()) if geo.has_fw else 0.0
            p5 = float(ppar[1, 0] + ppar[2, 0])
            # fairway whose ends sit at the landing area / approach of this hole (dog-legs keep their ends)
            fe = 0.0
            if geo.has_fw and len(geo.fw_ends):
                e = geo.fw_ends
                da = np.minimum(np.hypot(*(e[:, 0] - t).T) + np.hypot(*(e[:, 1] - g).T),
                                np.hypot(*(e[:, 1] - t).T) + np.hypot(*(e[:, 0] - g).T))
                # a fairway runs from ~60-250 yds off the tee to ~0-60 yds short of the green
                # -> its ends' summed distance to (tee, green) is ~ 0.3 D; anything near D is unrelated
                fe = float(max(0.0, 1.0 - (da.min() / D - 0.25) / 0.45))
            # the line crosses another green
            xs = t + np.outer(s_cross, v)
            cg = 0
            for gj, poly in enumerate(geo.gr):
                if gj != gi and np.hypot(*(G[gj] - (t + g) / 2)) < D / 2 + 30:
                    if contains_xy(poly, xs[:, 0], xs[:, 1]).any():
                        cg += 1
            # tee boxes far past the corridor's tee end but on the line (another hole's tees in play)
            rel = T - t
            s2 = rel @ u / D
            perp2 = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
            far_box = int(((s2 > 0.68) & (s2 < 0.9) & (perp2 < 12)).sum())
            nb = len(h["boxes"])
            f = dict(length=float(ll_len[0]), align=al,
                     fw_cov=(cov - 0.45) * p5 if geo.has_fw else 0.0,
                     fw_end=(fe - 0.4) * p5 if geo.has_fw else 0.0,
                     cross_green=-float(cg), boxes=math.log(nb), far_box=-float(far_box))
            score = sum(w[k] * f[k] for k in f) + w["bias"]
            res.append(dict(gi=gi, back=h["back"], boxes=[int(b) for b in h["boxes"]], D=D, score=score, feat=f,
                            ppar=[float(ppar[i, 0]) for i in range(3)]))
        res.sort(key=lambda r: -r["score"])
        out.append(res[:topk])
    return out, geo


# ----------------------------------------------------------------------------- clubhouse candidates
def hub_candidates(sc, geo, hyps, k=4):
    """Points where greens and hole starts meet (the clubhouse of returning nines: greens 9 / 18, tees 1 / 10)."""
    pts = []
    starts = np.array([sc.tees[h["back"]]["c"] for hs in hyps for h in hs[:2]]).reshape(-1, 2) if geo.T.size else np.zeros((0, 2))
    G = geo.G
    for p in list(G) + list(starts):
        ng = int((np.hypot(*(G - p).T) < 140).sum())
        nt = len({tuple(np.round(q)) for q in starts[np.hypot(*(starts - p).T) < 140]}) if len(starts) else 0
        pts.append((min(ng, 3) + min(nt, 3), p))
    pts.sort(key=lambda r: -r[0])
    out = []
    for sc_, p in pts:
        if any(np.hypot(*(p - q["c"])) < 150 for q in out):
            continue
        out.append(dict(c=np.asarray(p, float), w=0.05 * sc_ / 6, how="hub"))
        if len(out) >= k:
            break
    return out


# ----------------------------------------------------------------------------- the DP
def _popcount_layers(M, N):
    masks = np.arange(1 << M, dtype=np.int64)
    pc = np.zeros(1 << M, np.int8)
    for b in range(M):
        pc += ((masks >> b) & 1).astype(np.int8)
    return [np.nonzero(pc == k)[0] for k in range(N + 1)]


def _lse(a, axis=None):
    m = np.max(a, axis=axis, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)
    r = np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True)) + m
    return np.squeeze(r, axis=axis) if axis is not None else float(r.ravel()[0])


def route_dp(trans, start, end, N, turn=None, pos=None, layers=None, viterbi=True):
    """Soft and hard Held-Karp over paths of N distinct nodes out of M.

    trans[i, j]  log-weight of moving from node i to node j        (M x M, -inf allowed)
    start[j]     log-weight of j as the first node;  end[i] of i as the last
    turn[i, j]   replaces trans at the transition from position 9 to 10 (index 8 -> 9) when given
    pos[j, k]    log-weight of node j at position k (0-based), e.g. a card prior
    -> dict(logZ, best (list of nodes), best_score, marg (M x N): P(node j at position k))."""
    M = trans.shape[0]
    layers = layers or _popcount_layers(M, N)
    NEG = -1e30
    alpha = np.full((1 << M, M), NEG, np.float32)
    for j in range(M):
        alpha[1 << j, j] = start[j] + (pos[j, 0] if pos is not None else 0.0)
    vit = alpha.copy() if viterbi else None
    E = [None] * N
    for k in range(1, N):
        tr = turn if (turn is not None and k == 9) else trans
        idx = layers[k]
        A = alpha[idx]
        am = A.max(1, keepdims=True)
        tm = tr.max(0, keepdims=True)
        tm = np.where(np.isfinite(tm) & (tm > -1e29), tm, 0.0)
        eT = np.exp(np.clip(tr - tm, -700, 0))
        B = np.log(np.maximum(np.exp(A - am) @ eT, 1e-300)) + am + tm
        bit = ((idx[:, None] >> np.arange(M)[None, :]) & 1).astype(bool)
        B = np.where(bit, NEG, B)
        if pos is not None:
            B = B + pos[:, k][None, :]
        new = idx[:, None] | (1 << np.arange(M))[None, :]
        rows, cols = np.nonzero(~bit)
        alpha[new[rows, cols], cols] = B[rows, cols]
        if viterbi:
            V = vit[idx]
            best = np.full((len(idx), M), NEG)
            for i in range(M):
                cand = V[:, i:i + 1] + tr[i][None, :]
                best = np.maximum(best, cand)
            best = np.where(bit, NEG, best)
            if pos is not None:
                best = best + pos[:, k][None, :]
            vit[new[rows, cols], cols] = best[rows, cols]
    last = layers[N]
    fin = alpha[last] + end[None, :]
    logZ = _lse(fin.ravel())
    # backward
    beta = np.full((1 << M, M), NEG, np.float32)
    beta[last] = np.broadcast_to(end[None, :], (len(last), M))
    for k in range(N - 1, 0, -1):
        tr = turn if (turn is not None and k == 9) else trans
        idx = layers[k]
        bit = ((idx[:, None] >> np.arange(M)[None, :]) & 1).astype(bool)
        new = idx[:, None] | (1 << np.arange(M))[None, :]
        nb = np.where(bit, NEG, beta[np.where(bit, idx[:, None], new), np.arange(M)[None, :]])
        if pos is not None:
            nb = nb + pos[:, k][None, :]
        nm = nb.max(1, keepdims=True)
        tm = tr.max(1, keepdims=True)
        tm = np.where(np.isfinite(tm) & (tm > -1e29), tm, 0.0)
        eT = np.exp(np.clip(tr - tm, -700, 0))
        Bk = np.log(np.maximum(np.exp(nb - nm) @ eT.T, 1e-300)) + nm + tm.T
        beta[idx] = np.where(bit, Bk, NEG)
    marg = np.zeros((M, N))
    for k in range(N):
        idx = layers[k + 1]
        lp = alpha[idx] + beta[idx] - logZ
        marg[:, k] = np.exp(np.clip(lp, -700, 0)).sum(0)
    out = dict(logZ=float(logZ), marg=marg)
    if viterbi:
        fin_v = vit[last] + end[None, :]
        r, c = np.unravel_index(int(np.argmax(fin_v)), fin_v.shape)
        mask, j = int(last[r]), int(c)
        seq = [j]
        score = float(fin_v[r, c])
        for k in range(N - 1, 0, -1):
            tr = turn if (turn is not None and k == 9) else trans
            prev = mask & ~(1 << j)
            cand = vit[prev] + tr[:, j]
            cand[[i for i in range(M) if not (prev >> i) & 1]] = NEG
            i = int(np.argmax(cand))
            seq.append(i)
            mask, j = prev, i
        out.update(best=seq[::-1], best_score=score)
    return out


# ----------------------------------------------------------------------------- the solver
def n_holes_guess(sc, hyps):
    """9 / 18 / 27 / 36 from the greens that have at least one decent tee hypothesis."""
    good = sum(1 for hs in hyps if hs and hs[0]["score"] > -2.0)
    allg = len(hyps)
    for n in (36, 27, 18, 9):
        if good >= n - 1 or allg >= n + (1 if n >= 18 else 0):
            if good >= n - 2:
                return n
    return 9 if good >= 6 else max(1, good)


def card_info(card):
    """(pars, yards) per hole from a scorecard/1 dict (yards = the longest tee set), or (None, None)."""
    if not card:
        return None, None
    pars = card.get("par") or card.get("pars")
    ys = None
    ts = card.get("tee_sets") or {}
    best = None
    for name, t in ts.items():
        y = t.get("yards") if isinstance(t, dict) else t
        if y and (best is None or sum(v or 0 for v in y) > sum(v or 0 for v in best)):
            best = y
    ys = best or card.get("yards")
    return pars, ys


def solve(sc, card=None, n_holes=None, use_paths=True, use_clubhouse=True, temp=None, form_w=None, topk=TOPK,
          max_greens=20, return_debug=False):
    temp = temp or TEMP
    hyps, geo = hypotheses(sc, topk=topk, w=form_w)
    pars, yards = card_info(card)
    N = n_holes or (len(pars) if pars else n_holes_guess(sc, hyps))
    nG = len(sc.greens)
    if nG == 0:
        return dict(schema="course_structure/1", status="no_greens", holes=[], n_holes=N)
    T = geo.T
    G = geo.G
    # "not a hole" score per green: practice greens are small, close to the clubhouse, without a good hypothesis
    best_form = np.array([hs[0]["score"] if hs else -20.0 for hs in hyps])
    gconf = np.array([g.get("conf", 1.0) for g in sc.greens])
    not_hole = NOT_HOLE_BASE + 0.0 * best_form + np.log(np.maximum(gconf, 0.05))
    # pick the greens the route may use
    order = np.argsort(-(best_form - not_hole + 3 * gconf))
    M = min(nG, max(N, min(max_greens, N + 3)))
    if N > 22:
        M = min(nG, N + 2)
    keep = sorted(order[:M].tolist())
    if N > 22:
        return _solve_large(sc, hyps, geo, keep, N, pars, yards, temp, use_clubhouse, use_paths)
    # hole-level matrices over the kept greens
    hk = [hyps[g] for g in keep]
    walkd = []                                            # walkd[a][b][h] = green a -> boxes of hyp h of green b
    for a, ga in enumerate(keep):
        row = []
        for b, gb in enumerate(keep):
            row.append(np.array([min(np.hypot(*(T[h["boxes"]] - G[ga]).T)) for h in hk[b]]) if hk[b] else np.zeros(0))
        walkd.append(row)
    form = [np.array([h["score"] for h in hs]) / temp for hs in hk]
    Mk = len(keep)
    NEG = -1e30
    trans = np.full((Mk, Mk), NEG)
    for a in range(Mk):
        for b in range(Mk):
            if a == b or not len(form[b]):
                continue
            trans[a, b] = _lse(form[b] + walk_ll(walkd[a][b]) / temp)
    # the green of node b also stops being "not a hole"
    nh = np.array([not_hole[g] for g in keep]) / temp
    trans = trans - nh[None, :]
    # clubhouse candidates (latent)
    Hc = list(sc.clubhouse) if use_clubhouse else []
    Hc = Hc + hub_candidates(sc, geo, hyps)
    wsum = sum(h["w"] for h in Hc)
    runs = []
    layers = _popcount_layers(Mk, N)
    pos = None
    if pars or yards:
        pos = _card_pos(hk, pars, yards, N) / temp
    for H in Hc:
        c = H["c"]
        st = np.array([_lse(form[b] + anchor_ll([min(np.hypot(*(T[h["boxes"]] - c).T)) for h in hk[b]]) / temp)
                       if len(form[b]) else NEG for b in range(Mk)]) - nh
        en = anchor_ll(np.hypot(*(G[keep] - c).T)) / temp
        turn = None
        if N == 18:
            g9 = anchor_ll(np.hypot(*(G[keep] - c).T)) / temp
            turn = np.full((Mk, Mk), NEG)
            for a in range(Mk):
                for b in range(Mk):
                    if a == b or not len(form[b]):
                        continue
                    d10 = np.array([min(np.hypot(*(T[h["boxes"]] - c).T)) for h in hk[b]])
                    via = g9[a] + anchor_ll(d10) / temp
                    direct = walk_ll(walkd[a][b]) / temp + math.log(0.35)
                    turn[a, b] = _lse(form[b] + np.logaddexp(via + math.log(0.65), direct))
            turn = turn - nh[None, :]
        r = route_dp(trans, st, en, N, turn=turn, pos=pos, layers=layers)
        r["H"] = H
        r["logw"] = r["logZ"] + math.log(H["w"] / wsum)
        runs.append(r)
    lw = np.array([r["logw"] for r in runs])
    pw = np.exp(lw - _lse(lw))
    marg = sum(p * r["marg"] for p, r in zip(pw, runs))
    bestrun = runs[int(np.argmax([r["best_score"] + math.log(r["H"]["w"] / wsum) for r in runs]))]
    seq = bestrun["best"]
    return _assemble(sc, geo, hyps, keep, seq, marg, bestrun, pw, runs, N, pars, yards, walkd, form, temp,
                     return_debug)


def _card_pos(hk, pars, yards, N):
    """pos[j, k]: log-likelihood ratio of node j's best hypotheses being card hole k (length vs yards, par)."""
    Mk = len(hk)
    pos = np.zeros((Mk, N))
    for j, hs in enumerate(hk):
        if not hs:
            continue
        D = np.array([h["D"] for h in hs])
        fs = np.array([h["score"] for h in hs])
        wts = np.exp(fs - fs.max())
        wts /= wts.sum()
        for k in range(N):
            ll = np.zeros(len(hs))
            if yards and k < len(yards) and yards[k]:
                Y = float(yards[k])
                sd = 0.06 * Y + 12
                # straight line is shorter than the measured line on dog-legs
                z = (D - Y) / sd if True else 0
                z = np.where(D < Y, (D - Y) / (sd * 1.8), z)
                ll += -0.5 * z ** 2 - (length_loglik(D)[0])
            elif pars and k < len(pars) and pars[k]:
                p = int(pars[k])
                pp = length_loglik(D)[1]
                ll += np.log(np.maximum(pp[min(max(p, 3), 5) - 3], 1e-4) / PAR_PI.get(min(max(p, 3), 5), 0.3))
            pos[j, k] = _lse(np.log(np.maximum(wts, 1e-300)) + ll)
    return np.maximum(pos, -25.0)


def _assemble(sc, geo, hyps, keep, seq, marg, bestrun, pw, runs, N, pars, yards, walkd, form, temp, debug):
    T, G = geo.T, geo.G
    holes = []
    for k, node in enumerate(seq):
        gi = keep[node]
        hs = hyps[gi]
        # the hole's tee hypothesis given the previous green (posterior over hypotheses)
        lp = form[node].copy()
        if k > 0:
            lp = lp + walk_ll(walkd[seq[k - 1]][node]) / temp
        else:
            c = bestrun["H"]["c"]
            lp = lp + anchor_ll([min(np.hypot(*(T[h["boxes"]] - c).T)) for h in hs]) / temp
        ph = np.exp(lp - _lse(lp))
        hi = int(np.argmax(ph))
        h = hs[hi]
        back = T[h["back"]]
        p_num = float(marg[node, k])
        ppar = np.array(h["ppar"])
        holes.append(dict(number=k + 1, green=sc.greens[gi]["id"], green_xy=G[gi], tee=sc.tees[h["back"]]["id"],
                          tee_xy=back, boxes=[sc.tees[b]["id"] for b in h["boxes"]], length_yd=round(h["D"], 1),
                          p_par=[round(float(x), 3) for x in ppar], p_number=round(p_num, 3),
                          p_tee=round(float(ph[hi]), 3), confidence=round(p_num * float(ph[hi]), 3),
                          walk_in_yd=round(float(walkd[seq[k - 1]][node][hi]), 1) if k > 0 else None,
                          form_score=round(h["score"], 2), feat={a: round(b, 2) for a, b in h["feat"].items()}))
    pars_inf = infer_pars([h["p_par"] for h in holes], N)
    for h, p in zip(holes, pars_inf):
        h["par"] = p
    used = {keep[n] for n in seq}
    practice = [sc.greens[i]["id"] for i in range(len(sc.greens)) if i not in used]
    # nines swap: probability mass of the other nine's assignment
    out = dict(schema="course_structure/1", status="ok", n_holes=N, holes=holes, practice_greens=practice,
               clubhouse=dict(xy=bestrun["H"]["c"], how=bestrun["H"]["how"], p=round(float(pw.max()), 3)),
               total_par=int(sum(pars_inf)), card_used=bool(pars or yards),
               p_route=round(float(np.exp(bestrun["best_score"] - bestrun["logZ"])), 4))
    if debug:
        out["debug"] = dict(marg=marg, keep=keep, runs=[(r["H"]["how"], r["logw"]) for r in runs])
    return out


def infer_pars(pp, N):
    """Par per hole: the par posteriors with a prior on the number of par 3s / 5s (~N/4.5 each) and total par
    (70-72 for 18): a small DP over (count of 3s, count of 5s)."""
    n = len(pp)
    if n == 0:
        return []
    lp = np.log(np.maximum(np.array(pp), 1e-6))            # n x 3
    best = None
    exp3 = N * 4.2 / 18
    exp5 = N * 3.8 / 18
    # enumerate counts (n3, n5); for each, the best assignment is a greedy on score differences
    for n3 in range(0, n + 1):
        for n5 in range(0, n + 1 - n3):
            d3 = lp[:, 0] - lp[:, 1]
            d5 = lp[:, 2] - lp[:, 1]
            # choose n3 holes as par 3 and n5 as par 5 maximising the sum (Hungarian-free: greedy is exact for
            # disjoint top-k when ties are rare; good enough here)
            idx3 = list(np.argsort(-d3)[:n3])
            rest = [i for i in np.argsort(-d5) if i not in idx3][:n5]
            s = lp[:, 1].sum() + d3[idx3].sum() + d5[rest].sum()
            s += -0.5 * ((n3 - exp3) / 1.2) ** 2 - 0.5 * ((n5 - exp5) / 1.2) ** 2
            if best is None or s > best[0]:
                best = (s, idx3, rest)
    par = [4] * n
    for i in best[1]:
        par[i] = 3
    for i in best[2]:
        par[i] = 5
    return par


def _solve_large(sc, hyps, geo, keep, N, pars, yards, temp, use_clubhouse, use_paths):
    """27 / 36 holes: greedy chaining of loops of 9 from the clubhouse (exact DP is 2^27); marginals from the local
    soft-max at each step."""
    T, G = geo.T, geo.G
    Hc = (list(sc.clubhouse) if use_clubhouse else []) + hub_candidates(sc, geo, hyps)
    c = Hc[0]["c"]
    left = set(keep)
    holes = []
    prev = None
    k = 0
    while left and k < N:
        best = None
        cands = []
        for gi in left:
            for hi, h in enumerate(hyps[gi]):
                if prev is None or k % 9 == 0:
                    wl = anchor_ll(min(np.hypot(*(T[h["boxes"]] - c).T)))
                else:
                    wl = walk_ll(min(np.hypot(*(T[h["boxes"]] - G[prev]).T)))
                s = h["score"] + float(wl)
                cands.append((s, gi, hi))
        if not cands:
            break
        cands.sort(key=lambda r: -r[0])
        s0 = np.array([r[0] for r in cands]) / temp
        p = np.exp(s0 - _lse(s0))
        s, gi, hi = cands[0]
        h = hyps[gi][hi]
        holes.append(dict(number=k + 1, green=sc.greens[gi]["id"], green_xy=G[gi], tee=sc.tees[h["back"]]["id"],
                          tee_xy=T[h["back"]], boxes=[sc.tees[b]["id"] for b in h["boxes"]], length_yd=round(h["D"], 1),
                          p_par=[round(x, 3) for x in h["ppar"]], p_number=round(float(p[0]), 3), p_tee=1.0,
                          confidence=round(float(p[0]), 3), walk_in_yd=None, form_score=round(h["score"], 2), feat={}))
        left.discard(gi)
        prev = gi
        k += 1
    for h, p in zip(holes, infer_pars([h["p_par"] for h in holes], N)):
        h["par"] = p
    return dict(schema="course_structure/1", status="ok_greedy", n_holes=N, holes=holes,
                practice_greens=[sc.greens[i]["id"] for i in range(len(sc.greens)) if i not in {keep[0]} and
                                 sc.greens[i]["id"] not in {h["green"] for h in holes}],
                clubhouse=dict(xy=c, how=Hc[0]["how"], p=None), total_par=int(sum(h["par"] for h in holes)),
                card_used=bool(pars or yards), p_route=None)
