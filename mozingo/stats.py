"""Strokes-gained statistics on top of tee_strategy.py.

  python3 mozingo/stats.py            -> output/stats_report.md

1. Strokes gained off the tee (SG:OTT) per club, vs the tour baseline from the tee.
2. Paired club-vs-club difference with standard error and 95% CI. Every club uses
   the same random draws, so the noise largely cancels.
3. Robustness: re-run each hole under 100 random "what if my inputs are off"
   scenarios (dispersion, carry, roll, hazard edges +/- a few yds, how penal the
   trees / prairie really are) and count how often each club comes out best.
4. Hole 13 deep dive: where every shot ends up and what each outcome costs.
"""
import copy
import os
import numpy as np
import tee_strategy as t

OUT = os.path.join(t.HERE, "output", "stats_report.md")
N_SCEN = 100
SCEN_SHOTS = 2000
LIES = ("fairway", "rough", "sand", "recovery", "native", "water")
LIE_NAME = {"recovery": "trees"}


def sg_table(hole_no):
    res = {c: t.best_aim(hole_no, c, aims=t.AIMS_WIDE if c in t.IRONS else t.AIMS)
           for c in t.clubs_for(hole_no)}
    best = min(res, key=lambda c: res[c]["ev"])
    base = t.tee_baseline(hole_no)
    rows = []
    for c, r in res.items():
        d = r["strokes"] - res[best]["strokes"]
        se = d.std(ddof=1) / np.sqrt(len(d))
        rows.append(dict(club=c, aim=r["aim"], ev=r["ev"], sg=base - r["ev"],
                         diff=d.mean(), lo=d.mean() - 1.96 * se, hi=d.mean() + 1.96 * se,
                         fw=r["share"]["fairway"], appr=r["approach"]))
    return best, rows


def perturbed_world(rng, holes0, clubs0, irons0):
    """One plausible version of reality around the measured inputs."""
    spread = rng.uniform(0.9, 1.3)                       # dispersion usually worse than the app's
    roll_f = rng.uniform(0.6, 1.3)

    def jiggle(table):
        out = {}
        for c, (carry, total, w, d) in table.items():
            dc = rng.normal(0, 5)
            out[c] = (carry + dc, carry + dc + (total - carry) * roll_f, w * spread, d * rng.uniform(0.9, 1.2))
        return out
    clubs, irons = jiggle(clubs0), jiggle(irons0)
    holes = copy.deepcopy(holes0)
    for h in holes.values():
        ppy = t.hole_frame(h)[3]
        h["zones"] = [(name, [(x + dx, y + dy) for x, y in poly])
                      for name, poly in h["zones"]
                      for dx, dy in [rng.normal(0, 4 * ppy, 2)]]  # each zone off by ~4 yds
    return clubs, irons, holes, rng.uniform(0.4, 1.0), rng.uniform(0.3, 0.7)


def robustness(rng):
    holes0, clubs0, irons0 = copy.deepcopy(t.HOLES), dict(t.CLUBS), dict(t.IRONS)
    sev0, lost0, mis0 = t.TREE_SEVERITY, t.NATIVE_LOST, dict(t.MISHIT_RATE)
    wins = {h: {c: 0 for c in t.clubs_for(h)} for h in holes0}
    for _ in range(N_SCEN):
        t.CLUBS, t.IRONS, t.HOLES, t.TREE_SEVERITY, t.NATIVE_LOST = perturbed_world(rng, holes0, clubs0, irons0)
        f = rng.uniform(0.4, 2.0)                              # slight-mishit rate anywhere from 6% to 30%
        t.MISHIT_RATE = {c: r * f for c, r in mis0.items()}
        z = np.vstack([rng.standard_normal((2, SCEN_SHOTS)), rng.random((2, SCEN_SHOTS))])
        for h in holes0:
            evs = {c: t.best_aim(h, c, aims=np.arange(-15, 40.1 if c in irons0 else 15.1, 5), z=z)["ev"]
                   for c in t.clubs_for(h)}
            wins[h][min(evs, key=evs.get)] += 1
    t.CLUBS, t.IRONS, t.HOLES, t.TREE_SEVERITY, t.NATIVE_LOST = clubs0, irons0, holes0, sev0, lost0
    t.MISHIT_RATE = mis0
    return wins


