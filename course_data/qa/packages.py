"""QA adapter: find every auto-built course package and normalise it for the tests.

A "package" is whatever the data platform hands the product (ARCHITECTURE.md): a `package.json`
(platform/, newest contract) or, until that lands everywhere, the S6 `holes.json` (course_model/1).
Both are reduced to one shape so test_contracts.py / golden_spirit_hollow.py / review.py can check
any course without knowing which stage built it:

  Pkg(slug, path, kind, raw, course, holes={ref: QHole})
  QHole(ref, par, card, tee_ll, green_ll, aim_ll, bearing, zones_ll=[(lie, [[lon, lat], ...])],
        provenance, model=<tee_strategy hole dict in a pixel frame>, frame=<render.Frame>, raw)

Nothing here edits another team's files.
"""
import glob
import json
import math
import os
import sys

import numpy as np

QA = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(QA)
ROOT = os.path.dirname(CD)
for p in (CD, os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")):
    if p not in sys.path:
        sys.path.insert(0, p)

KNOWN_LIES = {"fairway", "first_cut", "rough", "sand", "recovery", "native", "water", "ob", "green"}
PENAL = {"sand", "recovery", "native", "water", "ob"}
YD = 0.9144


def _render():
    import render                                            # course_data/imagery/render.py
    return render


class QHole:
    def __init__(self, ref, raw):
        self.ref = str(ref)
        self.raw = raw
        self.par = None
        self.card = None            # scorecard yards for the tee set (None if unknown)
        self.length = None          # what the package says the hole plays
        self.tee_ll = self.green_ll = self.aim_ll = None
        self.bearing = None         # deg clockwise from north, tee -> aim
        self.zones_ll = []
        self.green_poly_ll = None
        self.hole_line_ll = None
        self.provenance = None
        self.model = None           # tee_strategy-ready dict (tee, dot270, green, zones in px)
        self.frame = None

    def __repr__(self):
        return f"QHole({self.ref}, par {self.par}, {self.length} yds)"


class Pkg:
    def __init__(self, slug, path, kind, raw):
        self.slug, self.path, self.kind, self.raw = slug, path, kind, raw
        self.course = {}
        self.holes = {}
        self.dir = os.path.dirname(path)
        self.errors = []            # adapter-level problems (become test failures)

    @property
    def id(self):
        return f"{self.slug}:{self.kind}"

    def __repr__(self):
        return f"Pkg({self.id}, {len(self.holes)} holes)"


# ----------------------------------------------------------------------------- geometry helpers
def bearing_deg(a_ll, b_ll):
    lat0 = math.radians(a_ll[1])
    de = (b_ll[0] - a_ll[0]) * math.cos(lat0)
    dn = b_ll[1] - a_ll[1]
    return (math.degrees(math.atan2(de, dn)) + 360) % 360


def dist_yd(a_ll, b_ll):
    lat0 = math.radians((a_ll[1] + b_ll[1]) / 2)
    de = (b_ll[0] - a_ll[0]) * math.cos(lat0) * 111320
    dn = (b_ll[1] - a_ll[1]) * 111320
    return math.hypot(de, dn) / YD


def path_yd(lls):
    return sum(dist_yd(a, b) for a, b in zip(lls[:-1], lls[1:]))


def _ll(p):
    """[lon, lat] from a list/tuple/dict; tolerate {lat, lon}."""
    if p is None:
        return None
    if isinstance(p, dict):
        if "lon" in p and "lat" in p:
            return [float(p["lon"]), float(p["lat"])]
        if "ll" in p:
            return _ll(p["ll"])
        if "coordinates" in p:
            return _ll(p["coordinates"])
        return None
    p = list(p)
    if len(p) >= 2 and abs(p[0]) <= 180 and abs(p[1]) <= 90:
        return [float(p[0]), float(p[1])]
    return None


# ----------------------------------------------------------------------------- holes.json (course_model/1)
def _from_course_model(path, raw):
    R = _render()
    slug = raw.get("slug") or os.path.basename(os.path.dirname(path))
    pkg = Pkg(slug, path, "holes.json", raw)
    pkg.course = raw.get("course", {})
    lengths = raw.get("lengths") or {}
    for ref, h in raw.get("holes", {}).items():
        q = QHole(ref, h)
        q.par = h.get("par")
        q.length = h.get("length")
        q.card = lengths.get(str(ref))
        q.tee_ll, q.aim_ll, q.green_ll = _ll(h.get("tee_ll")), _ll(h.get("aim_ll")), _ll(h.get("green_ll"))
        q.provenance = h.get("provenance")
        if q.tee_ll and q.aim_ll:
            q.bearing = bearing_deg(q.tee_ll, q.aim_ll)
            try:
                q.frame = R.Frame(q.tee_ll, q.aim_ll, ppy=h["px_per_yd"], tee_px=h["tee"], proj="utm")
                q.zones_ll = [(n, q.frame.px_to_ll(np.array(poly, float)).tolist()) for n, poly in h["zones"]]
                if h.get("green_polygon"):
                    q.green_poly_ll = q.frame.px_to_ll(np.array(h["green_polygon"], float)).tolist()
                if h.get("hole_line"):
                    q.hole_line_ll = q.frame.px_to_ll(np.array(h["hole_line"], float)).tolist()
            except Exception as e:                                 # noqa: BLE001
                pkg.errors.append(f"hole {ref}: frame rebuild failed: {type(e).__name__}: {e}")
        q.model = as_model_hole(h)
        pkg.holes[str(ref)] = q
    return pkg


def as_model_hole(h):
    d = dict(h)
    d["tee"], d["dot270"], d["green"] = tuple(h["tee"]), tuple(h["dot270"]), tuple(h["green"])
    d["zones"] = [(n, [tuple(p) for p in poly]) for n, poly in h["zones"]]
    d.setdefault("aim_min", -60)
    d.setdefault("aim_max", 60)
    return d


# ----------------------------------------------------------------------------- package.json (platform)
def _zones_generic(zs):
    """[(lie, [[lon,lat],...])] from the shapes a platform might use: [[lie, poly]], [{lie, poly|coords|
    geometry}], or a GeoJSON FeatureCollection with a lie/class property."""
    out = []
    if isinstance(zs, dict) and zs.get("type") == "FeatureCollection":
        zs = zs["features"]
    if isinstance(zs, dict):                                   # {lie: [poly, ...]}
        for lie, polys in zs.items():
            for poly in polys:
                out.append((lie, poly))
        return out
    for z in zs or []:
        if isinstance(z, (list, tuple)) and len(z) == 2 and isinstance(z[0], str):
            out.append((z[0], z[1]))
        elif isinstance(z, dict):
            props = z.get("properties", z)
            lie = props.get("lie") or props.get("class") or props.get("kind") or props.get("name") or z.get("lie")
            geom = z.get("geometry") or z.get("poly") or z.get("polygon") or z.get("coords") or z.get("ll")
            if isinstance(geom, dict) and "coordinates" in geom:
                if geom["type"] == "Polygon":
                    for i, ring in enumerate(geom["coordinates"][:1]):
                        out.append((lie, ring))
                elif geom["type"] == "MultiPolygon":
                    for p in geom["coordinates"]:
                        out.append((lie, p[0]))
            elif geom is not None:
                out.append((lie, geom))
    return out


def _from_package(path, raw):
    """Platform package.json. The contract is in ARCHITECTURE.md; this reader is deliberately lenient
    about *where* fields sit so the tests report missing/invalid fields instead of crashing."""
    R = _render()
    slug = raw.get("slug") or (raw.get("course") or {}).get("slug") or os.path.basename(os.path.dirname(path))
    pkg = Pkg(slug, path, "package.json", raw)
    pkg.course = raw.get("course", {})
    holes = raw.get("holes", {})
    if isinstance(holes, list):
        holes = {str(h.get("ref") or h.get("hole") or h.get("number") or i + 1): h for i, h in enumerate(holes)}
    for ref, h in holes.items():
        q = QHole(ref, h)
        q.par = h.get("par")
        tee = h.get("tee")
        q.tee_ll = _ll(h.get("tee_ll")) or _ll(tee if not isinstance(tee, dict) else tee)
        g = h.get("green")
        q.green_ll = _ll(h.get("green_ll")) or _ll(g.get("center") if isinstance(g, dict) and "center" in g else g)
        if isinstance(g, dict) and g.get("polygon"):
            q.green_poly_ll = g["polygon"]
        elif h.get("green_polygon"):
            q.green_poly_ll = h["green_polygon"]
        q.aim_ll = _ll(h.get("aim_ll"))
        q.bearing = h.get("bearing", h.get("bearing_deg"))
        q.card = h.get("card_yards", h.get("yards", h.get("length")))
        q.length = h.get("length", h.get("yards", q.card))
        if isinstance(q.card, dict):
            q.card = q.card.get("yards")
        q.provenance = h.get("provenance")
        q.hole_line_ll = h.get("hole_line_ll") or h.get("hole_line")
        if q.hole_line_ll and not _ll(q.hole_line_ll[0]):
            q.hole_line_ll = None
        q.zones_ll = [(lie, poly) for lie, poly in _zones_generic(h.get("zones", []))
                      if poly and _ll(poly[0])]
        if q.tee_ll and q.aim_ll is None and q.bearing is not None:
            th = math.radians(float(q.bearing))
            q.aim_ll = [q.tee_ll[0] + math.sin(th) * 0.002 / math.cos(math.radians(q.tee_ll[1])),
                        q.tee_ll[1] + math.cos(th) * 0.002]
        if q.tee_ll and q.aim_ll is None and q.green_ll:
            q.aim_ll = q.green_ll
        if q.bearing is None and q.tee_ll and q.aim_ll:
            q.bearing = bearing_deg(q.tee_ll, q.aim_ll)
        if q.tee_ll and q.aim_ll and q.green_ll:
            try:
                q.frame = R.Frame(q.tee_ll, q.aim_ll, ppy=3.4, tee_px=(460, 1900), proj="utm")
                q.model = dict(par=q.par, length=q.length, tee=(460.0, 1900.0), dot270=(460.0, 1900 - 270 * 3.4),
                               tee_ll=q.tee_ll, aim_ll=q.aim_ll, px_per_yd=3.4, provenance=q.provenance,
                               green=tuple(q.frame.ll_to_px([q.green_ll])[0]),
                               zones=[(lie, [tuple(p) for p in q.frame.ll_to_px(np.array(poly, float)[:, :2])])
                                      for lie, poly in q.zones_ll], aim_min=-60, aim_max=60)
            except Exception as e:                                 # noqa: BLE001
                pkg.errors.append(f"hole {ref}: frame failed: {type(e).__name__}: {e}")
        pkg.holes[str(ref)] = q
    return pkg


# ----------------------------------------------------------------------------- discovery
def find_packages(include_holes_json=True):
    """Every package on disk. package.json first; a course dir's holes.json too (it is S6's output and
    what the book reads today). Skips QA's own folder and backups."""
    seen = []
    for p in sorted(glob.glob(os.path.join(CD, "**", "package.json"), recursive=True)):
        if "/qa/" in p or "node_modules" in p:
            continue
        try:
            raw = json.load(open(p))
        except Exception as e:                                     # noqa: BLE001
            pk = Pkg(os.path.basename(os.path.dirname(p)), p, "package.json", {})
            pk.errors.append(f"unreadable JSON: {e}")
            seen.append(pk)
            continue
        if "holes" not in raw:
            continue
        seen.append(_from_package(p, raw))
    if include_holes_json:
        for p in sorted(glob.glob(os.path.join(CD, "**", "holes.json"), recursive=True)):
            if "/qa/" in p:
                continue
            try:
                raw = json.load(open(p))
            except Exception:                                      # noqa: BLE001
                continue
            if raw.get("schema") == "course_model/1":
                seen.append(_from_course_model(p, raw))
    return seen


def course_boundary(pkg):
    """shapely geometry of the leisure=golf_course polygon (from the package or the course's osm.geojson)."""
    from shapely.geometry import shape
    from shapely.ops import unary_union
    b = (pkg.raw.get("course") or {}).get("boundary") or pkg.raw.get("boundary")
    if isinstance(b, dict) and "type" in b:
        try:
            return shape(b.get("geometry", b))
        except Exception:                                          # noqa: BLE001
            pass
    for d in (pkg.dir, os.path.join(CD, pkg.slug), os.path.dirname(pkg.dir)):
        f = os.path.join(d, "osm.geojson")
        if os.path.exists(f):
            fc = json.load(open(f))
            gs = [shape(ft["geometry"]) for ft in fc["features"]
                  if ft["properties"].get("leisure") == "golf_course" and ft.get("geometry")
                  and ft["geometry"]["type"] in ("Polygon", "MultiPolygon")]
            if gs:
                return unary_union(gs)
    return None


def lie_at_ll(q, ll):
    """The lie the package gives a WGS84 point (later zones win; default rough)."""
    from matplotlib.path import Path
    lie = "rough"
    for name, poly in q.zones_ll:
        if len(poly) >= 3 and Path(np.array(poly, float)[:, :2]).contains_point(ll[:2]):
            lie = name
    return lie


if __name__ == "__main__":
    for pk in find_packages():
        print(pk, pk.path, pk.errors[:3])
        for q in list(pk.holes.values())[:2]:
            print("  ", q, q.bearing, len(q.zones_ll))
