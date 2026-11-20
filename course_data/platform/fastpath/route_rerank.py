"""Routing re-ranker for router v2 (route_scene): alternatives to the solver's routing, scored by a learned model.

solve2's objective is a sum of local terms; its errors are routings that cost less than the truth (route_struct,
NOTES_ROUTING.md). Most wrong holes sit in courses where a whole stretch is numbered wrong: a loop started from the
wrong tee shifts every number after it, the two nines are swapped, or a segment is played in the other direction.
This module

  * builds alternatives to the chosen routing seq0 (`candidates`): the beam's other best routings (plain and priced),
    renumberings of seq0 (each nine rotated, nines swapped, a nine reversed, combinations), and re-solves with a loop
    start fixed to another tee complex / a loop end fixed to another green (explicit loop-start alternatives);
  * describes each one by course-level features relative to seq0 (`features`): the solver's cost split into its
    parts, the full-card fit (yardage correlation, relative residuals, par 3 / par 5 positions), loop starts / ends
    near the clubhouse, walk lengths, crossings, virtual ends;
  * a gradient-boosted model (route_rerank_model.pkl) predicts the gain in right holes of each alternative over seq0;
    the best one replaces seq0 when its predicted gain clears the model's threshold. A model with rank=True is a
    LightGBM lambdarank ranker over each course's alternatives plus seq0 (graded by right holes); its score of an
    alternative minus seq0's own score (the row of seq0 against itself) is the gain the threshold reads.

Training rows come from the routing bench (scratch scripts; labels = route_struct.correct on the hidden OSM ways).
"""
from __future__ import annotations

import os
import pickle

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import detector as _DET  # noqa: E402
MODEL = _DET.routing_file("route_rerank_model.pkl", "ROUTE_RERANK_MODEL")
_M = {}


def _s2():
    import route_scene as RS
    RS._mods()
    import solve2 as S2
    return S2


# ----------------------------------------------------------------------------- costs
def cost_parts(pr, seq):
    """the solver's cost of seq (as beam2 scores it) split into parts -> dict"""
    S2 = _s2()
    cc, Tm, st, en = S2.tables(pr)
    out = dict(base=0.0, card=0.0, walk=0.0, ends=0.0, reuse=0.0, cross=0.0)
    last = 0
    used_t = np.uint64(0)
    for i, c in enumerate(seq):
        out["base"] += float(pr.base[c])
        out["card"] += float(cc[i, c])
        if i == 0:
            out["ends"] += float(st[0][c])
        else:
            a = float(Tm[i][last, c])
            if i % pr.loop == 0:
                b = float(en[i - 1][last] + st[i][c])
                if b < a:
                    out["ends"] += b
                else:
                    out["walk"] += a
            else:
                out["walk"] += a
        if pr.reuse is not None and (used_t & pr.tbit[c]) != 0:
            out["reuse"] += pr.reuse
        used_t |= pr.tbit[c]
        last = int(pr.endi[c])
    out["ends"] += float(en[pr.N - 1][last])
    nx = 0
    for a in range(len(seq)):
        for b in range(a + 1, len(seq)):
            nx += int(pr.X[seq[a], seq[b]])
    out["nx"] = float(nx)
    out["cross"] = pr.P["w_x"] * nx
    out["total"] = sum(out[k] for k in ("base", "card", "walk", "ends", "reuse", "cross"))
    return out


def valid(pr, seq):
    """every green at most once, a tee complex reused only when the solver allows it"""
    gm = np.uint64(0)
    tm = np.uint64(0)
    for c in seq:
        if (gm & pr.gbit[c]) != 0:
            return False
        if pr.reuse is None and (tm & pr.tbit[c]) != 0:
            return False
        gm |= pr.gbit[c]
        tm |= pr.tbit[c]
    return True


