"""Build the Mozingo Lake strategy book (PDF): one page per hole, 1-18.

  python3 mozingo/yardage_book.py   -> output/Mozingo_Lake_Strategy.pdf

Par 4/5: club + aim from tee_strategy.py. The aim zone is every aim that
scores within ZONE_TOL strokes of the best aim. Confidence comes from
output/stats_report.md (run stats.py first).

Par 3: DECADE edge rule. Aim (distance / 20) yds in from an edge, plus
WATER_ADD for water, BUNKER_ADD for a bunker and TREE_ADD for trees/tall grass.
Where the two sides' numbers overlap, aim at the point that splits them.
"""
import functools
import os
import re
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.image import imread
import tee_strategy as t

# Course being built; use_course() swaps these for another course.
NAME = "Mozingo Lake GC"
DIR = t.HERE                      # holds screenshots/ and output/
PREFIX = "Mozingo"                # output file names
STRATEGY_NAME = "Mozingo_Lake_Strategy.pdf"
ORDER = list(range(1, 19))
LABELS = {}                       # hole key -> what to print ("9 back tee")
ZONE_TOL = 0.02
WATER_ADD, BUNKER_ADD, TREE_ADD = 3.0, 1.0, 2.0
# DECADE edge modifiers (from the DECADE card): added to the baseline target number.
#  3 water/OB, 2 trees/tall grass/bad slope, 1 bunker, 0 rough, -2 a safe side with
#  short grass / room to run off ("runoff").
ADD = {"water": WATER_ADD, "ob": WATER_ADD, "bunker": BUNKER_ADD, "trees": TREE_ADD,
       "native": TREE_ADD, "rough": 0.0, "runoff": -2.0}
# "Lesser of evils": when both cushions don't fit, the worse side keeps its full cushion.
SEVERITY = {"water": 3, "ob": 3, "trees": 2, "native": 2, "bunker": 1, "rough": 0, "runoff": -1}
# DECADE baseline target: yds in from the nearest edge, by distance (card, 60-250 yds).
TARGET = {60: 3, 70: 4, 80: 4, 90: 5, 100: 5, 110: 6, 120: 6, 130: 7, 140: 7, 150: 8, 160: 8,
          170: 9, 180: 9, 190: 10, 200: 10, 210: 11, 220: 11, 230: 12, 240: 12, 250: 13}
# Wind modifier added to every edge: under 5 mph -1, 5-10 0, 10-20 +1, 20-30 +2, 30+ +3.
WIND = {"under 5 mph": -1, "5-10 mph": 0, "10-20 mph": 1, "20-30 mph": 2, "30+ mph": 3}
WIND_NOW = 0                                 # books are printed for a 5-10 mph day


def baseline_target(dist):
    d = int(round(min(max(dist, 60), 250) / 10.0) * 10)
    return float(TARGET[d])


def label(h):
    return LABELS.get(h, str(h))


def use_course(name, dir, prefix, holes, par3, notes, aim_at, order, labels=None):
    global NAME, DIR, PREFIX, STRATEGY_NAME, ORDER, LABELS, PAR3, NOTES, AIM_AT
    NAME, DIR, PREFIX, ORDER, LABELS = name, dir, prefix, order, labels or {}
    STRATEGY_NAME = f"{prefix}_Strategy.pdf"
    PAR3, NOTES, AIM_AT = par3, notes, aim_at
    t.HOLES = holes
    tee_plan.cache_clear()

