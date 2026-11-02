import numpy as np, lightgbm as lgb
from common import *
N_PER = 15000
CTX = ("slope", "relz25", "relz8", "canopy_frac15")
DROP = set()   # features excluded by featset tweaks (set by caller)

def norm_stats(d):
    names = list(d["names"]); ref = ref_mask(d, d["Xc"], names); st = {}
    for n in NORM:
        if n not in names: continue
        r = d["Xc"][ref, names.index(n)]; r = r[np.isfinite(r)]
        if len(r) < 200: st[n] = None; continue
        med = np.median(r); st[n] = (med, 1.4826 * np.median(np.abs(r - med)) + 1e-4)
    return st

def build(FS, names, Xraw, st):
    cols, N = [], []
    if FS in ("base", "norm"):
        cols.append(Xraw); N += names
    elif FS == "normonly":
        ctx = [i for i, n in enumerate(names) if n.startswith("d_") or n in CTX]
        cols.append(Xraw[:, ctx]); N += [names[i] for i in ctx]
    if FS in ("norm", "normonly"):
        for n in NORM:
            if n not in st: continue
            v = Xraw[:, names.index(n)]
            cols.append(((v - st[n][0]) / st[n][1]).astype(np.float32)[:, None] if st[n] else np.full((len(v), 1), np.nan, np.float32))
            N.append("z_" + n)
    X = np.column_stack(cols)
    keep = [i for i, n in enumerate(N) if n not in DROP]
    return X[:, keep], [N[i] for i in keep]

_CACHE = {}
def course(FS, c):
    k = (FS, c)
    if k not in _CACHE:
        d = load(c); names = list(d["names"]); st = norm_stats(d)
        X, N = build(FS, names, d["X"], st); Xc, _ = build(FS, names, d["Xc"], st)
        _CACHE[k] = dict(X=X, Xc=Xc, N=N, cls=d["cls"], along=d["along"], lat=d["lat"], strict=d["strict"], st=st, names=names)
    return _CACHE[k]

def sample(FS, c, seed=0):
    R = np.random.default_rng(seed); D = course(FS, c)
    y = D["cls"] == NATIVE; ok = np.isin(D["cls"], [NATIVE, ROUGH, FC]); out = []
    for v in (True, False):
        j = np.flatnonzero(ok & (y == v))
        if len(j): out.append(R.choice(j, min(N_PER, len(j)), replace=False))
    j = np.concatenate(out)
    return D["X"][j], y[j].astype(int)

PARAMS = dict(n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=200, subsample=0.8,
              subsample_freq=1, colsample_bytree=0.5, reg_lambda=5.0, n_jobs=1, verbose=-1, random_state=0)

def fit_loco(FS, test, courses=COURSES):
    tr = [c for c in courses if c != test]
    Xs, ys, ws = [], [], []
    for c in tr:
        X, y = sample(FS, c); Xs.append(X); ys.append(y); ws.append(np.full(len(y), 1.0 / len(y)))
    X, y, w = np.concatenate(Xs), np.concatenate(ys), np.concatenate(ws)
    clf = lgb.LGBMClassifier(**PARAMS); clf.fit(X, y, sample_weight=w * len(y) / w.sum())
    return clf, course(FS, tr[0])["N"]

def features_for_grid(FS, slug, F, idx):
    D = course(FS, slug)
    Xraw = F.matrix(idx, D["names"]).astype(np.float32)
    return build(FS, D["names"], Xraw, D["st"])[0]
