"""The course-level certainty gate: P(every hole number right) and the 'certain' flag.

    python course_data/zero_tap/sequence/gate.py fit  rows_dev.json            -> gate_params.json (dev only)
    python course_data/zero_tap/sequence/gate.py eval rows_*.json --split heldout,valtest -> gate_eval.json + .md

Model: L2 logistic regression on course-level features of the solved route (posterior of the MAP route, the
weakest hole's number / tee marginals, front-nine probability, clubhouse posterior, card fit, unused greens,
formation margins, ...), then isotonic calibration of 5-fold cross-fitted dev scores (grouped by course) ->
confidence. Fitted on the production modes only (struct, struct_card and, when present, pairs / evidence modes).

Threshold ('certain' = confidence >= t), chosen on the cross-fitted dev scores:
  * conformal / zero-error rule: t is just above the highest-scoring wrong dev course, so the calibration set has no
    false 'certain' (with n < 100 certified calibration courses, a 1 % error budget allows zero errors);
  * Learn-then-Test (binomial tail, delta 0.05) is reported too: the smallest t whose certified set rejects
    "precision < 99 %"; it needs >= 299 certified calibration courses with no error, so on today's dev it is empty.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = os.environ.get("ZT_GATE_PARAMS", os.path.join(HERE, "gate_params.json"))
PROD = ("struct", "struct_card", "struct_webcard", "pairs", "pairs_card", "pairs_webcard", "evidence", "evidence_webcard")
TARGET = 0.99

FEATS = ("lp_route", "lp_route_mix", "min_num", "mean_lnum", "min_tee", "mean_ltee", "lp_front", "card",
         "card_max_resid", "card_mean_resid", "unused", "lagr", "n9", "ch_p", "min_gap", "max_walk", "cx_ratio",
         "sum_l1m_other", "dp_front", "min_par", "sum_lpar")


def features(dg):
    N = max(1, dg.get("N", 18))
    num = np.clip(np.array(dg.get("marg_num") or [0.0]), 1e-6, 1)
    pt = np.clip(np.array(dg.get("p_tee") or [0.0]), 1e-6, 1)
    oth = np.clip(np.array(dg.get("marg_max_other") or [0.0]), 0, 1 - 1e-6)
    pf = dg.get("p_front")
    pfd = dg.get("p_front_dp")
    cr = dg.get("card_resid") or []
    walks = [w for w in (dg.get("walk_in") or []) if w is not None]
    gaps = dg.get("form_top_gap") or [0.0]
    pw = dg.get("pw") or [1.0]
    f = dict(lp_route=max(-30.0, math.log(max(dg.get("p_route", 0.0), 1e-13))),
             lp_route_mix=max(-30.0, math.log(max(dg.get("p_route_mix", 0.0), 1e-13))),
             min_num=float(num.min()), mean_lnum=float(np.log(num).mean()), min_tee=float(pt.min()),
             mean_ltee=float(np.log(pt).mean()),
             lp_front=0.0 if pf is None else math.log(max(pf, 1e-6)), card=float(bool(dg.get("card"))),
             card_max_resid=float(max(cr)) if cr else 0.0, card_mean_resid=float(np.mean(cr)) if cr else 0.0,
             unused=dg.get("unused_greens", 0) / N, lagr=float(dg.get("lagr_conflict", 0) > 0), n9=float(N == 9),
             ch_p=float(max(pw)), min_gap=float(min(10.0, min(gaps))), max_walk=math.log1p(max(walks) / 100) if walks else 0.0,
             cx_ratio=dg.get("n_cx", N) / N, sum_l1m_other=float(np.log1p(-oth).sum()),
             dp_front=0.0 if pfd is None else abs(pfd - 0.5) * 2,
             min_par=float(min(dg.get("par_conf") or [1.0])),
             sum_lpar=float(np.log(np.clip(dg.get("par_conf") or [1.0], 1e-6, 1)).sum()))
    return np.array([f[k] for k in FEATS])


def dataset(rows, modes=PROD):
    rs = [r for r in rows if "error" not in r and r.get("mode") in modes and r.get("diag")]
    X = np.array([features(r["diag"]) for r in rs]).reshape(-1, len(FEATS))
    y = np.array([int(r["all_correct"]) for r in rs])
    return rs, X, y


def fit_lr(X, y, l2=1.0):
    from scipy.optimize import minimize
    mu, sd = X.mean(0), X.std(0) + 1e-6
    Z = (X - mu) / sd
    Z1 = np.c_[Z, np.ones(len(Z))]

    def f(w):
        z = Z1 @ w
        p = 1 / (1 + np.exp(-z))
        g = Z1.T @ (p - y)
        reg = l2 * (w[:-1] ** 2).sum()
        return np.logaddexp(0, z).sum() - (y * z).sum() + reg, g + 2 * l2 * np.r_[w[:-1], 0]
    w = minimize(f, np.zeros(Z1.shape[1]), jac=True, method="L-BFGS-B").x
    return dict(mu=mu.tolist(), sd=sd.tolist(), w=w.tolist())


def score(m, X):
    Z = (np.asarray(X) - np.array(m["mu"])) / np.array(m["sd"])
    return np.c_[Z, np.ones(len(Z))] @ np.array(m["w"])


def isotonic(s, y):
    """Pool-adjacent-violators: -> (breakpoints, values) for a non-decreasing step map score -> P(correct)."""
    o = np.argsort(s)
    s, y = np.asarray(s)[o], np.asarray(y, float)[o]
    blocks = [[y[i], 1.0, s[i], s[i]] for i in range(len(s))]
    out = []
    for b in blocks:
        out.append(b)
        while len(out) > 1 and out[-2][0] / out[-2][1] > out[-1][0] / out[-1][1]:
            a, c = out.pop(), out.pop()
            out.append([a[0] + c[0], a[1] + c[1], c[2], a[3]])
    xs = [b[2] for b in out]
    vs = [b[0] / b[1] for b in out]
    return xs, vs


def iso_apply(xs, vs, s):
    i = np.searchsorted(np.asarray(xs), np.asarray(s), side="right") - 1
    return np.asarray(vs)[np.clip(i, 0, len(vs) - 1)] * (np.asarray(s) >= xs[0]) + 0.0


def binom_upper_ok(n, k, target=TARGET, delta=0.05):
    """True when k errors out of n certified reject 'precision < target' at level delta (binomial tail)."""
    from scipy.stats import binom
    return n > 0 and binom.cdf(k, n, 1 - target) <= delta


def crossfit(rows, X, y, folds=5, seed=0):
    slugs = sorted({r["slug"] for r in rows})
    rng = np.random.RandomState(seed)
    fid = dict(zip(slugs, rng.permutation(len(slugs)) % folds))
    f = np.array([fid[r["slug"]] for r in rows])
    s = np.zeros(len(y))
    for k in range(folds):
        tr = f != k
        if y[tr].sum() == 0:
            s[~tr] = -10
            continue
        m = fit_lr(X[tr], y[tr])
        s[~tr] = score(m, X[~tr])
    return s


def fit(rows_paths, out=PARAMS, modes=PROD, splits=("dev",)):
    rows = [r for p in rows_paths for r in _read(p) if r.get("split") in splits]
    rs, X, y = dataset(rows, modes)
    s_cv = crossfit(rs, X, y)
    xs, vs = isotonic(s_cv, y)
    conf_cv = iso_apply(xs, vs, s_cv)
    wrong = conf_cv[y == 0]
    # zero-error rule on the cross-fitted calibration scores: just above the best-scoring wrong course
    t0 = float(wrong.max()) + 1e-9 if len(wrong) else 0.0
    t_score = float(s_cv[y == 0].max()) + 1e-9 if (y == 0).any() else -1e9
    if y.sum() == 0:
        t_score = 1e9
    ltt = None
    for t in sorted(set(conf_cv.tolist())):
        sel = conf_cv >= t
        if binom_upper_ok(int(sel.sum()), int((sel & (y == 0)).sum())):
            ltt = float(t)
            break
    m = fit_lr(X, y)
    sel = s_cv >= t_score
    p = dict(schema="zero_tap_gate/1", feats=list(FEATS), model=m, iso=dict(x=xs, v=vs), threshold_score=t_score,
             threshold_conf=t0, ltt_threshold=ltt, target_precision=TARGET, modes=list(modes),
             calib=dict(rows=len(y), courses=len({r["slug"] for r in rs}), positives=int(y.sum()),
                        certified=int(sel.sum()), certified_wrong=int((sel & (y == 0)).sum())),
             note="fitted on dev rows only (bench.py); score threshold = zero cross-fitted dev errors")
    json.dump(p, open(out, "w"), indent=1)
    print(json.dumps(p["calib"]), "threshold score", round(t_score, 3), "ltt", ltt)
    return p


def _read(p):
    import gzip
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as fh:
        return json.load(fh)


def load(path=PARAMS):
    return json.load(open(path)) if os.path.exists(path) else None


def apply(p, dg):
    """-> (certain, confidence, score) for one solved course."""
    if not p:
        return False, None, None
    x = features(dg)[None]
    s = float(score(p["model"], x)[0])
    c = float(iso_apply(p["iso"]["x"], p["iso"]["v"], [s])[0])
    return bool(s >= p["threshold_score"]), c, s


def curve(s, y, n_pts=None):
    """Coverage vs precision as the score threshold sweeps from high to low."""
    o = np.argsort(-s)
    ys = np.asarray(y)[o]
    tp = np.cumsum(ys)
    k = np.arange(1, len(ys) + 1)
    out = []
    for i in range(len(ys)):
        if i + 1 < len(ys) and s[o][i + 1] == s[o][i]:
            continue
        out.append(dict(threshold=float(s[o][i]), certified=int(k[i]), coverage=float(k[i] / len(ys)),
                        precision=float(tp[i] / k[i])))
    return out


def evaluate(p, rows_paths, splits, out_dir):
    rows = [r for pth in rows_paths for r in _read(pth)]
    res = dict(schema="zero_tap_gate_eval/1", threshold_score=p["threshold_score"], by={})
    md = ["| split | mode | courses | fully correct | certified | coverage | precision (certified fully right) | "
          "coverage at 100 % precision | max coverage with precision >= 99 % |", "|" + "---|" * 9]
    for sp in splits:
        by = defaultdict(list)
        for r in rows:
            if r.get("split") == sp and "error" not in r and r.get("diag"):
                by[r["mode"]].append(r)
        pooled = []
        for mode in sorted(by):
            rs = by[mode]
            X = np.array([features(r["diag"]) for r in rs])
            y = np.array([int(r["all_correct"]) for r in rs])
            s = score(p["model"], X)
            if mode in PROD:
                pooled += list(zip(s, y, [mode] * len(y)))
            res["by"][f"{sp}/{mode}"] = _summ(s, y, p, rs)
            md.append(_md_row(sp, mode, res["by"][f"{sp}/{mode}"]))
        if pooled:
            s = np.array([a for a, _, _ in pooled])
            y = np.array([b for _, b, _ in pooled])
            res["by"][f"{sp}/production (pooled)"] = _summ(s, y, p, None)
            md.append(_md_row(sp, "production (pooled)", res["by"][f"{sp}/production (pooled)"]))
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "gate_eval.json"), "w"), indent=1, default=float)
    open(os.path.join(out_dir, "gate_eval.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))
    return res


def _summ(s, y, p, rs):
    cert = s >= p["threshold_score"]
    cv = curve(s, y)
    full = [c for c in cv if c["precision"] >= 1.0]
    p99 = [c for c in cv if c["precision"] >= TARGET]
    out = dict(n=int(len(y)), fully_correct=float(y.mean()) if len(y) else 0.0, certified=int(cert.sum()),
               coverage=float(cert.mean()) if len(y) else 0.0,
               precision=float(y[cert].mean()) if cert.any() else None,
               cov_at_100=max((c["coverage"] for c in full), default=0.0),
               cov_at_99=max((c["coverage"] for c in p99), default=0.0), curve=cv)
    if rs is not None:
        out["certified_courses"] = [dict(slug=r["slug"], ok=int(r["all_correct"])) for r, c in zip(rs, cert) if c]
    return out


def _md_row(sp, mode, d):
    prec = "-" if d["precision"] is None else f"{d['precision']:.1%}"
    return (f"| {sp} | {mode} | {d['n']} | {d['fully_correct']:.1%} | {d['certified']} | {d['coverage']:.1%} | {prec} | "
            f"{d['cov_at_100']:.1%} | {d['cov_at_99']:.1%} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["fit", "eval"])
    ap.add_argument("rows", nargs="+")
    ap.add_argument("--split", default="heldout,valtest,dev")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    a = ap.parse_args()
    if a.what == "fit":
        fit(a.rows)
    else:
        evaluate(load(), a.rows, a.split.split(","), a.out)


if __name__ == "__main__":
    main()
