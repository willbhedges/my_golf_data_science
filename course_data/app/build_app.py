"""Bundle every available course into one self-contained phone-app prototype page.

  python3 course_data/app/build_app.py [--out course_data/app/out/index.html] [--json DIR]

What goes in (course_data/app/SCHEMA.md documents the format, `golf_app/1`):
  * Spirit Hollow, the *verified* course: the hand-checked map and the live wind page's own data
    (spirit_hollow/build_wind_page.py functions: final_decision.json calm picks, wind_grid*.json for ten
    tee offsets, simulated shot patterns, USGS elevation, par-3 DECADE boxes for every tee set).
  * every other course package with a plan (course_data/packages/<slug>/out*/ from course_data/product/plan.py):
    decision.json, wind_grid.json, forecast.json, course.py, screenshots/ (NAIP hole images),
    out/review/review.json (the 2-minute pre-round check) and plan.json (CHECK flags). A course with one
    plan dir per tee set (out/, out_gold/, ...) gets real per-set picks; every set is drawn on the primary
    set's image through the WGS84 frames (course_data/imagery/render.Frame), so a hole ships one image.
  * the course library (SCHEMA.md "Library"): the app's courses, the hand-checked tournament courses linked to their
    published wind pages (WIND_PAGES), packages without a plan, course_data/library/index.json when present, and the
    IA / MO OpenStreetMap survey (course_data/packages/_survey).
  * shared_store.js: golfer confirmations and "problem with this hole" reports, in the artifact's shared db when
    the page is published with the db capability (SCHEMA.md "Publishing with shared storage"), else localStorage.
  * per auto course, the golfer-confirm data (course_data/app/pools/<slug>.json from confirm_pool.py: the routing v2
    pool the page re-solves over, the course's aerial overview) and the JS of confirm_engine.js (golf_confirm/1 in
    the browser) and typed_card.js (typed scorecard checks): "I'm playing course X from tees Y" on a course whose
    holes were placed automatically (SCHEMA.md, "Hole map confirm").

Nothing here re-runs the strategy model except the shot-pattern clouds of the auto courses
(yardage_book.shot_cloud, 4000 swings per club, seconds). The page itself needs no network: images are
data URIs; fonts come from Google Fonts when online and fall back to system fonts.
"""
import argparse
import base64
import datetime as dt
import glob
import importlib.util
import io
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
PKGS = os.path.join(CD, "packages")
TEMPLATE = os.path.join(HERE, "app_template.html")
POOLS = os.path.join(HERE, "pools")
LIBPLAY_JS = os.path.join(HERE, "lib_play.js")
ENGINE_JS = [os.path.join(HERE, "typed_card.js"), os.path.join(HERE, "confirm_engine.js"), os.path.join(HERE, "shared_store.js")]
ENGINE_JS.append(os.path.join(HERE, "course_index.js"))   # national index + "Request this course" (course_index.py)
COURSES_DIR = os.path.join(CD, "courses")
LIBRARY_INDEX = os.path.join(CD, "library", "index.json")
# Hand-checked courses with their own published wind page (linked, not embedded: each page is ~10 MB).
WIND_PAGES = {
    "blue_hills": "https://claude.ai/artifact/HKvWb1BjemS8rfomZTWRY6",
    "eagle_knoll": "https://claude.ai/artifact/QQkFta99SEstd6Dv8wzgf8",
    "gateway_national": "https://claude.ai/artifact/PCn2RTEcicJs2LrEC2ZBLb",
    "pine_dunes": "https://claude.ai/artifact/6aCeobGkESNQXPiZefXFVq",
    "national_kc": "https://claude.ai/artifact/X9Kn1MzX1CAgST63WpEuMP",
    "hot_springs_arlington": "https://claude.ai/artifact/PzgE7wAjaMXRn8AeewEAeQ",
    "spirit_hollow": "https://claude.ai/artifact/NroPJCYdEmhdN1osK23x4E",
}
OUT = os.path.join(HERE, "out", "index.html")

for _p in (os.path.join(ROOT, "spirit_hollow"), os.path.join(ROOT, "mozingo"), os.path.join(CD, "product"),
           os.path.join(CD, "imagery")):
    if _p not in sys.path:
        sys.path.append(_p)
sys.path.insert(0, os.path.join(ROOT, "mozingo"))
sys.path.insert(0, os.path.join(ROOT, "spirit_hollow"))

SPEEDS = [0, 5, 10, 15, 20, 25]
DIRS = list(range(0, 360, 30))
CELLS = ["0_0"] + [f"{s}_{d}" for s in SPEEDS[1:] for d in DIRS]
IMG_W = 560
PACE_MIN = 14
COLOURS = {"black": "#1b1b1b", "gold": "#d4a017", "blue": "#2563c9", "white": "#f4f4f4", "red": "#c8312b",
           "rust": "#a5502a", "green": "#2f8f4e", "silver": "#a8b0b5", "yellow": "#e5c228", "orange": "#e07a1f",
           "app": "#6b7c72", "combo": "#7a6bd1", "turquoise": "#2bb3b1", "brown": "#7a5230"}
PLAYER = dict(name="Default player (the book's bag)", clubs={
    "Driver": dict(carry=275, total=300), "2-wood": dict(carry=265, total=280), "4-wood": dict(carry=255, total=270),
    "Long iron": dict(carry=215, total=225), "Mid iron": dict(carry=180, total=188)},
    temp_carry_pct_per_f=0.10, temp_ref_f=70)
# The plan's own pattern (spirit_hollow/v2 prior centre, course_data/personal/bayes.BOOK_BAG): every precomputed
# pick, aim and drawn pattern assumes these widths. The app's "Your game" panel scales from them.
PLAYER["clubs"]["Driver"]["width95"] = 70.0
PLAYER["clubs"]["2-wood"]["width95"] = 65.0
PLAYER["clubs"]["4-wood"]["width95"] = 54.0
PLAYER["clubs"]["Long iron"]["width95"] = 43.2
PLAYER["clubs"]["Mid iron"]["width95"] = 36.7
# The golfer's bag as the "Your game" panel starts it (golf_player/1 `stated`; editable, kept in localStorage).
# `plan` = the precomputed club that stands in for it; null = not in the precomputed plans yet.
PROFILE_DEFAULTS = dict(
    schema="golf_player/1", reference_club="Driver", prior_name="v2",
    clubs={"Driver": dict(carry=275, total=300, width95=70.0, plan="Driver"),
           "2-wood": dict(carry=265, total=280, width95=65.0, plan="2-wood"),
           "4-wood": dict(carry=255, total=270, width95=54.0, plan="4-wood"),
           "Hybrid": dict(carry=235, total=250, width95=48.6, plan=None),
           "4-iron": dict(carry=210, total=225, width95=43.2, plan="Long iron")},
    # bayes.Prior.v2(): driver width LN(median = stated, 90 % up to x 80/70); ratio sds; carry N(0,5) common
    # + N(0,3) per club; range -> course width x LN(1.05, 0.08); session carry sd 3
    prior=dict(w_logsd=round(math.log(80 / 70) / 1.645, 4), ratio_sd={"2-wood": 0.04, "4-wood": 0.06},
               ratio_sd_default=0.08, c_common_sd=5.0, c_club_sd=3.0, f_median=1.05, f_logsd=0.08, session_sd=3.0,
               depth_mult=1.25, aim_sd={"plan": 3.0, "aim_point": 4.0, "fairway_centre": 6.0, "green_line": 10.0},
               gps_sd=5.0, beyond=35.0))