# ----------------------------------------------------------------------------- alternatives
def renumberings(N, L):
    """position permutations: seq'[p] = seq[perm[p]] (each loop rotated / reversed, loops reordered)"""
    import itertools
    nl = N // L
    out = []
    for order in itertools.permutations(range(nl)):
        for li in range(nl):
            for s in range(L):
                for rev in (0, 1):
                    perm = []
                    for lj in order:
                        lo = [lj * L + j for j in range(L)]
                        if lj == li:
                            lo = lo[s:] + lo[:s]
                            if rev:
                                lo = lo[::-1]
                        perm += lo
                    out.append(perm)
        if nl == 2:                                  # both nines rotated (with the nines in either order)
            for s1 in range(1, L):
                for s2 in range(1, L):
                    perm = []
                    for lj in order:
                        s = s1 if lj == 0 else s2
                        lo = [lj * L + j for j in range(L)]
                        perm += lo[s:] + lo[:s]
                    out.append(perm)
    if nl > 1:                                       # the whole card rotated across the nines
        for s in range(1, N):
            out.append([(j + s) % N for j in range(N)])
    seen, uniq = set(), []
    ident = tuple(range(N))
    for p in out:
        t = tuple(p)
        if t != ident and t not in seen:
            seen.add(t)
            uniq.append(p)
    return uniq


def candidates(pr, seq0, keep=10, n_anchor=6, renumber=True, fixed=True):
    """[(kind, seq)] alternatives to seq0 (seq0 itself first, kind 'chosen')"""
    S2 = _s2()
    N, L = pr.N, pr.loop
    out = [("chosen", list(seq0))]
    seen = {tuple(seq0)}

    def add(kind, s):
        t = tuple(int(c) for c in s)
        if len(t) == N and t not in seen and valid(pr, t):
            seen.add(t)
            out.append((kind, list(t)))
    try:
        for _, s in S2.beam2(pr, keep=keep + 1):
            add("beam", s)
        if pr.P.get("lag_iters", 0) > 0:
            for _, s in S2.beam2(pr, keep=keep + 1, price=S2.lagrange(pr)):
                add("beam", s)
    except Exception:                                                # noqa: BLE001
        pass
    if renumber:
        for perm in renumberings(N, L):
            add("renum", [seq0[j] for j in perm])
    if fixed:
        for i0 in range(0, N, L):                    # loop starts: another tee complex
            used = [int(pr.ct[c]) for c in seq0[i0:i0 + L] if pr.ct[c] >= 0]
            cur = int(pr.ct[seq0[i0]])
            top = [int(t) for t in np.argsort(-pr.ps)[:n_anchor]] if pr.nt else []
            ts = []
            for t in used[1:3] + used[-2:] + top:
                if t != cur and t not in ts:
                    ts.append(t)
            for t in ts[:n_anchor]:
                r = S2.search(pr, fix={i0: t})
                if r:
                    add("start", r[0][1])
        for i1 in range(L - 1, N, L):                # loop ends: another green
            used = [int(pr.cg[c]) for c in seq0[i1 - L + 1:i1 + 1] if pr.cg[c] >= 0]
            cur = int(pr.cg[seq0[i1]])
            top = [int(g) for g in np.argsort(-pr.pe)[:n_anchor]] if pr.ng else []
            gs = []
            for g in used[:2] + used[-3:-1] + top:
                if g != cur and g not in gs:
                    gs.append(g)
            for g in gs[:n_anchor]:
                r = S2.search(pr, fix={i1: ("g", g)})
                if r:
                    add("end", r[0][1])
    return out


# ----------------------------------------------------------------------------- features
FEATS = ("total", "base", "card", "walk", "ends", "reuse", "nx", "n_vt", "n_vg", "n_miss", "card_corr", "card_rel",
         "card_rel_max", "card_big", "par3_bad", "par5_bad", "par_bad", "club_start", "club_end", "club_rank_s",
         "club_rank_e", "walk_sum", "walk_max", "walk_long", "ps_sum", "pe_sum", "ph_sum")


