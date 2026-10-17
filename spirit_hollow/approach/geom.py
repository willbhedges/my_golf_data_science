"""Ground geometry for second shots at Spirit Hollow, in a local yard frame per hole.

Every hole gets an east/north yard frame with its origin on the OSM green's centroid
(course_data/packages/spirit_hollow/package.json, green_polygon_ll). The lie map merges three sources:

  1. the platform package's zones_ll for the whole hole (OSM fairway + vision2 long grass / trees / sand /
     water / OB), used OUTSIDE the hand-checked screenshot footprint,
  2. the hand-checked map (spirit_hollow/course.py HOLES zones incl. audit and landing-zone fixes, first
     cut), moved onto the ground through the NAIP registration (geo_zones.ShotGeo); INSIDE the
     screenshot footprint this is the truth (unzoned = rough),
  3. OSM bunkers and water (course_data/spirit_hollow/osm.geojson) everywhere on top, then this hole's
     green.

Screenshot pixels (the 920 x 2000 frame the wind page draws in) <-> ground: geo_zones.ShotGeo, then
course.display_xy for the holes drawn on a different screenshot (1, 10, 18).
"""
import json
import math
import os
import sys

import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
ROOT = os.path.dirname(SH)
for _p in (os.path.join(ROOT, "course_data", "imagery"), os.path.join(ROOT, "mozingo"), SH):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import course                                   # noqa: E402
import geo_zones as G                           # noqa: E402
import tee_strategy as t                        # noqa: E402

PACKAGE = os.path.join(ROOT, "course_data", "packages", "spirit_hollow", "package.json")
YD = 0.9144
# Precedence when the package's own zones overlap (later wins).
NEAR_GREEN = 40.0          # yds from the green centre where vision2 long grass is ignored
AUDITED = (150.0, 345.0)   # tee-distance band the landing-zone audit checked by eye
RANK = {"fairway": 0, "first_cut": 1, "recovery": 2, "native": 3, "sand": 4, "water": 5, "ob": 6}

_PKG = None
_OSM = None
_GEO = None


def package():
    global _PKG
    if _PKG is None:
        _PKG = json.load(open(PACKAGE))["holes"]
    return _PKG


def osm():
    global _OSM
    if _OSM is None:
        _OSM = G.osm_features()
    return _OSM


def geo():
    global _GEO
    if _GEO is None:
        _GEO = G.transforms_from_json()
    return _GEO


def ref_of(key):
    return G.ref_of(key)


class ENU:
    """Equirectangular yards about an origin (good to a few cm over a hole)."""

    def __init__(self, origin_ll):
        self.lon0, self.lat0 = float(origin_ll[0]), float(origin_ll[1])
        self.kx = 111320.0 * math.cos(math.radians(self.lat0)) / YD
        self.ky = 110540.0 / YD

    def from_ll(self, ll):
        ll = np.atleast_2d(np.asarray(ll, float))
        return np.c_[(ll[:, 0] - self.lon0) * self.kx, (ll[:, 1] - self.lat0) * self.ky]

    def to_ll(self, xy):
        xy = np.atleast_2d(np.asarray(xy, float))
        return np.c_[xy[:, 0] / self.kx + self.lon0, xy[:, 1] / self.ky + self.lat0]


