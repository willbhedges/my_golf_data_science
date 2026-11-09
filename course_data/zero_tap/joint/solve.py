"""joint routing: one constrained optimisation per course.

A routing is a sequence of N holes (tee complex, green) at positions 1..N. Its cost (nats, lower = better) is

    sum_i  hole(t_i, g_i)                     -log P(hole)  - detection log-odds of the green / tee used
         + card_i(t_i, g_i)                   -log-likelihood ratio of (play length - card yardage of hole i)
         + walk(g_i, t_{i+1})                 -log P(next tee); at a loop turn min(walk, end(g_i) + start(t_{i+1}))
         + start(t_1) + end(g_N)              loops begin / end at the clubhouse
         + cross * (#pairs of holes whose tee->green segments cross)

subject to: every green and every tee complex is used at most once. Detections may be missing: a hole may use a
*virtual tee* (green found, tee not: cost `c_vt`) or be entirely *missing* (cost `c_miss`), so the numbering of the
other holes survives; the missing piece is then proposed from the card (propose.py).

Search: beam over positions with state (greens used, tees used, last green), exact dynamic programme in the limit
of the beam width (Held-Karp); crossing counts are carried per state. `solve` returns the best routing; `margins`
re-solves with each position's green forbidden (min-marginals): the gap to the best routing that numbers that hole
differently, which is what the confidence is calibrated on.

Golfer answers (`fix`): {position (0-based): tee complex index} or {position: ('g', green index)} pins a hole.
"""
from __future__ import annotations

import numpy as np

BIG = 1e6
DEF = dict(K=6, beam=1500, w_h=1.0, w_w=1.0, w_c=1.0, w_s=1.0, w_x=1.5, w_dg=0.5, w_dt=0.25,
           c_vt=5.5, c_miss=11.0, c_nowalk=9.0, card_s=9.0, card_pi=0.9, card_bg=600.0, set_slack=12.0,
           two_pass=True, walk_miss=3.0, ph_min=0.004)


def _nl(p, lo=1e-4):
    return -np.log(np.clip(p, lo, 1.0))


