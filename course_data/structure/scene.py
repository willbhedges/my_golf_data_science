"""Scene: the solver's only view of a course (what a perception model or OSM can give, never hole numbers).

    sc = scene_from_osm(fc, boundary=course["boundary"])      # hole ways, pins and every ref / name hidden
    truth = truth_from_osm(fc, sc.proj)                        # [{ref, tee, green, par, line}] (eval only)
    sc2 = degrade(sc, rng, level=1.0)                          # perception-quality stand-in (eval)
    sc3 = scene_from_perception(scene_json)                    # course_data/perception/SCENE_SCHEMA.md

Everything is in a local equirectangular frame in yards (`Proj`). Elements carry a confidence `conf` in [0, 1]
(1 for OSM). Lists:
  greens   {id, c (centroid), ring, area, conf}
  tees     {id, c, ring | None, area, axis (radians, long-axis angle) | None, elong, conf}
  fairways {id, ring, c, conf}         bunkers / water / woods: rings (only used as weak evidence)
  paths    polylines (cart paths / footpaths inside or next to the course)
  clubhouse candidates {c, w, how}     w = prior weight (named clubhouse >> big building next to a car park)
  parking  points;  ranges: driving-range rings;  boundary: rings
"""
from __future__ import annotations

import gzip
import json
import math
import os
import random
from dataclasses import dataclass, field

import numpy as np

YD = 0.9144


class Proj:
    """Local equirectangular projection in yards around (lon0, lat0)."""

    def __init__(self, lon0, lat0):
        self.lon0, self.lat0 = float(lon0), float(lat0)
        self.kx = 111320.0 * math.cos(math.radians(lat0)) / YD
        self.ky = 110950.0 / YD

    def fwd(self, lon, lat):
        return (np.asarray(lon, float) - self.lon0) * self.kx, (np.asarray(lat, float) - self.lat0) * self.ky

    def inv(self, x, y):
        return self.lon0 + np.asarray(x, float) / self.kx, self.lat0 + np.asarray(y, float) / self.ky

    def ring(self, coords):
        a = np.asarray(coords, float)[:, :2]
        x, y = self.fwd(a[:, 0], a[:, 1])
        return np.c_[x, y]

    def ll(self, xy):
        lo, la = self.inv(xy[0], xy[1])
        return [round(float(lo), 7), round(float(la), 7)]


