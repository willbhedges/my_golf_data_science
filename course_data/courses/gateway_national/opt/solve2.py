"""(copied from the optimisation scratch; run as: python3 solve2.py <repo root> <which> <holes> <variants> <out.json>) Two-stage central-world solve (coarse 3000 swings on -60..60, fine N2 fresh swings on aim +/-10) per hole;
optional variants. Usage: solve2.py WT which holes variants out   (variants: comma list of names in VARS)"""
import json, os, sys, time
import numpy as np
WT, which, holes, variants, out = sys.argv[1:6]
sys.path.insert(0, os.path.join(WT, "course_data", "courses"))
import v2_course as vc
course, meta, M, D = vc.activate(os.environ.get("SLUG", "gateway_national"), which)
N1, N2 = 3000, int(os.environ.get("N2", 16000))
z1, z2 = M.draws_z(N1, 7), M.draws_z(N2, 77)
def wind_hook(sp, rel):
    import wind as W
    def mk(c):
        def f(carry, roll, sig_lat, sig_car):
            c2, t2, w2, d2, drift = W.adjust((carry, carry + roll, 4 * sig_lat, 4 * sig_car), sp, rel, club_name=c)
            return c2, max(t2 - c2, 0.0), w2 / 4, d2 / 4, drift
        return f
    return mk
def solve(h, P, wind=None):
    hd = M.HOLES[h]; R = M.Raster(hd); S = R.strokes(P, hd["length"])
    res = {}
    for c in M.REAL_CLUBS:
        hk = wind(c) if wind else None
        ev, _ = M.ev_curve(R, S, hd, c, P, z1, D.AIMS, wind=hk)
        r = D.robust_aim(D.AIMS, ev)
        aims = np.arange(r["aim"] - 10, r["aim"] + 10.01, 0.5)
        ev2, (a, l, lie, s) = M.ev_curve(R, S, hd, c, P, z2, aims, wind=hk)
        r2 = D.robust_aim(aims, ev2, lo=max(-40, aims[0]), hi=min(40, aims[-1]))
        j = int(np.argmin(np.abs(aims - r2["aim"])))
        res[c] = dict(aim=r2["aim"], ev=r2["ev"], s=(1.0 + s[:, j]), lie=lie[:, j])
    o = sorted(res, key=lambda c: res[c]["ev"])
    d = res[o[1]]["s"] - res[o[0]]["s"]
    tr = float(np.mean(res[o[0]]["lie"] == M.CODE["recovery"]))
    return dict(pick=o[0], runner=o[1], third=o[2], aim=res[o[0]]["aim"], margin=float(res[o[1]]["ev"] - res[o[0]]["ev"]),
                se=float(d.std(ddof=1) / np.sqrt(N2)), m3=float(res[o[2]]["ev"] - res[o[0]]["ev"]),
                ev={c: round(res[c]["ev"], 4) for c in o}, aims={c: res[c]["aim"] for c in o}, trees=round(tr, 3))
def _cap(h, c):
    for k, v in list(M.HOLES[h].get("elev", {}).items()):
        M.HOLES[h]["elev"][k] = (v[0], min(v[1], c)) + tuple(v[2:])
    return D.central(h)
def C(h, **kw):
    return D.central(h, **kw)
VARS = {
  "central": lambda h: (C(h), None),
  "carry+5": lambda h: (C(h, c_common=5.0), None),
  "carry-5": lambda h: (C(h, c_common=-5.0), None),
  "width+10": lambda h: (C(h, width={c: v * 1.1 for c, v in C(h)["width"].items()}), None),
  "width-10": lambda h: (C(h, width={c: v * 0.9 for c, v in C(h)["width"].items()}), None),
  "roll0.8": lambda h: (C(h, roll_mult=0.8), None),
  "roll1.2": lambda h: (C(h, roll_mult=1.2), None),
  "cap1.0": lambda h: (_cap(h, 1.0), None),
  "head5": lambda h: (C(h), wind_hook(5, 0)), "tail5": lambda h: (C(h), wind_hook(5, 180)),
  "left5": lambda h: (C(h), wind_hook(5, 90)), "right5": lambda h: (C(h), wind_hook(5, 270)),
}
res = {}
for hs in (holes.split(",") if holes else [str(k) for k in course.ORDER if k in course.HOLES]):
    h = int(hs); res[hs] = {}
    for v in variants.split(","):
        t = time.time(); P, w = VARS[v](h); r = solve(h, P, w); res[hs][v] = r
        print(which, hs, v, r["pick"], r["aim"], "m=%.4f se=%.4f" % (r["margin"], r["se"]), r["runner"], "trees", r["trees"], "%.0fs" % (time.time() - t), flush=True)
    json.dump(res, open(out, "w"), indent=0)
