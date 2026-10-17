"""Fit the clubhouse ranker and the front / back nine model on dev courses only -> anchors_params.json.

    python course_data/zero_tap/sequence/fit_anchors.py club          # ranker (no DP; seconds)
    python course_data/zero_tap/sequence/fit_anchors.py nine -j 4     # nine model (one oracle DP per 18-hole course)

Both report 5-fold cross-validated accuracy on dev, grouped by course, against the structure solver's defaults.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anchors as A                                                  # noqa: E402
import bench as B                                                    # noqa: E402
import joint as J                                                    # noqa: E402

V = A.V


def dev_courses():
    return [e for e in B.all_courses() if e["split"] == "dev"]


def save(key, val, note):
    js = json.load(open(A.PARAMS)) if os.path.exists(A.PARAMS) else {}
    js[key] = val
    js.setdefault("notes", {})[key] = note
    json.dump(js, open(A.PARAMS, "w"), indent=1)


# ----------------------------------------------------------------------------- clubhouse ranker
def club_data():
    data = []
    for e in dev_courses():
        d = B.load_course(e)
        if d.get("skip"):
            continue
        sc, geo, hyps = d["sc"], d["geo"], d["hyps"]
        cands = A._raw(sc, geo, hyps)
        if not cands:
            continue
        X = A.club_features(sc, geo, hyps, cands, d["roads"], d["addr_street"])
        ta = B.truth_anchors(d)
        t1, gN = np.array(ta["t1"]), np.array(ta["gN"])
        P = np.array([c["c"] for c in cands])
        L = np.hypot(*(P - t1).T) + np.hypot(*(P - gN).T)
        err = np.minimum(np.hypot(*(P - t1).T), np.hypot(*(P - gN).T))
        q = np.exp(-(L - L.min()) / 40.0)
        q /= q.sum()
        base = list(sc.clubhouse) + V.hub_candidates(sc, geo, hyps)
        b0 = base[0]["c"] if base else P[0]
        berr = float(min(np.hypot(*(b0 - t1)), np.hypot(*(b0 - gN))))
        data.append(dict(slug=e["slug"], X=X, q=q, err=err, base_err=berr, best_err=float(err.min())))
    return data


def fit_softmax(data, l2=0.3):
    from scipy.optimize import minimize
    nf = data[0]["X"].shape[1]

    def f(w):
        tot, g = 0.0, np.zeros(nf)
        for d in data:
            s = d["X"] @ w
            m = s.max()
            p = np.exp(s - m)
            Z = p.sum()
            p /= Z
            tot -= (d["q"] * (s - m - math.log(Z))).sum()
            g -= d["X"].T @ (d["q"] - p)
        return tot + l2 * (w ** 2).sum(), g + 2 * l2 * w
    r = minimize(f, np.zeros(nf), jac=True, method="L-BFGS-B")
    return r.x


def club(args):
    data = club_data()
    rng = np.random.RandomState(0)
    folds = rng.permutation(len(data)) % 5
    cv_err = []
    for k in range(5):
        w = fit_softmax([d for d, f in zip(data, folds) if f != k])
        for d, f in zip(data, folds):
            if f == k:
                cv_err.append(float(d["err"][int(np.argmax(d["X"] @ w))]))
    cv_err = np.array(cv_err)
    base = np.array([d["base_err"] for d in data])
    best = np.array([d["best_err"] for d in data])
    for thr in (60, 100, 150):
        print(f"clubhouse top-1 within {thr} yds of tee 1 / last green: structure {np.mean(base <= thr):.3f}  "
              f"ranker (5-fold CV) {np.mean(cv_err <= thr):.3f}  oracle candidate {np.mean(best <= thr):.3f}")
    w = fit_softmax(data)
    print(dict(zip(A.CLUB_FEATS, np.round(w, 3))))
    save("club_w", {k: round(float(v), 4) for k, v in zip(A.CLUB_FEATS, w)},
         f"softmax ranker on {len(data)} dev courses; CV top-1 <=100 yds {np.mean(cv_err <= 100):.3f} "
         f"(structure default {np.mean(base <= 100):.3f})")


# ----------------------------------------------------------------------------- nine model
def _nine_one(e):
    d = B.load_course(e)
    if d.get("skip") or d["N"] != 18:
        return None
    sc, truth, geo = d["sc"], d["truth"], d["geo"]
    o = J.oracle_hyps(sc, truth, geo, d["allh"], B.E.tee_ok, B.E.true_green)
    if o is None:
        return None
    hyps, keep = o
    cands = A.clubhouse_candidates(sc, geo, d["hyps"], roads=d["roads"], street=d["addr_street"])
    res = J.solve(sc, geo=geo, hyps=hyps, keep=keep, n_holes=18, cands=cands, nine=None, hyps_all=d["hyps"])
    dbg = res["_debug"]
    pb = dbg["pb"]
    tg = [B.E.true_green(geo.G, geo.gr_r, t["green"]) for t in truth]
    seq = [pb.keep.index(g) for g in tg]
    br = dbg["br"]
    dp = V.route_score(br["mats"], seq) - V.route_score(br["mats"], seq[9:] + seq[:9])
    lw = np.array([r["logw"] for r in dbg["runs"]])
    pw = np.exp(lw - V._lse(lw))
    x = A.nine_features(sc, geo, pb, br, seq, dbg["Hc"], pw, dbg["runs"], dp, d["roads"], d["addr_street"])
    xs = V.route_swap_x(sc, geo, pb, br, seq)
    xs["dp"] = dp
    zs = sum((V.SWAP_W or {}).get(k, 0.0) * xs.get(k, 0.0) for k in V.SWAP_FEATS)
    return dict(slug=e["slug"], x=[x[k] for k in A.NINE_FEATS], base_ok=bool(zs > 0))


def fit_anti(X, l2=0.5):
    from scipy.optimize import minimize

    def nll(w):
        z = X @ w
        return np.logaddexp(0, -z).sum() + l2 * (w ** 2).sum()
    return minimize(nll, np.zeros(X.shape[1])).x


def nine(args):
    ents = dev_courses()
    if args.j > 1:
        from multiprocessing import Pool
        with Pool(args.j) as pool:
            rows = [r for r in pool.map(_nine_one, ents) if r]
    else:
        rows = [r for r in map(_nine_one, ents) if r]
    json.dump(rows, open(os.path.join(args.cache, "nine_rows.json"), "w"))
    X = np.array([r["x"] for r in rows])
    rng = np.random.RandomState(0)
    folds = rng.permutation(len(X)) % 5
    ok = np.zeros(len(X), bool)
    for k in range(5):
        w = fit_anti(X[folds != k])
        ok[folds == k] = X[folds == k] @ w > 0
    base = np.mean([r["base_ok"] for r in rows])
    print(f"nine model: {len(X)} dev 18-hole routes (oracle formation); structure classifier {base:.3f}; "
          f"v2 5-fold CV {ok.mean():.3f}")
    for j, k in enumerate(A.NINE_FEATS):
        nz = X[:, j] != 0
        print(f"  {k:12s} alone {np.mean(X[nz, j] > 0) if nz.any() else float('nan'):.3f}  nonzero {int(nz.sum())}")
    w = fit_anti(X)
    print(dict(zip(A.NINE_FEATS, np.round(w, 3))))
    save("nine_w", {k: round(float(v), 4) for k, v in zip(A.NINE_FEATS, w)},
         f"antisymmetric logistic on {len(X)} dev routes (oracle formation, v2 clubhouse); CV {ok.mean():.3f} "
         f"(structure classifier {base:.3f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["club", "nine"])
    ap.add_argument("-j", type=int, default=1)
    ap.add_argument("--cache", default=B.CACHE)
    a = ap.parse_args()
    {"club": club, "nine": nine}[a.what](a)


if __name__ == "__main__":
    main()
