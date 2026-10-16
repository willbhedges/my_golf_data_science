"""Bayesian tee-shot decisions for Spirit Hollow.

  python3 spirit_hollow/decision.py         -> output/decision.json, output/decision_report.md

Why Bayesian: every input (your real dispersion, carry, roll, how penal the trees and long
grass are, exactly where each hazard edge is) is uncertain. A point estimate picks the club
that is best IF the inputs are exactly right. The Bayes decision instead picks the club and
aim that minimise expected strokes averaged over everything plausible:

    (club*, aim*) = argmin_{c,a}  E_theta[ ES(c, a | theta) ]

where ES is the strokes-gained simulation and theta ~ the prior below. That is the decision
rule a betting syndicate uses: integrate over the unknowns, don't bet on one guess.

Prior (theta)
  dispersion scale  lognormal, median 70/65 (centre 70 yds for driver, the other clubs
                    scaled alike), 90% interval ~ 62-80 yds. Fawcett's 65 is a tour pattern;
                    published 5-handicap data (research.md) points wider, so the prior leans a
                    little past 65 without assuming the worst.
  carry offsets     driver N(0, 5) yds; 2-wood / 4-wood N(0, 4), independent
  roll factor       U(0.75, 1.2) x the club's roll
  tree penalty      U(0.6, 1.0) (1 = always a chip-out)
  long-grass loss   U(0.35, 0.65) share of balls lost
  slight mishits    U(0.10, 0.20) of swings, 3-8% short
  map               every hazard outline moved by N(0, 2.5 yds) (after the full-zoom review)
  misses            normal (research.md: heavier tails aren't supported once the width is right)

Computation
  * S = 64 prior draws from a scrambled Sobol sequence (quasi-Monte Carlo: lower error than
    plain random draws for the same S).
  * Within each draw, common random numbers: the same 3,000 swings for every club and aim,
    so club-vs-club differences carry almost no simulation noise.
  * Aims searched on a 2.5-yd grid from -25 to +25 (+ hole-specific limits), then refined.

Outputs per hole
  * Bayes pick and aim; posterior expected strokes for every club (each at its own best aim).
  * Margin over the next club with a Monte Carlo standard error (paired across draws).
  * P(club is best) across the draws (with its own best aim per draw).
  * EVPI: strokes per round you'd save if you knew theta exactly (how much the uncertainty
    costs on this hole). Tiny EVPI = the decision is robust; it doesn't matter what's true.
  * Driver-width break-even: the driver dispersion at which the pick changes, with the other
    inputs at their prior means.
"""
import copy
import json
import os
import sys

import numpy as np
from scipy.stats import norm, qmc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE]

import course                                  # noqa: E402
import tee_strategy as t                       # noqa: E402

S = int(os.environ.get("DECISION_DRAWS", 64))
N = 3000
AIM_STEP = 2.5
CENTER_WIDTH = 70.0
BASE = dict(clubs=copy.deepcopy(t.CLUBS), holes=copy.deepcopy(course.HOLES), sev=t.TREE_SEVERITY,
            lost=t.NATIVE_LOST, mis=dict(t.MISHIT_RATE))
DIMS = ["width", "c_drv", "c_2w", "c_4w", "roll", "trees", "lost", "mishit", "map_seed"]


def prior_draws(s=S, seed=11):
    u = qmc.Sobol(len(DIMS), scramble=True, seed=seed).random(s)
    th = {}
    th["width"] = np.exp(np.log(CENTER_WIDTH / 65.0) + norm.ppf(u[:, 0]) * np.log(80 / 70) / 1.645)
    th["c_drv"] = norm.ppf(u[:, 1]) * 5
    th["c_2w"] = norm.ppf(u[:, 2]) * 4
    th["c_4w"] = norm.ppf(u[:, 3]) * 4
    th["roll"] = 0.75 + 0.45 * u[:, 4]
    th["trees"] = 0.6 + 0.4 * u[:, 5]
    th["lost"] = 0.35 + 0.30 * u[:, 6]
    th["mishit"] = 0.10 + 0.10 * u[:, 7]
    th["map_seed"] = (u[:, 8] * 1e9).astype(int)
    return [{k: th[k][i] for k in DIMS} for i in range(s)]


