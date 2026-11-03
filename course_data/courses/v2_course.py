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
    ft = eng.get("flight_trees")
    if ft:
        M.ev_curve = flight_tree_ev_curve(M, float(ft.get("height_yds", 20.0)), float(ft.get("p_hit", 0.7)),
                                          drop_of=eng.get("_drop_of"))


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
    crop = crop_factory(cdir(slug, which, "screenshots"))
    p3_now = {}

    def crop_jpeg(image, box, *a, **k):
        pp = p3_now.get("ppy")
        if pp:                                   # par 3: more ground round the green, most of it on the tee side
            e = (P3_PAD - 14.0) * pp
            box = (box[0] - e, box[1] - e, box[2] + e, box[3] + 1.6 * e)
        return crop(image, box, *a, **k)
    BW.crop_jpeg = crop_jpeg
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
        d = par3_hole(h) if h in course.PAR3 else BW.tee_hole(h)
        d["haz"] = hazard_outlines(p3z.get(h, []) if h in course.PAR3 else course.HOLES[h].get("zones", []))
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
                                 window=r.get("window"), runner=r.get("runner"), se=r.get("margin_se"),
                                 p=r.get("p_pick_beats_runner"))
            hn = (cfg.get("hole_notes") or {}).get(str(h))
            if hn:
                d["note"] = (d["note"] + " " if d["note"] else "") + "Map: " + hn
                d["map_note"] = hn
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
                fetched=fc.get("fetched_utc", ""), draws=int(cfg.get("draws", 64)),
                temp_k=float(M.central()["temp_k"]))
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
