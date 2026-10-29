"""The spirit_hollow/v2 engine and v2 wind page for any course (tournament courses in course_data/courses/<slug>/).

  python3 course_data/courses/v2_course.py prepare --slug pine_dunes --which auto|truth
        package (config.json "package" / "truth_package") -> <slug>/<which>/course.py + screenshots/ + meta.json
  python3 course_data/courses/v2_course.py decide  --slug S --which W [--holes 1,2] --out parts/x.json
  python3 course_data/courses/v2_course.py wind    --slug S --which W --back -20 --temps 40,55 --out parts/y.json
  python3 course_data/courses/v2_course.py merge   --slug S --which W PARTS_DIR       -> <slug>/<which>/v2/
  python3 course_data/courses/v2_course.py page    --slug S --which W [--out <slug>/wind_page/index.html]
  python3 course_data/courses/v2_course.py offsets --slug S --which W                  -> tee offsets to compute

How it reuses Spirit Hollow without editing it: the course module generated from the package (product/package.py
write_module, the same API as spirit_hollow/course.py) is registered as sys.modules["course"] BEFORE
spirit_hollow/v2/model.py, decide.py, wind_grid_v2.py and spirit_hollow/build_wind_page.py are imported, so they run
on this course. geom.py (Spirit Hollow's screenshot-scale / OSM-green corrections) is replaced by a no-op: package
frames are already ground yards. Bearings come from the package (tee -> aim, degrees true), par-3 elevation
(plays-like delta) from the package DEM, the per-club tee-shot elevation from the package (3DEP lidar DEM).

config.json (course_data/courses/<slug>/config.json):
  {"name", "package", "truth_package", "tees" (base set), "sets" [men's sets to offer], "colors" {set: css},
   "days" [YYYY-MM-DD, YYYY-MM-DD], "tee_hour" 9.0, "temps" [..], "forecast" (file, optional),
   "climate" {"temp_lo", "temp_hi", "wind_mph", "wind_from"} (placeholder forecast),
   "alt_bases" {set: which} (extra fully solved base sets), "display_imagery" {"year": 2023} (a sharper NAIP year for
   the page photos only: `fetch-display` fetches it on Actions, prepare / page render from it when present)}

  python3 course_data/courses/v2_course.py fetch-display --slug S      -> /tmp/v2_display_<slug>_<year> (Actions)
  python3 course_data/courses/v2_course.py prepare-all   --slug S      -> prepare truth + every alt base
"""
import argparse
import base64
import glob
import importlib.util
import io
import json
import math
import os
import re
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
SH = os.path.join(ROOT, "spirit_hollow")
V2 = os.path.join(SH, "v2")
TEMPLATE = os.path.join(HERE, "wind_page_template_course.html")
IMG_W = 620
CHECKED_HALF_WIDTH = 65.0          # hand-checked corridors are +/-65 yds (corridor.FOOT); v2 default 55


# course folders live here; the course-page workflow (course_data/library/course_page.py) points it at
# course_data/library so automatic pages never land beside the hand-checked tournament pages
COURSES = os.path.abspath(os.environ.get("V2_COURSES_DIR") or HERE)
JPEG_Q = int(os.environ.get("V2_JPEG_Q", "76"))      # hole-image quality in the page (library pages use less)


def cdir(slug, *p):
    return os.path.join(COURSES, slug, *p)


def config(slug):
    return json.load(open(cdir(slug, "config.json")))


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ prepare
def product_pk():
    sys.path[:0] = [os.path.join(CD, "product")]
    import package as PK                        # course_data/product/package.py
    return PK


def base_tees(cfg, which):
    """The tee set a `which` is solved for: config "alt_bases" {set: which} names extra fully solved base sets
    (e.g. {"Blue": "truth_blue"}: the same truth map, solved from the Blue tees); else config "tees"."""
    for s, w in (cfg.get("alt_bases") or {}).items():
        if w == which:
            return s
    return cfg["tees"]


