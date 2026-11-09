"""Pixel 'unmown' model, leave-one-course-out. python3 mow_pix.py MOWDIR OUT.pkl"""
import pickle, sys, os, numpy as np, glob, warnings
warnings.filterwarnings("ignore")
from scipy import ndimage
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
D, OUT = sys.argv[1:3]
NK = ("ndvi", "gray", "tex", "ntex", "tex9", "exg")

def feats(g):
    """per-cell feature dict (2-D arrays) for one hole grid"""
    sh = g["shape"]
    R = lambda k: np.asarray(g[k]).reshape(sh)
    hag = R("hag"); tree = np.nan_to_num(hag) >= 2.5
    if "chm" in g: tree |= np.nan_to_num(R("chm")) >= 3.0
    d = R("d"); open_ = ~tree & ~R("haz") & ~R("othermown")
    F = (d <= 0) & ~tree; N = (d >= 1) & (d < 6) & open_
    sm = lambda v: ndimage.uniform_filter(np.nan_to_num(v.astype(np.float32)), 5)
    f = {}
    f["hag25"] = sm((np.nan_to_num(hag) >= 0.25) & ~tree); f["hagm"] = sm(np.clip(np.nan_to_num(hag), 0, 2.5) * ~tree)
    f["s2"] = R("s2") if "s2" in g else np.full(sh, np.nan, np.float32)
    ys = [i for i in (0, 1) if f"y{i}_ndvi" in g]
    per = {k: [] for k in NK}
    for i in ys:
        for k in NK:
            v = sm(R(f"y{i}_{k}"))
            rF = np.nanmedian(v[F]) if F.sum() > 20 else np.nan
            rN = np.nanmedian(v[N]) if N.sum() > 20 else rF
            per[k].append((v, v - rF, v - rN))
    for k in NK:
        if not per[k]:
            for nm in ("", "_dF", "_dN", "_mdN"): f[k + nm] = np.full(sh, np.nan, np.float32)
            continue
        f[k] = np.mean([p[0] for p in per[k]], 0); f[k + "_dF"] = np.nanmean([p[1] for p in per[k]], 0)
        dn = np.array([p[2] for p in per[k]]); f[k + "_dN"] = np.nanmean(dn, 0)
        f[k + "_mdN"] = (np.nanmin(dn, 0) if k in ("tex", "ntex", "tex9") else np.nanmax(dn, 0))
    for k in ("hag25", "hagm"):
        rF = np.nanmedian(f[k][F]) if F.sum() > 20 else 0.0
        f[k + "_dF"] = f[k] - rF
    return f, dict(tree=tree, open=open_, d=d)

FN = None
if __name__ == "__main__":
    rows = []
    for fp in sorted(glob.glob(D + "/*.pkl")):
        c = pickle.load(open(fp, "rb"))
        rng = np.random.default_rng(0)
        for ref, g in c["holes"].items():
            if "foot" not in g: continue
            f, m = feats(g); sh = g["shape"]
            FN = sorted(f)
            sel = g["foot"].reshape(sh) & m["open"] & (m["d"] > 0) & (m["d"] < 60)
            sel &= rng.random(sh) < 0.15
            X = np.stack([f[k][sel] for k in FN], 1).astype(np.float32)
            rows.append(dict(slug=c["slug"], hole=ref, X=X, y=g["t_native"].reshape(sh)[sel], d=m["d"][sel]))
    slugs = sorted(set(r["slug"] for r in rows))
    print(FN)
    models = {}
    for held in slugs + [None]:
        tr = [r for r in rows if r["slug"] != held]
        X = np.concatenate([r["X"] for r in tr]); y = np.concatenate([r["y"] for r in tr])
        w = np.concatenate([np.full(len(r["y"]), 1.0 / sum(len(q["y"]) for q in tr if q["slug"] == r["slug"])) for r in tr]); w *= len(w) / w.sum()
        mdl = lgb.LGBMClassifier(n_estimators=150, num_leaves=15, learning_rate=0.06, min_child_samples=200, subsample=0.7, subsample_freq=1, colsample_bytree=0.7, reg_lambda=5.0, verbose=-1, n_jobs=2)
        mdl.fit(X, y, sample_weight=w)
        models[held or "_all"] = mdl
        if held:
            te = [r for r in rows if r["slug"] == held]
            Xt = np.concatenate([r["X"] for r in te]); yt = np.concatenate([r["y"] for r in te])
            p = mdl.predict_proba(Xt)[:, 1]
            print(f"{held:20s} n {len(yt):7d} pos {yt.mean():.2f} AUC {roc_auc_score(yt, p) if 0 < yt.mean() < 1 else float('nan'):.3f}  mean p pos {p[yt].mean() if yt.any() else float('nan'):.2f} neg {p[~yt].mean():.2f}", flush=True)
    imp = dict(zip(FN, models["_all"].feature_importances_)); print(sorted(imp.items(), key=lambda kv: -kv[1])[:12])
    pickle.dump(dict(FN=FN, models=models), open(OUT, "wb"))
