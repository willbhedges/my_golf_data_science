"""Full-size equivalence and seed-noise measurements behind README.md (minutes to hours on the engine side).

  # the engine's own Monte Carlo noise: the refined calm cell re-solved with other swing seeds
  python3 course_data/courses/fastsolve/equiv.py seeds --slug gateway_national --which truth [--engine slow] [--seeds 5]

  # engine vs fastsolve on the same tasks = two runs of run.py and a compare:
  python3 course_data/courses/fastsolve/run.py solve --slug S --out A --only wind --refine 16000 \
      --speeds 0,5,10 --dirs 0,90,180,270 --engine slow
  python3 course_data/courses/fastsolve/run.py solve --slug S --out B --only wind --refine 16000 \
      --speeds 0,5,10 --dirs 0,90,180,270
  python3 course_data/courses/fastsolve/run.py compare --slug S --out B --ref A
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


def seeds(a):
    import v2_course as vc
    course, meta, M, D = vc.activate(a.slug, a.which)
    import wind_grid as WG
    WG.osm_bearings = lambda: {}
    import wind_grid_v2 as WG2
    if getattr(D, "_aim_limit", None):
        L = float(D._aim_limit)
        WG2.AIMS = np.arange(-(L + 35.0), L + 35.0 + 1e-9, 0.5)
    WG2.N = 2500
    if a.engine == "fast":
        import fast
        fast.install(M, D)
    holes = [h for h in M.HOLES if not a.holes or str(h) in a.holes.split(",")]
    rows = {}
    t0 = time.time()
    for h in holes:
        hd = M.HOLES[h]
        R = M.Raster(hd)
        P = M.central(temp_f=a.temp)
        S = R.strokes(P, hd["length"])
        res = []
        for k in range(a.seeds):
            solve = vc.refined_solver(M, D, WG2, a.refine, seed=vc.REFINE_SEED + 100 * k)   # wraps the original solve
            res.append(solve(h, P, R, S, M.draws_z(WG2.N, 31 + 100 * k), a.speed, a.rel))
        clubs = [c for c in res[0]["clubs"] if c not in M.HYPOTHETICAL]
        pick0 = res[0]["pick"]
        rows[str(h)] = dict(
            picks=[r["pick"] for r in res], margin=[round(r["margin"], 4) for r in res],
            aim_sd={c: float(np.std([r["clubs"][c]["aim"] for r in res], ddof=1)) for c in clubs},
            aim_range={c: float(np.ptp([r["clubs"][c]["aim"] for r in res])) for c in clubs},
            ev_sd={c: float(np.std([r["clubs"][c]["ev"] for r in res], ddof=1)) for c in clubs},
            pick_aims=[r["clubs"][pick0]["aim"] for r in res])
        r = rows[str(h)]
        print(f"hole {h}: picks {r['picks']} margins {r['margin']} | {pick0} aims {r['pick_aims']} | "
              f"EV sd: " + ", ".join(f"{c} {r['ev_sd'][c]:.4f}" for c in clubs[:4]), flush=True)
    ev_sd = [v for r in rows.values() for v in r["ev_sd"].values()]
    aim_rng = [v for r in rows.values() for v in r["aim_range"].values()]
    pick_rng = [float(np.ptp(r["pick_aims"])) for r in rows.values()]
    summ = dict(seeds=a.seeds, refine=a.refine, temp=a.temp, speed=a.speed, rel=a.rel, engine=a.engine,
                ev_sd_median=float(np.median(ev_sd)), ev_sd_max=float(np.max(ev_sd)),
                aim_range_median=float(np.median(aim_rng)), aim_range_max=float(np.max(aim_rng)),
                pick_aim_range_median=float(np.median(pick_rng)), pick_aim_range_max=float(np.max(pick_rng)),
                holes_pick_flips=[h for h, r in rows.items() if len(set(r["picks"])) > 1],
                secs=round(time.time() - t0, 1))
    print(json.dumps(summ, indent=1))
    if a.out:
        json.dump(dict(summary=summ, holes=rows), open(a.out, "w"), indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["seeds"])
    ap.add_argument("--slug", required=True)
    ap.add_argument("--which", default="truth")
    ap.add_argument("--engine", choices=["slow", "fast"], default="slow")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--refine", type=int, default=16000)
    ap.add_argument("--temp", type=float, default=50.0)
    ap.add_argument("--speed", type=int, default=0)
    ap.add_argument("--rel", type=int, default=0)
    ap.add_argument("--holes", default="")
    ap.add_argument("--out")
    a = ap.parse_args()
    seeds(a)


if __name__ == "__main__":
    main()