def main_which(cfg, which):
    """An alt base's page is the main page (its holes are folded in as D.alt): the `which` that owns the page
    (config "main_which", default "truth"; automatic library pages use "auto")."""
    return cfg.get("main_which", "truth") if which in (cfg.get("alt_bases") or {}).values() else which


def display_dir(slug):
    """config "display_imagery" {"year": 2023[, "dir": ...]}: a sharper photo for the page only (picks, maps and grids
    are unchanged). Its folder (env V2_DISPLAY_DIR, else "dir", else /tmp/v2_display_<slug>_<year>) is filled by
    `fetch-display` (course_data/imagery/display_imagery.py, Actions); prepare renders the hole photos from it when
    it exists, else from the package imagery. V2_NO_DISPLAY=1 turns it off."""
    di = config(slug).get("display_imagery")
    if not di or os.environ.get("V2_NO_DISPLAY") == "1":
        return None
    d = os.environ.get("V2_DISPLAY_DIR") or di.get("dir") or f"/tmp/v2_display_{slug}_{di.get('year', 'best')}"
    d = d if os.path.isabs(d) else os.path.join(ROOT, d)
    return d if os.path.exists(os.path.join(d, "georef.json")) else None


def fetch_display(slug):
    di = config(slug).get("display_imagery")
    if not di:
        print(slug, "has no display_imagery in config.json: nothing to fetch")
        return None
    d = os.environ.get("V2_DISPLAY_DIR") or di.get("dir") or f"/tmp/v2_display_{slug}_{di.get('year', 'best')}"
    d = d if os.path.isabs(d) else os.path.join(ROOT, d)
    if not os.path.exists(os.path.join(d, "georef.json")):
        sys.path.insert(0, os.path.join(CD, "imagery"))
        import display_imagery as DI
        DI.fetch(slug, str(di.get("year", "best")), d)
    return d


def whiches(slug):
    cfg = config(slug)
    return [cfg.get("main_which", "truth")] + [w for w in (cfg.get("alt_bases") or {}).values()]


def ensure_shots(slug, which):
    """Re-render a which's hole photos (prepare, own process) when they are missing (alt-base screenshots are not
    committed) or were rendered from other imagery than the display / package imagery now in use."""
    shots = cdir(slug, which, "screenshots", "index.json")
    want = display_dir(slug)
    have = None
    if os.path.exists(shots):
        try:
            have = next(iter(json.load(open(shots)).values())).get("imagery_date")
        except Exception:                                      # noqa: BLE001
            have = None
    if want:
        g = json.load(open(os.path.join(want, "georef.json"))).get("imagery", {})
        want_date = ",".join(g.get("acquired", [])) or None
    else:
        want_date = json.load(open(cdir(slug, which, "meta.json"))).get("imagery_date") if have else None
    if have is None or (want and have != want_date):
        import subprocess
        print("re-rendering", which, "photos:", have, "->", want_date or "package imagery")
        subprocess.run([sys.executable, os.path.abspath(__file__), "prepare", "--slug", slug, "--which", which],
                       check=True)


