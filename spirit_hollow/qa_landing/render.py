import sys, os
sys.path[:0] = ["mozingo", "spirit_hollow"]
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
from matplotlib.image import imread
import course
col = dict(fairway="#00ff66", first_cut="#b6ff00", recovery="#ff00ff", water="#00b7ff", sand="#ffffff",
           native="#ffae00", rough="#bbbbbb", ob="#ff0000")
out = sys.argv[1]; holes = sys.argv[2:] or [str(h) for h in course.HOLES]
for hk in holes:
    h = int(hk) if hk.isdigit() else hk
    hd = course.HOLES[h]
    tee, d = np.array(hd["tee"], float), np.array(hd["dot270"], float)
    ppy = np.linalg.norm(d - tee) / 270; f = (d - tee) / np.linalg.norm(d - tee); r = np.array([-f[1], f[0]])
    P = lambda a, l: tee + (a * f + l * r) * ppy
    pts = np.array([P(a, l) for a in (190, 335) for l in (-55, 55)])
    x0, y0 = pts.min(0); x1, y1 = pts.max(0)
    clean = os.path.join("spirit_hollow/screenshots_clean", hd["image"])
    img = imread(clean)
    fig, axs = plt.subplots(1, 2, figsize=(13, 9))
    for k, ax in enumerate(axs):
        ax.imshow(img, extent=(0, 920, 2000, 0))
        for a in range(200, 331, 25):                     # distance ticks across the corridor
            q = np.array([P(a, -55), P(a, 55)]); ax.plot(q[:, 0], q[:, 1], color="w", lw=.5, alpha=.6)
            ax.text(*P(a, -48), f"{a}y", color="yellow", fontsize=8, weight="bold")
        for l in (-40, -20, 0, 20, 40):
            q = np.array([P(190, l), P(335, l)]); ax.plot(q[:, 0], q[:, 1], color="y" if l == 0 else "w",
                                                      lw=.8 if l == 0 else .4, alpha=.7)
            ax.text(*P(330, l), f"{l:+d}", color="yellow", fontsize=7)
        if k:
            for n, p in hd["zones"]:
                Q = np.array(list(p) + [p[0]], float)
                ax.fill(Q[:, 0], Q[:, 1], color=col.get(n, "k"), alpha=.25)
                ax.plot(Q[:, 0], Q[:, 1], color=col.get(n, "k"), lw=1.2)
        ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.tick_params(labelsize=6); ax.grid(False)
    fig.suptitle(f"Hole {h}: photo | model (magenta trees, orange long grass, blue water, white sand, green fw, lime 1st cut, grey rough)", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(out, f"h{h}.png"), dpi=72); plt.close(fig)
    print("rendered", h)
