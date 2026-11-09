"""joint routing: local evidence models (gradient-boosted trees), fitted on dev courses only.

  hole   P(tee complex t -> green g is one hole)          features feats.HF
  walk   P(green g -> tee complex t is the walk to the next hole)   features feats.WF
  start  P(tee complex starts a loop: hole 1, or 10 on an 18)       clubhouse / car-park distance and ranks
  end    P(green ends a loop: hole 9 / 18)

`fit_predict(dev, test)`: dev scores are out-of-fold (5 folds grouped by state), test scores come from the all-dev
fit. Each course dict gets `sc` = dict(ph [n hole pairs], pw [n walk pairs], ps [nt], pe [ng]).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

LF = ["club", "club_rk", "park", "park_rk", "p", "cen", "cen_rk", "n"]
PARAMS = dict(n_estimators=250, learning_rate=0.05, num_leaves=15, min_child_samples=25, subsample=0.8,
              subsample_freq=1, colsample_bytree=0.8, reg_lambda=2.0, verbose=-1, n_jobs=2)


def loop_features(co, geo, which):
    """Per tee complex ('start') or green ('end'): distance to the clubhouse / nearest car park and its rank."""
    P = geo["Tc"] if which == "start" else co["G"]
    p = np.array([t["p"] for t in co["T"]]) if which == "start" else co["Gp"]
    n = len(P)
    club = co.get("club")
    dc = np.hypot(P[:, 0] - club[0], P[:, 1] - club[1]) if club is not None else np.full(n, np.nan)
    pk = co["park"]
    dp = np.min(np.hypot(P[:, None, 0] - pk[None, :, 0], P[:, None, 1] - pk[None, :, 1]), axis=1) if len(pk) \
        else np.full(n, np.nan)
    cen = co["G"].mean(0)
    dz = np.hypot(P[:, 0] - cen[0], P[:, 1] - cen[1])

    def rk(v):
        return np.argsort(np.argsort(np.where(np.isnan(v), 1e9, v))).astype(float)
    return np.c_[dc, rk(dc), dp, rk(dp), p, dz, rk(dz), np.full(n, n)]


def labels(d):
    """Truth labels of one cached course: hole pairs, walk pairs, loop starts (tee), loop ends (green)."""
    lab, kind = d["lab"], d["kind"]
    g2h, t2h, refs = lab["g2h"], lab["t2h"], lab["refs"]
    byref = {v: j for j, v in enumerate(refs)}
    yh = np.array([int(g2h[g] >= 0 and g2h[g] in t2h[t]) for t, g in d["hp"]], int)
    nxt = {j: byref.get((r + 1, c)) for j, (r, c) in enumerate(refs)}
    yw = np.array([int(g2h[g] >= 0 and nxt.get(g2h[g]) is not None and nxt[g2h[g]] in t2h[t]) for g, t in d["wp"]], int)
    loop = 9 if kind != 18 else 9
    starts = {j for j, (r, c) in enumerate(refs) if (r - 1) % loop == 0}
    ends = {j for j, (r, c) in enumerate(refs) if r % loop == 0}
    ys = np.array([int(bool(s & starts)) for s in t2h], int)
    ye = np.array([int(j in ends) for j in g2h], int)
    return yh, yw, ys, ye


def _fit(X, y):
    m = lgb.LGBMClassifier(**PARAMS)
    m.fit(X, y)
    return m


def _tables(ds):
    H, W, S, E = [], [], [], []
    for d in ds:
        yh, yw, ys, ye = labels(d)
        H.append((d["hx"], yh))
        W.append((d["wx"], yw))
        S.append((loop_features(d["co"], d["geo"], "start"), ys))
        E.append((loop_features(d["co"], d["geo"], "end"), ye))
    return [(np.vstack([a for a, _ in t]), np.concatenate([b for _, b in t])) for t in (H, W, S, E)]


def fit(ds):
    return [_fit(X, y) for X, y in _tables(ds)]


def predict(ms, d):
    mh, mw, ms_, me = ms
    co, geo = d["co"], d["geo"]
    return dict(ph=mh.predict_proba(d["hx"])[:, 1] if len(d["hx"]) else np.zeros(0),
                pw=mw.predict_proba(d["wx"])[:, 1] if len(d["wx"]) else np.zeros(0),
                ps=ms_.predict_proba(loop_features(co, geo, "start"))[:, 1],
                pe=me.predict_proba(loop_features(co, geo, "end"))[:, 1])


def folds(ds, k=5):
    """Course folds grouped by state (deterministic)."""
    states = sorted({d["row"]["state"] for d in ds})
    return {s: i % k for i, s in enumerate(states)}


def fit_predict(dev, test=(), k=5):
    f = folds(dev, k)
    for i in range(k):
        tr = [d for d in dev if f[d["row"]["state"]] != i]
        te = [d for d in dev if f[d["row"]["state"]] == i]
        if not te:
            continue
        ms = fit(tr)
        for d in te:
            d["sc"] = predict(ms, d)
            d["fold"] = i
    ms = fit(dev)
    for d in test:
        d["sc"] = predict(ms, d)
    return ms
