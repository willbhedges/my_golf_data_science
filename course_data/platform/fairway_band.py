"""Widen a package's mapped fairway by a band (OSM mappers often trace the mown stripe, not the first cut).

    from fairway_band import widen_package
    pkg2, n = widen_package(pkg, band_yd=8, lie="fairway")     # new dict; the input is not mutated

Per hole, the union of the hole's fairway zones (zones_ll, lie fairway) is buffered outward by band_yd (mitred
joins, local metres); the band keeps only what was rough: every other zone of the hole (green, tee, sand, water,
trees, long grass, OB, first cut, other fairway) is cut out of it, so the band never covers a hazard the map
already has, and hole-free parts are appended to zones_ll as {lie, poly, src: "fairway_band+<n>yd"}. With
lie="first_cut" the band is first cut (product/package LIE_MAP), else more fairway. Holes with no fairway zone
are left alone. The yard-frame `zones` are refreshed with platform/package.reframe when given.
Calibration and the error-budget result: platform/ERROR_BUDGET.md "Fairway".
"""
from __future__ import annotations

import copy
import math

YD = 0.9144
KEEP_OUT = ("green", "tee", "sand", "bunker", "water", "recovery", "trees", "woods", "native", "ob", "first_cut")


def _proj(lon0, lat0):
    kx = math.cos(math.radians(lat0)) * 111320.0
    ky = 110574.0

    def fwd(x, y):
        return (x - lon0) * kx, (y - lat0) * ky

    def inv(x, y):
        return x / kx + lon0, y / ky + lat0
    return fwd, inv


def _poly(ring, fwd):
    from shapely.geometry import Polygon
    try:
        g = Polygon([fwd(float(p[0]), float(p[1])) for p in ring])
        return g if g.is_valid else g.buffer(0)
    except Exception:                                    # noqa: BLE001
        return None


def _rings(g):
    """Hole-free exterior rings of g (polygons with holes are split through each hole)."""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import split
    if g is None or g.is_empty:
        return []
    if g.geom_type in ("MultiPolygon", "GeometryCollection"):
        return [r for p in g.geoms for r in _rings(p)]
    if g.geom_type != "Polygon":
        return []
    if not g.interiors:
        return [list(g.exterior.coords)[:-1]]
    c = Polygon(g.interiors[0]).representative_point()
    x0, y0, x1, y1 = g.bounds
    for cut in (LineString([(c.x, y0 - 1), (c.x, y1 + 1)]), LineString([(x0 - 1, c.y), (x1 + 1, c.y)])):
        parts = [p for p in split(g, cut).geoms if p.geom_type == "Polygon"]
        if len(parts) >= 2 and all(len(p.interiors) < len(g.interiors) for p in parts):
            return [r for p in parts for r in _rings(p)]
    return [list(g.exterior.coords)[:-1]]


def band_zones(zones_ll, band_yd, lie="fairway", min_m2=4.0):
    """New zone dicts (WGS84) of the band around the fairway zones of one hole's zones_ll."""
    from shapely.ops import unary_union
    fw_z = [z for z in zones_ll or [] if isinstance(z, dict) and z.get("lie") == "fairway" and len(z.get("poly") or []) >= 3]
    if not fw_z or band_yd <= 0:
        return []
    p0 = fw_z[0]["poly"][0]
    fwd, inv = _proj(float(p0[0]), float(p0[1]))
    fw = unary_union([g for g in (_poly(z["poly"], fwd) for z in fw_z) if g is not None and not g.is_empty])
    other = [g for g in (_poly(z["poly"], fwd) for z in zones_ll
                         if isinstance(z, dict) and z.get("lie") in KEEP_OUT and len(z.get("poly") or []) >= 3)
             if g is not None and not g.is_empty]
    band = fw.buffer(band_yd * YD, join_style=2, mitre_limit=2.0).difference(fw)
    if other:
        band = band.difference(unary_union(other))
    out = []
    for r in _rings(band):
        from shapely.geometry import Polygon
        if len(r) < 3 or Polygon(r).area < min_m2:
            continue
        out.append(dict(lie=lie, poly=[[round(a, 7), round(b, 7)] for a, b in (inv(x, y) for x, y in r)],
                        src=f"fairway_band+{band_yd:g}yd", p=1.0))
    return out


def widen_package(pkg, band_yd, lie="fairway", reframe=None, holes=None):
    """(new package with the band on every hole's fairway, number of band zones). holes: {ref: band_yd} overrides."""
    out = copy.deepcopy(pkg)
    n = 0
    for ref, h in out["holes"].items():
        b = band_yd if holes is None else holes.get(str(ref), band_yd)
        zs = h.get("zones_ll")
        if not zs or not b:
            continue
        add = band_zones(zs, b, lie)
        if add:
            h["zones_ll"] = list(zs) + add
            n += len(add)
    out.setdefault("stages", {})["fairway_band"] = f"fairway widened by a {band_yd:g}-yd {lie} band ({n} zones)"
    if reframe is not None and n:
        out = reframe(out)
    return out, n
