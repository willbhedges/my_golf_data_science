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
# fix-aware extras (Calib2, fitted on constrained re-solves: calib_resolve.py): share of decoded holes the golfer has
# confirmed, confirmed route neighbours (0-2), hole not in the free (no-fact) decode, tee / green margins in the
# fixed hole-cost matrix (decode2.apply_fix: confirmed tees / greens no longer compete)
FIX_F = ["frac_fixed", "nb_fixed", "changed", "m_tee_c", "m_green_c"]
CONF_F2 = CONF_F + FIX_F


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


def fix_feats(H, Hf, holes, fix, free_pairs=None):
    """[n, len(FIX_F)] fix-aware features of decoded holes (H: free hole costs, Hf: apply_fix(H) or H)."""
    fixed = {(int(t), int(g)) for _, t, g in (fix or {}).get("pairs") or ()}
    n = max(len(holes), 1)
    nf = sum((h["t"], h["g"]) in fixed for h in holes)
    X = []
    for i, h in enumerate(holes):
        t, g = h["t"], h["g"]
        nb = 0
        for j in (i - 1, i + 1):
            if 0 <= j < len(holes) and holes[j]["loop"] == h["loop"] and (holes[j]["t"], holes[j]["g"]) in fixed:
                nb += 1
        ch = 0.0 if free_pairs is None else float((t, g) not in free_pairs)
        own = [t] + list(h["boxes"])
        col = Hf[:, g].copy()
        col[own] = np.inf
        row = Hf[t].copy()
        row[g] = np.inf
        base = Hf[t, g] if np.isfinite(Hf[t, g]) else H[t, g]
        X.append([nf / n, nb, ch, min(col.min() - base, 14), min(row.min() - base, 14)])
    return np.array(X, float).reshape(-1, len(FIX_F))


class Calib2:
    """Logistic calibration on constrained re-solves (calib_resolve.py). Plain coefficients so the browser can run
    it: p = sigmoid(coef . transform(x) + intercept), transform documented in `transform` (same in lib JS)."""
    def fit(self, X, y, C=1.0):
        Z = self.transform(X)
        self.mu, self.sd = Z.mean(0), Z.std(0) + 1e-9
        self.m = LogisticRegression(C=C, max_iter=4000).fit((Z - self.mu) / self.sd, y)
        self.coef = (self.m.coef_[0] / self.sd)
        self.intercept = float(self.m.intercept_[0] - np.sum(self.m.coef_[0] * self.mu / self.sd))
        return self

    @staticmethod
    def transform(X):
        X = np.asarray(X, float)
        mm = np.log1p(np.maximum(X[:, 6:7], 0))
        ff = X[:, 10:11]
        return np.c_[X[:, :6], mm, X[:, 7:8], X[:, 8:9] / 300.0, ff, X[:, 11:12], X[:, 12:13],
                     np.minimum(X[:, 13:15], 14), mm * ff, X[:, 5:6] * ff]

    def predict(self, X):
        z = self.transform(X) @ self.coef + self.intercept
        return 1.0 / (1.0 + np.exp(-z))

    def export(self):
        return dict(schema="pathroute_calib/2", features=CONF_F2, coef=[float(c) for c in self.coef],
                    intercept=self.intercept,
                    transform="[x0..x5, log1p(max(minmarg,0)), minmarg_c, L/300, frac_fixed, nb_fixed, changed, "
                              "min(m_tee_c,14), min(m_green_c,14), log1p(minmarg)*frac_fixed, route*frac_fixed]")


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
