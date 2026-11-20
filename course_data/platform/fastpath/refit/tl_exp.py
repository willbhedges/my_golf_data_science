"""tee-choice experiments on tgen2 rows. tl_exp.py GEN_DIR CACHE.pkl variant..."""
import os, sys, pickle, glob, json
import numpy as np
FP = os.environ["FP"]; sys.path[:0] = [FP, os.path.dirname(FP)]
import route_tee as RT
import route_bench as RB
new = set(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "never_used.txt")).read().strip().split(","))  # the 200 never-used courses
GEN, CACHE = sys.argv[1], sys.argv[2]
R = [r for r in (pickle.load(open(p, "rb")) for p in sorted(glob.glob(GEN + "/*.pkl"))) if r]
states = sorted({r["state"] for r in R}); fold = {s: i % 5 for i, s in enumerate(states)}
DI = RT.FEATS.index("D")
import route_scene as RSc
S1 = RSc._mods()[3]
def _card(slug):
    _, _, scj = RB.course_files(slug)
    return RB.bench_card(scj)[1]          # the bench's card convention (ROUTE_BENCH_CARD, pick by default)
for r in R:
    Y = S1.card_sets(_card(r["slug"]), r["n"])
    ys = RT.course_set(Y, {h["i"]: float(h["F"][0, DI]) for h in r["rows"]}); r["yset"] = ys
    for h in r["rows"]:
        h["rset"] = RT.set_resid(h["F"], ys[h["i"]] if ys is not None else None)
        h["yy"] = ys[h["i"]] if ys is not None else None

def extra(h):
    """extra per-candidate features computable from the stored rows"""
    F = h["F"]; P = h["P"]
    m = len(P)
    rs = h["rset"]
    rk = np.argsort(np.argsort(rs)).astype(float)
    pt = F[:, RT.FEATS.index("pt")]
    # local context: candidates within 30 yd, how many farther from green within 30 yd (back-of-tee-cluster)
    dd = np.hypot(*(P[:, None] - P[None]).transpose(2, 0, 1))
    D = F[:, DI]
    nb = ((dd < 30) & (D[None] > D[:, None] + 3)).sum(1).astype(float)
    nn = (dd < 30).sum(1).astype(float)
    return np.c_[rs, rk, rs - rs[0], nb, nn, pt - pt.max()]

def X_of(h, ex):
    return np.c_[h["F"], extra(h)] if ex else h["F"]

def lab(h, kind):
    if kind == "len": return h["y"].astype(int)
    if kind.startswith("str"):
        T = float(kind[3:]); return (h["y"] & (h["dst"] <= T)).astype(int)
    if kind.startswith("grade"):
        T = float(kind[5:]); return h["y"].astype(int) + (h["y"] & (h["dst"] <= T)).astype(int)
    raise ValueError(kind)

def fit_pred(kind, ex, rank=False, iters=300, leaves=31, allg=False):
    key = (kind, ex, rank, iters, leaves, allg)
    C = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else {}
    if key in C:
        return C[key]
    out = {}
    for f in range(5):
        tr = [h for r in R if fold[r["state"]] != f for h in r["rows"] if h["g_ok"] or allg]
        X = np.concatenate([X_of(h, ex) for h in tr]); y = np.concatenate([lab(h, kind) for h in tr])
        if rank:
            import lightgbm as lgb
            m = lgb.LGBMRanker(n_estimators=iters, num_leaves=leaves, learning_rate=0.05, min_child_samples=40,
                               reg_lambda=1.0, verbose=-1, label_gain=[0, 1, 3, 7])
            m.fit(X, y, group=[len(h["P"]) for h in tr])
            pr = lambda Z: m.predict(Z)
        else:
            from sklearn.ensemble import HistGradientBoostingClassifier
            m = HistGradientBoostingClassifier(max_iter=iters, max_leaf_nodes=leaves, learning_rate=0.05,
                                               l2_regularization=1.0, min_samples_leaf=40, random_state=0).fit(X, y > 0 if kind.startswith("grade") and False else y)
            pr = (lambda Z: m.predict_proba(Z)[:, 1]) if len(m.classes_) == 2 else (lambda Z: m.predict_proba(Z) @ np.arange(len(m.classes_)))
        for r in R:
            if fold[r["state"]] == f:
                for h in r["rows"]:
                    out[(r["slug"], h["i"])] = pr(X_of(h, ex))
    C = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else {}
    C[key] = out; pickle.dump(C, open(CACHE, "wb"))
    return out

def evaluate(rs, pick):
    H = base = gain = sw = good = bad = 0; yd = []
    for r in rs:
        H += r["n"]; base += r["right"]
        for h in r["rows"]:
            if not h["g_ok"]: continue
            j = pick(r, h)
            if h["yy"] is not None and h["yy"] == h["yy"]: yd.append(abs(h["F"][j, DI] - h["yy"]))
            if j:
                sw += 1; dg = int(h["y"][j]) - int(h["y"][0]); gain += dg; good += dg > 0; bad += dg < 0
    return "%.2f%% gain %d (+%d/-%d) sw %d yd %.1f/%.1f" % (100 * (base + gain) / H, gain, good, bad, sw, np.median(yd), np.percentile(yd, 90))

old = [r for r in R if r["slug"] not in new]; nw = [r for r in R if r["slug"] in new]
def rep(name, pick):
    print("%-40s choice %s | new %s" % (name, evaluate(old, pick), evaluate(nw, pick)), flush=True)
rep("incumbent", lambda r, h: 0)

def pk_choose(P, eps, delta):
    return lambda r, h: RT.choose(P[(r["slug"], h["i"])], h["rset"], delta, eps)

def pk_combo(Pa, Pb, eps, delta, eps2=0.0):
    """among Pa within eps of max: argmax Pb (then card tie-break within eps2); switch when Pa beats inc by delta"""
    def f(r, h):
        a = Pa[(r["slug"], h["i"])]; b = Pb[(r["slug"], h["i"])]
        A = np.where(a >= a.max() - eps)[0]
        bb = b[A]; B = A[bb >= bb.max() - eps2]
        j = int(B[np.argmin(h["rset"][B])])
        return j if (j != 0 and a[j] - a[0] > delta) else 0
    return f

for v in sys.argv[3:]:
    kind, ex, mode = v.split(":")[:3]
    ex = int(ex)
    if mode == "rank":
        P = fit_pred(kind, ex, rank=True)
        for eps in (0.0, 0.1, 0.3):
            rep(f"{v} rank eps{eps}", lambda r, h, P=P, eps=eps: (lambda s: (lambda j: j if s[j] - s[0] > 0 else 0)(
                int((lambda A: A[np.argmin(h['rset'][A])])(np.where(s >= s.max() - eps)[0]))))(P[(r['slug'], h['i'])]))
        continue
    P = fit_pred(kind, ex)
    if mode == "grid":
        for eps in (0.0, 0.05, 0.1, 0.15, 0.2):
            for delta in (0.0, 0.05):
                rep(f"{v} eps{eps} d{delta}", pk_choose(P, eps, delta))
    elif mode.startswith("combo"):
        Pa = fit_pred("len", ex)
        for eps in (0.05, 0.1, 0.15, 0.2, 0.3):
            for eps2 in (0.0, 0.05):
                rep(f"{v} eps{eps} eps2 {eps2}", pk_combo(Pa, P, eps, 0.0, eps2))
