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
    if not os.path.exists(os.path.join(d, "georef.json")) and di.get("fallback_dir"):
        # no fetched display imagery on this machine: a committed folder of the same photo (Gateway: the package's
        # NAIP 2023), so a local build still renders each page photo directly and is not tied to the 920 x 2000 frame
        d = os.path.join(ROOT, di["fallback_dir"])
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
    di = cfg.get("display_imagery") or {}
    idx = render_display(C, shots, di) if disp and di.get("render_scale") else imagery.render_all(C, shots, log=print)
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


def render_display(C, out_dir, di, log=print):
    """The page photos straight from the display imagery (config "display_imagery" {"render_scale": [tee, par3],
    "render_back": px}): each hole rendered at `render_scale` x the 920 x 2000 frame (tee shots 2x, par 3s 3x: the
    page crop is then a downsample) with Lanczos instead of bilinear, kept near-lossless (JPEG q95, 4:4:4), so the
    900-px page crop is one resample from the 0.3 m source, not bilinear -> q82 JPEG -> 1.8-2.9x upscale (Eagle
    Knoll 2026-11-06, blurry photos). `render_back` frame px more are rendered below the frame (behind the tee) so a
    shared photo also covers a set whose tee is further back. Display only: the frames (FRAMES: px <-> WGS84),
    zones and grids are unchanged; crop_factory reads the scale from the image width (k = width / 920)."""
    import cv2
    from PIL import Image
    sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as R
    sc = di.get("render_scale") or [2, 3]
    sc = sc if isinstance(sc, list) else [sc, sc]
    back = float(di.get("render_back", 0))
    os.makedirs(out_dir, exist_ok=True)
    img = R.Imagery(C.imagery_dir)
    index = {}
    for k in C.order:
        hd = C.holes.get(k) or C.par3[k]
        fr = R.Frame.from_json(C.frames[k])
        m = sc[1] if k in C.par3 else sc[0]
        big = R.Frame(fr.tee_ll, fr.aim_ll, fr.ppy * m, fr.tee_px * m, fr.proj,
                      (int(fr.size[0] * m), int((fr.size[1] + back) * m)))
        out, info = R.render(big, img, interp=cv2.INTER_LANCZOS4)
        path = os.path.join(out_dir, hd["image"])
        Image.fromarray(out[..., :3]).save(path, "JPEG", quality=95, subsampling=0)
        info.update(frame=fr.to_json(), tee_px=[float(v) for v in fr.tee_px],
                    dot270_px=[float(v) for v in fr.point_px(270)], yds_per_px=1 / fr.ppy, display_scale=m,
                    image=hd["image"], bytes=os.path.getsize(path))
        index[str(k)] = info
        if info["no_imagery_frac"] > 0.05:
            log(f"  ! hole {k}: {info['no_imagery_frac']:.0%} of the frame has no imagery")
    json.dump(index, open(os.path.join(out_dir, "index.json"), "w"), indent=1, default=float)
    log(f"display photos: {len(index)} holes at {sc}x, Lanczos, {img.res:.2f} m source")
    return index


LANDING_TOTALS = {"Driver": 300, "2-wood": 280, "4-wood": 270, "Long iron": 220, "Mid iron": 192,
                  "8-iron": 167, "Hybrid ~235 (not in bag)": 248}


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
    eng = dict(cfg.get("engine") or {})
    if eng.get("green_putting"):
        attach_greens(cfg, which, course, M)
    if eng.get("checked_extra_ll"):
        attach_checked_extra(eng["checked_extra_ll"], course)
    # "native_penalty_area": "relief" | "stroke_and_distance" (per course, default off). Gateway National, the golfer's
    # ground truth 2026-11-13: every standing tall-native zone is penalty area ("no finding it, too thick and tall"):
    # the ball is gone from the first yard in. "relief" = the engine's water rule (one stroke + a shot from rough at
    # the point the ball crossed the edge); "stroke_and_distance" = the engine's OB rule (unstaked: lost ball).
    # Env V2_NATIVE_PENALTY overrides for A/B runs ("off" = the default depth-ramp lost-ball model).
    npa = os.environ.get("V2_NATIVE_PENALTY") or eng.get("native_penalty_area")
    if npa in ("relief", "stroke_and_distance"):
        to = "water" if npa == "relief" else "ob"
        for hd in course.HOLES.values():
            hd["zones"] = [((to if z[0] == "native" else z[0]),) + tuple(z[1:]) for z in hd["zones"]]
    if eng.get("flight_trees"):
        dem = os.path.join(ROOT, meta["dem"]) if meta.get("dem") else None
        cache = {}
        key_of = {id(hd): k for k, hd in course.HOLES.items()}

        def drop_of(hd):
            k = key_of.get(id(hd))
            if k is None:
                return None
            ck = (k, tuple(np.round(np.asarray(hd["tee"], float), 1)))
            if ck not in cache:
                cache[ck] = ground_drop_grid(M, hd, course.FRAMES[k], dem)
            return cache[ck]
        eng["_drop_of"] = drop_of
        if eng["flight_trees"].get("mode") == "lidar" and lidar_opts(eng["flight_trees"]) is not None:
            o = lidar_opts(eng["flight_trees"])
            chm = os.path.join(ROOT, o["chm"]) if o.get("chm") else None
            ccache = {}

            def canopy_of(hd):
                k = key_of.get(id(hd))
                if k is None:
                    return None
                ck = (k, tuple(np.round(np.asarray(hd["tee"], float), 1)))
                if ck not in ccache:
                    ccache[ck] = canopy_grid(M, hd, course.FRAMES[k], chm, o, R=M.Raster(hd))
                return ccache[ck]
            eng["_canopy_of"] = canopy_of
    install_engine(eng, M, D)
    return course, meta, M, D


# ------------------------------------------------------------------------------------------------ engine options
# config "engine" (per course, default off, so library pages and the other tournament pages keep the engine they were
# solved with):
#   "extra_clubs": {"8-iron": [carry, total, width95, depth95], ...}   short lay-up clubs (Eagle Knoll audit item 2:
#                  the shortest club was the 185-carry "Mid iron", so a 170-yd lay-up on a 246-yd par 4 was never priced)
#   "flight_trees": {"height_yds": 20, "p_hit": 0.7}   the ball's flight can hit trees before it lands (audit item 1:
#                  the engine priced trees only where the ball finishes, so a drive over a corner of woods was free)
EXTRA_WIDTH_OF = "Mid iron"        # an extra club's width scales with this club's width in every prior draw
APEX_YDS = {"wood": 32.0, "iron": 30.0}          # TrackMan-style driver / long-iron apex at ~275 / ~200 carry
LAND_DEG = {"wood": 38.0, "iron": 46.0}
APEX_AT = 0.6                                    # apex at 60 % of the carry


