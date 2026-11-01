"""pathroute local models: P(tee -> green is one hole), P(green -> tee is the walk to the next hole),
P(tee starts a nine), P(green ends a nine). Gradient-boosted trees on dev-course labels only."""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")    # shared 4-core box: OpenMP oversubscription is 50x slower

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression


def hole_xy(d):
    lab = d["lab"]
    y = np.array([int(lab["green_h"][g] is not None and lab["green_h"][g] in lab["tee_h"][t]) for t, g in d["hp"]])
    return d["hX"], y


def trans_xy(d):
    lab = d["lab"]
    y = []
    for g, t in d["tp"]:
        j = lab["green_h"][g]
        k = lab["nxt"].get(j) if j is not None else None
        y.append(int(k is not None and k in lab["tee_h"][t]))
    return d["tX"], np.array(y)


def _loop_len(d):
    return 9 if d["kind"] in (9, 27) else 18


def start_xy(d):
    lab = d["lab"]
    n = _loop_len(d)
    starts = {j for j, r in enumerate(lab["refs"]) if r == 1 or (n == 18 and r == 10)}
    return d["cT"], np.array([int(bool(s & starts)) for s in lab["tee_h"]])


def end_xy(d):
    lab = d["lab"]
    n = _loop_len(d)
    ends = {j for j, r in enumerate(lab["refs"]) if r == n or (n == 18 and r == 9)}
    return d["cG"], np.array([int(g in ends) for g in lab["green_h"]])


XY = dict(hole=hole_xy, trans=trans_xy, start=start_xy, end=end_xy)


def _gbm():
    return HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31,
                                          min_samples_leaf=30, l2_regularization=1.0, random_state=0)


def stage2(d, ph, pt):
    """Second-stage features: each candidate's first-stage score relative to its competitors (same tee / same
    green), and cross-evidence between the two models (a tee that starts a strong hole; a 'next tee' that is in
    fact the green's own tee; the walk direction vs the green's approach direction)."""
    nt, ng = len(d["tees"]), len(d["greens"])
    Ph = np.zeros((nt, ng))
    for (t, g), p in zip(d["hp"], ph):
        Ph[t, g] = p
    Pt = np.zeros((ng, nt))
    for (g, t), p in zip(d["tp"], pt):
        Pt[g, t] = p
    tc, gc = np.asarray(d["tc"]), np.asarray(d["gc"])
    rowh, colh = Ph.max(1), Ph.max(0)
    rowt, colt = Pt.max(1), Pt.max(0)
    best_tee = Ph.argmax(0)
    app = gc - tc[best_tee]
    app /= np.maximum(np.hypot(*app.T), 1.0)[:, None]
    tee_pred = Pt.max(0)                      # some green walks to this tee
    Xh = []
    for (t, g), p in zip(d["hp"], ph):
        Ph_row = Ph[t].copy(); Ph_row[g] = 0
        Ph_col = Ph[:, g].copy(); Ph_col[t] = 0
        Xh.append([p, p / max(rowh[t], 1e-6), p / max(colh[g], 1e-6), Ph_row.max(), Ph_col.max(),
                   tee_pred[t], Pt[g].max()])
    Xt = []
    for (g, t), p in zip(d["tp"], pt):
        r = Pt[g].copy(); r[t] = 0
        c = Pt[:, t].copy(); c[g] = 0
        v = tc[t] - gc[g]
        cosang = float(v @ app[g] / max(np.hypot(*v), 1.0))
        Xt.append([p, p / max(rowt[g], 1e-6), p / max(colt[t], 1e-6), r.max(), c.max(), Ph[t, g], Ph[t].max(),
                   cosang])
    return (np.c_[d["hX"], np.array(Xh).reshape(-1, 7)], np.c_[d["tX"], np.array(Xt).reshape(-1, 8)])


class Models:
    def __init__(self, stack=True):
        self.m = {}
        self.stack = stack

    def fit(self, ds):
        self._fit1(ds)
        if not self.stack:
            return self
        # out-of-fold first-stage scores on the training courses -> fit the second stage
        k = 3
        sub = [Models(stack=False)._fit1([d for i, d in enumerate(ds) if i % k != f]) for f in range(k)]
        H2, T2, yh, yt = [], [], [], []
        for i, d in enumerate(ds):
            p = sub[i % k].predict(d)
            a, b = stage2(d, p["hole"], p["trans"])
            H2.append(a); T2.append(b)
            yh.append(hole_xy(d)[1]); yt.append(trans_xy(d)[1])
        self.m["hole2"] = _gbm().fit(np.vstack(H2), np.concatenate(yh))
        self.m["trans2"] = _gbm().fit(np.vstack(T2), np.concatenate(yt))
        return self

    def _fit1(self, ds):
        for k, f in XY.items():
            X, y = zip(*[f(d) for d in ds])
            X, y = np.vstack(X), np.concatenate(y)
            if k in ("hole", "trans"):
                m = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31,
                                                   min_samples_leaf=30, l2_regularization=1.0, random_state=0)
            else:
                X = self._club(X)
                m = LogisticRegression(C=1.0, max_iter=500)
            m.fit(X, y)
            self.m[k] = m
        return self

    @staticmethod
    def _club(X):
        d = X[:, 0:1]
        return np.c_[d / 100.0, np.log1p(d), np.minimum(X[:, 1:2], 10) / 10.0]

    def predict(self, d):
        out = {}
        for k, key in (("hole", "hX"), ("trans", "tX")):
            X = d[key]
            out[k] = self.m[k].predict_proba(X)[:, 1] if len(X) else np.zeros(0)
        if self.stack and "hole2" in self.m and len(d["hX"]) and len(d["tX"]):
            a, b = stage2(d, out["hole"], out["trans"])
            out["hole"] = self.m["hole2"].predict_proba(a)[:, 1]
            out["trans"] = self.m["trans2"].predict_proba(b)[:, 1]
        out["start"] = self.m["start"].predict_proba(self._club(d["cT"]))[:, 1]
        out["end"] = self.m["end"].predict_proba(self._club(d["cG"]))[:, 1]
        return out
