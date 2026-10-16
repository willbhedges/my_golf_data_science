"""Decision analysis for every Spirit Hollow tee shot.

  python3 spirit_hollow/analysis.py     -> output/analysis_report.md, output/analysis.json

For each hole:
  1. Decision with common random numbers (the same 10,000 swings for every club and aim) and
     the aim refined to 0.5 yd, plus the full outcome mix and the "blow-up" probability
     (penalty, trees or long grass).
  2. Model checks: does the pick survive (a) heavy-tailed misses (Student-t, nu=5, same 95%
     width), (b) misses that are correlated with distance (slice-type, rho = +/-0.3), and
     (c) an approximate 5-handicap scoring table instead of PGA Tour?
  3. Break-evens: one factor at a time over a grid, holding the rest at the measured values.
     Where the pick flips, the flip point is interpolated from the strokes difference.
  4. Global uncertainty: 120 random "worlds" drawing every uncertain input at once, including
     the map itself (each hazard outline moved ~4 yds). P(pick is best) is the share of worlds
     where it wins; the regret is what you'd lose on average by always playing the pick.
  5. Attribution: regress the strokes gap (pick - best alternative) on the standardised
     inputs across the worlds; each input's share of explained variance says which unknown
     the decision really hinges on.
"""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE]

import course                                  # noqa: E402
import tee_strategy as t                       # noqa: E402

t.HOLES = course.HOLES
N = 10000
ZS = np.vstack([np.random.default_rng(101).standard_normal((2, N)), np.random.default_rng(102).random((2, N))])
t.Z, t.N_SHOTS = ZS, N
AIMS = np.arange(-20, 20.1, 2.5)
BLOWUP = ("water", "ob", "recovery", "native")
BASE = dict(clubs=copy.deepcopy(t.CLUBS), holes=copy.deepcopy(course.HOLES), sev=t.TREE_SEVERITY,
            lost=t.NATIVE_LOST, mis=dict(t.MISHIT_RATE), roll=t.ROUGH_ROLL)


def reset():
    t.CLUBS = copy.deepcopy(BASE["clubs"])
    t.HOLES = copy.deepcopy(BASE["holes"])
    t.TREE_SEVERITY, t.NATIVE_LOST = BASE["sev"], BASE["lost"]
    t.MISHIT_RATE = dict(BASE["mis"])
    t.ROUGH_ROLL = BASE["roll"]
    t.set_tails(None)
    t.RHO = 0.0
    t.HCP_BASELINE = False


def decide(h, aims=AIMS, refine=True, z=None):
    t.REFINE = refine
    z = ZS if z is None else z
    res = {c: t.best_aim(h, c, aims=aims, z=z) for c in t.CLUBS}
    t.REFINE = False
    best = min(res, key=lambda c: res[c]["ev"])
    return best, res


def gap(res, pick):
    """EV(pick) - best EV of the other clubs (negative = pick is better)."""
    return res[pick]["ev"] - min(r["ev"] for c, r in res.items() if c != pick)


# ---------- 3. one-at-a-time break-evens -----------------------------------------------
def with_driver(width=None, carry_shift=0.0):
    c, tot, w, d = BASE["clubs"]["Driver"]
    t.CLUBS["Driver"] = (c + carry_shift, tot + carry_shift, width if width else w, d)


FACTORS = {
    "driver width (yds)": (np.array([50, 55, 60, 65, 70, 75, 80, 90]), lambda v: with_driver(width=v), 65),
    "driver carry vs 275": (np.array([-20, -10, -5, 0, 5, 10, 20]), lambda v: with_driver(carry_shift=v), 0),
    "all clubs' width x": (np.array([0.8, 0.9, 1.0, 1.15, 1.3, 1.5]),
                           lambda v: t.CLUBS.update({k: (a, b, w * v, d) for k, (a, b, w, d) in
                                                     BASE["clubs"].items()}), 1.0),
    "long grass lost-ball share": (np.array([0.1, 0.3, 0.5, 0.7, 0.9]), lambda v: setattr(t, "NATIVE_LOST", v), 0.5),
    "tree penalty (1 = chip out)": (np.array([0.3, 0.5, 0.75, 1.0]), lambda v: setattr(t, "TREE_SEVERITY", v), 1.0),
    "slight-mishit rate": (np.array([0.0, 0.08, 0.15, 0.25, 0.35]),
                           lambda v: setattr(t, "MISHIT_RATE", {k: v for k in BASE["mis"]}), 0.15),
}