def install_engine(eng, M, D):
    if getattr(M, "_engine_opts", None) is not None:
        return
    if os.environ.get("V2_ENGINE") == "0":       # A/B: the engine as solved before the options
        eng = {}
    for k in [k for k in os.environ.get("V2_ENGINE_OFF", "").split(",") if k]:
        eng = {a: b for a, b in eng.items() if a != k}
    M._engine_opts = eng
    extra = eng.get("extra_clubs") or {}
    for c, v in extra.items():
        if c in M.CLUBS:
            continue
        M.CLUBS[c] = tuple(float(x) for x in v)
        i = M.ALL_CLUBS.index(M.HYBRID) if M.HYBRID in M.ALL_CLUBS else len(M.ALL_CLUBS)
        M.ALL_CLUBS.insert(i, c)
        M.REAL_CLUBS.insert(M.REAL_CLUBS.index("Mid iron") + 1 if "Mid iron" in M.REAL_CLUBS else len(M.REAL_CLUBS), c)
        for hd in M.HOLES.values():                       # DEM carry / roll: the mid iron's (closest landing)
            e = hd.get("elev")
            if e and "Mid iron" in e and c not in e:
                e[c] = tuple(e["Mid iron"])
        try:
            import wind as W
            W.SENSITIVITY.setdefault(c, 1.3)            # shorter, higher-spin iron: moved a bit more than the mid iron
        except Exception:                                # noqa: BLE001
            pass
    if extra:
        base_prior = D.prior_draws
        ref = M.CLUBS[EXTRA_WIDTH_OF][2]

        def prior_draws(s=64, seed=2026, hole=None):
            out = base_prior(s, seed, hole)
            for P in out:
                for c in extra:
                    P["width"][c] = P["width"][EXTRA_WIDTH_OF] * M.CLUBS[c][2] / ref
                    P["c_club"][c] = P["c_club"].get(EXTRA_WIDTH_OF, 0.0)
            return out
        D.prior_draws = prior_draws
        try:
            import build_page_v2 as BP
            for c in extra:
                BP.SHORT.setdefault(c, c)
        except Exception:                                # noqa: BLE001
            pass
    if eng.get("physics"):
        install_physics(M, D, eng["physics"])
    if eng.get("green_putting"):
        install_green_putting(M, eng["green_putting"])
    if eng.get("aim_limit"):
        install_aim_limit(D, float(eng["aim_limit"]))
    if eng.get("checked_extra_ll"):
        install_checked_extra(M)
    ft = eng.get("flight_trees")
    if ft and ft.get("mode") == "lidar" and lidar_opts(ft) is not None:
        o = lidar_opts(ft)
        M.ev_curve = lidar_flight_ev_curve(M, o, eng.get("_canopy_of"), drop_of=eng.get("_drop_of"))
        M._lidar_opts = o
    elif ft:
        M.ev_curve = flight_tree_ev_curve(M, float(os.environ.get("V2_FLIGHT_HEIGHT") or ft.get("height_yds", 20.0)),
                                          float(os.environ.get("V2_FLIGHT_PHIT") or ft.get("p_hit", 0.7)),
                                          drop_of=eng.get("_drop_of"))


def install_physics(M, D, ph):
    """config engine "physics" (Gateway National second pass 2026-11-13, second_pass/PHYSICS.md: the engine's rules
    against an independent trajectory model). Per course, so the other pages keep the numbers they were solved with.
      "temp_k": carry lost per F below 70 (engine 0.00075 = the air alone; + the ball at air temperature + the
                weekend's high pressure = 0.00135). Central world, the prior draws (scaled) and the page's par 3s.
      "wind_sensitivity": {club: multiplier} replaces wind.SENSITIVITY entries (head / tail and drift per club).
      "drift_per_mph_275": wind.DRIFT_PER_MPH_275 (yds of drift per crosswind mph at 275 carry)."""
    if getattr(M, "_physics", None) is not None:
        return
    M._physics = dict(ph)
    import wind as W
    if ph.get("wind_sensitivity"):
        W.SENSITIVITY.update({c: float(v) for c, v in ph["wind_sensitivity"].items()})
    if ph.get("drift_per_mph_275"):
        W.DRIFT_PER_MPH_275 = float(ph["drift_per_mph_275"])
    if ph.get("temp_k"):
        K = float(ph["temp_k"])
        K0 = float(M.central()["temp_k"])
        base_central = M.central

        def central(**over):
            return base_central(**dict(dict(temp_k=K), **over))
        M.central = central
        base_prior = D.prior_draws

        def prior_draws(*a, **kw):
            out = base_prior(*a, **kw)
            for P in out:
                # decide.prior_draws passes its own U(0.0005, 0.0009) draw: keep its relative spread round K
                P["temp_k"] = P["temp_k"] * K / K0 if abs(P["temp_k"] - K) > 1e-12 else K
            return out
        D.prior_draws = prior_draws


def install_aim_limit(D, L):
    """config engine "aim_limit": the aim search bound (yds either side of the tee line, landing aim incl. wind drift;
    decide.AIM_LIMIT, default 40) and the decide aim grid (+/- L + 20). Gateway National audit 2026-11-09 item 6: on the
    dogleg 8th the 2-wood's best line sat on the 40-yd bound and the Driver's (about -50) beyond it, so the page showed
    a bound as an optimum. decide.robust_aim's default bounds are bound at its definition, so it is wrapped."""
    if getattr(D, "_aim_limit", None) == L:
        return
    base = getattr(D, "_robust_aim0", None) or D.robust_aim
    D._robust_aim0 = base
    D.AIM_LIMIT = L
    D.AIMS = np.arange(-(L + 20.0), L + 20.0 + 1e-9, 0.5)

    def robust_aim(aims, curve, lo=-L, hi=L):
        return base(aims, curve, lo, hi)
    D.robust_aim = robust_aim
    D._aim_limit = L


def flight_heights(f, kind="wood", carry=275.0):
    """Ball height (yds) at fraction f of the carry: a parabola up to the apex (APEX_AT of the carry), then a
    power-law descent whose slope at landing is LAND_DEG."""
    ref = 275.0 if kind == "wood" else 200.0
    H = APEX_YDS[kind] * float(np.clip(carry / ref, 0.6, 1.2))
    f = np.asarray(f, float)
    up = H * (1 - ((APEX_AT - f) / APEX_AT) ** 2)
    p = math.tan(math.radians(LAND_DEG[kind])) * (1 - APEX_AT) * carry / H
    dn = H * (1 - np.clip((f - APEX_AT) / (1 - APEX_AT), 0, 1) ** p)
    return np.where(f < APEX_AT, up, dn)


FLIGHT_F = np.array([0.6, 0.66, 0.72, 0.78, 0.83, 0.87, 0.9, 0.93, 0.955, 0.98])
FLIGHT_MIN_ALONG = 140.0   # only where the hand map is checked (corridors 145-440): the woods round the tee chutes
                           # are not traced to the yard (hole 5's chute is 5 yds wide on the map), and the climb
                           # out of the chute is not modelled
DROP_STEP = 4.0                                  # yds: ground-drop grid of a hole (DEM, tee frame)


def ground_drop_grid(M, hd, frame_json, dem_path):
    """(tee ground - ground) in yds on a DROP_STEP grid of the tee frame (+ = below the tee), from the package DEM;
    None without a DEM. Lets the flight clear a wooded ravine below the tee (hole 3) and meet rising ground."""
    if not dem_path or not os.path.exists(dem_path):
        return None
    PK = product_pk()
    if os.path.join(CD, "imagery") not in sys.path:
        sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as R
    f = PK._platform_pkg().dem_sampler(dem_path)
    fr = R.Frame.from_json(frame_json)
    tee, fwd, right, ppy = M.frame(hd)
    ga = np.arange(M.A0, M.A1 + DROP_STEP, DROP_STEP)
    gl = np.arange(M.L0, M.L1 + DROP_STEP, DROP_STEP)
    AA, LL = np.meshgrid(ga, gl, indexing="ij")
    pts = tee + (AA.ravel()[:, None] * fwd + LL.ravel()[:, None] * right) * ppy
    z = np.asarray(f(fr.px_to_ll(pts)), float).reshape(AA.shape)
    zt = float(np.asarray(f(fr.px_to_ll(np.array([tee]))), float)[0])
    if not np.isfinite(zt):
        return None
    d = (zt - z) / 0.9144
    d[~np.isfinite(d)] = 0.0
    return ga, gl, d


