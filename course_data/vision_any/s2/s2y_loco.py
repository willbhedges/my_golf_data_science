"""LOCO native classifier on per-year S2 features; P aggregated over seasons (drought gate).
python3 s2y_loco.py <courses,> [--drought 0.05]
Writes pred_s2y_<agg>.npz for agg in mean, median, min, gated (median over non-drought seasons) + drought.json."""
import os, sys, json, numpy as np, lightgbm as lgb
os.environ.setdefault("OMP_NUM_THREADS", "1")
import s2lib as S2, s2year as SY, common
COURSES = sys.argv[1].split(",")
DD = float(sys.argv[sys.argv.index("--drought") + 1]) if "--drought" in sys.argv else 0.05
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "s2y"
DROP = [s for s in (sys.argv[sys.argv.index("--drop") + 1].split(",") if "--drop" in sys.argv else []) if s]
P10 = dict(n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=0.8, subsample_freq=1,
           colsample_bytree=0.5, reg_lambda=5.0, n_jobs=1, verbose=-1, random_state=0)
LBL = (S2.NATIVE, S2.ROUGH, S2.FC)
_C = {}


def course(c):
    if c in _C: return _C[c]
    d = common.load(c)
    names, Y, g, di = SY.course_grid_years(c)
    keep = [i for i, n in enumerate(names) if not any(n.endswith(x) or x in n for x in DROP)]
    names = [names[i] for i in keep]; Y = {y: a[:, keep] for y, a in Y.items()}
    cell = S2.map_1m(d["idx"], g)
    ok = np.isin(d["cls"], LBL); cc = cell[ok]; nat = (d["cls"][ok] == S2.NATIVE).astype(float)
    u, inv = np.unique(cc, return_inverse=True); n = np.bincount(inv); fr = np.bincount(inv, nat) / n; k = n >= 30
    _C[c] = dict(names=names, Y=Y, g=g, di=di, cell=cell, c10=u[k], y10=(fr[k] >= 0.5).astype(int), w10=n[k])
    return _C[c]


def train(tr):
    Xs, ys, ws = [], [], []
    for c in tr:
        d = course(c); ny = len(d["Y"])
        for yr, G in d["Y"].items():
            X = G[d["c10"]]; y = d["y10"]; w = d["w10"].astype(float)
            for v in (0, 1):
                m = y == v
                if m.any(): w[m] = w[m] / w[m].sum() / ny
            Xs.append(X); ys.append(y); ws.append(w)
    X, y, w = np.concatenate(Xs), np.concatenate(ys), np.concatenate(ws)
    clf = lgb.LGBMClassifier(**P10); clf.fit(X, y, sample_weight=w * len(y) / w.sum())
    return clf


aggs = ("mean", "median", "min", "gated")
out = {a: {} for a in aggs}; dj = {}
for test in COURSES:
    clf = train([c for c in COURSES if c != test]); d = course(test)
    H, W = int(d["g"]["H"]), int(d["g"]["W"])
    yrs = sorted(d["Y"]); PY = np.stack([clf.predict_proba(d["Y"][y])[:, 1] for y in yrs]).astype(np.float32)
    di = np.array([d["di"][y] for y in yrs]); rel = di - np.nanmax(di)
    good = ~(rel <= -DD)
    if not good.any(): good[:] = True
    dj[test] = dict(years=yrs, drought_index=[float(x) for x in di], rel=[float(x) for x in rel], kept=[bool(x) for x in good])
    agg = dict(mean=PY.mean(0), median=np.median(PY, 0), min=PY.min(0), gated=np.median(PY[good], 0))
    for a in aggs:
        out[a][test + "_g"] = agg[a].reshape(H, W); out[a][test + "_p"] = agg[a][d["cell"]]
    print(test, "drought idx", " ".join(f"{y}:{x:+.3f}" for y, x in zip(yrs, di)), "kept", good.tolist(), flush=True)
for a in aggs:
    np.savez_compressed(f"pred_{TAG}_{a}.npz", **out[a])
json.dump(dj, open(f"drought_{TAG}.json", "w"), indent=1)
print("saved")