def features(pr, seq, seq0=None):
    """course-level description of a routing (absolute; the learner takes differences to seq0)"""
    S2 = _s2()
    f = cost_parts(pr, seq)
    N, L = pr.N, pr.loop
    typ = pr.typ[np.asarray(seq)]
    f["n_vt"] = float(np.sum(typ == S2.VT))
    f["n_vg"] = float(np.sum(typ == S2.VG))
    f["n_miss"] = float(np.sum(typ == S2.MISS))
    geo = pr.d["geo"]
    y = pr.ygeom()
    Ls, ys, rel = [], [], []
    p3b = p5b = 0
    for i, c in enumerate(seq):
        k, t, g = pr.cand[c]
        if k != S2.REAL or y is None:
            continue
        Lp = float(geo["P"][t, g])
        r = pr.R[pr.kstar, i, c] if (pr.R is not None and pr.kstar is not None) else \
            (np.min(pr.R[:, i, c]) if pr.R is not None else abs(Lp - y[i]))
        Ls.append(Lp)
        ys.append(float(y[i]))
        rel.append(float(r) / max(float(y[i]), 1.0))
        if pr.card_par and pr.card_par[i]:
            if pr.card_par[i] == 3 and Lp > 260:
                p3b += 1
            if pr.card_par[i] >= 4 and Lp < 215:
                p3b += 1
            if pr.card_par[i] == 5 and Lp < 410:
                p5b += 1
            if pr.card_par[i] <= 4 and Lp > 520:
                p5b += 1
    f["card_corr"] = float(np.corrcoef(Ls, ys)[0, 1]) if len(Ls) >= 4 and np.std(Ls) > 0 and np.std(ys) > 0 else 0.0
    f["card_rel"] = float(np.mean(rel)) if rel else 0.0
    f["card_rel_max"] = float(np.max(rel)) if rel else 0.0
    f["card_big"] = float(np.sum(np.asarray(rel) > 0.15)) if rel else 0.0
    f["par3_bad"], f["par5_bad"], f["par_bad"] = float(p3b), float(p5b), float(p3b + p5b)
    cs = ce = rs = re_ = 0.0
    if pr.club is not None:
        dct = pr.Dct if pr.Dct is not None else np.zeros(0)
        dcg = pr.Dcg
        for i0 in range(0, N, L):
            t = int(pr.ct[seq[i0]])
            if t >= 0 and len(dct):
                cs += float(np.log1p(dct[t] / 50.0))
                rs += float(np.sum(dct < dct[t])) / max(len(dct), 1)
            else:
                cs += 2.0
                rs += 0.5
        for i1 in range(L - 1, N, L):
            g = int(pr.cg[seq[i1]])
            if g >= 0:
                ce += float(np.log1p(dcg[g] / 50.0))
                re_ += float(np.sum(dcg < dcg[g])) / max(len(dcg), 1)
            else:
                ce += 2.0
                re_ += 0.5
    f["club_start"], f["club_end"], f["club_rank_s"], f["club_rank_e"] = cs, ce, rs, re_
    D = geo["D"]
    ws = []
    for i in range(N - 1):
        if (i + 1) % L == 0:
            continue
        g = int(pr.cg[seq[i]])
        t = int(pr.ct[seq[i + 1]])
        if g >= 0 and t >= 0 and pr.typ[seq[i + 1]] != S2.VT:
            ws.append(min(float(D[t, g]), 800.0))
    f["walk_sum"] = float(np.sum(ws)) if ws else 0.0
    f["walk_max"] = float(np.max(ws)) if ws else 0.0
    f["walk_long"] = float(np.sum(np.asarray(ws) > 250)) if ws else 0.0
    f["ps_sum"] = float(sum(pr.ps[int(pr.ct[seq[i0]])] for i0 in range(0, N, L) if pr.ct[seq[i0]] >= 0))
    f["pe_sum"] = float(sum(pr.pe[int(pr.cg[seq[i1]])] for i1 in range(L - 1, N, L) if pr.cg[seq[i1]] >= 0))
    f["ph_sum"] = float(sum(pr.ph.get((int(pr.ct[c]), int(pr.cg[c])), 0.0) for c in seq if pr.typ[c] == S2.REAL))
    return {k: f[k] for k in FEATS}