PLAYER["profile_defaults"] = PROFILE_DEFAULTS
V2_DECISIONS = os.path.join(ROOT, "spirit_hollow", "v2", "output", "v2_decisions.json")


def width_rule(rec):
    """spirit_hollow/v2 decision for one tee shot -> the app's `width_rule` (SCHEMA.md): the pick across the
    driver width (sweep + break-evens) and each club's aim at 60 / 70 / 82 yds (sens runs)."""
    if not rec or not rec.get("width_sweep"):
        return None
    sens = rec.get("sens") or {}
    cen = (sens.get("central") or {}).get("clubs") or {}
    aims = {}
    for c, v in cen.items():
        if "not in bag" in c:
            continue
        pts = [[70, r1(rec["aim"]) if c == rec["pick"] else r1(v["aim"])]]
        for key, w in (("width 60 (tighter)", 60), ("width 82 (published 5-hcp average)", 82)):
            e = sens.get(key)
            if e and e.get("pick") == c and e.get("aim") is not None:      # that run's change of this club's aim
                pts.append([w, r1(pts[0][1] + float(e["aim"]) - float(v["aim"]))])
        aims[c] = sorted(pts)
    return dict(base=70, pick=rec["pick"], aim=r1(rec["aim"]),
                sweep=[[int(x["width"]), x["pick"]] for x in rec["width_sweep"]],
                flips=[dict(width=r1(f["width"]), frm=f["frm"], to=f["to"]) for f in rec.get("width_flips") or []],
                aims=aims, source="spirit_hollow/v2 (v2_decisions.json): width sweep 55-90, break-evens, sens runs")


def r1(x):
    return None if x is None else round(float(x), 1)


def r4(x):
    return round(float(x), 4)


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------------- shared helpers
def frame(tee, toward, yds):
    tee = np.array(tee, float)
    v = np.array(toward, float) - tee
    ppy = np.linalg.norm(v) / yds
    f = v / np.linalg.norm(v)
    return tee, f, np.array([-f[1], f[0]]), ppy


def axes_px(tee, f, r, ppy, x0, y0, s):
    """Yard frame (along, lat) -> image px:  px = o + along * F + lat * R."""
    o = (np.asarray(tee, float) - [x0, y0]) * s
    return dict(o=[r1(o[0]), r1(o[1])], f=[r4(f[0] * ppy * s), r4(f[1] * ppy * s)],
                r=[r4(r[0] * ppy * s), r4(r[1] * ppy * s)])


def up_bearing(bearing, F):
    """Compass bearing of 'up' on the image, from the tee line's bearing and its px direction."""
    if bearing is None:
        return None
    ang = math.degrees(math.atan2(F[0], -F[1]))           # clockwise angle of the tee line from screen-up
    return round((bearing - ang) % 360, 1)


def cells_array(d, fn=lambda v: v):
    return [fn(d[c]) for c in CELLS]


def compact_grid(holegrid):
    """{cell: {clubs: {c: {...}}}} -> flight {c: [[carry, total, width, drift] per cell]},
    solve {c: [[aim per cell], [ev], [zone lo], [zone hi]]}"""
    clubs = list(holegrid["0_0"]["clubs"])
    flight, solve = {}, {}
    for c in clubs:
        cl = [holegrid[k]["clubs"][c] for k in CELLS]
        flight[c] = [[r1(v["carry"]), r1(v["total"]), r1(v["width"]), r1(v["drift"])] for v in cl]
        solve[c] = [[r1(v["aim"]) for v in cl], [r4(v["ev"]) for v in cl],
                    [r1(v["zone"][0]) for v in cl], [r1(v["zone"][1]) for v in cl]]
    return clubs, flight, solve


def from_live_compact(g):
    """build_wind_page.compact {cell: {c: [aim, ev, zlo, zhi, carry, total, width, drift]}} -> the same."""
    clubs = list(g["0_0"])
    flight, solve = {}, {}
    for c in clubs:
        cl = [g[k][c] for k in CELLS]
        flight[c] = [[r1(a[4]), r1(a[5]), r1(a[6]), r1(a[7])] for a in cl]
        solve[c] = [[r1(a[0]) for a in cl], [r4(a[1]) for a in cl], [r1(a[2]) for a in cl], [r1(a[3]) for a in cl]]
    return clubs, flight, solve