def flight_tree_ev_curve(M, height, p_hit, drop_of=None):
    """M.ev_curve with the flight checked against the trees: along the straight line from the tee to the landing
    spot (FLIGHT_F fractions of it, the descent; from FLIGHT_MIN_ALONG yds out) the ball's clearance above the local
    ground = flight height (flight_heights at the club's median carry) + the ground's drop below the tee - that
    fraction of the landing spot's drop; where it
    is under `height` over a tree cell the ball is stopped with probability p_hit (one uniform per swing, shared by
    every aim and club: common random numbers) and finishes there (a tree cell: punch-out cost from there).
    drop_of(hd) -> ground_drop_grid or None (flat ground)."""
    base_shots, base_finish = M.shots, M.finish
    TREE = M.CODE["recovery"]

    def ev_curve(R, S, hd, club, P, z, aims, wind=None):
        car, dev, roll = base_shots(hd, club, P, z, wind)
        a, l, lie = base_finish(R, car[:, None], dev[:, None] + aims[None, :], roll[:, None], P["rough_roll"],
                                P.get("v1_roll", False))
        kind = "wood" if club in M.WOODS else "iron"
        y = flight_heights(FLIGHT_F, kind, float(np.median(car)))
        G = drop_of(hd) if drop_of else None
        if G is not None:
            ga, gl, dg = G

            def drop(pa, pl):
                ia = np.clip(np.rint((pa - ga[0]) / DROP_STEP).astype(np.int32), 0, len(ga) - 1)
                il = np.clip(np.rint((pl - gl[0]) / DROP_STEP).astype(np.int32), 0, len(gl) - 1)
                return dg[ia, il]
        u = np.random.default_rng(int(z.shape[1]) * 7919 + 13).random(z.shape[1])[:, None]
        lat0 = dev[:, None] + aims[None, :]
        car2 = np.broadcast_to(car[:, None], a.shape)
        d_land = drop(car2, lat0) if G is not None else 0.0
        hit = np.zeros(a.shape, bool)
        ha, hl = a.copy(), l.copy()
        for f, yf in zip(FLIGHT_F, y):                 # first tree cell along the flight wins
            pa, pl = car2 * f, lat0 * f
            clear = yf + (drop(pa, pl) - f * d_land if G is not None else 0.0)
            t = (clear < height) & (pa >= FLIGHT_MIN_ALONG) & (R.lie_at(pa, pl) == TREE) & ~hit
            if not t.any():
                continue
            ha = np.where(t, pa, ha)
            hl = np.where(t, pl, hl)
            hit |= t
        stop = hit & (u < p_hit) & (lie != TREE)        # landing in trees is priced already
        a = np.where(stop, ha, a)
        l = np.where(stop, hl, l)
        lie = np.where(stop, TREE, lie)
        s = S[R.idx(a, l)]
        return 1.0 + s.mean(0), (a, l, lie, s)
    ev_curve._flight_trees = (height, p_hit)
    return ev_curve


# ------------------------------------------------------------------------------------------------ green putting
# config engine "green_putting": {"am_putt_off": 0.10} (Eagle Knoll panel finding, 2026-11-06). The tee-shot raster had
# no green lie (the green was fairway) and the scoring tables are clipped at 20 yds, so a drive that finished ON the
# drivable 14th green (10 yds from the hole) scored fairway-at-20 (~2.6 for Will) instead of ~2.1 putts, and a ball
# just over the green scored rough-at-20. With the option: cells inside the mapped green polygon score Broadie's
# PGA Tour expected putts by distance + am_putt_off (a 5-handicap putts ~0.1 more per hole), and fairway / rough /
# sand within 20 yds of the hole use Broadie's short-game values below 20 yds instead of the 20-yd clip.
PUTT_FT = [0, 3, 5, 8, 10, 15, 20, 30, 40, 50, 60, 90, 120]          # Broadie, Every Shot Counts (2014), tour putts
PUTT_TOUR = [1.0, 1.04, 1.23, 1.50, 1.61, 1.78, 1.87, 1.98, 2.06, 2.14, 2.21, 2.40, 2.55]
SHORT_YDS = [5.0, 10.0, 20.0]                                       # tour, off the green (Broadie): 20 = the table
SHORT_TOUR = {"fairway": [2.10, 2.18, 2.40], "rough": [2.25, 2.34, 2.59], "sand": [2.40, 2.43, 2.53]}


def attach_greens(cfg, which, course, M):
    """hd["green_poly"]: each tee shot's green polygon (package green_polygon_ll) in its own tee frame (yds along,
    yds right), as the Raster grid uses."""
    pkg = json.load(open(os.path.join(ROOT, cfg["truth_package" if which.startswith("truth") else "package"])))
    holes = pkg["holes"]
    holes = holes if isinstance(holes, list) else [dict(v, ref=k) for k, v in holes.items()]
    by = {str(h.get("ref")): h for h in holes}
    if os.path.join(CD, "imagery") not in sys.path:
        sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as RD
    for k, hd in course.HOLES.items():
        h = by.get(str(k))
        if not h or not h.get("green_polygon_ll") or k not in course.FRAMES:
            continue
        fr = RD.Frame.from_json(course.FRAMES[k])
        px = fr.ll_to_px(np.asarray(h["green_polygon_ll"], float))
        tee, fwd, right, ppy = M.frame(hd)
        d = (px - tee) / ppy
        hd["green_poly"] = np.column_stack([d @ fwd, d @ right])
        hd["green_poly_px"] = np.asarray(px, float)      # the Raster re-projects it from the tee in use (moved tees)


def attach_checked_extra(spec, course):
    """config engine "checked_extra_ll": {hole: [[lon, lat], ...] or a list of such rings}: ground outside the
    +/-65-yd hand corridor that was checked by eye as well (a dogleg whose fairway leaves the corridor: Gateway 8).
    Rough cells inside the ring stay rough instead of "unverified" (priced as half trees). Stored in photo px so a
    moved tee keeps it on the ground."""
    if os.path.join(CD, "imagery") not in sys.path:
        sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as RD
    for k, rings in spec.items():
        k = int(k) if str(k).isdigit() else k
        if k not in course.HOLES or k not in course.FRAMES:
            continue
        if rings and not isinstance(rings[0][0], (list, tuple)):
            rings = [rings]
        fr = RD.Frame.from_json(course.FRAMES[k])
        course.HOLES[k]["checked_extra_px"] = [np.asarray(fr.ll_to_px(np.asarray(r, float)), float) for r in rings]


def install_checked_extra(M):
    if getattr(M.Raster, "_checked_extra", False):
        return
    from matplotlib.path import Path as _Path
    base = M.Raster.__init__

    def init(self, hd, *a, **kw):
        base(self, hd, *a, **kw)
        rings = hd.get("checked_extra_px")
        if not rings:
            return
        tee, fwd, right, ppy = M.frame(hd)
        pts = np.column_stack([self.AA.ravel(), self.LL.ravel()])
        inside = np.zeros(len(pts), bool)
        for r in rings:
            d = (np.asarray(r, float) - tee) / ppy
            inside |= _Path(np.column_stack([d @ fwd, d @ right])).contains_points(pts)
        m = inside.reshape(self.lie.shape) & (self.lie == M.CODE["unverified"])
        if m.any():
            self.lie[m] = M.CODE["rough"]
            self._blocked()
    M.Raster.__init__ = init
    M.Raster._checked_extra = True


def footprint_ends(cfg, which, course, M):
    """{hole: yds along this base's tee line where the hand-checked map ends} (the far edge of the package's
    hand:footprint rough box), for the page's "lands past the hand-checked map" badge (Gateway audit 2026-11-09 item
    9: the badge used 345 from every base; Middle 3's map ends 282 from its tee)."""
    pkg = json.load(open(os.path.join(ROOT, cfg["truth_package" if which.startswith("truth") else "package"])))
    holes = pkg["holes"]
    holes = holes if isinstance(holes, list) else [dict(v, ref=k) for k, v in holes.items()]
    by = {str(h.get("ref")): h for h in holes}
    if os.path.join(CD, "imagery") not in sys.path:
        sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as RD
    out = {}
    for k, hd in course.HOLES.items():
        h = by.get(str(k)) or {}
        fp = [z for z in (h.get("zones_ll") or []) if z.get("src") == "hand:footprint"]
        if not fp or k not in course.FRAMES:
            continue
        fr = RD.Frame.from_json(course.FRAMES[k])
        px = fr.ll_to_px(np.asarray(fp[0]["poly"], float))
        tee, fwd, right, ppy = M.frame(hd)
        out[k] = round(float(((px - tee) / ppy @ fwd).max()), 1)
    return out


def putts(d_yds, off=0.0):
    return np.interp(np.asarray(d_yds, float) * 3.0, PUTT_FT, PUTT_TOUR) + off


