"""Build the v2 wind caddie page (same template and layout as spirit_hollow/build_wind_page.py).

  python3 spirit_hollow/v2/build_page_v2.py   -> spirit_hollow/v2/wind_page/index.html

Differences from the live page: club picks per wind cell from the v2 wind grids
(spirit_hollow/v2/output/wind_grid*.json), the calm-day pick/aim/tie from the v2 Bayesian run
(v2_decisions.json), shot patterns drawn from the v2 engine (soft course, 48 F), the blue bar is the
0.005-stroke aim window, and the page text says so. The live page and its inputs are not touched.
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

OUT = os.path.join(HERE, "wind_page", "index.html")


def cloud(h, grid0):
    """Per club: centre offset and 95% spread of where v2 shots finish at the calm aim, relative to
    the point the page draws (grid carry + DEM carry, roll x DEM factor; aim)."""
    hd = M.HOLES[h]
    P = M.central()
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


TEXT = [
    ("<title>Spirit Hollow Wind Caddie</title>", "<title>Spirit Hollow Caddie v2</title>"),
    ('localStorage.getItem("shwc")', 'localStorage.getItem("shwc_v2")'),
    ('localStorage.setItem("shwc"', 'localStorage.setItem("shwc_v2"'),
    ("Aim at the dot${", "Aim at the dot (anywhere on the blue bar is within 0.005 strokes)${"),
    ('Club picks in wind use the model at its central settings (driver pattern 70 yds); the calm-day pick comes '
     'from the full Bayesian run. "≈" marks a tie (within 0.01 strokes).',
     'Model v2: soft course (the ball stops within a couple of yards), 48°F carry, slight and heavy mishits, '
     'curving misses lose carry, lost balls and OB priced as stroke and distance, water relief from where the '
     'ball went in, trees as punch-outs, scratch-5 scoring. Club picks in wind use v2 at its central settings '
     '(driver pattern 70 yds); the calm-day pick and aim come from the v2 Bayesian run (64 prior draws), aims '
     'optimised to the half yard. "≈" marks a tie (within 0.01 strokes).'),
]


def main():
    yb.use_course("Spirit Hollow GC", SH, "Spirit_Hollow", course.HOLES, course.PAR3, course.NOTES,
                  course.AIM_AT, course.ORDER, course.LABELS)
    od = os.path.join(HERE, "output")
    grid = json.load(open(os.path.join(od, "wind_grid.json")))
    grids = {0: grid}
    for path in glob.glob(os.path.join(od, "wind_grid_back*.json")):
        grids[int(float(re.search(r"back([+-]?[0-9.]+)", path).group(1)))] = json.load(open(path))
    dec = json.load(open(os.path.join(od, "v2_decisions.json")))
    fc = json.load(open(os.path.join(ROOT, "course_data", "weather", "forecast_spirit_hollow.json")))
    holes = []
    for h in course.ORDER:
        d = BW.par3_hole(h) if h in course.PAR3 else BW.tee_hole(h)
        d["key"] = str(h)
        d["bearing"] = grid["bearings"].get(str(h))
        base, opts = BW.tee_options(h)
        d["base_set"], d["tee_opts"] = base, opts
        if h in course.PAR3:
            d["plays"] = grid["par3"][str(h)]
            d["by_set"] = BW.par3_sets(h, opts, grid)
        else:
            d["grids"] = {str(b): BW.compact(g["holes"][str(h)]) for b, g in sorted(grids.items())
                          if str(h) in g.get("holes", {})}
            d["cloud"] = cloud(h, grid["holes"][str(h)]["0_0"])
            r = dec.get(str(h))
            if r and "pick" in r:
                d["calm"] = dict(pick=r["pick"], aim=r["aim"], tie=bool(r["tie"]), margin=r["margin"],
                                 flips=r.get("width_flips", []))
        holes.append(d)
    data = dict(speeds=grid["speeds"], dirs=grid["dirs"], holes=holes, offsets=sorted(grids),
                forecast=[dict(date=r["date"], hour=r["hour"], mph=r["wind_mph"], gust=r["gust_mph"],
                               dir=r["wind_from_deg"], temp=r["temp_f"]) for r in fc["hourly"]],
                fetched=fc["fetched_utc"])
    html = open(os.path.join(SH, "wind_page_template.html")).read()
    for a, b in TEXT:
        if a not in html:
            raise SystemExit(f"template text not found: {a[:60]}")
        html = html.replace(a, b)
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(html)
    print("wrote", OUT, f"{os.path.getsize(OUT) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