class Hole:
    """One tee hole (course.HOLES key) on the ground, yards east/north of its green centroid."""

    def __init__(self, key):
        self.key = key
        self.hd = course.HOLES[key]
        self.ref = ref_of(key)
        self.pkg = package()[self.ref]
        self.par = int(self.hd["par"])
        g_ll = np.asarray(self.pkg["green_polygon_ll"], float)
        if np.allclose(g_ll[0], g_ll[-1]):
            g_ll = g_ll[:-1]
        self.enu = ENU(g_ll.mean(axis=0))
        self.green = self.enu.from_ll(g_ll)
        self.green_c = self._centroid(self.green)
        self.green_path = Path(self.green)
        self.geo = geo()[key]
        self.tee = self.px_to_xy([self.hd["tee"]])[0]
        self.green_trilat = self.px_to_xy([self.hd["green"]])[0]
        self.line = self.enu.from_ll(self.pkg["hole_line_ll"])
        self._build_lies()

    @staticmethod
    def _centroid(p):
        x, y = p[:, 0], p[:, 1]
        x1, y1 = np.roll(x, -1), np.roll(y, -1)
        c = x * y1 - x1 * y
        a = c.sum() / 2
        return np.array([((x + x1) * c).sum() / (6 * a), ((y + y1) * c).sum() / (6 * a)])

    # ---------------------------------------------------------------- frames
    def px_to_xy(self, px):
        return self.enu.from_ll(self.geo.px_to_ll(np.asarray(px, float)))

    def xy_to_px(self, xy):
        """Ground yards -> traced-screenshot px -> the px of the screenshot the page draws on."""
        px = self.geo.ll_to_px(self.enu.to_ll(xy))
        return course.display_xy(self.hd, px)

    def xy_to_ll(self, xy):
        return self.enu.to_ll(xy)

    # ---------------------------------------------------------------- lies
    def _build_lies(self):
        to = self.enu.from_ll
        pk = sorted(((z["lie"], to(z["poly"]), str(z.get("src", ""))) for z in self.pkg["zones_ll"] if z["lie"] in RANK),
                    key=lambda z: RANK[z[0]])
        # vision2 long grass (recall ~40%, many false alarms on mown rough round the greens when checked
        # against NAIP) is only used away from the green
        self.pkg_zones = [(lie, Path(p), lie == "native" and s_.startswith("vision"))
                          for lie, p, s_ in pk if len(p) >= 3]
        self.hand_zones = [(lie, Path(self.px_to_xy(poly))) for lie, poly in self.hd["zones"]]
        self.footprint = Path(self.px_to_xy(G.footprint_px()))
        near = lambda p: np.min(np.hypot(*(p - self.green_c).T)) < 700    # noqa: E731
        o = osm()
        self.osm_zones = ([("sand", Path(to(r))) for r in o["bunker"] if near(to(r))] +
                          [("water", Path(to(r))) for r in o["water"] if near(to(r))])

    def lie(self, pts):
        """Lie at each point (N x 2 yards): green, fairway, first_cut, rough, sand, recovery, native,
        water, ob.

        Inside the screenshot footprint AND the audited tee-shot band (AUDITED yds from the tee) the
        hand map is the whole truth (unzoned = rough: the audit removed vision false alarms there).
        Elsewhere the package zones fill in and the hand zones are drawn over them."""
        pts = np.atleast_2d(np.asarray(pts, float))
        lie = np.array(["rough"] * len(pts), dtype=object)
        r_tee = np.hypot(*(pts - self.tee).T)
        audited = self.footprint.contains_points(pts) & (r_tee >= AUDITED[0]) & (r_tee <= AUDITED[1])
        free = ~audited
        if free.any():
            q = pts[free]
            sub = lie[free]
            far = np.hypot(*(q - self.green_c).T) > NEAR_GREEN
            for name, p, vision_native in self.pkg_zones:
                m = p.contains_points(q)
                sub[m & far if vision_native else m] = name
            lie[free] = sub
        for name, p in self.hand_zones:
            lie[p.contains_points(pts)] = name
        for name, p in self.osm_zones:
            lie[p.contains_points(pts)] = name
        lie[self.green_path.contains_points(pts)] = "green"
        return lie

    # ---------------------------------------------------------------- hole line
    def along_line_from_green(self, dist):
        """Point on the hole line `dist` yds from the green centre walking back toward the tee
        (straight-line distance to the green centre), and the unit forward direction there."""
        line = np.vstack([self.line[:-1], self.green_c])           # end the line on our green centre
        rev = line[::-1]
        dense = [rev[0]]
        for a, b in zip(rev[:-1], rev[1:]):
            n = max(int(np.linalg.norm(b - a) / 1.0), 1)
            dense += [a + (b - a) * k / n for k in range(1, n + 1)]
        dense = np.array(dense)
        r = np.hypot(*(dense - self.green_c).T)
        i = int(np.searchsorted(np.maximum.accumulate(r), dist))
        i = min(max(i, 1), len(dense) - 1)
        p = dense[i]
        fwd = dense[max(i - 3, 0)] - dense[min(i + 3, len(dense) - 1)]
        fwd = fwd / np.linalg.norm(fwd)
        return p, fwd


def right_of(fwd):
    """Golfer's right for a forward unit vector in east/north yards."""
    return np.array([fwd[1], -fwd[0]])


LIES = ("green", "fairway", "first_cut", "rough", "sand", "recovery", "native", "water", "ob")
LIE_ID = {n: i for i, n in enumerate(LIES)}


class Raster:
    """The hole's lie map on a 1-yd grid (lookups are array indexing, so Monte Carlo is cheap).
    Points off the raster read as rough."""

    def __init__(self, hole, res=1.0, margin=90.0):
        pts = np.r_[hole.tee[None], hole.green, hole.line]
        self.x0, self.y0 = pts.min(axis=0) - margin
        x1, y1 = pts.max(axis=0) + margin
        self.res = res
        xs = np.arange(self.x0, x1, res) + res / 2
        ys = np.arange(self.y0, y1, res) + res / 2
        X, Y = np.meshgrid(xs, ys)
        lie = hole.lie(np.c_[X.ravel(), Y.ravel()])
        self.ids = np.array([LIE_ID[v] for v in lie], np.int8).reshape(X.shape)
        self.shape = X.shape

    def lie_id(self, pts):
        pts = np.asarray(pts, float)
        i = np.floor((pts[..., 1] - self.y0) / self.res).astype(int)
        j = np.floor((pts[..., 0] - self.x0) / self.res).astype(int)
        ok = (i >= 0) & (i < self.shape[0]) & (j >= 0) & (j < self.shape[1])
        out = np.full(pts.shape[:-1], LIE_ID["rough"], np.int8)
        out[ok] = self.ids[i[ok], j[ok]]
        return out
