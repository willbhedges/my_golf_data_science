"""Build the interactive wind caddie page (single self-contained HTML).

  python3 spirit_hollow/build_wind_page.py   -> output/wind_page/index.html

Inputs: output/wind_grid.json (wind_grid.py), output/final_decision.json (calm-day Bayes picks,
optional), course_data/weather/forecast_spirit_hollow.json, screenshots_clean/ (overlay-free maps),
course.py (geometry) and yardage_book.par3_plan (par-3 boxes for each DECADE wind modifier).
"""
import base64
import io
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [os.path.join(ROOT, "mozingo"), HERE]

import course                                  # noqa: E402
import tee_strategy as t                       # noqa: E402
import yardage_book as yb                      # noqa: E402

OUT = os.path.join(HERE, "output", "wind_page", "index.html")
_fn = os.path.join(HERE, "output", "final_notes.json")         # notes generated from the final run
FN = json.load(open(_fn)) if os.path.exists(_fn) else {}
IMG_W = 620


def frame(tee, toward, yds):
    tee = np.array(tee, float)
    v = np.array(toward, float) - tee
    ppy = np.linalg.norm(v) / yds
    f = v / np.linalg.norm(v)
    return tee, f, np.array([-f[1], f[0]]), ppy


def crop_jpeg(image, box, y_max=1830):
    """box in the 920x2000 frame -> (data URI, scale px/frame-px, (x0, y0), size). Rows past the
    bottom of the screenshot (a tee box the app cut off) are padded with a plain band."""
    k = 1206 / 920
    path = os.path.join(HERE, "screenshots_clean", image)
    if not os.path.exists(path):
        path = os.path.join(HERE, "screenshots", image)
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = box
    x0, x1 = max(0, x0), min(920, x1)
    y0, y1 = max(545, y0), min(y_max, y1)
    c = im.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(min(y1, 2000) * k)))
    if y1 > 2000:                                   # pad below the screenshot
        pad = Image.new("RGB", (c.width, int((y1 - y0) * k)), (52, 66, 56))
        pad.paste(c, (0, 0))
        c = pad
    scale = IMG_W / c.width
    c = c.resize((IMG_W, int(c.height * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    c.save(buf, "JPEG", quality=78, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), scale * k, (x0, y0), c.size


sys.path.insert(0, os.path.join(ROOT, "course_data", "elevation"))
try:
    import adjust as _E                                       # USGS 3DEP elevation per club
except Exception:
    _E = None


_REG = os.path.join(ROOT, "course_data", "spirit_hollow", "elev_registered.json")
_REG = json.load(open(_REG)) if os.path.exists(_REG) else {}


def elev_of(h):
    if _E is None:
        return None
    if str(h) in _REG and h in course.HOLES:                 # same numbers the model uses
        drops = _REG[str(h)].get("drop_ft", {})
        return dict(clubs={c: dict(dc=e[0], rf=e[1], kick=e[2], drop=drops.get(c, 0.0))
                           for c, e in course.HOLES[h]["elev"].items()})
    try:
        a = _E.adjustments(str(h))
    except Exception:
        p = course.PAR3.get(h, {})
        if p.get("green_drop_ft") is not None:                 # from the platform package (hole 3)
            return dict(green_drop=p["green_drop_ft"], dz=p.get("plays_like_delta"))
        return None
    if "clubs" in a and a["clubs"]:
        sl = a.get("landing_slope") or {}
        return dict(clubs={c: dict(dc=v["carry_delta_yds"], rf=v["roll_factor"], kick=v["lateral_kick_yds"],
                                   drop=v["landing_drop_ft"]) for c, v in a["clubs"].items()},
                    along=sl.get("along_pct"), cross=sl.get("cross_pct"))
    return dict(green_drop=a.get("green_drop_ft"), dz=a.get("plays_like_delta_yds"))


def tee_hole(h):
    hd = course.HOLES[h]
    tee, f, r, ppy = frame(hd["tee"], hd["dot270"], 270)
    # whole hole from the tee box (the page can zoom to the landing area)
    pts = [tee + (a * f + l * r) * ppy for a in (-14, 345) for l in (-75, 75)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    box = (min(xs), min(ys), max(xs), max(ys))
    uri, s, (x0, y0), size = crop_jpeg(hd["image"], box, y_max=10000)
    return dict(kind="tee", img=uri, w=size[0], h=size[1], s=s, x0=x0, y0=y0,
                tee=list(map(float, tee)), f=list(map(float, f)), r=list(map(float, r)), ppy=float(ppy),
                par=hd["par"], length=hd["length"], label=course.LABELS.get(h, str(h)),
                tee_name="Gold tee" if "Gold" in course.LABELS.get(h, "") else "Black tee",
                tee_offimage=bool(hd["tee"][1] > 2000), elev=elev_of(h) if course.ELEVATION else None,
                note=FN.get(str(h), {}).get("note", ""), aim_at=FN.get(str(h), {}).get("aim_at", ""))


def par3_hole(h):
    p = course.PAR3[h]
    tee, f, r, ppy = frame(p["tee"], p["flag"], p["center"])
    g = np.array(p["green"], float)
    gp = np.array([tee + ((p["center"] + d) * f + l * r) * ppy for l, d in g])
    pad = 14 * ppy
    box = (gp[:, 0].min() - pad, gp[:, 1].min() - pad, gp[:, 0].max() + pad, gp[:, 1].max() + pad)
    uri, s, (x0, y0), size = crop_jpeg(p["image"], box)
    boxes = {}
    for mod in (-1, 0, 1, 2, 3):
        yb.WIND_NOW = mod
        plan = yb.par3_plan(p)
        (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
        if l1 - l0 < 2:
            l0, l1 = (l0 + l1) / 2 - 1, (l0 + l1) / 2 + 1
        if d1 - d0 < 2:
            d0, d1 = (d0 + d1) / 2 - 1, (d0 + d1) / 2 + 1
        corners = [tee + ((p["center"] + d) * f + l * r) * ppy for l, d in ((l0, d0), (l1, d0), (l1, d1), (l0, d1))]
        boxes[str(mod)] = dict(poly=[[float(c[0]), float(c[1])] for c in corners],
                               play=float(p["center"] + plan["aim"][1]),
                               lo=float(p["center"] + plan["dep"][0]), hi=float(p["center"] + plan["dep"][1]))
    yb.WIND_NOW = 0
    green = [[float(q[0]), float(q[1])] for q in gp]
    return dict(kind="par3", img=uri, w=size[0], h=size[1], s=s, x0=x0, y0=y0, par=3, length=p["center"],
                label=str(h), boxes=boxes, elev=elev_of(h) if course.ELEVATION else None, green=green, note=p.get("note", ""), short=p.get("short", ""),
                front=p["front"], back=p["back"])


def main():
    yb.use_course("Spirit Hollow GC", HERE, "Spirit_Hollow", course.HOLES, course.PAR3, course.NOTES,
                  course.AIM_AT, course.ORDER, course.LABELS)
    grid = json.load(open(os.path.join(HERE, "output", "wind_grid.json")))
    final_path = os.path.join(HERE, "output", "final_decision.json")
    final = json.load(open(final_path)) if os.path.exists(final_path) else {}
    fc = json.load(open(os.path.join(ROOT, "course_data", "weather", "forecast_spirit_hollow.json")))
    holes = []
    for h in course.ORDER:
        d = par3_hole(h) if h in course.PAR3 else tee_hole(h)
        d["key"] = str(h)
        d["bearing"] = grid["bearings"].get(str(h))
        if h in course.PAR3:
            d["plays"] = grid["par3"][str(h)]
        else:
            d["grid"] = grid["holes"][str(h)]
            fd = final.get(str(h))
            if fd and fd.get("tie") is not None:
                d["calm"] = dict(pick=fd["pick"], aim=fd["aim"], tie=bool(fd["tie"]), margin=fd["margin"],
                                 flips=fd.get("width_flips", []))
        holes.append(d)
    data = dict(speeds=grid["speeds"], dirs=grid["dirs"], holes=holes,
                forecast=[dict(date=r["date"], hour=r["hour"], mph=r["wind_mph"], gust=r["gust_mph"],
                               dir=r["wind_from_deg"], temp=r["temp_f"]) for r in fc["hourly"]],
                fetched=fc["fetched_utc"])
    html = open(os.path.join(HERE, "wind_page_template.html")).read()
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(html)
    print("wrote", OUT, f"{os.path.getsize(OUT) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
