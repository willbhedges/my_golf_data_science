"""ON-DEMAND: one actual condition, every tee shot of a set, on the exact kernel (no precomputed grid, no
interpolation between cells): the refined solve of the wind job (2,500-swing aim curve, then 16,000 fresh common
swings on aim +/-10 yds; v2_course.refined_solver) at THIS temperature, THIS wind speed and THIS direction per hole.

  python3 course_data/courses/fastsolve/ondemand.py --slug gateway_national --which truth --temp 41 \
      --wind 12 --from 200 [--back 0] [--holes 8,9] [--swings sobol] [--json out.json]

--from is the compass direction the wind blows FROM (deg true); each hole's relative direction comes from its
bearing (wind.hole_relative), not rounded to the grid's 30-deg steps. Prints the solve time without the start-up
(imports + map load), which is what a long-lived process or a server would pay per condition.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.dirname(HERE)
for p in (COURSES, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)


def setup(slug, which, back=0.0, swings=None, refine=16000, n1=2500):
    import v2_course as vc
    course, meta, M, D = vc.activate(slug, which)
    import wind_grid as WG
    WG.osm_bearings = lambda: {}
    import wind_grid_v2 as WG2
    import wind as W
    import fast
    if getattr(D, "_aim_limit", None):
        L = float(D._aim_limit)
        WG2.AIMS = np.arange(-(L + 35.0), L + 35.0 + 1e-9, 0.5)
    if back:
        WG.shift_tees(back)
    F = fast.install(M, D, swings=swings)
    WG2.N = n1
    WG2.solve = fast.wind_solve(F, WG2)
    solve = vc.refined_solver(M, D, WG2, refine) if refine else WG2.solve
    z = M.draws_z(WG2.N, 31)
    rasters = {h: M.Raster(hd) for h, hd in M.HOLES.items()}          # the map: once per process
    return dict(M=M, D=D, W=W, WG2=WG2, solve=solve, z=z, rasters=rasters, strokes={})


def condition(E, temp_f, speed, wind_from, holes=None):
    """{hole: the wind-grid cell record} for one temperature / wind."""
    M, W = E["M"], E["W"]
    P = M.central(temp_f=temp_f)
    out = {}
    for h, hd in M.HOLES.items():
        if holes and str(h) not in holes:
            continue
        R = E["rasters"][h]
        S = E["strokes"].get(h)                      # the value raster does not depend on temperature or wind
        if S is None:
            S = E["strokes"][h] = R.strokes(P, hd["length"])
        rel = W.hole_relative(wind_from, (hd.get("elev_info") or {}).get("bearing") or 0.0) if speed else 0.0
        r = E["solve"](h, P, R, S, E["z"], speed, rel)
        r["rel"] = rel
        out[str(h)] = r
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", default="gateway_national")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--temp", type=float, default=50.0)
    ap.add_argument("--wind", type=float, default=0.0, help="mph")
    ap.add_argument("--from", dest="wfrom", type=float, default=0.0, help="deg true the wind blows FROM")
    ap.add_argument("--back", type=float, default=0.0)
    ap.add_argument("--holes", default="")
    ap.add_argument("--swings", choices=["mc", "sobol"], default=None)
    ap.add_argument("--refine", type=int, default=16000)
    ap.add_argument("--n1", type=int, default=2500)
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--json")
    a = ap.parse_args()
    t0 = time.perf_counter()
    E = setup(a.slug, a.which, a.back, a.swings, a.refine, a.n1)
    t1 = time.perf_counter()
    holes = a.holes.split(",") if a.holes else None
    best = None
    for _ in range(max(1, a.repeat)):
        t = time.perf_counter()
        out = condition(E, a.temp, a.wind, a.wfrom, holes)
        dt = time.perf_counter() - t
        best = dt if best is None else min(best, dt)
    print(f"{a.slug} {a.which} tee {a.back:+g}: {a.temp:g} F, wind {a.wind:g} mph from {a.wfrom:g}")
    print("hole  club        aim   window          margin  runner      wind rel")
    for h, r in out.items():
        c = r["clubs"][r["pick"]]
        print(f"{h:>4}  {r['pick']:10s} {c['aim']:+5.1f}  [{c['zone'][0]:+5.1f}, {c['zone'][1]:+5.1f}]  {r['margin']:.4f}  "
              f"{r['runner']:10s}  {r['rel']:5.0f}")
    print(f"solve: {best:.2f} s for {len(out)} tee shots (start-up {t1 - t0:.1f} s: imports, map, rasters)")
    if a.json:
        json.dump(dict(temp=a.temp, wind=a.wind, wind_from=a.wfrom, back=a.back, solve_s=best, holes=out),
                  open(a.json, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