def jpeg_uri(im, quality=74):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def crop_frame(path, box, width=IMG_W, quality=74):
    """box (x0, y0, x1, y1) in the 920 x 2000 frame of `path` -> (uri, s, x0, y0, w, h); s = image px per frame px."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    k = im.width / 920
    x0, y0, x1, y1 = box
    x0, x1 = max(0.0, x0), min(920.0, x1)
    y0, y1 = max(0.0, y0), min(im.height / k, y1)
    c = im.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)))
    scale = min(1.0, width / c.width) if c.width > width else width / c.width
    c = c.resize((max(1, round(c.width * scale)), max(1, round(c.height * scale))), Image.LANCZOS)
    return jpeg_uri(c, quality), scale * k, int(x0 * k) / k, int(y0 * k) / k, c.width, c.height


def forecast_block(fc):
    if not fc or not fc.get("hourly"):
        return None
    days = []
    for day in fc.get("days") or sorted({r["date"] for r in fc["hourly"]}):
        d = dt.date.fromisoformat(day)
        days.append(dict(key=day, label=f"{d.strftime('%a')} {d.month}/{d.day}"))
    rows = [dict(date=r["date"], hour=r["hour"], mph=r1(r["wind_mph"]), gust=r1(r.get("gust_mph") or r["wind_mph"]),
                 dir=r["wind_from_deg"], temp=r1(r.get("temp_f") if r.get("temp_f") is not None else 70),
                 pop=r.get("precip_prob_pct")) for r in fc["hourly"]]
    loc = fc.get("location") or {}
    return dict(fetched=fc.get("fetched_utc"), source="Open-Meteo" + (" (cross-checked with NWS)" if fc.get("nws_hourly") else ""),
                lat=loc.get("lat"), lon=loc.get("lon"), days=days, hourly=rows)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Images:
    """Course-level image table: id -> data URI (each hole image is stored once)."""

    def __init__(self):
        self.d = {}

    def add(self, key, uri):
        self.d[key] = uri
        return key


# ----------------------------------------------------------------------------- second shots (Spirit Hollow)
APPROACH_DIR = os.path.join(ROOT, "spirit_hollow", "approach", "output")


def geo_bearing(a, b):
    from pyproj import Geod
    az, _, _ = Geod(ellps="WGS84").inv(a[0], a[1], b[0], b[1])
    return round(az % 360, 1)


def approach_block(key, rec, gv, imgs):
    """spirit_hollow/approach output for one tee shot -> the app's `approach` block (SCHEMA.md)."""
    import wind_grid as WG
    centre = rec["green"]["centre"]["ll"][0]
    img = imgs.add(f"g{key}", gv["img"])
    P = lambda q: [r1(q[0]), r1(q[1])]                            # noqa: E731

    def boxes(src_rec, src_view):
        out = {}
        for lie, by_w in src_view.items():
            out[lie] = {}
            for w, b in by_w.items():
                full = src_rec[lie][w]
                out[lie][w] = dict(shape=[P(q) for q in b["shape"]], aim=P(b["aim"]), play=r1(b["play"]), lo=r1(b["lo"]),
                                   hi=r1(b["hi"]), aim_text=full.get("aim_text", ""), club=full.get("club", ""),
                                   haz={k: v for k, v in (full.get("haz") or {}).items() if v not in ("rough", "fairway")})
        return out

    def shot(sid, label, frm_ll, box_rec, box_view):
        brg = geo_bearing(frm_ll, centre)
        d0 = float(box_rec["fairway"]["0"]["play"])
        ratio = [r4(WG.plays_like(d0, *[int(x) for x in c.split("_")]) / d0) for c in CELLS]
        return dict(id=sid, label=label, bearing=brg, dist=r1(box_rec["fairway"]["0"]["dist"]), plays_ratio=ratio,
                    boxes=boxes(box_rec, box_view))
    ap = rec["approach"]
    blk = dict(image=img, w=gv["w"], h=gv["h"], ypp=gv["ypp"], up=geo_bearing(rec["box_from"]["ll"][0], centre),
               green=[P(q) for q in gv["green"]], black=bool(rec.get("black", True)),
               green_size=[r1(rec["green"].get("width_yd")), r1(rec["green"].get("depth_yd"))],
               typical=dict(median=r1(ap["median"]), p10=r1(ap["p10"]), p90=r1(ap["p90"]), club=ap.get("club"),
                            lies={k: round(v, 3) for k, v in ap["lie_share"].items() if v >= 0.01},
                            expected=ap.get("expected_strokes")),
               tee=rec.get("tee"), shots=[])
    if "par5" not in rec:
        s = shot("approach", "Approach", rec["box_from"]["ll"][0], rec["boxes"], gv["boxes"])
        sg = rec.get("sg_check") or {}
        if sg:
            s["sg"] = dict(recommend=sg.get("recommend"), cost=sg.get("decade_cost"), play=sg.get("play_sg"),
                           best=P(gv["sg_best"]) if gv.get("sg_best") else None,
                           box=[P(q) for q in gv.get("sg_box", [])], e_box=sg.get("e_decade"), e_best=sg.get("e_best"))
        blk["shots"].append(s)
    else:
        p5, lay = rec["par5"], rec["layup"]
        go = shot("go", "Go for it", rec["go_from"]["ll"][0], rec["go_boxes"], gv["go_boxes"]) if gv.get("go_boxes") else None
        if go:
            gt = rec.get("go_target")
            if gt and gv.get("go_target"):
                go["apron"] = dict(L=gt["L"], off=gt["off"], club=gt.get("club"), shot=r1(gt.get("shot")),
                                   target=P(gv["go_target"]["target"]), zone=[P(q) for q in gv["go_target"]["zone"]])
            blk["shots"].append(go)
        third = shot("third", "Lay up, then wedge", rec["box_from"]["ll"][0], rec["boxes"], gv["boxes"])
        blk["shots"].append(third)
        aims = sorted(p5["go_aims"].items(), key=lambda kv: -kv[1])[:3]
        blk["par5"] = dict(
            p_go=p5["p_go"], p_layup=p5["p_layup"], p_forced=p5["p_forced"], call="go" if p5["p_go"] >= 0.5 else "layup",
            go_up_to={k: int(round(v["go_up_to"])) for k, v in p5["go_rule"].items()},
            green_box_up_to={k: int(round(v["green_box_up_to"])) for k, v in p5["go_rule"].items()},
            go_aims=[[k, v] for k, v in aims if v >= 0.05], margin=p5.get("margin_go_minus_lay"),
            layup=dict(L=lay["L"], off=lay["off"], club=lay.get("club"), shot=r1(lay.get("shot")), ev=lay.get("ev"),
                       lies={k: round(v, 3) for k, v in (lay.get("lie_share") or {}).items() if v >= 0.01},
                       full_wedge_cost=lay.get("full_wedge_cost"), full_wedge_L=lay.get("full_wedge_L"),
                       target=P(gv["layup"]["target"]) if gv.get("layup") else None))
    return blk


