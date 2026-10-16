"""Interactive wind caddie for any course: wind grid (61 winds x every tee shot) + one self-contained page.

Course-agnostic version of spirit_hollow/wind_grid.py + build_wind_page.py (copied, not edited):
  * clubs adjusted with spirit_hollow/wind.py (carry, roll, width, depth, crosswind drift), at the
    central settings of the decision (decide.set_prior_means); `exposure` from the package scales the wind
    on tree-lined holes;
  * the aim grid is centred on each club's calm-day aim (auto tee lines can point well off the fairway);
  * bearings come from the package (tee -> aim, degrees true);
  * hole images are crops of our own clean NAIP renders;
  * par 3s: DECADE wind modifier boxes (yardage_book.par3_plan) and a plays-like distance.
"""
import base64
import datetime as dt
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "mozingo"), os.path.join(ROOT, "spirit_hollow")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tee_strategy as t                            # noqa: E402
import wind as W                                    # noqa: E402  spirit_hollow/wind.py (physics only)

import decide                                       # noqa: E402

SPEEDS = [0, 5, 10, 15, 20, 25]
DIRS = list(range(0, 360, 30))
ZONE_TOL = 0.02
IMG_W = 620
TEMPLATE = os.path.join(HERE, "wind_page_template.html")


def exposure_factor(x):
    """Package `exposure` (share of the landing zone's edge that is trees, 9.1-7) -> wind scale."""
    if x is None:
        return 1.0
    return float(np.clip(1.0 - 0.35 * x, 0.6, 1.0))


def solve(h, speed, rel, z, centers, exposure=1.0):
    calm = {**t.CLUBS, **t.IRONS}
    res = {}
    for c in decide.clubs_for(h):
        carry, total, width, depth, drift = W.adjust(calm[c], speed, rel, club_name=c, exposure=exposure)
        table = t.IRONS if c in t.IRONS else t.CLUBS
        saved = table[c]
        table[c] = (carry, total, width, depth)
        aims = centers[c] + np.arange(-25, 25.01, 2.5)
        ev = np.array([t.simulate(h, c, a + drift, z=z)[3].mean() for a in aims])
        table[c] = saved
        i = int(ev.argmin())
        ok = aims[ev <= ev[i] + ZONE_TOL]
        res[c] = dict(aim=float(aims[i]), ev=float(ev[i]), zone=[float(ok.min()), float(ok.max())],
                      carry=float(carry), total=float(total), width=float(width), drift=float(drift))
    best = min(res, key=lambda c: res[c]["ev"])
    runner = min((c for c in res if c != best), key=lambda c: res[c]["ev"])
    return dict(pick=best, margin=res[runner]["ev"] - res[best]["ev"], runner=runner, clubs=res)


def _grid_hole(args):
    h, centers, exposure, n = args
    decide.set_prior_means()
    rng = np.random.default_rng(31)
    z = np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])
    grid = {}
    for sp in SPEEDS:
        for rel in ([0] if sp == 0 else DIRS):
            grid[f"{sp}_{rel}"] = solve(h, sp, rel, z, centers, exposure)
    return h, grid


def plays_like(dist, speed, rel):
    carry = W.adjust((dist, dist + 5, 30, 15), speed, rel, club_name="Mid iron")[0]
    return dist * dist / carry


def build_grid(mod, results, n=2500, workers=None, log=print):
    decide.bind(mod.HOLES)
    jobs = []
    for h in mod.HOLES:
        centers = {c: v["aim"] for c, v in results[h]["clubs"].items()}
        jobs.append((h, centers, exposure_factor(mod.EXPOSURE.get(h)), n))
    out = dict(speeds=SPEEDS, dirs=DIRS, n=n, bearings={str(k): v for k, v in mod.BEARINGS.items()}, holes={}, par3={})
    workers = workers or min(len(jobs), os.cpu_count() or 1)
    if workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            for h, g in pool.imap_unordered(_grid_hole, jobs):
                out["holes"][str(h)] = g
                log(f"  wind grid {h}: calm {g['0_0']['pick']}")
    else:
        for j in jobs:
            h, g = _grid_hole(j)
            out["holes"][str(h)] = g
    out["holes"] = {str(h): out["holes"][str(h)] for h in mod.HOLES}
    for h, p in mod.PAR3.items():
        out["par3"][str(h)] = {f"{sp}_{rel}": plays_like(p["center"], sp, rel)
                               for sp in SPEEDS for rel in ([0] if sp == 0 else DIRS)}
    return out


# ----------------------------------------------------------------------------- page
def frame(tee, toward, yds):
    tee = np.array(tee, float)
    v = np.array(toward, float) - tee
    ppy = np.linalg.norm(v) / yds
    f = v / np.linalg.norm(v)
    return tee, f, np.array([-f[1], f[0]]), ppy


