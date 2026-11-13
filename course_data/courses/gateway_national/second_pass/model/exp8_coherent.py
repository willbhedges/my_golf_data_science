"""Coherent golfers. The engine's central world pairs a Tour-width pattern (driver 95 % width 70 yds: DECADE's
figure for elite players) with a scratch-to-5 scoring table (Tour + 0.36 + 0.0012 / yd). Both choices favour the
longer club: a narrow pattern makes the Driver safe, the amateur table makes its extra yards worth more. A golfer
is one or the other, so the picks are re-solved for golfers whose pattern and table belong together:
  elite      : width 70, PGA Tour table (a +2 or better; a Tour-width pattern scores like the Tour table: exp4_calib)
  scratch    : width 76, Tour + 0.22, slope 0.0006 / yd (Stagner / Arccos scratch: 3.04 from 100, ~3.17 from 150)
  5 handicap : width 82, Tour + 0.36 + 0.0012 / yd (the engine's table; Arccos 0-5 big-miss rate -> sigma ~21)
python3 exp8_coherent.py out.json [holes]"""
import json, sys, time
from harness import *

out = sys.argv[1]
holes = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else HOLES
C = lambda h, **kw: D.central(h, **kw)                     # noqa: E731
W = lambda h, f: {c: v * f for c, v in C(h)["width"].items()}   # noqa: E731
VARS = {
    "central": lambda h: C(h),
    "elite (70, tour)": lambda h: C(h, table="tour"),
    "scratch (76, +0.22, 0.0006)": lambda h: C(h, width=W(h, 76 / 70), am_off=0.22, am_slope=0.0006, am_tee_off=0.25),
    "5 hcp (82, engine am)": lambda h: C(h, width=W(h, 82 / 70)),
    "scratch table, width 70": lambda h: C(h, am_off=0.22, am_slope=0.0006, am_tee_off=0.25),
    "scratch table, width 82": lambda h: C(h, width=W(h, 82 / 70), am_off=0.22, am_slope=0.0006, am_tee_off=0.25),
}
res = {}
for h in holes:
    res[h] = {}
    for k, f in VARS.items():
        r = solve(h, f(h), n2=32000)
        res[h][k] = r
        print(h, "%-30s" % k, short(r), {c: (v["aim"], v["ev"]) for c, v in list(r["clubs"].items())[:3]},
              "| " + (compare(res[h]["central"], r) if k != "central" else ""), flush=True)
    json.dump({str(a): b for a, b in res.items()}, open(out, "w"), indent=0, default=float)
