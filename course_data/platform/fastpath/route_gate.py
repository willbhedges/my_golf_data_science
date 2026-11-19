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
import detector as _DET  # noqa: E402
PARAMS = _DET.routing_file("route_gate.json", "ROUTE_GATE_PARAMS")
FEATS = ["margin_c", "margin_lo", "card_rel", "card_bad", "virtual", "ob", "ph_lo", "cross", "ph_l", "pw_l", "pw_none", "g_l", "g_map", "t_l"]
MARGIN_CAP = 12.0
MIN_SHOWN = 3        # a threshold counts only when at least this many train courses clear it, all of them right: with
                     # 2 (d0+yall: willowhill 0.33, hatherly 0.17, then billy_caldwell 0.10 wrong) the blind loop's
                     # Remsen sat at 0.170 against 0.174, too thin a margin to show a course on
MIN_RATIO = 1.25     # ... and the threshold must sit 25 % above the best-scored wrong train course: 2026-11-16 (split tees,
                     # anchored virtual greens) 3 train courses clear 0.159, the next is wrong at 0.137 (ratio 1.15) and
                     # the top test course, wrong, scores 0.142


POLICY_ENV = "ROUTE_SHOW_POLICY"
APPROX_P = 0.5       # auto policy: a hole whose calibrated P(hole right) is below this is marked "approximate"
FALLBACK_P = 0.45    # cap on P(hole right) of a hole the shared-green fallback touched (so it is marked approximate)


def policy():
    """'auto' (default, product decision 2026-11-17): every scene-routed course with a complete routing is shown, no
    golfer confirms; each hole carries its calibrated P(hole right), holes under APPROX_P are marked approximate; only
    the hard blocks (no card, missing holes, card-order conflict, shared green, no routing) keep it a draft. Tier C
    (route_joint on OSM greens / tees, or unnumbered OSM hole lines) likewise, with p_joint (route_gate_joint.json).
    'calibrated': shown only when P(all holes right) clears the precision-1.0 threshold (the 2026-11-16 gate)."""
    v = (os.environ.get(POLICY_ENV) or "auto").strip().lower()
    return v if v in ("auto", "calibrated") else "auto"


def hole_x(h):
    m = min(float(h.get("margin") or 0.0), MARGIN_CAP)
    cr = h.get("card_rel")
    cr = 0.3 if cr is None else min(float(cr), 0.6)
    ph = h.get("ph")
    pw = h.get("pw")
    return [m / MARGIN_CAP, float(m < 2.0), cr, float(cr > 0.15), float(h.get("kind", 0) != 0),
            float(h.get("ob") or 0.0), float(ph is None or ph < 0.1), float(h.get("cross") or 0),
            _logit(ph) / 4.0, _logit(pw) / 4.0, float(pw is None), _logit(h.get("gp")) / 4.0, float(h.get("gmap") or 0),
            _logit(h.get("tp")) / 4.0]


def _logit(p):
    if p is None:
        return 0.0
    p = min(max(float(p), 0.01), 0.99)
    return math.log(p / (1 - p))


def _sets(card, n):
    out = []
    for s in ((card or {}).get("tee_sets") or {}).values():
        y = s.get("yards") or []
        if len(y) >= n and all(v for v in y[:n]):
            out.append(np.asarray(y[:n], float))
    return out


def card_order_conflict(card, others, n, order_yd=25.0, same_yd=15.0):
    """True when another web card holds the same holes (sorted yardages within same_yd, median) in a different order
    (hole by hole off by more than order_yd, median): the sources disagree on the numbering, so the card cannot
    number the routed holes. others: card dicts (tee_sets)."""
    a = _sets(card, n)
    for o in others or []:
        b = _sets(o, n)
        if not a or not b or o is card:
            continue
        idm = min(float(np.median(np.abs(x - y))) for x in a for y in b)
        srt = min(float(np.median(np.abs(np.sort(x) - np.sort(y)))) for x in a for y in b)
        if idm > order_yd and srt < same_yd:
            return True
    return False


def load(path=PARAMS):
    return json.load(open(path)) if os.path.exists(path) else None


def p_all(routed, params=None):
    """-> (P(all holes right), per-hole p) for a route_scene.route v1 result (None without a fitted gate)"""
    params = params or load()
    hf = routed.get("hole_features") or []
    if params is None or not hf:
        return None, []
    w = np.asarray(params["w"], float)
    X = np.array([hole_x(h) for h in hf], float)[:, :len(w) - 1]          # a gate fitted on fewer features
    z = X @ w[1:] + w[0]
    p = 1.0 / (1.0 + np.exp(-z))
    # holes the shared-green fallback (route_scene._shared_fallback) moved or that held the shared green: approximate
    fb = np.array([bool(h.get("fallback")) for h in hf])
    p = np.where(fb, np.minimum(p, FALLBACK_P), p)
    return float(np.prod(p)), [round(float(v), 4) for v in p]