def apply(theta, holes_subset=None):
    """Set the module globals to one prior draw."""
    off = {"Driver": theta["c_drv"], "2-wood": theta["c_2w"], "4-wood": theta["c_4w"]}
    t.CLUBS = {}
    for k, (c, tot, w, d) in BASE["clubs"].items():
        t.CLUBS[k] = (c + off[k], c + off[k] + (tot - c) * theta["roll"], w * theta["width"], d)
    t.TREE_SEVERITY, t.NATIVE_LOST = theta["trees"], theta["lost"]
    t.MISHIT_RATE = {k: theta["mishit"] for k in BASE["mis"]}
    rng = np.random.default_rng(theta["map_seed"])
    holes = copy.deepcopy(BASE["holes"])
    for h, hd in holes.items():
        ppy = t.hole_frame(hd)[3]
        hd["zones"] = [(nm, [(x + dx, y + dy) for x, y in poly])
                       for nm, poly in hd["zones"]
                       for dx, dy in [rng.normal(0, 2.5 * ppy / 1.414, 2)]]
    t.HOLES = holes


def reset():
    t.CLUBS = copy.deepcopy(BASE["clubs"])
    t.HOLES = copy.deepcopy(BASE["holes"])
    t.TREE_SEVERITY, t.NATIVE_LOST = BASE["sev"], BASE["lost"]
    t.MISHIT_RATE = dict(BASE["mis"])


def aims_for(h):
    hd = BASE["holes"][h]
    lo = max(hd.get("aim_min", -25), -25)
    hi = min(hd.get("aim_max", 25), 25)
    return np.arange(lo, hi + 0.01, AIM_STEP)


def clubs_for(h):
    return list(BASE["clubs"]) + (list(t.IRONS) if BASE["holes"][h].get("irons") else [])


def ev_grid(h, z):
    """EV[club][aim index] under the current globals, common random numbers z."""
    out = {}
    for c in clubs_for(h):
        aims = aims_for(h) if c not in t.IRONS else np.arange(-25, 45.1, AIM_STEP)
        out[c] = (aims, np.array([t.simulate(h, c, a, z=z)[3].mean() for a in aims]))
    return out


