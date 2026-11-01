"""Per-hole pair confidence: P(the decoded tee complex <-> green pairing is right), calibrated by a logistic model
fitted out-of-fold on dev courses, and the "taps" a golfer needs to confirm the low-confidence holes.

Features of a decoded hole (t, g): its hole probability, margins against the best other tee for g / other green for
t (hole-cost space), the walk probabilities into / out of the hole, the route confidence, and the min-marginal:
how much the best route's cost rises when this exact pair is forbidden (re-decode with a smaller beam).
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

CONF_F = ["p_hole", "m_tee", "m_green", "p_in", "p_out", "route", "minmarg", "minmarg_c", "L", "n_greens_x"]


def hole_conf_feats(d, H, T, holes, route_conf, minmarg):
    tc, gc = np.asarray(d["tc"]), np.asarray(d["gc"])
    X = []
    for i, h in enumerate(holes):
        t, g = h["t"], h["g"]
        own = [t] + list(h["boxes"])
        col = H[:, g].copy()
        col[own] = np.inf
        row = H[t].copy()
        row[g] = np.inf
        pin = T[holes[i - 1]["g"], t] if i > 0 and holes[i - 1]["loop"] == h["loop"] else np.nan
        pout = T[g, holes[i + 1]["t"]] if i + 1 < len(holes) and holes[i + 1]["loop"] == h["loop"] else np.nan
        mm = minmarg[i]
        X.append([np.exp(-H[t, g]), min(col.min() - H[t, g], 14), min(row.min() - H[t, g], 14),
                  np.exp(-pin) if np.isfinite(pin) else 0.5, np.exp(-pout) if np.isfinite(pout) else 0.5,
                  route_conf, min(mm, 30.0), float(np.clip(mm, 0, 30) > 3), h["L"], 0.0])
    return np.array(X, float).reshape(-1, len(CONF_F))


class Calib:
    def fit(self, X, y):
        self.m = LogisticRegression(C=1.0, max_iter=2000).fit(self._t(X), y)
        return self

    @staticmethod
    def _t(X):
        X = np.asarray(X, float)
        return np.c_[X[:, :6], np.log1p(np.maximum(X[:, 6:7], 0)), X[:, 7:8], X[:, 8:9] / 300.0]

    def predict(self, X):
        return self.m.predict_proba(self._t(X))[:, 1]


def taps_to_precision(courses, target=0.98):
    """courses: [(conf array, correct array)]. The app asks the golfer to confirm every hole whose confidence is
    below a global threshold; a confirmed hole is right (the golfer fixes it). -> smallest threshold whose
    resulting pair precision over all holes is >= target: (threshold, mean taps / course, precision,
    share of courses needing no tap)."""
    allc = np.concatenate([c for c, _ in courses])
    best = None
    for thr in np.r_[0.0, np.unique(allc)]:
        right = taps = n = 0
        zero = 0
        for c, y in courses:
            ask = c < thr
            right += int(np.sum(y[~ask])) + int(ask.sum())
            taps += int(ask.sum())
            n += len(c)
            zero += int(ask.sum() == 0)
        prec = right / max(n, 1)
        if prec >= target:
            best = (float(thr), taps / len(courses), prec, zero / len(courses))
            break
    return best
