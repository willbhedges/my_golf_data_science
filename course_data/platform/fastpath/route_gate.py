"""Show / block for a course whose holes were routed on imagery detections (route_scene.route version v1).

No golfer questions: a course is shown only when the calibrated probability that EVERY hole is numbered right is at
least the threshold; otherwise it is a draft (not shown), with the reason.

    p_hole = sigmoid(w . x_hole)          per-hole logistic model: solver margin (min-marginal, capped), card fit of
                                          the routed line (|length - card| / card), virtual / missing end, line over
                                          buildings / roads, hole-model probability, crossings
    P(all right) = prod_i p_hole_i        (holes treated as independent: conservative when errors come in runs)
    show  <=>  P(all right) >= THRESHOLD and the hard blocks pass (a missing hole, a shared green, the card not
               fitting 3+ holes by more than 25 yd: fast.extra_gate)

Fitted on the routing bench's TRAIN split (validation set simulated unmapped, real fastscene scenes; route_bench.py
gate fit), threshold chosen there for precision 1.0 on shown courses; test is only reported (route_gate.json holds
the weights, the threshold and both curves).
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = os.path.join(HERE, "route_gate.json")
FEATS = ["margin_c", "margin_lo", "card_rel", "card_bad", "virtual", "ob", "ph_lo", "cross"]
MARGIN_CAP = 12.0


def hole_x(h):
    m = min(float(h.get("margin") or 0.0), MARGIN_CAP)
    cr = h.get("card_rel")
    cr = 0.3 if cr is None else min(float(cr), 0.6)
    ph = h.get("ph")
    return [m / MARGIN_CAP, float(m < 2.0), cr, float(cr > 0.15), float(h.get("kind", 0) != 0),
            float(h.get("ob") or 0.0), float(ph is None or ph < 0.1), float(h.get("cross") or 0)]


def load(path=PARAMS):
    return json.load(open(path)) if os.path.exists(path) else None


def p_all(routed, params=None):
    """-> (P(all holes right), per-hole p) for a route_scene.route v1 result (None without a fitted gate)"""
    params = params or load()
    hf = routed.get("hole_features") or []
    if params is None or not hf:
        return None, []
    w = np.asarray(params["w"], float)
    X = np.array([hole_x(h) for h in hf], float)
    z = X @ w[1:] + w[0]
    p = 1.0 / (1.0 + np.exp(-z))
    return float(np.prod(p)), [round(float(v), 4) for v in p]


def decide(routed, params=None):
    """-> dict(show, p_all, threshold, reasons). Hard blocks first: no routing, a missing hole."""
    params = params or load()
    reasons = []
    n = int(routed.get("n_holes") or 0)
    if not routed.get("hole_features"):
        reasons.append("no routing")
    if routed.get("has_card") is False:
        reasons.append("no scorecard yardages: the hole order is a guess without them")
    if routed.get("n_miss"):
        reasons.append(f"{routed['n_miss']} holes with neither tee nor green found")
    if len(routed.get("hole_features") or []) < n:
        reasons.append(f"only {len(routed.get('hole_features') or [])} of {n} holes routed")
    p, ph = p_all(routed, params)
    thr = float(params["threshold"]) if params else 1.1
    if p is None:
        reasons.append("no calibrated gate (route_gate.json)")
    elif p < thr:
        weak = sorted(range(len(ph)), key=lambda i: ph[i])[:3]
        reasons.append(f"routing confidence {p:.3f} < {thr:.3f} (least certain holes: "
                       + ", ".join(f"{i + 1} ({ph[i]:.2f})" for i in weak) + ")")
    return dict(show=not reasons, p_all=p, threshold=thr, reasons=reasons, p_holes=ph)


def fit(courses, l2=1.0, iters=3000, lr=0.5):
    """courses: [dict(hole_features=[...], hole_ok=[bool per hole])]. Plain L2 logistic regression (numpy, no
    sklearn dependence at run time). -> weights [bias, w...]"""
    X, y = [], []
    for c in courses:
        for h, ok in zip(c["hole_features"], c["hole_ok"]):
            X.append(hole_x(h))
            y.append(float(ok))
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    A = np.c_[np.ones(len(X)), X]
    w = np.zeros(A.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(A @ w)))
        g = A.T @ (p - y) / len(y) + l2 * np.r_[0.0, w[1:]] / len(y)
        w -= lr * g
    return [float(v) for v in w]


def curve(courses, w):
    """(threshold, shown, shown with every hole right) over the distinct P(all) values, high to low"""
    ps = []
    for c in courses:
        hf = c.get("hole_features") or []
        if not hf or c.get("hard_block"):
            ps.append((-1.0, c["all_right"]))
            continue
        p, _ = p_all(dict(hole_features=hf), dict(w=w, threshold=0))
        ps.append((p, c["all_right"]))
    ps.sort(key=lambda t: -t[0])
    out = []
    shown = right = 0
    for p, ok in ps:
        if p < 0:
            break
        shown += 1
        right += int(ok)
        out.append(dict(threshold=round(p, 5), shown=shown, right=right, precision=round(right / shown, 3)))
    return out


def pick_threshold(cur, n_courses, min_shown=1):
    """the lowest threshold whose shown set is still all right (precision 1.0); 1.1 (show nothing) when none"""
    best = 1.1
    for r in cur:
        if r["right"] == r["shown"] and r["shown"] >= min_shown:
            best = r["threshold"]
        else:
            break
    return best


def _sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))
