"""tl_fit.py GEN_DIR CACHE TAU LAM_R LAM_C PICKS.json MODEL.pkl : hybrid tee rule OOF picks + final fits"""
import sys, pickle, json, numpy as np
tau, lam_r, lam_c, picks_p, model_p = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6], sys.argv[7]
sys.argv = sys.argv[:3]
src = open(sys.argv[0].replace("tl_fit.py", "tl_exp.py")).read().split('old = [r for r')[0]; exec(src)
Pc = fit_pred("len", 0); Pr = fit_pred("len", 1, rank=True)
old = [r for r in R if r["slug"] not in new]; nw = [r for r in R if r["slug"] in new]
def pick(r, h):
    k = (r['slug'], h['i']); pc = Pc[k]; rs = h['rset']
    if pc[0] < tau:
        s = Pr[k] - lam_r * np.minimum(rs, 0.3); j = int(np.argmax(s))
        if j and s[j] > s[0]: return j
    return RT.choose(pc, rs, 0.0, 0.15, lam_c)
for nm, f in (("incumbent", lambda r, h: 0), ("course-set eps .15", lambda r, h: RT.choose(Pc[(r['slug'], h['i'])], h['rset'], 0.0, 0.15)), ("hybrid", pick)):
    print("%-20s choice %s | new %s" % (nm, evaluate(old, f), evaluate(nw, f)), flush=True)
out = {}
for r in R:
    for h in r["rows"]:
        j = pick(r, h)
        if j: out.setdefault(r["slug"], {})[str(h["i"])] = [float(v) for v in h["P"][j]]
json.dump(out, open(picks_p, "w")); print("picks courses", len(out))
if model_p != "-":
    from sklearn.ensemble import HistGradientBoostingClassifier
    import lightgbm as lgb
    tr = [h for r in R for h in r["rows"] if h["g_ok"]]
    X = np.concatenate([h["F"] for h in tr]); y = np.concatenate([lab(h, "len") for h in tr])
    mc = HistGradientBoostingClassifier(max_iter=300, max_leaf_nodes=31, learning_rate=0.05, l2_regularization=1.0,
                                        min_samples_leaf=40, random_state=0).fit(X, y)
    X1 = np.concatenate([X_of(h, 1) for h in tr])
    mr = lgb.LGBMRanker(n_estimators=300, num_leaves=31, learning_rate=0.05, min_child_samples=40, reg_lambda=1.0,
                        verbose=-1, label_gain=[0, 1, 3, 7]).fit(X1, y, group=[len(h["P"]) for h in tr])
    pickle.dump(dict(model=mc, delta=0.0, eps=0.15, lam=lam_c, keep=list(range(len(RT.FEATS))), rank=mr, tau=tau,
                     lam_r=lam_r), open(model_p, "wb")); print("fit", model_p)
