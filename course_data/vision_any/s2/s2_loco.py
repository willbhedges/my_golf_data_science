"""Leave-one-course-out native classifier on Sentinel-2 10 m features (alone / fused with the v3 1 m features).
python3 s2_loco.py <featset> [courses]      featset: s2 | s2raw | s2fw | ctx | fused | v3
Writes pred_<featset>.npz: <slug>_p (P per 1 m ds cell), <slug>_g (10 m grid P; s2 featsets only)."""
import os, sys, numpy as np, lightgbm as lgb
os.environ.setdefault("OMP_NUM_THREADS", "1")
import s2lib as S2
FS = sys.argv[1]
COURSES = sys.argv[2].split(",") if len(sys.argv) > 2 else S2.COURSES
import common
common.COURSES[:] = COURSES
import model_lib as ML
P10 = dict(n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=0.8, subsample_freq=1,
           colsample_bytree=0.5, reg_lambda=5.0, n_jobs=1, verbose=-1, random_state=0)
LBL = (S2.NATIVE, S2.ROUGH, S2.FC)
_C = {}


def course(c):
    if c in _C: return _C[c]
    d = common.load(c)
    out = dict(cls=d["cls"], along=d["along"], lat=d["lat"], ref=d["ref"], idx=d["idx"],
               dfw=d["X"][:, list(d["names"]).index("d_fairway")])
    if FS != "v3":
        names, G, g = S2.course_grid(c, "s2" if FS == "fused" else FS)
        cell = S2.map_1m(d["idx"], g)
        out.update(names=names, G=G, cell=cell, g=g)
        ok = np.isin(d["cls"], LBL)
        cc = cell[ok]; nat = (d["cls"][ok] == S2.NATIVE).astype(float)
        u, inv = np.unique(cc, return_inverse=True)
        n = np.bincount(inv); fr = np.bincount(inv, nat) / n
        k = n >= 30
        out.update(c10=u[k], y10=(fr[k] >= 0.5).astype(int), w10=n[k], f10=fr[k])
    if FS in ("fused", "v3"):
        D = ML.course("norm", c)
        out["Xv3"] = D["X"]
    _C[c] = out
    return out


def train_10(tr):
    Xs, ys, ws = [], [], []
    for c in tr:
        d = course(c); X = d["G"][d["c10"]]; y = d["y10"]; w = d["w10"].astype(float)
        for v in (0, 1):                      # balance classes and courses
            m = y == v
            if m.any(): w[m] = w[m] / w[m].sum()
        Xs.append(X); ys.append(y); ws.append(w)
    X, y, w = np.concatenate(Xs), np.concatenate(ys), np.concatenate(ws)
    clf = lgb.LGBMClassifier(**P10); clf.fit(X, y, sample_weight=w * len(y) / w.sum())
    return clf


def sample_1m(c, seed=0):
    R = np.random.default_rng(seed); d = course(c)
    y = d["cls"] == S2.NATIVE; ok = np.isin(d["cls"], LBL); out = []
    for v in (True, False):
        j = np.flatnonzero(ok & (y == v))
        if len(j): out.append(R.choice(j, min(ML.N_PER, len(j)), replace=False))
    return np.concatenate(out), y


def X1(c, j=None):
    d = course(c); j = np.arange(len(d["cls"])) if j is None else j
    if FS == "v3": return d["Xv3"][j]
    return np.hstack([d["Xv3"][j], d["G"][d["cell"][j]]])


def train_1m(tr):
    Xs, ys, ws = [], [], []
    for c in tr:
        j, y = sample_1m(c); Xs.append(X1(c, j)); ys.append(y[j].astype(int)); ws.append(np.full(len(j), 1.0 / len(j)))
    X, y, w = np.concatenate(Xs), np.concatenate(ys), np.concatenate(ws)
    clf = lgb.LGBMClassifier(**ML.PARAMS); clf.fit(X, y, sample_weight=w * len(y) / w.sum())
    return clf


out = {}
for test in COURSES:
    tr = [c for c in COURSES if c != test]
    d = course(test)
    if FS in ("fused", "v3"):
        clf = train_1m(tr)
        out[test + "_p"] = clf.predict_proba(X1(test))[:, 1].astype(np.float32)
    else:
        clf = train_10(tr)
        G = d["G"]; pg = clf.predict_proba(G)[:, 1].astype(np.float32)
        out[test + "_g"] = pg.reshape(int(d["g"]["H"]), int(d["g"]["W"]))
        out[test + "_p"] = pg[d["cell"]]
        if test == COURSES[0]:
            imp = sorted(zip(clf.booster_.feature_importance("gain"), d["names"]), reverse=True)[:15]
            print("top gain:", ", ".join(n for _, n in imp), flush=True)
    print(test, "done", flush=True)
np.savez_compressed(f"pred_{FS}.npz", **out)
print("saved")
