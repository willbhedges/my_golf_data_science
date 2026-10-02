"""Mozingo Lake GC tee-shot strategy, Scott Fawcett / DECADE style.

For each hole and each tee club we:
  1. Model the shot pattern as a 2-D normal around the aim point. The lateral
     "dispersion" width from the GPS app (65 / 60 / 50 yds) is treated as the
     ~95% window (+/- 2 sigma), as in Fawcett's shot-pattern ellipses. Balls
     land at carry, then roll out (less in rough, not at all in a hazard).
  2. Drop thousands of simulated tee shots onto hazard polygons traced from
     the satellite screenshots in ./screenshots.
  3. Score every landing spot with strokes-gained baselines (expected strokes
     to hole out from that lie and distance; Mark Broadie's tour benchmarks).
  4. Search aim points left/right of the app's line and keep the best one.

The club with the lowest expected score from the tee is the play.

Geometry is traced by eye in screenshot pixels (920 x 2000 frame). Yardage
scale is calibrated per hole from the app's own 270-yard dot, so each tee and
dot position anchors the map.
"""

import os
import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(7)
N_SHOTS = 20000

# name: (carry yds, total yds on fairway, lateral 95% width, carry-depth 95% window)
CLUBS = {
    "Driver": (275, 300, 65, 28),
    "2-wood": (265, 280, 60, 26),
    "4-wood": (255, 270, 50, 24),
}
ROUGH_ROLL = 0.3    # share of remaining roll kept once the ball is in rough
HAZARDS = ("sand", "recovery", "native", "water")   # ball stops where it lands/enters

# Expected strokes to hole out (Broadie, PGA Tour baseline), by distance in yds.
DIST = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
BASELINE = {
    "fairway":  [2.40, 2.60, 2.70, 2.75, 2.80, 2.85, 2.91, 2.98, 3.08, 3.19, 3.32, 3.45, 3.58, 3.69, 3.78],
    "rough":    [2.59, 2.78, 2.91, 2.96, 3.02, 3.08, 3.15, 3.23, 3.31, 3.42, 3.53, 3.64, 3.74, 3.83, 3.90],
    "sand":     [2.53, 2.82, 3.15, 3.24, 3.23, 3.21, 3.22, 3.28, 3.40, 3.55, 3.70, 3.84, 3.93, 4.00, 4.04],
    "recovery": [3.40, 3.55, 3.70, 3.75, 3.80, 3.78, 3.80, 3.81, 3.82, 3.87, 3.92, 3.97, 4.03, 4.10, 4.20],
}


def expected_strokes(lie, dist):
    dist = np.clip(dist, DIST[0], DIST[-1])
    if lie == "water":     # penalty stroke, drop in rough at same distance
        return 1.0 + np.interp(dist, DIST, BASELINE["rough"])
    if lie == "native":    # tall prairie grass: ~half lost (re-drop w/ penalty), half hacked out
        return 0.5 * (1.0 + np.interp(dist, DIST, BASELINE["rough"])) + \
            0.5 * np.interp(dist, DIST, BASELINE["recovery"])
    return np.interp(dist, DIST, BASELINE[lie])