def prepare(slug, which):
    cfg = config(slug)
    pkg_path = os.path.join(ROOT, cfg["truth_package" if which.startswith("truth") else "package"])
    PK = product_pk()
    import imagery
    C = PK.load(pkg_path, base_tees(cfg, which))
    disp = display_dir(slug)
    if disp:
        C.imagery_dir = disp                    # display only: the module, frames and zones do not depend on it
        print("display imagery:", disp)
    out = cdir(slug, which)
    os.makedirs(out, exist_ok=True)
    PK.write_module(C, os.path.join(out, "course.py"))
    shots = os.path.join(out, "screenshots")
    idx = imagery.render_all(C, shots, log=print)
    pkg = C.package
    holes = pkg["holes"]
    holes = {str(h.get("ref")): h for h in holes} if isinstance(holes, list) else holes
    meta = dict(name=C.name, slug=C.slug, tee_set=C.tee_set, package=os.path.relpath(pkg_path, ROOT),
                imagery_date=next(iter(idx.values())).get("imagery_date"), tee_sets={}, holes={})
    for s, v in (pkg.get("tee_sets") or {}).items():
        meta["tee_sets"][s] = dict(yards=v.get("yards"), total=v.get("total"), colour=v.get("colour"),
                                   rating=v.get("rating"), slope=v.get("slope"))
    for ref, h in holes.items():
        k = PK.key_of(ref)
        e = h.get("elevation") or {}
        adj = e.get("adjustments") or {}
        m = dict(par=h.get("par"), yards=h.get("yards"))
        if adj.get("clubs"):
            m["clubs"] = {c: dict(dc=v.get("carry_delta_yds", 0.0), rf=v.get("roll_factor", 1.0),
                                  kick=v.get("lateral_kick_yds", 0.0), drop=v.get("landing_drop_ft", 0.0))
                          for c, v in adj["clubs"].items() if isinstance(v, dict)}
            sl = adj.get("landing_slope") or e.get("landing_slope") or {}
            m["along"], m["cross"] = sl.get("along_pct"), sl.get("cross_pct")
        if adj.get("green_drop_ft") is not None or (e.get("green") or {}).get("delta_ft") is not None:
            gd = adj.get("green_drop_ft")
            if gd is None:
                gd = -float(e["green"]["delta_ft"])
            m["green_drop"] = gd
            m["dz"] = adj.get("plays_like_delta_yds", round(-gd * 0.3048 / math.tan(math.radians(50)) / 0.9144, 1))
        meta["holes"][str(k)] = m
    dem_elevation(C, pkg_path, meta)
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), indent=1)
    print("prepared", out, len(C.holes), "tee shots,", len(C.par3), "par 3s")


LANDING_TOTALS = {"Driver": 300, "2-wood": 280, "4-wood": 270, "Long iron": 220, "Mid iron": 192,
                  "Hybrid ~235 (not in bag)": 248}


def dem_elevation(C, pkg_path, meta):
    """From the package DEM (3DEP lidar 1 m where available) at THIS module's tees (the plan's tee set):
    par 3s: green-centre drop below the tee (ft) and the plays-like delta (elevation/adjust.py rule: an iron
    landing at ~50 deg, -drop / tan 50); tee shots: landing drop (ft) at each club's calm total on the tee line
    (the page's elevation line; the carry / roll numbers are the product's along-line adjustments)."""
    PK = product_pk()
    sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as R
    path = PK.dem_path(C.package, pkg_path)
    if not path:
        meta["dem"] = None
        return
    f = PK._platform_pkg().dem_sampler(path)
    meta["dem"] = os.path.relpath(path, ROOT)
    for k in C.order:
        fr = R.Frame.from_json(C.frames[k])
        tee_ll = C.frames[k]["tee_ll"]
        zt = float(f([tee_ll])[0])
        m = meta["holes"].setdefault(str(k), {})
        m["tee_ft"] = round(zt / 0.3048, 1) if np.isfinite(zt) else None
        if k in C.par3:
            g_ll = fr.px_to_ll([C.par3[k]["flag"]])[0]
            zg = float(f([g_ll])[0])
            if np.isfinite(zt) and np.isfinite(zg):
                drop = (zt - zg) / 0.3048
                m["green_drop"] = round(drop, 1)
                m["dz"] = round(-drop * 0.3048 / math.tan(math.radians(50)) / 0.9144, 1)
                m["green_ft"] = round(zg / 0.3048, 1)
        else:
            hd = C.holes[k]
            tee = np.array(hd["tee"], float)
            v = np.array(hd["dot270"], float) - tee
            ppy = np.linalg.norm(v) / 270.0
            fwd = v / np.linalg.norm(v)
            clubs = m.setdefault("clubs", {})
            for c, tot in LANDING_TOTALS.items():
                ll = fr.px_to_ll([tee + fwd * tot * ppy])[0]
                z = float(f([ll])[0])
                if np.isfinite(z) and np.isfinite(zt):
                    clubs.setdefault(c, {})["drop"] = round((zt - z) / 0.3048, 1)