# ----------------------------------------------------------------------------- Spirit Hollow (verified)
def build_spirit_hollow():
    import build_wind_page as BW                                   # the live page's builder (unchanged)
    course, yb = BW.course, BW.yb
    yb.use_course("Spirit Hollow GC", os.path.join(ROOT, "spirit_hollow"), "Spirit_Hollow", course.HOLES, course.PAR3,
                  course.NOTES, course.AIM_AT, course.ORDER, course.LABELS)
    out_dir = os.path.join(ROOT, "spirit_hollow", "output")
    grid = json.load(open(os.path.join(out_dir, "wind_grid.json")))
    assert grid["speeds"] == SPEEDS and grid["dirs"] == DIRS, "Spirit Hollow grid axes changed"
    grids = {0: grid}
    for path in glob.glob(os.path.join(out_dir, "wind_grid_back*.json")):
        grids[int(float(re.search(r"back([+-]?[0-9.]+)", path).group(1)))] = json.load(open(path))
    final = json.load(open(os.path.join(out_dir, "final_decision.json")))
    v2 = json.load(open(V2_DECISIONS)) if os.path.exists(V2_DECISIONS) else {}
    apx_path, gv_path = os.path.join(APPROACH_DIR, "approach.json"), os.path.join(APPROACH_DIR, "green_views.json")
    APX = json.load(open(apx_path))["holes"] if os.path.exists(apx_path) else {}
    GV = json.load(open(gv_path))["holes"] if os.path.exists(gv_path) else {}
    fc = json.load(open(os.path.join(CD, "weather", "forecast_spirit_hollow.json")))
    card = json.load(open(os.path.join(CD, "tees", "scorecard.json")))["tee_sets"]
    pkg = json.load(open(os.path.join(PKGS, "spirit_hollow", "package.json")))
    imgs = Images()
    holes = {}
    for h in course.ORDER:
        d = BW.par3_hole(h) if h in course.PAR3 else BW.tee_hole(h)
        key = str(h)
        base, opts = BW.tee_options(h)
        if h in course.PAR3:                                       # exactly what build_wind_page.main() adds
            d["by_set"] = BW.par3_sets(h, opts, grid)
        else:
            d["grids"] = {str(b): BW.compact(g["holes"][key]) for b, g in sorted(grids.items()) if key in g.get("holes", {})}
            d["cloud"] = BW.clouds(h, grid["holes"][key])
            fd = final.get(key)
            if fd and fd.get("tie") is not None:
                d["calm"] = dict(pick=fd["pick"], aim=fd["aim"], tie=bool(fd["tie"]), margin=fd["margin"],
                                 flips=fd.get("width_flips", []))
        no = int(re.match(r"\d+", key).group(0))
        vid = key[len(str(no)):] or "main"
        bearing = grid["bearings"].get(key)
        img_id = imgs.add(f"h{key}", d["img"])
        if d["kind"] == "tee":
            ax = axes_px(d["tee"], d["f"], d["r"], d["ppy"], d["x0"], d["y0"], d["s"])
        else:
            p = course.PAR3[h]
            tee, f, r, ppy = frame(p["tee"], p["flag"], p["center"])
            ax = axes_px(tee, f, r, ppy, d["x0"], d["y0"], d["s"])
        P = lambda q: [r1((q[0] - d["x0"]) * d["s"]), r1((q[1] - d["y0"]) * d["s"])]  # noqa: E731
        v = dict(kind=d["kind"], image=img_id, w=d["w"], h=d["h"], axes=ax, bearing=bearing,
                 up=up_bearing(bearing, ax["f"]), length=r1(d["length"]), tee_label=f"{base} tee",
                 note=d.get("note", ""), aim_at=d.get("aim_at", ""), off_image_below=None)
        if d["kind"] == "tee":
            if d.get("tee_offimage"):
                v["off_image_below"] = r1((2000 - d["y0"]) * d["s"])
            offs = {}
            flight0 = None
            for b, g in sorted(d["grids"].items(), key=lambda kv: int(kv[0])):
                clubs, flight, solve = from_live_compact(g)
                if flight0 is None:
                    flight0 = flight
                elif any(flight[c] != flight0[c] for c in clubs):
                    raise SystemExit(f"Spirit Hollow {key}: club flight differs between tee offsets")
                offs[str(b)] = solve
            v.update(clubs=clubs, flight=flight0, offsets=offs, cloud=d.get("cloud") or {}, mapped_along=345,
                     elev=d.get("elev"), check=[])
            fd = final.get(key)
            v["calm"] = dict(pick=d["calm"]["pick"], aim=d["calm"]["aim"], tie=d["calm"]["tie"],
                             margin=r4(d["calm"]["margin"]),
                             flips=[dict(width=r1(x["width"]), frm=x["frm"], to=x["to"]) for x in d["calm"].get("flips", [])],
                             source="full Bayesian run (final_decision.json)") if d.get("calm") else None
            if fd and v["calm"] and fd.get("zone"):
                v["calm"]["zone"] = fd["zone"]
            wr = width_rule(v2.get(key))
            if wr:
                v["width_rule"] = wr
            if key in APX and key in GV:
                v["approach"] = approach_block(key, APX[key], GV[key], imgs)
        else:
            v["green"] = [P(q) for q in d["green"]]
            v["elev"] = d.get("elev")
            v["sets"] = {}
            for name, S in d["by_set"].items():
                v["sets"][name] = dict(center=r1(S["center"]), front=r1(S["front"]), back=r1(S["back"]),
                                       plays=[r1(S["plays"][c]) for c in CELLS],
                                       boxes={m: dict(poly=[P(q) for q in b["poly"]], play=r1(b["play"]), lo=r1(b["lo"]),
                                                      hi=r1(b["hi"])) for m, b in S["boxes"].items()})
            v["short"] = d.get("short", "")
        H = holes.setdefault(no, dict(no=no, ref=str(no), par=d["par"], hcp=None, variants={}, tees={},
                                      confidence=dict(level="verified", lines=["Hand-checked map (GPS-app screenshots "
                                                      "traced hole by hole); calm pick from the full Bayesian run."])))
        H["variants"][vid] = v
        for o in opts:
            H["tees"][o["name"]] = dict(variant=vid, yards=o["yards"], back=o["back"])
    hcp = {int(k): h.get("hcp") for k, h in pkg["holes"].items()}
    for no, H in holes.items():
        H["hcp"] = hcp.get(no)
    sets = []
    for name in BW.SETS:
        c = card[name]
        sets.append(dict(name=name, colour=COLOURS.get(name.lower(), "#888"), yards=c["yards"], total=sum(c["yards"]),
                         rating=c.get("rating"), slope=c.get("slope"), computed="offset" if name != "Black" else "exact",
                         note=("Planned from the Black tee" if name == "Black" else
                               f"Black-tee map; the tee moves along the line by the card difference, re-solved every 20 yds"
                               + ("; holes 2 and 9 use the Gold-box screenshots" if name == "Gold" else ""))))
    return dict(
        id="spirit_hollow", name="Spirit Hollow Golf Course", short="Spirit Hollow", town="Burlington", state="IA",
        lat=fc["location"]["lat"], lon=fc["location"]["lon"],
        confidence=dict(level="verified", summary="Verified: hand-checked map from the golfer's GPS-app screenshots, "
                        "USGS lidar elevation, full Bayesian club picks.", red=0, amber=0, check_holes=0),
        default_tee="Black", tee_sets=sets, forecast=forecast_block(fc), pace_min_per_hole=PACE_MIN,
        imagery="GPS-app screenshots with the app's markings removed (hole 3: 2023 aerial photo)",
        attribution=["Hole maps traced from the golfer's GPS-app screenshots", "USGS 3DEP (public domain)",
                     "Forecast: Open-Meteo (CC BY 4.0), NWS"],
        model="Fawcett-style strokes-gained simulation (mozingo/tee_strategy.py); wind from published TrackMan/"
              "Ping/Foresight figures and a ball-flight model; par 3s: DECADE target boxes.",
        checks=[], images=imgs.d, holes=[holes[k] for k in sorted(holes)], mapping="hand", confirm=None)


# ----------------------------------------------------------------------------- auto courses (packages)
def plan_dirs(slug):
    """{tee set: out dir} for every finished plan of a package (out/, out_<set>/; not out_full)."""
    res = {}
    for od in sorted(glob.glob(os.path.join(PKGS, slug, "out*"))):
        if os.path.basename(od) == "out_full":
            continue
        need = ("decision.json", "wind_grid.json", "course.py", "plan.json", "screenshots/index.json")
        if not all(os.path.exists(os.path.join(od, n)) for n in need):
            continue
        ts = json.load(open(os.path.join(od, "plan.json"))).get("tee_set")
        if ts and ts not in res:
            res[ts] = od
    return res


def clouds_for(mod, grid, holes):
    """Simulated finishing pattern per club at the calm aim (the live page's clouds(), course-agnostic)."""
    import decide
    import tee_strategy as t
    import yardage_book as yb
    decide.bind(mod.HOLES)
    decide.set_prior_means()
    out = {}
    for h in holes:
        hg = grid["holes"][str(h)]
        elev = mod.HOLES[h].get("elev", {}) or {}
        res = {}
        for c, v in hg["0_0"]["clubs"].items():
            try:
                cl = yb.shot_cloud(h, c, v["aim"], n=4000)
            except Exception as e:                                # noqa: BLE001
                log(f"    cloud {h} {c}: {e}")
                cl = None
            if not cl:
                continue
            dc, rf, kick = elev.get(c, (0.0, 1.0, 0.0))
            page_total = (v["carry"] + dc) + (v["total"] - v["carry"]) * rf
            (A, Bm), (u, w) = cl["axes"], cl["vec"]
            res[c] = dict(dA=r1(cl["along"] - page_total), dL=r1(cl["lat"] - (v["aim"] + kick)), A=r1(A), B=r1(Bm),
                          u=[r4(x) for x in u], w=[r4(x) for x in w], width=r1(v["width"]))
        out[h] = res
    t.HOLES = {}
    return out


def strip_badge(note, line):
    note = note or ""
    if line:
        for pre in ("⚠ " + line, line):
            if note.startswith(pre):
                return note[len(pre):].strip()
    return re.sub(r"^⚠ Unverified:.*?(?:yds? (?:right|left)\.|on the line\.|harder\.|easier\.)\s*", "", note)


