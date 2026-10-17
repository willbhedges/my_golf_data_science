"""Out-of-bounds inference for any course (research plan B4): OB polygons in WGS84 with confidence and provenance.

    from infer import apply_ob
    pkg2 = apply_ob(package)                 # new dict; zones_ll gain {"lie": "ob", "src": "ob:<evidence>", "p": ..}

    python3 course_data/ob/infer.py --package course_data/packages/<slug>/package.json [--out ...] [--geojson ...]

Evidence (course_data/ob/<slug>/raw/, fetched on Actions by fetch.py; all optional):
  course   the OSM leisure=golf_course outline, every ring (package["course"]["boundary"] or raw/osm.geojson)
  houses   buildings (OSM building=* and Microsoft ML footprints, deduplicated) that are not golf buildings
           (a building inside the course outline counts only if it sits in a residential landuse / private parcel)
  parcels  county/state parcels (Iowa statewide 2017): a non-course parcel holding a house = a private lot
  roads    public highways (motorway .. residential, not service/track/path) and railways
  landuse  landuse=residential/commercial/industrial/retail
  tags     golf=out_of_bounds polygons (rare)

Rule (the white stakes run along property lines, a few yards to tens of yards in front of the houses):
  ob = tags  U  lots  U  roads  U  residential  U  outside
    lots        parcels: the private lot polygons grown by parcel_off yds; no parcels: every house buffered by
                house_d yds, then closed by house_close yds so a row of houses gives one continuous line
    roads       centre line buffered by the class half-width + road_margin yds
    residential landuse polygons grown by res_off yds (None = not used)
    outside     everything outside the course outline grown by out_off yds (None = not used), restricted to
                within out_dev yds of a house or road when out_dev is set ("developed" outside)
  per hole: clipped to line_of_play (tee -> hole line -> green) buffered by CORRIDOR yds, minus the hole's
  fairway / green / water / sand / tee polygons (OB never overrides them), simplified 1.5 yds, pieces >= 100 yd2.
Parameters are calibrated on the hand-checked Spirit Hollow OB (evaluate.py, leave-one-hole-out); the fitted
values live in params.json next to this file, DEFAULTS below are used when it is missing.

Each zone: {"lie": "ob", "poly": [[lon, lat], ...], "src": "ob:<evidence>", "p": confidence, "evidence": [...]},
where evidence is the first matching of tag > parcel > road > house > residential > outside and p is that
evidence's precision on Spirit Hollow (P_DEFAULT when not calibrated).
"""
import argparse
import copy
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
YD = 0.9144
MODEL_ID = "ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB)"
CORRIDOR = 60.0
MIN_AREA = 100.0
SIMPLIFY = 1.5
DEFAULTS = dict(house_d=20.0, house_close=20.0, parcel_off=0.0, parcel_mode="houses", road_margin=5.0,
                road_inside=False, res_off=None, out_off=None, out_dev=None)
P_DEFAULT = dict(tag=0.95, parcel=0.8, road=0.75, house=0.6, residential=0.5, outside=0.4)
ORDER = ["tag", "parcel", "road", "house", "residential", "outside"]
ROAD_HALF = dict(motorway=14, trunk=12, primary=10, secondary=8, tertiary=7, unclassified=5, residential=5,
                 living_street=4, motorway_link=6, trunk_link=6, primary_link=6, secondary_link=5, tertiary_link=5)
RAIL_HALF = 5.0
DEV_LANDUSE = ("residential", "commercial", "industrial", "retail")
PROTECT = ("fairway", "green", "water", "sand", "tee")


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def load_module(path, name):
    """Import a module by path under a unique name (platform/ and product/ both have a package.py)."""
    import importlib.util
    if name in sys.modules:
        return sys.modules[name]
    d = os.path.dirname(path)
    if d not in sys.path:
        sys.path.append(d)                       # its sibling imports (platform_common, ...), after ours
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def platform_reframe():
    return load_module(os.path.join(CD, "platform", "package.py"), "ob_platform_package").reframe


def load_params(path=os.path.join(HERE, "params.json")):
    """-> (params incl. 'mode', precision per evidence) from params.json (evaluate.py calibrate) or DEFAULTS."""
    p = dict(DEFAULTS, mode="replace")
    pr = dict(P_DEFAULT)
    if os.path.exists(path):
        j = json.load(open(path))
        p.update(j.get("params") or {})
        p["mode"] = j.get("mode", p["mode"])
        pr.update({k: v for k, v in (j.get("precision") or {}).items() if v is not None})
    return p, pr