# Par 3s, traced from the Caddie-view screenshots on a 5-yd grid centred on the flag.
# green = putting-surface outline as (yds right of the tee-flag line, yds past the flag);
# it matches the app's front/back numbers on the line. haz = what sits off each edge.
PAR3 = {
    5: dict(image="hole05.png", short="Bunker hard right, trees left. Narrow green.", tee=(438, 1818), flag=(438, 922), center=182, front=166, back=199,
            green=[(-6, 17), (2, 17), (6, 14), (8, 10), (9.5, 3), (9, -5), (8, -10), (5, -15),
                   (0, -16.5), (-5, -15), (-8, -10), (-12, -5), (-15, 0), (-14, 6), (-11, 11), (-8, 15)],
            haz=dict(left="trees", right="bunker", short="rough", long="rough"),
            note="Bunker hard right (2 yds off the edge), front-left bunker and trees left. "
                 "The green is only ~24 yds wide, so the zone is a narrow strip."),
    8: dict(image="hole08.png", short="All carry. Water short keeps its full cushion.", tee=(475, 1950), flag=(475, 812), center=187, front=180, back=199,
            green=[(-14, 10), (-8, 13), (5, 13), (15, 12), (22, 9), (25, 3), (26, -2), (22, -5),
                   (10, -5.5), (0, -6.5), (-4, -7), (-6, -14), (-10, -20), (-15, -21), (-20, -15),
                   (-22.5, -8), (-22.5, 0), (-19, 6)],
            haz=dict(left="rough", right="trees", short="water", long="trees"),
            note="All carry over the pond, bunker front-right. The green is too shallow for both the "
                 "water cushion short and the trees cushion long, so water wins: the box sits "
                 "13 yds past the front edge. Left of the green is only rough."),
    11: dict(image="hole11.png", short="Pond short-left. The miss is long-right.", tee=(444, 1765), flag=(444, 802), center=219, front=208, back=230,
             green=[(-15, 10), (-5, 11.5), (5, 11.5), (14, 10), (19, 6), (20.5, 0), (18, -5),
                    (12, -9), (0, -11), (-10, -10), (-17, -7), (-21, -2), (-21.5, 3), (-19, 7)],
             haz=dict(left="water", right="rough", short="water", long="bunker"),
             note="Pond short and short-left. Right of the green is grass, so the miss is "
                  "long-right, never short-left."),
    15: dict(image="hole15.png", short="Lake right, bunker front-left.", tee=(500, 1873), flag=(471, 806), center=174, front=164, back=189,
             green=[(-15, 14), (0, 15), (12, 14.5), (20, 12), (22, 5), (20, -3), (14, -8), (5, -11),
                    (-2, -11), (-5, -8), (-8, -3), (-12, 2), (-15, 8)],
             haz=dict(left="bunker", right="water", short="rough", long="rough"),
             note="Lake off the right edge, bunker front-left. Triangular green, widest at the back."),
}

NOTES = {
    1: "2-wood is equal (0.006 apart). Driver brings the tree clumps at 270-320 into play.",
    2: "Driver carries 275, right onto the fairway bunker at 273-294 R. If driver is carrying "
       "290+ (downwind) it flies the bunker and becomes the play.",
    3: "Narrow: tall grass left of the landing zone (~25 yds left of the line, 220-340 out) and trees "
       "all down the right. Aim straight down the middle; every 5 yds left of the line costs ~0.03.",
    4: "Wide open. Left prairie (~40 yds left at 300+) is only in play if your driver is ~90 yds wide.",
    6: "Lake is ~100 yds left, out of play. Driver is worth 0.12-0.17 here.",
    7: "Only if the tree clumps at 260-310 really block you. If you can usually play out of "
       "them, driver wins by 0.03 instead.",
    9: "Reeds left and prairie right are both 30+ yds off the line. Driver leaves ~54.",
    10: "Trees down the right, so aim a touch left.",
    12: "Trees through the dogleg are ~345 out, unreachable. Driver flies the fairway bunker "
        "(240-270) that catches more 2-woods.",
    13: "Coin flip (within 0.005). Driver on good driving days, 4-wood otherwise. Never aim left of "
        "the line: each 5 yds left costs 0.02-0.03.",
    14: "Pond at 327-363 is out of reach. Driver to set up the second.",
    16: "Three-way tie. Scattered trees on both sides at 270-300 and the lake further right.",
    17: "Aim at the LEFT half of the upper fairway. Tall-grass island 206-276 sits under the app "
        "line. Into wind (driver carry ~262): 2-wood/4-wood aimed even further left. "
        "Iron lay-up costs ~0.19.",
    18: "Downhill: ~+20 yds of run (stops dead at trees). Marsh starts ~330 on the line, ~315 on the "
        "right. Firm/fast (+30): coin flip with 2-wood 5 L.",
}


