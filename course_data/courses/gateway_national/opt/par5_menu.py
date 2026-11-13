"""Gateway par 5s: the second-shot MENU for the page's "Second shot" mode (PAR5.md, section "The menu").

  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par5_menu.py solve --which truth --day sat
  ... --which truth --day sun ; --which truth_middle --day sat ; --which truth_middle --day sun     (one process each)
  python3 course_data/courses/gateway_national/opt/par5_menu.py page        -> gateway_national/par5_menu.json

For each par 5, base tee map (truth = Back, truth_middle = Middle) and forecast day:
  * starts: every 10 yds from 180 to 340 to the middle of the green ON THE HOLE'S LINE OF PLAY (the middle of the
    widest strip of fairway at that distance, not the straight tee-green line), and where the Driver and the 2-wood
    finish from each tee set (par5_second results); each from a fairway lie and from rough;
  * rows: every club off the deck at its own best direction (par5_second.play: same swings, map, pricing), labelled
    go (1 ball in 10 or more finishes on the green, or 15 % carry the front edge) or lay-up, with its strokes, where it
    finishes, what it leaves, shares and the pattern's size.
Coordinates are yds from the base tee along the tee line and yds right of it (the page's frame).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import par5_second as P5                                   # noqa: E402

GW = os.path.dirname(HERE)
OUT = os.path.join(HERE, "results")
PAGE = os.path.join(GW, "par5_menu.json")
DIST = list(range(180, 341, 10))
SETS_OF = {"truth": ["Back", "The Tips", "Champions"], "truth_middle": ["Middle"]}
BASE_NAME = {"truth": "Back", "truth_middle": "Middle"}
KEEP = 0.60            # rows within this many strokes of the best
N = 2500


def line_of_play(Wd, Rb, F, d):
    """(along, lateral, has_fairway) of the middle of the widest fairway strip d yds from the middle of the green."""
    M = Wd.M
    fw = np.isin(Rb.lie, [M.CODE["fairway"], M.CODE["first_cut"]]) & ~F.ongreen
    # this hole's corridor only (the map carries the neighbours' fairways): within 45 yds of the line that runs up
    # the tee line and bends to the green over the last 280 yds
    ref = F.green[1] * np.clip((Rb.AA - (F.green[0] - 280.0)) / 280.0, 0.0, 1.0)
    ring = (np.abs(Rb.dist - d) <= 1.0) & (Rb.AA < F.green[0] - 0.5 * d) & (np.abs(Rb.LL - ref) <= 45.0)
    m = ring & fw
    if m.sum() >= 6:
        a, l = Rb.AA[m], Rb.LL[m]
        o = np.argsort(l)
        a, l = a[o], l[o]
        cut = np.nonzero(np.diff(l) > 6.0)[0]
        segs = np.split(np.arange(len(l)), cut + 1)
        s = max(segs, key=lambda q: l[q[-1]] - l[q[0]])
        if l[s[-1]] - l[s[0]] >= 8:
            mid = 0.5 * (l[s[0]] + l[s[-1]])
            k = s[int(np.argmin(np.abs(l[s] - mid)))]
            return float(a[k]), float(l[k]), True
    return None


def row_stats(Wd, F, res, o):
    M = Wd.M
    a0, l0, d_front = res["a0"], res["l0"], res["d_front"]
    sm = np.convolve(o["ev"], [0.25, 0.5, 0.25], mode="same")
    sm[0], sm[-1] = o["ev"][0], o["ev"][-1]
    j = int(np.argmin(sm))
    th = np.radians(res["th0"] + P5.ANG[j])
    u = np.array([np.cos(th), np.sin(th)])
    v = np.array([-np.sin(th), np.cos(th)])
    a, l, code = o["a"][:, j], o["l"][:, j], o["code"][:, j]
    al = (a - a0) * u[0] + (l - l0) * u[1]
    cr = (a - a0) * v[0] + (l - l0) * v[1]
    solid = al > np.median(al) - 25
    ca, cc = float(np.median(al[solid])), float(np.median(cr[solid]))
    on = F.ongreen[F.R.idx(a, l)]
    dg = np.hypot(a - F.green[0], l - F.green[1])
    pen = o["pen"][:, j]
    trees = code == M.CODE["recovery"]
    sand = code == M.CODE["sand"]
    fwy = np.isin(code, [M.CODE["fairway"], M.CODE["first_cut"]]) & ~on
    around = ~on & ~pen & ~trees & (dg <= 40)
    c = np.array([a0, l0]) + ca * u + cc * v
    # go = at least 1 ball in 10 finishes on the green, or 15 % carry the front edge; otherwise it is a lay-up
    kind = "g" if (on.mean() >= 0.10 or (o["car"] >= d_front).mean() >= 0.15) else "l"
    return dict(c=o["club"], k=kind, ev=round(float(sm[j]), 3),
                t=[round(float(c[0]), 1), round(float(c[1]), 1)], tot=int(round(ca)),
                lv=int(round(float(np.hypot(c[0] - F.green[0], c[1] - F.green[1])))),
                rc=int(round(100 * float((o["car"] >= d_front).mean()))), g=int(round(100 * float(on.mean()))),
                ar=int(round(100 * float(around.mean()))), fw=int(round(100 * float((fwy & ~around).mean()))),
                x=int(round(100 * float((pen | trees).mean()))), sd=int(round(100 * float((sand & ~around).mean()))),
                w=int(round(float(np.percentile(cr, 97.5) - np.percentile(cr, 2.5)))),
                dp=int(round(float(np.percentile(al[solid], 97.5) - np.percentile(al[solid], 2.5)))),
                ax=round(float(P5.ANG[j]), 0))


def menu(Wd, F, P, z, a0, l0, lie, wx, bearing):
    res = P5.play(Wd, F, P, z, a0, l0, lie, wx, bearing)
    rows = sorted((row_stats(Wd, F, res, o) for o in res["opts"]), key=lambda r: r["ev"])
    rows = [r for r in rows if r["ev"] <= rows[0]["ev"] + KEEP]
    return dict(d=int(round(res["d_ctr"])), f=int(round(res["d_front"])), p=[round(a0, 1), round(l0, 1)], rows=rows)


def solve(a):
    Wd = P5.World(a.which)
    M = Wd.M
    z = M.draws_z(N, 5)
    path = os.path.join(OUT, f"par5_menu_{BASE_NAME[a.which]}_{a.day}.json")
    out = json.load(open(path)) if os.path.exists(path) else {}
    spots = {s: json.load(open(os.path.join(OUT, f"par5_second_{s.replace(' ', '_')}.json"))) for s in SETS_OF[a.which]}
    for h in [int(x) for x in a.holes.split(",")]:
        hd = Wd.course.HOLES[h]
        wx = Wd.wx(h, P5.DAYS[a.day])
        P = M.central(temp_f=wx["temp"])
        bearing = float(Wd.course.BEARINGS[h])
        _, Rb = Wd.big(hd)
        F = P5.Field(Wd, hd, P, Rb)
        H = dict(wx={k: round(float(v), 1) for k, v in wx.items()}, green=[round(float(x), 1) for x in F.green], dist={}, spots={})
        pts = {d: line_of_play(Wd, Rb, F, d) for d in DIST}
        known = [d for d in DIST if pts[d]]
        for d in DIST:
            if pts[d]:
                a0, l0, has = pts[d]
            else:                                              # no fairway at this distance: between its neighbours' lines
                lat = float(np.interp(d, known, [pts[k][1] for k in known]))
                along = F.green[0] - float(np.sqrt(max(d * d - (lat - F.green[1]) ** 2, 1.0)))
                a0, l0, has = along, lat, False
            e = {}
            for lie, key in (("fairway", "F"), ("rough", "R")):
                e[key] = menu(Wd, F, P, z, a0, l0, lie, wx, bearing)
            e["nofw"] = not has
            H["dist"][str(d)] = e
        for s, res in spots.items():
            r = res[f"{h}|{a.day}"]
            H["spots"][s] = {}
            for club, key in (("Driver", "D"), ("2-wood", "W")):
                ca, cl = r["tee"][club]["centre"]
                a0, l0 = ca - r["back"], cl
                H["spots"][s][key] = {k2: menu(Wd, F, P, z, a0, l0, lie, wx, bearing) for lie, k2 in (("fairway", "F"), ("rough", "R"))}
            H["spots"][s]["pick"] = r["tee_pick_engine"]
        out[str(h)] = H
        json.dump(out, open(path, "w"))
        b = H["dist"]["250"]["F"]["rows"][0]
        print(a.which, a.day, h, "250 F best", b["c"], b["k"], b["ev"], flush=True)


def page(_a):
    out = dict(source="opt/par5_menu.py (PAR5.md)", dist=DIST, holes={})
    for which, base in BASE_NAME.items():
        for day, key in (("sat", "d0"), ("sun", "d1")):
            p = os.path.join(OUT, f"par5_menu_{base}_{day}.json")
            if not os.path.exists(p):
                continue
            for h, H in json.load(open(p)).items():
                out["holes"].setdefault(h, {}).setdefault(base, {})[key] = H
    json.dump(out, open(PAGE, "w"), separators=(",", ":"))
    print("wrote", PAGE, os.path.getsize(PAGE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--day", default="sat")
    ap.add_argument("--holes", default="3,6,13,18")
    a = ap.parse_args()
    {"solve": solve, "page": page}[a.cmd](a)


if __name__ == "__main__":
    main()