def break_evens(h, pick):
    out = {}
    aims = np.arange(-20, 20.1, 5)
    for name, (grid, apply, base_v) in FACTORS.items():
        rows = []
        for v in grid:
            reset()
            apply(v)
            b, res = decide(h, aims=aims, refine=False)
            rows.append((float(v), b, {c: r["ev"] for c, r in res.items()}))
        reset()
        flips = []
        for (v0, b0, e0), (v1, b1, e1) in zip(rows, rows[1:]):
            if b0 != b1:
                d0 = e0[b0] - e0[b1]
                d1 = e1[b0] - e1[b1]
                x = v0 + (v1 - v0) * (0 - d0) / (d1 - d0) if d1 != d0 else (v0 + v1) / 2
                flips.append((x, b0, b1))
        out[name] = dict(base=base_v, picks=[(v, b) for v, b, _ in rows], flips=flips)
    return out


# ---------- 2. model-form checks ------------------------------------------------------------
def variants(h):
    out = {}
    for name, setup in [("heavy-tailed misses (t, nu=5)", lambda: t.set_tails(5)),
                        ("slice-type: right misses short (rho +0.3)", lambda: setattr(t, "RHO", 0.3)),
                        ("hook-type: left misses short (rho -0.3)", lambda: setattr(t, "RHO", -0.3)),
                        ("approx. 5-handicap scoring", lambda: setattr(t, "HCP_BASELINE", True))]:
        reset()
        setup()
        b, res = decide(h, refine=False)
        out[name] = (b, {c: float(r["ev"]) for c, r in res.items()})
    reset()
    return out


# ---------- 4/5. global uncertainty + attribution ----------------------------------------------
def worlds(n_worlds=120, seed=7):
    rng = np.random.default_rng(seed)
    zw = np.vstack([rng.standard_normal((2, 4000)), rng.random((2, 4000))])
    names = ["width x", "driver carry +", "roll x", "tree penalty", "lost-ball share", "mishit rate",
             "tail (t5=1)", "rho", "map jitter"]
    X, G, BEST = [], {h: [] for h in course.HOLES}, {h: [] for h in course.HOLES}
    EVS = {h: [] for h in course.HOLES}
    for wi in range(n_worlds):
        reset()
        f = dict(zip(names, [rng.uniform(0.9, 1.35), rng.normal(0, 6), rng.uniform(0.6, 1.3),
                             rng.uniform(0.4, 1.0), rng.uniform(0.3, 0.7), rng.uniform(0.05, 0.3),
                             float(rng.random() < 0.5), rng.uniform(-0.3, 0.3), rng.uniform(1, 6)]))
        for k, (c, tot, w, d) in BASE["clubs"].items():
            dc = f["driver carry +"] if k == "Driver" else rng.normal(0, 4)
            t.CLUBS[k] = (c + dc, c + dc + (tot - c) * f["roll x"], w * f["width x"], d)
        t.TREE_SEVERITY, t.NATIVE_LOST = f["tree penalty"], f["lost-ball share"]
        t.MISHIT_RATE = {k: f["mishit rate"] for k in BASE["mis"]}
        t.RHO = f["rho"]
        if f["tail (t5=1)"]:
            t.TAIL_NU = 5
            t.CHI = rng.chisquare(5, 4000) / 5
        for h, hd in t.HOLES.items():                       # move every outline a few yds
            ppy = t.hole_frame(hd)[3]
            hd["zones"] = [(nm, [(x + dx, y + dy) for x, y in poly])
                           for nm, poly in hd["zones"]
                           for dx, dy in [rng.normal(0, f["map jitter"] * ppy / 1.4, 2)]]
        X.append([f[k] for k in names])
        for h in course.HOLES:
            # CHI is cached for zw only when tails are on; simulate() uses it when z is Z,
            # so point Z at zw for this world
            t.Z = zw
            b, res = decide(h, aims=np.arange(-15, 15.1, 5), refine=False, z=zw)
            EVS[h].append({c: float(r["ev"]) for c, r in res.items()})
            BEST[h].append(b)
        t.Z = ZS
        print("world", wi + 1, flush=True)
    reset()
    return names, np.array(X), EVS, BEST


def attribution(names, X, evs, pick):
    gaps = np.array([e[pick] - min(v for c, v in e.items() if c != pick) for e in evs])
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    A = np.c_[np.ones(len(Xs)), Xs]
    coef, *_ = np.linalg.lstsq(A, gaps, rcond=None)
    pred = A @ coef
    r2 = 1 - ((gaps - pred) ** 2).sum() / max(((gaps - gaps.mean()) ** 2).sum(), 1e-12)
    contrib = coef[1:] ** 2                                  # independent inputs: var share
    share = contrib / max(contrib.sum(), 1e-12) * r2
    order = np.argsort(-share)
    return dict(r2=float(r2), top=[(names[i], float(share[i]), float(coef[1 + i])) for i in order[:3]],
                gap_mean=float(gaps.mean()), gap_p10=float(np.percentile(gaps, 10)),
                gap_p90=float(np.percentile(gaps, 90)))


