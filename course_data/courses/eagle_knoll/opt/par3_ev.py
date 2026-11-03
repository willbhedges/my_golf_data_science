"""Eagle Knoll par 3s: the page's DECADE target (yardage_book.par3_plan, floored as on the page) against the
expected-strokes-optimal aim for Will's iron pattern (OPTIMIZE.md section 5).

  python3 course_data/courses/eagle_knoll/opt/par3_ev.py [--n 4000] > par3_ev.json

Model (spirit_hollow/approach/shots.py numbers, copied: that module imports Spirit Hollow's map):
  * dispersion: lateral sigma 9.4 yds at 150 (6-7 % of the distance; 5-handicap proximity anchors), depth sigma
    1.5 x lateral; 2 yds of release; no mishits (irons <= 200 yds)
  * pins: 16 uniform points on the green, 4 yds inside the edge (pin positions unknown)
  * strokes after the shot: Broadie putting by feet (+0.06, 5-handicap), short game 2-40 yds by lie (+0.15), sand,
    trees as the recovery row; water = 1 + rough from 15 yds (drop near where it went in); OB = 1 + 3.1 (replay)
  * zones: the hand-checked truth package (the page's map), lies within 40 yds of the green
"""
import argparse
import json
import os
import sys

import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ROOT = os.path.dirname(CD)
sys.path[:0] = [os.path.join(CD, "courses"), os.path.join(ROOT, "mozingo")]

SIG_D = np.array([30, 50, 75, 100, 125, 150, 175, 200, 225], float)
SIG_LAT = np.array([3.5, 4.5, 5.8, 7.0, 8.2, 9.4, 11.2, 13.4, 15.8])
PUTT_FT = np.array([1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 90], float)
PUTTS = np.array([1.00, 1.01, 1.04, 1.13, 1.23, 1.34, 1.50, 1.61, 1.78, 1.87, 1.98, 2.06, 2.14, 2.21, 2.40]) + 0.06
SHORT_D = np.array([2, 5, 10, 15, 20, 30, 40], float)
SHORT = {k: np.array(v) + 0.15 for k, v in {
    "rough": [2.10, 2.20, 2.34, 2.47, 2.59, 2.70, 2.78], "fairway": [1.95, 2.05, 2.18, 2.30, 2.40, 2.52, 2.60],
    "sand": [2.30, 2.37, 2.43, 2.48, 2.53, 2.66, 2.82], "recovery": [3.00, 3.10, 3.20, 3.30, 3.40, 3.48, 3.55],
    "native": [2.70, 2.80, 2.90, 3.00, 3.10, 3.20, 3.30]}.items()}
RELEASE = 2.0
DEPTH_RATIO = 1.5            # depth sigma / lateral sigma (Broadie amateur patterns); --depth-ratio for sensitivity


def frame_zones(which):
    """Per par 3: green outline, zones and the DECADE plan in the page's green frame (yds right, yds past centre)."""
    import v2_course as vc
    cfg = vc.config("eagle_knoll")
    PK = vc.product_pk()
    import yardage_book as yb
    got = {}
    orig = PK._par3

    def cap(fr, green_ll, gpoly, zones, length, k):
        p = orig(fr, green_ll, gpoly, zones, length, k)
        tee = np.array(PK.TEE_PX)
        flag = fr.ll_to_px([green_ll])[0]
        v = (flag - tee) / np.linalg.norm(flag - tee)
        right = np.array([-v[1], v[0]])
        zz = []
        for lie, poly in zones:
            q = (np.asarray(poly, float) - flag) / PK.PPY
            zz.append((lie, np.c_[q @ right, q @ v]))
        got[k] = dict(p=p, zones=zz)
        return p
    PK._par3 = cap
    PK.load(os.path.join(ROOT, cfg["truth_package"]), vc.base_tees(cfg, which))
    PK._par3 = orig
    plan = vc.floored_plan(yb.par3_plan)
    for k, g in got.items():
        yb.WIND_NOW = 0
        g["plan"] = plan(g["p"])
    return got