# extended features (model key feats2=True; NOTES_ROUTING.md 2026-11-20 "re-ranker features")
FEATS2 = ("par_out_yd", "par4_bad", "rel_sum", "rel_n08", "rel_n25", "rel_top3", "rel_kset", "len_corr_k",
          "walk_rank_sum", "walk_rank_bad", "walk_back", "walk_med", "loop_close", "club_both", "nine_err",
          "nine_swap_gain", "nine_rel", "x_pairs_near", "ph_min", "ph_n05", "pw_sum", "pw_min")
# per-hole model aggregates + tee-box consistency (model key feats3=True; NOTES_ROUTING.md 2026-11-20 "re-ranker
# features 3"): mean hole score and holes under 0.7 over the routing's real holes, holes whose tee complex (whole or a
# split half) another hole also uses, greens used by two holes, virtual ends
FEATS3 = ("ph_mean", "ph_n07", "tee_shared", "green_shared", "n_virtual_ends")
PAR_BAND = {3: (90.0, 260.0), 4: (240.0, 490.0), 5: (430.0, 680.0)}


def features2(pr, seq):
    """extra course-level description of a routing: per-hole par bands, card residual distribution (course set and
    best set), walk geometry (next tee's rank among tees near the green, backtracking toward the green just played),
    loop closure / clubhouse, front / back nine totals vs the card (and vs the card with the nines swapped), the hole /
    walk model scores' weakest links"""
    S2 = _s2()
    N, L = pr.N, pr.loop
    geo = pr.d["geo"]
    D = geo["D"]                                    # [t, g]
    f = {k: 0.0 for k in FEATS2}
    Lp = np.full(N, np.nan)
    for i, c in enumerate(seq):
        k, t, g = pr.cand[c]
        if k == S2.REAL:
            Lp[i] = float(geo["P"][t, g])
    if pr.card_par:
        for i in range(N):
            par = pr.card_par[i]
            if par in PAR_BAND and Lp[i] == Lp[i]:
                lo, hi = PAR_BAND[par]
                out = max(0.0, lo - Lp[i], Lp[i] - hi)
                f["par_out_yd"] += min(out, 200.0)
                if par == 4 and out > 0:
                    f["par4_bad"] += 1
    if pr.Y is not None:
        ok = Lp == Lp
        Y = np.asarray(pr.Y, float)
        k0 = pr.kstar if pr.kstar is not None else int(np.argmin([np.nanmedian(np.abs(Lp[ok] - y[ok])) if ok.any()
                                                                  else 0 for y in Y]))
        y = Y[k0]
        rel = np.abs(Lp[ok] - y[ok]) / np.maximum(y[ok], 1.0)
        if len(rel):
            f["rel_sum"] = float(np.sum(np.minimum(rel, 0.5)))
            f["rel_n08"] = float(np.sum(rel > 0.08))
            f["rel_n25"] = float(np.sum(rel > 0.25))
            f["rel_top3"] = float(np.mean(np.sort(rel)[-3:]))
            f["rel_kset"] = float(np.mean(np.min(np.abs(Lp[ok][None] - Y[:, ok]) / np.maximum(Y[:, ok], 1.0), 0)))
            if ok.sum() >= 4 and np.std(Lp[ok]) > 0 and np.std(y[ok]) > 0:
                f["len_corr_k"] = float(np.corrcoef(Lp[ok], y[ok])[0, 1])
        if N == 18 and L == 9:
            def nine(a, b):
                m = (Lp[a:b] == Lp[a:b])
                return float(np.sum(Lp[a:b][m])), m
            fr, mf = nine(0, 9)
            bk, mb = nine(9, 18)
            yf, yb = y[:9], y[9:]
            e = abs(fr - np.sum(yf[mf])) + abs(bk - np.sum(yb[mb]))
            es = abs(fr - np.sum(yb[mf])) + abs(bk - np.sum(yf[mb]))
            f["nine_err"] = e
            f["nine_swap_gain"] = e - es
            f["nine_rel"] = e / max(float(np.sum(y)), 1.0)
    # walks: rank of the next tee among all tee complexes by distance from the green
    used_t = [int(pr.ct[c]) for c in seq]
    ws, rk = [], []
    for i in range(N - 1):
        if (i + 1) % L == 0:
            continue
        g = int(pr.cg[seq[i]])
        t = int(pr.ct[seq[i + 1]])
        if g < 0 or t < 0 or pr.typ[seq[i + 1]] == S2.VT:
            continue
        dg = D[:, g]
        r = int(np.sum(dg < dg[t]))
        rk.append(r)
        ws.append(float(dg[t]))
        tp = int(pr.ct[seq[i]])                    # backtracking: next tee nearer the tee just played than its green
        if tp >= 0 and pr.Dtt is not None and len(pr.Dtt) and pr.Dtt[tp, t] < 0.5 * float(D[tp, g]):
            f["walk_back"] += 1
    if rk:
        f["walk_rank_sum"] = float(np.sum(np.minimum(rk, 10)))
        f["walk_rank_bad"] = float(np.sum(np.asarray(rk) >= 3))
        f["walk_med"] = float(np.median(ws))
    for i0 in range(0, N, L):                       # loop closure: last green back near the first tee
        t = int(pr.ct[seq[i0]])
        g = int(pr.cg[seq[i0 + L - 1]])
        if t >= 0 and g >= 0:
            f["loop_close"] += min(float(D[t, g]), 1000.0)
        if pr.club is not None and t >= 0 and g >= 0 and pr.Dct is not None:
            f["club_both"] += float(np.log1p(pr.Dct[t] / 50.0) + np.log1p(pr.Dcg[g] / 50.0))
    # crossings between holes that are adjacent in the numbering are cheap; far ones are suspicious
    for a in range(N):
        for b in range(a + 2, N):
            if pr.X[seq[a], seq[b]]:
                f["x_pairs_near"] += 1
    ph = [pr.ph.get((int(pr.ct[c]), int(pr.cg[c])), 0.0) for c in seq if pr.typ[c] == S2.REAL]
    if ph:
        f["ph_min"] = float(np.min(ph))
        f["ph_n05"] = float(np.sum(np.asarray(ph) < 0.5))
        f["ph_mean"] = float(np.mean(ph))
        f["ph_n07"] = float(np.sum(np.asarray(ph) < 0.7))
    else:
        f["ph_mean"] = f["ph_n07"] = 0.0
    T = pr.d["co"]["T"]
    base = [str(T[int(pr.ct[c])].get("id", "")).split("/")[0] if int(pr.ct[c]) >= 0 else None for c in seq]
    cnt = {}
    for b in base:
        if b is not None:
            cnt[b] = cnt.get(b, 0) + 1
    f["tee_shared"] = float(sum(1 for b in base if b is not None and cnt[b] > 1))
    gs = [int(pr.cg[c]) for c in seq if int(pr.cg[c]) >= 0]
    f["green_shared"] = float(len(gs) - len(set(gs)))
    f["n_virtual_ends"] = float(sum(1 for c in seq if int(pr.ct[c]) < 0) + sum(1 for c in seq if int(pr.cg[c]) < 0))
    wn = []
    for i in range(N - 1):
        if (i + 1) % L == 0:
            continue
        g = int(pr.cg[seq[i]])
        t = int(pr.ct[seq[i + 1]])
        if g >= 0 and t >= 0:
            wn.append(float(pr.wn[g, t]))
    if wn:
        f["pw_sum"] = float(np.sum(wn))
        f["pw_min"] = float(np.max(wn))
    return f