def confidence():
    path = os.path.join(DIR, "output", "stats_report.md")
    conf = {}
    if os.path.exists(path):
        for line in open(path):
            m = re.match(r"\| (\S+?) \| \*\*(.+?)\*\* \|.*\| (\d+)% \|$", line.strip())
            if m:
                key = int(m.group(1)) if m.group(1).isdigit() else m.group(1)
                conf[key] = int(m.group(3))
    return conf


def side(yds):
    if abs(yds) < 1.25:
        return "on the app line"
    return f"{abs(yds):.0f} yds {'right' if yds > 0 else 'left'}"


def flag_side(yds):
    return "straight at the flag" if abs(yds) < 1.25 else f"{side(yds)} of the flag"


@functools.lru_cache(maxsize=None)
def tee_plan(h):
    res = {c: t.best_aim(h, c, aims=t.AIMS_WIDE if c in t.IRONS else t.AIMS) for c in t.clubs_for(h)}
    best = min(res, key=lambda c: res[c]["ev"])
    lo = t.HOLES[h].get("aim_min", -20)
    aims = np.arange(lo, t.HOLES[h].get("aim_max", 20) + 0.1, 2.5)
    curve = np.array([t.simulate(h, best, a)[3].mean() for a in aims])
    ok = aims[curve <= curve.min() + ZONE_TOL]
    return res, best, (ok.min(), ok.max())


def _axis(e_lo, e_hi, c_lo, c_hi, s_lo, s_hi):
    """One axis of the edge rule. Returns (zone_lo, zone_hi, how)."""
    if c_lo + c_hi <= e_hi - e_lo:
        return e_lo + c_lo, e_hi - c_hi, "fits"
    if s_lo == s_hi:                          # equal trouble: split the room by the two edge numbers
        x = e_lo + (e_hi - e_lo) * c_lo / (c_lo + c_hi)
        return x, x, "split"
    x = e_lo + c_lo if s_lo > s_hi else e_hi - c_hi     # worse side keeps its full cushion
    return x, x, "lo" if s_lo > s_hi else "hi"


def par3_plan(p, step=0.25):
    """DECADE edge rule on the traced green.

    Cushion = DECADE baseline target for the distance (card table, ~distance/20)
    yds in from each edge, +3 water/OB, +2 trees/tall grass, +1 bunker, -2 a safe
    runoff side. On each axis: if both cushions fit, the zone is what's left between
    them. If not, the worse side (water > trees/tall grass > bunker > rough) keeps
    its full cushion and the lesser side gives up room; with the same trouble both
    sides (e.g. a small green with no hazards) the aim splits them, i.e. the middle.
    """
    from matplotlib.path import Path
    base = baseline_target(p["center"]) + WIND_NOW
    off = {k: max(base + ADD[v], 0.0) for k, v in p["haz"].items()}
    sev = {k: SEVERITY[v] for k, v in p["haz"].items()}
    path = Path(p["green"])
    g = np.array(p["green"], float)

    def extent(axis, at):
        """Green edges along a line: axis 0 = lateral (row at depth `at`), 1 = depth (column)."""
        span = np.arange(-60, 60 + step, step)
        pts = np.c_[span, np.full_like(span, at)] if axis == 0 else np.c_[np.full_like(span, at), span]
        inside = span[path.contains_points(pts)]
        return (inside.min(), inside.max()) if len(inside) else (0.0, 0.0)

    lat_c = (g[:, 0].min() + g[:, 0].max()) / 2
    dep_c = (g[:, 1].min() + g[:, 1].max()) / 2
    for _ in range(3):                        # settle the two axes on each other
        f, b_ = extent(1, lat_c)
        d0, d1, how_d = _axis(f, b_, off["short"], off["long"], sev["short"], sev["long"])
        dep_c = (d0 + d1) / 2
        l, r = extent(0, dep_c)
        l0, l1, how_l = _axis(l, r, off["left"], off["right"], sev["left"], sev["right"])
        lat_c = (l0 + l1) / 2
    return dict(base=base, off=off, sev=sev, lat=(l0, l1), dep=(d0, d1), how_lat=how_l,
                how_dep=how_d, edges_lat=(l, r), edges_dep=(f, b_), aim=(lat_c, dep_c))


