"""Seed noise of the aim / EV / pick, and lower-variance swing sets, measured against a long reference run.

  python3 course_data/courses/fastsolve/noise.py --slug gateway_national --which truth [--holes 10,9] [--seeds 12]
      [--temp 50] [--speed 0 --rel 0] [--ref 1000000] --out noise.json

For each hole, at one world (central, one temperature, one wind cell) and for every club:
  reference  the EV curve on the decide aim grid from --ref pseudo-random swings (kernel; SE ~ 0.0005 strokes)
  estimators (each re-run with --seeds different seeds, the whole aim curve from the same N swings, then
              decide.robust_aim exactly as the engine):
      mc2500 / mc16k   the engine's swings (model.draws_z, numpy default_rng): today's coarse / refine stage
      sobol512 .. sobol16k   scrambled Sobol points (5-D: lateral, carry, mishit, mishit carry, roll)
      anti16k    antithetic pairs (z -> -z, u -> 1 - u), N = 16,000
      mc64k / mc256k   the engine's swings, 4x / 16x as many
  reported   SD over seeds of each club's aim and EV, the RMS error of the EV against the reference, how often the
             pick differs from the reference pick, and the REGRET: reference EV at the estimator's (club, aim) minus
             the reference optimum, i.e. what the noise costs in strokes.
Nothing here changes the engine; `fast.install(M, D, swings="sobol")` is the opt-in flag (run.py --swings sobol).
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
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", default="gateway_national")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--holes", default="")
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--temp", type=float, default=50.0)
    ap.add_argument("--speed", type=int, default=0)
    ap.add_argument("--rel", type=int, default=0)
    ap.add_argument("--ref", type=int, default=1000000)
    ap.add_argument("--est", default="", help="estimators to run (default all)")
    ap.add_argument("--out")
    a = ap.parse_args()
    import v2_course as vc
    course, meta, M, D = vc.activate(a.slug, a.which)
    import wind_grid as WG
    WG.osm_bearings = lambda: {}
    import wind_grid_v2 as WG2
    import fast
    F = fast.install(M, D)
    mc = F.slow_draws_z
    EST = {
        "mc2500": lambda s: mc(2500, 5000 + s),                     # today's coarse stage
        "mc16k": lambda s: mc(16000, 5000 + s),                     # today's refine stage
        "sobol512": lambda s: fast.sobol_draws(512, 5000 + s),
        "sobol1024": lambda s: fast.sobol_draws(1024, 5000 + s),
        "sobol2048": lambda s: fast.sobol_draws(2048, 5000 + s),
        "sobol4096": lambda s: fast.sobol_draws(4096, 5000 + s),
        "sobol16k": lambda s: fast.sobol_draws(16384, 5000 + s),
        "anti16k": lambda s: fast.antithetic_draws(16000, 5000 + s),
        "mc64k": lambda s: mc(64000, 5000 + s),
        "mc256k": lambda s: mc(256000, 5000 + s),
    }
    if a.est:
        EST = {k: v for k, v in EST.items() if k in a.est.split(",")}
    holes = [h for h in M.HOLES if not a.holes or str(h) in a.holes.split(",")]
    clubs = [c for c in M.ALL_CLUBS if c not in M.HYPOTHETICAL]
    out = {}
    t0 = time.time()
    for h in holes:
        hd = M.HOLES[h]
        R = M.Raster(hd)
        P = M.central(temp_f=a.temp)
        S = R.strokes(P, hd["length"])
        hooks = {c: (WG2.wind_hook(c, a.speed, a.rel) if a.speed else None) for c in clubs}
        drift = {c: (hooks[c](*M.club_numbers(hd, c, P))[4] if hooks[c] else 0.0) for c in clubs}
        lim = {c: (-D.AIM_LIMIT - drift[c], D.AIM_LIMIT - drift[c]) for c in clubs}
        aims = {c: np.arange(np.floor(lim[c][0]) - 20.0, np.ceil(lim[c][1]) + 20.0 + 1e-9, 0.5) for c in clubs}

        def solve(z):
            r = {}
            for c in clubs:
                ev, _ = M.ev_curve(R, S, hd, c, P, z, aims[c], wind=hooks[c])
                r[c] = (D.robust_aim(aims[c], ev, lo=lim[c][0], hi=lim[c][1]), ev)
            return r
        ref = solve(mc(a.ref, 424242))
        ref_curve = {c: ref[c][1] for c in clubs}
        ref_ev = {c: ref[c][0]["ev"] for c in clubs}
        ref_pick = min(clubs, key=lambda c: ref_ev[c])
        rows = {}
        for name, draw in EST.items():
            res = [solve(draw(s)) for s in range(a.seeds)]
            picks = [min(clubs, key=lambda c: r[c][0]["ev"]) for r in res]
            pick_aims = [r[ref_pick][0]["aim"] for r in res]
            regret = [float(np.interp(r[p][0]["aim"], aims[p], ref_curve[p]) - ref_ev[ref_pick]) for r, p in zip(res, picks)]
            rows[name] = dict(
                aim_sd=float(np.std(pick_aims, ddof=1)), aim_min=min(pick_aims), aim_max=max(pick_aims),
                ev_sd=float(np.std([r[ref_pick][0]["ev"] for r in res], ddof=1)),
                ev_rmse=float(np.sqrt(np.mean([(r[ref_pick][0]["ev"] - float(np.interp(r[ref_pick][0]["aim"], aims[ref_pick], ref_curve[ref_pick]))) ** 2 for r in res]))),
                curve_rmse=float(np.sqrt(np.mean([np.mean((r[ref_pick][1] - ref_curve[ref_pick]) ** 2) for r in res]))),
                margin_sd=float(np.std([sorted(r[c][0]["ev"] for c in clubs)[1] - sorted(r[c][0]["ev"] for c in clubs)[0] for r in res], ddof=1)),
                pick_differs=float(np.mean([p != ref_pick for p in picks])),
                regret_mean=float(np.mean(regret)), regret_max=float(np.max(regret)), aims=pick_aims)
        ro = sorted(ref_ev[c] for c in clubs)
        out[str(h)] = dict(ref_pick=ref_pick, ref_aim=ref[ref_pick][0]["aim"], ref_window=ref[ref_pick][0]["window"],
                           ref_margin=ro[1] - ro[0], est=rows)
        print(f"hole {h}: reference {ref_pick} aim {ref[ref_pick][0]['aim']:+.1f} window {ref[ref_pick][0]['window']} "
              f"margin {ro[1] - ro[0]:.4f}", flush=True)
        for name, r in rows.items():
            print(f"   {name:9s} aim sd {r['aim_sd']:.2f} [{r['aim_min']:+.1f}..{r['aim_max']:+.1f}]  EV sd {r['ev_sd']:.5f}  "
                  f"curve rmse {r['curve_rmse']:.5f}  margin sd {r['margin_sd']:.5f}  pick differs {r['pick_differs']:.0%}  "
                  f"regret {r['regret_mean']:.5f} (max {r['regret_max']:.5f})", flush=True)
    summ = {}
    for name in EST:
        g = lambda k, f=np.mean: float(f([out[h]["est"][name][k] for h in out]))      # noqa: E731
        summ[name] = dict(aim_sd_mean=g("aim_sd"), aim_sd_max=g("aim_sd", np.max), ev_sd_mean=g("ev_sd"),
                          curve_rmse_mean=g("curve_rmse"), margin_sd_mean=g("margin_sd"),
                          pick_differs_mean=g("pick_differs"), regret_mean=g("regret_mean"), regret_max=g("regret_max", np.max))
    print(json.dumps(summ, indent=1))
    print(f"{time.time() - t0:.0f}s")
    if a.out:
        json.dump(dict(args=vars(a), summary=summ, holes=out), open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
