import numpy as np, sys
from common import *
from sklearn.metrics import roc_auc_score
avail = [c for c in COURSES if os.path.exists(os.path.join(HERE, f"ds_{c}.npz"))]
rows = {}
P = {}
for c in avail:
    d = load(c); names = list(d["names"])
    nz, nn = add_norm(d)
    X = np.column_stack([d["X"], nz["X"]]); N = names + nn
    y = d["cls"] == NATIVE; ok = np.isin(d["cls"], [NATIVE, ROUGH, FC])
    P[c] = (X[ok], y[ok], N)
    print(c, "cells", ok.sum(), "native", y[ok].sum(), "share %.3f" % y[ok].mean())
N = P[avail[0]][2]
print()
print("feature".ljust(22), " ".join(c[:6].rjust(6) for c in avail), " pooledAUC")
res = []
for j, n in enumerate(N):
    a = []
    for c in avail:
        X, y, _ = P[c]
        v = X[:, j]; f = np.isfinite(v)
        a.append(roc_auc_score(y[f], v[f]) if 0 < y[f].mean() < 1 and f.mean() > .5 else np.nan)
    # pooled: native cells (all courses) vs non-native (all courses)
    Xa = np.concatenate([P[c][0][:, j] for c in avail]); ya = np.concatenate([P[c][1] for c in avail])
    f = np.isfinite(Xa)
    pa = roc_auc_score(ya[f], Xa[f]) if f.mean() > .5 else np.nan
    res.append((abs(pa - .5) if np.isfinite(pa) else 0, n, a, pa))
for _, n, a, pa in sorted(res, reverse=True)[:45]:
    print(n.ljust(22), " ".join(("%6.2f" % x) if np.isfinite(x) else "   nan" for x in a), " %.3f" % pa)
