"""Look inside the rollout on one hole: the delta map (hole-specific cost of the next shot) on the landing area and
the chosen second shots.  python3 exp4b_hole.py hole [kappa]"""
import sys
from harness import *
import mdp

h = int(sys.argv[1])
k = float(sys.argv[2]) if len(sys.argv) > 2 else 1.6
P = D.central(h)
R = raster(h)
base = solve(h, P, keep=True)
S, S2, g = mdp.improved_S(M, h, P, R, k)
r2 = solve(h, P, S=S2, keep=True)
print("table:", short(base), {c: (v["aim"], v["ev"]) for c, v in base["clubs"].items()})
print("MDP  :", short(r2), {c: (v["aim"], v["ev"]) for c, v in r2["clubs"].items()})
ga, gl, Dl = g["ga"], g["gl"], g["delta"]
print("green at", np.round(R.green, 0), "| delta map (x100), rows = yds along, cols = yds right; lie letter + delta")
cols = [j for j, l in enumerate(gl) if -60 <= l <= 60 and l % 10 == 0]
print("      " + "".join("%7d" % gl[j] for j in cols))
for i, a in enumerate(ga):
    if a % 20 or a > 420:
        continue
    row = "%5d " % a
    for j in cols:
        code = int(R.lie_at(np.array([a]), np.array([gl[j]]))[0])
        inf = g["info"].get((i, j))
        row += "%7s" % (M.LIES[code][0] + ("%+.0f" % (100 * Dl[i, j]) if inf else ""))
    print(row)
print("second shot chosen from the centre of each club's finish cloud (carry, lateral offset, value, table value):")
for c in base["order"][:4]:
    raw = r2["raw"][c]
    a0, l0 = float(np.median(raw["a"])), float(np.median(raw["l"]))
    i, j = int(np.argmin(np.abs(ga - a0))), int(np.argmin(np.abs(gl - l0)))
    inf = g["info"].get((i, j))
    print("  %-9s finishes ~(%.0f, %+.0f), %.0f to the hole:" % (c, a0, l0, np.hypot(R.green[0] - a0, R.green[1] - l0)),
          inf and "carry %.0f, offset %+.0f, V2 %.3f, lie %s, delta %+.3f" % (inf[1], inf[2], inf[0], inf[4], Dl[i, j]))