def plan_geo(ph, primary):
    """Where the plan's hole n is (the package's line, WGS84): the confirm step matches a routed hole to it
    (routing.score's rule: green within 20 yds, tee within 40 yds of the line's first 60 %)."""
    line = ph.get("hole_line_ll") or []
    tee = ((ph.get("tees") or {}).get(primary) or {}).get("tee_ll") or (line[0] if line else None)
    if not line or not ph.get("green_ll"):
        return None
    return dict(tee_ll=[round(x, 7) for x in tee], green_ll=[round(x, 7) for x in ph["green_ll"]],
                line=[[round(x, 7) for x in q] for q in line])


def confirm_block(slug, pkg):
    """The golfer-confirm data for a package course (course_data/app/pools/<slug>.json, confirm_pool.py), or None."""
    path = os.path.join(POOLS, f"{slug}.json")
    if not os.path.exists(path):
        return None
    pool = json.load(open(path))
    ov = pool.pop("overview", None)
    card_known = bool(pool.get("card"))
    typed = []
    tp = os.path.join(POOLS, "typed", f"{slug}.json")
    if os.path.exists(tp):                       # the pool re-solved with the package request's card
        t = json.load(open(tp))
        t.pop("overview", None)
        typed.append(t)
    return dict(pool=pool, overview=ov, card_known=card_known, typed_pools=typed,
                card_note=None if card_known else (
                    "No scorecard was found online for this course (golfify, the club site and OpenGolfAPI were "
                    "tried). Type the yardages from your card and the hole order gets much better."))


