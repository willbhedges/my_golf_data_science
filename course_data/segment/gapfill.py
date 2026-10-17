"""S4b imagery-model gap-fill: add U-Net fairway / bunker / green (and NIR-rule water) polygons to a course
package ONLY where OSM lacks them (ARCHITECTURE 9.1-5: never override OSM green/fairway/bunker/water).

    from gapfill import segment_gapfill
    pkg2 = segment_gapfill(package, "course_data/segment/<slug>/segment.geojson")   # new dict, input untouched

    python3 course_data/segment/gapfill.py --package course_data/packages/veenker/package.json \
        [--segment course_data/segment/veenker/segment.geojson] [--out package_filled.json]

Scope (default "hole"): a hole receives a lie only when it has no polygon of that lie (OSM or vision) within
30 yds of its line, i.e. the hole is poorly mapped for that class; fully mapped holes are left untouched.
Rules (all in a local metric projection):
  * existing = every zones_ll polygon of that lie in the package whose src is not "segment:*" (OSM and the
    vision stage), plus OSM green polygons for greens.
  * bunker / water / green: a model polygon is added only if < 10 % of it overlaps the existing class
    (a feature OSM does not have), minus the existing area.
  * fairway: model fairway minus the existing fairway (+3 m); pieces kept when >= 600 m2 and >= 8 m thick
    (2 x area / perimeter), so edge slivers next to a mapped fairway are dropped and whole unmapped fairways
    survive even when the model joins them to a mapped one.
  * everything is clipped to the OSM course boundary (+10 m); water pieces must be >= 1500 m2 (ponds).
  * a water piece whose 6 m ring is > 35 % tree canopy (the package's recovery zones) is a tree shadow: dropped.
  * U-Net water is never used (it marks the course interior); water comes from segment:nir.
  * min probability: fairway 0.5, bunker 0.5, green 0.6, water 0.6 (mean over the polygon).
Each added zone: {"lie", "poly", "src": "segment:ariadgolf-v4@<sha>" | "segment:nir", "p", "gapfill": "segment"}.
A hole with no OSM green polygon gets the nearest model green within 30 yds of green_ll
(provenance.green = "segment"). Unmapped tee candidates (U-Net tees near the first leg, > 10 yds from any
tee in the package) go to holes[ref]["tee_candidates_ll"] (not used for placement). Holes that received
zones get a flag; package.stages.segment / sources.segment record the model, sha and licence. Then
platform.package.reframe() refreshes the yard-frame zones and confidence.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)

LIE = {"fairway": "fairway", "bunker": "sand", "water": "water", "green": "green"}
MIN_P = {"fairway": 0.5, "sand": 0.5, "green": 0.6, "water": 0.6}
OVERLAP_MAX = 0.10
FAIRWAY_MIN_M2 = 600.0
FAIRWAY_MIN_THICK_M = 8.0
EDGE_BUFFER_M = 3.0
HOLE_REACH_M = 160 * 0.9144
CORRIDOR_M = 30 * 0.9144          # a hole "has" OSM <lie> when one lies within 30 yds of its line ...
CORRIDOR_MIN_M2 = {"fairway": 300.0, "sand": 5.0, "water": 50.0}   # ... with at least this much area there
GREEN_SNAP_M = 30 * 0.9144
TEE_MATCH_M = 10 * 0.9144
BOUNDARY_BUFFER_M = 10.0
WATER_MIN_M2 = 1500.0          # ponds only: small NIR-dark pieces were creek shade (SH 14)
SHADOW_RING_M = 6.0
SHADOW_TREE_FRAC = 0.35
LICENCE = ("ariadgolf/golf-course-segmentation weights: no licence granted (Hugging Face card: 'No additional "
           "license grant for the model weights is specified'); research/evaluation use until Ariad grants one. "
           "Labels it learned from: OpenStreetMap (ODbL). Imagery: USDA NAIP (public domain).")


class LocalProj:
    def __init__(self, lon0, lat0):
        from pyproj import Transformer
        crs = f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=m +ellps=WGS84"
        self.f = Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform
        self.i = Transformer.from_crs(crs, "EPSG:4326", always_xy=True).transform

    def fwd(self, g):
        from shapely.ops import transform
        return transform(self.f, g)

    def inv(self, g):
        from shapely.ops import transform
        return transform(self.i, g)


def _poly(ring):
    from shapely.geometry import Polygon
    p = Polygon(ring)
    return p if p.is_valid else p.buffer(0)


def _parts(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [x for x in getattr(g, "geoms", []) if x.geom_type == "Polygon" and not x.is_empty]


def _ring(p, ndig=7):
    return [[round(x, ndig), round(y, ndig)] for x, y in p.exterior.coords]


def load_segment(path):
    fc = json.load(open(path))
    return fc["features"], fc.get("properties", {})


def candidates(features, proj):
    """{lie: [(geom_m, p, src)]} and tee list [(geom_m, p)] from segment.geojson features."""
    from shapely.geometry import shape
    out = {v: [] for v in LIE.values()}
    tees = []
    for f in features:
        pr = f["properties"]
        c, src, p = pr["class"], pr["src"], float(pr.get("p", 1.0))
        g = proj.fwd(shape(f["geometry"]))
        g = g if g.is_valid else g.buffer(0)
        if c == "tee":
            tees.append((g, p))
            continue
        if c == "water" and not src.startswith("segment:nir"):
            continue                                            # the U-Net water class is not water
        lie = LIE.get(c)
        if lie and p >= MIN_P[lie]:
            out[lie].append((g, p, src))
    return out, tees


def existing(package, proj):
    from shapely.ops import unary_union
    seen, ex = set(), {v: [] for v in list(LIE.values()) + ["recovery"]}
    for h in package["holes"].values():
        for z in h.get("zones_ll") or []:
            src = str(z.get("src", ""))
            if src.startswith("segment"):
                continue
            lie = "sand" if z.get("lie") == "bunker" else z.get("lie")
            if lie not in ex:
                continue
            key = (lie, src, round(z["poly"][0][0], 6), round(z["poly"][0][1], 6), len(z["poly"]))
            if key in seen:
                continue
            seen.add(key)
            ex[lie].append(proj.fwd(_poly(z["poly"])))
        if h.get("green_polygon_ll") and str(h.get("provenance", {}).get("green", "")).startswith("osm"):
            ex["green"].append(proj.fwd(_poly(h["green_polygon_ll"])))
    return {k: unary_union(v) if v else None for k, v in ex.items()}


def fill_geoms(cands, ex):
    """[(lie, geom_m, p, src)] to add."""
    add = []
    for lie, items in cands.items():
        E = ex.get(lie)
        Eb = E.buffer(EDGE_BUFFER_M) if E is not None and not E.is_empty else None
        for g, p, src in items:
            if g.is_empty or g.area <= 0:
                continue
            if lie == "fairway":
                rest = g.difference(Eb) if Eb is not None else g
                for piece in _parts(rest):
                    thick = 2 * piece.area / max(piece.length, 1e-6)
                    if piece.area >= FAIRWAY_MIN_M2 and thick >= FAIRWAY_MIN_THICK_M:
                        add.append((lie, piece, p, src))
            else:
                ov = g.intersection(E).area / g.area if E is not None and not E.is_empty else 0.0
                if ov >= OVERLAP_MAX:
                    continue
                rest = g.difference(E) if E is not None and not E.is_empty else g
                for piece in _parts(rest):
                    if piece.area >= 0.5 * g.area or piece.area >= 50:
                        add.append((lie, piece, p, src))
    return add


def boundary(pkg, proj):
    from shapely.geometry import shape
    b = pkg.get("course", {}).get("boundary")
    if not b:
        return None
    g = shape(b) if isinstance(b, dict) else _poly(b)
    return proj.fwd(g if g.is_valid else g.buffer(0)).buffer(BOUNDARY_BUFFER_M)


def hole_has(pkg, proj, lines):
    """{ref: {lie}} lies the hole already has from non-segment sources inside its corridor."""
    out = {}
    for k, h in pkg["holes"].items():
        L = lines.get(k)
        out[k] = set()
        if L is None:
            continue
        cor = L.buffer(CORRIDOR_M)
        for z in h.get("zones_ll") or []:
            lie = "sand" if z.get("lie") == "bunker" else z.get("lie")
            if lie in CORRIDOR_MIN_M2 and lie not in out[k] and not str(z.get("src", "")).startswith("segment"):
                if proj.fwd(_poly(z["poly"])).intersection(cor).area >= CORRIDOR_MIN_M2[lie]:
                    out[k].add(lie)
    return out


def segment_gapfill(package, segment_path, *, reframe=True, scope="hole", log=print):
    """scope "hole" (default): a hole gets <lie> only when it has none within 30 yds of its line (a poorly
    mapped hole); fully mapped holes are untouched. scope "course": any model feature OSM lacks anywhere."""
    from shapely.geometry import LineString, Point
    feats, props = load_segment(segment_path)
    pkg = copy.deepcopy(package)
    c = pkg.get("course", {}).get("center") or pkg["holes"][next(iter(pkg["holes"]))]["green_ll"]
    proj = LocalProj(c[0], c[1])
    cands, tees = candidates(feats, proj)
    unet_src = next((f["properties"]["src"] for f in feats if f["properties"]["src"] != "segment:nir"), "segment:unet")
    ex = existing(pkg, proj)
    add = fill_geoms({k: v for k, v in cands.items() if k != "green"}, ex)
    B = boundary(pkg, proj)
    if B is not None:                                   # nothing outside the course (rivers, house ponds)
        add = [(lie, piece, p, src) for lie, g, p, src in add for piece in _parts(g.intersection(B))]
    add = [a for a in add if a[1].area >= (WATER_MIN_M2 if a[0] == "water" else 25.0)]
    trees = ex.get("recovery")
    if trees is not None and not trees.is_empty:        # NIR-dark + smooth next to canopy = tree shadow
        def shadow(g):
            ring = g.buffer(SHADOW_RING_M).difference(g)
            return ring.area > 0 and ring.intersection(trees).area / ring.area > SHADOW_TREE_FRAC
        add = [a for a in add if a[0] != "water" or not shadow(a[1])]
    stats = {"zones_added": 0, "holes": {}, "greens_added": 0, "tee_candidates": 0}
    lines = {k: proj.fwd(LineString(h["hole_line_ll"])) for k, h in pkg["holes"].items() if h.get("hole_line_ll")}
    has = hole_has(pkg, proj, lines) if scope == "hole" else {}
    for k, h in pkg["holes"].items():
        L = lines.get(k)
        if L is None:
            continue
        win = L.buffer(HOLE_REACH_M)
        got = {}
        for lie, g, p, src in add:
            if lie in has.get(k, ()) or not g.intersects(win):
                continue
            for piece in _parts(proj.inv(g)):
                h.setdefault("zones_ll", []).append({"lie": lie, "poly": _ring(piece), "src": src, "p": round(p, 3),
                                                     "gapfill": "segment"})
            got[lie] = got.get(lie, 0) + 1
        # green: only when the hole has no OSM green polygon
        if not str(h.get("provenance", {}).get("green", "")).startswith("osm") or not h.get("green_polygon_ll"):
            gp = proj.fwd(Point(*h["green_ll"])) if h.get("green_ll") else Point(L.coords[-1])
            best = min(cands["green"], key=lambda t: t[0].distance(gp), default=None)
            if best is not None and best[0].distance(gp) <= GREEN_SNAP_M:
                gl = proj.inv(max(_parts(best[0]), key=lambda x: x.area))
                h["green_polygon_ll"] = _ring(gl)
                h["green_ll"] = [round(gl.centroid.x, 7), round(gl.centroid.y, 7)]
                h.setdefault("provenance", {})["green"] = "segment"
                got["green"] = 1
                stats["greens_added"] += 1
        # tee candidates near the first leg that no package tee explains
        first = LineString(L.coords[:2])
        have = [proj.fwd(Point(*t["tee_ll"])) for t in (h.get("tees") or {}).values() if t.get("tee_ll")]
        tc = []
        for g, p in tees:
            ctr = g.centroid
            if ctr.distance(Point(first.coords[0])) > 0.5 * first.length + 50 or first.distance(ctr) > 45 * 0.9144:
                continue
            if have and min(ctr.distance(x) for x in have) <= TEE_MATCH_M:
                continue
            q = proj.inv(ctr)
            tc.append({"tee_ll": [round(q.x, 7), round(q.y, 7)], "p": round(p, 3), "area_m2": round(g.area, 1),
                       "src": unet_src})
        if tc:
            h["tee_candidates_ll"] = tc
            stats["tee_candidates"] += len(tc)
        if got:
            h.setdefault("flags", []).append(
                "imagery-model " + ", ".join(sorted(got)) + " where OSM has none (segment gap-fill; check on the map)")
            stats["holes"][k] = got
            stats["zones_added"] += sum(v for lie, v in got.items() if lie != "green")
    pkg.setdefault("stages", {})["segment"] = (
        f"ok: segment gap-fill {unet_src.split(':', 1)[1]} (+{stats['zones_added']} zones on {len(stats['holes'])} holes, "
        f"+{stats['greens_added']} greens, {stats['tee_candidates']} tee candidates)")
    pkg.setdefault("sources", {})["segment"] = {
        "model": props.get("model", "ariadgolf/golf-course-segmentation"), "model_sha": props.get("model_sha"),
        "naip": props.get("naip"), "file": os.path.relpath(os.path.abspath(segment_path), ROOT),
        "rule": "fill only where OSM lacks the class (never overrides OSM green/fairway/bunker/water)",
        "scope": scope,
        "licence": LICENCE if "ariadgolf" in str(props.get("model", "ariadgolf")) else str(props.get("licence", ""))}
    pkg.setdefault("attribution", [])
    if isinstance(pkg["attribution"], list) and not any("NAIP" in str(a) and "segment" in str(a) for a in pkg["attribution"]):
        pkg["attribution"].append("segment gap-fill: USDA NAIP imagery; U-Net trained on OpenStreetMap labels (ODbL)")
    log(f"segment gap-fill: {pkg['stages']['segment']}")
    if reframe:
        try:
            pkg = platform_module().reframe(pkg)
        except Exception as e:  # noqa: BLE001
            log(f"reframe failed ({type(e).__name__}: {e}); yard-frame zones not refreshed")
            pkg.setdefault("warnings", []).append(f"segment gap-fill: reframe failed: {e}")
    pkg["segment_fill"] = stats
    return pkg


def platform_module():
    import importlib.util
    name = "cdp_platform_package"
    if name in sys.modules:
        return sys.modules[name]
    pdir = os.path.join(CD, "platform")
    if pdir not in sys.path:
        sys.path.insert(0, pdir)
    spec = importlib.util.spec_from_file_location(name, os.path.join(pdir, "package.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def segment_for(package):
    """course_data/segment/<slug>/segment.geojson for a package, if the segment workflow produced one."""
    slug = package.get("slug") or package.get("course", {}).get("slug")
    p = os.path.join(HERE, slug or "-", "segment.geojson")
    return p if slug and os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--package", required=True)
    ap.add_argument("--segment")
    ap.add_argument("--out")
    a = ap.parse_args()
    pkg = json.load(open(a.package))
    seg = a.segment or segment_for(pkg)
    if not seg:
        sys.exit("no segment.geojson for this package (commit course_data/requests/segment_<slug>.json)")
    out = segment_gapfill(pkg, seg)
    json.dump(out, open(a.out or a.package, "w"), indent=1)
    print(json.dumps(out["segment_fill"], indent=1))


if __name__ == "__main__":
    main()
