"""Tracing aids for course_data/truth/<slug>/trace.py: bring raw evidence (OSM polygons, 3DEP lidar canopy) into a
hole's corridor frame so the hand trace can START from it and then be corrected by eye on the renders.

  from assist import osm, canopy, clip
  osm(slug, ref, "fairway")         -> [Z(...)]  the package's OSM polygons of that lie, (x, along) yds, clipped to FOOT
  canopy(slug, ref, thr=2.5)        -> [Z("recovery", ...)]  lidar HAG > thr m (vision_any raw/hag.tif), smoothed
  clip(xy)                          -> polygon clipped to the mapped footprint

Nothing here is a vision / model output: OSM is mapped by people, lidar is a measurement. Every polygon these return
is checked (and moved / cut / dropped) against the photo, CIR, other NAIP years and the lidar render before it stays
in a trace; the trace records which ones were kept as-is.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corridor as C                                         # noqa: E402

_CACHE = {}


def _fj(slug, ref):
    if slug not in _CACHE:
        _CACHE[slug] = C.frames(slug)
    return _CACHE[slug][ref]


def to_xy(slug, ref, ring_ll):
    fr = C.frame_of(_fj(slug, ref), 1.0)
    xy = fr.ll_to_yds(np.asarray(ring_ll, float)[:, :2])
    return np.c_[xy[:, 0], -xy[:, 1]]


def _foot(pad=0.0):
    from shapely.geometry import box
    F = C.FOOT
    return box(-F["lat"] - pad, F["a0"] - pad, F["lat"] + pad, F["a1"] + pad)


def _polys(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def clip(xy, pad=5.0, min_area=20.0):
    from shapely.geometry import Polygon
    g = Polygon(xy).buffer(0).intersection(_foot(pad))
    return [[[round(float(x), 1), round(float(a), 1)] for x, a in np.asarray(p.exterior.coords)[:-1]]
            for p in _polys(g) if p.area >= min_area]


def osm(slug, ref, lie, note=None, min_area=20.0):
    pkg = C.package(slug)
    out = []
    for z in pkg["holes"][ref].get("zones_ll") or []:
        if z.get("lie") != lie or not str(z.get("src", "")).startswith("osm") or "boundary" in str(z.get("src", "")):
            continue
        for p in clip(to_xy(slug, ref, z["poly"]), min_area=min_area):
            out.append(C.Z(lie, p, note or "OSM polygon, checked on the photo"))
    return out


def outside_outline(slug, ref, note=None, min_area=20.0):
    """The footprint beyond the OSM course outline (leisure=golf_course), as OB: use only where the photo shows
    private lots right behind that line (checked per hole)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    b = C.package(slug)["course"].get("boundary")
    if not b:
        return []
    polys = b["coordinates"] if b["type"] == "MultiPolygon" else [b["coordinates"]]
    inside = unary_union([Polygon(to_xy(slug, ref, p[0])).buffer(0) for p in polys])
    out = []
    for g in _polys(_foot(5.0).difference(inside)):
        if g.area >= min_area:
            out.append(C.Z("ob", [[round(float(x), 1), round(float(a), 1)] for x, a in np.asarray(g.exterior.coords)[:-1]],
                           note or "beyond the OSM course outline (private lots behind it)"))
    return out


def house_lots(slug, ref, d=25.0, close=25.0, note=None, min_area=20.0):
    """Private lots as OB: building footprints (course_data/ob/<slug>/raw: Microsoft ML + OSM buildings) grown by
    d yds (a rear yard) and closed by `close` yds so a row of houses gives one line. Used where the photo shows a
    row of houses with yards running to the course and no fence / stake line visible."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    polys = []
    for f in ("ms_buildings.geojson", "osm.geojson"):
        p = os.path.join(C.CD, "ob", slug, "raw", f)
        if not os.path.exists(p):
            continue
        for ft in json.load(open(p))["features"]:
            g = ft["geometry"]
            if f == "osm.geojson" and not (ft.get("properties") or {}).get("building"):
                continue
            if g["type"] == "Polygon":
                polys.append(g["coordinates"][0])
            elif g["type"] == "MultiPolygon":
                polys += [q[0] for q in g["coordinates"]]
    geoms = []
    for p in polys:
        xy = to_xy(slug, ref, p)
        if np.abs(xy[:, 0]).min() < 160 and (xy[:, 1].max() > -100):
            geoms.append(Polygon(xy).buffer(0))
    if not geoms:
        return []
    u = unary_union(geoms).buffer(d + close, join_style=2).buffer(-close, join_style=2).intersection(_foot(5.0))
    return [C.Z("ob", [[round(float(x), 1), round(float(a), 1)] for x, a in np.asarray(g.exterior.coords)[:-1]],
                note or f"private lots: houses + {d:g} yds of yard")
            for g in _polys(u) if g.area >= min_area]


def canopy(slug, ref, thr=2.5, smooth=1.0, min_area=40.0, note=None):
    """Tree crowns: lidar HAG > thr m in the corridor frame (1 px = 1 yd), closed + simplified."""
    import cv2
    S = C.sources(slug)
    if "hag" not in S:
        return []
    fj = _fj(slug, ref)
    F = C.FOOT
    fr = C.corridor_frame(fj["frame"]["tee_ll"], fj["frame"]["aim_ll"], 1.0, a0=F["a0"] - 5, a1=F["a1"] + 5,
                          lat=F["lat"] + 5)
    h = C.hag_m(S, fr)
    m = (np.nan_to_num(h) > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    lat, a1 = F["lat"] + 5, F["a1"] + 5
    for c in cs:
        if cv2.contourArea(c) < min_area:
            continue
        c = cv2.approxPolyDP(c, smooth, True)[:, 0, :].astype(float)
        xy = np.c_[c[:, 0] - lat, a1 - c[:, 1]]                  # px -> (x, along)
        for p in clip(xy, min_area=min_area):
            out.append(C.Z("recovery", p, note or f"lidar canopy > {thr:g} m (2015 leaf-off), checked on the photo"))
    return out
