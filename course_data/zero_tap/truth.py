"""OSM hole truth for the zero-tap benchmark: hole lines, their greens / tees, par, completeness checks.

truth/1 (one per course, course_data/zero_tap/truth/<slug>.json):
  {"schema": "truth/1", "slug", "kind": 9|18|27|36, "n_holes", "complete": bool, "problems": [..],
   "greens_mapped": frac, "tees_mapped": frac,
   "holes": [{"ref": int, "course": label|null, "line": [[lon, lat], ..], "tee_ll", "green_ll" (OSM green centroid,
              else the line end), "green_osm": "way/1"|null, "green_r_yd", "tees_osm": ["way/2", ..],
              "length_yd", "par": int|null, "par_src": "osm"|"card"|null}],
   "hand_check": {...} (osm_check.py: per hole verdicts against NAIP, when the course was hand checked)}

Completeness (`complete`): the numeric refs of the course's golf=hole ways are exactly 1..N once (N = 9 / 18 / 27 /
36), or 1..9 three / four times, or 1..18 twice, or 1..18 + 1..9 (27 / 36-hole facilities); every hole line is
50-750 yds; >= 90 % of hole lines end on a mapped OSM green (<= 12 yds from its edge). Tee mapping is a label only.
"""
from __future__ import annotations

import gzip
import json
import math
from collections import Counter

YD = 1.0 / 0.9144


class Proj:
    """Local equirectangular frame in yards around (lon0, lat0)."""

    def __init__(self, lon0, lat0):
        self.lon0, self.lat0 = lon0, lat0
        self.kx = 111320.0 * math.cos(math.radians(lat0)) * YD
        self.ky = 110540.0 * YD

    def fwd(self, lon, lat):
        return ((lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky)

    def inv(self, x, y):
        return [self.lon0 + x / self.kx, self.lat0 + y / self.ky]


def load_fc(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return json.load(fh)


def _outer(geom):
    t = geom["type"]
    if t == "Polygon":
        return [geom["coordinates"][0]]
    if t == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    if t == "LineString" and len(geom["coordinates"]) >= 4 and geom["coordinates"][0] == geom["coordinates"][-1]:
        return [geom["coordinates"]]
    return []


def _centroid(ring):
    xs = [p[0] for p in ring[:-1]] or [ring[0][0]]
    ys = [p[1] for p in ring[:-1]] or [ring[0][1]]
    return [sum(xs) / len(xs), sum(ys) / len(ys)]


def _area(xy):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]):
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


def _pip(pt, poly):
    x, y = pt
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
            inside = not inside
    return inside


def seg_dist(p, line):
    best = 1e18
    for a, b in zip(line[:-1], line[1:]):
        abx, aby = b[0] - a[0], b[1] - a[1]
        L2 = abx * abx + aby * aby
        t = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, ((p[0] - a[0]) * abx + (p[1] - a[1]) * aby) / L2))
        best = min(best, math.hypot(a[0] + t * abx - p[0], a[1] + t * aby - p[1]))
    if len(line) == 1:
        best = math.hypot(line[0][0] - p[0], line[0][1] - p[1])
    return best


def poly_dist(p, poly):
    """0 inside, else distance to the ring."""
    if len(poly) >= 3 and _pip(p, poly):
        return 0.0
    return seg_dist(p, poly + poly[:1])


def features(fc, kind):
    """[(id, ring_ll or None, centroid_ll)] of golf=<kind> features."""
    out = []
    for f in fc.get("features", []):
        p = f["properties"]
        if p.get("golf") != kind or not f.get("geometry"):
            continue
        fid = f"{p.get('osm_type', 'f')}/{p.get('osm_id', len(out))}"
        g = f["geometry"]
        rings = _outer(g)
        if rings:
            for r in rings:
                out.append((fid, r, _centroid(r)))
        elif g["type"] == "Point":
            out.append((fid, None, g["coordinates"]))
        elif g["type"] == "LineString":
            out.append((fid, None, _centroid(g["coordinates"] + [g["coordinates"][0]])))
    return out


def _kind_of(refs):
    c = Counter(refs)
    keys = sorted(c)
    if not keys:
        return None
    for n in (9, 18, 27, 36):
        if keys == list(range(1, n + 1)) and all(v == 1 for v in c.values()):
            return n
    if keys == list(range(1, 10)) and len(set(c.values())) == 1 and c[1] in (3, 4):
        return 9 * c[1]
    if keys == list(range(1, 19)) and all(v == 2 for v in c.values()):
        return 36
    if keys == list(range(1, 19)) and all(c[i] == 2 for i in range(1, 10)) and all(c[i] == 1 for i in range(10, 19)):
        return 27
    return None


