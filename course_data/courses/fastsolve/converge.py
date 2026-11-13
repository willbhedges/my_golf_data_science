"""How many swings until the answer stops moving: convergence curves, random vs Sobol swings.

  python3 course_data/courses/fastsolve/converge.py --slug gateway_national --holes 8,10,16,13 --reps 30 --out c.json

Per hole (central world, calm, one temperature), for N in 128 .. 32,768 and for the engine's random swings (mc) and
scrambled Sobol swings, `--reps` independent replications (seeds / scrambles) of the whole decision: every club's EV
curve on the decide aim grid from the same N swings, decide.robust_aim, pick = lowest EV. Against the converged answer
(4 x 262,144 Sobol swings) it reports per N: how often the pick is the converged pick, how often the converged pick's
aim is within 1 yd of the converged aim, the sd of that aim, the sd of the best-minus-runner-up margin (= its
standard error at that N) and the mean sd of the clubs' EVs; and the smallest N meeting (a) pick agreement >= 99 %,
(b) aim within 1 yd in >= 99 %, (c) margin SE < 0.002. With R replications ">= 99 %" means all R agree.
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
LADDER = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", default="gateway_national")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--holes", default="8,10,16,13")
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--temp", type=float, default=50.0)
    ap.add_argument("--out")
    a = ap.parse_args()
    import v2_course as vc
    course, meta, M, D = vc.activate(a.slug, a.which)
    import fast
    F = fast.install(M, D)
    mc = F.slow_draws_z
    clubs = [c for c in M.ALL_CLUBS if c not in M.HYPOTHETICAL]
    aims = D.AIMS
    out = {}
    for h in [D.key(x) for x in a.holes.split(",")]:
        hd = M.HOLES[h]
        R = M.Raster(hd)
        P = M.central(temp_f=a.temp)
        S = R.strokes(P, hd["length"])

        def solve(z):
            cv = {c: M.ev_curve(R, S, hd, c, P, z, aims)[0] for c in clubs}
            ra = {c: D.robust_aim(aims, cv[c]) for c in clubs}
            return cv, ra
        t0 = time.time()
        ref = np.mean([[solve(fast.sobol_draws(262144, 900 + k))[0][c] for c in clubs] for k in range(4)], axis=0)
        rra = {c: D.robust_aim(aims, ref[i]) for i, c in enumerate(clubs)}
        order = sorted(clubs, key=lambda c: rra[c]["ev"])
        best, run = order[0], order[1]
        conv = dict(pick=best, runner=run, aim=rra[best]["aim"], window=rra[best]["window"],
                    margin=rra[run]["ev"] - rra[best]["ev"])
        rows = {}
        for kind, draw in (("mc", mc), ("sobol", fast.sobol_draws)):
            for N in LADDER:
                picks, aims_, margins, evs = [], [], [], []
                for r in range(a.reps):
                    cv, ra = solve(draw(N, 70000 + 1000 * r + N % 997))
                    picks.append(min(clubs, key=lambda c: ra[c]["ev"]))
                    aims_.append(ra[best]["aim"])
                    margins.append(ra[run]["ev"] - ra[best]["ev"])
                    evs.append([ra[c]["ev"] for c in clubs])
                rows[f"{kind}{N}"] = dict(
                    pick_ok=float(np.mean([p == best for p in picks])),
                    aim_ok=float(np.mean(np.abs(np.array(aims_) - conv["aim"]) <= 1.0)),
                    aim_sd=float(np.std(aims_, ddof=1)), aim_bias=float(np.mean(aims_) - conv["aim"]),
                    margin_se=float(np.std(margins, ddof=1)), margin_mean=float(np.mean(margins)),
                    ev_sd=float(np.mean(np.std(evs, axis=0, ddof=1))))
        need = {}
        for kind in ("mc", "sobol"):
            def first(test):
                ok = [N for N in LADDER if all(test(rows[f"{kind}{M2}"]) for M2 in LADDER if M2 >= N)]
                return ok[0] if ok else None
            need[kind] = dict(pick99=first(lambda r: r["pick_ok"] >= 0.99), aim99=first(lambda r: r["aim_ok"] >= 0.99),
                              margin_se_002=first(lambda r: r["margin_se"] < 0.002))
        out[str(h)] = dict(converged=conv, rows=rows, need=need)
        print(f"hole {h}: converged {best} {conv['aim']:+.1f} window {conv['window']} margin {conv['margin']:.4f} over {run} "
              f"({time.time() - t0:.0f}s)")
        print("      N   | mc: pick ok  aim<=1yd  aim sd  margin SE  EV sd | sobol: pick ok  aim<=1yd  aim sd  margin SE  EV sd")
        for N in LADDER:
            m, s = rows[f"mc{N}"], rows[f"sobol{N}"]
            print(f"  {N:6d} |     {m['pick_ok']:5.0%}    {m['aim_ok']:5.0%}   {m['aim_sd']:5.2f}   {m['margin_se']:.4f}   {m['ev_sd']:.4f} |"
                  f"        {s['pick_ok']:5.0%}    {s['aim_ok']:5.0%}   {s['aim_sd']:5.2f}   {s['margin_se']:.4f}   {s['ev_sd']:.4f}")
        print("  N needed (pick >= 99 %, aim within 1 yd >= 99 %, margin SE < 0.002):", json.dumps(need), flush=True)
    if a.out:
        json.dump(dict(args=vars(a), ladder=LADDER, holes=out), open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
