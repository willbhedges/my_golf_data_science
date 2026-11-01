"""pathroute decoder: the round as a tour clubhouse -> tee_1 -> green_1 -> (walk) -> tee_2 -> ... -> green_n ->
clubhouse, scored with the local models, solved by an exact-in-the-limit beam over (greens used, last green).

The tee of each hole is chosen inside the green -> green step (min over tees of walk + hole cost), so pairing and
order are solved jointly. 18-hole loops add the clubhouse return/start at the 9 -> 10 turn.
"""
from __future__ import annotations

import math

import numpy as np

BIG = 14.0


def _nl(p):
    return -np.log(np.clip(p, 1e-5, 1.0))


def cost_mats(d, pr, w):
    nt, ng = len(d["tees"]), len(d["greens"])
    H = np.full((nt, ng), BIG)
    for (t, g), p in zip(d["hp"], pr["hole"]):
        H[t, g] = _nl(p)
    T = np.full((ng, nt), BIG)
    for (g, t), p in zip(d["tp"], pr["trans"]):
        T[g, t] = _nl(p)
    S = _nl(pr["start"])
    E = _nl(pr["end"])
    return H, w["trans"] * T, w["club"] * S, w["club"] * E


def step_mat(H, T, add_t=None, add_g=None):
    """green g -> green g' through the best tee t: min_t T[g,t] (+add_t[t]) + H[t,g'] (+add_g[g])."""
    TT = T if add_t is None else T + add_t[None, :]
    C = TT[:, :, None] + H[None, :, :]                      # g, t, g'
    arg = np.argmin(C, axis=1)
    W = np.take_along_axis(C, arg[:, None, :], 1)[:, 0, :]
    if add_g is not None:
        W = W + add_g[:, None]
    np.fill_diagonal(W, np.inf)
    return W, arg


def card_cost(D, y, lam):
    """Position cost of a tee -> green straight-line length D against the card's (back-tee) yardage y."""
    r = np.log(np.maximum(D, 30.0) / max(float(y), 50.0)) + 0.04
    return lam * np.minimum((r / 0.12) ** 2, 9.0)


def beam_loop(H, T, S, E, n, avail_g, avail_t, beam=20000, mid=None, D=None, card_y=None, lam=0.0):
    """Best loop of n holes over the available greens / tees. -> (greens, tees, cost, conf).
    With a card (card_y: yards per position, D: tee x green lengths) each position k adds card_cost."""
    ng = H.shape[1]
    Hm = H.copy()
    Hm[~avail_t, :] = np.inf
    Hm[:, ~avail_g] = np.inf
    W, A = step_mat(Hm, T)
    if mid:
        Wm, Am = step_mat(Hm, T, add_t=S, add_g=E)
    Hk = None
    if card_y is not None and D is not None and lam > 0:
        Hk = [Hm + card_cost(D, card_y[k], lam) for k in range(n)]
    s0 = S[:, None] + (Hm if Hk is None else Hk[0])                                    # start: clubhouse -> tee t -> green g
    a0 = np.argmin(s0, axis=0)
    c = s0[a0, np.arange(ng)]
    ok = np.isfinite(c)
    last = np.nonzero(ok)[0]
    cost = c[ok]
    mask = (np.int64(1) << last.astype(np.int64))
    hist = []                                               # per step: (parent idx, last, tee)
    hist.append((np.full(len(last), -1), last.copy(), a0[last]))
    for k in range(2, n + 1):
        if Hk is not None:
            Wk, Ak = step_mat(Hk[k - 1], T, add_t=S, add_g=E) if (mid and k == mid + 1) else step_mat(Hk[k - 1], T)
        else:
            Wk, Ak = (Wm, Am) if (mid and k == mid + 1) else (W, A)
        cand = cost[:, None] + Wk[last, :]
        used = ((mask[:, None] >> np.arange(ng, dtype=np.int64)[None, :]) & 1).astype(bool)
        cand[used] = np.inf
        flat = cand.ravel()
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
        cost = flat[order[first]]
        mask = nm[first]
        tee = Ak[last[par], g]
        last = g
        hist.append((par, g.copy(), tee))
    fin = cost + E[last]
    o = np.argsort(fin)
    best = o[0]
    rel = fin[o[:500]] - fin[best]
    conf = float(1.0 / np.sum(np.exp(-rel)))
    greens, tees = [], []
    i = best
    for par, g, t in reversed(hist):
        greens.append(int(g[i]))
        tees.append(int(t[i]))
        i = par[i]
    return greens[::-1], tees[::-1], float(fin[best]), conf


def decode(d, pr, w, beam=4000, card_y=None):
    kind = d["kind"]
    n = 9 if kind in (9, 27) else 18
    loops = {9: 1, 18: 1, 27: 3, 36: 2}.get(kind, max(1, round(kind / n)))
    H, T, S, E = cost_mats(d, pr, w)
    ng, nt = H.shape[1], H.shape[0]
    avail_g, avail_t = np.ones(ng, bool), np.ones(nt, bool)
    tc = np.array(d["tc"])
    gcs = np.array(d["gc"])
    D = np.hypot(tc[:, None, 0] - gcs[None, :, 0], tc[:, None, 1] - gcs[None, :, 1])
    out = []
    confs = []
    for li in range(loops):
        cy = card_y[li * n:(li + 1) * n] if card_y is not None and len(card_y) >= (li + 1) * n else \
            (card_y[:n] if card_y is not None and len(card_y) >= n else None)
        r = beam_loop(H, T, S, E, n, avail_g, avail_t, beam=beam, mid=9 if n == 18 else None, D=D, card_y=cy,
                      lam=w.get("card", 0.0))
        if r is None:
            break
        gs, ts, c, conf = r
        confs.append(conf)
        for k, (g, t) in enumerate(zip(gs, ts)):
            gp = np.array(d["gc"][g])
            tp = tc[t]
            u = (gp - tp) / max(np.hypot(*(gp - tp)), 1.0)
            rel = tc - tp
            along = rel @ u
            lat = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
            box = np.nonzero((np.hypot(*rel.T) < 80) & (lat < 22) & avail_t)[0]
            box = [int(b) for b in box if b != t]
            L = max([float(np.hypot(*(gp - tc[b]))) for b in box + [t]])
            out.append(dict(number=k + 1, g=g, t=t, boxes=box, L=L, loop=li))
            avail_g[g] = False
            avail_t[t] = False
            for b in box:
                avail_t[b] = False
    return out, float(np.prod(confs)) if confs else 0.0


def par_from_len(L, cut3=225.0, cut4=450.0):          # cuts fitted on dev (PATHROUTE.md)
    return 3 if L <= cut3 else (4 if L <= cut4 else 5)