def centroid(xy):
    xy = np.asarray(xy, float)
    if len(xy) < 3:
        return xy.mean(0)
    x, y = xy[:, 0], xy[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    c = x * y1 - x1 * y
    a = c.sum() / 2
    if abs(a) < 1e-9:
        return xy.mean(0)
    return np.array([((x + x1) * c).sum() / (6 * a), ((y + y1) * c).sum() / (6 * a)])


def area(xy):
    x, y = np.asarray(xy, float).T
    return abs(np.dot(x, np.roll(y, -1)) - np.dot(np.roll(x, -1), y)) / 2


def long_axis(xy):
    """(angle of the long axis in radians, elongation >= 1) from the vertex-free second moment of the polygon
    (area-weighted triangles, so vertex density does not bias it)."""
    xy = np.asarray(xy, float)
    if len(xy) < 3:
        return None, 1.0
    c = centroid(xy)
    p = xy - c
    q = np.roll(p, -1, 0)
    cr = p[:, 0] * q[:, 1] - q[:, 0] * p[:, 1]
    sxx = (cr * (p[:, 0] ** 2 + p[:, 0] * q[:, 0] + q[:, 0] ** 2)).sum() / 12
    syy = (cr * (p[:, 1] ** 2 + p[:, 1] * q[:, 1] + q[:, 1] ** 2)).sum() / 12
    sxy = (cr * (2 * p[:, 0] * p[:, 1] + p[:, 0] * q[:, 1] + q[:, 0] * p[:, 1] + 2 * q[:, 0] * q[:, 1])).sum() / 24
    m = np.array([[sxx, sxy], [sxy, syy]]) * np.sign(cr.sum() or 1)
    w, v = np.linalg.eigh(m)
    if w[1] <= 1e-9:
        return None, 1.0
    return math.atan2(v[1, 1], v[0, 1]), float(math.sqrt(max(w[1], 1e-9) / max(w[0], 1e-9)))


def _rings(geom):
    t, c = geom.get("type"), geom.get("coordinates")
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [p[0] for p in c]
    return []


def _lines(geom):
    t, c = geom.get("type"), geom.get("coordinates")
    if t == "LineString":
        return [c]
    if t == "MultiLineString":
        return list(c)
    return []


@dataclass
class Scene:
    proj: Proj
    greens: list = field(default_factory=list)
    tees: list = field(default_factory=list)
    fairways: list = field(default_factory=list)
    bunkers: list = field(default_factory=list)
    water: list = field(default_factory=list)
    woods: list = field(default_factory=list)
    paths: list = field(default_factory=list)
    clubhouse: list = field(default_factory=list)
    parking: list = field(default_factory=list)
    ranges: list = field(default_factory=list)
    boundary: list = field(default_factory=list)
    buildings: list = field(default_factory=list)
    path_m: dict = field(default_factory=dict)
    source: str = "osm"
    meta: dict = field(default_factory=dict)

    def summary(self):
        return dict(greens=len(self.greens), tees=len(self.tees), fairways=len(self.fairways), paths=len(self.paths),
                    clubhouse=len(self.clubhouse), parking=len(self.parking), ranges=len(self.ranges),
                    source=self.source)


def _boundary_rings(boundary):
    if not boundary:
        return []
    if isinstance(boundary, str):
        import ast
        try:
            boundary = ast.literal_eval(boundary)
        except Exception:                                          # noqa: BLE001
            return []
    return _rings(boundary)


def _inside(pt, rings):
    x, y = pt
    for r in rings:
        n, inside, j = len(r), False, len(r) - 1
        for i in range(n):
            xi, yi = r[i]
            xj, yj = r[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
                inside = not inside
            j = i
        if inside:
            return True
    return False


def _dist_to_rings(pt, rings):
    if not rings:
        return 0.0
    if _inside(pt, rings):
        return 0.0
    best = 1e9
    for r in rings:
        a, b = r[:-1], r[1:]
        ab = b - a
        t = np.clip(((pt - a) * ab).sum(1) / np.maximum((ab ** 2).sum(1), 1e-9), 0, 1)
        d = np.hypot(*(a + ab * t[:, None] - pt).T)
        best = min(best, float(d.min()))
    return best


NAMED = ("clubhouse", "club house", "pro shop", "golf shop", "proshop", "golf club")
PATH_HW = ("path", "footway", "service", "track", "cycleway", "bridleway", "pedestrian")


def load_fc(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return json.load(fh)


def scene_from_osm(fc, boundary=None, center=None):
    """OSM features -> Scene with every hole hint hidden (golf=hole ways, pins, ref / name tags of golf features)."""
    feats = [f for f in fc.get("features", []) if f.get("geometry")]
    pts = []
    for f in feats:
        if f["properties"].get("golf") in ("green", "tee"):
            for r in _rings(f["geometry"]):
                pts += [p[:2] for p in r]
    if center is None:
        center = np.mean(pts, 0) if pts else np.mean([p[:2] for f in feats for r in _rings(f["geometry"]) for p in r], 0)
    pj = Proj(*center)
    sc = Scene(proj=pj)
    sc.boundary = [pj.ring(r) for r in _boundary_rings(boundary)]
    if not sc.boundary:
        for f in feats:
            if f["properties"].get("leisure") == "golf_course":
                sc.boundary += [pj.ring(r) for r in _rings(f["geometry"])]
    named = []
    for f in feats:
        p, g = f["properties"], f["geometry"]
        golf = p.get("golf")
        if golf in ("hole", "pin"):
            continue
        rings = [pj.ring(r) for r in _rings(g) if len(r) >= 4]
        if golf == "green":
            for r in rings:
                a = area(r)
                if a >= 60:
                    sc.greens.append(dict(id=f"g{len(sc.greens)}", c=centroid(r), ring=r, area=a, conf=1.0))
            if g["type"] == "Point":
                sc.greens.append(dict(id=f"g{len(sc.greens)}", c=np.array(pj.fwd(*g["coordinates"][:2])), ring=None,
                                      area=500.0, conf=0.7))
        elif golf == "tee":
            for r in rings:
                ax, el = long_axis(r)
                sc.tees.append(dict(id=f"t{len(sc.tees)}", c=centroid(r), ring=r, area=area(r), axis=ax, elong=el,
                                    conf=1.0))
            if g["type"] == "Point":
                sc.tees.append(dict(id=f"t{len(sc.tees)}", c=np.array(pj.fwd(*g["coordinates"][:2])), ring=None,
                                    area=0.0, axis=None, elong=1.0, conf=0.8))
        elif golf == "fairway":
            for r in rings:
                sc.fairways.append(dict(id=f"f{len(sc.fairways)}", ring=r, c=centroid(r), conf=1.0))
        elif golf == "bunker":
            sc.bunkers += rings
        elif golf in ("water_hazard", "lateral_water_hazard") or p.get("natural") == "water" or p.get("water"):
            sc.water += rings
        elif golf == "driving_range" or (golf and "range" in str(golf)):
            sc.ranges += rings
        elif golf in ("cartpath", "path"):
            sc.paths += [pj.ring(l) for l in _lines(g)]
        if p.get("natural") in ("wood", "tree_row", "scrub") or p.get("landuse") == "forest":
            sc.woods += rings
        if p.get("highway") in PATH_HW and g["type"] == "LineString" and p.get("service") != "parking_aisle" \
                and golf not in ("cartpath", "path"):
            sc.paths.append(pj.ring(g["coordinates"]))
        nm = str(p.get("name", "")).lower()
        if (golf == "clubhouse" or p.get("building") == "clubhouse" or p.get("club") == "golf" or
                (p.get("building") and any(k in nm for k in NAMED))):
            c = centroid(rings[0]) if rings else (np.array(pj.fwd(*g["coordinates"][:2])) if g["type"] == "Point" else None)
            if c is not None:
                named.append(c)
        if p.get("amenity") == "parking" or p.get("service") == "parking_aisle":
            c = centroid(rings[0]) if rings else (np.array(pj.fwd(*g["coordinates"][:2])) if g["type"] == "Point"
                                                  else pj.ring(g["coordinates"]).mean(0))
            sc.parking.append(c)
        if p.get("building") and rings and golf != "clubhouse":
            sc.buildings.append(dict(c=centroid(rings[0]), area=area(rings[0])))
    sc.clubhouse = clubhouse_candidates(sc, named)
    sc.meta["n_named_clubhouse"] = len(named)
    return sc


def clubhouse_candidates(sc, named=()):
    """Prior candidates for the clubhouse: named / tagged clubhouses (w 1), else buildings of >= 150 sq yds inside or
    within 150 yds of the course and within 150 yds of a car park (w by size), else car parks next to the course."""
    out = []
    bd = sc.boundary
    for c in named:
        if not bd or _dist_to_rings(c, bd) < 250:
            out.append(dict(c=np.asarray(c, float), w=1.0, how="named"))
    if out:
        return out
    for b in sc.buildings:
        if b["area"] < 150 or b["area"] > 6000:
            continue
        if bd and _dist_to_rings(b["c"], bd) > 150:
            continue
        dp = min((float(np.hypot(*(b["c"] - p))) for p in sc.parking), default=1e9)
        if dp > 150:
            continue
        out.append(dict(c=b["c"], w=0.25 + 0.5 * min(1.0, b["area"] / 1500), how="building"))
    if not out:
        for p in sc.parking:
            if not bd or _dist_to_rings(p, bd) < 150:
                out.append(dict(c=p, w=0.2, how="parking"))
    out.sort(key=lambda d: -d["w"])
    return out[:12]


def truth_from_osm(fc, proj):
    """[{ref, tee, green, par, line}] from the golf=hole ways (refs as int; ways without a numeric ref skipped)."""
    out = []
    for f in fc.get("features", []):
        p = f["properties"]
        if p.get("golf") != "hole" or f["geometry"]["type"] != "LineString":
            continue
        try:
            ref = int(str(p.get("ref")).strip())
        except (TypeError, ValueError):
            continue
        line = proj.ring(f["geometry"]["coordinates"])
        if len(line) < 2:
            continue
        try:
            par = int(p.get("par")) if p.get("par") else None
        except ValueError:
            par = None
        out.append(dict(ref=ref, tee=line[0], green=line[-1], par=par, line=line,
                        length=float(np.hypot(*np.diff(line, axis=0).T).sum())))
    out.sort(key=lambda h: h["ref"])
    return out


# ----------------------------------------------------------------------------- perception-quality stand-in
def degrade(sc, rng=None, level=1.0, drop_paths=None, drop_clubhouse=None):
    """A noisier copy of an OSM scene, mimicking a detector: tee boxes missed (p 0.25 level) or merged with a
    neighbour within 12 yds, centroid jitter (sd 4 yds), tee axes lost on 40 %, fairways missed (p 0.2) and
    clipped, greens missed (p 0.03) and false greens added near the clubhouse / in fairways (~1 per course),
    cart paths cut into pieces (p 0.3 per piece dropped), clubhouse only as an unnamed building (w 0.6) and
    confidences in 0.5-1. `level` scales every rate."""
    import copy
    rng = rng or random.Random(0)
    s = copy.copy(sc)
    s.source = f"osm_degraded_{level:g}"

    def jit(c, sd=4.0):
        return np.asarray(c, float) + np.array([rng.gauss(0, sd * level), rng.gauss(0, sd * level)])

    gr = []
    for g in sc.greens:
        if rng.random() < 0.03 * level:
            continue
        gr.append(dict(g, c=jit(g["c"], 2.5), conf=round(rng.uniform(0.6, 1.0), 2)))
    nfalse = sum(rng.random() < 0.5 * level for _ in range(2))
    for _ in range(nfalse):
        base = rng.choice(sc.fairways)["c"] if sc.fairways and rng.random() < 0.5 else \
            (sc.clubhouse[0]["c"] if sc.clubhouse else rng.choice(sc.greens)["c"])
        c = jit(base, 40.0)
        gr.append(dict(id="fg", c=c, ring=None, area=float(rng.uniform(250, 700)), conf=round(rng.uniform(0.3, 0.7), 2)))
    tees = []
    for t in sc.tees:
        if rng.random() < 0.25 * level:
            continue
        keep_axis = rng.random() > 0.4 * level
        tees.append(dict(t, c=jit(t["c"]), axis=t["axis"] if keep_axis else None,
                         elong=t["elong"] if keep_axis else 1.0, conf=round(rng.uniform(0.5, 1.0), 2)))
    merged, used = [], set()
    for i, t in enumerate(tees):
        if i in used:
            continue
        for j in range(i + 1, len(tees)):
            if j not in used and np.hypot(*(tees[j]["c"] - t["c"])) < 12 and rng.random() < 0.5 * level:
                used.add(j)
                t = dict(t, c=(t["c"] + tees[j]["c"]) / 2)
        merged.append(t)
    fws = []
    for f in sc.fairways:
        if rng.random() < 0.2 * level:
            continue
        fws.append(dict(f, conf=round(rng.uniform(0.5, 1.0), 2)))
    paths = []
    if not drop_paths:
        for p in sc.paths:
            n = len(p)
            k = 0
            while k < n - 1:
                m = rng.randint(3, 12)
                if rng.random() > 0.3 * level:
                    paths.append(p[k:k + m + 1])
                k += m
    ch = [] if drop_clubhouse else [dict(c=jit(c["c"], 8), w=min(c["w"], 0.6), how="detected") for c in sc.clubhouse[:3]]
    for i, g in enumerate(gr):
        g["id"] = f"g{i}"
    for i, t in enumerate(merged):
        t["id"] = f"t{i}"
    s.greens, s.tees, s.fairways, s.paths, s.clubhouse = gr, merged, fws, paths, ch
    return s


# ----------------------------------------------------------------------------- perception scenes
def scene_from_perception(obj, proj=None):
    """course_data/perception scene.json (`course_scene/1`, SCENE_SCHEMA.md) -> Scene.

    greens: every green (hole / practice / uncertain) with conf = p and `p_hole` kept (the solver's "not a hole"
    prior uses it); tee_complexes -> one tee each (centroid, axis from `axis_deg`, elongation from `length_m`),
    boxes kept for the walk distance; fairways: polygon and / or centreline (+ `ends`); cart_paths edges -> paths;
    clubhouse point (p) and buildings next to parking as extra candidates; relations.green_to_tee path_m kept as
    `sc.path_m[(green id, tee id)]` (cart-path walking distance)."""
    if obj.get("schema", "").startswith("course_scene"):
        return _from_course_scene(obj, proj)
    feats = list(obj.get("features") or [])
    pts = [p[:2] for f in feats for r in _rings(f.get("geometry") or {}) for p in r]
    if proj is None:
        proj = Proj(*np.mean(pts, 0)) if pts else Proj(0, 0)
    sc = Scene(proj=proj, source="perception_geojson")
    for f in feats:
        g = f.get("geometry") or {}
        p = f.get("properties", {})
        cls = str(p.get("class") or p.get("golf") or "").lower()
        conf = float(p.get("p", p.get("confidence", 1.0)) or 0)
        rings = [proj.ring(r) for r in _rings(g) if len(r) >= 3]
        pt = np.array(proj.fwd(*g["coordinates"][:2])) if g.get("type") == "Point" else None
        c = centroid(rings[0]) if rings else pt
        if cls == "green" and c is not None:
            sc.greens.append(dict(id=f"g{len(sc.greens)}", c=c, ring=rings[0] if rings else None,
                                  area=area(rings[0]) if rings else 500.0, conf=conf))
        elif cls in ("tee", "tee_complex") and c is not None:
            ax, el = long_axis(rings[0]) if rings else (None, 1.0)
            sc.tees.append(dict(id=f"t{len(sc.tees)}", c=c, ring=rings[0] if rings else None,
                                area=area(rings[0]) if rings else 0.0, axis=ax, elong=el, conf=conf))
        elif cls == "fairway":
            for r in rings:
                sc.fairways.append(dict(id=f"f{len(sc.fairways)}", ring=r, c=centroid(r), conf=conf))
        elif cls in ("cartpath", "cart_path"):
            sc.paths += [proj.ring(l) for l in _lines(g)]
        elif cls == "clubhouse" and c is not None:
            sc.clubhouse.append(dict(c=c, w=max(0.2, conf), how="perception"))
    return sc


def _bearing_to_axis(deg):
    """Bearing (0 = north, clockwise) -> math angle (radians from +x, counter-clockwise)."""
    return math.radians(90.0 - float(deg))


def _from_course_scene(obj, proj=None):
    pts = [g["centroid"] for g in obj.get("greens", []) if g.get("centroid")] + \
          [t["centroid"] for t in obj.get("tee_complexes", []) if t.get("centroid")]
    if proj is None:
        proj = Proj(*np.mean(pts, 0)) if pts else Proj(0, 0)
    M = 1.0 / YD
    sc = Scene(proj=proj, source="perception")
    sc.meta["scene_ids"] = {}
    for g in obj.get("greens", []):
        ring = proj.ring(g["polygon"]) if g.get("polygon") and len(g["polygon"]) >= 4 else None
        c = np.array(proj.fwd(*g["centroid"][:2])) if g.get("centroid") else (centroid(ring) if ring is not None else None)
        if c is None:
            continue
        p = float(g.get("p", 1.0))
        sc.greens.append(dict(id=g.get("id") or f"g{len(sc.greens)}", c=c, ring=ring,
                              area=float(g.get("area_m2", 450.0)) * M * M, conf=p,
                              p_hole=float(g.get("p_hole", p)), kind=g.get("kind")))
    for t in obj.get("tee_complexes", []):
        c = np.array(proj.fwd(*t["centroid"][:2])) if t.get("centroid") else None
        if c is None:
            continue
        ring = proj.ring(t["polygon"]) if t.get("polygon") and len(t["polygon"]) >= 4 else None
        ax = _bearing_to_axis(t["axis_deg"]) if t.get("axis_deg") is not None else None
        length = float(t.get("length_m") or 0) * M
        el = max(1.0, length / 12.0) if ax is not None else 1.0
        if ring is not None and ax is None:
            ax, el = long_axis(ring)
        boxes = [np.array(proj.fwd(*b["centroid"][:2])) for b in t.get("boxes", []) if b.get("centroid")]
        sc.tees.append(dict(id=t.get("id") or f"t{len(sc.tees)}", c=c, ring=ring, area=area(ring) if ring is not None else 0.0,
                            axis=ax, elong=el, conf=float(t.get("p", 1.0)) * (1 - float(t.get("p_range_tee", 0.0))),
                            box_xy=boxes))
    for f in obj.get("fairways", []):
        ring = proj.ring(f["polygon"]) if f.get("polygon") and len(f["polygon"]) >= 4 else None
        line = proj.ring(f["centerline"]) if f.get("centerline") and len(f["centerline"]) >= 2 else None
        ends = [np.array(proj.fwd(*e[:2])) for e in f.get("ends", [])] if f.get("ends") else None
        if ring is None and line is None:
            continue
        sc.fairways.append(dict(id=f.get("id") or f"f{len(sc.fairways)}", ring=ring, line=line, ends=ends,
                                c=centroid(ring) if ring is not None else line.mean(0), conf=float(f.get("p", 1.0))))
    for k, dst in (("bunkers", sc.bunkers), ("water", sc.water), ("trees", sc.woods)):
        for e in obj.get(k, []):
            if e.get("polygon") and len(e["polygon"]) >= 4:
                dst.append(proj.ring(e["polygon"]))
    cp = obj.get("cart_paths") or {}
    for e in cp.get("edges", []):
        if e.get("line") and len(e["line"]) >= 2:
            sc.paths.append(proj.ring(e["line"]))
    for pk in obj.get("parking", []):
        if pk.get("centroid"):
            sc.parking.append(np.array(proj.fwd(*pk["centroid"][:2])))
    for b in obj.get("buildings", []):
        if b.get("polygon") and len(b["polygon"]) >= 4:
            r = proj.ring(b["polygon"])
            sc.buildings.append(dict(c=centroid(r), area=area(r)))
    ch = obj.get("clubhouse")
    if ch and ch.get("ll"):
        sc.clubhouse.append(dict(c=np.array(proj.fwd(*ch["ll"][:2])), w=max(0.2, float(ch.get("p", 0.5))),
                                 how="perception"))
    sc.clubhouse += [c for c in clubhouse_candidates(sc) if c["how"] != "named"][:4]
    dr = (obj.get("practice") or {}).get("driving_range")
    if dr and dr.get("polygon"):
        sc.ranges.append(proj.ring(dr["polygon"]))
    sc.path_m = {}
    for r in (obj.get("relations") or {}).get("green_to_tee", []):
        if r.get("path_m") is not None:
            sc.path_m[(r["green"], r["tee"])] = float(r["path_m"]) * M
    return sc