def extract(fc, slug=None, card=None):
    holes_raw = []
    for f in fc.get("features", []):
        p = f["properties"]
        if p.get("golf") != "hole" or not f.get("geometry") or f["geometry"]["type"] != "LineString":
            continue
        if p.get("inside_course") is False:
            continue
        try:
            ref = int(str(p.get("ref")).strip())
        except (TypeError, ValueError):
            continue
        co = f["geometry"]["coordinates"]
        if len(co) < 2:
            continue
        try:
            par = int(str(p.get("par")).strip()) if p.get("par") not in (None, "") else None
        except ValueError:
            par = None
        holes_raw.append(dict(ref=ref, line=[[round(a, 7), round(b, 7)] for a, b in co], par=par,
                              course=p.get("golf:course") or None, osm=f"{p.get('osm_type', 'way')}/{p.get('osm_id')}"))
    problems = []
    if not holes_raw:
        return dict(schema="truth/1", slug=slug, kind=None, n_holes=0, complete=False, problems=["no hole ways"],
                    greens_mapped=0.0, tees_mapped=0.0, par_known=0.0, holes=[])
    lon0 = sum(h["line"][-1][0] for h in holes_raw) / len(holes_raw)
    lat0 = sum(h["line"][-1][1] for h in holes_raw) / len(holes_raw)
    pj = Proj(lon0, lat0)
    greens = [(fid, [pj.fwd(*q) for q in r] if r else None, pj.fwd(*c), c) for fid, r, c in features(fc, "green")]
    tees = [(fid, [pj.fwd(*q) for q in r] if r else None, pj.fwd(*c), c) for fid, r, c in features(fc, "tee")]
    kind = _kind_of([h["ref"] for h in holes_raw])
    if kind is None:
        problems.append("refs not 1..N: " + ",".join(str(r) for r in sorted(h["ref"] for h in holes_raw))[:200])
    nG = nT = 0
    out = []
    for h in sorted(holes_raw, key=lambda h: (h["ref"], h["course"] or "")):
        line = [pj.fwd(*q) for q in h["line"]]
        L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(line[:-1], line[1:]))
        end, start = line[-1], line[0]
        best = None
        for fid, ring, c, cll in greens:
            d = poly_dist(end, ring) if ring else max(0.0, math.hypot(c[0] - end[0], c[1] - end[1]) - 8)
            if best is None or d < best[0]:
                best = (d, fid, ring, c, cll)
        e = dict(ref=h["ref"], course=h["course"], hole_osm=h["osm"], line=h["line"], tee_ll=h["line"][0],
                 green_ll=h["line"][-1], green_osm=None, green_r_yd=None, tees_osm=[], length_yd=round(L, 1),
                 par=h["par"], par_src="osm" if h["par"] else None)
        if best and best[0] <= 12:
            nG += 1
            ring = best[2]
            r = math.sqrt(max(_area(ring), 50.0) / math.pi) if ring and len(ring) >= 3 else 12.0
            e.update(green_ll=[round(best[4][0], 7), round(best[4][1], 7)], green_osm=best[1], green_r_yd=round(r, 1))
        near = sorted({fid for fid, ring, c, _ in tees
                       if (poly_dist(start, ring) if ring else math.hypot(c[0] - start[0], c[1] - start[1])) <= 35})
        if near:
            nT += 1
        e["tees_osm"] = near
        if not 50 <= L <= 750:
            problems.append(f"hole {h['ref']}: line {L:.0f} yds")
        out.append(e)
    n = len(out)
    if card and kind in (9, 18):
        cp = card.get("par") or []
        if len(cp) == kind:
            for e in out:
                if e["par"] is None and str(cp[e["ref"] - 1]).isdigit():
                    e["par"], e["par_src"] = int(cp[e["ref"] - 1]), "card"
    gm, tm = nG / max(n, 1), nT / max(n, 1)
    if gm < 0.9:
        problems.append(f"greens mapped {gm:.0%}")
    complete = kind is not None and gm >= 0.9 and not any("line" in p for p in problems)
    return dict(schema="truth/1", slug=slug, kind=kind, n_holes=n, complete=complete, problems=problems,
                greens_mapped=round(gm, 3), tees_mapped=round(tm, 3),
                par_known=round(sum(1 for e in out if e["par"]) / max(n, 1), 3), holes=out)


def hide(fc):
    """The OSM file a method may see in the OSM-mapped tier: golf=hole ways and golf=pin dropped, ref / name /
    par / handicap of every golf feature removed."""
    feats = []
    for f in fc.get("features", []):
        p = f["properties"]
        if p.get("golf") in ("hole", "pin"):
            continue
        if p.get("golf"):
            p = {k: v for k, v in p.items() if k not in ("ref", "name", "par", "handicap", "dist", "distance", "length")}
        feats.append(dict(f, properties=p))
    return dict(fc, features=feats)


def strip_golf(fc):
    """The unmapped tier: every golf=* feature dropped (boundary, buildings, car parks, paths, water, woods stay)."""
    return dict(fc, features=[f for f in fc.get("features", []) if not f["properties"].get("golf")])