# Hazard polygons in screenshot pixels (920 x 2000). Later zones override
# earlier ones; anything not covered is rough.
# Order of precedence: fairway < trees < sand < native < water.
HOLES = {
    1: dict(
        par=4, image="hole01.png",
        tee=(388, 1940), dot270=(483, 978), green=(595, 630),
        zones=[
            ("fairway", [(395, 1300), (560, 1300), (570, 1100), (585, 960), (595, 860),
                         (625, 700), (600, 620), (520, 620), (480, 700), (440, 860),
                         (405, 960), (390, 1100)]),
            ("recovery", [(60, 690), (480, 690), (480, 780), (445, 860), (370, 880),
                          (370, 960), (300, 960), (250, 880), (60, 880)]),   # trees left 270-320
            ("recovery", [(600, 850), (660, 850), (670, 1010), (605, 1010)]),  # trees right 255-300
            ("sand", [(510, 610), (550, 610), (552, 665), (515, 665)]),        # greenside bunker
            ("native", [(165, 1000), (265, 1000), (265, 1350), (180, 1380)]),
            ("native", [(640, 1090), (900, 1150), (900, 1300), (670, 1310)]),
            ("water", [(705, 540), (920, 540), (920, 770), (740, 760)]),       # lake right of green
        ]),
    2: dict(
        par=4, image="hole02.png",
        tee=(363, 1843), dot270=(409, 920), green=(470, 655),
        zones=[
            ("fairway", [(310, 1250), (440, 1250), (450, 1100), (480, 1000), (510, 900),
                         (520, 800), (510, 720), (330, 720), (300, 850), (300, 1000)]),
            ("recovery", [(40, 860), (270, 860), (275, 1350), (40, 1350)]),    # trees left of path
            ("recovery", [(455, 1050), (500, 980), (760, 980), (760, 1850), (460, 1850)]),  # trees right
            ("native", [(525, 640), (650, 640), (640, 1000), (500, 990), (515, 850)]),      # prairie right
            ("sand", [(440, 845), (490, 838), (500, 880), (470, 910), (440, 895)]),         # fairway bunker R
            ("sand", [(385, 640), (420, 640), (420, 720), (385, 720)]),                     # greenside L
            ("sand", [(450, 690), (530, 680), (530, 770), (455, 770)]),                     # greenside R
        ]),
    3: dict(
        par=5, image="hole03.png",
        tee=(476, 1740), dot270=(472, 1008), green=(470, 339),
        zones=[
            ("fairway", [(330, 1450), (480, 1450), (490, 1200), (500, 1050), (520, 950),
                         (560, 800), (600, 650), (460, 600), (400, 800), (340, 1000), (320, 1200)]),
            ("recovery", [(545, 940), (600, 920), (700, 950), (760, 1100), (700, 1500),
                          (600, 1560), (495, 1500), (495, 1250), (505, 1100), (525, 1000)]),  # trees right
            ("native", [(650, 540), (900, 540), (900, 900), (660, 900)]),                     # prairie right
        ]),
    4: dict(
        par=4, image="hole04.png",
        tee=(471, 1822), dot270=(486, 990), green=(492, 710),
        zones=[
            ("fairway", [(420, 1300), (540, 1300), (560, 1100), (575, 900), (580, 720),
                         (400, 720), (400, 900), (410, 1100)]),
            ("recovery", [(520, 1400), (600, 1400), (600, 1650), (520, 1650)]),  # tree line R (short)
            ("sand", [(560, 1700), (630, 1700), (630, 1780), (560, 1780)]),
            ("native", [(200, 550), (370, 550), (365, 900), (200, 900)]),        # prairie long-left
        ]),
    6: dict(
        par=5, image="hole06.png",
        tee=(481, 1890), dot270=(471, 932), green=(465, 147),
        zones=[
            ("fairway", [(330, 1500), (560, 1500), (570, 1100), (580, 900), (590, 540),
                         (310, 540), (305, 800), (310, 1100)]),
            ("recovery", [(595, 940), (680, 940), (690, 1060), (600, 1070)]),    # trees right
            ("recovery", [(560, 1150), (690, 1150), (690, 1360), (560, 1360)]),
            ("sand", [(525, 945), (575, 945), (578, 1030), (528, 1030)]),        # fairway bunker R
            ("native", [(100, 540), (300, 540), (300, 1100), (330, 1300), (370, 1500),
                        (260, 1500), (160, 1200), (100, 1100)]),                 # marsh / prairie strip
            ("water", [(0, 540), (100, 540), (100, 1100), (170, 1500), (250, 2000), (0, 2000)]),  # Mozingo Lake
        ]),
    7: dict(
        par=4, image="hole07.png",
        tee=(445, 1922), dot270=(499, 1045), green=(525, 530),
        zones=[
            ("fairway", [(350, 1500), (600, 1500), (640, 1200), (610, 1050), (570, 900),
                         (540, 700), (470, 700), (440, 900), (400, 1100), (360, 1300)]),
            ("recovery", [(360, 920), (410, 920), (450, 1010), (420, 1090), (370, 1095),
                          (360, 1000)]),                                         # trees left 260-310
            ("recovery", [(580, 950), (635, 950), (640, 1040), (585, 1040)]),    # trees right ~280
            ("native", [(240, 700), (300, 700), (330, 900), (350, 1080), (330, 1300),
                        (300, 1300), (300, 1100), (245, 1000)]),                 # reeds on the shore
            ("water", [(0, 540), (240, 540), (245, 1000), (300, 1100), (320, 1400),
                       (340, 1700), (380, 2000), (0, 2000)]),                    # Mozingo Lake
        ]),
    9: dict(
        par=4, image="hole09.png",
        tee=(469, 1862), dot270=(447, 950), green=(400, 690),
        zones=[
            ("fairway", [(330, 1250), (580, 1250), (640, 1050), (560, 900), (510, 700),
                         (330, 700), (320, 900)]),
            ("native", [(230, 700), (330, 700), (340, 1300), (260, 1300)]),       # reeds left
            ("native", [(560, 780), (700, 780), (790, 1000), (790, 1290), (680, 1290),
                        (640, 1000)]),                                           # prairie right
            ("sand", [(440, 630), (500, 630), (500, 700), (450, 700)]),          # greenside
            ("water", [(0, 540), (250, 540), (270, 800), (260, 1300), (300, 1450),
                       (650, 1460), (650, 1560), (0, 1560)]),                    # lake left + carry
        ]),
    10: dict(
        par=4, image="hole10.png",
        tee=(458, 1785), dot270=(458, 963), green=(450, 600),
        zones=[
            ("fairway", [(340, 1400), (500, 1400), (510, 1100), (530, 900), (520, 650),
                         (380, 650), (330, 850), (320, 1100)]),
            ("recovery", [(560, 880), (640, 900), (700, 1000), (700, 1350), (520, 1350),
                          (510, 1150), (530, 1000)]),                            # trees right
            ("native", [(265, 760), (310, 700), (330, 850), (320, 1100), (330, 1350),
                        (300, 1350), (275, 1050)]),                              # prairie strip left
            ("native", [(580, 540), (680, 540), (680, 880), (600, 880)]),        # prairie long-right
            ("sand", [(480, 595), (510, 595), (510, 660), (480, 660)]),          # greenside
        ]),
    12: dict(
        par=5, image="hole12.png",
        tee=(375, 1660), dot270=(425, 958), green=(900, 530),   # dogleg right; green off-screen
        zones=[
            ("fairway", [(250, 1150), (420, 1150), (440, 1050), (450, 950), (520, 880),
                         (760, 700), (740, 620), (560, 700), (300, 840), (240, 1000)]),
            ("recovery", [(0, 540), (750, 540), (720, 605), (300, 820), (0, 820)]),   # trees through the corner
            ("recovery", [(60, 830), (290, 830), (220, 1040), (240, 1300), (260, 1600),
                          (100, 1600), (60, 1000)]),                                  # tree line left
            ("recovery", [(500, 1020), (550, 1020), (550, 1060), (500, 1060)]),       # lone tree right
            ("sand", [(440, 965), (495, 965), (500, 1040), (445, 1040)]),             # fairway bunker
        ]),
    13: dict(
        par=4, image="hole13.png",
        tee=(480, 1825), dot270=(471, 1040), green=(305, 715),  # dogleg left
        zones=[
            ("fairway", [(420, 1500), (560, 1500), (590, 1250), (560, 1050), (500, 900),
                         (440, 780), (300, 700), (260, 760), (300, 880), (400, 1000), (410, 1200)]),
            ("recovery", [(0, 600), (230, 600), (270, 900), (390, 1000), (395, 1100),
                          (100, 1100), (0, 1000)]),                              # trees left of corner
            ("native", [(100, 1120), (395, 1150), (405, 1500), (410, 1800), (100, 1800)]),
            ("sand", [(340, 700), (370, 700), (370, 760), (340, 760)]),          # greenside
            ("sand", [(265, 770), (295, 770), (295, 820), (265, 820)]),
        ]),
}