KINDS = ("beam", "renum", "start", "end")


CLUB_FEATS = ("club_start", "club_end", "club_rank_s", "club_rank_e", "club_both")


def row(f, f0, kind, ham, N, f2=None, f20=None, noclub=False, sub2=None, x3=False):
    """learner input: differences to seq0, a few seq0 levels, the alternative's kind and size (+ FEATS2 differences
    and seq0 levels when given). noclub: the clubhouse-derived features are zeroed (on the bench the clubhouse comes
    from OSM tags / car parks far more often than on unmapped courses, where it is usually absent)"""
    if noclub:
        f, f0 = ({k: (0.0 if k in CLUB_FEATS else v) for k, v in x.items()} for x in (f, f0))
        if f2 is not None:
            f2, f20 = ({k: (0.0 if k in CLUB_FEATS else v) for k, v in x.items()} for x in (f2, f20))
    d = [f[k] - f0[k] for k in FEATS]
    lv = [f0["total"] / N, f0["card_rel"], f0["card_corr"], f0["n_vt"] + f0["n_vg"] + f0["n_miss"], N]
    out = d + lv + [float(kind == k) for k in KINDS] + [ham, ham / N]
    if f2 is not None:
        if sub2:
            out += [f2[k] - f20[k] for k in sub2]
        else:
            out += [f2[k] - f20[k] for k in FEATS2] + [f20[k] for k in FEATS2]
        if x3:
            out += [f2.get(k, 0.0) - f20.get(k, 0.0) for k in FEATS3] + [f20.get(k, 0.0) for k in FEATS3]
    return out


