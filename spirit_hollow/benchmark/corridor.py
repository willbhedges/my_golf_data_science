"""DECADE benchmark: Scott Fawcett's corridor rule vs the simulation model.

  python3 spirit_hollow/benchmark/corridor.py            -> benchmark/results.json + table.md
  python3 spirit_hollow/benchmark/corridor.py --no-model -> corridors only (seconds)

For each hole and wood, measure the width of the corridor free of "dead" zones
(water, ob, recovery = trees; optionally native long grass too) across the
club's landing window (total-20 .. total+10 yds, every 2 yds). At each along
distance the lateral line -60..+60 yds is scanned every 0.5 yd and the widest
contiguous dead-free run that contains the tee line (or, failing that, the one
nearest it) is kept. The corridor width for the club is the minimum over the
window; its centre (the DECADE aim) is the middle of the lateral band that is
clear at every step of the window (max of the left edges .. min of the right
edges). Widths/edges are capped by the +-60 scan, so 120 means 'wide open'.

DECADE rule (Fawcett): driver if its corridor >= 65 yds; otherwise the
longest of 2-wood / 4-wood whose corridor >= 65; if none does, the club with the
widest corridor (longer club on ties within 2 yds). Aim = that club's corridor
centre. Rough and bunkers are ignored, as the rule does.

The model's pick is t.best_aim() on each wood with the default settings (the
same as the published book), and spirit_hollow/output/decision.json's 'pick'
if that file exists.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SH, "..", "mozingo"))
sys.path.insert(0, SH)

import course                     # noqa: E402
import tee_strategy as t          # noqa: E402

t.HOLES = course.HOLES
WOODS = ["Driver", "2-wood", "4-wood"]
DEAD = ("water", "ob", "recovery")
DEAD_NATIVE = DEAD + ("native",)
THRESH = 65.0
LATS = np.arange(-60, 60.01, 0.5)
STEP = 0.5


def runs(free):
    """Contiguous True runs in a boolean array -> list of (i0, i1) inclusive."""
    out, i, n = [], 0, len(free)
    while i < n:
        if free[i]:
            j = i
            while j + 1 < n and free[j + 1]:
                j += 1
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def corridor_at(h, along, dead):
    tee, fwd, right, ppy = t.hole_frame(h)
    pts = tee + (along * fwd[None, :] + LATS[:, None] * right[None, :]) * ppy
    lie = t.lie_at(h, pts)
    free = ~np.isin(lie, dead)
    rs = runs(free)
    if not rs:
        return 0.0, 0.0, 0.0, 0.0
    i0 = np.argmin(np.abs(LATS))
    containing = [r for r in rs if r[0] <= i0 <= r[1]]
    if containing:
        r = containing[0]
    else:   # nearest run to the tee line, widest among equally near
        r = min(rs, key=lambda r: (min(abs(LATS[r[0]]), abs(LATS[r[1]])), -(r[1] - r[0])))
    lo, hi = LATS[r[0]] - STEP / 2, LATS[r[1]] + STEP / 2   # each sample covers +-0.25 yd
    lo, hi = max(lo, LATS[0]), min(hi, LATS[-1])
    return hi - lo, (lo + hi) / 2, lo, hi


def corridor(hole, club, dead):
    h = course.HOLES[hole]
    total = t.CLUBS[club][1]          # nominal total (no extra_roll), per the task spec
    rows = []
    for a in np.arange(total - 20, total + 10.01, 2):
        w, c, lo, hi = corridor_at(h, a, dead)
        rows.append((float(a), w, c, lo, hi))
    k = int(np.argmin([r[1] for r in rows]))
    lo, hi = max(r[3] for r in rows), min(r[4] for r in rows)   # corridor clear over the whole window
    return dict(min_width=rows[k][1], at=rows[k][0], centre=(lo + hi) / 2 if hi > lo else rows[k][2],
                centre_mean=float(np.mean([r[2] for r in rows])), centre_at_min=rows[k][2], lo=lo, hi=hi,
                profile=[(r[0], r[1], r[2]) for r in rows])


def decade(widths, centres):
    for c in WOODS:
        if widths[c] >= THRESH:
            return c, centres[c], "corridor >= 65"
    best = max(WOODS, key=lambda c: widths[c])
    for c in WOODS:                                   # longest club within 2 yds of the widest
        if widths[c] >= widths[best] - 2:
            return c, centres[c], "none >= 65: widest corridor"
    return best, centres[best], "none >= 65: widest corridor"


def main(run_model=True):
    t0 = time.time()
    dec_path = os.path.join(SH, "output", "decision.json")
    bayes = json.load(open(dec_path)) if os.path.exists(dec_path) else None
    out = {}
    for hole in course.HOLES:
        r = dict(corr={}, corr_native={})
        for c in WOODS:
            r["corr"][c] = corridor(hole, c, DEAD)
            r["corr_native"][c] = corridor(hole, c, DEAD_NATIVE)
        w = {c: r["corr"][c]["min_width"] for c in WOODS}
        ce = {c: r["corr"][c]["centre"] for c in WOODS}
        r["decade"] = decade(w, ce)
        wn = {c: r["corr_native"][c]["min_width"] for c in WOODS}
        cn = {c: r["corr_native"][c]["centre"] for c in WOODS}
        r["decade_native"] = decade(wn, cn)
        if run_model:
            m = {}
            for c in WOODS:
                b = t.best_aim(hole, c)
                m[c] = dict(aim=float(b["aim"]), ev=float(b["ev"]), approach=b["approach"], share=b["share"])
            pick = min(WOODS, key=lambda c: m[c]["ev"])
            r["model"] = dict(clubs=m, pick=pick, aim=m[pick]["aim"])
        if bayes and str(hole) in bayes:
            bh = bayes[str(hole)]
            r["bayes"] = dict(pick=bh["pick"], aim=bh["aim"], margin=bh.get("margin"),
                              margin_se=bh.get("margin_se"), p_best=bh.get("p_best"))
        out[str(hole)] = r
        print(f"{hole}: done ({time.time() - t0:.0f}s)", flush=True)
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    write_table(out)
    print(f"total {time.time() - t0:.0f}s")


def write_table(out):
    ab = {"Driver": "D", "2-wood": "2W", "4-wood": "4W"}
    L = ["| Hole | Corridor D / 2W / 4W (yds, dead = water/OB/trees) | + native as dead | DECADE pick, aim "
         "| DECADE (native dead) | Model pick, aim (EV gap to next) | Bayes pick, aim | Agree? |",
         "|---|---|---|---|---|---|---|---|"]
    for hole, r in out.items():
        w = " / ".join(f"{r['corr'][c]['min_width']:.0f}" for c in WOODS)
        wn = " / ".join(f"{r['corr_native'][c]['min_width']:.0f}" for c in WOODS)
        d, da, _ = r["decade"]
        dn, dna, _ = r["decade_native"]
        ms = mb = ag = "-"
        if "model" in r:
            m = r["model"]
            evs = sorted(m["clubs"][c]["ev"] for c in WOODS)
            ms = f"{ab[m['pick']]} {m['aim']:+.1f} ({evs[1] - evs[0]:.3f})"
            ag = "yes" if m["pick"] == d else "**no**"
        if "bayes" in r:
            mb = f"{ab[r['bayes']['pick']]} {r['bayes']['aim']:+.1f}"
            if "model" in r and r["bayes"]["pick"] != d:
                ag = ag + " / Bayes no" if ag == "yes" else ag
        L.append(f"| {course.LABELS.get(hole if not hole.isdigit() else int(hole), hole)} | {w} | {wn} | "
                 f"{ab[d]} {da:+.1f} | {ab[dn]} {dna:+.1f} | {ms} | {mb} | {ag} |")
    with open(os.path.join(HERE, "table.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(run_model="--no-model" not in sys.argv)