def main():
    draws = prior_draws()
    rng = np.random.default_rng(5)
    holes = list(BASE["holes"])
    # E[h][c] = list over draws of (aims, ev array)
    E = {h: {} for h in holes}
    for si, th in enumerate(draws):
        apply(th)
        z = np.vstack([rng.standard_normal((2, N)), rng.random((2, N))])
        for h in holes:
            for c, (aims, ev) in ev_grid(h, z).items():
                E[h].setdefault(c, []).append((aims, ev))
        print(f"draw {si + 1}/{len(draws)}", flush=True)
    reset()
    res = {}
    for h in holes:
        clubs = list(E[h])
        post = {}                                      # posterior mean EV over aims
        for c in clubs:
            aims = E[h][c][0][0]
            M = np.stack([ev for _, ev in E[h][c]])    # draws x aims
            post[c] = (aims, M)
        best_c, best = None, None
        for c, (aims, M) in post.items():
            mean = M.mean(0)
            i = int(mean.argmin())
            if best is None or mean[i] < best[1]:
                best_c, best = c, (aims[i], mean[i], i)
        per_club = {}
        for c, (aims, M) in post.items():
            mean = M.mean(0)
            i = int(mean.argmin())
            per_club[c] = dict(aim=float(aims[i]), ev=float(mean[i]), col=i)
        runner = min((c for c in clubs if c != best_c), key=lambda c: per_club[c]["ev"])
        # paired MC error of the margin (each club at its posterior-best aim)
        a = post[best_c][1][:, per_club[best_c]["col"]]
        b = post[runner][1][:, per_club[runner]["col"]]
        d = b - a
        margin, se = float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))
        # P(best) and EVPI: per draw, best club at its own best aim
        per_draw_min = np.min(np.stack([post[c][1].min(1) for c in clubs]), axis=0)
        winners = [clubs[int(np.argmin([post[c][1][s].min() for c in clubs]))] for s in range(len(draws))]
        p_best = {c: winners.count(c) / len(draws) for c in clubs}
        evpi = float(np.mean(a - per_draw_min))
        res[h] = dict(pick=best_c, aim=float(per_club[best_c]["aim"]), ev=float(per_club[best_c]["ev"]),
                      runner=runner, margin=margin, margin_se=se, p_best=p_best, evpi=evpi,
                      clubs={c: dict(aim=v["aim"], ev=v["ev"]) for c, v in per_club.items()})
        print(h, best_c, f"aim {res[h]['aim']:+.1f}", f"margin {margin:.3f}±{se:.3f}",
              f"P(best) {p_best[best_c]:.0%}", f"EVPI {evpi:.3f}", flush=True)
    # driver-width break-evens at prior-mean other inputs
    mean_th = dict(width=CENTER_WIDTH / 65.0, c_drv=0.0, c_2w=0.0, c_4w=0.0, roll=1.0, trees=0.8,
                   lost=0.5, mishit=0.15, map_seed=0)
    zb = np.vstack([np.random.default_rng(9).standard_normal((2, 6000)), np.random.default_rng(10).random((2, 6000))])
    widths = np.array([55, 60, 65, 70, 75, 80, 85, 90]) / 65.0
    for h in holes:
        picks, gaps = [], []
        for w in widths:
            th = dict(mean_th, width=w)
            apply(th)
            t.HOLES = copy.deepcopy(BASE["holes"])      # no map jitter for the sweep
            # scale only the driver: other clubs at the centre width
            c0, tot0, w0, d0 = BASE["clubs"]["Driver"]
            t.CLUBS["Driver"] = (c0, tot0, w0 * w, d0)
            for k in ("2-wood", "4-wood"):
                c1, tt1, w1, d1 = BASE["clubs"][k]
                t.CLUBS[k] = (c1, tt1, w1 * CENTER_WIDTH / 65.0, d1)
            g = ev_grid(h, zb)
            evs = {c: ev.min() for c, (aims, ev) in g.items()}
            picks.append(min(evs, key=evs.get))
            gaps.append(evs)
        flips = []
        for i in range(len(widths) - 1):
            if picks[i] != picks[i + 1]:
                p0, p1 = picks[i], picks[i + 1]
                d0 = gaps[i][p0] - gaps[i][p1]
                d1 = gaps[i + 1][p0] - gaps[i + 1][p1]
                x = widths[i] + (widths[i + 1] - widths[i]) * (-d0) / (d1 - d0) if d1 != d0 else widths[i]
                flips.append(dict(width=float(x * 65), frm=p0, to=p1))
        res[h]["width_sweep"] = [dict(width=float(w * 65), pick=p) for w, p in zip(widths, picks)]
        res[h]["width_flips"] = flips
        print(h, "width flips", flips, flush=True)
    reset()
    with open(os.path.join(HERE, "output", "decision.json"), "w") as f:
        json.dump({str(k): v for k, v in res.items()}, f, indent=1)
    write_report(res)


def write_report(res):
    lab = course.LABELS
    md = ["# Spirit Hollow — Bayesian tee-shot decisions", "",
          f"{S} quasi-Monte Carlo prior draws x {N} swings (common random numbers within each draw). "
          "Driver dispersion prior centred on 70 yds (90% ~62-80). Margin is posterior expected strokes "
          "saved per round vs the next club, ± Monte Carlo standard error. P(best) is the share of "
          "plausible worlds where the pick is the right club. EVPI is what perfect knowledge of your "
          "game would save on that hole: small EVPI means the decision is robust.", "",
          "| Hole | Pick | Aim | Margin ± SE | P(best) | EVPI | Driver-width break-even |",
          "|---|---|---|---|---|---|---|"]
    for h, r in res.items():
        fl = "; ".join(f"{f['frm']}→{f['to']} at {f['width']:.0f} yds" for f in r["width_flips"]) or "none (55-90 yds)"
        md.append(f"| {lab.get(h, h)} | **{r['pick']}** | {r['aim']:+.1f} | {r['margin']:.3f} ± {r['margin_se']:.3f} "
                  f"vs {r['runner']} | {r['p_best'][r['pick']]:.0%} | {r['evpi']:.3f} | {fl} |")
    tot_evpi = sum(r["evpi"] for r in res.values())
    md += ["", f"Total EVPI over these tee shots: {tot_evpi:.2f} strokes per round.", ""]
    with open(os.path.join(HERE, "output", "decision_report.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