def install_green_putting(M, opts):
    if getattr(M.Raster, "_green_putting", False):
        return
    from matplotlib.path import Path as _Path
    base = M.Raster.strokes
    off = float(opts.get("am_putt_off", 0.10))

    def strokes(self, P, length):
        S = base(self, P, length)
        d, lie = self.dist, self.lie
        near = d < SHORT_YDS[-1]
        if near.any():
            # the tables are clipped at 20 yds, so S = the 20-yd value there: add the tour short-game change below 20
            # (rough / sand gaps over fairway scaled by the amateur multipliers, as table() does)
            fw_d = lambda x: np.interp(x, SHORT_YDS, SHORT_TOUR["fairway"]) - SHORT_TOUR["fairway"][-1]  # noqa: E731
            for kind in ("fairway", "first_cut", "rough", "sand"):
                m = near & (lie == M.CODE[kind])
                if not m.any():
                    continue
                x = d[m]
                delta = fw_d(x)
                if kind in ("rough", "sand", "first_cut"):
                    k2 = "sand" if kind == "sand" else "rough"
                    gap = (np.interp(x, SHORT_YDS, SHORT_TOUR[k2]) - np.interp(x, SHORT_YDS, SHORT_TOUR["fairway"])
                           - (SHORT_TOUR[k2][-1] - SHORT_TOUR["fairway"][-1]))
                    mult = 1.0 if P.get("table") != "am" else (P["m_sand"] if kind == "sand" else P["m_rough"])
                    if kind == "first_cut":
                        mult = mult * P["first_cut"]
                    delta = delta + mult * gap
                S[m] = S[m] + delta
        gp = self.hd.get("green_poly")
        if self.hd.get("green_poly_px") is not None:
            # a tee moved along the line (wind grids of the other tee sets, wind_grid.shift_tees) moves the frame:
            # project the polygon from the tee in use (2026-11-13: it stayed in the card tee's yards, so from a
            # moved tee the putting area sat `back` yds off the green)
            tee, fwd, right, ppy = M.frame(self.hd)
            dd = (np.asarray(self.hd["green_poly_px"], float) - tee) / ppy
            gp = np.column_stack([dd @ fwd, dd @ right])
        if gp is not None:
            AA, LL = np.meshgrid(self.a, self.l, indexing="ij")
            g = _Path(np.asarray(gp, float)).contains_points(np.column_stack([AA.ravel(), LL.ravel()])).reshape(AA.shape)
            g &= (lie == M.CODE["fairway"]) | (lie == M.CODE["first_cut"]) | (lie == M.CODE["rough"])
            S[g] = putts(d[g], off if P.get("table") == "am" else 0.0)
        return S
    M.Raster.strokes = strokes
    M.Raster._green_putting = True
# ------------------------------------------------------------------------------------------------ lidar flight trees
# config engine "flight_trees": {"mode": "lidar", ...} (Eagle Knoll, OPTIMIZE.md 2026-11-06). Replaces the constant
# 20-yd crown and the flat 70 % stop with the measured canopy: every cell's crown top from the 3DEP lidar
# height-above-ground (+ growth since the survey), a crown base at base_frac of the local tree height, and a stop
# chance that grows with the length of the ball's path inside crowns: P(stop) = 1 - exp(-k L). k is the extinction of
# ball-stopping contacts per yard of path (woody area index of leaf-off broadleaf crowns, ball size, the leaf share
# left on the trees in early November); see OPTIMIZE.md section 12.
LIDAR_DEFAULTS = dict(units_m=0.25, nodata=255, growth_m=1.5, min_tree_m=4.0, base_frac=0.35, base_window_yds=7,
                      k_per_yd=0.10, step_yds=3.0, f0=0.3, min_along=100.0, exclude=("ob",), fill_chm=None,
                      fill_units_m=1.0, fill_default_m=10.0)
CANOPY_STEP = 1.0                                 # yds: canopy grid of a hole (tee frame)
_RASTERS = {}
LIDAR_ENV = dict(k_per_yd="V2_LIDAR_K", growth_m="V2_LIDAR_GROWTH", base_frac="V2_LIDAR_BASE",
                 min_tree_m="V2_LIDAR_MIN")        # sensitivity runs (opt/solve2.py variants)


def lidar_opts(ft):
    """config flight_trees (mode lidar) + defaults + V2_LIDAR_* environment overrides (sensitivities)."""
    if os.environ.get("V2_FLIGHT_MODE") == "legacy":          # A/B against the constant-height check
        return None
    o = dict(LIDAR_DEFAULTS)
    o.update({k: v for k, v in ft.items() if k != "mode"})
    for k, e in LIDAR_ENV.items():
        if os.environ.get(e):
            o[k] = float(os.environ[e])
    o["exclude"] = tuple(o.get("exclude") or ())
    return o


def _raster_nearest(path):
    """lonlat (N,2) -> raster value (nearest cell, the file's units; NaN outside / nodata kept as is)."""
    if path not in _RASTERS:
        import rasterio
        from pyproj import Transformer
        with rasterio.open(path) as src:
            _RASTERS[path] = (src.read(1), ~src.transform,
                              Transformer.from_crs("EPSG:4326", src.crs.to_string(), always_xy=True))
    z, inv, to = _RASTERS[path]

    def f(ll):
        ll = np.atleast_2d(np.asarray(ll, float))
        x, y = to.transform(ll[:, 0], ll[:, 1])
        c = np.floor(inv.a * np.asarray(x) + inv.b * np.asarray(y) + inv.c).astype(np.int64)
        r = np.floor(inv.d * np.asarray(x) + inv.e * np.asarray(y) + inv.f).astype(np.int64)
        ok = (c >= 0) & (r >= 0) & (c < z.shape[1]) & (r < z.shape[0])
        v = z[np.clip(r, 0, z.shape[0] - 1), np.clip(c, 0, z.shape[1] - 1)].astype(float)
        return np.where(ok, v, np.nan)
    return f


def canopy_grid(M, hd, frame_json, chm_path, opts, R=None):
    """(ga, gl, top, base) on a CANOPY_STEP grid of the tee frame, in yds above the ground: crown top from the lidar
    height-above-ground (nodata / outside -> no tree) + growth, cells under min_tree_m -> no crown, cells on map lies in
    opts["exclude"] (OB: the house lots on 18, whose roofs are in the lidar too) -> no crown; crown base = base_frac x
    the tallest top within base_window_yds (the crown of that tree, not of its sloping edge). None without the file."""
    if not chm_path or not os.path.exists(chm_path):
        return None
    if os.path.join(CD, "imagery") not in sys.path:
        sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as RD
    from scipy import ndimage
    f = _raster_nearest(chm_path)
    fr = RD.Frame.from_json(frame_json)
    tee, fwd, right, ppy = M.frame(hd)
    ga = np.arange(M.A0, M.A1 + CANOPY_STEP, CANOPY_STEP)
    gl = np.arange(M.L0, M.L1 + CANOPY_STEP, CANOPY_STEP)
    AA, LL = np.meshgrid(ga, gl, indexing="ij")
    pts = tee + (AA.ravel()[:, None] * fwd + LL.ravel()[:, None] * right) * ppy
    v = np.asarray(f(fr.px_to_ll(pts)), float).reshape(AA.shape)
    v[~np.isfinite(v) | (v == opts["nodata"])] = 0.0
    top_m = v * opts["units_m"]
    tree = top_m >= opts["min_tree_m"]
    top = np.where(tree, (top_m + opts["growth_m"]) / 0.9144, 0.0)
    lie = R.lie_at(AA, LL) if R is not None else None
    fill = opts.get("fill_chm")
    if lie is not None and fill is not None:
        # map trees with no 2015 lidar crown (grown in since: 5 left, 9 right on the NAIP 2020 pass): the newer
        # canopy-height map (Meta / WRI, 1 m, ~2018-20 imagery) there, else fill_default_m; no growth added
        miss = (lie == M.CODE["recovery"]) & ~tree
        if miss.any():
            fv = np.asarray(_raster_nearest(os.path.join(ROOT, fill) if not os.path.isabs(fill) else fill)(
                fr.px_to_ll(pts)), float).reshape(AA.shape) * opts.get("fill_units_m", 1.0)
            fv[~np.isfinite(fv) | (fv > 60)] = 0.0
            fv = np.where(fv >= opts["min_tree_m"], fv, opts.get("fill_default_m", 10.0))
            top = np.where(miss, fv / 0.9144, top)
    if lie is not None and opts.get("exclude"):
        for k in opts["exclude"]:
            if k in M.CODE:
                top = np.where(lie == M.CODE[k], 0.0, top)
    w = max(1, int(round(opts["base_window_yds"] / CANOPY_STEP)))
    base = np.where(top > 0, opts["base_frac"] * ndimage.maximum_filter(top, size=w, mode="nearest"), 0.0)
    return ga, gl, top.astype(np.float32), base.astype(np.float32)