# ----------------------------------------------------------------------------- projection
class Proj:
    """lon/lat <-> UTM yards (the same metric as the package's yard frame)."""

    def __init__(self, lon0, lat0):
        from pyproj import Transformer
        epsg = (32600 if lat0 >= 0 else 32700) + int((lon0 + 180) // 6) + 1
        self.fw = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
        self.bw = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)

    def xy(self, ll):
        ll = np.atleast_2d(np.asarray(ll, float))
        x, y = self.fw.transform(ll[:, 0], ll[:, 1])
        return np.c_[x, y] / YD

    def ll(self, xy):
        xy = np.atleast_2d(np.asarray(xy, float)) * YD
        lon, lat = self.bw.transform(xy[:, 0], xy[:, 1])
        return np.c_[lon, lat]

    def to_m(self, g):
        import shapely
        return shapely.transform(g, lambda a: self.xy(a))

    def to_ll(self, g):
        import shapely
        return shapely.transform(g, lambda a: self.ll(a))


def _valid(g):
    return g if g.is_valid else g.buffer(0)


def _polys(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [x for x in getattr(g, "geoms", []) if x.geom_type == "Polygon" and not x.is_empty] + \
        [y for x in getattr(g, "geoms", []) if x.geom_type in ("MultiPolygon", "GeometryCollection") for y in _polys(x)]


# ----------------------------------------------------------------------------- layers
def layers_dir(slug):
    return os.path.join(HERE, slug, "raw")


def load_layers(package=None, slug=None, raw_dir=None):
    """-> dict of WGS84 shapely geometries: course (MultiPolygon|None), buildings [..], parcels [..],
    roads [(LineString, half_yd)], landuse [..], tags [..], plus `have` (which sources exist)."""
    from shapely.geometry import MultiPolygon, Polygon, shape
    slug = slug or ((package or {}).get("course") or {}).get("slug") or (package or {}).get("slug")
    raw_dir = raw_dir or layers_dir(slug)
    L = dict(course=None, buildings=[], parcels=[], roads=[], landuse=[], tags=[], have=[])

    def read(name):
        p = os.path.join(raw_dir, name)
        return json.load(open(p)) if os.path.exists(p) else None

    bnd = ((package or {}).get("course") or {}).get("boundary")
    if bnd and bnd.get("coordinates"):
        polys = [bnd["coordinates"]] if bnd["type"] == "Polygon" else bnd["coordinates"]
        L["course"] = _valid(MultiPolygon([Polygon(p[0], p[1:]) for p in polys]))
    osm = read("osm.geojson")
    if osm is None and slug:                                   # fall back to the package's own OSM fetch
        p = os.path.join(CD, "packages", slug, "raw", "osm.geojson")
        osm = json.load(open(p)) if os.path.exists(p) else None
    if osm:
        L["have"].append("osm")
        cr = []
        for f in osm["features"]:
            p, g = f["properties"], f.get("geometry")
            if not g:
                continue
            try:
                s = shape(g)
            except Exception:                                  # noqa: BLE001
                continue
            area = s.geom_type in ("Polygon", "MultiPolygon")
            if p.get("leisure") == "golf_course" and area:
                cr.append(_valid(s))
            elif p.get("golf") == "out_of_bounds" and area:
                L["tags"].append(_valid(s))
            elif p.get("building") and area:
                L["buildings"].append(_valid(s))
            elif p.get("landuse") in DEV_LANDUSE and area:
                L["landuse"].append(_valid(s))
            elif p.get("highway") in ROAD_HALF and not area:
                L["roads"].append((s, float(ROAD_HALF[p["highway"]])))
            elif p.get("railway") in ("rail", "light_rail") and not area:
                L["roads"].append((s, RAIL_HALF))
        if L["course"] is None and cr:
            from shapely.ops import unary_union
            L["course"] = unary_union(cr)
    ms = read("ms_buildings.geojson")
    if ms:
        L["have"].append("ms_buildings")
        from shapely.strtree import STRtree
        osm_b = L["buildings"]
        tree = STRtree(osm_b) if osm_b else None
        for f in ms["features"]:
            s = _valid(shape(f["geometry"]))
            if tree is not None and len(tree.query(s, predicate="intersects")):
                continue                                       # already in OSM
            L["buildings"].append(s)
    par = read("parcels.geojson")
    if par and par.get("features"):
        L["have"].append("parcels")
        for f in par["features"]:
            if f.get("geometry"):
                try:
                    L["parcels"].append(_valid(shape(f["geometry"])))
                except Exception:                              # noqa: BLE001
                    pass
    return L


# ----------------------------------------------------------------------------- course-level OB regions
class Regions:
    """Projected layers + per-component OB regions (metric yards), cached per parameter value."""

    def __init__(self, L, proj=None):
        from shapely.ops import unary_union
        from shapely.strtree import STRtree
        self.L = L
        allg = ([L["course"]] if L["course"] is not None else []) + L["buildings"][:1] + [r for r, _ in L["roads"][:1]]
        c = allg[0].centroid if allg else None
        self.P = proj or Proj(c.x, c.y)
        P = self.P
        self.course = P.to_m(L["course"]) if L["course"] is not None else None
        self.res = unary_union([P.to_m(g) for g in L["landuse"]]) if L["landuse"] else None
        self.tags = unary_union([P.to_m(g) for g in L["tags"]]) if L["tags"] else None
        self.roads = [(P.to_m(g), h) for g, h in L["roads"]]
        parcels = [P.to_m(g) for g in L["parcels"]]
        blds = [P.to_m(g) for g in L["buildings"]]
        # course parcels: mostly inside the outline (or the outline mostly inside them: the course's own parcel)
        priv = []
        for g in parcels:
            if g.area <= 0:
                continue
            ov = g.intersection(self.course).area if self.course is not None else 0.0
            if ov > 0.5 * g.area or (ov > 0.3 * self.course.area if self.course is not None else False):
                continue
            priv.append(g)
        self.private = priv
        ptree = STRtree(priv) if priv else None
        houses = []
        for b in blds:
            if b.area < 25:                                    # < ~20 m2: sheds, noise
                continue
            pt = b.representative_point()
            inside = self.course is not None and self.course.contains(pt)
            in_priv = ptree is not None and len(ptree.query(pt, predicate="within"))
            in_res = self.res is not None and self.res.contains(pt)
            if inside and not (in_priv or in_res):
                continue                                       # clubhouse, maintenance shed, shelter
            houses.append(b)
        self.houses = houses
        self.house_union = unary_union(houses) if houses else None
        lots = []
        if ptree is not None and houses:
            pts = [h.representative_point() for h in houses]
            for i, g in enumerate(priv):
                if any(g.contains(p) for p in pts if g.bounds[0] <= p.x <= g.bounds[2] and g.bounds[1] <= p.y <= g.bounds[3]):
                    lots.append(g)
        self.lots = unary_union(lots) if lots else None
        self.house_free = unary_union([h for h in houses if self.lots is None or not self.lots.contains(h.representative_point())]) \
            if houses else None
        self.priv_all = unary_union(priv) if priv else None
        self._cache = {}

    def _c(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    def road(self, margin, inside=True):
        """Public roads buffered by half-width + margin; inside=False drops the parts inside the course outline
        (entrance drives and park roads through a course are rarely OB)."""
        from shapely.ops import unary_union
        if not self.roads:
            return None
        g = self._c(("road", margin), lambda: unary_union([g.buffer(h + margin, cap_style=2) for g, h in self.roads]))
        if inside or self.course is None:
            return g
        return self._c(("road_out", margin), lambda: g.difference(self.course))

    def house(self, d, close, unlotted=False):
        g = self.house_free if unlotted else self.house_union
        if g is None or g.is_empty:
            return None
        return self._c(("house", d, close, unlotted), lambda: g.buffer(d + close).buffer(-close) if close else g.buffer(d))

    def parcel(self, off, mode):
        g = self.lots if mode == "houses" else self.priv_all
        if g is None:
            return None
        return self._c(("parcel", off, mode), lambda: g.buffer(off) if off else g)

    def residential(self, off):
        if off is None or self.res is None:
            return None
        return self._c(("res", off), lambda: self.res.buffer(off) if off else self.res)

    def outside(self, off, dev, dev_road_margin=5.0):
        if off is None or self.course is None:
            return None

        def mk():
            from shapely.geometry import box
            x0, y0, x1, y1 = self.course.bounds
            big = box(x0 - 2000, y0 - 2000, x1 + 2000, y1 + 2000)
            o = big.difference(self.course.buffer(off) if off else self.course)
            if dev is not None:
                parts = [g for g in (self.house_union, self.road(dev_road_margin)) if g is not None]
                if not parts:
                    return None
                from shapely.ops import unary_union
                o = o.intersection(unary_union(parts).buffer(dev))
            return o
        return self._c(("out", off, dev), mk)

    def components(self, prm):
        """-> [(evidence, region)] in ORDER for the parameter dict prm (None regions dropped)."""
        out = [("tag", self.tags),
               ("parcel", self.parcel(prm.get("parcel_off") or 0.0, prm.get("parcel_mode", "houses"))
                if prm.get("parcel_off") is not None else None),
               ("road", self.road(prm["road_margin"], prm.get("road_inside", True))
                if prm.get("road_margin") is not None else None),
               ("house", self.house(prm["house_d"], prm.get("house_close") or 0.0,
                                    unlotted=self.lots is not None and prm.get("parcel_off") is not None)
                if prm.get("house_d") is not None else None),
               ("residential", self.residential(prm.get("res_off"))),
               ("outside", self.outside(prm.get("out_off"), prm.get("out_dev")))]
        return [(k, g) for k, g in out if g is not None and not g.is_empty]


# ----------------------------------------------------------------------------- per hole
def line_of_play_ll(h, tee_set=None):
    t = (h.get("tees") or {}).get(tee_set) if tee_set else None
    tee = (t or {}).get("tee_ll") or h.get("tee_ll")
    pts = ([tee] if tee else []) + list(h.get("hole_line_ll") or []) + ([h["green_ll"]] if h.get("green_ll") else [])
    return [p for p in pts if p]


def corridor_m(h, P, width=CORRIDOR):
    from shapely.geometry import LineString, Point
    from shapely.ops import unary_union
    lines = []
    tees = [t.get("tee_ll") for t in (h.get("tees") or {}).values() if t.get("tee_ll")] or [h.get("tee_ll")]
    rest = list(h.get("hole_line_ll") or []) + ([h["green_ll"]] if h.get("green_ll") else [])
    for t in tees:
        pts = [p for p in [t] + rest if p]
        if len(pts) >= 2:
            lines.append(LineString(P.xy(pts)))
        elif pts:
            lines.append(Point(P.xy(pts)[0]))
    return unary_union([g.buffer(width) for g in lines]) if lines else None


def protect_m(h, P):
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    gs = []
    for z in h.get("zones_ll") or []:
        if z.get("lie") in PROTECT and len(z.get("poly") or []) >= 3:
            gs.append(_valid(Polygon(P.xy(z["poly"]))))
    if h.get("green_polygon_ll") and len(h["green_polygon_ll"]) >= 3:
        gs.append(_valid(Polygon(P.xy(h["green_polygon_ll"]))))
    return unary_union(gs) if gs else None


def hole_ob(h, R, prm, prec, comps=None):
    """-> list of zones_ll dicts (lie 'ob') for one package hole."""
    cor = corridor_m(h, R.P)
    if cor is None:
        return []
    prot = protect_m(h, R.P)
    taken = None
    out = []
    for ev, g in (comps if comps is not None else R.components(prm)):
        piece = g.intersection(cor)
        if prot is not None:
            piece = piece.difference(prot)
        if taken is not None:
            piece = piece.difference(taken)
        if piece.is_empty:
            continue
        taken = piece if taken is None else taken.union(piece)
        for poly in _polys(piece.simplify(SIMPLIFY)):
            if poly.area < MIN_AREA:
                continue
            for q in _holefree(poly):
                if q.area < MIN_AREA:
                    continue
                ring = R.P.ll(np.asarray(q.exterior.coords)[:-1])
                out.append(dict(lie="ob", poly=[[round(float(a), 7), round(float(b), 7)] for a, b in ring],
                                src=f"ob:{ev}", p=round(float(prec.get(ev, P_DEFAULT.get(ev, 0.5))), 3),
                                evidence=ev, area_yd2=round(q.area)))
    return out


def _holefree(p):
    return load_module(os.path.join(CD, "vision_any", "gapfill.py"), "ob_gapfill").holefree(p)


def is_geometry_ob(z):
    """OB zones the geometry stage derived from the same OSM evidence (replaced by apply_ob)."""
    return z.get("lie") in ("ob", "ob_boundary") and not str(z.get("src", "")).startswith("ob:") and \
        str(z.get("src", "osm")).startswith("osm")


def apply_ob(package, layers=None, params=None, precision=None, mode=None, use_reframe=True):
    """course_package/1 dict -> new dict with inferred OB in every hole's zones_ll (+ reframed zones).
    mode: replace = drop the geometry stage's OSM OB (outline/buildings/roads) first; add = keep it too;
    None = the calibrated choice in params.json (default replace)."""
    out = copy.deepcopy(package)
    prm, prec = load_params()
    prm.update(params or {})
    mode = mode or prm.pop("mode", "replace")
    prm.pop("mode", None)
    prec.update(precision or {})
    L = layers if layers is not None else load_layers(out)
    st = out.setdefault("stages", {})
    if not L.get("have") and L.get("course") is None:
        st["ob"] = "missing: no OB layers (commit course_data/requests/ob_<slug>.json: .github/workflows/ob.yml)"
        return out
    R = Regions(L)
    comps = R.components(prm)
    counts = {}
    for ref, h in out["holes"].items():
        zl = list(h.get("zones_ll") or [])
        zl = [z for z in zl if not str(z.get("src", "")).startswith("ob:")]
        if mode == "replace":
            zl = [z for z in zl if not is_geometry_ob(z)]
        add = hole_ob(h, R, prm, prec, comps)
        h["zones_ll"] = zl + add
        for z in add:
            counts[z["evidence"]] = counts.get(z["evidence"], 0) + 1
        if add:
            prov = h.setdefault("provenance", {})
            pz = prov.get("zones") if isinstance(prov.get("zones"), dict) else {}
            pz["ob"] = "ob_infer:" + "+".join(sorted({z["evidence"] for z in add}))
            prov["zones"] = pz
        h["ob_inferred"] = dict(n=len(add), area_yd2=sum(z["area_yd2"] for z in add),
                                evidence=sorted({z["evidence"] for z in add}))
    st["ob"] = (f"ok: {MODEL_ID}; layers {'+'.join(L['have']) or 'course outline only'}; "
                f"{sum(counts.values())} polygons ({', '.join(f'{k} {v}' for k, v in sorted(counts.items()))}); mode {mode}")
    out.setdefault("sources", {})["ob"] = dict(
        model=MODEL_ID, params=prm, precision=prec, layers=L["have"], mode=mode,
        files=f"course_data/ob/{(out.get('course') or {}).get('slug') or out.get('slug')}/raw/",
        calibrated_on="Spirit Hollow hand-checked OB (spirit_hollow/hand_zones_ll.json), leave-one-hole-out",
        attribution=_attribution(L["have"]))
    att = out.setdefault("attribution", [])
    for a in _attribution(L["have"]):
        if a not in att:
            att.append(a)
    if use_reframe:
        try:
            out = platform_reframe()(out)
        except Exception as e:                                 # noqa: BLE001
            log("  ob: reframe failed:", type(e).__name__, str(e)[:200])
    return out


def _attribution(have):
    a = []
    if "osm" in have:
        a.append("(c) OpenStreetMap contributors, ODbL 1.0")
    if "ms_buildings" in have:
        a.append("Microsoft Global ML Building Footprints, ODbL 1.0")
    if "parcels" in have:
        a.append("Parcels: Iowa HSEMD statewide parcels 2017 (county assessors)")
    return a


def to_geojson(package):
    feats = []
    for ref, h in package["holes"].items():
        for z in h.get("zones_ll") or []:
            if str(z.get("src", "")).startswith("ob:"):
                feats.append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[z["poly"] + [z["poly"][0]]]),
                                  properties=dict(hole=ref, lie="ob", src=z["src"], p=z["p"], area_yd2=z.get("area_yd2"))))
    return dict(type="FeatureCollection", features=feats)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--package", required=True)
    ap.add_argument("--out", help="write the package with OB here")
    ap.add_argument("--geojson", help="write the inferred OB polygons here")
    ap.add_argument("--mode", default=None, choices=["replace", "add"])
    a = ap.parse_args(argv)
    pkg = json.load(open(a.package))
    o = apply_ob(pkg, mode=a.mode)
    log(o["stages"].get("ob"))
    if a.out:
        json.dump(o, open(a.out, "w"), indent=1)
    if a.geojson:
        json.dump(to_geojson(o), open(a.geojson, "w"))


if __name__ == "__main__":
    main()
