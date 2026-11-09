"""Wind +/-5 mph sensitivity of each tee shot from the page's own wind grid (card tee, the hole's forecast-nearest
grid temperature): the calm pick vs the pick in every 5-mph cell (12 directions) and at 10 mph.

  python3 course_data/courses/eagle_knoll/opt/wind_sens.py [which] [temp]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
which = sys.argv[1] if len(sys.argv) > 1 else "truth"
T = sys.argv[2] if len(sys.argv) > 2 else "50"
g = json.load(open(os.path.join(os.path.dirname(HERE), which, "v2", "wind_grid.json")))
REL = {0: "into", 30: "into-R>L", 60: "R>L-into", 90: "R>L", 120: "R>L-help", 150: "help-R>L", 180: "helping",
       210: "help-L>R", 240: "L>R-help", 270: "L>R", 300: "L>R-into", 330: "into-L>R"}
real = lambda cl: sorted([c for c in cl if "not in bag" not in c], key=lambda c: cl[c]["ev"])
out = {}
for h, byT in g["holes"].items():
    cells = byT[T]
    c0 = cells["0_0"]; o0 = real(c0["clubs"]); p0 = o0[0]
    row = dict(calm=p0, calm_margin=round(c0["clubs"][o0[1]]["ev"] - c0["clubs"][p0]["ev"], 4), flips5=[], flips10=[])
    for sp in (5, 10):
        for rel in range(0, 360, 30):
            c = cells[f"{sp}_{rel}"]; o = real(c["clubs"])
            if o[0] != p0:
                row[f"flips{sp}"].append(f"{REL[rel]} -> {o[0]} ({c['clubs'][o[1]]['ev'] - c['clubs'][o[0]]['ev']:.3f})")
    out[h] = row
    print(h, p0, row["calm_margin"], "| 5 mph:", "; ".join(row["flips5"]) or "same", "| 10 mph:", len(row["flips10"]), "of 12 dirs differ")
json.dump(out, open(os.path.join(HERE, f"wind_sens_{which}_{T}.json"), "w"), indent=1)
