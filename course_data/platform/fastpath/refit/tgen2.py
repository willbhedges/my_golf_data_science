"""route_tee training rows: tgen.py SPLIT OUT_DIR [procs] [slugs]  (env as the bench; ROUTE_RERANK=0 + ROUTE_RERANK_PICKS for oof)"""
import os, sys, pickle, json, math, traceback
import numpy as np
FP = os.environ["FP"]; sys.path[:0] = [FP, os.path.dirname(FP)]
import route_bench as RB
import routing as R
from routing import Proj
VER = os.environ.get("ROUTE_LEARN_VER", "feae37f33_d0+yall")
CAP = {}

def first_part(ln):
    cum = np.r_[0, np.cumsum(np.hypot(*np.diff(ln, axis=0).T))]
    return ln[: max(2, int(np.searchsorted(cum, 0.6 * cum[-1])) + 1)]

def one(c, out_dir):
    p = os.path.join(out_dir, c["slug"] + ".pkl")
    if os.path.exists(p): return "skip"
    import route_scene as RS
    if not getattr(RS, "_wrapped", False):
        orig = RS.route
        def wrap(*a, **k):
            k = dict(k); prm = dict(k.get("params") or {}); dump = []; prm["tee_dump"] = dump; prm["tee"] = 0
            k["params"] = prm
            r = orig(*a, **k)
            CAP["d"] = (k.get("prepared") or [None])[0]; CAP["dump"] = dump; CAP["r"] = r
            return r
        RS.route = wrap; RS._wrapped = True
    CAP.clear()
    out = RB.run_one(c, "fast", "v2", 0, VER, prep=True)
    if "score" not in out or not CAP.get("dump"):
        pickle.dump(None, open(p, "wb")); return "none"
    d = CAP["d"]; cs = CAP["dump"][0]; pj = d["co"]["pj"]
    fc, _, _ = RB.course_files(c["slug"])
    n = int(out["n"])
    tr = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= n}
    rows = []
    for i, cc in enumerate(cs):
        if cc is None: continue
        t = tr.get(str(i + 1))
        if t is None: continue
        ln = out["lines"].get(str(i + 1))
        if ln is None: continue
        pr = Proj(*t["green_ll"]); line = pr.ring(t["line"]); fp = first_part(np.asarray(line))
        g_ok = math.hypot(*pr.fwd(*ln["co"][-1][:2])) <= 20
        LL = np.column_stack(pj.inv(*cc["P"].T)) if len(cc["P"]) else np.zeros((0, 2))
        y = np.array([R._seg_dist(np.asarray(pr.fwd(*q)), fp) <= 40 for q in LL])
        ts = np.asarray(pr.fwd(*t["tee_ll"]))
        dst = np.array([float(np.hypot(*(np.asarray(pr.fwd(*q)) - ts))) for q in LL])
        dln = np.array([float(R._seg_dist(np.asarray(pr.fwd(*q)), np.asarray(line))) for q in LL])
        rows.append(dict(i=i, F=cc["F"], y=y, dst=dst, dln=dln, tlen=float(t["length_yd"]), cpx=cc.get("cpx"), g_ok=bool(g_ok), P=cc["P"], src=cc["src"], inc_ok=bool(out["hole_ok"].get(str(i + 1)))))
    pickle.dump(dict(slug=c["slug"], state=c["state"], split=c["split"], n=n, rows=rows,
                     right=sum(out["hole_ok"].values())), open(p, "wb"))
    return "ok"

def job(a):
    try: return a[0]["slug"], one(*a)
    except Exception: return a[0]["slug"], traceback.format_exc()[-600:]

if __name__ == "__main__":
    split, out = sys.argv[1:3]
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    os.makedirs(out, exist_ok=True)
    cs = [c for c in RB.courses(split) if c.get("card")]
    if len(sys.argv) > 4:
        S = set(open(sys.argv[4]).read().replace("\n", ",").split(",")); cs = [c for c in cs if c["slug"] in S]
    cs = [c for c in cs if not os.path.exists(os.path.join(out, c["slug"] + ".pkl"))]
    print("todo", len(cs), flush=True)
    from multiprocessing import Pool
    with Pool(procs) as pool:
        for i, (s, r) in enumerate(pool.imap_unordered(job, [(c, out) for c in cs], chunksize=1)):
            if r not in ("ok", "skip") or i % 50 == 0: print(i, s, r, flush=True)
    print("GEN DONE", flush=True)
