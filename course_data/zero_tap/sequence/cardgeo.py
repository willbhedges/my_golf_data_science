"""Tee pairing with the scorecard's own geometry (zero-tap sequence v3).

The v2 route CRF used the card as one number per hole: the longest tee set's yardage against the straight length of
the hole's back tee, marginalised over the tee hypotheses (structure/solver._card_pos), so the card never chose
between two tees of one green. This module scores every (green node, tee hypothesis h, card hole k) jointly:

  back     the hypothesis' back box is the box of one of the card's tee sets (normally the longest; a shorter one
           when the back box is not mapped): straight length vs that set's yardage, measured >= straight (dog-legs)
  nest     every other distinct yardage of the hole must have a box on the same line of play (the hypothesis' own
           complex + the forward complexes it covers), at the distance the card's differences predict:
           d(box) = D_back - (Y_anchor - Y_i); a set with no box there is an outlier (OSM / perception miss boxes)
  par      each tee set's par for the hole against the par-by-length prior of that set's yardage (a set whose par
           differs from the men's par, e.g. a women's par 5, is checked against its own yardage)
  hcp      the card's handicap order: among par-4 / par-5 holes the harder (lower index) holes are longer for their
           par; a weak per-node term from the hypothesis length relative to the par mean (fitted weight, may be 0)

-> card_hk (M, K, N): log-likelihood ratios per kept node, hypothesis and card position, added inside the route
DP's per-position tee sum (joint.solve(card_hk=...)). Parameters are fitted on dev courses only (fit_cardgeo.py).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(CD, "structure"))
import solver as V                                                   # noqa: E402

PARAMS_PATH = os.path.join(HERE, "cardgeo_params.json")
DEFAULT = dict(
    sd_a=0.05, sd_b=12.0,       # back: sd = sd_a * Y + sd_b
    dogleg=2.0,                 # measured > straight is dog-leg slack: sd x dogleg on that side
    back_out=0.1,               # back: outlier mass (uniform over 600 yds)
    anchor_p0=0.8,              # P(the back box is the longest set's box); the rest spread over shorter sets
    nest_sd=10.0,               # nest: sd of a forward box's distance around the card's prediction
    nest_pi=0.55,               # nest: P(a shorter set's box is on the map)
    nest_R=150.0,               # nest: outlier density 1 / R
    nest_min=8.0,               # distinct yardages: sets within this of each other share a box
    par_w=0.0,                  # weight of the per-set par-by-length term
    hcp_w=0.0,                  # weight of the handicap-order term
    clip_lo=-20.0, clip_hi=12.0,
)


def load(path=PARAMS_PATH):
    p = dict(DEFAULT)
    if os.path.exists(path):
        p.update(json.load(open(path)).get("params", {}))
    return p


# ----------------------------------------------------------------------------- the card per hole
def card_holes(card, N):
    """scorecard/1 -> per hole k < N: dict(Y=[distinct yardages, longest first], sets=[(yards, par)], par, hcp)."""
    out = [dict(Y=[], sets=[], par=None, hcp=None) for _ in range(N)]
    if not card:
        return out
    pars = card.get("par") or card.get("pars")
    hcp = card.get("handicap")
    ts = card.get("tee_sets") or {}
    if not ts and card.get("yards"):
        ts = {"card": dict(yards=card["yards"], par=pars)}
    for name, t in ts.items():
        y = t.get("yards") if isinstance(t, dict) else t
        tp = (t.get("par") if isinstance(t, dict) else None) or pars
        if not y:
            continue
        for k in range(min(N, len(y))):
            v = y[k]
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            if not (50 <= v <= 750):
                continue
            pk = None
            if tp and k < len(tp) and tp[k]:
                try:
                    pk = int(tp[k])
                except (TypeError, ValueError):
                    pk = None
            out[k]["sets"].append((v, pk))
        if hcp is None and isinstance(t, dict) and t.get("handicap"):
            hcp = t["handicap"]
    for k in range(N):
        if pars and k < len(pars) and pars[k]:
            try:
                out[k]["par"] = int(pars[k])
            except (TypeError, ValueError):
                pass
        if hcp and k < len(hcp) and hcp[k]:
            try:
                out[k]["hcp"] = int(hcp[k])
            except (TypeError, ValueError):
                pass
        ys = sorted({s[0] for s in out[k]["sets"]}, reverse=True)
        Y = []
        for v in ys:
            if not Y or Y[-1] - v >= DEFAULT["nest_min"]:
                Y.append(v)
        out[k]["Y"] = Y
    return out


# ----------------------------------------------------------------------------- the hypothesis' boxes
def box_dists(geo, gi, h):
    """Distances (yds) green centre -> every box on the hypothesis' line of play (its complex + covered forward
    complexes), longest first."""
    g = geo.G[gi]
    ks = set(h.get("cover") or []) | {h["k"]}
    d = []
    for k in ks:
        xy = np.asarray(geo.cx[k]["xy"], float).reshape(-1, 2)
        d.extend(np.hypot(*(xy - g).T).tolist())
    d = np.array(sorted(d, reverse=True))
    return d[d <= h["D"] + 1.0]


def _back_ll(D, Y, P):
    sd = P["sd_a"] * Y + P["sd_b"]
    z = (D - Y) / sd if D > Y else (D - Y) / (P["dogleg"] * sd)
    return math.log((1 - P["back_out"]) * math.exp(-0.5 * z * z) / (sd * 2.5) + P["back_out"] / 600.0) + math.log(600.0)


def _nest_ll(d, e, P):
    """One shorter set: its box predicted at straight distance e; d = the hypothesis' box distances."""
    if not len(d):
        best = 0.0
    else:
        r = (d - e) / P["nest_sd"]
        best = float(np.exp(-0.5 * r * r).max()) / (P["nest_sd"] * 2.5066)
    num = P["nest_pi"] * best + (1 - P["nest_pi"]) / P["nest_R"]
    return math.log(num * P["nest_R"])                           # ratio vs the outlier density


