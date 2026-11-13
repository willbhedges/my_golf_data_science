"""The speed-ups that were tried and NOT adopted, reproducible (README.md "Evaluated and rejected").

  python3 course_data/courses/fastsolve/experiments.py conv     [--holes 8,10,16,1]
      the aim sweep as a convolution: (1) finishes computed once at aim 0 and shifted sideways; (2) a landing-value
      raster (roll-out from the landing cell centre, roll rounded to 1 yd) gathered at swing offsets
  python3 course_data/courses/fastsolve/experiments.py fastmath [--holes 8,10,16,1]
      kernel.c built with -Ofast -ffp-contract=fast against the exact build: time, and EV / aim / pick differences
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.dirname(HERE)
for p in (COURSES, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)


def _engine(a):
    import v2_course as vc
    course, meta, M, D = vc.activate(a.slug, a.which)
    import fast
    fast.THREADS = 1
    return M, D, fast.install(M, D), fast


def conv(a):
    M, D, F, fast = _engine(a)
    aims = D.AIMS
    inside = np.abs(aims) <= D.AIM_LIMIT
    worst = dict(shift=0.0, lvr=0.0, shift_aim=0.0, lvr_aim=0.0)
    for h in [D.key(x) for x in a.holes.split(",")]:
        hd = M.HOLES[h]
        R = M.Raster(hd)
        P = M.central(temp_f=50.0)
        S = R.strokes(P, hd["length"])
        z = M.draws_z(16000, 32)
        for c in ("Driver", "2-wood", "Long iron"):
            ev, _ = M.ev_curve(R, S, hd, c, P, z, aims)
            car, dev, roll = M.shots(hd, c, P, z)
            _, (a0, l0, _, _) = M.ev_curve(R, S, hd, c, P, z, np.array([0.0]))
            a0, l0 = np.asarray(a0)[:, 0], np.asarray(l0)[:, 0]
            ev1 = np.array([1 + S[R.idx(a0, l0 + x)].mean() for x in aims])
            ia, il = R.idx(car[:, None], dev[:, None] + aims[None, :])
            ca, cl = R.a[ia], R.l[il]
            fa, fl, _ = F.slow_finish(R, ca, cl, np.broadcast_to(np.round(roll)[:, None], ca.shape), P["rough_roll"])
            ev2 = 1 + S[R.idx(fa, fl)].mean(0)
            r0, r1, r2 = D.robust_aim(aims, ev), D.robust_aim(aims, ev1), D.robust_aim(aims, ev2)
            d1, d2 = float(np.abs(ev1 - ev)[inside].max()), float(np.abs(ev2 - ev)[inside].max())
            worst = dict(shift=max(worst["shift"], d1), lvr=max(worst["lvr"], d2),
                         shift_aim=max(worst["shift_aim"], abs(r1["aim"] - r0["aim"])),
                         lvr_aim=max(worst["lvr_aim"], abs(r2["aim"] - r0["aim"])))
            print(f"hole {h} {c:9s} exact aim {r0['aim']:+.1f} | shifted finishes: max |dEV| {d1:.4f}, aim {r1['aim']:+.1f} | "
                  f"landing-value raster: max |dEV| {d2:.4f}, aim {r2['aim']:+.1f}", flush=True)
    print(json.dumps(worst))


def _curves(a):
    M, D, F, fast = _engine(a)
    aims = D.AIMS
    out, t = {}, 0.0
    for h in [D.key(x) for x in a.holes.split(",")]:
        hd = M.HOLES[h]
        R = M.Raster(hd)
        P = M.central(temp_f=50.0)
        S = R.strokes(P, hd["length"])
        z = M.draws_z(16000, 32)
        for c in M.ALL_CLUBS:
            t0 = time.perf_counter()
            ev, _ = M.ev_curve(R, S, hd, c, P, z, aims)
            t += time.perf_counter() - t0
            out[f"{h}|{c}"] = dict(ev=[float(x) for x in ev], aim=D.robust_aim(aims, ev)["aim"])
    json.dump(dict(secs=t, curves=out), sys.stdout)


def fastmath(a):
    res = {}
    for name, flags in (("exact", ""), ("fastmath", "-Ofast -ffp-contract=fast")):
        env = dict(os.environ, FASTSOLVE_CFLAGS=flags) if flags else {k: v for k, v in os.environ.items() if k != "FASTSOLVE_CFLAGS"}
        best = None
        for _ in range(3):
            r = json.loads(subprocess.run([sys.executable, os.path.abspath(__file__), "_curves", "--holes", a.holes,
                                           "--slug", a.slug, "--which", a.which], env=env, capture_output=True,
                                          text=True, check=True).stdout.splitlines()[-1])
            best = r if best is None or r["secs"] < best["secs"] else best
        res[name] = best
    e, f = res["exact"]["curves"], res["fastmath"]["curves"]
    dev = max(float(np.abs(np.array(e[k]["ev"]) - np.array(f[k]["ev"])).max()) for k in e)
    nbit = sum(e[k]["ev"] != f[k]["ev"] for k in e)
    daim = max(abs(e[k]["aim"] - f[k]["aim"]) for k in e)
    print(f"kernel time (1 thread, {len(e)} curves): exact {res['exact']['secs']:.3f}s, fast-math {res['fastmath']['secs']:.3f}s "
          f"(x{res['exact']['secs'] / res['fastmath']['secs']:.2f}); curves not bit-identical: {nbit} of {len(e)}; "
          f"max |dEV| {dev:.2e}; max aim change {daim:g} yd")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["conv", "fastmath", "_curves"])
    ap.add_argument("--slug", default="gateway_national")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--holes", default="8,10,16,1")
    a = ap.parse_args()
    {"conv": conv, "fastmath": fastmath, "_curves": _curves}[a.cmd](a)


if __name__ == "__main__":
    main()
