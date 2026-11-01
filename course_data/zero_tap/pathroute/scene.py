"""pathroute scene: the card-blind course structure a human reads off the map.

From a (holes-hidden) OSM feature collection: greens, tee boxes, fairways, buildings, water, the clubhouse, and a
walking graph built from golf=cartpath + highway=path/footway/service/track/cycleway/steps inside (or near) the
course. Everything is in a local yard frame (truth.Proj).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import shape, Point, LineString
from shapely.ops import unary_union, transform
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import truth as TR  # noqa: E402

WALK_HW = {"path", "footway", "service", "track", "cycleway", "steps", "bridleway", "pedestrian"}
HOUSE_B = {"house", "residential", "apartments", "semidetached_house", "terrace", "detached", "garage", "yes",
           "commercial", "retail", "industrial", "shed", "roof"}


def _geom(f, pj):
    try:
        g = shape(f["geometry"])
    except Exception:
        return None
    if g.is_empty:
        return None
    g = transform(lambda x, y, z=None: pj.fwd_arr(x, y), g)
    if not g.is_valid:
        g = g.buffer(0)
    return g


class _Proj(TR.Proj):
    def fwd_arr(self, x, y):
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        return (x - self.lon0) * self.kx, (y - self.lat0) * self.ky


def _axis(poly):
    """(unit major-axis vector, elongation >= 1) of a polygon from its minimum rotated rectangle."""
    try:
        r = poly.minimum_rotated_rectangle
        xs, ys = r.exterior.coords.xy
        e1 = (xs[1] - xs[0], ys[1] - ys[0])
        e2 = (xs[2] - xs[1], ys[2] - ys[1])
        l1, l2 = math.hypot(*e1), math.hypot(*e2)
        if l1 < l2:
            e1, l1, l2 = e2, l2, l1
        return (e1[0] / (l1 or 1), e1[1] / (l1 or 1)), (l1 / max(l2, 1.0)), l1
    except Exception:
        return (1.0, 0.0), 1.0, 0.0


class Scene:
    def __init__(self, fc, course=None):
        feats = fc.get("features", [])
        pts = []
        for f in feats:
            if f["properties"].get("golf") == "green":
                try:
                    c = shape(f["geometry"]).centroid
                    pts.append((c.x, c.y))
                except Exception:
                    pass
        if not pts:
            raise ValueError("no greens")
        lon0 = float(np.mean([p[0] for p in pts]))
        lat0 = float(np.mean([p[1] for p in pts]))
        self.pj = _Proj(lon0, lat0)
        self.greens, self.tees, fair, bld, water, club, park, lines = [], [], [], [], [], [], [], []
        self.range_ = []
        for f in feats:
            p = f["properties"]
            gk, hw = p.get("golf"), p.get("highway")
            if gk in ("green", "tee", "fairway", "water_hazard", "lateral_water_hazard", "clubhouse", "cartpath",
                      "driving_range", "path") or hw in WALK_HW or p.get("building") or p.get("amenity") == "parking" \
                    or p.get("natural") == "water":
                g = _geom(f, self.pj)
                if g is None:
                    continue
                fid = f"{p.get('osm_type', 'x')}/{p.get('osm_id', len(self.tees))}"
                if gk == "green" and g.area > 30:
                    self.greens.append(dict(id=fid, g=g, c=(g.centroid.x, g.centroid.y),
                                            r=math.sqrt(g.area / math.pi)))
                elif gk == "tee":
                    if g.geom_type == "Point":
                        g = g.buffer(4)
                    ax, el, L = _axis(g)
                    self.tees.append(dict(id=fid, g=g, c=(g.centroid.x, g.centroid.y), ax=ax, el=el, L=L,
                                          area=g.area))
                elif gk == "fairway":
                    fair.append(g)
                elif gk in ("water_hazard", "lateral_water_hazard") or p.get("natural") == "water":
                    if g.geom_type in ("Polygon", "MultiPolygon"):
                        water.append(g)
                elif gk == "clubhouse" or p.get("building") == "clubhouse" or p.get("amenity") == "clubhouse":
                    club.append(g)
                elif gk == "driving_range":
                    self.range_.append(g)
                elif p.get("amenity") == "parking":
                    park.append(g)
                elif p.get("building"):
                    if g.geom_type in ("Polygon", "MultiPolygon"):
                        bld.append(g)
                if gk == "cartpath" or gk == "path" or hw in WALK_HW:
                    if g.geom_type in ("LineString", "MultiLineString"):
                        lines.append((g, gk == "cartpath"))
        if not self.tees:
            raise ValueError("no tees")
        self.fairways = fair
        self.fair_u = unary_union(fair) if fair else None
        self.fair_tree = STRtree(fair) if fair else None
        self.bld_u = unary_union(bld) if bld else None
        self.water_u = unary_union(water) if water else None
        self.green_u = unary_union([g["g"] for g in self.greens])
        gc = np.array([g["c"] for g in self.greens])
        self.gc = gc
        self.tc = np.array([t["c"] for t in self.tees])
        # clubhouse: tagged clubhouse, else the biggest non-house building closest to the greens' centre of mass
        # among those near a car park, else the car park nearest the greens.
        self.club = None
        self.club_src = "none"
        if club:
            cu = max(club, key=lambda g: g.area)
            self.club = (cu.centroid.x, cu.centroid.y)
            self.club_src = "clubhouse"
        else:
            hull = self.green_u.convex_hull.buffer(150)
            cands = [g for g in bld if g.area > 300 and hull.contains(g.centroid)]
            if park:
                pu = unary_union(park)
                near = [g for g in cands if g.distance(pu) < 80]
                if near:
                    cu = max(near, key=lambda g: g.area)
                    self.club, self.club_src = (cu.centroid.x, cu.centroid.y), "building+parking"
                else:
                    pk = [g for g in park if hull.contains(g.centroid)]
                    if pk:
                        cu = max(pk, key=lambda g: g.area)
                        self.club, self.club_src = (cu.centroid.x, cu.centroid.y), "parking"
            if self.club is None and cands:
                cu = max(cands, key=lambda g: g.area)
                self.club, self.club_src = (cu.centroid.x, cu.centroid.y), "building"
        if self.club is None:
            self.club = tuple(gc.mean(0))
            self.club_src = "centroid"
        self._graph(lines)

    # ------------------------------------------------------------------ walking graph
    def _graph(self, lines, step=15.0, join=6.0):
        hull = self.green_u.convex_hull.buffer(250)
        nodes, edges = [], []
        for g, cart in lines:
            parts = list(g.geoms) if g.geom_type == "MultiLineString" else [g]
            for ln in parts:
                if not ln.intersects(hull):
                    continue
                n = max(1, int(math.ceil(ln.length / step)))
                ps = [ln.interpolate(i / n, normalized=True) for i in range(n + 1)]
                base = len(nodes)
                nodes.extend((q.x, q.y) for q in ps)
                for i in range(n):
                    d = math.hypot(ps[i + 1].x - ps[i].x, ps[i + 1].y - ps[i].y)
                    edges.append((base + i, base + i + 1, d * (0.95 if cart else 1.0)))
        self.nodes = np.array(nodes) if nodes else np.zeros((0, 2))
        if len(nodes) < 2:
            self.G = None
            return
        from scipy.spatial import cKDTree
        self.kd = cKDTree(self.nodes)
        for i, j in self.kd.query_pairs(join):
            edges.append((i, j, float(np.hypot(*(self.nodes[i] - self.nodes[j])))))
        e = np.array(edges)
        n = len(nodes)
        self.G = coo_matrix((np.r_[e[:, 2], e[:, 2]] + 1e-3, (np.r_[e[:, 0], e[:, 1]].astype(int),
                                                             np.r_[e[:, 1], e[:, 0]].astype(int))), shape=(n, n)).tocsr()

    def path_dist(self, snap=45.0):
        """[green, tee] walking distance: off-path legs (green edge -> path, path -> tee edge) + graph distance;
        inf when either end is farther than `snap` from a path. Also returns the off-path leg lengths."""
        ng, nt = len(self.greens), len(self.tees)
        D = np.full((ng, nt), np.inf)
        if self.G is None:
            return D
        tsn = [self.kd.query_ball_point(t["c"], snap + t["L"] / 2) for t in self.tees]
        allt = sorted({i for s in tsn for i in s})
        if not allt:
            return D
        for gi, g in enumerate(self.greens):
            src = self.kd.query_ball_point(g["c"], snap + g["r"])
            if not src:
                continue
            gdist = np.array([max(0.0, math.hypot(*(self.nodes[s] - g["c"])) - g["r"]) for s in src])
            dd = dijkstra(self.G, indices=src, limit=1500)
            best = np.min(dd + gdist[:, None], axis=0)
            for ti, s in enumerate(tsn):
                if not s:
                    continue
                t = self.tees[ti]
                legs = np.array([max(0.0, math.hypot(*(self.nodes[k] - t["c"])) - t["L"] / 2) for k in s])
                D[gi, ti] = float(np.min(best[s] + legs))
        return D
