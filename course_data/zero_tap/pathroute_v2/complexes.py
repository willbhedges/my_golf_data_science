"""Tee complexes: group the tee boxes of one hole (P(same hole) from a boosted model on tee-pair geometry), then
average-linkage agglomeration. comp[t] = complex id."""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier


class TeePairModel:
    def fit(self, ds):
        X = np.vstack([d["tpX"] for d in ds if len(d["tpX"])])
        y = np.concatenate([d["tpy"] for d in ds if len(d["tpX"])])
        self.m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=31,
                                                min_samples_leaf=30, l2_regularization=1.0, random_state=0).fit(X, y)
        return self

    def predict(self, d):
        return self.m.predict_proba(d["tpX"])[:, 1] if len(d["tpX"]) else np.zeros(0)


def cluster(nt, pairs, p, thr=0.5):
    """Average-linkage agglomeration over the sparse pair probabilities (missing pairs = 0)."""
    P = np.zeros((nt, nt))
    for (a, b), q in zip(pairs, p):
        P[a, b] = P[b, a] = q
    members = {i: [i] for i in range(nt)}
    while True:
        best, bk = thr, None
        keys = list(members)
        # candidate merges only along observed pairs
        cand = set()
        lab = {i: c for c, ms in members.items() for i in ms}
        for (a, b), q in zip(pairs, p):
            if q > thr and lab[a] != lab[b]:
                cand.add((min(lab[a], lab[b]), max(lab[a], lab[b])))
        for ca, cb in cand:
            s = P[np.ix_(members[ca], members[cb])].mean()
            if s > best:
                best, bk = s, (ca, cb)
        if bk is None:
            break
        ca, cb = bk
        members[ca] += members.pop(cb)
        del keys
    comp = np.zeros(nt, int)
    for c, ms in members.items():
        comp[ms] = c
    return comp
