"""Comparison tables for REPORT.md (v1 final_decision.json vs v2 v2_decisions.json).

  python3 spirit_hollow/v2/tables.py > spirit_hollow/v2/output/tables.md
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
LAB = {"2B": "2 Gold", "2F": "2 Black", "9B": "9 Gold", "9F": "9 Black"}
SHORT = {"Driver": "D", "2-wood": "2W", "4-wood": "4W", "Long iron": "LI", "Mid iron": "MI"}


def side(a):
    return "line" if abs(a) < 0.25 else f"{abs(a):.1f} {'L' if a < 0 else 'R'}"


def main():
    v1 = json.load(open(os.path.join(SH, "output", "final_decision.json")))
    v2 = json.load(open(os.path.join(HERE, "output", "v2_decisions.json")))
    print("## Per hole: v1 (live page) vs v2\n")
    print("Aims in yds left (L) / right (R) of the app's line. v1 aim on a 2.5-yd grid, search ±25; v2 aim to "
          "0.5 yd (Brent on the prior-averaged, smoothed curve), search ±60. Aim window = every aim within "
          "0.005 strokes of the best. Margin = expected strokes saved vs the runner-up club (± MC SE over 64 "
          "draws); cross-fitted = choose on half the draws, score on the other half.\n")
    print("| Hole | v1 pick, aim | v1 margin | v2 pick, aim | v2 aim window | v2 margin ± SE vs | cross-fit | "
          "P(beats runner) | change |")
    print("|---|---|---|---|---|---|---|---|---|")
    for h, r in v2.items():
        a = v1.get(h, {})
        v1s = f"{a.get('pick')} {side(a.get('aim', 0))}" + (" (tie)" if a.get("tie") else "") if a else "—"
        v1m = f"{a['margin']:.3f} vs {SHORT.get(a['runner'], a['runner'])}" if a else "—"
        w = r["window"]
        v2s = f"**{r['pick']}** {side(r['aim'])}" + (" (tie)" if r["tie"] else "")
        bound = " ⚠ bound" if r["at_bound"] else ""
        chg = []
        if a and a.get("pick") != r["pick"]:
            chg.append("club")
        if a and a.get("pick") == r["pick"] and abs(a.get("aim", 0) - r["aim"]) >= 3:
            chg.append(f"aim {r['aim'] - a['aim']:+.1f}")
        print(f"| {LAB.get(h, h)} | {v1s} | {v1m} | {v2s}{bound} | {side(w[0])} to {side(w[1])} | "
              f"{r['margin']:.3f} ± {r['margin_se']:.3f} {SHORT[r['runner']]} | {r['crossfit_margin']:.3f} | "
              f"{r['p_pick_beats_runner']:.0%} | {', '.join(chg) or '—'} |")
    print("\n## Cost of playing v1's club and aim, scored by v2 (prior-averaged curves)\n")
    print("| Hole | v1 play | v2 play | strokes lost by v1 play |")
    print("|---|---|---|---|")
    import numpy as np
    tot = 0.0
    for h, r in v2.items():
        a = v1.get(h)
        if not a:
            continue
        x = np.array(r["curve_aims"])
        y = np.array(r["clubs"][a["pick"]]["curve"])
        yb = np.array(r["clubs"][r["pick"]]["curve"])
        loss = float(np.interp(a["aim"], x, y) - np.interp(r["aim"], x, yb))
        if h not in ("2B", "9B"):
            tot += loss
        print(f"| {LAB.get(h, h)} | {a['pick']} {side(a['aim'])} | {r['pick']} {side(r['aim'])} | {loss:+.3f} |")
    print(f"\nBlack-tee round (14 tee holes, Gold 2/9 excluded): v1's plays cost **{tot:.2f} strokes** "
          "per round under v2.\n")
    print("\n## Every club at its own robust aim (v2, prior-averaged EV; window in brackets)\n")
    print("| Hole | Driver | 2-wood | 4-wood | Long iron | Mid iron |")
    print("|---|---|---|---|---|---|")
    for h, r in v2.items():
        best = min(v["ev"] for v in r["clubs"].values())
        cells = []
        for c in ("Driver", "2-wood", "4-wood", "Long iron", "Mid iron"):
            v = r["clubs"][c]
            d = v["ev"] - best
            cells.append(("**" if d == 0 else "") + f"{side(v['aim'])} [{side(v['window'][0])}, {side(v['window'][1])}]"
                         f" {'+%.3f' % d if d else '%.3f' % v['ev']}" + (" ⚠" if v["at_bound"] else "")
                         + ("**" if d == 0 else ""))
        print(f"| {LAB.get(h, h)} | " + " | ".join(cells) + " |")
    print("\n## Change ladder (central world): pick / aim after each change, cumulative from v1's world\n")
    steps = [s["step"] for s in next(iter(v2.values()))["ladder"]]
    print("| Hole | " + " | ".join(f"{i}" for i in range(len(steps))) + " |")
    print("|---|" + "---|" * len(steps))
    for h, r in v2.items():
        print(f"| {LAB.get(h, h)} | " + " | ".join(f"{SHORT[s['pick']]} {side(s['aim'])}" for s in r["ladder"]) + " |")
    print("\nSteps: " + "; ".join(f"{i} = {s}" for i, s in enumerate(steps)) + ".\n")
    print("## Sensitivities (central world, N = 12,000): pick / aim\n")
    names = list(next(iter(v2.values()))["sens"])
    print("| Hole | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    for h, r in v2.items():
        base = r["sens"]["central"]["pick"]
        cells = []
        for n in names:
            s = r["sens"][n]
            txt = f"{SHORT[s['pick']]} {side(s['aim'])}"
            cells.append(f"**{txt}**" if s["pick"] != base else txt)
        print(f"| {LAB.get(h, h)} | " + " | ".join(cells) + " |")
    print("\nBold = a different club from the v2 central world.\n")
    print("## Common-width break-evens (v2 central world; all clubs scale together)\n")
    print("| Hole | " + " | ".join(str(w["width"]) for w in next(iter(v2.values()))["width_sweep"]) + " | flips |")
    print("|---|" + "---|" * (len(next(iter(v2.values()))["width_sweep"]) + 1))
    for h, r in v2.items():
        fl = "; ".join(f"{f['frm']}→{f['to']} at {f['width']:.0f}" for f in r["width_flips"]) or "none"
        print(f"| {LAB.get(h, h)} | " + " | ".join(SHORT[w["pick"]] for w in r["width_sweep"]) + f" | {fl} |")


if __name__ == "__main__":
    main()
