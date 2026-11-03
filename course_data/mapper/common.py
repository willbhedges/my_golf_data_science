"""Shared helpers for the agent mapper (course_data/mapper/BRIEF.md): paths, the base package, corridor frames,
yard <-> WGS84 conversion, the edit shapes an agent writes in edits.json.

Every coordinate an agent writes is (x, along) in yards in ONE hole's corridor frame (render.Frame, UTM; the same
frame as course_data/truth/corridor.py): x = yds right of the corridor set's tee line, along = yds from that tee
towards the package aim point. The frames are fixed when the inputs are rendered (course_data/mapper/<slug>/
frames.json, committed with the edits), so an edit always lands on the ground point it was drawn on.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
for _p in (os.path.join(CD, "truth"), os.path.join(CD, "imagery")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

YD = 0.9144
# the window the mapper reviews and may edit: every par-4/5 tee shot of the corridor set, 120-400 yds out, +/-70 yds
WIN = dict(a0=120.0, a1=400.0, lat=70.0)
LIES = ("fairway", "first_cut", "recovery", "native", "water", "sand", "ob")
LAYER_OF = {"fairway": "fairway", "first_cut": "fairway", "recovery": "trees", "native": "long_grass",
            "water": "water", "sand": "bunkers", "ob": "ob"}
LAYERS = ("fairway", "trees", "long_grass", "water", "ob", "bunkers")
OPS = ("add", "erase", "grow")
# green edits (any hole, any par; BRIEF "Greens"): a window of +/-GREEN_WIN yds around the package green in the
# hole's green frame (par 3: the corridor-set tee -> green, the tee sheet's frame; par 4/5: the hole-line point
# GREEN_APPROACH yds before its end -> green), so x = yds right of the line of approach, along = yds from the frame
# origin (the green sits at `green_along`)
GREEN_WIN = 60.0
GREEN_APPROACH = 100.0
GREEN_AREA = (150.0, 2500.0)      # sq yds: a drawn green outside this is refused (a typo / a whole complex)
GREEN_TYPICAL = (300.0, 1300.0)   # outside this: listed under Checks
CONF = ("high", "medium", "low")
SRC = "agent:mapper"


def log(*a):
    print(*a, flush=True)


def mdir(slug, *p):
    return os.path.join(HERE, slug, *p)


def rj(p, d=None):
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return d


def wj(p, d, indent=1):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, "w") as fh:
        json.dump(d, fh, indent=indent, default=float)


def sha1_file(p):
    h = hashlib.sha1()
    with open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()[:16]


def imagery_dir(slug):
    """The package's imagery (course_data/packages/<slug>/imagery), else the older builder's
    course_data/imagery/<slug>/ (e.g. spirit_hollow: package stage imagery 'ok: course_data/imagery/<slug>')."""
    for d in (os.path.join(CD, "packages", slug, "imagery"), os.path.join(CD, "imagery", slug)):
        if os.path.exists(os.path.join(d, "naip_rgb.tif")):
            return d
    return os.path.join(CD, "packages", slug, "imagery")


def sources(slug):
    """corridor.sources (package NAIP / NIR, vision_any NAIP years, lidar) + the DEM, with the imagery_dir fallback."""
    import corridor as C
    S = C.sources(slug)
    d = imagery_dir(slug)
    if "photo" not in S and os.path.exists(os.path.join(d, "naip_rgb.tif")):
        S["photo"] = C.Raster(os.path.join(d, "naip_rgb.tif"), label="NAIP %s 0.3 m" % C._year(d))
        if os.path.exists(os.path.join(d, "naip_nir.tif")):
            S["nir"] = C.Raster(os.path.join(d, "naip_nir.tif"))
    if os.path.exists(os.path.join(d, "dem.tif")):
        S["dem"] = C.Raster(os.path.join(d, "dem.tif"), label="3DEP DEM")
    return S


def committed_package_path(slug):
    return os.path.join(CD, "packages", slug, "package.json")


def base_package_path(slug):
    """The package the mapper reviewed: course_data/mapper/<slug>/base/package.json (prepare.py), else the
    committed course_data/packages/<slug>/package.json."""
    p = mdir(slug, "base", "package.json")
    return p if os.path.exists(p) else committed_package_path(slug)


def load_base(slug):
    p = base_package_path(slug)
    pkg = rj(p)
    if pkg is None:
        raise SystemExit(f"{slug}: no package at {os.path.relpath(p, ROOT)} (push course_data/requests/package_{slug}.json)")
    return pkg


def hole_key(k):
    return (int(k), "") if str(k).isdigit() else (99, str(k))


def tee_set_of(pkg, want=None):
    sets = list(pkg.get("tee_sets") or {})
    if want:
        k = next((s for s in sets if s.lower() == str(want).lower()), None)
        if k is None:
            raise SystemExit(f"tee set {want!r} not in the package's sets {sets}")
        return k
    return pkg.get("tee_set") or (sets[0] if sets else None)


def corridor_frame(tee_ll, aim_ll, ppy, a0=None, a1=None, lat=None):
    import corridor as C
    return C.corridor_frame(tee_ll, aim_ll, ppy, a0=WIN["a0"] if a0 is None else a0,
                            a1=WIN["a1"] if a1 is None else a1, lat=WIN["lat"] if lat is None else lat)


def make_frames(pkg, st):
    """{ref: {ref, par, set, yards, tee_ll, aim_ll, green_ll, tee_method, tee_conf, frame}} for the par-4/5 holes."""
    out = {}
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: hole_key(kv[0])):
        if int(h.get("par") or 0) < 4:
            continue
        t = (h.get("tees") or {}).get(st) or {}
        tee, aim = t.get("tee_ll") or h.get("tee_ll"), t.get("aim_ll") or h.get("aim_ll")
        if not tee or not aim:
            log(f"  ! hole {ref}: no {st} tee / aim; not framed")
            continue
        fr = corridor_frame(tee, aim, 1.0)
        out[ref] = dict(ref=ref, par=int(h["par"]), set=st, yards=(h.get("yards") or {}).get(st) or t.get("card_yards"),
                        tee_ll=tee, aim_ll=aim, green_ll=h.get("green_ll"), tee_method=t.get("method"),
                        tee_conf=t.get("confidence"), measured=t.get("measured_yards"), frame=fr.to_json())
    return out


def _line_back(line_ll, green_ll, yds):
    """The point `yds` back from the green along the hole line (walked from its end), else the line's start."""
    import corridor as C
    if not line_ll or len(line_ll) < 2:
        return None
    fr = C.corridor_frame(line_ll[0], green_ll, 1.0)
    xy = fr.ll_to_yds(np.asarray([p[:2] for p in line_ll] + [green_ll], float))
    pts = [xy[-1]]
    for q in xy[-2::-1]:
        if np.hypot(*(q - pts[-1])) > 0.5:
            pts.append(q)
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        d = float(np.hypot(*(b - a)))
        if acc + d >= yds:
            t = (yds - acc) / d
            return fr.yds_to_ll(np.array([a + t * (b - a)]))[0].tolist()
        acc += d
    return [float(v) for v in line_ll[0][:2]]