def hole_ll(D, d, hk, P, base=None, ppar=None, nest=True):
    """Log-likelihood ratio of a hypothesis (back length D, box distances d) being card hole hk."""
    Y = hk["Y"]
    if not Y:
        if hk.get("par") and ppar is not None:
            p = min(max(hk["par"], 3), 5)
            return math.log(max(ppar[p - 3], 1e-3) / V.PAR_PI[p])
        return 0.0
    if base is None:
        base = float(V.length_loglik(np.array([D]))[0][0])
    terms = []
    m = len(Y)
    fwd = d[d < D - 3.0]
    for j in range(m if nest else 1):
        lp = math.log(P["anchor_p0"]) if j == 0 else math.log((1 - P["anchor_p0"]) / max(m - 1, 1))
        t = lp + _back_ll(D, Y[j], P) - base
        if nest:
            for i in range(j + 1, m):
                e = D - (Y[j] - Y[i])
                if e < 40:
                    continue
                t += _nest_ll(fwd, e, P)
        terms.append(t)
    ll = float(V._lse(np.array(terms))) if len(terms) > 1 else terms[0]
    if P.get("par_w") and ppar is not None:
        pars = [s[1] for s in hk["sets"] if s[1]]
        if pars:
            p = min(max(int(round(np.median(pars))), 3), 5)
            ll += P["par_w"] * math.log(max(ppar[p - 3], 1e-3) / V.PAR_PI[p])
    return ll


def hcp_node(D, hk, P, card_rows):
    """Handicap order: z = (hypothesis length - mean card length for that par) / sd, against the card's handicap
    rank among holes of that par (low index = hard = long). -> log-ratio, weight hcp_w."""
    if not P.get("hcp_w") or hk.get("hcp") is None or hk.get("par") not in (4, 5):
        return 0.0
    same = [r for r in card_rows if r.get("par") == hk["par"] and r.get("hcp") is not None]
    if len(same) < 3:
        return 0.0
    rank = sorted(r["hcp"] for r in same).index(hk["hcp"]) / (len(same) - 1)       # 0 hardest .. 1 easiest
    mu = V.PAR_MU[hk["par"]]
    sd = V.PAR_SD[hk["par"]]
    z = (D - mu) / sd
    return P["hcp_w"] * (0.5 - rank) * z


def card_hk(sc, geo, hyps, keep, card, N, P=None, nest=True):
    """(M, K, N) card log-likelihood ratios for the kept nodes' hypotheses (padding 0), or None without a card."""
    if not card:
        return None
    P = P or load()
    rows = card_holes(card, N)
    if not any(r["Y"] or r["par"] for r in rows):
        return None
    K = max(1, max(len(hyps[g]) for g in keep))
    out = np.zeros((len(keep), K, N))
    for b, g in enumerate(keep):
        hs = hyps[g][:K]
        if not hs:
            continue
        Ds = np.array([h["D"] for h in hs])
        base, pp = V.length_loglik(Ds)
        for hi, h in enumerate(hs):
            d = box_dists(geo, g, h)
            for k in range(N):
                v = hole_ll(h["D"], d, rows[k], P, base=float(base[hi]), ppar=pp[:, hi], nest=nest)
                v += hcp_node(h["D"], rows[k], P, rows)
                out[b, hi, k] = v
    return np.clip(out, P["clip_lo"], P["clip_hi"])
