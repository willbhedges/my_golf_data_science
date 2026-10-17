"""Small multiples of the prior-averaged EV-vs-aim curve per club, one panel per hole.

  python3 spirit_hollow/v2/plot_curves.py   -> spirit_hollow/v2/output/ev_curves.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                 # noqa: E402
import numpy as np                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
COL = {"Driver": "#2a78d6", "2-wood": "#eb6834", "4-wood": "#1baf7a", "Long iron": "#eda100", "Mid iron": "#e87ba4"}
LAB = {"2B": "2 Gold", "2F": "2 Black", "9B": "9 Gold", "9F": "9 Black"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def main():
    v2 = json.load(open(os.path.join(HERE, "output", "v2_decisions.json")))
    fig, axs = plt.subplots(4, 4, figsize=(15, 13), facecolor="#fcfcfb")
    for ax, (h, r) in zip(axs.ravel(), v2.items()):
        x = np.array(r["curve_aims"])
        best = min(v["ev"] for v in r["clubs"].values())
        ax.set_facecolor("#fcfcfb")
        for c, v in r["clubs"].items():
            y = np.array(v["curve"]) - best
            ax.plot(x, y, color=COL[c], lw=2, label=c)
        p = r["clubs"][r["pick"]]
        ax.axvspan(*r["window"], color=COL[r["pick"]], alpha=0.15, lw=0)
        ax.plot([r["aim"]], [p["ev"] - best], "o", ms=8, color=COL[r["pick"]], mec="#fcfcfb", mew=2)
        ax.set_ylim(-0.02, 0.3)
        ax.set_xlim(-60, 60)
        ax.axvline(0, color=GRID, lw=1, zorder=0)
        ax.grid(axis="y", color=GRID, lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID)
        ax.tick_params(colors=MUTED, labelsize=8)
        side = "line" if abs(r["aim"]) < 0.25 else f"{abs(r['aim']):.1f} {'L' if r['aim'] < 0 else 'R'}"
        ax.set_title(f"{LAB.get(h, 'Hole ' + h)}: {r['pick']}, aim {side}" + (" (tie)" if r["tie"] else ""),
                     fontsize=10, color=INK, loc="left")
    axs[0, 0].legend(fontsize=8, frameon=False, labelcolor=INK)
    fig.supxlabel("Aim, yds right of the app line (negative = left)", color=MUTED)
    fig.supylabel("Expected strokes above the hole's best club and aim", color=MUTED)
    fig.suptitle("v2: expected strokes vs aim, every club, averaged over 64 prior draws (shaded = aim window, "
                 "within 0.005)", color=INK, fontsize=12)
    fig.tight_layout(rect=(0.02, 0.02, 1, 0.97))
    fig.savefig(os.path.join(HERE, "output", "ev_curves.png"), dpi=90)


if __name__ == "__main__":
    main()
