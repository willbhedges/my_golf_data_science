"""ranker re-ranker: OOF picks + final fit. rr_fit.py GEN_DIR THR PICKS.json MODEL.pkl"""
import sys, pickle, json, numpy as np
sys.argv = [sys.argv[0], sys.argv[1]] + ["__none__"] + sys.argv[2:]
src = open(sys.argv[0].replace("rr_fit.py", "rr_exp.py")).read().split("for v in sys.argv[2:]:")[0]
exec(src)
thr, picks_p, model_p = float(sys.argv[3]), sys.argv[4], sys.argv[5]
KS = os.environ.get("KS", "start,end").split(",")
oof(KS, os.environ.get("MODEL", "rank"))
for t2 in sorted(set([thr] + [float(x) for x in os.environ.get("THRS", "").split(",") if x])):
    print("OOF thr", t2, "choice", ev(old, t2), "new", ev(nw, t2), flush=True)
    out = {}
    for r in R:
        if len(r["y"]) and r["pred"].max() > t2:
            out[r["slug"]] = r["seqs"][r["idx"][int(np.argmax(r["pred"]))]]
    pp = picks_p if t2 == thr else picks_p.replace(".json", "_%s.json" % t2)
    json.dump(out, open(pp, "w")); print("picks", t2, len(out), pp)
import lightgbm as lgb
if model_p == "-": sys.exit(0)
Xs, ys, gs = [], [], []
for r in R:
    if not len(r["y"]): continue
    z = zrow(r)
    XX = np.r_[z, r["X"]]; yy = np.r_[0, r["y"]]; yy = yy - yy.min()
    Xs.append(XX); ys.append(np.minimum(yy, 30).astype(int)); gs.append(len(XX))
if os.environ.get("MODEL", "rank") == "rankbag":
    m = RR.RankAvg([lgb.LGBMRanker(n_estimators=300, num_leaves=15, learning_rate=0.05, min_child_samples=40, verbose=-1,
                                   label_gain=list(range(31)), lambdarank_truncation_level=3, subsample=0.8,
                                   subsample_freq=1, colsample_bytree=0.8, random_state=sd).fit(
        np.concatenate(Xs), np.concatenate(ys), group=gs) for sd in range(5)])
else:
    m = lgb.LGBMRanker(n_estimators=300, num_leaves=15, learning_rate=0.05, min_child_samples=40, verbose=-1,
                       label_gain=list(range(31)), lambdarank_truncation_level=3)
    m.fit(np.concatenate(Xs), np.concatenate(ys), group=gs)
pickle.dump(dict(model=m, thr=thr, gen={}, kinds=KS, rank=True, feats2=bool(X2), noclub=bool(NC), feats2_sub=SUB), open(model_p, "wb")); print("fit", model_p)
