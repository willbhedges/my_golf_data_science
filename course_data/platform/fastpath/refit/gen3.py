"""candidate routings per course + labels. gen.py SPLIT SC_DIR OUT_DIR [procs]"""
import os, sys, pickle, time, traceback
import numpy as np
FP = os.environ["FP"]
sys.path[:0] = [FP, os.path.dirname(FP)]
import route_struct as RS
import route_bench as RB
VER = os.environ.get("ROUTE_LEARN_VER", "feae37f33_d0+yall")


def one(c, sc_dir, out_dir):
    p = os.path.join(out_dir, c["slug"] + ".pkl")
    if os.path.exists(p):
        return "skip"
    import route_rerank as RR
    ld = RS.load(c, VER, sc_dir)
    if ld is None:
        pickle.dump(None, open(p, "wb")); return "none"
    x, d = ld
    if x.get("card") is None:
        pickle.dump(None, open(p, "wb")); return "nocard"
    P0 = RS.base_params()
    cost, seq, pr = RS.decode(d, x["card"], P0)
    if not seq:
        pickle.dump(None, open(p, "wb")); return "noseq"
    t = time.time()
    cands = RR.candidates(pr, seq)
    F = [RR.features(pr, s, seq) for k, s in cands]
    F2 = [RR.features2(pr, s) for k, s in cands]
    Cor = RS.correct(pr, d, x["truth"]) if len(x["truth"]) == int(x["n"]) else None
    right = [int(sum(Cor[i, c2] for i, c2 in enumerate(s))) for k, s in cands] if Cor is not None else None
    pickle.dump(dict(slug=c["slug"], state=c["state"], split=c["split"], n=int(x["n"]), kinds=[k for k, s in cands],
                     seqs=[s for k, s in cands], F=F, F2=F2, right=right, n_rc=int(Cor.any(1).sum()) if Cor is not None else None,
                     sec=time.time() - t,
                     # per-hole correctness of every option used by an alternative + the option's (tee, green) ids
                     # (t4 per-hole combination; ignored by the re-ranker scripts)
                     cor={(i, int(c2)): bool(Cor[i, c2]) for k, s in cands for i, c2 in enumerate(s)} if Cor is not None else None,
                     cand={int(c2): tuple(int(v) for v in pr.cand[c2]) for k, s in cands for c2 in s}), open(p, "wb"))
    return "ok"


def job(a):
    try:
        return a[0]["slug"], one(*a)
    except Exception:
        return a[0]["slug"], traceback.format_exc()[-400:]


if __name__ == "__main__":
    split, sc_dir, out = sys.argv[1:4]
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    os.makedirs(out, exist_ok=True)
    cs = [c for c in RB.courses(split) if c.get("card")]
    if len(sys.argv) > 5:
        S = set(open(sys.argv[5]).read().replace("\n", ",").split(","))
        cs = [c for c in cs if c["slug"] in S]
    cs = [c for c in cs if not os.path.exists(os.path.join(out, c["slug"] + ".pkl"))]
    print("todo", len(cs), flush=True)
    from multiprocessing import Pool
    with Pool(procs) as pool:
        for i, (s, r) in enumerate(pool.imap_unordered(job, [(c, sc_dir, out) for c in cs], chunksize=1)):
            if r not in ("ok", "skip") or i % 50 == 0:
                print(i, s, r, flush=True)
