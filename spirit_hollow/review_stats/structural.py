"""Structural sensitivity at the prior-mean world (no map jitter), every hole, N=6000 fixed swings.

Configs: as-is (decision.py's mean world) | lost ball = stroke & distance (baseline_patch) |
5-hcp baseline | both | both + driver width 84 (research.md sigma ~21) with clubs scaled alike.
python3 spirit_hollow/review_stats/structural.py  -> structural_results.json
"""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(SH, "..", "mozingo"), SH, HERE]

import decision as D            # noqa: E402
import tee_strategy as t        # noqa: E402
import baseline_patch as BP     # noqa: E402

MEAN = dict(width=D.CENTER_WIDTH / 65.0, c_drv=0.0, c_2w=0.0, c_4w=0.0, roll=1.0, trees=0.8,
            lost=0.5, mishit=0.15, map_seed=0)
r = np.random.default_rng(77)
Z = np.vstack([r.standard_normal((2, 6000)), r.random((2, 6000))])
CONFIGS = {
    "as_is": dict(fix=False, hcp=False, W=70),
    "lost=S&D": dict(fix=True, hcp=False, W=70),
    "hcp": dict(fix=False, hcp=True, W=70),
    "lost=S&D+hcp": dict(fix=True, hcp=True, W=70),
    "lost=S&D+hcp+W84": dict(fix=True, hcp=True, W=84),
}


def main():
    out = {}
    for name, cf in CONFIGS.items():
        D.apply(dict(MEAN, width=cf["W"] / 65.0))
        t.HOLES = copy.deepcopy(D.BASE["holes"])
        t.HCP_BASELINE = cf["hcp"]
        if cf["fix"]:
            BP.install()
        try:
            for h in D.BASE["holes"]:
                g = D.ev_grid(h, Z)
                evs = {c: float(ev.min()) for c, (_, ev) in g.items()}
                aim = {c: float(a[int(ev.argmin())]) for c, (a, ev) in g.items()}
                p = min(evs, key=evs.get)
                second = sorted(evs.values())[1]
                out.setdefault(str(h), {})[name] = dict(pick=p, aim=aim[p], gap=second - evs[p], evs=evs)
        finally:
            BP.uninstall()
            t.HCP_BASELINE = False
            D.reset()
        print(name, {h: (v[name]["pick"], round(v[name]["gap"], 3)) for h, v in out.items()}, flush=True)
    with open(os.path.join(HERE, "structural_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\n| Hole | " + " | ".join(CONFIGS) + " |")
    print("|---|" + "---|" * len(CONFIGS))
    for h, v in out.items():
        print(f"| {h} | " + " | ".join(f"{v[c]['pick']} ({v[c]['gap']:.3f})" for c in CONFIGS) + " |")


if __name__ == "__main__":
    main()