def build_package(slug, entry):
    from render import Frame
    pkg = json.load(open(os.path.join(PKGS, slug, "package.json")))
    plans = plan_dirs(slug)
    if not plans:
        return None
    primary = pkg.get("tee_set") if pkg.get("tee_set") in plans else next(iter(plans))
    log(f"  {slug}: plans {', '.join(f'{k} ({os.path.relpath(v, ROOT)})' for k, v in plans.items())}; primary {primary}")
    P = {}
    for ts, od in plans.items():
        mod = load_module(os.path.join(od, "course.py"), f"app_course_{slug}_{ts.lower()}")
        P[ts] = dict(dir=od, mod=mod, grid=json.load(open(os.path.join(od, "wind_grid.json"))),
                     dec=json.load(open(os.path.join(od, "decision.json"))),
                     plan=json.load(open(os.path.join(od, "plan.json"))),
                     shots=json.load(open(os.path.join(od, "screenshots", "index.json"))))
        g = P[ts]["grid"]
        assert g["speeds"] == SPEEDS and g["dirs"] == DIRS, f"{slug} {ts}: grid axes changed"
        tee_holes = [h for h in mod.HOLES if str(h) in g["holes"]]
        P[ts]["clouds"] = clouds_for(mod, g, tee_holes)
    main = P[primary]
    pr_mod = main["mod"]
    review_path = os.path.join(plans[primary], "review", "review.json")
    review = json.load(open(review_path)) if os.path.exists(review_path) else None
    badges = main["plan"].get("badges") or {}
    imgs = Images()
    fc_path = os.path.join(plans[primary], "forecast.json")
    fc = json.load(open(fc_path)) if os.path.exists(fc_path) else None
    holes = []
    for h in pr_mod.ORDER:
        k = str(h)
        ph = pkg["holes"][k]
        par = ph.get("par")
        frames = {ts: Frame.from_json(P[ts]["shots"][k]["frame"]) for ts in P if k in P[ts]["shots"]}
        F0 = frames[primary]
        # every set's yard frame -> primary frame px (an exact similarity: both are UTM-based rotations)

        def to_primary(ts, pts):
            pts = np.atleast_2d(np.asarray(pts, float))
            return F0.ll_to_px(frames[ts].px_to_ll(pts)) if ts != primary else pts
        variants, tees = {}, {}
        is3 = h in pr_mod.PAR3
        # crop box in the primary frame
        if is3:
            gpts = []
            for ts in P:
                p = P[ts]["mod"].PAR3[h]
                tee, f, r, ppy = frame(p["tee"], p["flag"], p["center"])
                g = np.array(p["green"], float)
                gpts += list(to_primary(ts, [tee + ((p["center"] + d) * f + l * r) * ppy for l, d in g]))
            gpts = np.array(gpts)
            pad = 16 * F0.ppy
            box = (gpts[:, 0].min() - pad, gpts[:, 1].min() - pad, gpts[:, 0].max() + pad, gpts[:, 1].max() + pad)
            width = 480
        else:
            pts = []
            for ts in P:
                hd = P[ts]["mod"].HOLES[h]
                tee, f, r, ppy = frame(hd["tee"], hd["dot270"], 270)
                aims = [v["aim"] for v in P[ts]["dec"][k]["clubs"].values()]
                lo, hi = min(min(aims) - 65, -75), max(max(aims) + 65, 75)
                far = min(float(hd["length"]) + 20, 560)
                pts += list(to_primary(ts, [tee + (a * f + l * r) * ppy for a in (-18, far) for l in (lo, hi)]))
            pts = np.array(pts)
            box = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
            width = IMG_W
        img_path = os.path.join(plans[primary], "screenshots", P[primary]["shots"][k]["image"])
        uri, s, x0, y0, w, hh = crop_frame(img_path, box, width=width)
        img_id = imgs.add(f"h{k}", uri)
        up = None
        for ts in P:
            mod, g, dec = P[ts]["mod"], P[ts]["grid"], P[ts]["dec"]
            bearing = g["bearings"].get(k)
            if is3:
                p = mod.PAR3[h]
                tee, f, r, ppy = frame(p["tee"], p["flag"], p["center"])
            else:
                hd = mod.HOLES[h]
                tee, f, r, ppy = frame(hd["tee"], hd["dot270"], 270)
            # the set's tee, 100 yds along and 100 yds right, mapped into the primary image
            q = to_primary(ts, [tee, tee + 100 * f * ppy, tee + 100 * r * ppy])
            o = (q[0] - [x0, y0]) * s
            ax = dict(o=[r1(o[0]), r1(o[1])], f=[r4((q[1] - q[0])[0] * s / 100), r4((q[1] - q[0])[1] * s / 100)],
                      r=[r4((q[2] - q[0])[0] * s / 100), r4((q[2] - q[0])[1] * s / 100)])
            if ts == primary:
                up = up_bearing(bearing, ax["f"])
            notes_line = (P[ts]["plan"].get("badges") or {}).get(k, {}).get("line") if ts == primary else None
            v = dict(kind="par3" if is3 else "tee", image=img_id, w=w, h=hh, axes=ax, bearing=bearing, up=None,
                     length=r1((mod.PAR3[h]["center"] if is3 else mod.HOLES[h]["length"])), tee_label=f"{ts} tee",
                     note=strip_badge(mod.NOTES.get(h, ""), notes_line), aim_at=mod.AIM_AT.get(h, ""),
                     off_image_below=None)
            el = (ph.get("elevation") or {}).get("adjustments") or {}
            same_set = ts == pkg.get("tee_set")
            if is3:
                p = mod.PAR3[h]
                import yardage_book as yb
                gp = [tee + ((p["center"] + dd) * f + l * r) * ppy for l, dd in p["green"]]
                Pp = lambda pts: [[r1(a), r1(b)] for a, b in (to_primary(ts, pts) - [x0, y0]) * s]  # noqa: E731
                boxes = {}
                for m in (-1, 0, 1, 2, 3):
                    yb.WIND_NOW = m
                    plan = yb.par3_plan(p)
                    (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
                    if l1 - l0 < 2:
                        l0, l1 = (l0 + l1) / 2 - 1, (l0 + l1) / 2 + 1
                    if d1 - d0 < 2:
                        d0, d1 = (d0 + d1) / 2 - 1, (d0 + d1) / 2 + 1
                    corners = [tee + ((p["center"] + dd) * f + l * r) * ppy for l, dd in ((l0, d0), (l1, d0), (l1, d1), (l0, d1))]
                    boxes[str(m)] = dict(poly=Pp(corners), play=r1(p["center"] + plan["aim"][1]),
                                         lo=r1(p["center"] + plan["dep"][0]), hi=r1(p["center"] + plan["dep"][1]))
                yb.WIND_NOW = 0
                dz = el.get("plays_like_delta_yds") or 0.0
                v["green"] = Pp(gp)
                v["elev"] = dict(green_drop=el.get("green_drop_ft"), dz=dz,
                                 approx=not same_set) if el.get("green_drop_ft") is not None else None
                v["sets"] = {ts: dict(center=r1(p["center"]), front=r1(p["front"]), back=r1(p["back"]),
                                      plays=[r1(g["par3"][k][c] + dz) for c in CELLS], boxes=boxes)}
                v["short"] = p.get("short", "")
            else:
                clubs, flight, solve = compact_grid(g["holes"][k])
                ce = mod.HOLES[h].get("elev") or {}
                drops = {c: x.get("landing_drop_ft") for c, x in (el.get("clubs") or {}).items()} if same_set else {}
                v.update(clubs=clubs, flight=flight, offsets={"0": solve}, cloud=P[ts]["clouds"].get(h, {}),
                         elev=dict(clubs={c: dict(dc=r1(e[0]), rf=round(float(e[1]), 3), kick=r1(e[2]), drop=r1(drops.get(c)))
                                          for c, e in ce.items()}) if ce else None)
                dk = dec[k]
                v["calm"] = dict(pick=dk["pick"], aim=dk["aim"], tie=bool(dk.get("tie")), margin=r4(dk["margin"]),
                                 zone=dk.get("zone"), flips=[], source=f"quick plan (n={dk.get('n')}, central settings)")
                v["check"] = list(dk.get("check") or [])
                if hd.get("tee") is not None and hd["tee"][1] > 1990:
                    v["off_image_below"] = r1((2000 - y0) * s)
            variants[ts] = v
            yards = (pkg["tee_sets"].get(ts, {}).get("yards") or [None] * 18)
            tees[ts] = dict(variant=ts, yards=yards[int(k) - 1] if len(yards) >= int(k) else None, back=0)
        for v in variants.values():
            v["up"] = up
        # confidence: the product's CHECK flags (decision.json) + the 2-minute check's badges (review.json)
        lines, level = [], "auto"
        b = badges.get(k) or {}
        for ts in variants:                                       # every tee set's own CHECK flags
            if not is3 and variants[ts].get("check"):
                level = "check"
                lines.append(f"CHECK ({ts} tees): the plan's safety guard flagged this tee shot; the best printable aim "
                             "is shown. " + "; ".join(variants[ts]["check"]))
        if b.get("state") == "unverified":
            level = "check"
            lines.append(b.get("line", ""))
        gv = ph.get("green_visibility") or {}
        if gv.get("visible") is False:                           # package.check_green_visibility
            level = "check"
            lines.append(f"The green does not show on the {gv.get('year')} aerial photo (bare soil or construction "
                         "when it was flown): the dashed outline is where OpenStreetMap puts it.")
        conf = (ph.get("confidence") or {})
        holes.append(dict(no=int(k), ref=k, par=par, hcp=ph.get("hcp"), variants=variants, tees=tees,
                          confidence=dict(level=level, lines=[x for x in lines if x], map_score=conf.get("score"),
                                          flags=conf.get("flags", [])),
                          geo=plan_geo(ph, primary)))
    # pre-round check cards (red and amber items of out/review/review.json)
    checks, red, amber = [], 0, 0
    if review:
        for it in review["items"]:
            if it.get("severity") not in ("red", "amber"):
                continue
            red += it["severity"] == "red"
            amber += it["severity"] == "amber"
            opts = []
            for o in it.get("options", []):
                oc = o.get("outcome")
                opts.append(dict(answer=o["answer"], label=o.get("label"), text=o.get("text") or "; ".join(
                    s.get("text", "") for s in (o.get("samples") or [])[:2]),
                    outcome=dict(pick=oc["pick"], aim=oc.get("aim_frame", oc.get("aim")), club_changed=oc.get("club_changed"),
                                 d_ev=oc.get("d_ev")) if oc and oc.get("pick") else None))
            card = dict(id=it["id"], hole=int(it["hole"]), severity=it["severity"], type=it["type"],
                        question=it["question"], detail=it.get("detail", ""), p_wrong=it.get("p_wrong"),
                        worst_regret=it.get("worst_regret"), options=opts, tee_set=review.get("tee_set"))
            cr = it.get("crop")
            if cr and it["severity"] == "red":
                ov = cr.get("overlay") or {}
                card["crop"] = dict(img=cr["img"], w=cr["w"], h=cr["h"], overlay=dict(
                    polys=ov.get("polys", []), line=ov.get("line"), tee=ov.get("tee"), target=ov.get("target"),
                    ellipse=ov.get("ellipse"), pick=ov.get("pick")))
            checks.append(card)
    sev = {"red": 0, "amber": 1}
    checks.sort(key=lambda c: (sev[c["severity"]], -(c.get("worst_regret") or 0)))
    for H in holes:
        mine = [c for c in checks if c["hole"] == H["no"]]
        if any(c["severity"] == "red" for c in mine) and H["confidence"]["level"] != "check":
            H["confidence"]["level"] = "check"
        H["confidence"]["items"] = [c["id"] for c in mine]
    sets = []
    for name, ts in pkg["tee_sets"].items():
        sets.append(dict(name=name, colour=COLOURS.get((ts.get("colour") or name).lower(), "#888"), yards=ts.get("yards"),
                         total=ts.get("total"), rating=ts.get("rating"), slope=ts.get("slope"),
                         computed="exact" if name in plans else "missing",
                         note=("Planned from this tee" if name in plans else
                               "Not planned yet (needs a plan run for this tee set)")))
    sets.sort(key=lambda s: -(s["total"] or 0))
    n_check = sum(1 for H in holes if H["confidence"]["level"] == "check")
    c = pkg["course"]
    ti = pkg.get("tee_set_info") or {}
    summary = (f"Auto-mapped from OpenStreetMap + USDA NAIP {pkg['imagery'].get('year', '')} imagery + USGS lidar; "
               f"quick-mode club picks. {n_check} hole{'s' if n_check != 1 else ''} to check before you play.")
    if ti.get("warning"):
        summary += " " + ti["warning"].capitalize() + "."
    short = re.sub(r"\s+(Golf Course|Golf Club|Country Club|Memorial Golf Course)$", "", c["name"])
    if slug == "veenker":
        short = "Veenker"
    loc = (fc or {}).get("location") or {}
    return dict(
        id=slug, name=c["name"], short=short, town=c.get("town"), state=c.get("state"),
        lat=loc.get("lat", c["center"][1]), lon=loc.get("lon", c["center"][0]),
        confidence=dict(level="auto", summary=summary, red=red, amber=amber, check_holes=n_check,
                        map_score=entry.get("summary", {}).get("mean_confidence")),
        default_tee=primary, tee_sets=sets, forecast=forecast_block(fc), pace_min_per_hole=PACE_MIN,
        imagery=f"USDA NAIP {pkg['imagery'].get('naip_date') or pkg['imagery'].get('year')} (0.3-0.6 m), re-projected so each tee line runs up the screen"
                + (f". Year: {(pkg['imagery'].get('selection') or {}).get('reason')}"
                   if (pkg['imagery'].get('selection') or {}).get("reason") else ""),
        attribution=pkg.get("attribution", []) + ["Forecast: Open-Meteo (CC BY 4.0)"],
        model="Fawcett-style strokes-gained simulation at the model's central settings (quick mode); wind from "
              "published TrackMan/Ping/Foresight figures and a ball-flight model; par 3s: DECADE target boxes.",
        checks=checks, images=imgs.d, holes=holes, mapping="auto", confirm=confirm_block(slug, pkg))


# ----------------------------------------------------------------------------- catalogue + page
def catalog(built_ids):
    states, upcoming = [], []
    names = {re.sub(r"[^a-z]", "", n) for n in built_ids}
    for path in sorted(glob.glob(os.path.join(PKGS, "_survey", "*.json"))):
        s = json.load(open(path))
        states.append(dict(state=s["state"], n_courses=s["n_courses"], n_with_holes=s["n_with_holes"],
                           n_18_holes=s.get("n_18_holes"), surveyed=s.get("surveyed_utc")))
        for c in s["courses"]:
            holes = (c.get("counts") or {}).get("hole", 0)
            if holes < 9 or not c.get("name"):
                continue
            if re.sub(r"[^a-z]", "", c["name"].lower()) in names:
                continue
            upcoming.append([c["name"], c.get("town") or "", s["state"], holes])
    return dict(states=states, n_courses=sum(s["n_courses"] for s in states),
                n_with_holes=sum(s["n_with_holes"] for s in states), upcoming=upcoming)


def _norm(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower().replace("&", "and"))


def _tees(tee_sets):
    """{name: {colour, total}} -> [[name, hex colour, total yds]], longest first."""
    out = []
    for name, ts in (tee_sets or {}).items():
        out.append([name, COLOURS.get(str(ts.get("colour") or name).split()[0].lower(), "#888"), ts.get("total")])
    return sorted(out, key=lambda t: -(t[2] or 0))


def _status_of(raw):
    """a library/index.json status string -> the page's status key"""
    s = str(raw or "").lower()
    if "hand" in s or "verified" in s or "truth" in s:
        return "hand"
    if "confirm" in s or "check" in s:
        return "confirm"
    if "auto" in s or s in ("ok", "ready"):
        return "auto"
    return "none"


def library(courses):
    """Every course the page knows, light (golf_library/1, SCHEMA.md "Library"): the courses playable in this page,
    the hand-checked tournament courses (a link to their wind page), the course packages without a plan yet, and the
    IA / MO OpenStreetMap survey. course_data/library/index.json (when present) adds courses and fills gaps.
    Entry: {id, name, town, state, holes, status, tees: [[name, colour, yds]], app, link, event, note, src}
      status: "hand" (hand-checked) | "auto" (auto-mapped; the page re-derives auto-OK / needs-confirm from the
              hole-map confirm, shared confirmations included) | "confirm" (needs confirm, from the library index)
              | "none" (not built yet)"""
    ents, seen = [], {}

    def add(e):
        k = _norm(e["name"]) + "|" + (e.get("state") or "")
        if k in seen:
            old = seen[k]
            for f, v in e.items():
                if old.get(f) in (None, "", []) and v not in (None, "", []):
                    old[f] = v
            return old
        e.setdefault("tees", [])
        seen[k] = e
        ents.append(e)
        return e
    for c in courses:                                   # 1. playable here
        add(dict(id=c["id"], name=c["name"], town=c.get("town"), state=c.get("state"), holes=len(c["holes"]),
                 status="hand" if c["mapping"] == "hand" else "auto",
                 tees=[[t["name"], t["colour"], t["total"], int(t["computed"] != "missing")] for t in c["tee_sets"]], app=c["id"],
                 link=WIND_PAGES.get(c["id"]), src="app",
                 note="Hand-checked map: GPS-app screenshots traced hole by hole" if c["mapping"] == "hand" else
                      "Auto-mapped (OpenStreetMap + NAIP + lidar); golfers confirm the hole order"))
    for cfg_path in sorted(glob.glob(os.path.join(COURSES_DIR, "*", "config.json"))):   # 2. hand-checked wind pages
        slug = os.path.basename(os.path.dirname(cfg_path))
        if slug not in WIND_PAGES:
            continue
        cfg = json.load(open(cfg_path))
        tp = os.path.join(COURSES_DIR, slug, "truth", "package.json")
        pk = json.load(open(tp)) if os.path.exists(tp) else json.load(open(os.path.join(PKGS, slug, "package.json")))
        c = pk.get("course") or {}
        days = cfg.get("day_labels") or []
        add(dict(id=slug, name=cfg.get("name") or c.get("name"), town=c.get("town") or c.get("city"), state=c.get("state"),
                 holes=len(pk.get("holes") or {}) or 18, status="hand", tees=_tees(pk.get("tee_sets")), app=None,
                 link=WIND_PAGES[slug], event=(cfg.get("event") or "") + (f" · {' & '.join(days)}" if days and "(" not in (cfg.get("event") or "") else ""),
                 note="Hand-checked map with its own wind page (club and aim in the event's forecast)", src="wind_page"))
    idx = json.load(open(os.path.join(PKGS, "_index.json")))
    for slug, entry in sorted(idx.items()):              # 3. packages without a plan
        pj = os.path.join(PKGS, slug, "package.json")
        if entry.get("status") != "ok" or not os.path.exists(pj):
            continue
        pk = json.load(open(pj))
        c = pk.get("course") or {}
        add(dict(id=slug, name=c.get("name") or entry.get("name"), town=c.get("town") or entry.get("town"),
                 state=c.get("state") or entry.get("state"), holes=len(pk.get("holes") or {}), status="none",
                 tees=_tees(pk.get("tee_sets")), app=None, link=None, src="package",
                 note="Mapped automatically (course package built); the club-and-aim plan has not been run yet"))
    lib_src = None
    if os.path.exists(LIBRARY_INDEX):                    # 4. the course library (course_library/1, library/README.md)
        try:
            li = json.load(open(LIBRARY_INDEX))
            rows = li.get("courses", li) if isinstance(li, dict) else li
            rows = list(rows.values()) if isinstance(rows, dict) else rows
            n0 = len(ents)
            for r in rows:
                if not isinstance(r, dict) or not r.get("name"):
                    continue
                tees = r.get("tees") or r.get("tee_sets") or []
                if isinstance(tees, dict):
                    tees = _tees(tees)
                elif tees and isinstance(tees[0], dict):    # {name, yards, colour, on_page: solved | offset | null}
                    tees = [[t.get("name"), COLOURS.get(str(t.get("colour") or t.get("color") or t.get("name") or "").split(" ")[0].lower(), "#888"),
                             t.get("total") or t.get("yards")] + ([int(bool(t["on_page"]))] if "on_page" in t else [])
                            for t in tees]
                tees = [list(t)[:4] for t in tees if isinstance(t, (list, tuple)) and t and t[0]][:10]
                slug = r.get("id") or r.get("slug")
                status = _status_of(r.get("status"))
                link = r.get("link") or r.get("url") or WIND_PAGES.get(slug)
                chk = [int(h) for h in (r.get("check_holes") or []) if str(h).isdigit()]
                why = "; ".join(str(x) for x in (r.get("reasons") or [])[:3])
                note = r.get("note") or (
                    f"Auto-mapped wind page; confirm hole{'s' if len(chk) != 1 else ''} {', '.join(map(str, chk))}" + (f" ({why})" if why else "")
                    if status == "confirm" and chk else
                    "Auto-mapped wind page: every hole passed the picture checks" if status == "auto" else
                    f"Not built: {why}" if str(r.get("status")).lower() == "failed" and why else "")
                if r.get("page") and not link and status != "none":
                    note += (" · " if note else "") + "page built, not published yet"
                e = add(dict(id=slug, name=r["name"], town=r.get("town") or r.get("city"),
                             state=r.get("state"), holes=r.get("holes") or r.get("n_holes"),
                             status=status, tees=tees, app=None, link=link, note=note, src="library"))
                if e.get("src") == "wind_page" and tees:     # the index knows which sets the wind page shows
                    e["tees"] = tees
                if e.get("src") != "app" and str(r.get("status")).lower() == "failed":
                    e["status"] = "none"
            lib_src = dict(path=os.path.relpath(LIBRARY_INDEX, ROOT), n=len(rows), added=len(ents) - n0,
                           updated=li.get("updated") if isinstance(li, dict) else None)
        except Exception as e:                           # noqa: BLE001
            log(f"  library/index.json not used: {e}")

    survey = []
    for path in sorted(glob.glob(os.path.join(PKGS, "_survey", "*.json"))):   # 5. the OSM survey
        s = json.load(open(path))
        survey.append(dict(state=s["state"], n_courses=s["n_courses"], n_with_holes=s["n_with_holes"]))
        for c in s["courses"]:
            holes = (c.get("counts") or {}).get("hole", 0)
            if holes < 9 or not c.get("name"):
                continue
            add(dict(id=None, name=c["name"], town=c.get("town") or "", state=s["state"], holes=holes, status="none",
                     tees=[], app=None, link=None, src="survey", note=f"{holes} holes mapped on OpenStreetMap"))
    for e in ents:                                        # compact: drop empty fields
        for k in [k for k, v in e.items() if v in (None, "", [])]:
            del e[k]
    return dict(schema="golf_library/1", entries=ents, survey=survey, index=lib_src,
                states=sorted({e["state"] for e in ents if e.get("state")}))


def artifact_format(html):
    """The artifact page contract: no doctype / html / head / body / charset / viewport tags (the host wraps
    the page), <title> first."""
    head, sep, rest = html.partition("<script>")
    for pat in (r"<!doctype html>\s*", r"</?html[^>]*>\s*", r"</?head>\s*", r"</?body>\s*",
                r'<meta charset="[^"]*">\s*', r'<meta name="viewport"[^>]*>\s*'):
        head = re.sub(pat, "", head, flags=re.I)
    tail = re.sub(r"\s*</body>\s*</html>\s*$", "\n", rest, flags=re.I)
    m = re.search(r"<title>.*?</title>\s*", head, flags=re.S)
    head = m.group(0).strip() + "\n" + head[:m.start()] + head[m.end():]
    return head + sep + tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--json", help="also write one golf_app/1 course document per course into this dir")
    a = ap.parse_args()
    courses = []
    log("Spirit Hollow (verified: live page data)")
    courses.append(build_spirit_hollow())
    idx = json.load(open(os.path.join(PKGS, "_index.json")))
    for slug, entry in sorted(idx.items()):
        if slug == "spirit_hollow" or entry.get("status") != "ok":
            continue
        log(f"{slug} (auto package)")
        c = build_package(slug, entry)
        if c:
            courses.append(c)
    bundle = dict(schema="golf_app/1", built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                  wind_axes=dict(speeds=SPEEDS, dirs=DIRS, cells=CELLS), player=PLAYER,
                  catalog=catalog([c["name"].lower() for c in courses]), library=library(courses), courses=courses)
    bundle["catalog"].pop("upcoming", None)              # the library carries those courses now
    log("library play records (out/lib/<slug>.json, fetched by the page; build_library_play.py)")
    import build_library_play
    lib_dir = os.path.join(os.path.dirname(a.out), "lib")
    played = build_library_play.build(lib_dir, log=log)
    for e in bundle["library"]["entries"]:
        x = played.get(e.get("id")) if not e.get("app") else None
        if x:
            e["lib"] = x["file"]
            e["checks"] = x["check_holes"]
            e["holes"] = x["holes"]
    log(f"  {len(played)} library courses playable, {sum(x['bytes'] for x in played.values()) / 1e6:.1f} MB in {os.path.relpath(lib_dir, ROOT)}")
    if a.json:
        os.makedirs(a.json, exist_ok=True)
        for c in courses:
            with open(os.path.join(a.json, f"{c['id']}.json"), "w") as fh:
                json.dump(dict(schema="golf_app/1#course", wind_axes=bundle["wind_axes"], player=PLAYER, course=c), fh)
    blob = json.dumps(bundle, separators=(",", ":")).replace("</", "<\\/")
    engine = "\n".join(open(p).read() for p in ENGINE_JS).replace("</", "<\\/")
    import course_index                                   # national index (course_index.py, SCHEMA.md)
    engine, natidx = course_index.inject(engine)
    log(f"  national index: {natidx['n']} courses, {len(natidx['b64']) / 1e6:.2f} MB" if natidx else "  national index: none yet")
    libplay = open(LIBPLAY_JS).read().replace("</", "<\\/")
    html = open(TEMPLATE).read().replace("/*__ENGINE__*/", engine).replace("/*__LIBPLAY__*/", libplay).replace("/*__DATA__*/null", blob)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        fh.write(html)
    log(f"wrote {os.path.relpath(a.out, ROOT)} {os.path.getsize(a.out) / 1e6:.2f} MB")
    art = os.path.join(os.path.dirname(a.out), "aim_caddie.html")
    with open(art, "w") as fh:
        fh.write(artifact_format(html))
    log(f"wrote {os.path.relpath(art, ROOT)} {os.path.getsize(art) / 1e6:.2f} MB (artifact format)")
    L = bundle["library"]
    by = {}
    for e in L["entries"]:
        by[e["status"]] = by.get(e["status"], 0) + 1
    log(f"  library: {len(L['entries'])} courses {by}, {len(json.dumps(L, separators=(',', ':'))) / 1e3:.0f} kB"
        + (f"; library/index.json: {L['index']}" if L["index"] else "; no library/index.json yet"))
    for c in courses:
        n = len(json.dumps(c, separators=(",", ":")))
        im = sum(len(u) for u in c["images"].values()) + sum(len(json.dumps(x.get("crop", ""))) for x in c["checks"])
        log(f"  {c['id']:14s} {n / 1e6:5.2f} MB (images {im / 1e6:.2f} MB), {len(c['holes'])} holes, "
            f"sets {[s['name'] + ':' + s['computed'] for s in c['tee_sets']]}, checks {len(c['checks'])}")


if __name__ == "__main__":
    main()
