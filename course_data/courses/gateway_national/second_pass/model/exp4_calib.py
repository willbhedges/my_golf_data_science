"""Is the engine's amateur table consistent with the engine's own iron pattern?  Featureless hole, fairway lie:
rollout value by distance for a spread multiplier kappa, against the table (am and tour)."""
from harness import *
import mdp

P = M.central(temp_f=70.0)
Pt = M.central(temp_f=70.0, table="tour")
print("d    table_am  table_tour | rollout(am short game) kappa=1.0  1.3  1.6  2.0 | rollout(tour short game) kappa=0.8 1.0")
for d in (80, 100, 120, 150, 180, 200, 220):
    row = [float(M.table("fairway", d, P)), float(M.table("fairway", d, Pt))]
    am = [mdp.flat_value(M, vc, P, d, "fairway", k)[0] for k in (1.0, 1.3, 1.6, 2.0)]
    tr = [mdp.flat_value(M, vc, Pt, d, "fairway", k)[0] for k in (0.8, 1.0)]
    print("%3d  %.3f  %.3f | %s | %s" % (d, row[0], row[1], "  ".join("%.3f" % x for x in am), "  ".join("%.3f" % x for x in tr)))
print("rough:")
for d in (100, 150, 200):
    print(d, "table am %.3f" % float(M.table("rough", d, P)), "rollout kappa 1.0/1.3/1.6:",
          ["%.3f" % mdp.flat_value(M, vc, P, d, "rough", k)[0] for k in (1.0, 1.3, 1.6)])