def green_frames(pkg, st):
    """{ref: {ref, par, set, kind, frame, green_along, window {a0, a1, lat}, green_src}} for every hole with a green:
    the frame a green edit is drawn in (par 3: corridor-set tee -> green; par 4/5: GREEN_APPROACH yds back along the
    hole line -> green)."""
    out = {}
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: hole_key(kv[0])):
        g = h.get("green_ll")
        if not g:
            continue
        t = (h.get("tees") or {}).get(st) or {}
        tee = t.get("tee_ll") or h.get("tee_ll")
        par = int(h.get("par") or 0)
        org, kind = None, "tee"
        if par >= 4:
            org, kind = _line_back(h.get("hole_line_ll"), g, GREEN_APPROACH), "approach"
        if org is None or yd_between(org, g) < 20:
            org, kind = tee, "tee"
        if not org:
            continue
        fr = corridor_frame(org, g, 1.0)
        ga = float(-fr.ll_to_yds(np.asarray([g], float))[0][1])
        out[ref] = dict(ref=ref, par=par, set=st, kind=kind, frame=fr.to_json(), green_along=round(ga, 1),
                        window=dict(a0=round(ga - GREEN_WIN, 1), a1=round(ga + GREEN_WIN, 1), lat=GREEN_WIN),
                        green_src=(h.get("provenance") or {}).get("green"))
    return out


def has_mapped_green(h):
    """The hole has a green outline someone mapped (OSM, a review, the mapper), not an estimate."""
    src = str((h.get("provenance") or {}).get("green") or "")
    return bool(h.get("green_polygon_ll")) and (src.startswith("osm") or src.startswith("review") or src.startswith("agent"))


def frames(slug):
    f = rj(mdir(slug, "frames.json"))
    if f is None:
        raise SystemExit(f"{slug}: no course_data/mapper/{slug}/frames.json (run render_inputs.py first)")
    return f["holes"]


def frame_of(fj, ppy=1.0, **kw):
    f = fj["frame"]
    return corridor_frame(f["tee_ll"], f["aim_ll"], ppy, **kw)


def xy_to_ll(fj, xy):
    """[(x, along)] yds in the hole's corridor frame -> [[lon, lat]]."""
    fr = frame_of(fj)
    xy = np.asarray(xy, float).reshape(-1, 2)
    return fr.yds_to_ll(np.c_[xy[:, 0], -xy[:, 1]])


def ll_to_xy(fj, ll):
    fr = frame_of(fj)
    p = fr.ll_to_yds(np.asarray(ll, float).reshape(-1, 2)[:, :2])
    return np.c_[p[:, 0], -p[:, 1]]


def ring_ll(poly):
    """A package zone polygon (zones_ll 'poly': [[lon, lat], ...] or a {type, coordinates} geometry) -> [[lon, lat]]."""
    if isinstance(poly, dict):
        c = poly.get("coordinates") or []
        if poly.get("type") == "Polygon":
            return c[0] if c else []
        if poly.get("type") == "MultiPolygon":
            return c[0][0] if c and c[0] else []
        return []
    return poly or []