def crop_jpeg(path, box):
    """box in the 920x2000 frame -> (data URI, scale, (x0, y0), size)."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    k = im.width / 920
    x0, y0, x1, y1 = box
    x0, x1 = max(0, x0), min(920, x1)
    y0, y1 = max(0, y0), min(2000, y1)
    c = im.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)))
    scale = IMG_W / c.width
    c = c.resize((IMG_W, int(c.height * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    c.save(buf, "JPEG", quality=76, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), scale * k, (x0, y0), c.size


def tee_hole(mod, h, shots, results):
    hd = mod.HOLES[h]
    tee, f, r, ppy = frame(hd["tee"], hd["dot270"], 270)
    lat = [v["aim"] for v in results[h]["clubs"].values()]
    lo, hi = min(min(lat) - 70, -75), max(max(lat) + 70, 75)
    pts = [tee + (a * f + l * r) * ppy for a in (175, 345) for l in (lo, hi)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    uri, s, (x0, y0), size = crop_jpeg(os.path.join(shots, hd["image"]), (min(xs), min(ys), max(xs), max(ys)))
    return dict(kind="tee", img=uri, w=size[0], h=size[1], s=s, x0=x0, y0=y0,
                tee=list(map(float, tee)), f=list(map(float, f)), r=list(map(float, r)), ppy=float(ppy),
                par=hd["par"], length=hd["length"], label=mod.LABELS.get(h, str(h)),
                note=mod.NOTES.get(h, ""), aim_at=mod.AIM_AT.get(h, ""))


def par3_hole(mod, h, shots):
    import yardage_book as yb
    p = mod.PAR3[h]
    tee, f, r, ppy = frame(p["tee"], p["flag"], p["center"])
    g = np.array(p["green"], float)
    gp = np.array([tee + ((p["center"] + d) * f + l * r) * ppy for l, d in g])
    pad = 14 * ppy
    box = (gp[:, 0].min() - pad, gp[:, 1].min() - pad, gp[:, 0].max() + pad, gp[:, 1].max() + pad)
    uri, s, (x0, y0), size = crop_jpeg(os.path.join(shots, p["image"]), box)
    boxes = {}
    for m in (-1, 0, 1, 2, 3):
        yb.WIND_NOW = m
        plan = yb.par3_plan(p)
        (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
        if l1 - l0 < 2:
            l0, l1 = (l0 + l1) / 2 - 1, (l0 + l1) / 2 + 1
        if d1 - d0 < 2:
            d0, d1 = (d0 + d1) / 2 - 1, (d0 + d1) / 2 + 1
        corners = [tee + ((p["center"] + d) * f + l * r) * ppy for l, d in ((l0, d0), (l1, d0), (l1, d1), (l0, d1))]
        boxes[str(m)] = dict(poly=[[float(c[0]), float(c[1])] for c in corners],
                             play=float(p["center"] + plan["aim"][1]),
                             lo=float(p["center"] + plan["dep"][0]), hi=float(p["center"] + plan["dep"][1]))
    yb.WIND_NOW = 0
    return dict(kind="par3", img=uri, w=size[0], h=size[1], s=s, x0=x0, y0=y0, par=3, length=p["center"],
                label=mod.LABELS.get(h, str(h)), boxes=boxes, green=[[float(q[0]), float(q[1])] for q in gp],
                note=p.get("note", ""), short=p.get("short", ""), front=p["front"], back=p["back"])


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_page(mod, slug, grid, results, forecast, shots, out_html, mode, tee_set):
    holes = []
    for h in mod.ORDER:
        d = par3_hole(mod, h, shots) if h in mod.PAR3 else tee_hole(mod, h, shots, results)
        d["key"] = str(h)
        d["bearing"] = grid["bearings"].get(str(h))
        if h in mod.PAR3:
            d["plays"] = grid["par3"][str(h)]
        else:
            d["grid"] = grid["holes"][str(h)]
            r = results[h]
            d["calm"] = dict(pick=r["pick"], aim=r["aim"], tie=bool(r["tie"]), margin=r["margin"],
                             flips=r.get("width_flips", []))
        holes.append(d)
    days, rows, fetched = [], [], None
    if forecast and forecast.get("hourly"):
        fetched = forecast.get("fetched_utc")
        for day in forecast.get("days") or sorted({r["date"] for r in forecast["hourly"]}):
            dd = dt.date.fromisoformat(day)
            days.append(dict(key=day, date=day, label=f"{dd.strftime('%a')} {dd.month}/{dd.day}"))
        rows = [dict(date=r["date"], hour=r["hour"], mph=r["wind_mph"], gust=r.get("gust_mph") or r["wind_mph"],
                     dir=r["wind_from_deg"], temp=r.get("temp_f") or 70) for r in forecast["hourly"]]
    calm_note = ("Calm pick from the full Bayesian run." if mode == "full"
                 else "Calm pick from the model at its central settings (quick mode).")
    fc = (f"Forecast: Open-Meteo for {forecast['location']['lat']:.3f}, {forecast['location']['lon']:.3f}, "
          f"fetched {fetched[:16].replace('T', ' ')} UTC. ") if fetched else \
        "No forecast attached (set the wind by hand, or re-run on Actions to fetch one). "
    foot = (fc + "Wind effects on carry, roll, dispersion and drift from published TrackMan/Ping/Foresight "
            "figures and a ball-flight model. Maps are NAIP aerial imagery re-projected so the tee line runs up "
            "the page; aims are yards left/right of that line. Club picks in wind use the model at its central "
            f"settings (driver pattern 70 yds). {calm_note} \"≈\" marks a tie (within 0.01 strokes). Hole "
            "geometry is auto-built from OpenStreetMap; check the notes for data flags.")
    data = dict(name=mod.NAME, slug=slug, speeds=grid["speeds"], dirs=grid["dirs"], holes=holes, days=days,
                forecast=rows, fetched=fetched, calm_note=calm_note, foot=foot)
    short_name = mod.NAME.replace(" Golf Course", "").replace(" Golf Club", "").replace(" Country Club", "")
    title = f"{short_name} Wind Caddie"
    sub = (f"{tee_set} tees · Driver 275/300 · 2-wood 265/280 · 4-wood 255/270 · club and aim re-solved "
           "for the wind you set")
    btns = "".join(f'<button data-v="{d["key"]}">{_esc(d["label"])}</button>' for d in days)
    html = open(TEMPLATE).read()
    html = (html.replace("__TITLE__", _esc(title)).replace("__SUB__", _esc(sub)).replace("__SRC_BUTTONS__", btns)
            .replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")).replace("</", "<\\/")))
    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    with open(out_html, "w") as fh:
        fh.write(html)
    return out_html
