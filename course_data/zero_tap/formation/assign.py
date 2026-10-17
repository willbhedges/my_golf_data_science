"""Global green <-> tee-candidate assignment: each tee complex starts at most one hole, each green ends at most one.

Pair log-odds S (greens x candidates, -inf where no pair) plus a per-green slack (a practice green, or a hole whose tee
is not among the candidates) -> calibrated pair marginals by capacity-constrained Sinkhorn balancing (rows sum to
1 over candidates + slack; a column whose mass exceeds 1 is scaled down to 1), and the MAP assignment by the
Hungarian algorithm on the same scores. A candidate that is a forward tee of a hole (on its corridor) is not
"used" by that hole: forward complexes simply stay unassigned.
"""
from __future__ import annotations

import numpy as np


def sinkhorn(S, slack, temp=1.0, iters=60):
    """S (nG, nC) log-scores (-inf = impossible); slack (nG,) log-score of 'no candidate'. -> (P (nG, nC), p_slack)."""
    nG, nC = S.shape
    if nG == 0:
        return np.zeros((0, nC)), np.zeros(0)
    Z = np.concatenate([S, slack[:, None]], 1) / temp
    Z = Z - np.nanmax(np.where(np.isfinite(Z), Z, -1e30), 1, keepdims=True)
    K = np.where(np.isfinite(Z), np.exp(Z), 0.0)
    P = K / np.maximum(K.sum(1, keepdims=True), 1e-300)
    colw = np.ones(nC)
    for _ in range(iters):
        Kc = K.copy()
        Kc[:, :nC] *= colw[None, :]
        P = Kc / np.maximum(Kc.sum(1, keepdims=True), 1e-300)
        cs = P[:, :nC].sum(0)
        over = cs > 1.0 + 1e-6
        if not over.any():
            break
        colw = np.where(over, colw / np.maximum(cs, 1e-12), colw)
        # let columns that are now under-used recover a little (avoid over-shrinking)
        colw = np.where(~over & (cs < 0.999) & (colw < 1.0), np.minimum(1.0, colw / np.maximum(cs, 1e-3) ** 0.5), colw)
    return P[:, :nC], P[:, nC]


def map_assign(S, slack):
    """Hungarian MAP: -> list of (gi, k or None)."""
    from scipy.optimize import linear_sum_assignment
    nG, nC = S.shape
    BIG = 1e6
    C = np.full((nG, nC + nG), BIG)
    C[:, :nC] = np.where(np.isfinite(S), -S, BIG)
    C[np.arange(nG), nC + np.arange(nG)] = -slack
    r, c = linear_sum_assignment(C)
    out = []
    for i, j in zip(r, c):
        out.append((int(i), int(j) if j < nC and C[i, j] < BIG / 2 else None))
    out.sort()
    return out