def hole_frame(h):
    """Unit vectors + yards-per-pixel so (along, lateral) yds <-> pixels."""
    tee = np.array(h["tee"], float)
    v = np.array(h["dot270"], float) - tee
    px_per_yd = np.linalg.norm(v) / 270.0
    fwd = v / np.linalg.norm(v)
    right = np.array([-fwd[1], fwd[0]])       # golfer's right (screen y points down)
    return tee, fwd, right, px_per_yd


def lie_at(h, pts):
    lie = np.array(["rough"] * len(pts), dtype=object)
    for name, poly in h["zones"]:
        lie[Path(poly).contains_points(pts)] = name
    return lie


def simulate(hole_no, club, aim_lat=0.0, n=N_SHOTS):
    h = HOLES[hole_no]
    tee, fwd, right, ppy = hole_frame(h)
    carry, total, width, depth = CLUBS[club]
    along = RNG.normal(carry, depth / 4, n)
    lat = RNG.normal(aim_lat, width / 4, n)
    pts = tee + (along[:, None] * fwd + lat[:, None] * right) * ppy
    lie = lie_at(h, pts)

    # Roll out along the flight line in 2-yd steps: full roll on fairway,
    # ROUGH_ROLL of it in rough, and the ball stops dead in any hazard.
    heading = (pts - tee) / np.linalg.norm(pts - tee, axis=1)[:, None]
    roll_left = np.full(n, float(total - carry))
    roll_left[lie == "rough"] *= ROUGH_ROLL
    while True:
        moving = (roll_left > 0) & ~np.isin(lie, HAZARDS)
        if not moving.any():
            break
        step = np.minimum(roll_left[moving], 2.0)
        pts[moving] += heading[moving] * (step * ppy)[:, None]
        roll_left[moving] -= step
        new_lie = lie_at(h, pts[moving])
        into_rough = (new_lie == "rough") & (lie[moving] == "fairway")
        idx = np.flatnonzero(moving)
        roll_left[idx[into_rough]] *= ROUGH_ROLL
        lie[moving] = new_lie

    to_green = np.linalg.norm(pts - np.array(h["green"], float), axis=1) / ppy

    strokes = np.empty(n)
    for name in set(lie):
        m = lie == name
        strokes[m] = expected_strokes(name, to_green[m])
    return pts, lie, to_green, 1.0 + strokes   # +1 for the tee shot itself


