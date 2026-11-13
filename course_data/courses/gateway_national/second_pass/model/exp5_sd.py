"""Stroke-and-distance cost: the engine charges 1 + tee_value(length) = 1 + (PGA Tour tee baseline, clipped to
300-600 yds) + am_tee_off 0.40. The exact cost of replaying the tee shot is 1 + V*, V* = the hole's own expected
score from the tee under the same model (a fixed point: V = E[strokes | no S&D] + p_sd (1 + V)). Compare, and
re-solve with the self-consistent value.  python3 exp5_sd.py out.json"""
import json, sys
from harness import *

out = sys.argv[1]
orig = M.tee_value
FIX = {}
M.tee_value = lambda length, P: P["tee_v"] if P.get("tee_v") is not None else orig(length, P)
res = {}
for h in HOLES:
    P = D.central(h)
    L = M.HOLES[h]["length"]
    base = solve(h, P, keep=True)
    raw = base.pop("raw")
    lie = raw[base["pick"]]["lie"]
    v = base["clubs"][base["pick"]]["ev"]
    hist = [v]
    r = base
    for it in range(4):
        r = solve(h, dict(P, tee_v=v))
        v = r["clubs"][r["pick"]]["ev"]
        hist.append(v)
    res[h] = dict(length=L, engine_sd_value=float(orig(L, P)), base=base, fixed=r, hist=hist,
                  p_ob=float(np.mean(lie == M.CODE["ob"])), p_native=float(np.mean(lie == M.CODE["native"])))
    print(h, L, "engine re-tee value %.3f | own EV %.3f -> fixed point %.3f | base %s | fixed %s | %s" % (
        orig(L, P), hist[0], hist[-1], short(base), short(r), compare(base, r)), flush=True)
    json.dump({str(a): b for a, b in res.items()}, open(out, "w"), indent=0, default=float)
