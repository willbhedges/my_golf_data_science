"""False water: paved paths / roads / bare ground the automatic water layer calls water, and piped OSM streams.

Three mapper agents (course_data/mapper/{rivercut,gustin,la_nickell}) erased automatic water that lies on cart
paths and roads: the NDWI open-water rule (layers.water_mask: green-NIR > 0.05 and NDVI < 0.05) also fires on
asphalt / concrete, whose NIR is as high as its green, and the OSM stream corridor was drawn across a fairway
where the stream is piped. The rules here are general (no course is named or tuned on):

  vision water (a connected component of the vision water layer, OSM water polygons never touched):
    road      >= 50 % of it within an OSM highway=* / golf=cartpath line's paved width (+3 m), elongated
              (skeleton length >= 4 x mean width) and >= 40 % of it paved (below)          -> not water
    strip     thin (mean width <= 9 m), >= 25 m long, elongated, >= 60 % paved and no channel in the DTM (its
              median ground is not >= 0.3 m below the ground 3-8 m around it)                -> not water
    raised    >= 60 % paved and its median ground >= 0.3 m ABOVE the ground around it (water cannot stand
              above its banks)                                                               -> not water
    cells     what is left: cells on an OSM path / road's paved width (+1 m) that are paved -> not water
              (a cart path through a creek corridor)
  paved = bright and bare in every NAIP year: NIR >= 0.25 and NDVI < 0.15 (open water is dark in NIR; turf and
  creek-bank vegetation have NDVI well above 0.15).

  OSM streams (waterway=stream/ditch/drain/canal lines) are not surface water where
    tagged    tunnel=* (yes, culvert, ...), covered=yes or location=underground
    crossing  they cross an OSM fairway / green / tee and the DTM shows no channel there (cross-section depth:
              median ground 7-12 m either side minus the lowest ground within 3 m < 0.3 m) - a culvert /
              pipe under the turf
  The piped pieces (buffered by the stream's half width + 1 m), minus every OSM water polygon (ponds stay), are
  removed from the hole's water zones.

Used by layers.water_mask (new vision layers), gapfill.gapfill (every package build: the committed vision layer
and the OSM stream zones are filtered there, so re-packaging is enough) and platform/rebuild_tees_trees.py
--layers water (error budget). Tests: test_water_filter.py.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# paved half widths (m) of an OSM highway line by class; tolerance added on top
ROAD_HALF_M = dict(motorway=12.0, trunk=10.0, primary=9.0, secondary=7.5, tertiary=6.0, unclassified=4.0,
                   residential=4.5, living_street=4.0, service=3.0, track=2.0, motorway_link=5.0, trunk_link=5.0,
                   primary_link=5.0, secondary_link=4.5, tertiary_link=4.0, path=1.5, footway=1.5, cycleway=1.5,
                   bridleway=1.5, pedestrian=2.5, steps=1.5, golf_cart=1.5)
ROAD_HALF_DEFAULT = 3.0
CARTPATH_HALF = 1.5
TOL_COMPONENT_M = 3.0
TOL_CELL_M = 1.0
NIR_PAVED = 0.25
NDVI_PAVED = 0.15
ROAD_SHARE = 0.5
ROAD_PAVED = 0.4
ELONG = 4.0
STRIP_WIDTH_M = 9.0
STRIP_LEN_M = 25.0
STRIP_PAVED = 0.6
CHANNEL_DEPTH_M = 0.3            # component ground this far below its surroundings = a channel / pond basin
RAISED_M = 0.3
MIN_PART_M2 = 40.0
STREAMS = ("stream", "ditch", "drain", "canal")
STREAM_HALF_M = dict(stream=2.7, ditch=1.8, drain=1.8, canal=5.5)
PIPE_DEPTH_M = 0.3
STEP_M = 5.0


# --------------------------------------------------------------------------- OSM tags
def is_piped(props):
    """An OSM waterway that runs underground by its tags (tunnel=* / covered=yes / location=underground)."""
    p = props or {}
    return (str(p.get("tunnel", "no")).strip().lower() not in ("", "no")
            or str(p.get("covered", "no")).strip().lower() == "yes"
            or str(p.get("location", "")).strip().lower() == "underground")


def road_half_m(props):
    """Paved half width (m) of an OSM line that is a road / path / cart path, else None."""
    p = props or {}
    if p.get("golf") == "cartpath":
        return CARTPATH_HALF
    hw = p.get("highway")
    if not hw or hw in ("proposed", "construction", "abandoned", "razed"):
        return None
    try:
        w = float(str(p.get("width", "")).split()[0])
        if 1.0 <= w <= 40.0:
            return w / 2.0
    except (ValueError, IndexError):
        pass
    return ROAD_HALF_M.get(hw, ROAD_HALF_DEFAULT)


def road_lines(fc):
    """[(shapely line (WGS84), half width m)] of every OSM highway=* / golf=cartpath line."""
    from shapely.geometry import shape
    out = []
    for f in fc.get("features", []):
        g = f.get("geometry")
        if not g or g.get("type") not in ("LineString", "MultiLineString"):
            continue
        hw = road_half_m(f.get("properties"))
        if hw is not None:
            out.append((shape(g), hw))
    return out


# --------------------------------------------------------------------------- rasters
def road_distance(S, roads):
    """-> grid of (distance to the nearest road's paved edge) in m: <= 0 on the pavement."""
    out = np.full((S.H, S.W), np.inf, np.float32)
    by = {}
    for g, hw in roads:
        by.setdefault(hw, []).append(g)
    for hw, gs in by.items():
        m = S.rasterize(gs)
        if m.any():
            out = np.minimum(out, ndimage.distance_transform_edt(~m) * S.res - hw)
    return out


def paved_mask(S):
    """Bright and bare in every NAIP year (asphalt, concrete, bare soil, dry sand): not open water."""
    if not S.naip:
        return np.zeros((S.H, S.W), bool)
    out = np.ones((S.H, S.W), bool)
    for _, b in S.naip:
        nir, red = b[..., 3], b[..., 0]
        nd = (nir - red) / (nir + red + 1e-6)
        out &= np.nan_to_num(nir, nan=0.0) >= NIR_PAVED
        out &= np.nan_to_num(nd, nan=1.0) < NDVI_PAVED
    return out


def dtm_grid(S):
    """The stack's DTM, else the package DEM (course_data/packages/<slug>/imagery/dem.tif) on the stack grid."""
    d = S.layers.get("dtm")
    if d is not None and np.isfinite(d).mean() > 0.5:
        return d
    cands = []
    cd = getattr(S, "course_dir", None)
    if cd:
        cands.append(os.path.join(cd, "..", "imagery", "dem.tif"))
    slug = getattr(S, "slug", None)
    if slug:
        cands.append(os.path.join(ROOT, "course_data", "packages", slug, "imagery", "dem.tif"))
    for p in cands:
        if os.path.exists(p):
            try:
                import rasterio
                from rasterio.warp import Resampling, reproject
                out = np.full((S.H, S.W), np.nan, np.float32)
                with rasterio.open(p) as src:
                    a = src.read(1).astype(np.float32)
                    if src.nodata is not None and np.isfinite(src.nodata):
                        a[a == src.nodata] = np.nan
                    reproject(a, out, src_transform=src.transform, src_crs=src.crs, dst_transform=S.transform,
                              dst_crs=S.crs, resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
                if np.isfinite(out).mean() > 0.5:
                    return out
            except Exception:                                     # noqa: BLE001
                continue
    return None


def _skeleton_len(m):
    try:
        from skimage.morphology import skeletonize
        return max(int(skeletonize(m).sum()), 1)
    except ImportError:                                           # width ~ 2 x mean inner distance
        e = ndimage.distance_transform_edt(m)
        w = max(2.0 * float(e[m].mean()), 1.0)
        return max(int(m.sum() / w), 1)


def component_stats(m, paved, road_d, dtm, res=1.0):
    """One component (bool crop with >= 8 cells margin) -> dict(area, width, length, road, paved, depth)."""
    a = int(m.sum())
    sk = _skeleton_len(m)
    st = dict(area=a * res * res, length=sk * res, width=a / sk * res,
              road=float((road_d[m] <= TOL_COMPONENT_M).mean()) if road_d is not None else 0.0,
              paved=float(paved[m].mean()), depth=None)
    if dtm is not None:
        ring = ndimage.binary_dilation(m, iterations=8) & ~ndimage.binary_dilation(m, iterations=3)
        dm, dr = dtm[m], dtm[ring]
        if np.isfinite(dm).mean() > 0.5 and np.isfinite(dr).mean() > 0.5:
            st["depth"] = float(np.nanmedian(dr) - np.nanmedian(dm))      # > 0: lower than its surroundings
    return st


def verdict(st):
    """-> reason the component is not water ('road' | 'strip' | 'raised') or None (kept)."""
    elong = st["length"] >= ELONG * st["width"]
    dep = st["depth"]
    if st["road"] >= ROAD_SHARE and elong and st["paved"] >= ROAD_PAVED:
        return "road"
    if (st["width"] <= STRIP_WIDTH_M and st["length"] >= STRIP_LEN_M and elong and st["paved"] >= STRIP_PAVED
            and (dep is None or dep < CHANNEL_DEPTH_M)):
        return "strip"
    if st["paved"] >= STRIP_PAVED and dep is not None and dep <= -RAISED_M:
        return "raised"
    return None


def false_water(water, paved, road_d=None, dtm=None, keep=None, res=1.0):
    """water (bool grid) -> (cleaned water, [component reports]). `keep` (OSM water polygons) is never removed and
    is not part of the components judged."""
    keep = np.zeros_like(water) if keep is None else keep
    cand = water & ~keep
    lab, n = ndimage.label(cand)
    drop = np.zeros_like(water)
    rep = []
    H, W = water.shape
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        r0, r1 = max(sl[0].start - 10, 0), min(sl[0].stop + 10, H)
        c0, c1 = max(sl[1].start - 10, 0), min(sl[1].stop + 10, W)
        m = lab[r0:r1, c0:c1] == i
        if m.sum() * res * res < MIN_PART_M2:
            continue
        st = component_stats(m, paved[r0:r1, c0:c1], None if road_d is None else road_d[r0:r1, c0:c1],
                             None if dtm is None else dtm[r0:r1, c0:c1], res)
        why = verdict(st)
        if why:
            drop[r0:r1, c0:c1] |= m
            rep.append(dict(st, reason=why, rc=[int((r0 + r1) / 2), int((c0 + c1) / 2)]))
    out = water & ~drop
    if road_d is not None:                                         # paved road cells inside what is kept
        cell = (road_d <= TOL_CELL_M) & paved & out & ~keep
        if cell.any():
            out &= ~cell
            rep.append(dict(reason="cells", area=float(cell.sum() * res * res)))
        # fragments the cell rule cut off
        lab, n = ndimage.label(out & ~keep)
        if n:
            sz = ndimage.sum(np.ones(lab.shape), lab, np.arange(1, n + 1)) * res * res
            touch = np.unique(lab[ndimage.binary_dilation(cell) & (lab > 0)])
            small = [i for i in touch if sz[i - 1] < MIN_PART_M2]
            if small:
                out &= ~np.isin(lab, small)
    return out, rep


def clean_grid(S, fc, water, keep=None, dtm="auto"):
    """layers.water_mask hook: the stack + OSM FeatureCollection -> (cleaned water mask, reports)."""
    d = dtm_grid(S) if isinstance(dtm, str) else dtm
    roads = road_lines(fc)
    rd = road_distance(S, roads) if roads else None
    return false_water(water, paved_mask(S), rd, d, keep=keep, res=S.res)


def _reasons(rep):
    out = {}
    for r in rep:
        out[r["reason"]] = round(out.get(r["reason"], 0) + r.get("area", 0))
    return out


# --------------------------------------------------------------------------- piped OSM streams
class _DEM:
    """Point sampler of a DEM GeoTIFF in its own (metric) CRS."""

    def __init__(self, path):
        import rasterio
        with rasterio.open(path) as src:
            self.a = src.read(1).astype(np.float32)
            if src.nodata is not None and np.isfinite(src.nodata):
                self.a[self.a == src.nodata] = np.nan
            self.inv = ~src.transform
            self.crs = src.crs

    def at(self, xy):
        xy = np.atleast_2d(xy)
        c, r = self.inv * (xy[:, 0], xy[:, 1])
        c, r = np.floor(c).astype(int), np.floor(r).astype(int)
        ok = (r >= 0) & (r < self.a.shape[0]) & (c >= 0) & (c < self.a.shape[1])
        out = np.full(len(xy), np.nan, np.float32)
        out[ok] = self.a[r[ok], c[ok]]
        return out


def channel_depth(sample, p, t):
    """Cross-section at p (x, y m) across the unit direction t: median ground 7-12 m either side minus the lowest
    ground within 3 m (m; ~0 = no channel), or None without enough DEM. `sample(xy)` -> heights."""
    n = np.array([-t[1], t[0]])
    near = np.arange(-3.0, 3.01, 1.0)
    far = np.r_[np.arange(-12.0, -6.99, 1.0), np.arange(7.0, 12.01, 1.0)]
    zn = sample(p + near[:, None] * n)
    zf = sample(p + far[:, None] * n)
    if not np.isfinite(zn).any() or np.isfinite(zf).sum() < 4:
        return None
    return float(np.nanmedian(zf) - np.nanmin(zn))


def _is_water_poly(p):
    return (p.get("golf") in ("water_hazard", "lateral_water_hazard") or p.get("natural") == "water"
            or bool(p.get("water")) or p.get("landuse") in ("reservoir", "basin"))


def piped_streams(osm_fc, dem_path=None):
    """OSM stream pieces that are not surface water -> (list of WGS84 polygons, report). Tagged tunnels always;
    with a DEM, the 5 m pieces over an OSM fairway / green / tee whose cross-section shows no channel
    (depth < PIPE_DEPTH_M). Buffered by the stream's half width + 1 m; OSM water polygons are cut out (kept)."""
    from pyproj import CRS, Transformer
    from shapely.geometry import LineString, Point, shape
    from shapely.ops import transform, unary_union
    feats = [f for f in osm_fc.get("features", []) if f.get("geometry")]
    streams = [f for f in feats if (f.get("properties") or {}).get("waterway") in STREAMS
               and f["geometry"]["type"] in ("LineString", "MultiLineString")]
    rep = dict(tagged=0, crossing_m=0.0, dem=bool(dem_path and os.path.exists(dem_path)))
    if not streams:
        return [], rep
    D = _DEM(dem_path) if rep["dem"] else None
    if D is not None and D.crs is not None and CRS.from_user_input(D.crs).is_projected:
        crs = CRS.from_user_input(D.crs)
    else:
        c = shape(streams[0]["geometry"]).centroid
        crs = CRS.from_epsg((32600 if c.y >= 0 else 32700) + int((c.x + 180) // 6) + 1)
    fw = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    bw = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    to_m = lambda g: transform(fw.transform, g)                   # noqa: E731
    to_ll = lambda g: transform(bw.transform, g)                  # noqa: E731
    turf = [to_m(shape(f["geometry"])).buffer(0) for f in feats
            if f["geometry"]["type"] in ("Polygon", "MultiPolygon")
            and (f.get("properties") or {}).get("golf") in ("fairway", "green", "tee")]
    water = [shape(f["geometry"]).buffer(0) for f in feats
             if f["geometry"]["type"] in ("Polygon", "MultiPolygon") and _is_water_poly(f.get("properties") or {})]
    T = unary_union(turf) if turf else None
    pieces = []
    for f in streams:
        p = f["properties"]
        half = STREAM_HALF_M.get(p.get("waterway"), 2.7)
        try:
            half = max(float(str(p.get("width", "")).split()[0]) / 2.0, 1.4)
        except (ValueError, IndexError):
            pass
        gm = to_m(shape(f["geometry"]))
        if is_piped(p):
            pieces.append(gm.buffer(half + 1.0, cap_style=2))
            rep["tagged"] += 1
            continue
        if T is None or D is None or not gm.intersects(T):
            continue
        for ln in getattr(gm, "geoms", [gm]):
            k = max(int(ln.length // STEP_M), 1)
            for j in range(k):
                pa = np.array(ln.interpolate(j * ln.length / k).coords[0])
                pb = np.array(ln.interpolate((j + 1) * ln.length / k).coords[0])
                mid, t = (pa + pb) / 2, pb - pa
                if not np.linalg.norm(t) or not T.contains(Point(mid)):
                    continue
                d = channel_depth(D.at, mid, t / np.linalg.norm(t))
                if d is not None and d < PIPE_DEPTH_M:
                    pieces.append(LineString([pa, pb]).buffer(half + 1.0, cap_style=2))
                    rep["crossing_m"] += float(np.linalg.norm(t))
    rep["crossing_m"] = round(rep["crossing_m"], 1)
    if not pieces:
        return [], rep
    out = to_ll(unary_union(pieces))
    if water:
        out = out.difference(unary_union(water))
    return [g for g in getattr(out, "geoms", [out]) if not g.is_empty and g.area > 0], rep


def subtract_from_hole(h, piped_ll, srcs=None):
    """Remove the piped stream polygons from a package hole's water zones_ll (every src unless `srcs`).
    -> number of zones changed."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    if not piped_ll or not h.get("zones_ll"):
        return 0
    P = unary_union(piped_ll)
    out, n = [], 0
    for z in h["zones_ll"]:
        if z.get("lie") != "water" or (srcs and not any(str(z.get("src", "")).startswith(s) for s in srcs)):
            out.append(z)
            continue
        try:
            g = Polygon(z["poly"]).buffer(0)
        except Exception:                                         # noqa: BLE001
            out.append(z)
            continue
        if not g.intersects(P):
            out.append(z)
            continue
        n += 1
        r = g.difference(P)
        for q in getattr(r, "geoms", [r]):
            if q.geom_type != "Polygon" or q.is_empty or q.area < g.area * 1e-3:
                continue
            nz = dict(z, poly=[[round(float(a), 7), round(float(b), 7)] for a, b in list(q.exterior.coords)[:-1]])
            if "area_yd2" in z and g.area > 0:
                nz["area_yd2"] = round(z["area_yd2"] * q.area / g.area)
            nz["piped_cut"] = True
            out.append(nz)
    h["zones_ll"] = out
    return n


def _vision_slug(pkg, slug):
    import gapfill as G
    c = pkg.get("course") or {}
    return G.resolve_slug(slug or c.get("slug") or pkg.get("slug"), c.get("center"))


def filter_package(pkg, slug=None, img_dir=None, min_yd2=150.0):
    """Package (course_package/1 dict, edited in place) -> report. Removes from the holes' water zones_ll:
    the piped OSM stream pieces (every water src; OSM water polygons are cut out of the pieces first) and the
    false vision water (water_filter rules on the vision water zones, judged course-wide on the vision stack
    grid). Zone pieces < min_yd2 left by a cut are dropped. The yard-frame `zones` are NOT refreshed here
    (gapfill / the caller reframes)."""
    from shapely.geometry import Polygon
    from shapely.ops import transform, unary_union
    slug = slug or pkg.get("slug") or (pkg.get("course") or {}).get("slug")
    pdir = os.path.join(ROOT, "course_data", "packages", slug or "_none_")
    osm_p = ((pkg.get("sources") or {}).get("osm") or {}).get("file")
    osm_p = os.path.join(ROOT, osm_p) if osm_p and not os.path.isabs(osm_p) else osm_p
    if not osm_p or not os.path.exists(osm_p):
        osm_p = os.path.join(pdir, "raw", "osm.geojson")
    rep = dict(piped=None, vision=None)
    if not os.path.exists(osm_p):
        rep["skipped"] = "no raw/osm.geojson"
        return rep
    with open(osm_p) as fh:
        osm = json.load(fh)
    dem = os.path.join(img_dir or os.path.join(pdir, "imagery"), "dem.tif")
    piped, prep = piped_streams(osm, dem if os.path.exists(dem) else None)
    n = sum(subtract_from_hole(h, piped) for h in pkg["holes"].values()) if piped else 0
    rep["piped"] = dict(prep, zones_cut=n)
    # vision water, course-wide on the stack grid
    vz = [(h, z) for h in pkg["holes"].values() for z in h.get("zones_ll") or []
          if z.get("lie") == "water" and str(z.get("src", "")).startswith("vision")]
    vslug = _vision_slug(pkg, slug)
    if not vz:
        rep["vision"] = "no vision water"
    elif not os.path.exists(os.path.join(HERE, vslug or "_none_", "raw", "meta.json")):
        rep["vision"] = f"skipped: no course_data/vision_any/{vslug}/raw stack"
    else:
        import layers as L
        S = L.Stack.load(vslug, os.path.dirname(osm_p))
        M, _ = L.osm_masks(S, osm)
        W = S.rasterize([Polygon(z["poly"]).buffer(0) for _, z in vz]) & ~M["water"]
        W2, crep = clean_grid(S, osm, W, keep=M["water"])
        gone = W & ~W2
        rep["vision"] = dict(water_m2=float(W.sum() * S.res ** 2), removed_m2=float(gone.sum() * S.res ** 2),
                             reasons=_reasons(crep))
        if gone.any():
            G = unary_union([g.buffer(0) for g in L.mask_to_polys(S, gone, min_yd2=0, simplify_yd=0.5)]
                            or [Polygon()])
            from pyproj import CRS, Transformer
            lon, lat = np.asarray(vz[0][1]["poly"][0], float)
            utm = CRS.from_epsg((32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1)
            fw = Transformer.from_crs("EPSG:4326", utm, always_xy=True).transform
            bw = Transformer.from_crs(utm, "EPSG:4326", always_xy=True).transform
            Gm = transform(fw, G).buffer(0.5)
            for h in pkg["holes"].values():
                out = []
                for z in h.get("zones_ll") or []:
                    if not (z.get("lie") == "water" and str(z.get("src", "")).startswith("vision")):
                        out.append(z)
                        continue
                    g = transform(fw, Polygon(z["poly"]).buffer(0))
                    if not g.intersects(Gm):
                        out.append(z)
                        continue
                    r = g.difference(Gm)
                    for q in getattr(r, "geoms", [r]):
                        a = q.area / 0.9144 ** 2
                        if q.geom_type != "Polygon" or q.is_empty or a < min_yd2:
                            continue
                        ll = transform(bw, q.simplify(0.5))
                        out.append(dict(z, poly=[[round(float(x), 7), round(float(y), 7)]
                                                 for x, y in list(ll.exterior.coords)[:-1]],
                                        area_yd2=round(a), water_filter_cut=True))
                h["zones_ll"] = out
    pkg.setdefault("sources", {})["water_filter"] = dict(
        rule="vision_any/water_filter.py: vision water on OSM roads / paths (paved), thin paved strips with no DTM "
             "channel, raised bare ground, paved path cells; OSM streams tagged tunnel / covered or crossing "
             "fairway / green / tee with no DTM channel", **{k: v for k, v in rep.items() if v is not None})
    return rep
