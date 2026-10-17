"""OSM labels (stack labels.geojson) -> truth objects in the stack's metric grid. EVALUATION / TRAINING ONLY.

    T = Truth(st)            # st = stack.load(dir); uses st.labels + st.meta["boundary"] (course polygon)
    T.greens  [{xy ring, kind: hole|practice|unknown, ref}]      T.holes [{ref, line xy, start, end, par}]
    T.tees    [{ring}]   T.fairways / bunkers / water / buildings / parking / ranges / woods [{ring}]
    T.cart_paths [line xy]  T.roads [line xy]   T.clubhouse xy | None
    T.raster(kind)  -> bool (H, W) mask of a polygon class;  T.line_raster(lines, width_m)
"""
from __future__ import annotations

import math
import re

import numpy as np

CART_HW = ("path", "footway", "track", "cycleway", "bridleway", "pedestrian", "service")
ROAD_HW = ("motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street",
           "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "road")
HOLE_END_M = 18.0


def _rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [p[0] for p in c]
    return []


def _ref_key(r):
    m = re.match(r"\s*(\d+)", str(r or ""))
    return int(m.group(1)) if m else None


class Truth:
    MIN_HOLES = 9          # hole vs practice greens only when the course's hole ways are mapped

    def __init__(self, st):
        self.st = st
        fc = st.labels or {"features": []}
        self.boundary = []
        b = st.meta.get("boundary")
        if b:
            for r in _rings(b):
                self.boundary.append(self._xy(r))
        self.greens, self.tees, self.fairways, self.bunkers, self.water = [], [], [], [], []
        self.buildings, self.parking, self.parking_pts, self.ranges, self.woods = [], [], [], [], []
        self.holes, self.cart_paths, self.roads, self.service = [], [], [], []
        self.clubhouse = None
        self.clubhouse_how = None
        ch_named = []
        for f in fc["features"]:
            p, g = f["properties"], f["geometry"]
            if not g:
                continue
            golf = p.get("golf")
            t = g["type"]
            if golf == "hole" and t == "LineString":
                xy = self._xy(g["coordinates"])
                self.holes.append(dict(ref=_ref_key(p.get("ref")), line=xy, start=xy[0], end=xy[-1], par=p.get("par")))
                continue
            if t in ("LineString",) and (golf in ("cartpath", "path") or p.get("golf_cart") in ("yes", "designated", "permissive")
                                          or (p.get("highway") in CART_HW and p.get("service") != "parking_aisle"
                                              and p.get("highway") != "service")):
                xy = self._xy(g["coordinates"])
                self.cart_paths.append(xy)
                continue
            if t == "LineString" and p.get("highway") == "service":
                if p.get("service") != "parking_aisle":
                    self.service.append(self._xy(g["coordinates"]))
                continue
            if t == "LineString" and p.get("highway") in ROAD_HW:
                self.roads.append(self._xy(g["coordinates"]))
                continue
            rings = [self._xy(r) for r in _rings(g)]
            if golf == "clubhouse" or p.get("building") == "clubhouse":
                c = (rings[0].mean(0) if rings else self._xy([g["coordinates"]])[0]) if t != "Point" else self._xy([g["coordinates"]])[0]
                self.clubhouse, self.clubhouse_how = c, "tagged"
            if t == "Point":
                if p.get("amenity") == "parking":
                    self.parking_pts.append(self._xy([g["coordinates"]])[0])
                continue
            if not rings:
                continue
            if golf == "green":
                for r in rings:
                    self.greens.append(dict(ring=r, kind="unknown", osm=p.get("osm")))
            elif golf == "tee":
                self.tees += [dict(ring=r) for r in rings]
            elif golf == "fairway":
                self.fairways += [dict(ring=r) for r in rings]
            elif golf == "bunker":
                self.bunkers += [dict(ring=r) for r in rings]
            elif golf in ("water_hazard", "lateral_water_hazard") or p.get("natural") == "water" or p.get("water") \
                    or p.get("landuse") in ("reservoir", "basin"):
                self.water += [dict(ring=r) for r in rings]
            elif golf == "driving_range" or (golf and "driving" in str(golf)):
                self.ranges += [dict(ring=r) for r in rings]
            elif p.get("amenity") == "parking":
                self.parking += [dict(ring=r) for r in rings]
            elif p.get("natural") in ("wood", "scrub") or p.get("landuse") == "forest":
                self.woods += [dict(ring=r) for r in rings]
            if p.get("building") and golf != "green":
                for r in rings:
                    self.buildings.append(dict(ring=r, name=p.get("name"), tag=p.get("building")))
                    nm = str(p.get("name") or "").lower()
                    if re.search(r"club ?house|pro shop|clubhouse", nm) or p.get("building") == "clubhouse":
                        ch_named.append(r.mean(0))
        if self.clubhouse is None and ch_named:
            self.clubhouse, self.clubhouse_how = ch_named[0], "named"
        # service ways mostly inside the course are cart / maintenance paths (run_course._is_cart_path)
        if self.boundary and self.service:
            from shapely.geometry import LineString, Polygon
            from shapely.ops import unary_union
            b = unary_union([Polygon(r).buffer(0) for r in self.boundary if len(r) >= 3])
            for l in self.service:
                ls = LineString(l)
                if ls.length > 0 and ls.intersection(b).length >= 0.7 * ls.length:
                    self.cart_paths.append(l)
                else:
                    self.roads.append(l)
        else:
            self.roads += self.service
        self.holes = [h for h in self.holes if len(h["line"]) >= 2]
        # hole vs practice greens: a hole way ends on (or within 18 m of) every hole green
        if len(self.holes) >= self.MIN_HOLES:
            from shapely.geometry import Point, Polygon
            ends = [Point(*h["end"]) for h in self.holes]
            for g in self.greens:
                try:
                    poly = Polygon(g["ring"]).buffer(0)
                except Exception:                                # noqa: BLE001
                    continue
                d = min(poly.distance(e) for e in ends)
                g["kind"] = "hole" if d <= HOLE_END_M else "practice"
                if g["kind"] == "hole":
                    h = min(self.holes, key=lambda h: poly.distance(Point(*h["end"])))
                    g["ref"] = h["ref"]

    # ------------------------------------------------------------------ helpers
    def _xy(self, coords):
        a = np.asarray(coords, float)[:, :2]
        x, y = self.st.ll_to_xy(a[:, 0], a[:, 1])
        return np.c_[np.atleast_1d(x), np.atleast_1d(y)]

    @property
    def mapped_holes(self):
        return len({h["ref"] for h in self.holes if h["ref"] is not None})

    def in_boundary_mask(self, pad_m=0.0):
        if not self.boundary:
            return np.ones((self.st.H, self.st.W), bool)
        m = self.raster_rings(self.boundary)
        if pad_m:
            from scipy import ndimage as ndi
            m = ndi.binary_dilation(m, iterations=int(pad_m / self.st.res))
        return m

    def raster_rings(self, rings):
        from rasterio import features
        from shapely.geometry import Polygon
        import geo
        shapes = []
        for r in rings:
            if len(r) >= 3:
                try:
                    shapes.append((Polygon(r).buffer(0), 1))
                except Exception:                                # noqa: BLE001
                    pass
        if not shapes:
            return np.zeros((self.st.H, self.st.W), bool)
        return features.rasterize(shapes, out_shape=(self.st.H, self.st.W), transform=geo.affine(self.st),
                                  fill=0, dtype="uint8").astype(bool)

    def raster(self, kind):
        return self.raster_rings([o["ring"] for o in getattr(self, kind)])

    def line_raster(self, lines, width_m):
        from rasterio import features
        from shapely.geometry import LineString
        import geo
        shapes = [(LineString(l).buffer(width_m / 2.0, cap_style=2), 1) for l in lines if len(l) >= 2]
        if not shapes:
            return np.zeros((self.st.H, self.st.W), bool)
        return features.rasterize(shapes, out_shape=(self.st.H, self.st.W), transform=geo.affine(self.st),
                                  fill=0, dtype="uint8").astype(bool)

    def cart_length_m(self, inside=True):
        from shapely.geometry import LineString, Polygon
        from shapely.ops import unary_union
        if not self.cart_paths:
            return 0.0
        ml = unary_union([LineString(l) for l in self.cart_paths if len(l) >= 2])
        if inside and self.boundary:
            b = unary_union([Polygon(r).buffer(30) for r in self.boundary if len(r) >= 3])
            ml = ml.intersection(b)
        return float(ml.length)

    def transitions(self):
        """Consecutive hole pairs (green end of hole n -> start of hole n+1) from the mapped hole ways."""
        by = {}
        for h in self.holes:
            if h["ref"] is not None and h["ref"] not in by:
                by[h["ref"]] = h
        out = []
        for k in sorted(by):
            if k + 1 in by:
                out.append(dict(ref=k, green_end=by[k]["end"], next_start=by[k + 1]["start"]))
        return out


def line_bearing_at(line, xy):
    """Bearing (deg true) of the segment of polyline `line` nearest to point xy."""
    best, bb = 1e18, None
    for a, b in zip(line[:-1], line[1:]):
        ab = b - a
        t = np.clip(np.dot(xy - a, ab) / max(np.dot(ab, ab), 1e-9), 0, 1)
        d = np.hypot(*(a + t * ab - xy))
        if d < best:
            best, bb = d, (math.degrees(math.atan2(ab[0], ab[1])) + 360) % 360
    return bb, best
