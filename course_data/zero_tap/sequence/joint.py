"""Joint order-of-play solver (zero-tap workstream C).

The route CRF of course_data/structure/ (exact Held-Karp over the greens, tee choice summed out inside each move,
clubhouse latent) with hooks for the other workstreams and for the anchor / nine models of this package:

  hyps / keep    formation: the structure solver's hypotheses (default), workstream A's hole_pairs/1 re-scoring
                 them (pairs.py), or the true pairs (oracle, for measuring the sequence alone)
  cands          clubhouse candidates with prior weights (anchors.clubhouse_candidates; default: structure's)
  pos_extra      position evidence, log-ratio per (kept green, hole number): workstream B's hole_evidence/1
  nine           front / back nine model (anchors.NineModel; default: structure's classifier)

solve() returns the structure-style result plus `diag`, the quantities the certainty gate reads.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(CD, "structure"))
import solver as V                                                   # noqa: E402
import crf                                                           # noqa: E402

LAGR_ITERS = 12


def default_cands(sc, geo, hyps, use_clubhouse=True):
    return (list(sc.clubhouse) if use_clubhouse else []) + V.hub_candidates(sc, geo, hyps)


def choose_keep(sc, hyps, geo, N, max_greens=19):
    n_guess, asg = V.n_holes_guess(hyps, len(geo.C), return_scores=True)
    best_form = np.array([hs[0]["score"] if hs else -30.0 for hs in hyps])
    gconf = np.array([g.get("p_hole", g.get("conf", 1.0)) for g in sc.greens])
    nothole = V.NOT_HOLE + np.log(np.maximum(gconf, 0.02)) - 0.5 * np.log(np.maximum(1 - gconf, 0.02))
    order = np.argsort(-(asg + 0.3 * best_form + nothole))
    nG = len(sc.greens)
    M = max(min(nG, max_greens, N + 3), min(nG, N))
    return sorted(order[:M].tolist()), nothole, n_guess


def solve(sc, card=None, n_holes=None, use_paths=True, hyps=None, geo=None, keep=None, cands=None,
          pos_extra=None, pad_extra=None, nine=None, max_h=6, max_greens=19, hyps_all=None):
    """-> result dict (holes numbered 1..N, as structure.solver.solve) with result['diag'] for the gate.

    hyps/geo: formation hypotheses (structure.solver.hypotheses output, possibly re-scored / restricted);
    keep: the greens the route may use (default: the structure solver's choice); cands: [{c, w, how}];
    pos_extra: (len(keep), N) log-ratios; pad_extra: (len(keep), K) formation offsets added to the potentials."""
    temp = V.TEMP
    if hyps is None:
        hyps, geo = V.hypotheses(sc, topk=V.TOPK, clubs=list(sc.clubhouse))
    pars, yards = V.card_info(card)
    if keep is None:
        n_guess = V.n_holes_guess(hyps, len(geo.C))
        N = n_holes or (len(pars) if pars else (len(yards) if yards else n_guess))
        keep, nothole, _ = choose_keep(sc, hyps, geo, N, max_greens)
    else:
        N = n_holes or len(keep)
        gconf = np.array([g.get("p_hole", g.get("conf", 1.0)) for g in sc.greens])
        nothole = V.NOT_HOLE + np.log(np.maximum(gconf, 0.02)) - 0.5 * np.log(np.maximum(1 - gconf, 0.02))
    if len(keep) < N:
        N = len(keep)
    if N < 2 or not len(geo.C):
        return dict(status="no_greens_or_tees", holes=[], n_holes=N, diag={})
    pb = V.Problem(sc, hyps, geo, keep, use_paths=use_paths)
    if pad_extra is not None:
        pb.pad = pb.pad + pad_extra[:, :pb.K]
    Mk = len(keep)
    nh = nothole[keep]
    Hc = cands if cands is not None else default_cands(sc, geo, hyps_all or hyps)
    Hc = sorted(Hc, key=lambda h: -h["w"])[:max_h]
    if not Hc:
        Hc = V.hub_candidates(sc, geo, hyps_all or hyps)[:1]
    wsum = sum(h["w"] for h in Hc)
    pos_base = V._card_pos(pb.hk, pars, yards, N) if (pars or yards) else None
    pp = V._par_pos(pb.hk, N)
    if pp is not None:
        pos_base = pp if pos_base is None else pos_base + pp
    if pos_extra is not None:
        pos_base = pos_extra if pos_base is None else pos_base + pos_extra
    price = np.zeros(len(geo.C) + 1)
    anchors = [pb.anchors(H["c"]) for H in Hc]
    theta = crf.theta_from_params()

    def mats(st_en, lam, parts=False):
        trans, turn, start, end, P = crf.potentials(pb, st_en, theta, N, price=lam, nh=nh)
        out = (trans / temp, None if turn is None else turn / temp, start / temp, end / temp)
        return (out, P) if parts else out

    def run_all(lam, marginals, only=None, soft=True):
        runs = []
        for i, (H, se) in enumerate(zip(Hc, anchors)):
            if only is not None and i not in only:
                continue
            trans, turn, start, end = mats(se, lam)
            r = V.route_dp(trans, start, end, N, turn=turn, pos=None if pos_base is None else pos_base / temp,
                           marginals=marginals, soft=soft)
            r.update(H=H, se=se, i=i, logw=r["logZ"] + math.log(H["w"] / wsum),
                     mapw=r["best_score"] + math.log(H["w"] / wsum))
            runs.append(r)
        return runs

    runs = run_all(price, marginals=False, soft=False)
    top = sorted(runs, key=lambda r: -r["mapw"])[:4]
    only = {r["i"] for r in top}
    best_i = {top[0]["i"]}
    lagr_conflict = 0
    for it in range(LAGR_ITERS):
        br = max(runs, key=lambda r: r["mapw"])
        cnt = V._coverage(pb, mats(br["se"], price, parts=True)[1], br["best"], N)
        if cnt.max() <= 1:
            break
        lagr_conflict = it + 1
        price = price + 1.0 * (cnt > 1) * (1 + 0.5 * it)
        runs = run_all(price, marginals=False, only=best_i, soft=False)
    runs = run_all(price, marginals=True, only=only)
    lw = np.array([r["logw"] for r in runs])
    pw = np.exp(lw - V._lse(lw))
    marg = sum(p * r["marg"] for p, r in zip(pw, runs))
    br = max(runs, key=lambda r: r["mapw"])
    br["mats"], br["parts"] = mats(br["se"], price, parts=True)
    seq = list(br["best"])
    # the DP's own P(MAP route) under the mixture of clubhouse candidates
    p_route_mix = float(sum(p * math.exp(min(0.0, V.route_score(mats(r["se"], price), seq) +
                                              (0.0 if pos_base is None else sum(pos_base[n, k] / temp for k, n in enumerate(seq)))
                                              - r["logZ"])) for p, r in zip(pw, runs)))
    p_front = None
    p_front_dp = None
    sw_x = None
    if N == 18 and not (pars or yards):
        sw = seq[9:] + seq[:9]
        dp = V.route_score(br["mats"], seq) - V.route_score(br["mats"], sw)
        p_front_dp = 1 / (1 + math.exp(-max(-30, min(30, dp))))
        if nine is not None:
            p, sw_x = nine.prob(sc, geo, pb, br, seq, Hc, pw, runs, dp)
        else:
            x = V.route_swap_x(sc, geo, pb, br, seq)
            x["dp"] = dp
            z = sum((V.SWAP_W or {}).get(k, 0.0) * x.get(k, 0.0) for k in V.SWAP_FEATS)
            p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            sw_x = x
        if p < 0.5:
            seq, p = sw, 1 - p
        p_front = p
        sym = marg + np.roll(marg, 9, axis=1)
        marg = np.clip(sym * p, 0, 1)
    holes = []
    ptee = []
    for k, node in enumerate(seq):
        gi = pb.keep[node]
        hs = pb.hk[node]
        lp = V._tee_lp(br["parts"], seq, k, N) / temp
        ph = np.exp(lp - V._lse(lp))
        hi = int(np.argmax(ph))
        h = hs[hi]
        cx = geo.cx[h["k"]]
        ptee.append(float(ph[hi]))
        holes.append(dict(number=k + 1, green=sc.greens[gi]["id"], green_xy=[float(x) for x in geo.G[gi]],
                          tee_complex=cx["id"], tee=sc.tees[cx["boxes"][0]]["id"],
                          tee_xy=[float(x) for x in h["tee"]], boxes=[sc.tees[b]["id"] for b in cx["boxes"]],
                          length_yd=round(h["D"], 1), p_par=[round(float(x), 3) for x in h["ppar"]],
                          p_number=round(float(marg[node, k]), 4), p_tee=round(float(ph[hi]), 4),
                          confidence=round(float(marg[node, k]) * float(ph[hi]), 4), form_score=round(h["score"], 2)))
    pars_inf = V.infer_pars([h["p_par"] for h in holes], N)
    for h, p in zip(holes, pars_inf):
        h["par"] = p
    if pars:
        for h, p in zip(holes, pars):
            if p:
                h["par"] = int(p)
    par_conf = [1.0 if (pars and k < len(pars) and pars[k]) else float(max(h["p_par"])) for k, h in enumerate(holes)]
    used = {pb.keep[n] for n in seq}
    # card fit: straight length vs card yards per hole (in route order)
    card_resid = None
    if yards:
        r = [abs(h["length_yd"] - y) / max(y, 1) for h, y in zip(holes, yards) if y]
        card_resid = r
    diag = dict(N=N, M=Mk, n_greens=len(sc.greens), n_cx=len(geo.cx), n_tees=len(sc.tees), K=pb.K,
                p_route=float(math.exp(min(0.0, br["best_score"] - br["logZ"]))), p_route_mix=p_route_mix,
                pw=[float(x) for x in pw], H_how=[r["H"]["how"] for r in runs], H_c=[list(map(float, r["H"]["c"])) for r in runs],
                br_how=br["H"]["how"], p_front=p_front, p_front_dp=p_front_dp, swap_x=sw_x,
                marg_num=[float(marg[n, k]) for k, n in enumerate(seq)], p_tee=ptee,
                marg_max_other=[float(np.delete(marg[n], k).max()) if N > 1 else 0.0 for k, n in enumerate(seq)],
                lagr_conflict=lagr_conflict, card=bool(pars or yards), card_resid=card_resid,
                unused_greens=len(sc.greens) - N, form_top_gap=[_gap(pb.hk[n]) for n in seq],
                walk_in=[float(pb.wd[seq[k - 1]][n][int(np.argmax(V._tee_lp(br["parts"], seq, k, N)))]) if k else None
                         for k, n in enumerate(seq)],
                par_conf=par_conf, seq=[int(pb.keep[n]) for n in seq], keep=[int(x) for x in keep])
    return dict(schema="course_structure/1", status="ok", n_holes=N, holes=holes, card_used=bool(pars or yards),
                practice_greens=[sc.greens[i]["id"] for i in range(len(sc.greens)) if i not in used],
                clubhouse=dict(xy=[float(x) for x in br["H"]["c"]], how=br["H"]["how"],
                               p=round(float(pw[runs.index(br)]), 3)),
                total_par=int(sum(h["par"] for h in holes)), p_front_nine=p_front, diag=diag,
                _debug=dict(pb=pb, geo=geo, br=br, runs=runs, marg=marg, seq=seq, Hc=Hc))


def _gap(hs):
    if len(hs) < 2:
        return 10.0
    return float(hs[0]["score"] - hs[1]["score"])


def oracle_hyps(sc, truth, geo, hyps_all, tee_ok, true_green):
    """Formation given: per true green, the single best hypothesis whose tee matches the true hole's.
    -> (hyps restricted, keep) or None when a true hole has no matching hypothesis."""
    tg = [true_green(geo.G, geo.gr_r, t["green"]) for t in truth]
    if any(g is None for g in tg) or len(set(tg)) < len(tg):
        return None
    out = [[] for _ in hyps_all]
    for t, g in zip(truth, tg):
        cand = [h for h in hyps_all[g] if tee_ok(h["tee"], list(geo.cx[h["k"]]["xy"]), t)]
        if not cand:
            return None
        out[g] = [cand[0]]
    return out, sorted(tg)