# ------------------------------------------------------------------------------------------------ activate
def activate(slug, which):
    """Register the course module as `course`, import the v2 engine on it. Returns (course, meta, M, D)."""
    cfg = config(slug)
    meta = json.load(open(cdir(slug, which, "meta.json")))
    course = _load(cdir(slug, which, "course.py"), "course")
    course.ELEVATION = True
    for k, hd in course.HOLES.items():
        hd.setdefault("elev_info", {})["bearing"] = course.BEARINGS.get(k)
    for k, p in course.PAR3.items():
        p["bearing"] = course.BEARINGS.get(k)
        m = meta["holes"].get(str(k), {})
        if m.get("dz") is not None:
            p["plays_like_delta"] = float(m["dz"])
            p["green_drop_ft"] = float(m["green_drop"])
    geom = types.ModuleType("geom")
    geom.set_geometry = lambda flags=None: []
    geom.summary = lambda: {}
    sys.modules["geom"] = geom
    for p in (V2, SH, os.path.join(ROOT, "mozingo")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import model as M
    M.CHECKED_HALF_WIDTH = CHECKED_HALF_WIDTH
    fc = forecast(slug)
    M.FORECAST = fc["hourly"]
    M.TEE_DAY, M.TEE_HOUR = cfg["days"][0], float(cfg.get("tee_hour", 9.0))
    # hole_temp(h, day=TEE_DAY, tee_hour=TEE_HOUR) bound Spirit Hollow's day at import: without this every hole of
    # another course got the no-forecast fallback (48 F) in the decide runs and the page's calm temperature
    M.hole_temp.__defaults__ = (M.TEE_DAY, M.TEE_HOUR)
    import decide as D
    return course, meta, M, D


def forecast(slug):
    """The course's forecast file (config "forecast"), else a placeholder from the event-week climate."""
    cfg = config(slug)
    f = cfg.get("forecast")
    if f and os.path.exists(os.path.join(ROOT, f)):
        return json.load(open(os.path.join(ROOT, f)))
    cl = cfg["climate"]
    rows = []
    for d in cfg["days"]:
        for hr in range(6, 20):
            # diurnal: low at 6 am, high at 3 pm
            x = (hr - 6) / 9.0 if hr <= 15 else 1 - (hr - 15) / 12.0
            temp = cl["temp_lo"] + (cl["temp_hi"] - cl["temp_lo"]) * math.sin(min(max(x, 0), 1) * math.pi / 2)
            rows.append(dict(date=d, hour=hr, temp_f=round(temp, 1), wind_mph=float(cl["wind_mph"]),
                             gust_mph=round(cl["wind_mph"] * 1.6, 1), wind_from_deg=float(cl["wind_from"])))
    return dict(placeholder=True, fetched_utc="placeholder (climate normals, not a forecast)", hourly=rows,
                note="PLACEHOLDER: event-week climate normals (" + cl.get("source", "NOAA normals") + "), constant wind. "
                     "Replace with a real forecast inside ~7 days of the event.")


# ------------------------------------------------------------------------------------------------ compute
def run_decide(slug, which, holes, out, draws=64, swings=3000, central=12000):
    course, meta, M, D = activate(slug, which)
    os.environ.update(V2_HOLES=",".join(holes or []), V2_DRAWS=str(draws), V2_SWINGS=str(swings),
                      V2_CENTRAL_SWINGS=str(central), V2_OUT=out, V2_GEOM="")
    D.main()


def run_wind(slug, which, back, temps, out, swings=2500):
    course, meta, M, D = activate(slug, which)
    os.environ.update(TEE_BACK=str(back), WIND_TEMPS=",".join(str(t) for t in temps), WIND_SWINGS=str(swings),
                      WIND_OUT=out, V2_GEOM="", WIND_HOLES=os.environ.get("WIND_ONLY", ""))
    import wind_grid as WG
    WG.osm_bearings = lambda: {}
    import wind_grid_v2 as WG2
    WG2.TEMPS = [float(t) for t in temps]
    WG2.N = swings
    WG2.main()


def offsets(slug, which):
    """Tee offsets (yds back of the base set, nearest 20) needed to cover every offered set on every tee shot."""
    cfg = config(slug)
    course, meta, M, D = activate(slug, which)
    base = meta["tee_set"]
    sets = cfg.get("sets") or list(meta["tee_sets"])
    need = {0}
    for k in course.HOLES:
        y = meta["holes"][str(k)].get("yards") or {}
        for s in sets:
            if s in y and base in y and y[s] and y[base]:
                need.add(int(20 * round((y[s] - y[base]) / 20.0)))
    return sorted(need)


def merge(slug, which, parts):
    course = _load(cdir(slug, which, "course.py"), "course")
    out = cdir(slug, which, "v2")
    os.makedirs(out, exist_ok=True)
    order = [str(k) for k in course.ORDER if k in course.HOLES]
    dec = {}
    for p in sorted(glob.glob(os.path.join(parts, "**", "v2dec_*.json"), recursive=True)):
        dec.update(json.load(open(p)))
    if dec:
        old = os.path.join(out, "v2_decisions.json")
        merged = json.load(open(old)) if os.path.exists(old) else {}
        merged.update(dec)
        json.dump({k: merged[k] for k in order if k in merged}, open(old, "w"), indent=1)
        print("v2_decisions:", len(dec), "holes")
    grids = {}
    for p in sorted(glob.glob(os.path.join(parts, "**", "v2wind_*.json"), recursive=True)):
        d = json.load(open(p))
        g = grids.setdefault(d["back"], dict(speeds=d["speeds"], dirs=d["dirs"], temps=[], bearings={}, holes={},
                                             par3={}, tee_back=d["back"], model="v2"))
        g["temps"] = sorted(set(g["temps"]) | set(d.get("temps", [])))
        for h, byT in d["holes"].items():
            g["holes"].setdefault(h, {}).update(byT)
        g["bearings"].update(d["bearings"])
        g["par3"].update(d["par3"])
    for b, g in grids.items():
        name = "wind_grid.json" if not b else f"wind_grid_back{b:+.0f}.json"
        json.dump(g, open(os.path.join(out, name), "w"))
        print(name, len(g["holes"]), "holes", g["temps"])


# ------------------------------------------------------------------------------------------------ page
def crop_factory(shots):
    from PIL import Image

    def crop_jpeg(image, box, y_max=2000):
        """box in the 920x2000 render frame -> (data URI, scale, (x0, y0), size); rows off the render padded."""
        im = Image.open(os.path.join(shots, image)).convert("RGB")
        k = im.width / 920
        x0, y0, x1, y1 = box
        x0, x1 = max(0, x0), min(920, x1)
        top, bot = max(0, y0), min(2000, y1)
        c = im.crop((int(x0 * k), int(top * k), int(x1 * k), int(bot * k)))
        if y1 > 2000 or y0 < 0:
            pad = Image.new("RGB", (c.width, int((y1 - y0) * k)), (52, 66, 56))
            pad.paste(c, (0, int((top - y0) * k)))
            c = pad
        scale = IMG_W / c.width
        c = c.resize((IMG_W, int(c.height * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        c.save(buf, "JPEG", quality=JPEG_Q, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), scale * k, (x0, y0), c.size
    return crop_jpeg


def build_page(slug, which, out=None, data_out=None):
    """The wind page. With config "alt_bases" {set: which}, each alt base is built in its own process (the v2
    engine binds one course module per process) with data_out, and its holes ride along as D.alt[set]: the page
    swaps to them when that set is picked, so that set is a fully solved base (own tees, aims, calm-day picks)."""
    cfg = config(slug)
    if data_out is None and main_which(cfg, which) != which:
        which = main_which(cfg, which)
    alt = {}
    if data_out is None:
        import subprocess
        import tempfile
        ensure_shots(slug, which)
        for s, w in (cfg.get("alt_bases") or {}).items():
            if not os.path.exists(cdir(slug, w, "v2", "wind_grid.json")):
                print("alt base", s, "(", w, ") not computed yet: skipped")
                continue
            ensure_shots(slug, w)
            with tempfile.TemporaryDirectory() as td:
                p = os.path.join(td, "alt.json")
                subprocess.run([sys.executable, os.path.abspath(__file__), "page", "--slug", slug, "--which", w,
                                "--data-out", p], check=True)
                alt[s] = json.load(open(p))["holes"]
    course, meta, M, D = activate(slug, which)
    import build_wind_page as BW
    import build_page_v2 as BP
    import yardage_book as yb
    yb.use_course(course.NAME, cdir(slug, which), slug, course.HOLES, course.PAR3, course.NOTES, course.AIM_AT,
                  course.ORDER, course.LABELS)
    BW.crop_jpeg = crop_factory(cdir(slug, which, "screenshots"))
    BW.FN = {}
    base = meta["tee_set"]
    sets = [s for s in (cfg.get("sets") or list(meta["tee_sets"])) if s in meta["tee_sets"]]

    def elev_of(h):
        m = meta["holes"].get(str(h), {})
        if h in course.PAR3:
            return dict(green_drop=m["green_drop"], dz=m.get("dz")) if m.get("green_drop") is not None else None
        e = course.HOLES[h].get("elev")
        if not e:
            return None
        drops = {c: v.get("drop", 0.0) for c, v in (m.get("clubs") or {}).items()}
        return dict(clubs={c: dict(dc=v[0], rf=v[1], kick=v[2], drop=drops.get(c, 0.0)) for c, v in e.items()},
                    along=m.get("along"), cross=m.get("cross"))
    BW.elev_of = elev_of

    def tee_options(h):
        y = meta["holes"][str(h)].get("yards") or {}
        yb_ = y.get(base)
        out_ = [dict(name=s, yards=y[s], back=(y[s] - yb_) if yb_ else 0) for s in sets if y.get(s)]
        return base, out_
    BW.tee_options = tee_options
    v2dir = cdir(slug, which, "v2")
    grid = json.load(open(os.path.join(v2dir, "wind_grid.json")))
    grids = {0: grid}
    for path in glob.glob(os.path.join(v2dir, "wind_grid_back*.json")):
        grids[int(float(re.search(r"back([+-]?[0-9.]+)", path).group(1)))] = json.load(open(path))
    dp = os.path.join(v2dir, "v2_decisions.json")
    dec = json.load(open(dp)) if os.path.exists(dp) else {}
    fc = forecast(slug)
    holes = []
    for h in course.ORDER:
        d = BW.par3_hole(h) if h in course.PAR3 else BW.tee_hole(h)
        d["key"] = str(h)
        d["label"] = str(h)
        d["bearing"] = course.BEARINGS.get(h)
        b0, opts = tee_options(h)
        d["base_set"], d["tee_opts"] = b0, opts
        if h in course.PAR3:
            d["plays"] = grid["par3"][str(h)]
            d["by_set"] = BW.par3_sets(h, opts, grid)
            d["note"] = course.PAR3[h].get("note", "")
        else:
            d["tee_name"] = base + " tee"
            d["tee_offimage"] = False
            keep = set(grids)
            if cfg.get("grid_prune"):
                # page size: only the grids some offered set snaps to on this hole (alt bases carry their own holes)
                have = [b for b, g in grids.items() if str(h) in g.get("holes", {})]
                keep = {0} | {min(have, key=lambda b: abs(b - o["back"])) for o in opts
                              if o["name"] not in (cfg.get("alt_bases") or {})}
            d["grids"] = {str(b): {T: BP.compact(gT) for T, gT in g["holes"][str(h)].items()}
                          for b, g in sorted(grids.items()) if str(h) in g.get("holes", {}) and b in keep}
            Tn = min(grid["temps"], key=lambda T: abs(T - M.hole_temp(h)))
            d["cloud"] = BP.cloud(h, grid["holes"][str(h)][f"{Tn:g}"]["0_0"], Tn)
            r = dec.get(str(h))
            d["note"] = ""
            if r and "pick" in r:
                d["note"] = BP.note_v2(h, r).replace(" of 64 what-if worlds", f" of {r.get('draws', 64)} what-if worlds")
                d["calm"] = dict(pick=r["pick"], aim=r["aim"], tie=bool(r["tie"]), margin=r["margin"],
                                 flips=r.get("width_flips", []), temp=r.get("temp_f", M.hole_temp(h)),
                                 window=r.get("window"))
            hn = (cfg.get("hole_notes") or {}).get(str(h))
            if hn:
                d["note"] = (d["note"] + " " if d["note"] else "") + "Map: " + hn
        if h in course.PAR3:
            hn = (cfg.get("hole_notes") or {}).get(str(h))
            if hn:
                d["note"] = (d["note"] + " " if d["note"] else "") + "Map: " + hn
        holes.append(d)
    tot = {s: meta["tee_sets"][s].get("total") for s in sets}
    data = dict(slug=slug, title=cfg.get("title") or (course.NAME + " Caddie"), base_set=base, sets=sets,
                colors=cfg.get("colors", {}), set_totals=tot, days=cfg["days"],
                day_labels=cfg.get("day_labels") or cfg["days"], tee_hour=float(cfg.get("tee_hour", 9.0)),
                sub=cfg.get("sub", ""), foot_extra=cfg.get("foot", ""), placeholder=bool(fc.get("placeholder")),
                fc_note=fc.get("note", ""), imagery=meta.get("imagery_date"),
                speeds=grid["speeds"], dirs=grid["dirs"], temps=grid["temps"], holes=holes, offsets=sorted(grids),
                forecast=[dict(date=r["date"], hour=r["hour"], mph=r["wind_mph"], gust=r["gust_mph"],
                               dir=r["wind_from_deg"], temp=r["temp_f"]) for r in fc["hourly"]],
                fetched=fc.get("fetched_utc", ""), draws=int(cfg.get("draws", 64)))
    if data_out:
        json.dump(data, open(data_out, "w"), separators=(",", ":"))
        return
    if alt:
        data["alt"] = alt
    html = open(TEMPLATE).read().replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    html = html.replace("__TITLE__", data["title"])
    out = out or cdir(slug, "wind_page", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)
    print("wrote", out, f"{os.path.getsize(out) / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["prepare", "decide", "wind", "merge", "page", "offsets", "fetch-display",
                                    "prepare-all"])
    ap.add_argument("parts", nargs="?")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--which", default="truth")
    ap.add_argument("--holes", default="")
    ap.add_argument("--back", type=float, default=0.0)
    ap.add_argument("--temps", default="")
    ap.add_argument("--out")
    ap.add_argument("--draws", type=int, default=64)
    ap.add_argument("--swings", type=int, default=0)
    ap.add_argument("--data-out")
    a = ap.parse_intermixed_args()
    if a.cmd == "prepare":
        prepare(a.slug, a.which)
    elif a.cmd == "decide":
        run_decide(a.slug, a.which, [h for h in a.holes.split(",") if h], a.out, draws=a.draws,
                   swings=a.swings or 3000)
    elif a.cmd == "wind":
        temps = [float(t) for t in (a.temps or ",".join(str(t) for t in config(a.slug)["temps"])).split(",")]
        run_wind(a.slug, a.which, a.back, temps, a.out, swings=a.swings or 2500)
    elif a.cmd == "merge":
        merge(a.slug, a.which, a.parts)
    elif a.cmd == "page":
        build_page(a.slug, a.which, a.out, data_out=a.data_out)
    elif a.cmd == "offsets":
        print(json.dumps(offsets(a.slug, a.which)))
    elif a.cmd == "fetch-display":
        fetch_display(a.slug)
    elif a.cmd == "prepare-all":
        for w in whiches(a.slug):
            if os.path.exists(cdir(a.slug, w)) or w == "truth":
                prepare(a.slug, w)


if __name__ == "__main__":
    main()
