"""Calibration check: what the model says a Driver does over the 16 tee holes vs published amateur data.

  python3 spirit_hollow/v2/calibrate.py   -> spirit_hollow/v2/output/calibration.json

Driver at its own best aim (central world), per hole: fairway, first cut, penalty (water, OB, lost
in long grass), trouble (penalty + trees + found in long grass), sand. Published 0-5 hcp targets
(research.md): ~49% fairways (Shot Scope, driver), 1-3% tee-shot penalties (Shot Scope) and ~12%
penalty-or-recovery (Arccos scratch-4.9), ~7% of drives > 40 yds from the fairway centre (Stagner).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decide as D                              # noqa: E402
import model as M                               # noqa: E402


def rates(h, P, n=8000, club="Driver"):
    hd = M.HOLES[h]
    R = M.Raster(hd)
    S = R.strokes(P, hd["length"])
    z = M.draws_z(n, 21)
    ev, _ = M.ev_curve(R, S, hd, club, P, z, D.AIMS)
    aim = D.robust_aim(D.AIMS, ev)["aim"]
    _, (a, l, lie, s) = M.ev_curve(R, S, hd, club, P, z, np.array([aim]))
    a, l, lie = a[:, 0], l[:, 0], lie[:, 0]
    nat = lie == M.CODE["native"]
    if P.get("v1_penalties"):
        pl = np.where(nat, P["lost_deep"], 0.0)
    else:
        dep = R.native_depth[R.idx(a, l)]
        pl = np.where(nat, P["lost_edge"] + (P["lost_deep"] - P["lost_edge"]) * np.clip(dep / P["lost_ramp"], 0, 1), 0)
    pen = np.mean((lie == M.CODE["water"]) | (lie == M.CODE["ob"])) + pl.mean()
    trouble = np.mean(np.isin(lie, [M.CODE["water"], M.CODE["ob"], M.CODE["recovery"], M.CODE["native"]]))
    car, dev, roll = M.shots(hd, club, P, z)
    return dict(aim=aim, fairway=float(np.mean(lie == M.CODE["fairway"])),
                first_cut=float(np.mean(lie == M.CODE["first_cut"])), penalty=float(pen),
                trouble=float(trouble), sand=float(np.mean(lie == M.CODE["sand"])),
                beyond40=float(np.mean(np.abs(dev - P["bias"]) > 40)))


def main():
    import geom
    out = {}
    w82 = {c: v * 82 / 70 for c, v in M.central()["width"].items()}
    for name, geo, mk in (("v1 world", "", lambda h: M.v1_world()),
                          ("v2 central", "scale,elev,green", lambda h: D.central(h)),
                          ("v2, width 82", "scale,elev,green", lambda h: D.central(h, width=w82))):
        geom.set_geometry(geo)
        rows = {str(h): rates(h, mk(h)) for h in M.HOLES}
        mean = {k: float(np.mean([r[k] for r in rows.values()])) for k in ("fairway", "first_cut", "penalty",
                                                                            "trouble", "sand", "beyond40")}
        out[name] = dict(holes=rows, mean=mean)
        print(name, {k: round(v, 3) for k, v in mean.items()}, flush=True)
    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "output", "calibration.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
