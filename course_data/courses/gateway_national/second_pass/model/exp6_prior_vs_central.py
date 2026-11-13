"""One central pattern vs the prior average over 'what-if golfers' (decide.bayes): same club? same aim?
python3 exp6_prior_vs_central.py out.json holes [draws]"""
import json, sys, time
from harness import *

out = sys.argv[1]
holes = [int(x) for x in sys.argv[2].split(",")]
S = int(sys.argv[3]) if len(sys.argv) > 3 else 64
res = {}
for h in holes:
    t0 = time.time()
    c = solve(h)
    b = D.bayes(h, S, 3000)
    # the central pick scored in the prior-average world and vice versa
    bc = b["clubs"]
    res[h] = dict(central=c, bayes={k: b[k] for k in ("pick", "runner", "aim", "window", "margin", "margin_se",
                                                       "crossfit_margin", "p_pick_beats_runner", "swing_noise_share",
                                                       "per_draw_aim_sd")},
                  bayes_clubs={k: dict(aim=v["aim"], ev=v["ev"], window=v["window"]) for k, v in bc.items()})
    print(h, "central:", short(c), "| prior average (%d draws): %s %+.1f m=%.3f+/-%.3f vs %s, cf %.3f, p %.2f, swing-noise share %.2f | ev by club (prior avg) %s  %.0fs" % (
        S, b["pick"], b["aim"], b["margin"], b["margin_se"], b["runner"], b["crossfit_margin"], b["p_pick_beats_runner"],
        b["swing_noise_share"] or 0, {k: (v["aim"], v["ev"]) for k, v in bc.items() if k in c["order"][:3]}, time.time() - t0), flush=True)
    json.dump({str(a): b_ for a, b_ in res.items()}, open(out, "w"), indent=0, default=float)
