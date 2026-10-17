"""The route model as a CRF, and its maximum-likelihood fit with exact inference (dev courses only).

A round is a sequence of N greens b_1..b_N, each with a hole hypothesis h_k (its tee complex). Log-potentials:

    u[b, h]      = th_form . phi_form[b, h]                         formation (solver.FEATS)
    start[b]     = lse_h( u[b, h] + a_t1  * As[b, h] )              tee 1 near the clubhouse H
    trans[a, b]  = lse_h( u[b, h] + th_trans . phi_trans[a, b, h] ) green a -> hole (b, h) (solver.TFEATS)
    turn[a, b]   = a_g9 * Ae[a] + lse_h( u[b, h] + a_t10 * As[b, h] + th_turn . phi_trans[a, b, h] )   (18 holes)
    end[a]       = a_g18 * Ae[a]                                    the last green near H
    As / Ae      = anchor log-lik (solver.anchor_ll) of the hole's nearest box / the green edge to H

P(route, hyps | H) = exp(sum of potentials) / Z_H, and H is latent with prior weights w_H. Z_H is the exact sum over all
routes of N out of M greens and all hypotheses (forward-backward over subsets, solver.route_dp's recursion with the
pairwise marginals xi kept). The gradient of the log-likelihood of the true route (truth: the OSM golf=hole ways of
the dev courses) is observed minus expected features, so every weight (formation, walk, direction, cart paths,
anchors, turn) is fitted jointly, the way it is used at inference.

    python course_data/structure/crf.py          -> params.json (form_w, trans_w, turn_w, anchor_w)
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solver as V                                                   # noqa: E402

ANCH = ("t1", "g18", "g9", "t10", "t1_d", "g18_d", "g9_d", "t10_d")
NEG = -1e30


def theta_names():
    return ([("form", k) for k in V.FEATS] + [("trans", k) for k in V.TFEATS] + [("turn", k) for k in V.TFEATS] +
            [("anchor", k) for k in ANCH])


def theta_from_params():
    out = []
    for grp, k in theta_names():
        if grp == "form":
            out.append(V.FORM_W.get(k, 0.0))
        elif grp == "trans":
            out.append(V.TRANS_W.get(k, 0.0))
        elif grp == "turn":
            out.append(V.TURN_W.get(k, 0.0))
        else:
            out.append(V.ANCHOR_W.get(k, 0.0 if k.endswith("_d") else 1.0))
    return np.array(out, float)


def split(theta):
    nf, nt = len(V.FEATS), len(V.TFEATS)
    return theta[:nf], theta[nf:nf + nt], theta[nf + nt:nf + 2 * nt], theta[nf + 2 * nt:]


def anc(ta, A, i):
    """Anchor potential i (0 t1, 1 g18, 2 g9, 3 t10): log-normal term + linear distance term."""
    return ta[i] * A[..., 0] + ta[4 + i] * A[..., 1]


def potentials(pb, se, theta, N, price=None, nh=None):
    """(trans, turn, start, end, parts) for one clubhouse candidate (se = pb.anchors(H))."""
    tf, tt, tu, ta = split(theta)
    As, Ae = se
    u = pb.Phi @ tf + pb.pad                                         # (M, K)
    if price is not None:
        u = u - pb.cov @ price
    if nh is not None:
        u = u - nh[:, None]
    gt = pb.F @ tt                                                   # (a, b, h)
    zt = u[None] + gt
    trans = V._lse(zt, axis=2)
    M = u.shape[0]
    eye = np.eye(M, dtype=bool)
    trans = np.where(eye, -1e4, trans)
    turn = zu = None
    if N == 18:
        zu = u[None] + anc(ta, As, 3)[None] + pb.F @ tu
        turn = np.where(eye, -1e4, anc(ta, Ae, 2)[:, None] + V._lse(zu, axis=2))
    z0 = u + anc(ta, As, 0)
    start = V._lse(z0, axis=1)
    end = anc(ta, Ae, 1)
    return trans, turn, start, end, dict(u=u, zt=zt, zu=zu, z0=z0)


def fb(trans, turn, start, end, N):
    """Forward-backward with pairwise marginals: logZ, marg (M x N), xi (normal moves, M x M), xi_turn."""
    M = trans.shape[0]
    layers = V._popcount_layers(M, N)
    bits = np.arange(M)
    alpha = np.full((1 << M, M), NEG)
    for j in range(M):
        alpha[1 << j, j] = start[j]
    for k in range(1, N):
        tr = turn if (turn is not None and k == 9) else trans
        idx = layers[k]
        bit = ((idx[:, None] >> bits[None, :]) & 1).astype(bool)
        new = idx[:, None] | (1 << bits)[None, :]
        rows, cols = np.nonzero(~bit)
        A = alpha[idx]
        am = A.max(1, keepdims=True)
        tm = tr.max(0, keepdims=True)
        B = np.log(np.maximum(np.exp(A - am) @ np.exp(tr - tm), 1e-300)) + am + tm
        alpha[new[rows, cols], cols] = B[rows, cols]
    last = layers[N]
    logZ = V._lse((alpha[last] + end[None, :]).ravel())
    beta = np.full((1 << M, M), NEG)
    beta[last] = np.broadcast_to(end[None, :], (len(last), M))
    xi = np.zeros((M, M))
    xi_t = np.zeros((M, M))
    for k in range(N - 1, 0, -1):
        tr = turn if (turn is not None and k == 9) else trans
        idx = layers[k]
        bit = ((idx[:, None] >> bits[None, :]) & 1).astype(bool)
        new = idx[:, None] | (1 << bits)[None, :]
        nb = np.where(bit, NEG, beta[np.where(bit, idx[:, None], new), bits[None, :]])
        nm = nb.max(1, keepdims=True)
        tm = tr.max(1, keepdims=True)
        Bk = np.log(np.maximum(np.exp(nb - nm) @ np.exp(tr - tm).T, 1e-300)) + nm + tm.T
        beta[idx] = np.where(bit, Bk, NEG)
        A = alpha[idx]
        am = A.max(1, keepdims=True)
        w = np.exp(np.clip(am + nm - logZ, -700, 700))[:, 0]
        x = (np.exp(A - am) * w[:, None]).T @ np.exp(nb - nm) * np.exp(np.clip(tr, -700, 700))
        if turn is not None and k == 9:
            xi_t += x
        else:
            xi += x
    marg = np.zeros((M, N))
    for k in range(N):
        idx = layers[k + 1]
        marg[:, k] = np.exp(np.clip(alpha[idx] + beta[idx] - logZ, -700, 0)).sum(0)
    return logZ, marg, xi, xi_t


def _softmax(z, axis):
    m = z.max(axis=axis, keepdims=True)
    e = np.exp(z - m)
    return e / e.sum(axis=axis, keepdims=True)


def course_obj(theta, pb, ses, wH, N, seq, hseq):
    """-log P(true route, true hyps) and its gradient for one course."""
    nth = len(theta)
    nf, nt = len(V.FEATS), len(V.TFEATS)
    lw_true, lw_Z, g_true, g_exp = [], [], [], []
    for se, w in zip(ses, wH):
        As, Ae = se
        trans, turn, start, end, P = potentials(pb, se, theta, N)
        # true route score and features
        s = P["z0"][seq[0], hseq[0]]
        g = np.zeros(nth)
        g[:nf] += pb.Phi[seq[0], hseq[0]]
        A0 = nf + 2 * nt
        g[[A0 + 0, A0 + 4]] += As[seq[0], hseq[0]]
        for k in range(1, N):
            a, b, h = seq[k - 1], seq[k], hseq[k]
            if N == 18 and k == 9:
                s += P["zu"][a, b, h] + anc(split(theta)[3], Ae[a], 2)
                g[:nf] += pb.Phi[b, h]
                g[nf + nt:nf + 2 * nt] += pb.F[a, b, h]
                g[[A0 + 2, A0 + 6]] += Ae[a]
                g[[A0 + 3, A0 + 7]] += As[b, h]
            else:
                s += P["zt"][a, b, h]
                g[:nf] += pb.Phi[b, h]
                g[nf:nf + nt] += pb.F[a, b, h]
        s += end[seq[-1]]
        g[[A0 + 1, A0 + 5]] += Ae[seq[-1]]
        logZ, marg, xi, xi_t = fb(trans, turn, start, end, N)
        e = np.zeros(nth)
        A0 = nf + 2 * nt
        q0 = _softmax(P["z0"], 1)                                    # (b, h)
        e[:nf] += np.einsum("b,bh,bhf->f", marg[:, 0], q0, pb.Phi)
        e[[A0 + 0, A0 + 4]] += np.einsum("b,bh,bhx->x", marg[:, 0], q0, As)
        q = _softmax(P["zt"], 2)                                     # (a, b, h)
        e[:nf] += np.einsum("ab,abh,bhf->f", xi, q, pb.Phi)
        e[nf:nf + nt] += np.einsum("ab,abh,abhf->f", xi, q, pb.F)
        if N == 18:
            qu = _softmax(P["zu"], 2)
            e[:nf] += np.einsum("ab,abh,bhf->f", xi_t, qu, pb.Phi)
            e[nf + nt:nf + 2 * nt] += np.einsum("ab,abh,abhf->f", xi_t, qu, pb.F)
            e[[A0 + 2, A0 + 6]] += xi_t.sum(1) @ Ae
            e[[A0 + 3, A0 + 7]] += np.einsum("ab,abh,bhx->x", xi_t, qu, As)
        e[[A0 + 1, A0 + 5]] += marg[:, N - 1] @ Ae
        lw_true.append(math.log(w) + s)
        lw_Z.append(math.log(w) + logZ)
        g_true.append(g)
        g_exp.append(e)
    lt, lz = np.array(lw_true), np.array(lw_Z)
    rt = np.exp(lt - V._lse(lt))
    rz = np.exp(lz - V._lse(lz))
    nll = -(V._lse(lt) - V._lse(lz))
    grad = -(rt @ np.array(g_true) - rz @ np.array(g_exp))
    return nll, grad


def build_training(entries, degrade=None, extra=0, max_h=2):
    """Per dev course: Problem over the true greens + `extra` other greens, the true sequence and hypotheses."""
    import random
    import eval as E
    import scene as S
    out = []
    for e in entries:
        sc, truth, N, _ = E.load(e)
        if N not in (9, 18):
            continue
        if degrade:
            sc = S.degrade(sc, random.Random(f"crf-{e['slug']}"), level=degrade)
        hyps, geo = V.hypotheses(sc, topk=V.TOPK)
        tg = [E.true_green(geo.G, geo.gr_r, t["green"]) for t in truth]
        if any(g is None for g in tg) or len(set(tg)) < N:
            continue
        allh, _ = V.hypotheses(sc, topk=400, geo=geo)
        hseq = []
        ok = True
        for t, g in zip(truth, tg):
            idx = [i for i, h in enumerate(hyps[g]) if E.tee_ok(h["tee"], list(geo.cx[h["k"]]["xy"]), t)]
            if not idx:
                cand = [h for h in allh[g] if E.tee_ok(h["tee"], list(geo.cx[h["k"]]["xy"]), t)]
                if not cand:
                    ok = False
                    break
                hyps[g] = hyps[g][:V.TOPK - 1] + [cand[0]]
                idx = [len(hyps[g]) - 1]
            hseq.append(idx[0])
        if not ok:
            continue
        others = [i for i in np.argsort([-(hs[0]["score"] if hs else -99) for hs in hyps]) if i not in tg][:extra]
        keep = sorted(tg + [int(i) for i in others])
        pb = V.Problem(sc, hyps, geo, keep)
        seq = [keep.index(g) for g in tg]
        Hc = (list(sc.clubhouse) + V.hub_candidates(sc, geo, hyps))
        Hc = sorted(Hc, key=lambda h: -h["w"])[:max_h]
        ses = [pb.anchors(H["c"]) for H in Hc]
        wH = np.array([H["w"] for H in Hc])
        out.append(dict(slug=e["slug"], pb=pb, ses=ses, wH=wH / wH.sum(), N=N, seq=seq, hseq=hseq))
    return out


def fit(data, theta0, l2=0.5):
    from scipy.optimize import minimize
    names = theta_names()

    def f(th):
        tot, g = 0.0, np.zeros_like(th)
        for d in data:
            v, gr = course_obj(th, d["pb"], d["ses"], d["wH"], d["N"], d["seq"], d["hseq"])
            tot += v
            g += gr
        tot += l2 * ((th - theta0) ** 2).sum()
        g += 2 * l2 * (th - theta0)
        return tot, g
    v0, _ = f(theta0)
    r = minimize(f, theta0, jac=True, method="L-BFGS-B", options=dict(maxiter=25))
    print("nll", round(v0, 2), "->", round(r.fun, 2), r.message)
    return r.x, dict(zip([f"{a}.{b}" for a, b in names], np.round(r.x, 3)))


def main():
    import argparse
    import eval as E
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--no-degraded", action="store_true")
    a = ap.parse_args()
    ents = E.courses("dev")
    if a.limit:
        ents = ents[:a.limit]
    data = build_training(ents)
    if not a.no_degraded:
        data += build_training(ents, degrade=1.0)
    print("training courses", len(data))
    th0 = theta_from_params()
    th, named = fit(data, th0)
    print(named)
    p = json.load(open(V.PARAMS_PATH)) if os.path.exists(V.PARAMS_PATH) else {}
    tf, tt, tu, ta = split(th)
    p["form_w"] = {k: round(float(v), 4) for k, v in zip(V.FEATS, tf)}
    p["trans_w"] = {k: round(float(v), 4) for k, v in zip(V.TFEATS, tt)}
    p["turn_w"] = {k: round(float(v), 4) for k, v in zip(V.TFEATS, tu)}
    p["anchor_w"] = {k: round(float(v), 4) for k, v in zip(ANCH, ta)}
    p["crf_note"] = f"joint max-likelihood fit (crf.py) on {len(data)} dev routes (clean + degraded)"
    json.dump(p, open(V.PARAMS_PATH, "w"), indent=1)


if __name__ == "__main__":
    main()