def card_sets(card, n):
    """Yardage rows [k, n] of the card's tee sets that list every hole (longest set first), or None."""
    if not card:
        return None
    rows = []
    for s in (card.get("tee_sets") or {}).values():
        y = s.get("yards")
        if not y or any(v is None or v <= 0 for v in y):
            continue
        y = list(y)
        if len(y) < n and n % len(y) == 0:
            y = y * (n // len(y))
        if len(y) >= n:
            rows.append(y[:n])
    if not rows:
        return None
    Y = np.unique(np.array(rows, float), axis=0)
    return Y[np.argsort(-Y.sum(1))]


def card_llr(r, P):
    """-log likelihood ratio of a card residual r (yd): true hole = Laplace(card_s) with outliers, else uniform."""
    s, pi, bg = P["card_s"], P["card_pi"], P["card_bg"]
    f = pi * np.exp(-np.abs(r) / s) / (2 * s) + (1 - pi) / bg
    return -np.log(f * bg)


def segs_cross(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)


class Problem:
    """Candidates and cost tables of one course."""

    def __init__(self, d, card=None, params=None):
        P = dict(DEF)
        P.update(params or {})
        self.P = P
        self.d = d
        co, geo, sc = d["co"], d["geo"], d["sc"]
        self.N = N = int(d["kind"])
        self.loop = 9 if N % 9 == 0 else N
        ng, nt = len(co["G"]), len(co["T"])
        self.ng = ng
        ph = {(int(t), int(g)): float(p) for (t, g), p in zip(d["hp"], sc["ph"])}
        # candidate holes: per green its K best tees (+ anything decent)
        cand = []
        for g in range(ng):
            ts = sorted(((p, t) for (t, gg), p in ph.items() if gg == g), reverse=True)
            for r, (p, t) in enumerate(ts):
                if (r < P["K"] and p >= P["ph_min"]) or p >= 0.2:
                    cand.append((t, g))
        used_t = sorted({t for t, g in cand})
        if len(used_t) > 63 or ng > 63:                       # bitmask limit: keep the most probable
            raise ValueError("too many candidates")
        self.real = len(cand)
        cand += [(-1, g) for g in range(ng)]
        cand.append((-1, -1))
        self.cand = cand
        C = len(cand)
        self.ct = np.array([t for t, g in cand])
        self.cg = np.array([g for t, g in cand])
        self.gbit = np.array([np.uint64(1) << np.uint64(g) if g >= 0 else np.uint64(0) for t, g in cand], np.uint64)
        tpos = {t: i for i, t in enumerate(used_t)}
        self.tbit = np.array([np.uint64(1) << np.uint64(tpos[t]) if t >= 0 else np.uint64(0) for t, g in cand],
                             np.uint64)
        Gp = np.clip(co["Gp"], 0.03, 0.97)
        Tp = np.clip(np.array([t["p"] for t in co["T"]]), 0.03, 0.97) if nt else np.zeros(0)
        base = np.zeros(C)
        for c, (t, g) in enumerate(cand):
            if g >= 0:
                base[c] -= P["w_dg"] * np.log(Gp[g] / (1 - Gp[g]))
            if t >= 0:
                base[c] += P["w_h"] * _nl(ph[(t, g)]) - P["w_dt"] * np.log(Tp[t] / (1 - Tp[t]))
            elif g >= 0:
                base[c] += P["c_vt"]
            else:
                base[c] += P["c_miss"]
        self.base = base
        # walk table [last green + 1 (0 = none), cand]
        pw = np.full((ng, nt), 0.0)
        for (g, t), p in zip(d["wp"], sc["pw"]):
            pw[g, t] = p
        wn = P["w_w"] * _nl(pw) if nt else np.zeros((ng, 0))
        wn = np.minimum(wn, P["c_nowalk"])
        self.walk = np.zeros((ng + 1, C))
        for c, (t, g) in enumerate(cand):
            if t >= 0:
                self.walk[1:, c] = wn[:, t]
                self.walk[0, c] = P["walk_miss"]
            else:
                self.walk[:, c] = P["walk_miss"] if g >= 0 else 0.0
        self.start = np.array([P["w_s"] * _nl(sc["ps"][t], 1e-3) if t >= 0 else P["w_s"] * 3.0 for t, g in cand])
        end = P["w_s"] * _nl(sc["pe"], 1e-3)
        self.end = np.r_[P["w_s"] * 3.0, end]                 # by last + 1
        # crossings between real candidates
        Tc, G = geo["Tc"], co["G"]
        X = np.zeros((C, C), np.uint8)
        for a in range(self.real):
            ta, ga = cand[a]
            for b in range(a + 1, self.real):
                tb, gb = cand[b]
                if ta == tb or ga == gb:
                    continue
                if segs_cross(Tc[ta], G[ga], Tc[tb], G[gb]):
                    X[a, b] = X[b, a] = 1
        self.X = X
        # card residuals [set, position, cand]
        self.Y = card_sets(card, N)
        self.R = None
        if self.Y is not None:
            K = len(self.Y)
            R = np.full((K, N, C), np.nan)
            for c in range(self.real):
                t, g = cand[c]
                pb = geo["Pbox"][t][g]
                R[:, :, c] = np.min(np.abs(pb[None, None, :] - self.Y[:, :, None]), axis=2)
            self.R = R
        self.kstar = None

    def card_cost(self):
        """[position, cand] card cost. Before a tee set is chosen: best set per hole; after: the chosen set, any
        other set at `set_slack` yd extra."""
        C = len(self.cand)
        if self.R is None:
            return np.zeros((self.N, C))
        r = np.min(self.R, axis=0)
        if self.kstar is not None:
            r = np.minimum(self.R[self.kstar], r + self.P["set_slack"])
        cc = self.P["w_c"] * card_llr(r, self.P)
        return np.where(np.isnan(r), 0.0, cc)


def beam(pr, fix=None, forbid=None, beam_w=None, keep=1):
    """Beam / DP over positions. fix {pos: tee index | ('g', green index) | ('c', cand index)};
    forbid = set of (pos, green index). -> list of (cost, [cand index per position]) best first (up to `keep`)."""
    P = pr.P
    B = beam_w or P["beam"]
    N, C = pr.N, len(pr.cand)
    cc = pr.card_cost()
    fix = fix or {}
    forbid = forbid or ()
    gm = np.zeros(1, np.uint64)
    tm = np.zeros(1, np.uint64)
    last = np.zeros(1, np.int64)                              # last green + 1
    score = np.zeros(1)
    acc = np.zeros((1, C), np.uint8)
    back = []
    wx = P["w_x"]
    for i in range(N):
        step = pr.base + cc[i]
        allow = np.ones(C, bool)
        if i in fix:
            f = fix[i]
            if isinstance(f, tuple) and f[0] == "g":
                allow = pr.cg == f[1]
            elif isinstance(f, tuple) and f[0] == "c":
                allow = np.arange(C) == f[1]
            else:
                allow = pr.ct == f
            if not allow.any():
                allow = np.ones(C, bool)
        for (pi, g) in forbid:
            if pi == i:
                allow &= pr.cg != g
        step = np.where(allow, step, BIG)
        if i == 0:
            tr = pr.start[None, :] + np.zeros((1, 1))
        elif i % pr.loop == 0:
            tr = np.minimum(pr.walk[last], pr.end[last][:, None] + pr.start[None, :])
        else:
            tr = pr.walk[last]
        tot = score[:, None] + step[None, :] + tr + wx * acc
        bad = ((gm[:, None] & pr.gbit[None, :]) != 0) | ((tm[:, None] & pr.tbit[None, :]) != 0)
        tot = np.where(bad, BIG * 10, tot)
        flat = tot.ravel()
        k = min(len(flat), B * 4)
        idx = np.argpartition(flat, k - 1)[:k] if k < len(flat) else np.arange(len(flat))
        idx = idx[flat[idx] < BIG]
        if not len(idx):
            return []
        idx = idx[np.argsort(flat[idx], kind="stable")]
        par, c = idx // C, idx % C
        ngm, ntm = gm[par] | pr.gbit[c], tm[par] | pr.tbit[c]
        nl = pr.cg[c] + 1
        key = (ngm * np.uint64(0x9E3779B97F4A7C15)) ^ (ntm * np.uint64(0xC2B2AE3D27D4EB4F)) ^ nl.astype(np.uint64)
        _, first = np.unique(key, return_index=True)
        first = np.sort(first)[:B]
        par, c = par[first], c[first]
        gm, tm, last, score = ngm[first], ntm[first], nl[first], flat[idx[first]]
        acc = acc[par] + pr.X[c]
        back.append((par, c))
    score = score + pr.end[last]
    out = []
    for j in np.argsort(score, kind="stable")[:keep]:
        seq, k = [], int(j)
        for par, c in reversed(back):
            seq.append(int(c[k]))
            k = int(par[k])
        out.append((float(score[j]), seq[::-1]))
    return out


def solve(d, card=None, params=None, fix=None):
    """-> dict(cost, seq [cand index per position], holes [(tee index | -1, green index | -1)], pr)."""
    pr = Problem(d, card, params)
    res = beam(pr, fix)
    if not res:
        return dict(cost=None, seq=[], holes=[], pr=pr)
    if pr.R is not None and pr.P["two_pass"] and len(pr.Y) > 1:
        cost, seq = res[0]
        real = [(i, c) for i, c in enumerate(seq) if c < pr.real]
        if len(real) >= pr.N // 2:
            tot = [np.median([pr.R[k, i, c] for i, c in real]) for k in range(len(pr.Y))]
            pr.kstar = int(np.argmin(tot))
            res = beam(pr, fix)
    cost, seq = res[0]
    return dict(cost=cost, seq=seq, holes=[pr.cand[c] for c in seq], pr=pr)


def margins(sol, fix=None, beam_w=400):
    """Per position: cost of the best routing that puts another green (or none) there, minus the best cost."""
    pr = sol["pr"]
    out = []
    for i, c in enumerate(sol["seq"]):
        g = pr.cg[c]
        if g < 0 or (fix and i in fix and isinstance(fix[i], tuple) and fix[i][0] in ("g", "c")):
            out.append(0.0 if g < 0 else 99.0)
            continue
        r = beam(pr, fix, forbid={(i, int(g))}, beam_w=beam_w)
        out.append(max(0.0, r[0][0] - sol["cost"]) if r else 99.0)
    return out
