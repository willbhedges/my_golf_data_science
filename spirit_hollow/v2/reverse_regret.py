"""Reverse check: what v2's plays cost if v1's world (its central settings) were true.

  python3 spirit_hollow/v2/reverse_regret.py   -> spirit_hollow/v2/output/reverse_regret.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decide as D                              # noqa: E402
import model as M                               # noqa: E402


def main():
    v2 = json.load(open(os.path.join(HERE, "output", "v2_decisions.json")))
    out = {}
    tot = 0.0
    for h, r in v2.items():
        k = D.key(h)
        P = M.v1_world()
        clubs = M.clubs_for(k, all_clubs=False)
        R, S, z, cv = D.curves(k, P, 8000, 7, M.ALL_CLUBS)
        best = min(D.robust_aim(D.AIMS, cv[c], -25, 25)["ev"] for c in clubs)        # v1's own search
        mine = float(np.interp(r["aim"], D.AIMS, cv[r["pick"]]))
        out[h] = round(mine - best, 4)
        if h not in ("2B", "9B"):
            tot += mine - best
        print(h, r["pick"], r["aim"], f"{mine - best:+.3f}", flush=True)
    out["black_round_total"] = round(tot, 3)
    json.dump(out, open(os.path.join(HERE, "output", "reverse_regret.json"), "w"), indent=1)
    print("total", round(tot, 3))


if __name__ == "__main__":
    main()