def frame(tee, toward, yds):
    tee = np.array(tee, float)
    v = np.array(toward, float) - tee
    ppy = np.linalg.norm(v) / yds
    fwd = v / np.linalg.norm(v)
    return tee, fwd, np.array([-fwd[1], fwd[0]]), ppy


def px(fr, along, lat):
    tee, fwd, right, ppy = fr
    return tee + (along * fwd + lat * right) * ppy


def draw_image(ax, image):
    clean = os.path.join(DIR, "screenshots_clean", image)          # app overlays removed
    img = imread(clean if os.path.exists(clean) else os.path.join(DIR, "screenshots", image))
    ax.imshow(img, extent=(0, 920, 2000, 0))
    ax.axis("off")


def finish(ax):
    ax.set_xlim(0, 920)
    ax.set_ylim(2000, 540)


def display_hole(hd):
    """A hole may carry 'display' = another screenshot of the same tee line (e.g. zoomed out to show
    the tee): map tee/dot270 onto it so everything drawn from the frame lands on that image."""
    dsp = hd.get("display")
    if not dsp:
        return hd
    if "M" in dsp:                                  # image-matched 2x3 similarity transform
        M = np.asarray(dsp["M"], float)
        m = lambda p: tuple(M[:, :2] @ np.asarray(p, float) + M[:, 2])
    else:
        (a, b), (c, d) = [complex(*q) for q in dsp["src"]], [complex(*q) for q in dsp["dst"]]
        m = lambda p: (lambda w: (w.real, w.imag))(c + (d - c) / (b - a) * (complex(*p) - a))
    return dict(hd, image=dsp["image"], tee=m(hd["tee"]), dot270=m(hd["dot270"]))


def shot_cloud(h, club, aim, n=4000):
    """Centre (along, lat yds) and 95% ellipse axes of the simulated finishing spots."""
    try:
        pts = t.simulate(h, club, aim, n=n)[0]
    except Exception:
        return None
    hd = t.HOLES[h]
    tee, fwd, right, ppy = t.hole_frame(hd)
    rel = (np.asarray(pts, float) - tee) / ppy
    xy = np.c_[rel @ fwd, rel @ right]
    mu = np.median(xy, axis=0)
    cov = np.cov((xy - mu).T)
    w, v = np.linalg.eigh(cov)
    k = 2.4477                                     # sqrt(chi2_2(0.95))
    return dict(along=float(mu[0]), lat=float(mu[1]), axes=(k * np.sqrt(w[1]), k * np.sqrt(w[0])),
                vec=(v[:, 1], v[:, 0]))


def cloud_point(cl, a):
    (A, Bm), (u, w) = cl["axes"], cl["vec"]
    d = A * np.cos(a) * u + Bm * np.sin(a) * w
    return cl["along"] + d[0], cl["lat"] + d[1]