def best_aim(hole_no, club):
    best = None
    for aim in np.arange(-20, 20.1, 2.5):
        _, lie, to_green, strokes = simulate(hole_no, club, aim)
        ev = strokes.mean()
        if best is None or ev < best["ev"]:
            share = {k: float(np.mean(lie == k)) for k in
                     ("fairway", "rough", "sand", "recovery", "native", "water")}
            best = dict(aim=aim, ev=ev, approach=float(np.median(to_green)), share=share)
    return best


def plot_hole(hole_no, results, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.image import imread

    h = HOLES[hole_no]
    img = imread(os.path.join(HERE, "screenshots", h["image"]))
    fig, ax = plt.subplots(figsize=(4.6, 10))
    ax.imshow(img, extent=(0, 920, 2000, 0))
    colors = {"fairway": "#7CFC00", "recovery": "#8B4513", "sand": "#F5DEB3",
              "native": "#DAA520", "water": "#1E90FF"}
    for name, poly in h["zones"]:
        p = np.array(poly + [poly[0]])
        ax.plot(p[:, 0], p[:, 1], color=colors[name], lw=1.2)
    for club, c in zip(CLUBS, ("#ff3b30", "#ffcc00", "#00e5ff")):
        pts, *_ = simulate(hole_no, club, results[club]["aim"], n=400)
        ax.scatter(pts[:, 0], pts[:, 1], s=2, color=c, alpha=0.6, label=club)
    ax.set_xlim(0, 920)
    ax.set_ylim(2000, 540)
    ax.axis("off")
    ax.legend(loc="lower left", fontsize=7)
    ax.set_title(f"Hole {hole_no} (par {h['par']})", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def main():
    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    lines = ["| Hole | Par | Club | Aim (yds, +R) | Approach left | Fairway | Rough | Sand | Trees | Native | Water | Exp. score | vs best |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    picks = []
    for hole_no, h in HOLES.items():
        results = {club: best_aim(hole_no, club) for club in CLUBS}
        best_ev = min(r["ev"] for r in results.values())
        best_club = min(results, key=lambda c: results[c]["ev"])
        picks.append((hole_no, best_club, results[best_club]["aim"]))
        for club, r in results.items():
            s = r["share"]
            mark = " **<- play**" if club == best_club else ""
            lines.append(
                f"| {hole_no} | {h['par']} | {club}{mark} | {r['aim']:+.1f} | {r['approach']:.0f} | "
                f"{s['fairway']:.0%} | {s['rough']:.0%} | {s['sand']:.0%} | {s['recovery']:.0%} | "
                f"{s['native']:.0%} | {s['water']:.0%} | {r['ev']:.3f} | {r['ev'] - best_ev:+.3f} |")
        plot_hole(hole_no, results, os.path.join(out_dir, f"hole{hole_no:02d}_patterns.png"))
    table = "\n".join(lines)
    print(table)
    with open(os.path.join(out_dir, "results_table.md"), "w") as f:
        f.write(table + "\n")
    print()
    for hole_no, club, aim in picks:
        side = "on the app line" if aim == 0 else f"{abs(aim):.1f} yds {'right' if aim > 0 else 'left'} of the app line"
        print(f"Hole {hole_no}: {club}, aim {side}")


if __name__ == "__main__":
    main()