def lidar_flight_ev_curve(M, opts, canopy_of, drop_of=None):
    """M.ev_curve with the flight traced through the measured crowns. Each swing's descent (from f0 of its carry,
    and min_along yds out, in step_yds steps along the straight tee-to-landing line) is at
    clearance = flight height + the ground's drop below the tee - that fraction of the landing drop (as in
    flight_tree_ev_curve). Where base < clearance < top the ball is inside a crown and its path length there (3-D,
    the flight's own slope) accumulates. The ball stops at the first point where that length passes its own
    exponential draw -ln(1 - u) / k (u: one uniform per swing shared by every aim and club, common random numbers),
    i.e. P(stop) = 1 - exp(-k L) over the whole path, and drops there: it finishes at that spot on the map, whatever
    the lie (trees under the crown: the punch-out cost; rough under an overhanging edge: rough). canopy_of(hd) ->
    canopy_grid or None (no flight check on that hole); drop_of(hd) -> ground_drop_grid or None (flat ground)."""
    base_shots, base_finish = M.shots, M.finish
    k = float(opts["k_per_yd"])

    def ev_curve(R, S, hd, club, P, z, aims, wind=None):
        car, dev, roll = base_shots(hd, club, P, z, wind)
        a, l, lie = base_finish(R, car[:, None], dev[:, None] + aims[None, :], roll[:, None], P["rough_roll"],
                                P.get("v1_roll", False))
        C = canopy_of(hd) if canopy_of else None
        if C is None or k <= 0:
            s = S[R.idx(a, l)]
            return 1.0 + s.mean(0), (a, l, lie, s)
        ga, gl, top, base = C
        tmax = float(top.max())
        kind = "wood" if club in M.WOODS else "iron"
        cm = float(np.median(car))
        n = max(4, int(np.ceil((1.0 - opts["f0"]) * cm / opts["step_yds"])))
        F = np.linspace(opts["f0"], 1.0, n + 1)[:-1] + 0.5 * (1.0 - opts["f0"]) / n      # step mid-points
        y = flight_heights(F, kind, cm)
        dydx = np.gradient(flight_heights(np.linspace(0, 1, 401), kind, cm), np.linspace(0, cm, 401))
        slope = np.interp(F, np.linspace(0, 1, 401), dydx)
        G = drop_of(hd) if drop_of else None
        if G is not None:
            dga, dgl, dg = G

            def drop(pa, pl):
                ia = np.clip(np.rint((pa - dga[0]) / DROP_STEP).astype(np.int32), 0, len(dga) - 1)
                il = np.clip(np.rint((pl - dgl[0]) / DROP_STEP).astype(np.int32), 0, len(dgl) - 1)
                return dg[ia, il]
        u = np.random.default_rng(int(z.shape[1]) * 7919 + 17).random(z.shape[1])
        need = (-np.log1p(-np.minimum(u, 1 - 1e-12)) / k).astype(np.float32)   # yds of crown this swing survives
        shp = a.shape
        lat0 = (dev[:, None] + aims[None, :]).ravel()
        car1 = np.broadcast_to(car[:, None], shp).ravel()
        need1 = np.broadcast_to(need[:, None], shp).ravel()
        sw = np.broadcast_to(np.arange(shp[0])[:, None], shp).ravel()
        d_land = drop(car1, lat0) if G is not None else np.zeros_like(car1)
        dmin = float(G[2].min()) if G is not None else 0.0          # the ground is never higher than this
        acc = np.zeros(car1.shape, np.float32)
        stop = np.zeros(car1.shape, bool)
        ha, hl = np.zeros(car1.shape), np.zeros(car1.shape)
        stepf = (1.0 - opts["f0"]) / n
        for f, yf, sl in zip(F, y, slope):
            # cheap lower bound of the clearance first, then only the balls that can be under a crown top
            c = np.flatnonzero((yf - f * d_land + dmin < tmax) & ~stop & (car1 * f >= opts["min_along"]))
            if not c.size:
                continue
            pa, pl = car1[c] * f, lat0[c] * f
            clear = yf - f * d_land[c] + (drop(pa, pl) if G is not None else 0.0)
            ia = np.clip(np.rint((pa - ga[0]) / CANOPY_STEP).astype(np.int32), 0, len(ga) - 1)
            il = np.clip(np.rint((pl - gl[0]) / CANOPY_STEP).astype(np.int32), 0, len(gl) - 1)
            ins = (clear < top[ia, il]) & (clear > base[ia, il])
            if not ins.any():
                continue
            c, pa, pl = c[ins], pa[ins], pl[ins]
            acc[c] += (car1[c] * stepf * math.sqrt(1.0 + sl * sl)).astype(np.float32)
            s = acc[c] >= need1[c]
            c, pa, pl = c[s], pa[s], pl[s]
            ha[c], hl[c] = pa, pl
            stop[c] = True
        stop = stop.reshape(shp)
        ha, hl = ha.reshape(shp), hl.reshape(shp)
        if stop.any():
            a = np.where(stop, ha, a)
            l = np.where(stop, hl, l)
            lie = np.where(stop, R.lie_at(a, l), lie)
        s = S[R.idx(a, l)]
        return 1.0 + s.mean(0), (a, l, lie, s)
    ev_curve._flight_trees = ("lidar", k)
    ev_curve._lidar_stop = True
    return ev_curve


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


REFINE_HALF = 10.0       # refine stage: +/- yds around the coarse aim (0.5-yd steps)
REFINE_SEED = 32


def refined_solver(M, D, WG2, n2, half=REFINE_HALF, seed=REFINE_SEED):
    """wind_grid_v2.solve with a second, precise stage (Eagle Knoll MC audit 2026-11-03): the grid's single central
    world uses N = 2,500 common swings for the whole +/-75-yd aim curve, so a club-vs-club margin has a Monte Carlo
    SE of ~0.004-0.005 strokes and fresh swings flipped 3 of 13 cells of a 10-mph hole-15 grid (2-wood -> 4-wood).
    Stage 1 is the original solve (coarse curve, aim window); stage 2 re-evaluates every club on aim +/- `half` yds
    with n2 fresh common swings (seed `seed`, shared by every club, cell, temperature and hole: paired differences)
    and takes the aim, EV and pick from that curve. The 0.005 window comes from the fine curve where it fits inside
    the refined range, else that side keeps the coarse edge. Spirit Hollow's wind_grid_v2.py is not edited: this
    replaces WG2.solve in the tournament wind job only (nccga_v2 request "refine_swings")."""
    orig = WG2.solve
    z2 = M.draws_z(int(n2), seed)

    def solve(h, P, R, S, z, speed, rel):
        res = orig(h, P, R, S, z, speed, rel)
        hd = M.HOLES[h]
        for c, v in res["clubs"].items():
            hook = WG2.wind_hook(c, speed, rel) if speed else None
            dr = hook(*M.club_numbers(hd, c, P))[4] if hook else 0.0
            lo, hi = -D.AIM_LIMIT - dr, D.AIM_LIMIT - dr
            a0 = min(max(v["aim"], lo), hi)
            aims = np.arange(a0 - half, a0 + half + 1e-9, 0.5)
            ev, _ = M.ev_curve(R, S, hd, c, P, z2, aims, wind=hook)
            r = D.robust_aim(aims, ev, lo=max(lo, aims[0]), hi=min(hi, aims[-1]))
            zl, zh = r["window"]
            if zl <= aims[0] + 1e-9:
                zl = min(zl, v["zone"][0])
            if zh >= aims[-1] - 1e-9:
                zh = max(zh, v["zone"][1])
            v.update(aim=r["aim"], ev=r["ev"], zone=[zl, zh], at_bound=bool(v["at_bound"] or r["at_bound"]),
                     ev_coarse=v["ev"], n_refine=int(n2))
        real = [c for c in res["clubs"] if c not in M.HYPOTHETICAL]
        best = min(real, key=lambda c: res["clubs"][c]["ev"])
        runner = min((c for c in real if c != best), key=lambda c: res["clubs"][c]["ev"])
        res.update(pick=best, runner=runner, margin=res["clubs"][runner]["ev"] - res["clubs"][best]["ev"])
        return res
    return solve


