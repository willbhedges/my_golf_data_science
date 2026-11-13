"""Wall-time benchmark, engine vs fastsolve, one course (README.md section "Benchmarks").

  python3 course_data/courses/fastsolve/bench.py --slug gateway_national --which truth --hole 8 [--out bench.json]

Everything is measured in ONE process on ONE core unless stated (the Actions jobs run one engine process per core, so
per-core time is the fair unit); the kernel's OpenMP threads are reported separately. The engine side is measured on
slices and extrapolated by counts (cells, draws, worlds): running it in full takes hours.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="gateway_national")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--hole", default="8")
    ap.add_argument("--request")
    ap.add_argument("--slow-cells", type=int, default=6, help="engine: refined wind cells measured")
    ap.add_argument("--slow-draws", type=int, default=3, help="engine: prior draws measured")
    ap.add_argument("--skip-slow-worlds", action="store_true", help="engine: do not time a 12,000-swing central world")
    ap.add_argument("--out")
    a = ap.parse_args()
    import v2_course as vc
    course, meta, M, D = vc.activate(a.slug, a.which)
    import wind_grid as WG
    WG.osm_bearings = lambda: {}
    import wind_grid_v2 as WG2
    if getattr(D, "_aim_limit", None):
        L = float(D._aim_limit)
        WG2.AIMS = np.arange(-(L + 35.0), L + 35.0 + 1e-9, 0.5)
    WG2.N = 2500
    import fast
    h = D.key(a.hole)
    hd = M.HOLES[h]
    q = json.load(open(a.request)) if a.request else {}
    offsets = q.get("offsets", [0])
    r_off = q.get("refine_offsets", [0])
    temps = q.get("temps", json.load(open(os.path.join(COURSES, a.slug, "config.json")))["temps"])
    draws = int(q.get("draws", 256))
    n_holes = len(M.HOLES)
    cells = [(sp, rel) for sp in WG2.SPEEDS for rel in ([0] if sp == 0 else WG2.DIRS)]
    per_T = len(cells)
    res = dict(slug=a.slug, which=a.which, hole=str(h), cpus=os.cpu_count(), n_holes=n_holes, cells_per_hole=per_T * len(temps),
               offsets=len(offsets), refined_offsets=len([b for b in offsets if b in r_off]), draws=draws)
    sample = [cells[i] for i in np.linspace(0, per_T - 1, a.slow_cells).round().astype(int)]
    z = M.draws_z(WG2.N, 31)

    def wind(cs, refined=True):
        solve = vc.refined_solver(M, D, WG2, 16000) if refined else WG2.solve
        R = M.Raster(hd)
        P = M.central(temp_f=50.0)
        S = R.strokes(P, hd["length"])
        t = time.perf_counter()
        out = [solve(h, P, R, S, z, sp, rel) for sp, rel in cs]
        return (time.perf_counter() - t) / len(cs), out

    def book_bayes(n):
        t = time.perf_counter()
        D.bayes(h, n, 3000)
        return (time.perf_counter() - t) / n

    def book_world(n=12000):
        t = time.perf_counter()
        D.solve_world(h, D.central(h), n)
        return time.perf_counter() - t

    # ---------------- engine (slices)
    e_ref, o_ref = wind(sample)
    e_coarse, _ = wind(sample[:3], refined=False)
    e_draw = book_bayes(a.slow_draws)
    e_world = None if a.skip_slow_worlds else book_world()
    res["engine"] = dict(refined_cell_s=e_ref, coarse_cell_s=e_coarse, bayes_draw_s=e_draw, world_12000_s=e_world)
    print("engine  : refined cell %.3fs, coarse cell %.3fs, prior draw %.3fs, 12,000-swing world %s"
          % (e_ref, e_coarse, e_draw, "%.2fs" % e_world if e_world else "-"), flush=True)
    # ---------------- fastsolve
    F = fast.install(M, D)
    res["simd"], res["hypot_inline"] = bool(fast.lib().simd), bool(fast.lib().hypot_inline)
    for nt in (1, os.cpu_count()):
        fast.THREADS = nt
        f_ref, o2 = wind(sample)
        assert json.dumps(o_ref, sort_keys=True, default=float) == json.dumps(o2, sort_keys=True, default=float), \
            "fastsolve differs from the engine"
        t = time.perf_counter()
        f_grid_T, _ = wind(cells)                              # one temperature of the full refined grid, for real
        grid_s = (time.perf_counter() - t) * len(temps)
        f_coarse, _ = wind(cells, refined=False)
        f_draw = book_bayes(16)
        f_world = book_world()
        res[f"fast_{nt}thr"] = dict(refined_cell_s=f_ref, refined_cell_grid_avg_s=f_grid_T, coarse_cell_s=f_coarse,
                                   bayes_draw_s=f_draw, world_12000_s=f_world, hole_grid_s=grid_s)
        print("fast %dthr: refined cell %.4fs (x%.1f), whole-grid average %.4fs, coarse %.4fs (x%.1f), prior draw %.4fs "
              "(x%.1f), world %.3fs%s; one hole's refined grid (%d cells) %.1fs vs engine ~%.0fs (extrapolated)"
              % (nt, f_ref, e_ref / f_ref, f_grid_T, f_coarse, e_coarse / f_coarse, f_draw, e_draw / f_draw, f_world,
                 " (x%.1f)" % (e_world / f_world) if e_world else "", per_T * len(temps), grid_s,
                 e_ref * per_T * len(temps)), flush=True)
    # ---------------- whole solve, CPU-seconds on one core (engine extrapolated by counts)
    n_ref = res["refined_offsets"] * n_holes * per_T * len(temps)
    n_coarse = (len(offsets) - res["refined_offsets"]) * n_holes * per_T * len(temps)
    worlds = len(D.LADDER) + 15 + 8 * 0.5                      # ladder + sensitivities (12,000) + width sweep (6,000)
    f1 = res["fast_1thr"]
    tot_e = n_ref * e_ref + n_coarse * e_coarse + n_holes * (draws * e_draw + (worlds * e_world if e_world else 0))
    tot_f = n_ref * f1["refined_cell_grid_avg_s"] + n_coarse * f1["coarse_cell_s"] + n_holes * (draws * f1["bayes_draw_s"] + worlds * f1["world_12000_s"])
    res["whole_solve_cpu_s"] = dict(engine_extrapolated=tot_e, fast_extrapolated=tot_f, refined_cells=n_ref,
                                    coarse_cells=n_coarse, bayes_draws=n_holes * draws, central_worlds=n_holes * worlds)
    print("whole solve (%d refined + %d coarse cells, %d prior draws, %.0f central worlds), one core: engine ~%.1f h, "
          "fastsolve ~%.1f min (x%.1f) [from this hole's rates; run.py gives the real fastsolve wall time]"
          % (n_ref, n_coarse, n_holes * draws, n_holes * worlds, tot_e / 3600, tot_f / 60, tot_e / tot_f))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
