"""Par-3 club ladder for the page (audit Nov 9 item 1): the expected-strokes-best club as a function of the page's own
"Plays" number, per tee set and par 3, so the page picks the club live from whatever wind / temperature / tee time /
start hole / tee move is set (the club line in par3_targets.json was solved once, for the Nov 7 forecast).

  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par3_ladder.py [--sets Back,...] [--n 6000]

Model: the par-3 agent's (opt/par3_target.py = Eagle Knoll OPTIMIZE.md section 13): Will's iron pattern with
mishits, the truth-map green and surrounds, uniform pins, the DEM. Each club is played at calm 70 F with its stock
carry shifted by -s (o["carry_shift"]), which is the same as the hole playing s yds longer; the lateral aim is
optimised per club (club_eval). The page's calm 70-F number to the box is P0 = card + box depth + dz (par3_targets.py:
play = box.play x plays / card, plays(calm) = (A + dz) card / A, A = card + aim depth); the model's own calm 70-F
carry to the same box (map distance, DEM) is p0 = carry_needed. A live page "Plays" N is read as the carry Will
needs, so the club is the ladder's at s = N - p0 (the card is taken as the truth for the yardage: the page's number
already uses it, and Move this tee changes it). Wind changes the dispersion a little as well as the length; the ladder keeps only the length (the
stated simplification). The map's tee-to-centre distance is stored too (`map_center`): on 4 and 7 the card is 3-5
yds longer than the map.

Writes course_data/courses/gateway_national/par3_ladder.json {set: {hole: {p0, map_center, card, steps:
[[s, pick, runner, margin, se, tie], ...]}}}; read by par3_targets.install (config "par3_ladder").
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(GW, "..", "..", ".."))
OUT = os.path.join(GW, "par3_ladder.json")

os.environ.setdefault("P3_FEATURES", "1")       # the second-pass surrounds, as opt/par3_decade.py (PAR3.md 0.4)
if "--tall-grass" in sys.argv and sys.argv[sys.argv.index("--tall-grass") + 1] == "lost":
    os.environ["P3_TALL_GRASS"] = "lost"      # the page's second rule set (opt/par3_target.py LOST_MODE)
    OUT = os.path.join(GW, "par3_ladder_lost.json")
_spec = importlib.util.spec_from_file_location("gw_par3", os.path.join(HERE, "par3_target.py"))
G = importlib.util.module_from_spec(_spec)
sys.modules["gw_par3"] = G
_spec.loader.exec_module(G)
E = G.E
SHIFTS = np.arange(-30.0, 40.0 + 1e-9, 2.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default=",".join(G.SETS))
    ap.add_argument("--holes", default="4,7,12,14,17")
    ap.add_argument("--n", type=int, default=6000)
    ap.add_argument("--tall-grass", choices=["drop", "lost"], default="drop")
    a = ap.parse_args()
    G.setup_engine()
    T = json.load(open(G.PAGE))["sets"]         # par3_targets.json (par3_targets_lost.json with --tall-grass lost)
    meta = json.load(open(os.path.join(GW, "truth", "meta.json")))
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    cond = dict(temp=70.0, mph=0.0, rel=0.0)
    lats = np.arange(-12.0, 12.0 + 1e-9, 1.0)
    for s in a.sets.split(","):
        holes = G.load_holes(s)
        cards = G.card(s)
        for k in [int(x) for x in a.holes.split(",")]:
            H = E.Hole(holes[k], E.opts())
            dep = float(T[s][str(k)]["boxes"]["-1"]["aim"][1])
            dz = float(meta["holes"][str(k)].get("dz") or 0.0)
            p0 = float(E.carry_needed(H, dep, cond, E.opts()))     # the model's calm 70-F carry to the box (map)
            page0 = cards[k] + dep + dz                               # the page's calm 70-F number (card)
            z = E.draws(a.n, 23)
            steps = []
            for sh in SHIFTS:
                ce = G.club_eval(H, cond, E.opts(carry_shift=-float(sh)), z, lats)
                order = sorted(ce, key=lambda c: ce[c]["ev"])
                b, r = order[0], order[1]
                d, se = E.paired(ce[r]["per"], ce[b]["per"])
                nm = lambda c: E.SHORT_NAME.get(c, c)       # noqa: E731
                steps.append([float(sh), nm(b), nm(r), round(float(d), 4), round(float(se), 4),
                              bool(d < 2 * se or d < 0.01)])
            row = dict(p0=round(p0, 1), page0=round(page0, 1), card=cards[k], map_center=round(float(H.center), 1),
                                                 aim_dep=dep, dz=dz, steps=steps)
            print(s, k, "p0", round(p0, 1), "page0", round(page0, 1), "map", round(float(H.center), 1), "card", cards[k],
                  [(int(x[0]), x[1]) for x in steps[::3]], file=sys.stderr, flush=True)
            import fcntl                      # several sets may run at once: read-update-write under a lock
            with open(OUT + ".lock", "w") as lk:
                fcntl.flock(lk, fcntl.LOCK_EX)
                out = json.load(open(OUT)) if os.path.exists(OUT) else {}
                out.setdefault(s, {})[str(k)] = row
                json.dump(out, open(OUT, "w"), indent=0)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
