"""Build the v2 wind caddie page (same template and layout as spirit_hollow/build_wind_page.py).

  python3 spirit_hollow/v2/build_page_v2.py   -> spirit_hollow/v2/wind_page/index.html

Differences from the live page: club picks per wind cell AND temperature (35/45/55/65 F, interpolated
to the forecast for when you reach each hole) from the v2 wind grids (spirit_hollow/v2/output/
wind_grid*.json), the calm-day pick/aim/tie from the v2 Bayesian run (v2_decisions.json), shot
patterns from the v2 engine, the blue bar is the 0.005-stroke aim window, a hypothetical ~235 hybrid
shown in each table (never the pick). Template: spirit_hollow/v2/wind_page_template_v2.html (a copy
of the live template). The live page and its inputs are not touched.
"""
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
ROOT = os.path.dirname(SH)
sys.path[:0] = [HERE, SH, os.path.join(ROOT, "mozingo")]

import build_wind_page as BW                    # noqa: E402
import course                                   # noqa: E402
import model as M                               # noqa: E402
import yardage_book as yb                       # noqa: E402

OUT = os.environ.get("V2_PAGE_OUT") or os.path.join(HERE, "wind_page", "index.html")
IN = os.environ.get("V2_PAGE_IN") or os.path.join(HERE, "output")


def cloud(h, grid0, temp_f):
    """Per club: centre offset and 95% spread of where v2 shots finish at the calm aim, relative to
    the point the page draws (grid carry + DEM carry, roll x DEM factor; aim)."""
    hd = M.HOLES[h]
    P = M.central(temp_f=temp_f)
    R = M.Raster(hd)
    S = R.strokes(P, hd["length"])
    z = M.draws_z(6000, 17)
    out = {}
    elev = hd.get("elev", {})
    for c, v in grid0["clubs"].items():
        _, (a, l, lie, s) = M.ev_curve(R, S, hd, c, P, z, np.array([v["aim"]]))
        xy = np.c_[a[:, 0], l[:, 0]]
        mu = np.median(xy, axis=0)
        w, vec = np.linalg.eigh(np.cov((xy - mu).T))
        half = [0.5 * float(np.subtract(*np.percentile((xy - mu) @ vec[:, i], [97.5, 2.5]))) for i in (1, 0)]
        dc, rf, kick = elev.get(c, (0.0, 1.0, 0.0))
        page_total = (v["carry"] + dc) + (v["total"] - v["carry"]) * rf
        out[c] = dict(dA=round(float(mu[0] - page_total), 1), dL=round(float(mu[1] - (v["aim"] + kick)), 1),
                      A=round(half[0], 1), B=round(half[1], 1), u=[round(float(x), 4) for x in vec[:, 1]],
                      w=[round(float(x), 4) for x in vec[:, 0]], width=v["width"])
    return out


SHORT = {"Driver": "driver", "2-wood": "2-wood", "4-wood": "4-wood", "Long iron": "long iron", "Mid iron": "mid iron"}


def side(a):
    return "on the app line" if abs(a) < 0.25 else f"{abs(a):.1f} yds {'left' if a < 0 else 'right'}"


