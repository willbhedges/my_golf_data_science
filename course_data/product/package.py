"""Course package (ARCHITECTURE.md 9.2, schema package/1) -> the strategy model's course module.

The package is frame-free (WGS84 [lon, lat]). Here each hole gets the virtual pixel frame of the book
(ARCHITECTURE.md 2 / 3.7): 920 x 2000 px, tee at (460, 1900), tee line straight up, 3.4 px per yd, UTM
planar projection (the same `render.Frame` the imagery renderer uses), so the zones, the model and the
rendered NAIP image line up exactly.

  load(path, tees)            -> Course: normalised course in that frame (tee holes + par 3s)
  write_module(course, path)  -> a generated course module (same API as spirit_hollow/course.py)
  from_course_model(path)     -> package/1 dict built from a v1 holes.json (stand-in until platform lands)
"""
import datetime as dt
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
for _p in (os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import render as R                                  # noqa: E402  course_data/imagery/render.py

PPY, TEE_PX, PROJ = 3.4, (460.0, 1900.0), "utm"
# ARCHITECTURE 9.1-4: later zones win; sort by this precedence (stable inside a class).
ORDER = ["ob_boundary", "native", "recovery", "ob", "first_cut", "fairway", "green", "water", "sand"]
LIE_MAP = {"ob_boundary": "ob", "green": "fairway", "trees": "recovery", "woods": "recovery",
           "bunker": "sand", "long_grass": "native", "tall_grass": "native"}
MODEL_LIES = {"fairway", "first_cut", "rough", "sand", "recovery", "native", "water", "ob"}
# par-3 edge hazards: model lie -> yardage_book.ADD key, and its severity for "worst on that side"
P3_HAZ = {"water": "water", "ob": "ob", "recovery": "trees", "native": "native", "sand": "bunker",
          "rough": "rough", "fairway": "rough", "first_cut": "rough"}
SEV = {"water": 3, "ob": 3, "trees": 2, "native": 2, "bunker": 1, "rough": 0}


def key_of(ref):
    return int(ref) if str(ref).isdigit() else str(ref)


def image_name(ref):
    return f"hole{int(ref):02d}.jpg" if str(ref).isdigit() else f"hole{ref}.jpg"


def _ll(p):
    if p is None:
        return None
    if isinstance(p, dict):
        if "lon" in p and "lat" in p:
            return [float(p["lon"]), float(p["lat"])]
        for k in ("ll", "coordinates", "center"):
            if k in p:
                return _ll(p[k])
        return None
    p = list(p)
    return [float(p[0]), float(p[1])] if len(p) >= 2 else None


def bearing_deg(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    y = math.sin(lon2 - lon1) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _zones(zs):
    """[(lie, [[lon, lat], ...]), ...] from package zones ([{lie, poly}], [[lie, poly]], {lie: [poly]})."""
    out = []
    if isinstance(zs, dict) and zs.get("type") == "FeatureCollection":
        zs = zs["features"]
    if isinstance(zs, dict):
        return [(lie, poly) for lie, polys in zs.items() for poly in polys]
    for z in zs or []:
        if isinstance(z, (list, tuple)) and len(z) == 2 and isinstance(z[0], str):
            out.append((z[0], z[1]))
        elif isinstance(z, dict):
            pr = z.get("properties", z)
            lie = pr.get("lie") or pr.get("class") or z.get("lie")
            g = z.get("poly") or z.get("polygon") or z.get("geometry") or z.get("coords")
            if isinstance(g, dict) and g.get("type") == "Polygon":
                out.append((lie, g["coordinates"][0]))
            elif isinstance(g, dict) and g.get("type") == "MultiPolygon":
                out += [(lie, p[0]) for p in g["coordinates"]]
            elif g is not None:
                out.append((lie, g))
    return out


class Course:
    """Normalised course for one tee set, in the per-hole virtual pixel frame."""

    def __init__(self):
        self.name = self.slug = self.tee_set = None
        self.center = None            # (lat, lon)
        self.state = None
        self.imagery_dir = None
        self.source = None            # where the package came from
        self.holes, self.par3 = {}, {}
        self.frames = {}              # key -> render.Frame json
        self.bearings, self.exposure, self.confidence = {}, {}, {}
        self.notes, self.labels, self.order = {}, {}, []
        self.flags = {}               # key -> [str] data-quality flags (from the package)
        self.package = None


def _tee_entry(h, tee_set):
    """(tee_ll, aim_ll, length, info) for the tee set; falls back to the hole-level fields."""
    tees = h.get("tees") or {}
    want = (tee_set or "").lower()
    ent = next((v for k, v in tees.items() if k.lower() == want), None)
    if ent is None and tees and want:
        ent = next((v for k, v in tees.items() if want in [a.lower() for a in v.get("aliases", [])]), None)
    yards = h.get("yards") if isinstance(h.get("yards"), dict) else {}
    card = next((v for k, v in yards.items() if k.lower() == want), None)
    if ent:
        tee_ll, aim_ll = _ll(ent.get("tee_ll")), _ll(ent.get("aim_ll"))
        length = ent.get("card_yards") or card or ent.get("measured_yards") or h.get("length")
        return tee_ll, aim_ll, length, ent
    return _ll(h.get("tee_ll")), _ll(h.get("aim_ll")), card or h.get("length"), {}


TEE_LINE = "landing"     # "landing": tee -> the hole line LANDING yds out (book/page line); "package": its aim_ll
LANDING = 250


def _is_ll(p, ref):
    return abs(float(p[0]) - ref[0]) < 0.2 and abs(float(p[1]) - ref[1]) < 0.2


def _zone_meta(zs):
    if isinstance(zs, dict) and zs.get("type") == "FeatureCollection":
        zs = zs["features"]
    if isinstance(zs, dict):
        return [{} for polys in zs.values() for _ in polys]
    out = []
    for z in zs or []:
        if isinstance(z, dict):
            g = z.get("poly") or z.get("polygon") or z.get("geometry") or z.get("coords")
            n = len(g["coordinates"]) if isinstance(g, dict) and g.get("type") == "MultiPolygon" else 1
            out += [z.get("properties", z)] * n
        else:
            out.append({})
    return out


def _aim_along(tee_ll, line_ll, green_ll, length):
    """The point LANDING yds (at most 62% of the hole) along the hole line, measured from the tee's
    projection onto it: the book's tee line then runs over the landing area even when the line's first
    node is a short leg or the line starts at another tee box. None without a usable hole line."""
    if not line_ll or len(line_ll) < 2:
        return None
    lat0 = math.radians(tee_ll[1])
    k = np.array([math.cos(lat0) * 111320 / 0.9144, 111320 / 0.9144])
    P = (np.array([p[:2] for p in line_ll] + [green_ll], float) - tee_ll) * k
    best = None
    for i in range(len(P) - 1):                   # tee's nearest point on the polyline
        a, b = P[i], P[i + 1]
        d = b - a
        u = float(np.clip(-(a @ d) / max(d @ d, 1e-9), 0, 1))
        dist = float(np.linalg.norm(a + u * d))
        if best is None or dist < best[0]:
            best = (dist, i, u)
    if best[0] > 60:
        return None
    _, i, u = best
    want = min(LANDING, 0.62 * length)
    pts = [P[i] + u * (P[i + 1] - P[i])] + list(P[i + 1:])
    run = float(np.linalg.norm(pts[0]))           # tee -> line offset counts toward the distance
    for a, b in zip(pts[:-1], pts[1:]):
        seg = float(np.linalg.norm(b - a))
        if run + seg >= want and seg > 0:
            q = a + (b - a) * (want - run) / seg
            return [tee_ll[0] + q[0] / k[0], tee_ll[1] + q[1] / k[1]]
        run += seg
    return None


def _resolve_set(pkg, tees):
    """Map a requested tee name (or alias) onto the package's tee-set key."""
    sets = pkg.get("tee_sets") or {}
    if not tees:
        return pkg.get("tee_set") or (next(iter(sets)) if sets else None)
    t = tees.lower()
    for k, v in sets.items():
        if k.lower() == t or t in [a.lower() for a in (v or {}).get("aliases", [])]:
            return k
    if sets:
        raise SystemExit(f"tee set {tees!r} is not in this package (sets: {', '.join(sets)})")
    return tees


def load(path, tees=None):
    """package.json (package/1) or a v1 holes.json (course_model/1) -> Course."""
    raw = json.load(open(path))
    if raw.get("schema", "").startswith("course_model"):
        raw = from_course_model(path, raw)
    pkg = raw
    C = Course()
    C.package = pkg
    C.source = os.path.relpath(os.path.abspath(path), ROOT)
    course = pkg.get("course", {})
    C.name = course.get("name") or pkg.get("name") or "Golf course"
    C.slug = course.get("slug") or pkg.get("slug") or os.path.basename(os.path.dirname(os.path.abspath(path)))
    C.state = course.get("state")
    C.tee_set = _resolve_set(pkg, tees)
    img = ((pkg.get("imagery") or {}).get("dir") or ((pkg.get("sources") or {}).get("imagery") or {}).get("dir"))
    cands = [img and (img if os.path.isabs(img) else os.path.join(ROOT, img)), os.path.join(os.path.dirname(os.path.abspath(path)), "imagery"),
             os.path.join(CD, "imagery", C.slug)]
    C.imagery_dir = next((c for c in cands if c and os.path.isdir(c)), None)

    holes = pkg.get("holes", {})
    if isinstance(holes, list):
        holes = {str(h.get("ref") or i + 1): h for i, h in enumerate(holes)}
    lls = []
    for ref, h in holes.items():
        k = key_of(ref)
        tee_ll, aim_ll, length, ent = _tee_entry(h, C.tee_set)
        g = h.get("green")
        green_ll = _ll(h.get("green_ll")) or _ll(g.get("center") if isinstance(g, dict) else g)
        gpoly = (h.get("green_polygon_ll") or h.get("green_polygon")
                 or (g.get("polygon") if isinstance(g, dict) else None))
        if tee_ll is None or green_ll is None:
            C.flags[k] = ["no tee or green position for this tee set: hole skipped"]
            continue
        par = int(h.get("par") or (3 if (length or 0) < 250 else 4))
        lls += [tee_ll, green_ll]
        line_ll = h.get("hole_line_ll")
        if par == 3:
            aim_ll, how = green_ll, "green"
        else:
            own = _aim_along(tee_ll, line_ll, green_ll, float(length or 400)) if TEE_LINE == "landing" else None
            aim_ll, how = (own, "landing") if own else (aim_ll or green_ll, "package")
        fr = R.Frame(tee_ll, aim_ll, ppy=PPY, tee_px=TEE_PX, proj=PROJ)
        C.frames[k] = dict(fr.to_json(), aim=how)
        C.bearings[k] = (bearing_deg(tee_ll, aim_ll) if how != "package" else
                         float(ent.get("bearing_deg") or h.get("bearing_deg") or bearing_deg(tee_ll, aim_ll)))
        e = _elev(ent.get("elevation") or h.get("elevation"))
        if h.get("exposure") is not None:
            C.exposure[k] = float(h["exposure"])
        conf = h.get("confidence") or {}
        C.confidence[k] = conf
        C.flags[k] = list(conf.get("flags") or [])
        zones = []
        raw_z = h.get("zones_ll") if h.get("zones_ll") is not None else h.get("zones")
        for z, (lie, poly) in zip(_zone_meta(raw_z), _zones(raw_z)):
            if not poly or len(poly) < 3 or not _is_ll(poly[0], tee_ll):
                continue                       # yard-frame zones (a package's per-set view) are not WGS84
            boundary = lie == "ob" and str(z.get("src", "")).endswith("course_boundary")
            lie = LIE_MAP.get(lie, lie)
            if lie not in MODEL_LIES:
                continue
            q = fr.ll_to_px(np.array(poly, float)[:, :2])
            zones.append(("ob_boundary" if boundary else lie, [(round(float(x), 1), round(float(y), 1)) for x, y in q]))
        rank = {l: i for i, l in enumerate(ORDER)}
        zones.sort(key=lambda z: rank.get(z[0], 0))
        zones = [(LIE_MAP.get(n, n), p) for n, p in zones]
        green_px = tuple(round(float(v), 1) for v in fr.ll_to_px([green_ll])[0])
        length = int(round(float(length))) if length else int(round(np.hypot(*(np.array(green_px) - TEE_PX)) / PPY))
        image = image_name(ref)
        if par == 3:
            p3 = _par3(fr, green_ll, gpoly, zones, length, k)
            p3["image"] = image
            C.par3[k] = p3
        else:
            C.holes[k] = dict(par=par, image=image, length=length, tee=TEE_PX,
                              dot270=(TEE_PX[0], TEE_PX[1] - 270 * PPY), green=green_px, zones=zones,
                              aim_min=-60, aim_max=60)
            for extra in ("extra_roll", "irons"):
                if h.get(extra) is not None:
                    C.holes[k][extra] = h[extra]
            if e or h.get("elev"):
                C.holes[k]["elev"] = e or h["elev"]
    C.order = sorted(set(C.holes) | set(C.par3), key=lambda k: (str(k).rstrip("BFabf").zfill(3), str(k)))
    c = _ll(course.get("center"))
    C.center = (c[1], c[0]) if c else tuple(np.mean(np.array(lls), 0)[::-1]) if lls else None
    return C


def _elev(e):
    """platform hole.elevation.adjustments -> tee_strategy's hole["elev"] {club: (carry +yd, roll x, kick yd)}."""
    adj = (e or {}).get("adjustments") or {}
    clubs = adj.get("clubs") or {}
    out = {c: (float(v.get("carry_delta_yds", 0.0)), float(v.get("roll_factor", 1.0)),
               float(v.get("lateral_kick_yds", 0.0))) for c, v in clubs.items() if isinstance(v, dict)}
    return out or None


def _par3(fr, green_ll, gpoly, zones, length, k):
    """PAR3 entry (yardage_book format): green outline in (yds right, yds past the flag) and the trouble
    off each edge, sampled from the zones 2-10 yds outside the green."""
    from matplotlib.path import Path
    tee = np.array(TEE_PX)
    flag = fr.ll_to_px([green_ll])[0]
    center = float(np.hypot(*(flag - tee)) / PPY)
    v = (flag - tee) / np.linalg.norm(flag - tee)
    right = np.array([-v[1], v[0]])
    flags = []
    if gpoly and len(gpoly) >= 3:
        gp = fr.ll_to_px(np.array(gpoly, float)[:, :2])
        rel = gp - flag
        green = [(float(r @ right / PPY), float(r @ v / PPY)) for r in rel]
    else:
        green = [(12 * math.cos(a), 12 * math.sin(a)) for a in np.linspace(0, 2 * np.pi, 20, endpoint=False)]
        flags.append("no green polygon: a 24-yd round green is assumed")
    g = np.array(green)

    def lie(pts_yd):
        pts = np.array([flag + (l * right + d * v) * PPY for l, d in pts_yd])
        out = np.array(["rough"] * len(pts), dtype=object)
        for name, poly in zones:
            out[Path(poly).contains_points(pts)] = name
        return out

    l0, l1, d0, d1 = g[:, 0].min(), g[:, 0].max(), g[:, 1].min(), g[:, 1].max()
    samples = {"left": [(l0 - o, d) for o in (3, 6, 9) for d in np.linspace(d0 * 0.6, d1 * 0.6, 5)],
               "right": [(l1 + o, d) for o in (3, 6, 9) for d in np.linspace(d0 * 0.6, d1 * 0.6, 5)],
               "short": [(l, d0 - o) for o in (3, 6, 9) for l in np.linspace(l0 * 0.6, l1 * 0.6, 5)],
               "long": [(l, d1 + o) for o in (3, 6, 9) for l in np.linspace(l0 * 0.6, l1 * 0.6, 5)]}
    haz = {}
    for side, pts in samples.items():
        found = [P3_HAZ.get(x, "rough") for x in lie(pts)]
        haz[side] = max(found, key=lambda h: SEV[h])
    words = {"water": "water", "ob": "OB", "trees": "trees", "native": "long grass", "bunker": "a bunker"}
    bits = [f"{words[h]} {s}" for s, h in haz.items() if h in words]
    short = (", ".join(bits)[:1].upper() + ", ".join(bits)[1:] + ".") if bits else "No mapped trouble near the green."
    worst = max(haz.values(), key=lambda h: SEV[h])
    safe = [s for s, h in haz.items() if SEV[h] == 0]
    note = short + (f" The safe miss is {safe[0]}." if safe and worst != "rough" else "")
    note += " (Edge hazards read from the mapped zones 3-9 yds off the green.)"
    if flags:
        note += " " + "; ".join(flags) + "."
    return dict(tee=TEE_PX, flag=(round(float(flag[0]), 1), round(float(flag[1]), 1)), center=round(center),
                front=round(center + d0), back=round(center + d1), green=[(round(a, 2), round(b, 2)) for a, b in green],
                haz=haz, note=note, short=short, card=length)


# ----------------------------------------------------------------------------- generated module
MODULE = '''"""Course module for {name} ({tee_set} tees). Generated by course_data/product/plan.py from
{source} on {built}. Do not edit by hand; re-run plan.py.

Same API as spirit_hollow/course.py (HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS) in each hole's virtual
pixel frame (920 x 2000, tee (460, 1900), 3.4 px/yd, tee line straight up; FRAMES[k] is the
course_data/imagery/render.Frame that maps it to WGS84), so mozingo/yardage_book.use_course() and
mozingo/tee_strategy take it unchanged.
"""
NAME = {name!r}
TEE_SET = {tee_set!r}
CENTER = {center!r}
HOLES = {holes}
PAR3 = {par3}
NOTES = {notes}
AIM_AT = {aim_at}
ORDER = {order!r}
LABELS = {labels!r}
FRAMES = {frames}
BEARINGS = {bearings!r}
EXPOSURE = {exposure!r}
APP, GREEN_SIDE = {{}}, {{}}
'''


def _fmt(d):
    import pprint
    return pprint.pformat(d, width=110, compact=True, sort_dicts=False)


def write_module(C, path, notes=None, aim_at=None):
    with open(path, "w") as fh:
        fh.write(MODULE.format(name=C.name, tee_set=C.tee_set, source=C.source,
                               built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                               center=tuple(float(x) for x in C.center) if C.center else None,
                               holes=_fmt(C.holes), par3=_fmt(C.par3), notes=_fmt(notes or C.notes),
                               aim_at=_fmt(aim_at or {}), order=C.order, labels=C.labels,
                               frames=_fmt(C.frames), bearings={k: round(v, 2) for k, v in C.bearings.items()},
                               exposure=C.exposure))
    return path


def import_module(path, name="plan_course"):
    import importlib.util
    sys.dont_write_bytecode = True               # keep __pycache__ out of the output folder
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------- stand-in
def from_course_model(path, raw=None):
    """v1 holes.json (course_model/1, per tee set, fitted pixel frame) -> a package/1 dict (WGS84).

    The stand-in used until course_data/platform/ writes package.json: the fitted frame is rebuilt exactly
    (render.Frame(tee_ll, aim_ll, px_per_yd, tee px, 'utm'), as course_data/qa/packages.py does)."""
    raw = raw or json.load(open(path))
    tee_set = raw.get("tee_set")
    holes = {}
    for ref, h in raw["holes"].items():
        fr = R.Frame(h["tee_ll"], h["aim_ll"], ppy=h["px_per_yd"], tee_px=h["tee"], proj="utm")
        zones = [{"lie": n, "poly": fr.px_to_ll(np.array(p, float)).tolist(), "src": "course_model"}
                 for n, p in h["zones"] if len(p) >= 3]
        gp = fr.px_to_ll(np.array(h["green_polygon"], float)).tolist() if h.get("green_polygon") else None
        line = fr.px_to_ll(np.array(h["hole_line"], float)).tolist() if h.get("hole_line") else None
        conf = dict(h.get("auto") or h.get("confidence") or {})
        holes[str(ref)] = dict(ref=str(ref), par=h["par"], tee_ll=h["tee_ll"], aim_ll=h["aim_ll"],
                               green_ll=h.get("green_ll"), green_polygon=gp, green_polygon_ll=gp,
                               length=h["length"], yards={tee_set: h["length"]}, exposure=None, zones_ll=zones,
                               hole_line_ll=line,
                               bearing_deg=bearing_deg(h["tee_ll"], h["aim_ll"]),
                               tees={tee_set: dict(tee_ll=h["tee_ll"], aim_ll=h["aim_ll"], card_yards=h["length"],
                                                   method=h.get("tee_choice"))},
                               zones=zones, provenance=h.get("provenance"), confidence=conf)
    course = dict(raw.get("course") or {})
    c = course.get("center")
    if isinstance(c, dict):
        course["center"] = [c["lon"], c["lat"]]
    course.setdefault("slug", raw.get("slug"))
    return {"schema": "package/1", "course": course, "built": raw.get("built"), "tee_set": tee_set,
            "tee_sets": {tee_set: {"aliases": [tee_set.lower()]}},
            "sources": {"imagery": {"dir": f"course_data/imagery/{raw.get('slug')}"},
                        "standin": os.path.relpath(os.path.abspath(path), ROOT) if os.path.exists(path) else path},
            "stages": raw.get("stages", {}), "holes": holes}


def standin_from_pipeline(course_name, tees, out_path):
    """Build a package/1 stand-in with course_data/pipeline.build_course (offline, no image render)."""
    sys.path.insert(0, CD)
    import pipeline as P
    model = P.build_course(course_name, tees, render=False, quiet=True)
    pkg = from_course_model(f"pipeline.build_course({course_name!r}, {tees!r})", json.loads(json.dumps(model, default=float)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(pkg, fh, separators=(",", ":"))
    return out_path