def run_wind(slug, which, back, temps, out, swings=2500, refine=0):
    course, meta, M, D = activate(slug, which)
    os.environ.update(TEE_BACK=str(back), WIND_TEMPS=",".join(str(t) for t in temps), WIND_SWINGS=str(swings),
                      WIND_OUT=out, V2_GEOM="", WIND_HOLES=os.environ.get("WIND_ONLY", ""))
    import wind_grid as WG
    WG.osm_bearings = lambda: {}
    import wind_grid_v2 as WG2
    if getattr(D, "_aim_limit", None):           # config engine aim_limit: the wind grid's aim curve covers it + drift
        L = float(D._aim_limit)
        WG2.AIMS = np.arange(-(L + 35.0), L + 35.0 + 1e-9, 0.5)
    WG2.TEMPS = [float(t) for t in temps]
    WG2.N = swings
    if refine:
        WG2.solve = refined_solver(M, D, WG2, refine)
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
        if d["back"] not in grids:                   # a holes-limited run keeps the stored grid's other holes
            prev = os.path.join(out, "wind_grid.json" if not d["back"] else f"wind_grid_back{d['back']:+.0f}.json")
            base = json.load(open(prev)) if os.path.exists(prev) else {}
            same = base.get("speeds") == d["speeds"] and base.get("dirs") == d["dirs"]
            grids[d["back"]] = dict(speeds=d["speeds"], dirs=d["dirs"], temps=list(base.get("temps", [])) if same else [],
                                    bearings=dict(base.get("bearings", {})) if same else {},
                                    holes=dict(base.get("holes", {})) if same else {},
                                    par3=dict(base.get("par3", {})) if same else {}, tee_back=d["back"], model="v2")
        g = grids[d["back"]]
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
def crop_factory(shots, img_w=None, quality=None, sharpen=False, subsampling=None):
    """img_w / quality / sharpen / subsampling: config "display_imagery" {"img_w", "jpeg_q", "sharpen" (true or
    [radius, percent, threshold]), "jpeg_sub" (0 = 4:4:4, 2 = 4:2:0)} (page photos only). The source photo may be
    rendered at a multiple of the 920 x 2000 frame and taller than it (render_display): k = width / 920."""
    from PIL import Image, ImageFilter
    img_w, quality = img_w or IMG_W, quality or JPEG_Q
    usm = (1.6, 80, 2) if sharpen is True else tuple(sharpen) if sharpen else None
    sub = subsampling if subsampling is not None else (0 if quality >= 85 else 2)

    def crop_jpeg(image, box, y_max=2000):
        """box in the render frame (920 wide) -> (data URI, scale, (x0, y0), size); rows off the render padded."""
        im = Image.open(os.path.join(shots, image)).convert("RGB")
        k = im.width / 920
        h_fr = im.height / k
        x0, y0, x1, y1 = box
        x0, x1 = max(0, x0), min(920, x1)
        top, bot = max(0, y0), min(h_fr, y1)
        c = im.crop((int(round(x0 * k)), int(round(top * k)), int(round(x1 * k)), int(round(bot * k))))
        if y1 > h_fr or y0 < 0:
            pad = Image.new("RGB", (c.width, int(round((y1 - y0) * k))), (52, 66, 56))
            pad.paste(c, (0, int(round((top - y0) * k))))
            c = pad
        scale = img_w / c.width
        c = c.resize((img_w, int(round(c.height * scale))), Image.LANCZOS)
        if usm:                          # the source is upsampled ~2x for the page: a light unsharp mask restores edges
            c = c.filter(ImageFilter.UnsharpMask(radius=usm[0], percent=int(usm[1]), threshold=int(usm[2])))
        buf = io.BytesIO()
        c.save(buf, "JPEG", quality=quality, optimize=True, progressive=True, subsampling=sub)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), scale * k, (x0, y0), c.size
    return crop_jpeg


def install_landing_pattern(M, BP):
    """The dashed landing oval: build_page_v2.cloud (Spirit Hollow's, read-only) -> course_data/library/
    landing_pattern.page_cloud, the same simulated finishes measured in the tee-line frame (lateral left / right,
    depth short / long of the median after a linear tilt) instead of covariance eigen axes with a symmetric depth,
    which drew the model's wider-than-long pattern as a near circle (Eagle Knoll 2026-11-03: drawn depth / width
    0.75-1.06, axes up to 76 degrees off the lateral). The template draws the new shape (cloud fields long / short /
    left / right / tilt); V2_LANDING_PATTERN=0 keeps the old cloud. Only this module's page stage is patched:
    Spirit Hollow's own page (spirit_hollow/v2/build_page_v2.py main) is not built through here."""
    if os.environ.get("V2_LANDING_PATTERN", "1") == "0" or getattr(BP, "_tee_frame_cloud", False):
        return
    lib = os.path.join(CD, "library")
    if lib not in sys.path:
        sys.path.insert(0, lib)
    import landing_pattern as LP
    BP.cloud = lambda h, grid0, temp_f: LP.page_cloud(M, h, grid0, temp_f)
    BP._tee_frame_cloud = True


HAZ_LIES = ("water", "ob")       # outlined on the page photo (the creek under the trees on 17, the OB on 18 ...)
P3_PAD = 32.0                    # yds of ground shown round a par-3 green (was 14: the water short of 6 / 16 was cut off)
BOX_MIN = 4.0                    # yds: a par-3 target box is never drawn thinner than this


def _simplify(poly, tol=1.5):
    """Drop vertices closer than tol px to the last kept one (page size), rounded to 0.1 px."""
    out = []
    for x, y in poly:
        if not out or math.hypot(x - out[-1][0], y - out[-1][1]) >= tol:
            out.append([round(float(x), 1), round(float(y), 1)])
    return out if len(out) >= 3 else []


def hazard_outlines(zones):
    return [[lie, q] for lie, poly in zones if lie in HAZ_LIES for q in [_simplify(poly)] if q]


def par3_zones(cfg, which):
    """Each par 3's zones (render px), captured from the package load (the course module keeps only the green and
    the edge-hazard summary)."""
    PK = product_pk()
    got = {}
    orig = PK._par3

    def cap(fr, green_ll, gpoly, zones, length, k):
        got[k] = list(zones)
        return orig(fr, green_ll, gpoly, zones, length, k)
    PK._par3 = cap
    try:
        PK.load(os.path.join(ROOT, cfg["truth_package" if which.startswith("truth") else "package"]), base_tees(cfg, which))
    except Exception as e:                       # noqa: BLE001
        print("par-3 zones not read:", e)
    finally:
        PK._par3 = orig
    return got


def floored_plan(plan_fn, min_w=BOX_MIN):
    """yardage_book.par3_plan with the box drawn at least min_w yds each way, centred on the DECADE target (which is
    kept). When the DECADE cushions do not fit, the worse side keeps its full cushion and the box is a single line
    (hole 16 Back: 159-159 in light wind), drawn as a point. The target is NOT moved: an expected-strokes check on
    Will's iron pattern (eagle_knoll/opt/par3_ev.py) found moving it 2 yds long on 16, toward the trees, costs
    ~0.03 strokes. Spirit Hollow's own book does not use this (patched in the v2_course page process only)."""
    def plan(p, *a, **k):
        r = dict(plan_fn(p, *a, **k))
        for ax in ("lat", "dep"):
            lo, hi = r[ax]
            if hi - lo < min_w:
                c = (lo + hi) / 2
                r[ax] = (c - min_w / 2, c + min_w / 2)
        return r
    plan._floored = True
    return plan


def _frames(slug, which):
    """FRAMES {hole key: frame json} (render px <-> WGS84) of a which's course module, read without importing it."""
    import ast
    for node in ast.parse(open(cdir(slug, which, "course.py")).read()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "FRAMES" for t in node.targets):
            return {str(k): v for k, v in ast.literal_eval(node.value).items()}
    return {}


