"""re-ranker experiments on gen rows. rr_exp.py GEN_DIR variant..."""
import os, sys, pickle, glob
import numpy as np
from collections import Counter
FP = os.environ["FP"]; sys.path[:0] = [FP]
import route_rerank as RR
new = set(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "never_used.txt")).read().strip().split(","))  # the 200 never-used courses
R = [r for r in (pickle.load(open(p, "rb")) for p in sorted(glob.glob(sys.argv[1] + "/*.pkl"))) if r and r.get("right") is not None]
states = sorted({r["state"] for r in R}); fold = {s: i % 5 for i, s in enumerate(states)}
old = [r for r in R if r["slug"] not in new]; nw = [r for r in R if r["slug"] in new]
H = lambda rs: sum(r["n"] for r in rs)
def oracle(rs, ks):
    g = 0
    for r in rs:
        g += max([0] + [r["right"][j] - r["right"][0] for j in range(1, len(r["seqs"])) if r["kinds"][j] in ks])
    return g
for ks in (["beam"], ["renum"], ["start"], ["end"], ["start", "end"], ["beam", "renum", "start", "end"]):
    print("oracle", ks, "choice +%d of %d, new +%d" % (oracle(old, ks), H(old), oracle(nw, ks)))
print("base choice %.2f new %.2f" % (100 * sum(r["right"][0] for r in old) / H(old), 100 * sum(r["right"][0] for r in nw) / H(nw)))

X2 = int(os.environ.get("X2", "0")); NC = int(os.environ.get("NC", "0")); SUB = [k for k in os.environ.get("SUB", "").split(",") if k] or None
NF = len(RR.FEATS) + 5 + len(RR.KINDS) + 2 + ((len(SUB) if SUB else 2 * len(RR.FEATS2)) if X2 else 0)
def rows(r, ks):
    X, y, idx = [], [], []
    f0 = r["F"][0]
    for j in range(1, len(r["seqs"])):
        if r["kinds"][j] not in ks: continue
        ham = sum(a != b for a, b in zip(r["seqs"][j], r["seqs"][0]))
        X.append(RR.row(r["F"][j], f0, r["kinds"][j], ham, r["n"], r["F2"][j] if X2 else None, r["F2"][0] if X2 else None, NC, SUB)); y.append(r["right"][j] - r["right"][0]); idx.append(j)
    return np.asarray(X, float).reshape(-1, NF), np.asarray(y, float), idx
def zrow(r):
    f0 = r["F"][0]
    return np.asarray([RR.row(f0, f0, "chosen", 0, r["n"], r["F2"][0] if X2 else None, r["F2"][0] if X2 else None, NC, SUB)], float)
def oof(ks, model="reg", loss="absolute_error", leaves=15, iters=300, msl=40):
    for r in R: r["X"], r["y"], r["idx"] = rows(r, ks)
    for f in range(5):
        tr = [r for r in R if fold[r["state"]] != f and len(r["y"])]
        X = np.concatenate([r["X"] for r in tr]); y = np.concatenate([r["y"] for r in tr])
        if model == "reg":
            from sklearn.ensemble import HistGradientBoostingRegressor
            m = HistGradientBoostingRegressor(max_iter=iters, max_leaf_nodes=leaves, learning_rate=0.05, loss=loss,
                                              l2_regularization=1.0, min_samples_leaf=msl, random_state=0).fit(X, y)
            pr = m.predict
        elif model == "cls":   # P(better) - P(worse), weighted
            from sklearn.ensemble import HistGradientBoostingClassifier
            m = HistGradientBoostingClassifier(max_iter=iters, max_leaf_nodes=leaves, learning_rate=0.05,
                                               l2_regularization=1.0, min_samples_leaf=msl, random_state=0).fit(X, np.sign(y).astype(int))
            cl = list(m.classes_)
            pr = lambda Z, m=m, cl=cl: m.predict_proba(Z)[:, cl.index(1)] - m.predict_proba(Z)[:, cl.index(-1)]
        elif model in ("rank", "rankbag"):
            import lightgbm as lgb
            # each course: rows incl. a zero row for seq0 (all-difference features 0)
            Xs, ys, gs = [], [], []
            for r in tr:
                z = zrow(r)
                XX = np.r_[z, r["X"]]; yy = np.r_[0, r["y"]]; yy = yy - yy.min()
                Xs.append(XX); ys.append(np.minimum(yy, 30).astype(int)); gs.append(len(XX))
            if model == "rank":
                m = lgb.LGBMRanker(n_estimators=iters, num_leaves=leaves, learning_rate=0.05, min_child_samples=msl,
                                   verbose=-1, label_gain=list(range(31)), lambdarank_truncation_level=3)
                m.fit(np.concatenate(Xs), np.concatenate(ys), group=gs)
            else:
                ms = [lgb.LGBMRanker(n_estimators=iters, num_leaves=leaves, learning_rate=0.05, min_child_samples=msl,
                                     verbose=-1, label_gain=list(range(31)), lambdarank_truncation_level=3,
                                     subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=sd).fit(
                          np.concatenate(Xs), np.concatenate(ys), group=gs) for sd in range(5)]
                class _Avg:
                    def predict(self, Z, ms=ms):
                        return np.mean([q.predict(Z) for q in ms], 0)
                m = _Avg()
            def pr(Z, m=m):
                return Z  # placeholder handled below
            for r in R:
                if fold[r["state"]] == f and len(r["y"]):
                    z = zrow(r)
                    s = m.predict(np.r_[z, r["X"]]); r["pred"] = s[1:] - s[0]
            continue
        for r in R:
            if fold[r["state"]] == f:
                r["pred"] = pr(r["X"]) if len(r["y"]) else np.zeros(0)
def ev(rs, thr):
    gain = sw = good = bad = 0
    for r in rs:
        if len(r["y"]) and r["pred"].max() > thr:
            j = int(np.argmax(r["pred"])); gain += r["y"][j]; sw += 1; good += r["y"][j] > 0; bad += r["y"][j] < 0
    return "%+4d (%d: +%d/-%d)" % (gain, sw, good, bad)
for v in sys.argv[2:]:
    ks, model, *rest = v.split(":")
    kw = dict(x.split("=") for x in rest)
    kw = {k: (int(x) if x.isdigit() else x) for k, x in kw.items()}
    oof(ks.split(","), model, **kw)
    qs = np.quantile(np.concatenate([r["pred"] for r in R if len(r["pred"])]), [0.9, 0.97, 0.99, 0.995, 0.999])
    thrs = sorted(set([0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0] + [round(float(q), 3) for q in qs]))
    print(v, " | ".join("thr %s choice %s new %s" % (t, ev(old, t), ev(nw, t)) for t in thrs), flush=True)
