"""Value-function / penalty sensitivities, central world, every Back tee shot.  python3 exp1_value.py out.json [holes]"""
import json, sys, time
from harness import *

out = sys.argv[1]
holes = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else HOLES
names = sys.argv[3].split("|") if len(sys.argv) > 3 else None
C = lambda h, **kw: D.central(h, **kw)                     # noqa: E731
VARS = {
    "central": lambda h: C(h),
    "tour table": lambda h: C(h, table="tour"),
    "am level 0.20 (scratch)": lambda h: C(h, am_off=0.20, am_tee_off=0.22),
    "am level 0.50 (5+ hcp)": lambda h: C(h, am_off=0.50, am_tee_off=0.56),
    "am_slope 0": lambda h: C(h, am_slope=0.0),
    "am_slope 0.0025": lambda h: C(h, am_slope=0.0025),
    "m_rough 0.4": lambda h: C(h, m_rough=0.4),
    "m_rough 1.0": lambda h: C(h, m_rough=1.0),
    "m_rough 1.3": lambda h: C(h, m_rough=1.3),
    "m_sand 1.5": lambda h: C(h, m_sand=1.5),
    "lost 0.05-0.25 (dormant, thin)": lambda h: C(h, lost_edge=0.05, lost_deep=0.25),
    "lost 0.10-0.40": lambda h: C(h, lost_edge=0.10, lost_deep=0.40),
    "lost 0.40-0.90": lambda h: C(h, lost_edge=0.40, lost_deep=0.90),
    "trees 0.5": lambda h: C(h, trees=0.5),
    "trees 1.0": lambda h: C(h, trees=1.0),
    "punch_adv 60": lambda h: C(h, punch_adv=60.0),
    "block_sev 0": lambda h: C(h, block_sev=0.0),
    "block_sev 0.8": lambda h: C(h, block_sev=0.8),
    "first_cut 0": lambda h: C(h, first_cut=0.0),
}
res = {}
for h in holes:
    res[h] = {}
    for k, f in VARS.items():
        if names and k not in names and k != "central":
            continue
        t = time.time()
        r = solve(h, f(h))
        res[h][k] = r
        print(h, "%-32s" % k, short(r), "| " + (compare(res[h]["central"], r) if k != "central" else ""),
              "%.0fs" % (time.time() - t), flush=True)
    json.dump({str(a): b for a, b in res.items()}, open(out, "w"), indent=0, default=float)
