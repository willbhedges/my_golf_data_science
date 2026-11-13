"""Par-3 target box from an expected-strokes solve (config "par3_targets": path to a page file written by e.g.
course_data/courses/eagle_knoll/opt/par3_target.py), in place of the DECADE box (yardage_book.par3_plan).

Switched on per course: only a config with "par3_targets" calls install(); every other page keeps the DECADE box.
The page data keep their shape, so the template needs no change:
  * boxes[mod].poly / lo / hi: the aim box (aims within 0.02 strokes of the best, at least 4 yds each way) for that
    DECADE wind class (-1 calm ... 3), drawn on the green like the DECADE box;
  * boxes[mod].play = card + best aim depth (yds past the green centre), so "Play it like" is the carry to the best
    aim, not to the centre;
  * by_set[set].plays[cell] = (plays_like(A, cell) + dz) x card / A with A = card + calm aim depth: the template
    computes play = box.play x plays / card x temperature, which then equals plays_like(A) + dz at the aim, and its
    breakdown chips (target / elevation / wind / temperature) still add up (elevation = dz exactly).
  * d["p3club"]: the club line ("PW, 9-iron a tie") for the forecast days, for a template that wants to show it;
    by_set[set]["p3club"] the same for each offered set (the template shows the picked set's club). Config
    "par3_club_hide" {set: [hole, ...]} blanks it ("": the page shows "Plays N" instead) where the club pick means
    nothing (Gateway 2026-11-09: The Tips / Champions 14 and 17 need 218-232 carry, in the gap between the 210 long
    iron and the 255 4-wood, so "4-iron" lands 14-33 short; Forward 12 is a 90-yd wedge).
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MODS = (-1, 0, 1, 2, 3)


def load(cfg):
    p = cfg.get("par3_targets")
    if not p:
        return None
    return json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p)))


def target(T, set_name, base_set, h):
    sets = T.get("sets", {})
    for s in (set_name, base_set):
        t = (sets.get(s) or {}).get(str(h))
        if t:
            return t
    return None


def club_line(t):
    out = []
    for day, lab in (("sat", "Sat"), ("sun", "Sun")):
        c = (t.get("clubs") or {}).get(day)
        if c:
            out.append(f"{lab}: {c['pick']}" + (f" (tie with {c['runner']})" if c.get("tie") else ""))
    return "; ".join(out)


def boxes_for(t, tee, f, r, ppy, scale_center, yards):
    """yds frame -> page px polygons; depths are relative to the green centre, drawn at the base tee's scale."""
    out = {}
    for mod in MODS:
        b = t["boxes"][str(mod)]
        (l0, l1), (d0, d1) = b["lat"], b["dep"]
        corners = [tee + ((scale_center + d) * f + l * r) * ppy for l, d in ((l0, d0), (l1, d0), (l1, d1), (l0, d1))]
        out[str(mod)] = dict(poly=[[float(c[0]), float(c[1])] for c in corners], play=float(yards + b["aim"][1]),
                             lo=float(yards + d0), hi=float(yards + d1), aim=[float(x) for x in b["aim"]])
        if b.get("m"):       # yds from the target to the green edge each way (Gateway 2026-11-13, opt/par3_decade.py)
            out[str(mod)]["m"] = {k: float(v) for k, v in b["m"].items()}
    return out


def install(cfg, BW, base_set):
    """Patch build_wind_page's par3_hole / par3_sets (this page process only)."""
    T = load(cfg)
    if T is None or getattr(BW, "_p3_targets", False):
        return
    hole0, sets0 = BW.par3_hole, BW.par3_sets
    lad = {}
    if cfg.get("par3_ladder"):                  # live club by the page's number (par3_ladder.py; audit 2026-11-09 item 1)
        lp = cfg["par3_ladder"]
        lad = json.load(open(lp if os.path.isabs(lp) else os.path.join(ROOT, lp)))
    hide = {s: {str(h) for h in hs} for s, hs in (cfg.get("par3_club_hide") or {}).items()}

    def clubs_of(t, set_name, h):
        return "" if str(h) in hide.get(set_name, ()) else club_line(t)

    def par3_hole(h):
        d = hole0(h)
        t = target(T, base_set, base_set, h)
        if t:
            p = BW.course.PAR3[h]
            tee, f, r, ppy = BW.frame(p["tee"], p["flag"], p["center"])
            d["boxes"] = boxes_for(t, tee, f, r, ppy, p["center"], p["center"])
            d["p3club"] = clubs_of(t, base_set, h)
            if t.get("green"):      # the outline the margins are measured on (yds right, yds past the centre): drawn dashed
                d["green"] = [[float(c[0]), float(c[1])] for c in
                              (tee + ((p["center"] + dd) * f + l * r) * ppy for l, dd in t["green"])]
            d["p3_source"] = "expected strokes"
        return d

    def par3_sets(h, opts, grid):
        import wind_grid as WG
        out = sets0(h, opts, grid)
        p0 = BW.course.PAR3[h]
        tee, f, r, ppy = BW.frame(p0["tee"], p0["flag"], p0["center"])
        dz = p0.get("plays_like_delta", 0.0)
        for o in opts:
            t = target(T, o["name"], base_set, h)
            if not t or o["name"] not in out:
                continue
            S = out[o["name"]]
            yards = o["yards"]
            S["boxes"] = boxes_for(t, tee, f, r, ppy, p0["center"], yards)
            A = yards + t["boxes"]["-1"]["aim"][1]
            S["plays"] = {k: (WG.plays_like(A, *[int(x) for x in k.split("_")]) + dz) * yards / A
                          for k in grid["par3"][str(h)]}
            S["aim_dist"] = float(A)
            S["p3club"] = clubs_of(t, o["name"], h)
            L = (lad.get(o["name"]) or {}).get(str(h))
            if L:
                S["ladder"] = dict(p0=L["p0"], map_center=L.get("map_center"), steps=L["steps"])
        return out
    BW.par3_hole, BW.par3_sets = par3_hole, par3_sets
    BW._p3_targets = True


def page_play(box_play, plays_cell, center, tmul):
    """The template's par-3 number (solvePar3), for tests."""
    return box_play * plays_cell / center * tmul


__all__ = ["install", "load", "target", "boxes_for", "page_play", "np"]
