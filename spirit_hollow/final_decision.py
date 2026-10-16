"""Final Bayesian tee-shot decisions for Spirit Hollow (this is what the book uses).

  python3 spirit_hollow/final_decision.py    -> output/final_decision.json, output/final_decision.md

Combines
  * the audited map (course.py incl. AUDIT_FIXES),
  * the model fix from the statistics review: a ball lost in long grass is stroke and distance,
  * the reviewer's prior structure (review_stats/prior_patch.py): common + per-club carry,
    uncertain club-to-club width ratios, carry-depth and rough-roll uncertainty, 128 Sobol draws
    -- with two deliberate choices by the golfer/integrator:
      - driver dispersion centred on 70 yds (90% ~62-80), i.e. close to Fawcett's 65-yd tour
        pattern rather than the reviewer's research-based 82;
      - PGA Tour scoring tables (as DECADE uses), not the 5-handicap table;
      - carry-depth widening 1.25x (reviewer suggested 1.5x);
  * the reviewer's honest reporting (review_stats/decision_stats.py): cross-fitted margin
    (winner's-curse corrected), error budget, EVPI bracket, noise-corrected P(best), and an
    all-clubs-scaled dispersion break-even.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE, os.path.join(HERE, "review_stats")]

import course                                  # noqa: E402
import decision as D                           # noqa: E402
import decision_stats as DS                    # noqa: E402
import prior_patch as PP                       # noqa: E402
import tee_strategy as t                       # noqa: E402

S = int(os.environ.get("FINAL_DRAWS", 128))
N = 3000
WIDTH_MEDIAN, WIDTH_HI90 = 70.0, 80.0
DEPTH_SCALE = 1.25
TIE = 0.01                                      # margins under this (after cross-fitting) = tie


def draws():
    th = PP.prior_draws(S, width_median=WIDTH_MEDIAN, width_hi90=WIDTH_HI90)
    for d in th:
        d["depth"] = d["depth"] / 1.5 * DEPTH_SCALE
        d["hcp"] = False
    return th


def main():
    rng = np.random.default_rng(2027)
    only = [x.strip() for x in os.environ.get("FINAL_HOLES", "").split(",") if x.strip()]
    E = {h: {} for h in D.BASE["holes"] if not only or str(h) in only}   # same draws/z either way
    for i, th in enumerate(draws()):
        PP.apply(th)
        t.HCP_BASELINE = False
        z = np.vstack([rng.standard_normal((2, N)), rng.random((2, N))])
        for h in E:
            DS.accumulate(E[h], DS.ev_grid_halves(h, z))
        print(f"draw {i + 1}/{S}", flush=True)
    PP.reset()
    path = os.path.join(HERE, "output", "final_decision.json")
    out = json.load(open(path)) if only and os.path.exists(path) else {}    # update those holes only
    for h in E:
        r = DS.summarize(E[h])
        cf = r["crossfit"]
        cf_margin = float(cf["margin_out"])
        r["crossfit_margin"] = cf_margin
        r["tie"] = bool(min(r["margin"], cf_margin) < TIE)
        picks, flips, rows = DS.width_sweep(h, mode="common")
        r["width_sweep"] = [dict(width=w, pick=p) for w, p in zip((55, 60, 65, 70, 75, 80, 85, 90), picks)]
        r["width_flips"] = [dict(width=float(x), frm=a, to=b) for x, a, b in flips]
        out[str(h)] = r
        print(h, r["pick"], f"aim {r['aim']:+.1f}", f"margin {r['margin']:.3f}±{r['margin_se']:.3f}",
              f"cf {cf_margin:.3f}", "TIE" if r["tie"] else "", r["width_flips"], flush=True)
    with open(path, "w") as f:
        json.dump(out, f, indent=1, default=float)
    write_md(out)


def write_md(out):
    lab = course.LABELS
    md = ["# Spirit Hollow — final tee decisions", "",
          f"{S} Sobol prior draws x {N} swings; driver dispersion centred 70 yds (90% 62-80); PGA Tour "
          "baselines; lost ball in long grass = stroke and distance; audited map. Margin = expected "
          "strokes saved vs the next club (± MC SE); cross-fitted = the same, corrected for picking "
          f"the best of a noisy grid. Margins under {TIE} are ties.", "",
          "| Hole | Pick | Aim | Margin ± SE | Cross-fitted | P(pick beats runner-up) | EVPI | Width break-even |",
          "|---|---|---|---|---|---|---|---|"]
    for h, r in out.items():
        key = int(h) if h.isdigit() else h
        fl = "; ".join(f"{f['frm']}→{f['to']} at {f['width']:.0f}" for f in r["width_flips"]) or "none 55-90"
        pb = r.get("p_pick_beats", {}).get(r["runner"])
        pb = f"{pb:.0%}" if isinstance(pb, (int, float)) else "—"
        md.append(f"| {lab.get(key, h)} | **{r['pick']}**{' (tie)' if r['tie'] else ''} | {r['aim']:+.1f} | "
                  f"{r['margin']:.3f} ± {r['margin_se']:.3f} vs {r['runner']} | {r['crossfit_margin']:.3f} | {pb} | "
                  f"{r['evpi_crossfit']:.3f}-{r['evpi_naive']:.3f} | {fl} |")
    with open(os.path.join(HERE, "output", "final_decision.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
