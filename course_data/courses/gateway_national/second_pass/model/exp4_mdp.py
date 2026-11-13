"""Hole-specific second-shot rollout vs the one-shot table: does it change a Back tee decision?
python3 exp4_mdp.py out.json [holes] [kappa]"""
import json, sys, time
from harness import *
import mdp

out = sys.argv[1]
holes = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] else HOLES
kappas = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [1.6]
res = {}
for h in holes:
    P = D.central(h)
    R = raster(h)
    base = solve(h, P)
    res[h] = dict(base=base)
    print(h, "table   ", short(base), {c: (v["aim"], v["ev"]) for c, v in list(base["clubs"].items())[:4]}, flush=True)
    for k in kappas:
        t0 = time.time()
        S, S2, g = mdp.improved_S(M, h, P, R, k)
        # level: mean delta over fairway nodes (the rollout is calibrated on a featureless hole at 150 yds)
        inf = g["info"]
        dl = np.array([g["delta"][i, j] for (i, j) in inf])
        dd = np.array([v[3] for v in inf.values()])
        fw = np.array([v[4] == "fairway" for v in inf.values()])
        lev = float(np.mean(dl[fw])) if fw.any() else 0.0
        r = solve(h, P, S=S2)
        # the same with the hole's mean fairway shift removed is identical for decisions except S&D; report both
        byd = {}
        for lo in range(60, 400, 40):
            m = fw & (dd >= lo) & (dd < lo + 40)
            if m.sum() >= 3:
                byd[lo] = (round(float(dl[m].mean()), 3), round(float(dl[m].min()), 3), round(float(dl[m].max()), 3))
        res[h]["kappa%.1f" % k] = dict(r, level=lev, by_dist=byd)
        print(h, "MDP k=%.1f" % k, short(r), "| " + compare(base, r), "| fairway delta mean %.3f by dist %s  %.0fs" % (
            lev, byd, time.time() - t0), {c: (v["aim"], v["ev"]) for c, v in list(r["clubs"].items())[:4]}, flush=True)
    json.dump({str(a): b for a, b in res.items()}, open(out, "w"), indent=0, default=float)
