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


class Models:
    def __init__(self, feats=("hole", "trans")):
        self.m = {}

    def fit(self, ds):
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
        out["start"] = self.m["start"].predict_proba(self._club(d["cT"]))[:, 1]
        out["end"] = self.m["end"].predict_proba(self._club(d["cG"]))[:, 1]
        return out
