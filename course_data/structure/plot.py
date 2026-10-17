"""Debug / report plot of one course: true holes (grey, numbered) vs the routed holes (coloured by correctness).

    python course_data/structure/plot.py <slug> [--degrade] [--out file.png]
"""
from __future__ import annotations

import argparse
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eval as E                                                     # noqa: E402
import scene as S                                                    # noqa: E402
import solver as V                                                   # noqa: E402


def plot(sc, truth, res, out, title=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 11))
    for f in sc.fairways:
        if f.get("ring") is not None:
            ax.fill(*np.asarray(f["ring"]).T, color="#cfe8c0", lw=0)
    for r in sc.water:
        ax.fill(*np.asarray(r).T, color="#bcd7f0", lw=0)
    for p in sc.paths:
        ax.plot(*np.asarray(p).T, color="#c8b89a", lw=0.8)
    for g in sc.greens:
        if g.get("ring") is not None:
            ax.fill(*np.asarray(g["ring"]).T, color="#4caf50", lw=0)
        ax.text(*g["c"], g["id"], fontsize=6, color="#1b5e20")
    for t in sc.tees:
        ax.plot(*t["c"], "s", ms=3, color="#795548")
    for h in truth:
        ax.plot(*np.asarray(h["line"]).T, color="#888", lw=1, ls="--")
        ax.text(*h["tee"], f"T{h['ref']}", fontsize=8, color="#555")
    m = E.match(res, sc, truth) if truth else [None] * len(res["holes"])
    for h, r in zip(res["holes"], m):
        col = "#1565c0" if r == h["number"] else ("#ef6c00" if r is not None else "#c62828")
        t, g = np.asarray(h["tee_xy"]), np.asarray(h["green_xy"])
        ax.annotate("", g, t, arrowprops=dict(arrowstyle="->", color=col, lw=1.6))
        ax.text(*(t + (g - t) * 0.5), f"{h['number']} ({h['confidence']:.2f})", color=col, fontsize=9, weight="bold")
    for c in sc.clubhouse:
        ax.plot(*c["c"], "*", ms=14, color="#6a1b9a")
    if res.get("clubhouse"):
        ax.plot(*res["clubhouse"]["xy"], "x", ms=14, color="#d81b60", mew=3)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(out, dpi=90)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--degrade", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    e = next(x for x in E.courses() if x["slug"] == a.slug)
    sc, truth, N, _ = E.load(e)
    if a.degrade:
        sc = S.degrade(sc, random.Random(f"0-{a.slug}"))
    res = V.solve(sc)
    r = E.score_course(res, sc, truth, N)
    plot(sc, truth, res, a.out or f"{a.slug}.png",
         f"{a.slug}: formation {r['formation']}/{N}, numbers {r['number']}/{N} (blue right, orange wrong number, red wrong hole)")
    print(a.out)


if __name__ == "__main__":
    main()
