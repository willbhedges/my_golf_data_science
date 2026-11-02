import numpy as np, itertools, os
from scipy import ndimage
from common import *
CS = [c for c in COURSES if os.path.exists(f"var/p_norm_{c}.npy")]
T1 = [0.3, 0.4, 0.5]; T2 = [0.0, 0.15, 0.2, 0.25, 0.3, 0.35]; RAD = [20, 40]
stats = {}
for c in CS:
    p = np.load(f"var/p_norm_{c}.npy").astype(np.float32) / 255
    d = load(c)
    cor = (d["along"] >= 180) & (d["along"] <= 320) & (np.abs(d["lat"]) <= 50) & np.isin(d["cls"], [NATIVE, ROUGH, FC])
    idx = d["idx"][cor]; y = d["cls"][cor] == NATIVE
    idx, first = np.unique(idx, return_index=True); y = y[first]
    ps = ndimage.uniform_filter(p, 3)
    valid = (p > 0).astype(np.float32)
    for R in RAD:
        lm = ndimage.uniform_filter(p, 2 * R + 1) / np.maximum(ndimage.uniform_filter(valid, 2 * R + 1), 1e-3)
        for t1, t2 in itertools.product(T1, T2):
            m = ((ps >= t1) & (lm >= t2)).ravel()[idx]
            stats[(c, R, t1, t2)] = ((m & y).sum(), (m & ~y).sum(), (~m & y).sum(), (m & ~y).sum() if c not in ("gateway_national","spirit_hollow","coldwater","ellis","mozingo") else 0)
    print(c, "ok", flush=True)
def agg(cs, k):
    a = np.sum([stats[(c,) + k] for c in cs], 0); tp, fp, fn, fpn = a
    return tp / max(tp + fp, 1), tp / max(tp + fn, 1), fpn
keys = [(R, t1, t2) for R in RAD for t1 in T1 for t2 in T2]
print("all-course table (in sample):")
for k in keys:
    pr, rc, fpn = agg(CS, k); print(k, "prec %.2f rec %.2f FPnoNative %d" % (pr, rc, fpn))
print("LOCO-selected (max recall s.t. prec>=0.7 on other courses):")
for c in CS:
    oth = [x for x in CS if x != c]
    best = max(keys, key=lambda k: (agg(oth, k)[0] >= 0.7, agg(oth, k)[1]))
    tp, fp, fn, _ = stats[(c,) + best]
    print(c, best, "test prec %.2f rec %.2f pred %d truth %d" % (tp / max(tp + fp, 1), tp / max(tp + fn, 1), tp + fp, tp + fn))