def note_v2(h, r):
    """The hole note from the v2 run (replaces v1's final_notes.json text)."""
    w = r["window"]
    sh = r.get("shares", {})
    parts = [f"{r['pick']} by {r['margin']:.3f} ± {r['margin_se']:.3f} strokes over {SHORT[r['runner']]}"
             + (" (a tie: within 0.01)" if r["tie"] else "")
             + f"; it beats {SHORT[r['runner']]} in {r['p_pick_beats_runner']:.0%} of 64 what-if worlds."]
    parts.append(f"Aim {side(r['aim'])}; anywhere from {side(w[0])} to {side(w[1])} is within 0.005.")
    fl = r.get("width_flips") or []
    parts.append("Same club for any driver pattern from 55 to 90 yds." if not fl else
                 "Driver-pattern break-even (all clubs scaled): " +
                 "; ".join(f"{f['frm']} → {f['to']} at {f['width']:.0f} yds" for f in fl) + ".")
    if sh:
        bits = [f"fairway {sh['fairway']:.0%}", f"first cut {sh['first_cut']:.0%}"]
        for k, lab in (("sand", "sand"), ("recovery", "trees"), ("native", "long grass"), ("water", "water"),
                       ("ob", "OB")):
            if sh.get(k, 0) >= 0.01:
                bits.append(f"{lab} {sh[k]:.0%}")
        parts.append(f"With {SHORT[r['pick']]} at {r.get('temp_f', M.hole_temp(h)):.0f}°F: " + ", ".join(bits)
                     + f", about {sh['median_to_green']:.0f} yds in.")
    hy = r.get("hybrid")
    if hy:
        d = hy["vs_pick"]
        parts.append(f"A ~235 hybrid (not in your bag) would {'gain' if d < 0 else 'cost'} {abs(d):.3f} strokes here.")
    hd = course.HOLES[h]
    if hd.get("tee_moved"):
        parts.append(f"Tee: planned from the Black box, {hd['tee_moved']} yds ahead of the app's tee marker.")
    return " ".join(parts)


def main():
    import geom
    geom.set_geometry(os.environ.get("V2_GEOM", "scale,elev,green"))
    yb.use_course("Spirit Hollow GC", SH, "Spirit_Hollow", course.HOLES, course.PAR3, course.NOTES,
                  course.AIM_AT, course.ORDER, course.LABELS)
    od = IN
    grid = json.load(open(os.path.join(od, "wind_grid.json")))
    grids = {0: grid}
    for path in glob.glob(os.path.join(od, "wind_grid_back*.json")):
        grids[int(float(re.search(r"back([+-]?[0-9.]+)", path).group(1)))] = json.load(open(path))
    dec = json.load(open(os.path.join(od, "v2_decisions.json")))
    fc = json.load(open(os.path.join(ROOT, "course_data", "weather", "forecast_spirit_hollow.json")))
    holes = []
    for h in course.ORDER:
        d = BW.par3_hole(h) if h in course.PAR3 else BW.tee_hole(h)
        if h not in course.PAR3:
            d["ppy"] = d["ppy"] / course.HOLES[h].get("ground_scale", 1.0)     # draw in ground yards
        d["key"] = str(h)
        d["bearing"] = grid["bearings"].get(str(h))
        base, opts = BW.tee_options(h)
        d["base_set"], d["tee_opts"] = base, opts
        if h in course.PAR3:
            d["plays"] = grid["par3"][str(h)]
            d["by_set"] = BW.par3_sets(h, opts, grid)
        else:
            d["grids"] = {str(b): {T: BW.compact(gT) for T, gT in g["holes"][str(h)].items()}
                          for b, g in sorted(grids.items()) if str(h) in g.get("holes", {})}
            Tn = min(grid["temps"], key=lambda T: abs(T - M.hole_temp(h)))
            d["cloud"] = cloud(h, grid["holes"][str(h)][f"{Tn:g}"]["0_0"], Tn)
            r = dec.get(str(h))
            if r and "pick" in r:
                d["note"] = note_v2(h, r)
                d["calm"] = dict(pick=r["pick"], aim=r["aim"], tie=bool(r["tie"]), margin=r["margin"],
                                 flips=r.get("width_flips", []), temp=r.get("temp_f", M.hole_temp(h)),
                                 window=r.get("window"))
        holes.append(d)
    data = dict(speeds=grid["speeds"], dirs=grid["dirs"], temps=grid["temps"], holes=holes, offsets=sorted(grids),
                forecast=[dict(date=r["date"], hour=r["hour"], mph=r["wind_mph"], gust=r["gust_mph"],
                               dir=r["wind_from_deg"], temp=r["temp_f"]) for r in fc["hourly"]],
                fetched=fc["fetched_utc"])
    html = open(os.path.join(HERE, "wind_page_template_v2.html")).read()
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(html)
    print("wrote", OUT, f"{os.path.getsize(OUT) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