def lie_breakdown(hole_no, club, aim):
    _, lie, to_green, strokes = t.simulate(hole_no, club, aim)
    ev = strokes.mean()
    rows = []
    for name in LIES:
        m = lie == name
        if not m.any():
            continue
        rows.append(dict(lie=LIE_NAME.get(name, name), share=m.mean(), dist=to_green[m].mean(),
                         after=strokes[m].mean() - 1, contrib=(strokes[m] - ev).sum() / len(strokes)))
    return ev, rows


def main():
    rng = np.random.default_rng(2026)
    md = ["# Mozingo Lake — strokes-gained tee report", "",
          "SG:OTT = tour expected strokes from the tee minus (1 + expected strokes after the drive). "
          "Higher is better. *Diff* is the extra strokes per round vs the best club on that hole "
          "(paired, same random draws), with a 95% confidence interval.", ""]

    sg = {h: sg_table(h) for h in t.HOLES}
    print("SG tables done", flush=True)
    wins = robustness(rng)
    print("robustness done", flush=True)

    md += ["## Every hole", "",
           "| Hole | Club | Aim | Fairway | Approach | SG:OTT | Diff vs best (95% CI) | Best in % of what-if worlds |",
           "|---|---|---|---|---|---|---|---|"]
    for h, (best, rows) in sg.items():
        for r in rows:
            tag = f"**{r['club']}**" if r["club"] == best else r["club"]
            ci = "—" if r["club"] == best else f"+{r['diff']:.3f} ({r['lo']:+.3f} to {r['hi']:+.3f})"
            md.append(f"| {h} | {tag} | {r['aim']:+.1f} | {r['fw']:.0%} | {r['appr']:.0f} | "
                      f"{r['sg']:+.3f} | {ci} | {wins[h][r['club']]}% |")

    md += ["", "## Hole 13 deep dive", ""]
    _, rows13 = sg[13]
    for r in rows13:
        ev, br = lie_breakdown(13, r["club"], r["aim"])
        md += [f"### {r['club']} (aim {r['aim']:+.1f} yds) — expected score {ev:.3f}, SG:OTT {r['sg']:+.3f}", "",
               "| Ends in | Share | Avg yds to centre | Expected strokes from there | Cost vs this club's average |",
               "|---|---|---|---|---|"]
        for b in br:
            md.append(f"| {b['lie']} | {b['share']:.1%} | {b['dist']:.0f} | {b['after']:.2f} | {b['contrib']:+.3f} |")
        md.append("")

    md += ["### Aim curve (expected score by aim, yds right of the app line)", "",
           "| Aim | " + " | ".join(t.CLUBS) + " |", "|---|" + "---|" * len(t.CLUBS)]
    for aim in np.arange(-15, 15.1, 5):
        md.append(f"| {aim:+.0f} | " + " | ".join(f"{t.simulate(13, c, aim)[3].mean():.3f}" for c in t.CLUBS) + " |")

    md += ["", "### What would have to be true for one club to pull clear", "",
           "| Assumption | Driver | 2-wood | 4-wood |", "|---|---|---|---|"]
    clubs0 = dict(t.CLUBS)

    def row(label):
        evs = {c: t.best_aim(13, c)["ev"] for c in t.CLUBS}
        b = min(evs.values())
        md.append(f"| {label} | " + " | ".join(f"{evs[c] - b:+.3f}" for c in t.CLUBS) + " |")

    row("As measured")
    t.CLUBS = dict(clubs0, Driver=(275, 300, 55, 28)); row("Driver 55 wide (a good driving day)")
    t.CLUBS = {k: (c, tot, w * 1.2, d) for k, (c, tot, w, d) in clubs0.items()}; row("Everything 20% wider")
    t.CLUBS = {k: (c, c + 5, w, d) for k, (c, tot, w, d) in clubs0.items()}; row("Firm-ground roll off (soft day)")
    t.CLUBS = dict(clubs0)
    t.ROUGH_ROLL, r0 = 0.6, t.ROUGH_ROLL; row("Rough lets the ball run (60% roll)"); t.ROUGH_ROLL = r0
    t.TREE_SEVERITY = 0.5; row("Trees left only half as penal"); t.TREE_SEVERITY = 1.0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