def main():
    out = {}
    print("decisions + model checks + break-evens", flush=True)
    for h in course.HOLES:
        reset()
        pick, res = decide(h)
        r = res[pick]
        others = sorted((c for c in res if c != pick), key=lambda c: res[c]["ev"])
        out[h] = dict(pick=pick, aim=r["aim"], ev=float(r["ev"]), margin=float(res[others[0]]["ev"] - r["ev"]),
                      runner=others[0],
                      blowup={c: float(sum(res[c]["share"][k] for k in BLOWUP)) for c in res},
                      fairway={c: res[c]["share"]["fairway"] for c in res},
                      approach={c: res[c]["approach"] for c in res},
                      sd=float(r["strokes"].std()),
                      variants=variants(h), breaks=break_evens(h, pick))
        print(h, pick, f"{out[h]['margin']:.3f}", flush=True)
    names, X, EVS, BEST = worlds()
    for h in course.HOLES:
        pick = out[h]["pick"]
        b = BEST[h]
        out[h]["p_best"] = {c: b.count(c) / len(b) for c in t.CLUBS}
        out[h]["regret"] = float(np.mean([e[pick] - min(e.values()) for e in EVS[h]]))
        out[h]["attr"] = attribution(names, X, EVS[h], pick)
    with open(os.path.join(HERE, "output", "analysis.json"), "w") as f:
        json.dump({str(k): v for k, v in out.items()}, f, indent=1, default=float)
    write_report(out)


def describe_flip(name, info, pick):
    if not info["flips"]:
        return None
    parts = []
    for x, b0, b1 in info["flips"]:
        if "carry" in name:
            parts.append(f"{b0}→{b1} at driver carry {275 + x:.0f}")
        elif "width x" in name:
            parts.append(f"{b0}→{b1} at {x:.2f}× everyone's width")
        elif "width" in name:
            parts.append(f"{b0}→{b1} at driver width {x:.0f}")
        elif "lost" in name:
            parts.append(f"{b0}→{b1} at {x:.0%} lost balls in long grass")
        elif "tree" in name:
            parts.append(f"{b0}→{b1} at tree penalty {x:.2f}")
        else:
            parts.append(f"{b0}→{b1} at {x:.0%} mishits")
    return "; ".join(parts)


def write_report(out):
    lab = course.LABELS
    md = ["# Spirit Hollow — tee-shot decision analysis", "",
          "Margins are strokes per round on that hole (pick vs the next-best club). P(best) is the "
          "share of 120 random what-if worlds (all inputs and the map uncertain at once) in which "
          "the pick is the best club; regret is the average strokes lost in those worlds by always "
          "playing the pick. 'Hinges on' is the input that explains most of the variation in the "
          "pick's margin across the worlds.", "",
          "| Hole | Pick | Aim | Margin | P(best) | Regret | Blow-up risk pick / runner-up | Hinges on |",
          "|---|---|---|---|---|---|---|---|"]
    for h, o in out.items():
        a = o["attr"]["top"][0]
        md.append(f"| {lab.get(h, h)} | **{o['pick']}** | {o['aim']:+.1f} | {o['margin']:.3f} vs {o['runner']} | "
                  f"{o['p_best'][o['pick']]:.0%} | {o['regret']:.3f} | {o['blowup'][o['pick']]:.0%} / "
                  f"{o['blowup'][o['runner']]:.0%} | {a[0]} ({a[1]:.0%}) |")
    md += ["", "## Hole by hole", ""]
    for h, o in out.items():
        md += [f"### {lab.get(h, h)} — {o['pick']} (aim {o['aim']:+.1f})", ""]
        md.append("Model checks: " + "; ".join(
            f"{name}: {b}" + ("" if b == o["pick"] else " **(flips)**") for name, (b, _) in o["variants"].items()))
        flips = [describe_flip(n, i, o["pick"]) for n, i in o["breaks"].items()]
        flips = [f for f in flips if f]
        md.append("")
        md.append("Break-evens: " + ("; ".join(flips) if flips else "none inside the tested ranges"))
        a = o["attr"]
        md += ["", f"Across the worlds the pick's margin runs {-a['gap_p90']:+.3f} to {-a['gap_p10']:+.3f} "
               f"(10th-90th pct). Inputs explain {a['r2']:.0%} of that; top: "
               + ", ".join(f"{n} {s:.0%} ({'helps' if c < 0 else 'hurts'} the pick as it rises)"
                           for n, s, c in a["top"]), ""]
    path = os.path.join(HERE, "output", "analysis_report.md")
    with open(path, "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[:30]))


if __name__ == "__main__":
    main()
