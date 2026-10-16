"""OpenStreetMap golf features -> the strategy model's per-hole dicts, in the 920 x 2000 screen frame.

  python course_data/geometry/build_holes.py course_data/spirit_hollow [--tee blue]
         [--lengths 1=419,2=616] [--tees tees.json] [--ppy 3.4] [--trees extra_trees.geojson] [--check]

Reads <dir>/osm.geojson (course_data/fetch_course.py) and writes
  <dir>/auto_holes.json   every hole: par, length, tee, dot270, green, zones (+ par-3 outline, tee options)
  <dir>/auto_course.py    loader exposing HOLES / PAR3 / ORDER / NOTES / AIM_AT / LABELS in
                          spirit_hollow/course.py's format (par 3s with a green polygon go in PAR3)
  <dir>/auto_preview.png  all holes drawn in their frames
  <dir>/holes_osm.json    the same holes in the yard frame (tee (0,0), dot270 (0,-270); ARCHITECTURE.md 3.5)
Tee: --tees (tee stage) > a tee box tagged --tee > the box whose playing length is closest to --lengths >
the box nearest the hole-line start (usually the back tee). Long tee polygons also offer their ends.
--trees adds recovery polygons from another source (imagery gap-fill); OSM here has no tree features.
--check compares against the hand-traced spirit_hollow/course.py (length, par, lie agreement on a
landing-zone grid) and prints which holes are missing on either side.

Frame (as mozingo/tee_strategy.hole_frame reads it): screen pixels, y down, the tee line points up
the screen, px-per-yd = |dot270 - tee| / 270. The tee line is the tee -> the first golf=hole node
>= 60 yds past it (the first leg on a dogleg). The scale fits the tee, the 240-330 yd landing area
and the green, capped at MAX_PPY so short holes don't get absurdly zoomed.

Zones (later wins, as in tee_strategy.lie_at; untraced = rough):
  ob (outside the leisure=golf_course boundary) < native < recovery < ob (buildings, residential
  landuse, roads, golf=out_of_bounds) < fairway (golf=fairway, golf=green) < water < sand.
Polygons with holes are cut into hole-free pieces, since lie_at uses plain matplotlib Paths.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import shapely
from pyproj import CRS, Transformer
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box, shape
from shapely.ops import split, unary_union

YD = 0.9144
W, H = 920, 2000
MARGIN_X, MARGIN_TOP, TEE_Y = 40, 90, 1920
MAX_PPY = 4.5
YARD_WINDOW = (150.0, 40.0)           # yard frame: +/- lateral, behind the tee (ahead: 40 past the green)
LONG_BOX = 600.0                      # yd2: a tee polygon this big offers its ends as tee points
MIN_TURN = 8.0                        # deg: a hole-line node bending less than this is not a dogleg
MIN_LEG = 60.0                        # yds: a hole-line node closer than this to the tee doesn't aim
LANDING = (240.0, 330.0, 45.0)        # along from, along to, +/- lateral yds that must be on screen
ORDER = ["ob_boundary", "native", "recovery", "ob", "fairway", "water", "sand"]
ROAD_HALF = dict(motorway=14, trunk=12, primary=10, secondary=8, tertiary=7, unclassified=5,
                 residential=5, motorway_link=6, trunk_link=6, primary_link=6, secondary_link=5)
WATERWAY_HALF = dict(stream=3, ditch=2, drain=2, canal=6, river=15)


# ----------------------------------------------------------------------------- OSM -> layers
def lie_of(p, gtype):
    """OSM tags -> (lie, half-width yds for lines) or None."""
    g, nat, lu = p.get("golf"), p.get("natural"), p.get("landuse")
    line = gtype in ("LineString", "MultiLineString")
    if g == "bunker" or (nat == "sand" and not line):
        return "sand", 0
    if g in ("water_hazard", "lateral_water_hazard") or nat in ("water", "wetland") \
            or (p.get("water") and not line):
        return ("water", 3) if line else ("water", 0)
    if p.get("waterway") and line:
        if p["waterway"] in ("dam", "weir"):
            return None
        try:
            half = float(str(p.get("width", "")).split()[0]) / YD / 2
        except (ValueError, IndexError):
            half = WATERWAY_HALF.get(p["waterway"], 3)
        return "water", max(half, 1.5)
    if g in ("fairway", "green"):
        return "fairway", 0
    if nat in ("wood", "scrub") or lu == "forest":
        return "recovery", 0
    if nat == "tree_row":
        return "recovery", 6
    if nat == "tree" and gtype == "Point":
        return "recovery", 5
    if g == "rough" and str(p.get("rough", p.get("golf:rough", ""))).lower() in ("deep", "native", "long", "high"):
        return "native", 0
    if g == "native" or nat in ("grassland", "heath") or lu in ("meadow",):
        return "native", 0
    if g == "out_of_bounds" or p.get("building") or lu in ("residential", "commercial", "industrial", "retail"):
        return "ob", 0 if not line else 2
    if line and p.get("highway") in ROAD_HALF:
        return "ob", ROAD_HALF[p["highway"]]
    if line and p.get("railway") in ("rail", "light_rail"):
        return "ob", 5
    return None


class World:
    """All features projected to a metric (UTM) frame, in yards."""

    def __init__(self, fc, extra_layers=()):
        feats = [f for f in fc["features"] if f.get("geometry")]
        lons, lats = [], []
        for f in feats:
            if f["properties"].get("leisure") == "golf_course":
                c = shape(f["geometry"]).centroid
                lons.append(c.x), lats.append(c.y)
        if not lons:
            c = shape(feats[0]["geometry"]).centroid
            lons, lats = [c.x], [c.y]
        lon0, lat0 = float(np.mean(lons)), float(np.mean(lats))
        zone = int((lon0 + 180) // 6) + 1
        self.crs = CRS.from_epsg((32600 if lat0 >= 0 else 32700) + zone)
        tr = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
        self.inv = Transformer.from_crs(self.crs, "EPSG:4326", always_xy=True)

        def proj(g):
            return shapely.transform(g, lambda xy: np.c_[tr.transform(xy[:, 0], xy[:, 1])] / YD)
        self.proj = proj
        self.counts = {}
        self.layers = {k: [] for k in ORDER}
        self.tees, self.greens, self.holes, self.course = [], [], [], []
        for f in feats:
            p, gt = f["properties"], f["geometry"]["type"]
            for k in ("golf", "natural", "landuse", "waterway", "leisure", "highway", "building", "water"):
                if k in p:
                    key = f"{k}={p[k] if k != 'building' else 'yes'}"
                    self.counts[key] = self.counts.get(key, 0) + 1
            g = proj(shape(f["geometry"]))
            if not g.is_valid:
                g = g.buffer(0)
            golf = p.get("golf")
            if golf == "tee":
                self.tees.append(dict(geom=g, pt=g.centroid if g.area > 0 else g, props=p))
            if golf == "green" and g.area > 0:
                self.greens.append(dict(geom=g, pt=g.centroid, props=p))
            if golf == "hole" and gt == "LineString":
                self.holes.append(dict(line=np.array(g.coords), props=p))
            if p.get("leisure") == "golf_course" and g.area > 0:
                self.course.append(g)
            lie = lie_of(p, gt)
            if lie:
                name, half = lie
                if g.geom_type in ("LineString", "MultiLineString", "Point"):
                    g = g.buffer(half or 2, cap_style="flat" if g.geom_type != "Point" else "round")
                if g.area > 0:
                    self.layers[name].append(g)
        for name, geoms in extra_layers:
            self.layers[name] += [proj(g) for g in geoms]
        self.course = unary_union(self.course) if self.course else None
        self.union = {k: unary_union(v) if v else None for k, v in self.layers.items()}


# ----------------------------------------------------------------------------- holes
def _arc(line):
    return np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))]


def _project(pt, line):
    """(arc position, distance) of pt on the polyline; behind the first node extrapolates (s < 0)."""
    best, s0 = (math.inf, 0.0), 0.0
    for a, b in zip(line, line[1:]):
        d = b - a
        L = float(np.hypot(*d))
        u = float(np.dot(pt - a, d) / (L * L + 1e-9))
        u = min(max(u, -10.0 if s0 == 0 else 0.0), 1.0)
        dist = float(np.hypot(*(a + u * d - pt)))
        if dist < best[0]:
            best = (dist, s0 + u * L)
        s0 += L
    return best[1], best[0]


def _turn(line, i):
    """Turn angle (deg) of the polyline at interior node i."""
    a, b = line[i] - line[i - 1], line[i + 1] - line[i]
    c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
    return math.degrees(math.acos(min(max(c, -1.0), 1.0)))


def _tee_path(pt, line, green_pt):
    """Playing path from a tee point (the tee, the hole-line nodes >= MIN_LEG ahead of it, the
    green), its length, the tee's arc position / offset on the line, and the aim point: the first
    of those nodes where the line really bends (> MIN_TURN), else the green. Nodes on a straight
    stretch don't set the direction, so a tee box mapped off to the side of the line still aims
    down the hole rather than across it at a nearby node."""
    seg = _arc(line)
    s, off = _project(pt, line)
    ahead = [i for i in range(1, len(line)) if seg[i] > s + MIN_LEG] or [len(line) - 1]
    path = np.vstack([pt, line[ahead]])
    path[-1] = green_pt
    bends = [k for k, i in enumerate(ahead, start=1) if i < len(line) - 1 and _turn(line, i) > MIN_TURN]
    aim = path[bends[0]] if bends else path[-1]
    return path, float(np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1))), s, off, aim


def tee_options(hole, world, green_pt):
    """Every golf=tee near the start of this hole's line, with the playing length from it. A long
    box (> LONG_BOX yd2, often several tee sets mapped as one polygon) also offers its back and
    front ends (5 yds in from the tip) as kind='box_back' / 'box_front'."""
    line = hole["line"]
    seg = _arc(line)
    out = []
    for t in world.tees:
        pt = np.array(t["pt"].coords[0])
        path, L, s, off, aim = _tee_path(pt, line, green_pt)
        if not (off < 40 and -160 < s < min(seg[-1] - 90, 180)):
            continue
        tag = " ".join(str(t["props"].get(k, "")) for k in ("tee", "golf:tee", "colour", "color", "ref", "name")).strip()
        base = dict(tag=tag, area=float(t["geom"].area), osm_id=t["props"].get("osm_id"))
        out.append(dict(base, pt=pt, path=path, length=L, kind="box", aim=aim,
                        start_dist=float(np.hypot(*(pt - line[0])))))
        if t["geom"].area > LONG_BOX:
            ring = np.array(t["geom"].exterior.coords)
            u = (green_pt - pt) / np.linalg.norm(green_pt - pt)
            proj = (ring - pt) @ u
            for kind, tip in (("box_back", proj.min() + 5), ("box_front", proj.max() - 5)):
                q = pt + tip * u
                pth, Lq, _, _, aq = _tee_path(q, line, green_pt)
                out.append(dict(base, pt=q, path=pth, length=Lq, kind=kind, aim=aq,
                                start_dist=float(np.hypot(*(q - line[0])))))
    return out


def choose_tee(opts, line, green_pt, tag=None, length=None):
    if tag:
        hit = [o for o in opts if tag.lower() in o["tag"].lower().split()]
        if hit:
            return hit[0], f"tee tagged {tag}"
    if length and opts:
        o = min(opts, key=lambda o: abs(o["length"] - length))
        return o, f"tee closest to {length:.0f} yds"
    boxes = [o for o in opts if o["kind"] == "box"]
    if boxes:
        return min(boxes, key=lambda o: o["start_dist"]), "tee nearest the hole-line start"
    path, L, _, _, aim = _tee_path(np.asarray(line[0], float), line, green_pt)
    return dict(pt=line[0], path=path, length=L, aim=aim, tag="", start_dist=0.0, kind="line"), \
        "hole-line start (no golf=tee near it)"


def find_green(world, end):
    p = Point(end)
    inside = [g for g in world.greens if g["geom"].buffer(3).contains(p)]
    if inside:
        return inside[0]
    near = sorted(world.greens, key=lambda g: g["geom"].distance(p))
    return near[0] if near and near[0]["geom"].distance(p) < 40 else None


def infer_holes(world):
    """No golf=hole ways: pair each green with the tee group that best fits a fairway between them."""
    holes, used = [], set()
    fw = world.union["fairway"]
    for gi, g in enumerate(world.greens):
        gp = np.array(g["pt"].coords[0])
        best = None
        for ti, t in enumerate(world.tees):
            if ti in used:
                continue
            tp = np.array(t["pt"].coords[0])
            L = float(np.hypot(*(gp - tp)))
            if not 90 < L < 650:
                continue
            seg = LineString([tp, gp])
            cover = seg.intersection(fw).length / L if fw is not None else 0.0
            score = cover - 0.0005 * L if L > 260 else 0.15 - 0.0005 * L     # par 3s need no fairway
            if best is None or score > best[0]:
                best = (score, ti, tp, L)
        if best:
            used.add(best[1])
            par = 3 if best[3] < 250 else (4 if best[3] < 480 else 5)
            holes.append(dict(line=np.vstack([best[2], gp]), props=dict(ref=str(len(holes) + 1), par=str(par)),
                              inferred=True))
    return holes


def frame_for(tee, aim, green_geom, green_pt, par, length, frame="fit"):
    """Affine (world yds -> frame) with the tee line pointing up, + the clip rectangle.
    frame: 'fit' (920 x 2000 px, scale fitted), a number (920 x 2000 px at that px/yd, tee at
    (460, 1900), as ARCHITECTURE.md's virtual pixel frame) or 'yard' (ppy 1, tee (0, 0))."""
    f = (aim - tee) / np.linalg.norm(aim - tee)
    r = np.array([f[1], -f[0]])                               # golfer's right in east/north

    def lo(pts):                                               # -> (right, along) yds
        d = np.atleast_2d(pts) - tee
        return np.c_[d @ r, d @ f]
    pts = [lo(tee)]
    if par >= 4:
        a0, a1, lat = LANDING
        a1 = min(a1, length + 20)
        pts.append(np.array([[-lat, a0], [lat, a0], [-lat, a1], [lat, a1]]))
    gp = np.array(green_geom.exterior.coords) if green_geom is not None else np.atleast_2d(green_pt)
    gl = lo(gp)
    pts.append(np.vstack([gl + [12, 12], gl - [12, 12]]))
    allp = np.vstack(pts)
    xmin, xmax = allp[:, 0].min(), allp[:, 0].max()
    amax = allp[:, 1].max()
    if frame == "yard":
        ppy, tx, ty = 1.0, 0.0, 0.0
        reach = max(330.0, amax - 12 + 40)
        clip = (-YARD_WINDOW[0], -reach, YARD_WINDOW[0], YARD_WINDOW[1])
    elif frame == "fit":
        ppy = min((W - 2 * MARGIN_X) / max(xmax - xmin, 1), (TEE_Y - MARGIN_TOP) / max(amax, 1), MAX_PPY)
        tx = W / 2 - (xmin + xmax) / 2 * ppy
        tx = min(max(tx, MARGIN_X), W - MARGIN_X)
        ty = TEE_Y
        clip = (0, 0, W, H)
    else:
        ppy, tx, ty, clip = float(frame), 460.0, 1900.0, (0, 0, W, H)
    # x = tx + ppy * right ; y = ty - ppy * along
    a, b = ppy * r[0], ppy * r[1]
    d, e = -ppy * f[0], -ppy * f[1]
    xoff = tx - (a * tee[0] + b * tee[1])
    yoff = ty - (d * tee[0] + e * tee[1])
    return [a, b, d, e, xoff, yoff], ppy, (tx, ty), f, r, clip


def _holefree(g):
    """Polygon(s) -> list of hole-free Polygons (cut through each interior ring)."""
    todo = list(getattr(g, "geoms", [g]))
    out = []
    while todo:
        p = todo.pop()
        if p.geom_type != "Polygon" or p.area < 1:
            if p.geom_type in ("MultiPolygon", "GeometryCollection"):
                todo += list(p.geoms)
            continue
        if not p.interiors:
            out.append(p)
            continue
        c = Polygon(p.interiors[0]).representative_point()
        x0, y0, x1, y1 = p.bounds
        cut = LineString([(c.x, y0 - 1), (c.x, y1 + 1)])
        parts = list(split(p, cut).geoms)
        if len(parts) < 2:                                   # degenerate: drop the hole
            out.append(Polygon(p.exterior))
            continue
        todo += parts
    return out


def zones_in_frame(world, M, clip, min_area=20):
    scr = box(*clip)
    zones = []
    for name in ORDER:
        if name == "ob_boundary":
            if world.course is None:
                continue
            course_px = affinity.affine_transform(world.course, M)
            g = scr.difference(course_px)
        else:
            u = world.union[name]
            if u is None:
                continue
            g = affinity.affine_transform(u, M).intersection(scr)
        if g.is_empty:
            continue
        g = g.simplify(0.75 * math.sqrt(min_area / 20))
        for p in _holefree(g):
            if p.area < min_area:                                     # < ~1-2 sq yds on screen
                continue
            xy = [(round(x, 1), round(y, 1)) for x, y in p.exterior.coords[:-1]]
            zones.append(("ob" if name == "ob_boundary" else name, xy))
    return zones


def par3_entry(world, h, M, ppy, tee_px, flag_px, green_geom):
    """course.PAR3-style dict: green outline as (yds right, yds past the flag)."""
    tee = np.array(tee_px)
    flag = np.array(flag_px)
    v = flag - tee
    center = float(np.linalg.norm(v)) / ppy
    fwd = v / np.linalg.norm(v)
    right = np.array([-fwd[1], fwd[0]])
    gpx = np.array(affinity.affine_transform(green_geom, M).simplify(0.6).exterior.coords[:-1])
    rel = gpx - flag
    yds = [(round(float(q @ right / ppy), 1), round(float(q @ fwd / ppy), 1)) for q in rel]
    # what lies off each edge: worst lie within 2-14 yds of the green edge
    sev = dict(water=4, ob=4, recovery=3, native=3, sand=2, fairway=0, rough=0)
    name = dict(water="water", ob="ob", recovery="trees", native="native", sand="bunker", fairway="rough",
                rough="rough")
    from matplotlib.path import Path
    paths = [(n, Path(p)) for n, p in h["zones"]]
    gl = np.array(yds)
    haz = {}
    for side, (ax, sign) in dict(left=(0, -1), right=(0, 1), short=(1, -1), long=(1, 1)).items():
        edge = gl[:, ax].max() if sign > 0 else gl[:, ax].min()
        other = 1 - ax
        probes = []
        for dd in np.arange(2, 15, 2):
            for o in np.linspace(-6, 6, 5):
                q = np.zeros(2)
                q[ax] = edge + sign * dd
                q[other] = o
                probes.append(flag + (q[0] * right + q[1] * fwd) * ppy)
        lies = np.array(["rough"] * len(probes), dtype=object)
        for n, pth in paths:
            lies[pth.contains_points(np.array(probes))] = n
        worst = max(set(lies), key=lambda n: (sev[n], list(lies).count(n)))
        haz[side] = name[worst]
    front = round(center + min(d for _, d in yds))
    back = round(center + max(d for _, d in yds))
    bad = [f"{v} {k}" for k, v in haz.items() if v != "rough"]
    note = ("Auto-built from OpenStreetMap. " + (", ".join(bad) + "." if bad else "No mapped trouble near the green."))
    return dict(image=None, tee=tuple(tee_px), flag=tuple(round(float(c), 1) for c in flag_px),
                center=round(center), front=front, back=back, green=yds, haz=haz, note=note,
                short=note.replace("Auto-built from OpenStreetMap. ", ""), source="osm")


def build(fc, tee_tag=None, lengths=None, extra_layers=(), only=None, world=None, tees=None, frame="fit"):
    """{ref: hole dict}. tees = tees.json's dict (schema tees/1): its tee_ll wins over OSM boxes."""
    world = world or World(fc, extra_layers)
    ext = (tees or {}).get("holes", {})
    holes = world.holes or infer_holes(world)
    out, report = {}, {}
    for hole in holes:
        p = hole["props"]
        ref = str(p.get("ref") or len(out) + 1)
        if only and ref != only:
            continue
        par = int(p["par"]) if str(p.get("par", "")).isdigit() else None
        line = hole["line"]
        g = find_green(world, line[-1])
        green_geom = g["geom"] if g else None
        green_pt = np.array(g["pt"].coords[0]) if g else line[-1]
        opts = tee_options(hole, world, green_pt)
        if ref in ext and ext[ref].get("tee_ll"):
            pt = np.array(world.proj(Point(ext[ref]["tee_ll"])).coords[0])
            pth, L, _, _, aq = _tee_path(pt, line, green_pt)
            tee, how = dict(pt=pt, path=pth, length=L, aim=aq), "tees.json:" + str(ext[ref].get("how", "given"))
        else:
            tee, how = choose_tee(opts, line, green_pt, tee_tag, (lengths or {}).get(ref))
        path = tee["path"]
        length = tee["length"]
        if par is None:
            par = 3 if length < 250 else (4 if length < 480 else 5)
        aim = tee["aim"]
        M, ppy, tee_px, f, r, clip = frame_for(tee["pt"], aim, green_geom, green_pt, par, length, frame)
        dot270 = (tee_px[0], tee_px[1] - 270 * ppy)
        green_px = affinity.affine_transform(Point(green_pt), M).coords[0]
        hpath = np.array(affinity.affine_transform(LineString(path), M).coords)
        h = dict(par=par, length=round(length), image=None, source="osm",
                 tee=(round(tee_px[0], 1), round(tee_px[1], 1)),
                 dot270=(round(dot270[0], 1), round(dot270[1], 1)),
                 green=(round(green_px[0], 1), round(green_px[1], 1)),
                 px_per_yd=round(ppy, 3), tee_choice=how, inferred=bool(hole.get("inferred")),
                 hole_line=hpath.round(1).tolist(),
                 tee_options=sorted(round(o["length"]) for o in opts),
                 handicap=p.get("handicap"),
                 tee_ll=_ll(world, tee["pt"]), aim_ll=_ll(world, aim), green_ll=_ll(world, green_pt),
                 provenance=dict(tee=how, green="osm_green" if g else "hole line end",
                                 par="osm" if str(p.get("par", "")).isdigit() else "length rule",
                                 length="measured along the hole line"),
                 zones=zones_in_frame(world, M, clip, 20 if frame != "yard" else 1.5))
        if green_geom is not None:
            h["green_polygon"] = np.array(affinity.affine_transform(green_geom, M).simplify(
                0.3 * ppy).exterior.coords[:-1]).round(1).tolist()
        if par == 3 and green_geom is not None:
            h["par3"] = par3_entry(world, h, M, ppy, h["tee"], green_px, green_geom)
        out[ref] = h
        report[ref] = dict(how=how, green=bool(g), tees=len(opts))
    return out, world


def _ll(world, pt):
    return [round(v, 7) for v in world.inv.transform(*(np.asarray(pt, float) * YD))]


def build_holes(fc, tees=None, frame="yard", **kw):
    """ARCHITECTURE.md S3 entry point: {ref: hole} (yard frame by default; 'fit' or a px/yd for pixels)."""
    return build(fc, tees=tees, frame=frame, **kw)[0]


# ----------------------------------------------------------------------------- outputs
AUTO_COURSE = '''"""Auto-built course (OpenStreetMap -> course_data/geometry/build_holes.py). Do not edit by hand:
re-run  python course_data/geometry/build_holes.py {dir}

Same format as spirit_hollow/course.py: HOLES (par 4/5, plus par 3s without a mapped green) with tee,
dot270, green, length, par, zones in a 920 x 2000 screen frame; PAR3 with the green outline in yds.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "auto_holes.json")) as _fh:
    _RAW = json.load(_fh)["holes"]


def _key(k):
    return int(k) if str(k).isdigit() else k


HOLES, PAR3 = {{}}, {{}}
for _k, _h in _RAW.items():
    _h = dict(_h)
    _h["tee"], _h["dot270"], _h["green"] = tuple(_h["tee"]), tuple(_h["dot270"]), tuple(_h["green"])
    _h["zones"] = [(n, [tuple(p) for p in poly]) for n, poly in _h["zones"]]
    _h.setdefault("aim_min", -40)
    _h.setdefault("aim_max", 40)
    _p3 = _h.pop("par3", None)
    if _p3:
        _p3 = dict(_p3, tee=tuple(_p3["tee"]), flag=tuple(_p3["flag"]), green=[tuple(p) for p in _p3["green"]])
        _p3["zones"] = _h["zones"]
        PAR3[_key(_k)] = _p3
    else:
        HOLES[_key(_k)] = _h

ORDER = sorted(set(HOLES) | set(PAR3), key=lambda k: (str(k).rstrip("BF").zfill(3), str(k)))
NOTES = {{k: "Auto-built from OpenStreetMap ({{}}).".format(h.get("tee_choice", "")) for k, h in HOLES.items()}}
AIM_AT = {{k: "Centre of the fairway" for k in HOLES}}
LABELS = {{}}
'''

COL = dict(ob="#bdbdbd", native="#d8c37a", recovery="#2f6b3a", fairway="#7ccf6a", water="#4a90d9",
           sand="#f1e3b0")


def preview(holes, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly
    keys = sorted(holes, key=lambda k: str(k).zfill(3))
    cols = min(6, len(keys))
    rows = math.ceil(len(keys) / cols)
    fig, axs = plt.subplots(rows, cols, figsize=(2.3 * cols, 4.8 * rows), squeeze=False)
    for ax in axs.flat:
        ax.axis("off")
    for ax, k in zip(axs.flat, keys):
        h = holes[k]
        ax.add_patch(MPoly([[0, 0], [W, 0], [W, H], [0, H]], color="#a7d39b", lw=0))
        for n, xy in h["zones"]:
            ax.add_patch(MPoly(xy, closed=True, color=COL[n], lw=0))
        hl = np.array(h["hole_line"])
        ax.plot(hl[:, 0], hl[:, 1], "r-", lw=0.8)
        ax.plot(*h["tee"], "ks", ms=4)
        ax.plot(*h["dot270"], "ro", ms=3)
        ax.plot(*h["green"], "wo", mec="k", ms=5)
        ax.set_xlim(0, W)
        ax.set_ylim(H, 0)
        ax.set_aspect("equal")
        ax.set_title(f"{k}  par {h['par']}  {h['length']} yd", fontsize=8)
    fig.suptitle("auto_holes: grey=OB tan=native dkgreen=trees green=fairway/green blue=water sand=bunker; "
                 "red line = hole line, red dot = 270", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


# ----------------------------------------------------------------------------- self-check
def check(fc, holes_auto, extra_layers=()):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, "..", ".."))
    sys.path[:0] = [os.path.join(root, "spirit_hollow"), os.path.join(root, "mozingo")]
    import course
    import tee_strategy as t
    a, l = np.meshgrid(np.arange(200, 321, 5), np.arange(-45, 46, 5))
    along, lat = a.ravel().astype(float), l.ravel().astype(float)

    def lies(h, al=along, la=lat):
        tee, f, r, ppy = t.hole_frame(h)
        return t.lie_at(h, tee + (al[:, None] * f + la[:, None] * r) * ppy)
    # tee per traced variant (2B/2F, 9B/9F) by matching the traced length
    lengths = {str(k).rstrip("BF"): float(h["length"]) for k, h in course.HOLES.items()}
    rows, conf = [], {}
    for k, h in list(course.HOLES.items()) + list(course.PAR3.items()):
        ref = str(k).rstrip("BF")
        traced_len = h.get("length", h.get("center"))
        if ref not in holes_auto:
            rows.append(dict(hole=k, missing="osm"))
            continue
        # the screenshots came from the app's tee, not necessarily the back one: compare from the
        # OSM tee box whose playing length is closest to the traced length
        alt, _ = build(fc, lengths={ref: float(traced_len)}, extra_layers=extra_layers, only=ref)
        ah = alt[ref]
        row = dict(hole=k, par_hand=h.get("par", 3), par_osm=ah["par"], len_hand=traced_len,
                   len_osm=ah["length"] if "par3" not in ah else ah["par3"]["center"],
                   len_default=holes_auto[ref]["length"],
                   tee_opts=ah["tee_options"])
        if "zones" in h:
            # green position: yds along/right of each map's own tee line
            for nm, hh in (("hand", h), ("osm", ah)):
                tee, f, r, ppy = t.hole_frame(hh)
                g = (np.array(hh["green"]) - tee) / ppy
                row[f"green_{nm}"] = (round(float(g @ f)), round(float(g @ r)))
            # the two tee lines differ (app's dashed line vs OSM's first leg): register by rotating the
            # OSM frame about the tee so the green bearings agree, then compare lies on the same grid
            # the two tee lines differ (the app's dashed line vs OSM's first leg): register by the
            # rotation about the tee (+/-8 deg) that best matches the lies, and report both
            tr = lies(h)
            au_raw = lies(ah)
            best = (-1, 0.0, au_raw)
            for deg in np.arange(-8, 8.1, 1.0):
                c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
                au_r = lies(ah, along * c - lat * s_, along * s_ + lat * c)
                sc = float(np.mean(tr == au_r))
                if sc > best[0] + 1e-9:
                    best = (sc, deg, au_r)
            au = best[2]
            row["rot_deg"] = best[1]
            row["agree_raw"] = float(np.mean(tr == au_raw))
            row["agree"] = best[0]
            row["fw_iou"] = float(np.sum((tr == "fairway") & (au_raw == "fairway")) /
                                  max(np.sum((tr == "fairway") | (au_raw == "fairway")), 1))
            for x, y in zip(tr, au):
                conf[(x, y)] = conf.get((x, y), 0) + 1
        rows.append(row)
    hand_refs = {str(k).rstrip("BF") for k in list(course.HOLES) + list(course.PAR3)}
    missing_hand = sorted(set(holes_auto) - hand_refs, key=lambda s: s.zfill(3))
    return rows, conf, missing_hand


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("course_dir")
    ap.add_argument("--tee", help="tee tag to prefer (tee / golf:tee / colour / name), e.g. blue")
    ap.add_argument("--lengths", help="scorecard yardages, e.g. 1=419,2=616 (picks the tee box)")
    ap.add_argument("--trees", help="extra recovery polygons (GeoJSON in WGS84), e.g. from naip_trees.py")
    ap.add_argument("--tees", help="tees.json (schema tees/1) from the tee stage; its tee_ll wins")
    ap.add_argument("--ppy", type=float, help="fixed px/yd with the tee at (460, 1900) instead of a fitted scale")
    ap.add_argument("--check", action="store_true", help="compare against spirit_hollow/course.py")
    a = ap.parse_args()
    with open(os.path.join(a.course_dir, "osm.geojson")) as fh:
        fc = json.load(fh)
    lengths = {k: float(v) for k, v in (kv.split("=") for kv in a.lengths.split(","))} if a.lengths else None
    extra = []
    if a.trees:
        with open(a.trees) as fh:
            extra = [("recovery", [shape(f["geometry"]) for f in json.load(fh)["features"]])]
    tees = None
    if a.tees:
        with open(a.tees) as fh:
            tees = json.load(fh)
    world = World(fc, extra)
    holes, _ = build(fc, a.tee, lengths, world=world, tees=tees, frame=a.ppy or "fit")
    yard, _ = build(fc, a.tee, lengths, world=world, tees=tees, frame="yard")
    with open(os.path.join(a.course_dir, "holes_osm.json"), "w") as fh:
        json.dump(dict(schema="holes/1", frame="yard", source="course_data/geometry/build_holes.py",
                       holes={k: dict(ref=k, **v) for k, v in yard.items()}), fh, separators=(",", ":"))
    meta = dict(source="OpenStreetMap" + (" + " + os.path.basename(a.trees) if a.trees else ""),
                frame=[W, H], px_per_yd=a.ppy or "fitted per hole", tag_counts=dict(sorted(world.counts.items(), key=lambda kv: -kv[1])),
                tee_tag=a.tee, lengths=lengths, n_holes=len(holes))
    with open(os.path.join(a.course_dir, "auto_holes.json"), "w") as fh:
        json.dump(dict(meta=meta, holes=holes), fh, separators=(",", ":"))
    with open(os.path.join(a.course_dir, "auto_course.py"), "w") as fh:
        fh.write(AUTO_COURSE.format(dir=a.course_dir))
    preview(holes, os.path.join(a.course_dir, "auto_preview.png"))
    print(f"{len(holes)} holes:", {k: (h["par"], h["length"], len(h["zones"])) for k, h in holes.items()})
    if a.check:
        rows, conf, missing_hand = check(fc, holes, extra)
        print("\nhole  par hand/osm  len hand/osm  diff  lie-agree raw->registered  green(along,right) hand / osm  tee options")
        diffs = []
        for r in rows:
            if r.get("missing"):
                print(f"{str(r['hole']):>4}  MISSING in OSM")
                continue
            d = r["len_osm"] - r["len_hand"]
            diffs.append(d)
            ag = (f"{r['agree_raw']:.2f}->{r['agree']:.2f} ({r['rot_deg']:+.0f}deg)  fw-IoU {r['fw_iou']:.2f}"
                  if "agree" in r else "  -  ")
            print(f"{str(r['hole']):>4}  {r['par_hand']}/{r['par_osm']}  {r['len_hand']:>4.0f}/{r['len_osm']:>4.0f}"
                  f"  {d:+5.0f}  {ag}  {r.get('green_hand', '')} / {r.get('green_osm', '')}  {r['tee_opts']}")
        ags = [r["agree"] for r in rows if "agree" in r]
        print(f"\nmedian |len diff| {np.median(np.abs(diffs)):.0f} yds, max {np.max(np.abs(diffs)):.0f}; "
              f"par mismatches: {[r['hole'] for r in rows if not r.get('missing') and r['par_hand'] != r['par_osm']]}")
        print(f"mean lie agreement on the 200-320 x +/-45 yd grid: raw {np.mean([r['agree_raw'] for r in rows if 'agree' in r]):.3f}, "
              f"registered {np.mean(ags):.3f}")
        labs = sorted({x for x, _ in conf} | {y for _, y in conf})
        print("confusion (rows hand, cols osm):", labs)
        for x in labs:
            print(f"{x:>9}", [conf.get((x, y), 0) for y in labs])
        print("holes in OSM but not hand-traced:", missing_hand)


if __name__ == "__main__":
    main()