def draw_tee(ax, h, club, aim, zone, label=None):
    hd = display_hole(t.HOLES[h])
    draw_image(ax, hd["image"])
    fr = frame(hd["tee"], hd["dot270"], 270)
    carry, total, width, depth = {**t.CLUBS, **t.IRONS}[club]
    total += hd.get("extra_roll", 0)
    th = np.linspace(0, 2 * np.pi, 80)
    cl = shot_cloud(h, club, aim)
    if cl:      # 95% ellipse of where the model's simulated shots actually finish (elevation, slope, roll)
        ell = np.array([px(fr, *cloud_point(cl, a)) for a in th])
        total, aim_end = cl["along"], cl["lat"]
    else:
        ell = np.array([px(fr, total + depth / 2 * np.sin(a), aim + width / 2 * np.cos(a)) for a in th])
    ax.fill(ell[:, 0], ell[:, 1], color="#ffd60a", alpha=0.18, lw=0)
    ax.plot(ell[:, 0], ell[:, 1], color="#ffd60a", lw=1.2, ls="--")
    z = np.array([px(fr, total, zone[0]), px(fr, total, zone[1])])
    ax.plot(z[:, 0], z[:, 1], color="#00e5ff", lw=9, alpha=0.75, solid_capstyle="butt")
    tee = px(fr, 0, 0)
    tgt = px(fr, total, aim)
    ax.plot([tee[0], tgt[0]], [tee[1], tgt[1]], color="#ffd60a", lw=2)
    # precise aim marker: crosshair + ringed dot whose centre is exactly the aim point
    r_ = 26                                                       # crosshair half-length, frame px
    for d in (fwd_ := (tgt - tee) / np.linalg.norm(tgt - tee), np.array([-fwd_[1], fwd_[0]])):
        a_, b_ = tgt - d * r_, tgt + d * r_
        ax.plot([a_[0], b_[0]], [a_[1], b_[1]], color="black", lw=3.2, zorder=7, solid_capstyle="butt")
        ax.plot([a_[0], b_[0]], [a_[1], b_[1]], color="#ffd60a", lw=1.4, zorder=8, solid_capstyle="butt")
    ax.plot(*tgt, marker="o", ms=11, mfc="none", mec="black", mew=3.0, zorder=9)
    ax.plot(*tgt, marker="o", ms=11, mfc="none", mec="#ffd60a", mew=1.4, zorder=10)
    ax.plot(*tgt, marker="o", ms=2.6, color="#e5202a", mec="black", mew=0.6, zorder=11)
    ax.annotate(label or f"AIM  {club}\n{side(aim)}", tgt, xytext=(16, 8), textcoords="offset points",
                color="black", fontsize=9, weight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffd60a", ec="black", lw=0.8))
    finish(ax)


def draw_green(ax, p, plan, title=None, aspect=None):
    """Green-only close-up: traced outline and the rule box. No star."""
    draw_image(ax, p["image"])
    fr = frame(p["tee"], p["flag"], p["center"])
    tee, fwd, right, ppy = fr

    def to_px(lat, dep):
        return tee + ((p["center"] + dep) * fwd + lat * right) * ppy

    (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
    if l1 - l0 < 2:                           # a single aim line: draw it 2 yds wide so it shows
        l0, l1 = (l0 + l1) / 2 - 1, (l0 + l1) / 2 + 1
    if d1 - d0 < 2:
        d0, d1 = (d0 + d1) / 2 - 1, (d0 + d1) / 2 + 1
    box = np.array([to_px(l0, d0), to_px(l1, d0), to_px(l1, d1), to_px(l0, d1), to_px(l0, d0)])
    ax.fill(box[:, 0], box[:, 1], color="#00e5ff", alpha=0.55, lw=0, zorder=5)
    ax.plot(box[:, 0], box[:, 1], color="#00e5ff", lw=2.5, zorder=6)
    g = np.array(p["green"] + [p["green"][0]], float)
    gp = np.array([to_px(a_, b_) for a_, b_ in g])
    gx, gy = gp[:, 0], gp[:, 1]
    ax.plot(gx, gy, color="white", lw=1.2, ls="--", zorder=4)
    pad = 10 * ppy
    x0, x1, y0, y1 = gx.min() - pad, gx.max() + pad, gy.min() - pad, gy.max() + pad
    if aspect:                                 # grow the view to fill the axes (h / w)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        w, h = x1 - x0, y1 - y0
        if h / w < aspect:
            h = w * aspect
        else:
            w = h / aspect
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    if title:
        ax.set_title(title, fontsize=10)


def text_block(fig, x, y, lines, size=10, gap=0.021, width=44):
    for ln in lines:
        bold = ln.startswith("**")
        ln = ln.strip("*")
        for i, piece in enumerate(textwrap.wrap(ln, width) or [""]):
            fig.text(x, y, piece, fontsize=size, weight="bold" if bold else "normal", va="top")
            y -= gap
    return y


def header(fig, h, par, yds):
    fig.patches.append(plt.Rectangle((0, 0.94), 1, 0.06, transform=fig.transFigure,
                                     color="#1f5130", zorder=-1))
    fig.text(0.04, 0.97, f"Hole {label(h)}", fontsize=24 if h in ORDER and len(label(h)) < 4 else 18,
             weight="bold", color="white", va="center")
    fig.text(0.42 if len(label(h)) > 3 else 0.30, 0.97, f"Par {par}  ·  {yds} yds", fontsize=15,
             color="white", va="center")
    fig.text(0.96, 0.97, NAME, fontsize=11, color="#cfe8d5", va="center", ha="right")


def tee_page(pdf, h, conf):
    hd = t.HOLES[h]
    res, best, zone = tee_plan(h)
    r = res[best]
    others = sorted((c for c in res if c != best), key=lambda c: res[c]["ev"])
    fig = plt.figure(figsize=(8.5, 11))
    header(fig, h, hd["par"], hd["length"])
    draw_tee(fig.add_axes([0.02, 0.03, 0.52, 0.89]), h, best, r["aim"], zone)
    carry, total, *_ = {**t.CLUBS, **t.IRONS}[best]
    lines = [
        f"**PLAY: {best.upper()}",
        f"**Aim: {side(r['aim'])} of the app line",
        f"Aim zone: {side(zone[0])} to {side(zone[1])} (every aim in the blue band "
        f"is within {ZONE_TOL} strokes of the best)",
        f"Carry {carry} / ~{total + hd.get('extra_roll', 0)} total",
        "",
        "**Expected outcome",
        f"Fairway {r['share']['fairway']:.0%}  ·  rough {r['share']['rough']:.0%}",
        f"Trees {r['share']['recovery']:.0%}  ·  sand {r['share']['sand']:.0%}  ·  "
        f"tall grass {r['share']['native']:.0%}  ·  water/OB {r['share']['water'] + r['share']['ob']:.0%}",
        f"Approach left: ~{r['approach']:.0f} yds",
        f"Strokes gained off the tee: {t.tee_baseline(h) - r['ev']:+.2f}",
        f"Edge over {others[0]}: {res[others[0]]['ev'] - r['ev']:.3f} strokes",
        *([f"Confidence: best club in {conf[h]}% of what-if worlds"] if h in conf else []),
        "",
        "**Other clubs (strokes lost vs the play)",
    ]
    for c in others:
        lines.append(f"{c}: +{res[c]['ev'] - r['ev']:.3f}  (aim {side(res[c]['aim'])}, "
                     f"fairway {res[c]['share']['fairway']:.0%}, ~{res[c]['approach']:.0f} in)")
    lines += ["", "**Notes", NOTES.get(h, "")]
    text_block(fig, 0.57, 0.90, lines)
    fig.text(0.57, 0.035, "Crosshair dot = exact aim point.  Dashed oval = 95% shot pattern.\n"
             "Blue band = aim zone.", fontsize=8, color="#555")
    pdf.savefig(fig)
    plt.close(fig)
    return dict(hole=label(h), par=hd["par"], yds=hd["length"], club=best, aim=side(r["aim"]),
                zone=f"{side(zone[0])} to {side(zone[1])}", conf=conf.get(h))


def par3_summary(p, plan):
    d0, d1 = (p["center"] + plan["dep"][0], p["center"] + plan["dep"][1])
    play = p["center"] + plan["aim"][1]
    return play, d0, d1


def _how(plan, axis, lo_name, hi_name, p):
    how = plan["how_lat" if axis == "lat" else "how_dep"]
    lo_h, hi_h = p["haz"][lo_name], p["haz"][hi_name]
    if how == "fits":
        return f"{lo_name.capitalize()}/{hi_name}: both cushions fit, the box is the room left between them."
    if how == "split":
        return (f"{lo_name.capitalize()}/{hi_name}: not enough room for both and the trouble is equal "
                f"({lo_h} / {hi_h}), so the room is split in proportion to the two edge numbers.")
    worse, lesser = (lo_name, hi_name) if how == "lo" else (hi_name, lo_name)
    return (f"{lo_name.capitalize()}/{hi_name}: not enough room for both. {worse.capitalize()} "
            f"({p['haz'][worse]}) is the worse miss, so it keeps its full "
            f"{plan['off'][worse]:.1f} yds and the {lesser} side ({p['haz'][lesser]}) gives up room.")


def par3_page(pdf, h):
    p = PAR3[h]
    plan = par3_plan(p)
    play, d0, d1 = par3_summary(p, plan)
    fig = plt.figure(figsize=(8.5, 11))
    header(fig, h, 3, p["center"])
    draw_green(fig.add_axes([0.03, 0.40, 0.94, 0.52]), p, plan, aspect=0.52 * 11 / (0.94 * 8.5))
    off = plan["off"]
    dz = f"{d0:.0f}" if d1 - d0 < 1 else f"{d0:.0f}-{d1:.0f}"
    lines = [
        f"**PLAY {play:.0f} YDS — land it in the blue box",
        f"Box: {dz} yds.  Green (app): front {p['front']} · centre {p['center']} · back {p['back']}.  "
        "Dashed white line = the green as traced.",
        "",
        f"**DECADE target for {p['center']} yds: {plan['base']:.0f} yds in from each edge "
        "(+3 water/OB, +2 trees/tall grass, +1 bunker, -2 safe runoff)",
        "Wind: add 1 yd to every edge at 10-20 mph, 2 at 20-30, 3 at 30+; take 1 off under 5 mph.",
    ]
    for k in ("left", "right", "short", "long"):
        lines.append(f"{k.capitalize()} edge: {p['haz'][k]} → {off[k]:.1f} yds in")
    lines += [_how(plan, "lat", "left", "right", p), _how(plan, "dep", "short", "long", p)]
    lines += ["", "**Notes", p["note"]]
    text_block(fig, 0.05, 0.37, lines, width=95)
    pdf.savefig(fig)
    plt.close(fig)
    return dict(hole=label(h), par=3, yds=p["center"], club=f"Play {play:.0f}",
                aim="Blue box on the green", zone=f"{dz} yds", conf=None)


AIM_AT = {
    1: "Centre of the fairway",
    2: "Left-centre of the fairway, away from the right-side bunker",
    3: "Middle of the fairway, between the tall grass left and the trees right",
    4: "Centre of the fairway",
    5: "Just left of the flag",
    6: "Left-centre of the fairway",
    7: "Right-centre of the fairway, between the tree clumps",
    8: "Just left of the flag, middle-to-back of the green",
    9: "Centre of the fairway",
    10: "Left-centre of the fairway (trees right)",
    11: "At the flag, middle-to-back. Long-right is the safe miss",
    12: "Centre of the fairway",
    13: "Centre to right-centre of the fairway",
    14: "Right-centre of the fairway",
    15: "At the flag",
    16: "Left-centre of the fairway",
    17: "Left half of the upper fairway, left of the tall-grass island",
    18: "Left edge of the fairway, away from the trees and marsh",
}


def aim_sheet(pdf, h):
    """Phone-friendly page: just the screenshot, the aim dot, and one line of words."""
    fig = plt.figure(figsize=(6, 10.4))
    if h in PAR3:
        p = PAR3[h]
        plan = par3_plan(p)
        play, d0, d1 = par3_summary(p, plan)
        title, par = f"PLAY {play:.0f} YDS", 3
        draw_green(fig.add_axes([0, 0, 1, 0.89]), p, plan, aspect=0.89 * 10.4 / 6)
    else:
        res, best, zone = tee_plan(h)
        title, par = best.upper(), t.HOLES[h]["par"]
        draw_tee(fig.add_axes([0, 0, 1, 0.89]), h, best, res[best]["aim"], zone, label="AIM HERE")
    fig.patches.append(plt.Rectangle((0, 0.89), 1, 0.11, transform=fig.transFigure,
                                     color="#1f5130", zorder=-1))
    fig.text(0.04, 0.965, f"Hole {label(h)}", fontsize=22 if len(label(h)) < 4 else 16,
             weight="bold", color="white", va="center")
    fig.text(0.52 if len(label(h)) > 3 else 0.40, 0.965, f"Par {par}", fontsize=13, color="#cfe8d5", va="center")
    fig.text(0.96, 0.965, title, fontsize=20, weight="bold", color="#ffd60a", va="center", ha="right")
    line = ("Land it in the blue box. " + PAR3[h]["short"]) if h in PAR3 else "Aim at the dot. " + AIM_AT[h]
    for i, piece in enumerate(textwrap.wrap(line, 60)[:2]):
        fig.text(0.04, 0.925 - i * 0.022, piece, fontsize=11, color="white", va="center")
    pdf.savefig(fig)
    plt.close(fig)


def cover(pdf, rows):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patches.append(plt.Rectangle((0, 0.90), 1, 0.10, transform=fig.transFigure,
                                     color="#1f5130", zorder=-1))
    fig.text(0.05, 0.955, f"{NAME} — Strategy Card", fontsize=22, weight="bold",
             color="white", va="center")
    fig.text(0.05, 0.915, "Driver 275/300 (65 wide) · 2-wood 265/280 (60) · 4-wood 255/270 (50)",
             fontsize=11, color="#cfe8d5", va="center")
    ax = fig.add_axes([0.04, 0.22, 0.92, 0.65])
    ax.axis("off")
    cells = [[r["hole"], r["par"], r["yds"], r["club"], r["aim"], r["zone"],
              "" if r["conf"] is None else f"{r['conf']}%"] for r in rows]
    tb = ax.table(cellText=cells, colLabels=["Hole", "Par", "Yds", "Play", "Aim", "Zone",
                                             "Confidence"],
                  loc="upper center", cellLoc="center",
                  colWidths=[0.07, 0.06, 0.07, 0.15, 0.22, 0.31, 0.12])
    tb.auto_set_font_size(False)
    tb.set_fontsize(9.5)
    tb.scale(1, 1.75)
    for (i, j), c in tb.get_celld().items():
        if i == 0:
            c.set_facecolor("#1f5130")
            c.set_text_props(color="white", weight="bold")
        elif i % 2 == 0:
            c.set_facecolor("#eef5ef")
    text_block(fig, 0.05, 0.20, [
        "**How to read this",
        "Par 4/5: club and aim from 20,000 simulated tee shots per club, scored with "
        "strokes-gained baselines. Aims are yards left/right of the GPS app's tee line. "
        "Zone = any aim within 0.02 strokes of the best. Confidence = how often the club "
        "stayed best across 100 'what if my inputs are off' scenarios (dispersion, carry, "
        "roll, hazard edges, how penal trees/grass are).",
        "Par 3: DECADE target table (e.g. 160 = 8 yds, 180 = 9, 200 = 10 in from the nearest "
        "edge), +3 water/OB, +2 trees/tall grass, +1 bunker, -2 safe runoff; wind adds 1-3. If "
        "both sides don't fit, the worse miss keeps its full cushion; equal trouble splits the "
        "room in proportion to the two numbers.",
        "Locks (95%+): " + (", ".join(str(r["hole"]) for r in rows if (r["conf"] or 0) >= 95) or "none")
        + ".  Coin flips (under 50%): "
        + (", ".join(str(r["hole"]) for r in rows if r["conf"] is not None and r["conf"] < 50) or "none")
        + ".",
    ], size=9, gap=0.017, width=105)
    pdf.savefig(fig)
    plt.close(fig)


def build():
    conf = confidence()
    rows = []
    # render hole pages once to a throwaway PDF so the cover can summarise them;
    # tee_plan is cached, so the second pass is just drawing
    with PdfPages(os.devnull) as tmp:
        for h in ORDER:
            rows.append(par3_page(tmp, h) if h in PAR3 else tee_page(tmp, h, conf))
            print("hole", label(h), "done", flush=True)
    out = os.path.join(DIR, "output", STRATEGY_NAME)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with PdfPages(out) as pdf:
        cover(pdf, rows)
        for h in ORDER:
            if h in PAR3:
                par3_page(pdf, h)
            else:
                tee_page(pdf, h, conf)
    print("wrote", out)
    sheets = os.path.join(DIR, "output", f"{PREFIX}_Aim_Sheets.pdf")
    with PdfPages(sheets) as pdf:
        for h in ORDER:
            aim_sheet(pdf, h)
    print("wrote", sheets)
    return rows


main = build


if __name__ == "__main__":
    main()