def share_plan(slug, cfg, which, alt):
    """config "display_imagery" {"share_photos": true}: the alt bases (Eagle, Middle ...) show the main set's photo
    of the same hole instead of carrying their own (page size: one photo per hole, not one per set). Every set's
    overlays stay in its own frame; only the photo is drawn through an affine map (main crop px -> the set's view).
    -> ({key: [boxes in main frame px]} to widen the main crop so it covers every set's view, {set: {key: (L, t)}}
    main frame px -> alt frame px, fitted on WGS84 through both frames, residual < 0.05 px)."""
    sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as R
    fm = _frames(slug, which)
    extra, maps = {}, {}
    for s, holes in alt.items():
        fa = _frames(slug, (cfg.get("alt_bases") or {})[s])
        maps[s] = {}
        for h in holes:
            k = h["key"]
            if k not in fm or k not in fa or not h.get("img"):
                continue
            Fm, Fa = R.Frame.from_json(fm[k]), R.Frame.from_json(fa[k])
            gx, gy = np.meshgrid(np.linspace(0, 920, 5), np.linspace(0, 2200, 9))
            P = np.c_[gx.ravel(), gy.ravel()]
            Q = Fa.ll_to_px(Fm.px_to_ll(P))
            A, *_ = np.linalg.lstsq(np.c_[P, np.ones(len(P))], Q, rcond=None)
            res = float(np.abs(np.c_[P, np.ones(len(P))] @ A - Q).max())
            if res > 0.5:
                print(f"share photos: {s} hole {k} frames not affine ({res:.2f} px): own photo kept")
                continue
            L, t = A[:2].T, A[2]
            x0, y0 = h["x0"], h["y0"]
            x1, y1 = x0 + h["w"] / h["s"], y0 + h["h"] / h["s"]
            C = Fm.ll_to_px(Fa.px_to_ll(np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])))
            extra.setdefault(k, []).append((C[:, 0].min(), C[:, 1].min(), C[:, 0].max(), C[:, 1].max()))
            maps[s][k] = (L, t)
    return extra, maps


def share_photos(holes, alt, maps):
    """Point each alt hole at the main hole's photo: img_ref (the main key) + img_m, the SVG matrix from the main
    photo's px to the alt view's px (template: <image transform="matrix(...)">)."""
    main = {h["key"]: h for h in holes}
    n = 0
    for s, hs in alt.items():
        for h in hs:
            k = h["key"]
            if k not in maps.get(s, {}) or k not in main:
                continue
            L, t = maps[s][k]
            m = main[k]
            om, oa = np.array([m["x0"], m["y0"]]), np.array([h["x0"], h["y0"]])
            Lq = h["s"] / m["s"] * L
            e = h["s"] * (L @ om + t - oa)
            # the alt view (0..w, 0..h) must lie inside the main photo
            inv = np.linalg.inv(Lq)
            cz = (np.array([[0, 0], [h["w"], 0], [h["w"], h["h"]], [0, h["h"]]]) - e) @ inv.T
            if cz[:, 0].min() < -2 or cz[:, 1].min() < -2 or cz[:, 0].max() > m["w"] + 2 or cz[:, 1].max() > m["h"] + 2:
                print(f"share photos: {s} hole {k} view not inside the main photo: own photo kept")
                continue
            h["img"], h["img_ref"] = "", k
            h["img_m"] = [round(float(v), 5) for v in (Lq[0, 0], Lq[1, 0], Lq[0, 1], Lq[1, 1], e[0], e[1])]
            n += 1
    print(f"share photos: {n} alt holes use the main photo")


HAZ_WORDS = re.compile(r"water|pond|lake|creek|stream|ravine|hazard|penalt|\bOB\b|out of bounds|bunker|sand|"
                       r"\btrees?\b|(?<![-\w])wood(s|ed)?\b|house lots", re.I)


def golfer_text(t):
    """Golfer-facing note without hazard words (config "page_text" {"hide_hazards": true}; golfer request 2026-11-06:
    "I don't want my mind to think about water"): the finish shares keep fairway / first cut / yards in (the water,
    OB, sand, trees and long-grass shares are dropped from the text only: the picks and numbers are unchanged), and
    any other sentence naming a hazard is left out."""
    t = re.sub(r",\s*(sand|trees|long grass|water|OB)\s+\d+%", "", t or "")
    t = re.sub(r",\s*first cut 0%", "", t)            # no first-cut class on a hand map that has none (audit nit)
    t = re.sub(r"\s*\(Edge hazards[^)]*\)", "", t)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z~])", t.strip())
    return " ".join(x for x in parts if x and not HAZ_WORDS.search(x)).strip()


def _photo_source(slug, which):
    """'USGS NAIP Plus ... 0.25 m' from the rendered photos' index (the page footer names the photo it shows)."""
    try:
        i = next(iter(json.load(open(cdir(slug, which, "screenshots", "index.json"))).values()))
        return f"{i.get('imagery_source') or 'aerial photo'}, {float(i['source_res_m']):.2g} m"
    except Exception:                                          # noqa: BLE001
        return ""