class RankAvg:
    """the mean score of several rankers (bagged LightGBM lambdarank fits: row / column subsamples, seeds)"""

    def __init__(self, models):
        self.models = list(models)

    def predict(self, X):
        return np.mean([m.predict(X) for m in self.models], axis=0)


# ----------------------------------------------------------------------------- production
def model():
    if "m" not in _M:
        _M["m"] = pickle.load(open(MODEL, "rb")) if os.path.exists(MODEL) else None
    return _M["m"]


def rerank(pr, seq0, m=None):
    """-> (seq, info): the model's pick among the alternatives (seq0 unless an alternative clears the threshold)"""
    m = m or model()
    if m is None or not seq0:
        return seq0, None
    try:
        return _rerank(pr, seq0, m)
    except Exception as e:                                           # noqa: BLE001
        return seq0, dict(error=repr(e)[:200])


def _rerank(pr, seq0, m):
    cands = candidates(pr, seq0, **m.get("gen", {}))
    pr.rr_cands = cands                  # reused by route_scene's shared-green fallback
    f0 = features(pr, seq0)
    x2 = bool(m.get("feats2"))
    nc = bool(m.get("noclub"))
    sub2 = m.get("feats2_sub")
    f20 = features2(pr, seq0) if x2 else None
    best, bi, gains = m["thr"], 0, []
    X, keep = [], []
    kinds = set(m.get("kinds") or KINDS)
    for k, s in cands[1:]:
        if k not in kinds:
            continue
        ham = sum(a != b for a, b in zip(s, seq0))
        X.append(row(features(pr, s), f0, k, ham, pr.N, features2(pr, s) if x2 else None, f20, nc, sub2,
                     x3=bool(m.get("feats3"))))
        keep.append((k, s))
    if not X:
        return seq0, dict(n_alts=0)
    X = np.asarray(X, float)
    if m.get("rank"):                    # a ranker (LightGBM lambdarank): scores relative to seq0's own row
        s0 = m["model"].predict(np.asarray([row(f0, f0, "chosen", 0, pr.N, f20, f20, nc, sub2)], float))[0]
        g = m["model"].predict(X) - s0
    else:
        g = m["model"].predict(X)
    j = int(np.argmax(g))
    info = dict(n_alts=len(X), best_gain=round(float(g[j]), 3), kind=keep[j][0])
    if g[j] > best:
        info["switched"] = True
        return list(keep[j][1]), info
    return seq0, info