def decide(routed, params=None, show_policy=None):
    """-> dict(show, p_all, threshold, reasons, p_holes, policy, approximate). Hard blocks first: no routing, no card,
    card-order conflict, a hole with neither end, a missing hole. Policy 'calibrated' adds the P(all) threshold;
    'auto' does not (approximate = indices of holes with p < APPROX_P)."""
    params = params or load()
    show_policy = show_policy or policy()
    reasons = []
    n = int(routed.get("n_holes") or 0)
    if not routed.get("hole_features"):
        reasons.append("no routing")
    if routed.get("has_card") is False:
        reasons.append("no scorecard yardages: the hole order is a guess without them")
    if routed.get("card_conflict"):
        reasons.append("the web scorecards disagree on the hole order: the card cannot number the holes")
    if routed.get("n_miss"):
        reasons.append(f"{routed['n_miss']} holes with neither tee nor green found")
    if len(routed.get("hole_features") or []) < n:
        reasons.append(f"only {len(routed.get('hole_features') or [])} of {n} holes routed")
    p, ph = p_all(routed, params)
    thr = float(params["threshold"]) if params else 1.1
    approx = [i for i, v in enumerate(ph) if v < APPROX_P]
    if show_policy == "auto":
        return dict(show=not reasons, p_all=p, threshold=thr, reasons=reasons, p_holes=ph, policy="auto",
                    approximate=approx)
    if p is None:
        reasons.append("no calibrated gate (route_gate.json)")
    elif p < thr:
        weak = sorted(range(len(ph)), key=lambda i: ph[i])[:3]
        reasons.append(f"routing confidence {p:.3f} < {thr:.3f} (least certain holes: "
                       + ", ".join(f"{i + 1} ({ph[i]:.2f})" for i in weak) + ")")
    return dict(show=not reasons, p_all=p, threshold=thr, reasons=reasons, p_holes=ph, policy="calibrated",
                approximate=approx)


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


def pick_threshold(cur, n_courses, min_shown=1, min_ratio=1.0):
    """the lowest threshold whose shown set is still all right (precision 1.0) with at least min_shown courses above
    it, and at least min_ratio times the P(all) of the best-scored wrong course; 1.1 (show nothing) when none"""
    best = 1.1
    wrong = next((r["threshold"] for r in cur if r["right"] != r["shown"]), 0.0)
    for r in cur:
        if r["right"] != r["shown"]:
            break
        if r["shown"] >= min_shown and r["threshold"] >= min_ratio * wrong:
            best = r["threshold"]
    return best


def _sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


# ----------------------------------------------------------------------------- tier C (route_joint) per-hole confidence
JOINT_PARAMS = os.path.join(HERE, "route_gate_joint.json")
JFEATS = ["margin_c", "margin_lo", "card_rel", "card_bad", "course_mg", "virt_frac", "lines_mode"]


def _line_yd(co):
    a = np.asarray(co, float)
    k = math.cos(math.radians(a[:, 1].mean()))
    return float(np.hypot(np.diff(a[:, 0]) * k, np.diff(a[:, 1])).sum() * 111320.0 / 0.9144)


def joint_card_rel(feats, card, n):
    """{ref: |routed length - card| / card} for the card tee set that fits the routed lines best (median)"""
    L = {str(f["properties"]["ref"]): _line_yd(f["geometry"]["coordinates"]) for f in feats or []}
    best = None
    for s in ((card or {}).get("tee_sets") or {}).values():
        y = list(s.get("yards") or [])
        if len(y) < n and y and n % len(y) == 0:
            y = y * (n // len(y))
        r = {k: abs(L[k] - y[int(k) - 1]) / max(float(y[int(k) - 1]), 1.0) for k in L if int(k) - 1 < len(y) and y[int(k) - 1]}
        if r and (best is None or np.median(list(r.values())) < np.median(list(best.values()))):
            best = r
    return best or {}


def joint_rows(routed, card_rel, mode):
    """per routed hole: feature dicts for the tier C calibration (margins indexed by position)"""
    n = int(routed.get("n_holes") or 0) or len(routed.get("margins") or [])
    mg = routed.get("margins") or []
    cmg = min(float(routed.get("min_margin") or 0.0), MARGIN_CAP)
    vf = float(routed.get("n_virtual") or 0) / max(n, 1)
    out = []
    for ref, cr in sorted(card_rel.items(), key=lambda kv: int(kv[0])):
        i = int(ref) - 1
        m = min(float(mg[i]) if i < len(mg) else 0.0, MARGIN_CAP)
        out.append(dict(ref=ref, margin=m, card_rel=cr, course_mg=cmg, virt=vf, lines=float(mode == "lines")))
    return out


def joint_x(h):
    cr = min(float(h["card_rel"]), 0.6)
    return [h["margin"] / MARGIN_CAP, float(h["margin"] < 2.0), cr, float(cr > 0.15), h["course_mg"] / MARGIN_CAP,
            h["virt"], h["lines"]]


def fit_joint(rows, l2=1.0, iters=3000, lr=0.5):
    """rows: [(hole feature dict, ok)] -> weights [bias, w...] (L2 logistic, as fit)"""
    X = np.asarray([joint_x(h) for h, _ in rows], float)
    y = np.asarray([float(ok) for _, ok in rows], float)
    A = np.c_[np.ones(len(X)), X]
    w = np.zeros(A.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(A @ w)))
        w -= lr * (A.T @ (p - y) / len(y) + l2 * np.r_[0.0, w[1:]] / len(y))
    return [float(v) for v in w]


def p_joint(rows, params=None):
    """-> {ref: calibrated P(hole numbered right)} for a route_joint routing (None without route_gate_joint.json)"""
    if params is None:
        params = json.load(open(JOINT_PARAMS)) if os.path.exists(JOINT_PARAMS) else None
    if params is None or not rows:
        return None
    w = np.asarray(params["w"], float)
    X = np.asarray([joint_x(h) for h in rows], float)
    p = 1.0 / (1.0 + np.exp(-(X @ w[1:] + w[0])))
    return {h["ref"]: round(float(v), 4) for h, v in zip(rows, p)}