def direct_factory(course, disp, di):
    """config display_imagery "direct": each page photo rendered straight from the display imagery (0.3 m NAIP Plus)
    at its page size (img_w px wide) with Lanczos: one resampling step, no 920 x 2000 render in between (golfer
    2026-11-06: par 3s "really blurry", a tight crop of the render upscaled 3-4x). The crop box is in the hole's
    frame px; the photo frame is the same frame scaled by m = img_w / box width and shifted to the box corner, so
    page px = (frame px - box corner) x m exactly, as for a crop (overlays unchanged). None when no display imagery."""
    if not disp:
        return None
    import cv2
    from PIL import Image, ImageFilter
    sys.path.insert(0, os.path.join(CD, "imagery"))
    import render as R
    img = R.Imagery(disp)
    img_w, q = int(di.get("img_w") or IMG_W), int(di.get("jpeg_q") or JPEG_Q)
    sh = di.get("sharpen")
    usm = (1.6, 80, 2) if sh is True else tuple(sh) if sh else None
    sub = di.get("jpeg_sub", 2)
    frames = {str(k): v for k, v in course.FRAMES.items()}

    def render_box(key, box):
        fr = R.Frame.from_json(frames[str(key)])
        x0, y0, x1, y1 = box
        m = img_w / (x1 - x0)
        H = int(round((y1 - y0) * m))
        f2 = R.Frame(fr.tee_ll, fr.aim_ll, fr.ppy * m, (fr.tee_px - np.array([x0, y0])) * m, fr.proj, (img_w, H))
        out, _ = R.render(f2, img, interp=cv2.INTER_LANCZOS4)
        c = Image.fromarray(out[..., :3])
        if usm:
            c = c.filter(ImageFilter.UnsharpMask(radius=usm[0], percent=int(usm[1]), threshold=int(usm[2])))
        buf = io.BytesIO()
        c.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling=sub)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), m, (x0, y0), c.size
    print("page photos rendered directly from", disp, f"({img.res:.2f} m)")
    return render_box


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
    install_landing_pattern(M, BP)
    yb.use_course(course.NAME, cdir(slug, which), slug, course.HOLES, course.PAR3, course.NOTES, course.AIM_AT,
                  course.ORDER, course.LABELS)
    di = config(slug).get("display_imagery") or {}
    crop = crop_factory(cdir(slug, which, "screenshots"), img_w=di.get("img_w"), quality=di.get("jpeg_q"),
                        sharpen=di.get("sharpen") or False, subsampling=di.get("jpeg_sub"))
    p3_now = {}
    direct = direct_factory(course, display_dir(slug), di) if di.get("direct") else None
    share = bool(di.get("share_photos")) and bool(alt)
    extra, maps = share_plan(slug, cfg, which, alt) if share else ({}, {})
    cur = {}

    def crop_jpeg(image, box, *a, **k):
        pp = p3_now.get("ppy")
        if pp:                                   # par 3: more ground round the green, most of it on the tee side
            e = (P3_PAD - 14.0) * pp
            box = (box[0] - e, box[1] - e, box[2] + e, box[3] + 1.6 * e)
            vw = float(di.get("p3_view_yds") or 0) * pp   # show more ground rather than magnify the 0.3 m source
            if box[2] - box[0] < vw:
                c = (box[0] + box[2]) / 2
                box = (c - vw / 2, box[1], c + vw / 2, box[3])
            if box[3] - box[1] < 1.1 * vw:              # the extra height on the tee side
                box = (box[0], box[1], box[2], box[1] + 1.1 * vw)
        gy_ = di.get("include_green_yds")       # tee shots: the "Whole hole" photo reaches the green (+ this pad)
        if gy_ and not pp:
            try:
                hd_ = course.HOLES[int(cur.get("key"))]
                gx, gyp = [float(v) for v in hd_["green"]]
                e = float(gy_) * 3.4
                box = (min(box[0], gx - e), min(box[1], gyp - e), max(box[2], gx + e), box[3])
                if not direct:                   # a crop of the 920-wide render: no photo above / beside the frame
                    box = (max(box[0], 0.0), max(box[1], 0.0), min(box[2], 920.0), box[3])
            except (KeyError, TypeError, ValueError):
                pass
        for b in extra.get(cur.get("key"), []):  # shared photo: cover every set's view of this hole
            box = (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
        if gy_ and not pp and not direct:        # an alt set's longer view must not run off the top of the render
            box = (max(box[0], 0.0), max(box[1], 0.0), min(box[2], 920.0), box[3])
        if direct:
            return direct(cur.get("key"), box)
        return crop(image, box, *a, **k)
    BW.crop_jpeg = crop_jpeg
    if cfg.get("par3_targets"):                  # expected-strokes par-3 box (course_data/courses/par3_targets.py)
        import par3_targets
        par3_targets.install(cfg, BW, meta["tee_set"])
    par3_hole0 = BW.par3_hole

    def par3_hole(h):
        p = course.PAR3[h]
        p3_now["ppy"] = BW.frame(p["tee"], p["flag"], p["center"])[3]
        try:
            return par3_hole0(h)
        finally:
            p3_now.clear()
    if not getattr(yb.par3_plan, "_floored", False):
        yb.par3_plan = floored_plan(yb.par3_plan)
    p3z = par3_zones(cfg, which) if course.PAR3 else {}
    foot_a1 = footprint_ends(cfg, which, course, M)
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
    pt = cfg.get("page_text") or {}
    calm = bool(pt.get("hide_hazards"))

    def map_note(h):
        """config hole_notes (the mapper's record, unchanged); with hide_hazards the golfer reads page_text
        "map_notes" {hole: text} instead ("" = none), else the hole note without its hazard sentences."""
        hn = (cfg.get("hole_notes") or {}).get(str(h))
        if not calm:
            return hn
        own = pt.get("map_notes") or {}
        return own[str(h)] if str(h) in own else golfer_text(hn)
    for h in course.ORDER:
        cur["key"] = str(h)
        d = par3_hole(h) if h in course.PAR3 else BW.tee_hole(h)
        d["haz"] = [] if calm else hazard_outlines(p3z.get(h, []) if h in course.PAR3 else course.HOLES[h].get("zones", []))
        d["key"] = str(h)
        d["label"] = str(h)
        if h in foot_a1:
            # page_text "checked_beyond" {hole: yds}: ground past the hand corridor's end that was checked on the photo
            # and lidar afterwards (Gateway 18: to 395), so the "lands past the hand-checked map" badge starts later
            d["foot_a1"] = foot_a1[h] + float(((config(slug).get("page_text") or {}).get("checked_beyond") or {}).get(str(h), 0))
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
                if calm:
                    d["note"] = golfer_text(d["note"])
                d["calm"] = dict(pick=r["pick"], aim=r["aim"], tie=bool(r["tie"]), margin=r["margin"],
                                 flips=r.get("width_flips", []), temp=r.get("temp_f", M.hole_temp(h)),
                                 window=r.get("window"), runner=r.get("runner"), se=r.get("margin_se"),
                                 p=r.get("p_pick_beats_runner"))
            hn = map_note(h)
            if hn:
                d["note"] = (d["note"] + " " if d["note"] else "") + "Map: " + hn
                d["map_note"] = hn
        if h in course.PAR3:
            hn = map_note(h)
            if calm:
                d["note"], d["short"] = golfer_text(d.get("note")), golfer_text(d.get("short"))
            if hn:
                d["note"] = (d["note"] + " " if d["note"] else "") + "Map: " + hn
            p3n = (pt.get("par3_notes") or {}).get(str(h))          # page_text "par3_notes": replaces the par-3 note
            if p3n is not None:
                d["note"] = p3n
        holes.append(d)
    tot = {s: meta["tee_sets"][s].get("total") for s in sets}
    data = dict(slug=slug, title=cfg.get("title") or (course.NAME + " Caddie"), base_set=base, sets=sets,
                colors=cfg.get("colors", {}), set_totals=tot, days=cfg["days"],
                day_labels=cfg.get("day_labels") or cfg["days"], tee_hour=float(cfg.get("tee_hour", 9.0)),
                sub=cfg.get("sub", ""), foot_extra=cfg.get("foot", ""), placeholder=bool(fc.get("placeholder")),
                fc_note=fc.get("note", ""), imagery=meta.get("imagery_date"), imagery_src=_photo_source(slug, which),
                speeds=grid["speeds"], dirs=grid["dirs"], temps=grid["temps"], holes=holes, offsets=sorted(grids),
                forecast=[dict(date=r["date"], hour=r["hour"], mph=r["wind_mph"], gust=r["gust_mph"],
                               dir=r["wind_from_deg"], temp=r["temp_f"]) for r in fc["hourly"]],
                fetched=fc.get("fetched_utc", ""), draws=int(cfg.get("draws", 64)),
                aim_limit=float(D.AIM_LIMIT), p3_bag=cfg.get("par3_bag"),
                temp_k=float(M.central()["temp_k"]))
    pt_ = cfg.get("page_text") or {}
    if pt_.get("simple"):
        data["simple"] = True
    if pt_.get("close_margin"):
        data["close_margin"] = float(pt_["close_margin"])
    for d_ in holes:
        cn = (pt_.get("condition_notes") or {}).get(str(d_.get("key")))
        if isinstance(cn, dict):                       # {tee set: text}: a note for one base set only
            cn = cn.get(d_.get("base_set"))
        if cn and d_.get("kind") == "tee":
            d_["cond_note"] = cn
        # page_text "why" {hole: text | {tee set: text}}: the one-sentence reason for the pick, shown first in the
        # note; "prefer_on_tie" {hole: {"club": c, "within": strokes, "text": pill}}: show this club when it is within
        # that many strokes of the best one (Gateway 10: the two woods are level, the shorter one misses less often)
        wy = (pt_.get("why") or {}).get(str(d_.get("key")))
        if isinstance(wy, dict):
            wy = wy.get(d_.get("base_set"))
        if wy and d_.get("kind") == "tee":
            d_["why"] = wy
        sn = (pt_.get("set_notes") or {}).get(str(d_.get("key")))    # {tee set picked on the page: pill text}
        if sn and d_.get("kind") == "tee":
            d_["set_note"] = sn
        pf = (pt_.get("prefer_on_tie") or {}).get(str(d_.get("key")))
        if pf and d_.get("kind") == "tee":
            d_["prefer"] = pf
    if cfg.get("par3_drift_per_mph"):
        data["p3_drift"] = float(cfg["par3_drift_per_mph"])
    if cfg.get("temp_note"):
        data["temp_note"] = str(cfg["temp_note"])
    if data_out:
        json.dump(data, open(data_out, "w"), separators=(",", ":"))
        return
    if alt:
        if share:
            share_photos(holes, alt, maps)
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
    ap.add_argument("--refine", type=int, default=0, help="wind: fresh common swings for the +/-10-yd aim refine stage")
    ap.add_argument("--data-out")
    a = ap.parse_intermixed_args()
    if a.cmd == "prepare":
        prepare(a.slug, a.which)
    elif a.cmd == "decide":
        run_decide(a.slug, a.which, [h for h in a.holes.split(",") if h], a.out, draws=a.draws,
                   swings=a.swings or 3000)
    elif a.cmd == "wind":
        temps = [float(t) for t in (a.temps or ",".join(str(t) for t in config(a.slug)["temps"])).split(",")]
        run_wind(a.slug, a.which, a.back, temps, a.out, swings=a.swings or 2500, refine=a.refine)
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