def ev_grid(g, n=4000, seed=5, span=12, step=1.0):
    p = g["p"]
    green = Path(np.array(p["green"], float))
    gp = np.array(p["green"], float)
    r = np.random.default_rng(seed)
    zl, zd = r.standard_normal(n), r.standard_normal(n)
    # pins: 4 yds inside the edge
    lo, hi = gp.min(0), gp.max(0)
    cand = np.c_[r.uniform(lo[0], hi[0], 4000), r.uniform(lo[1], hi[1], 4000)]
    inner = Path(np.array(p["green"], float))
    ok = inner.contains_points(cand)
    from scipy.spatial import cKDTree
    edge = cKDTree(np.r_[[gp[i] + (gp[(i + 1) % len(gp)] - gp[i]) * t for i in range(len(gp)) for t in np.linspace(0, 1, 6)]])
    ok &= edge.query(cand)[0] >= 4.0
    pins = cand[ok][:16]
    aims = [(a, d) for a in np.arange(-span, span + 1e-9, step) for d in np.arange(-span, span + 1e-9, step)]
    out = {}
    for (al, ad) in aims:
        dist = p["center"] + ad
        sl = float(np.interp(dist, SIG_D, SIG_LAT))
        x = al + sl * zl
        y = ad + DEPTH_RATIO * sl * zd + RELEASE
        pts = np.c_[x, y]
        lie = np.array(["rough"] * n, dtype=object)
        for name, poly in g["zones"]:
            if name in ("fairway", "first_cut"):
                name = "fairway"
            lie[Path(poly).contains_points(pts)] = name
        on = green.contains_points(pts)
        tot = np.zeros(n)
        for pin in pins:
            dyd = np.hypot(x - pin[0], y - pin[1])
            s = np.where(on, np.interp(dyd * 3, PUTT_FT, PUTTS), 0.0)
            for name in ("rough", "fairway", "sand", "recovery", "native"):
                m = ~on & (lie == name)
                s[m] = np.interp(dyd[m], SHORT_D, SHORT[name]) + np.maximum(dyd[m] - 40, 0) * 0.01
            m = ~on & (lie == "water")
            s[m] = 1.0 + np.interp(15, SHORT_D, SHORT["rough"])
            m = ~on & (lie == "ob")
            s[m] = 1.0 + 3.1
            tot += s
        out[(al, ad)] = dict(ev=1.0 + float(tot.mean() / len(pins)), green=float(on.mean()),
                             water=float(np.mean(~on & (lie == "water"))))
    return out, pins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--depth-ratio", type=float, default=1.5)
    ap.add_argument("--tree-cost", type=float, default=1.0, help="x the recovery row's excess over rough")
    ap.add_argument("--sets", default="Back,Eagle,Middle")
    a = ap.parse_args()
    global DEPTH_RATIO
    DEPTH_RATIO = a.depth_ratio
    SHORT["recovery"] = SHORT["rough"] + a.tree_cost * (SHORT["recovery"] - SHORT["rough"])
    res = {}
    for which, s in (("truth", "Back"), ("truth_eagle", "Eagle"), ("truth_middle", "Middle")):
        if s not in a.sets.split(","):
            continue
        for k, g in sorted(frame_zones(which).items()):
            grid, pins = ev_grid(g, a.n)
            best = min(grid, key=lambda q: grid[q]["ev"])
            pl = g["plan"]
            box = (round(pl["aim"][0]), round(pl["aim"][1]))
            box = min(grid, key=lambda q: abs(q[0] - pl["aim"][0]) + abs(q[1] - pl["aim"][1]))
            cen = (0.0, 0.0)
            res[f"{s} {k}"] = dict(card=g["p"]["center"], haz=g["p"]["haz"], decade_aim=[round(x, 1) for x in pl["aim"]],
                                   decade_box=dict(lat=[round(x, 1) for x in pl["lat"]], dep=[round(x, 1) for x in pl["dep"]]),
                                   ev_decade=round(grid[box]["ev"], 4), ev_centre=round(grid[cen]["ev"], 4),
                                   best_aim=list(best), ev_best=round(grid[best]["ev"], 4),
                                   decade_cost=round(grid[box]["ev"] - grid[best]["ev"], 4),
                                   green_decade=round(grid[box]["green"], 3), water_decade=round(grid[box]["water"], 3),
                                   green_best=round(grid[best]["green"], 3), water_best=round(grid[best]["water"], 3))
            print(s, k, json.dumps(res[f"{s} {k}"], default=float), file=sys.stderr, flush=True)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