def auto_zones_xy(fj, h, lies=None):
    """The package hole's zones_ll as [{lie, xy, src, i}] in the corridor frame (only those near the window)."""
    out = []
    for i, z in enumerate(h.get("zones_ll") or []):
        lie = z.get("lie")
        if lies and lie not in lies:
            continue
        r = ring_ll(z.get("poly"))
        if len(r) < 3:
            continue
        xy = ll_to_xy(fj, r)
        if (xy[:, 1].max() < WIN["a0"] - 60 or xy[:, 1].min() > WIN["a1"] + 60 or
                xy[:, 0].max() < -WIN["lat"] - 60 or xy[:, 0].min() > WIN["lat"] + 60):
            continue
        out.append(dict(lie=lie, xy=xy.tolist(), src=z.get("src"), i=i))
    return out


# ----------------------------------------------------------------------------- shapes (edits.json)
def _poly(xy):
    from shapely.geometry import Polygon
    g = Polygon([(float(x), float(a)) for x, a in xy])
    return g if g.is_valid else g.buffer(0)


def window(pad=0.0):
    from shapely.geometry import box
    return box(-WIN["lat"] - pad, WIN["a0"] - pad, WIN["lat"] + pad, WIN["a1"] + pad)


def shape_geom(shape, fj=None, h=None):
    """An edit's shape (yard frame) -> shapely geometry in (x, along). Shapes:
      {"poly": [[x, along], ...]}
      {"rect": [x0, x1, a0, a1]}
      {"ell": [cx, ca, rx, ra]}                        one crown / pond (half-widths rx lateral, ra along)
      {"band": {"left": [[along, x], ...], "right": [[along, x], ...]}}   between two edges (e.g. a strip of trees)
      {"side": {"side": "L"|"R", "from": x_inner, "to": x_outer, "a0": .., "a1": ..}}   a lateral strip
      {"beyond_fairway": {"w": 10, "side": "L"|"R"|"both", "a0": 120, "a1": 400, "x0": -70, "x1": 70}}
            the box minus every fairway / first-cut zone of the BASE package's hole grown by w yds
            (long grass beyond the mown rough; needs fj + h)."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    if not isinstance(shape, dict) or len(shape) != 1:
        raise ValueError(f"shape must be one of poly / rect / ell / band / side / beyond_fairway: {shape!r}")
    (kind, v), = shape.items()
    if kind == "poly":
        if len(v) < 3:
            raise ValueError("poly needs >= 3 points")
        return _poly(v)
    if kind == "rect":
        x0, x1, a0, a1 = map(float, v)
        return box(min(x0, x1), min(a0, a1), max(x0, x1), max(a0, a1))
    if kind == "ell":
        cx, ca, rx, ra = map(float, v)
        t = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        return _poly(np.c_[cx + rx * np.cos(t), ca + ra * np.sin(t)])
    if kind == "band":
        L_ = sorted((float(a), float(x)) for a, x in v["left"])
        R_ = sorted(((float(a), float(x)) for a, x in v["right"]), reverse=True)
        return _poly([(x, a) for a, x in L_] + [(x, a) for a, x in R_])
    if kind == "side":
        s = v.get("side", "L").upper()
        x_in, x_out = abs(float(v["from"])), abs(float(v["to"]))
        a0, a1 = float(v.get("a0", WIN["a0"])), float(v.get("a1", WIN["a1"]))
        x0, x1 = (-x_out, -x_in) if s == "L" else (x_in, x_out)
        return box(x0, a0, x1, a1)
    if kind == "beyond_fairway":
        if fj is None or h is None:
            raise ValueError("beyond_fairway needs the hole's frame and base package")
        w = float(v.get("w", 10.0))
        s = str(v.get("side", "both")).upper()
        x0, x1 = float(v.get("x0", -WIN["lat"])), float(v.get("x1", WIN["lat"]))
        if s == "L":
            x1 = min(x1, 0.0)
        elif s == "R":
            x0 = max(x0, 0.0)
        g = box(x0, float(v.get("a0", WIN["a0"])), x1, float(v.get("a1", WIN["a1"])))
        fw = [_poly(z["xy"]) for z in auto_zones_xy(fj, h, ("fairway", "first_cut", "green"))]
        if fw:
            g = g.difference(unary_union(fw).buffer(w))
        return g
    raise ValueError(f"unknown shape {kind!r}")


def polys_of(g, min_area=4.0):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g] if g.area >= min_area else []
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon" and p.area >= min_area]


def yd_between(a_ll, b_ll):
    lat0 = math.radians((a_ll[1] + b_ll[1]) / 2)
    dx = (a_ll[0] - b_ll[0]) * 111320.0 * math.cos(lat0)
    dy = (a_ll[1] - b_ll[1]) * 110574.0
    return math.hypot(dx, dy) / YD
