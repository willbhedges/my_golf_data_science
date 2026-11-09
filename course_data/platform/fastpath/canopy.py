"""Trees from Meta / WRI global canopy height (1 m, dataforgood-fb-data COGs) instead of 3DEP lidar point clouds:
one windowed COG read per course (seconds; no PDAL), the product's tree rule on it, polygons into the package.

  fetch(bbox_wsen, out_dir)        -> out_dir/chm_meta.tif (uint8 metres, UTM 1 m grid), seconds
  add_trees(package, cache)        -> n zones added (lie 'recovery', src 'meta:chm>=3m'): the hole's zones_ll
Rule (not tuned on the truth courses: the lidar layer's own clump size, and its +1 m edge): canopy = height >= 3 m,
clumps < 100 m2 dropped, edge + 1 m.
"""
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
META_CHM = "https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/chm/{qk}.tif"
HEIGHT_M, MIN_AREA_M2, EDGE_M = 3.0, 100.0, 1.0
SRC = "meta:chm>=3m"


def quadkeys(ll_bbox, z=9):
    w, s, e, n = ll_bbox

    def tile(lon, lat):
        x = (lon + 180) / 360 * 2 ** z
        y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2 ** z
        return int(x), int(y)
    x0, y0 = tile(w, n)
    x1, y1 = tile(e, s)
    out = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            q = ""
            for i in range(z, 0, -1):
                m = 1 << (i - 1)
                q += str((1 if x & m else 0) + (2 if y & m else 0))
            out.append(q)
    return out


def fetch(bbox_wsen, out_dir, margin_m=160.0):
    import rasterio
    from rasterio.crs import CRS
    from rasterio.enums import Resampling
    from rasterio.warp import reproject, transform_bounds
    t0 = time.time()
    path = os.path.join(out_dir, "chm_meta.tif")
    if os.path.exists(path):
        return path, 0.0
    os.makedirs(out_dir, exist_ok=True)
    w, s, e, n = bbox_wsen
    dy = margin_m / 111320.0
    dx = dy / math.cos(math.radians((s + n) / 2))
    w, s, e, n = w - dx, s - dy, e + dx, n + dy
    zone = int((w + e) / 2 // 6 + 31)
    crs = CRS.from_epsg(32600 + zone)
    x0, y0, x1, y1 = transform_bounds("EPSG:4326", crs, w, s, e, n, densify_pts=21)
    x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)
    W, H = int(x1 - x0), int(y1 - y0)
    tr = rasterio.transform.from_origin(x0, y1, 1.0, 1.0)
    arr = np.full((H, W), np.nan, np.float32)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", AWS_NO_SIGN_REQUEST="YES", VSI_CACHE="TRUE",
                      GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        for qk in quadkeys((w, s, e, n)):
            with rasterio.open("/vsicurl/" + META_CHM.format(qk=qk)) as src:
                tmp = np.full((H, W), np.nan, np.float32)
                reproject(rasterio.band(src, 1), tmp, src_nodata=src.nodata, dst_nodata=np.nan, dst_transform=tr,
                          dst_crs=crs, resampling=Resampling.bilinear)
            f = np.isnan(arr) & np.isfinite(tmp)
            arr[f] = tmp[f]
    q = np.where(np.isfinite(arr), np.clip(np.round(arr), 0, 254), 255).astype(np.uint8)
    with rasterio.open(path, "w", driver="GTiff", height=H, width=W, count=1, dtype="uint8", crs=crs, transform=tr,
                       nodata=255, compress="deflate") as dst:
        dst.write(q, 1)
    return path, round(time.time() - t0, 2)


def tree_polygons(chm_path):
    """[shapely polygons in lon / lat] of the tree rule on the canopy raster"""
    import rasterio
    from rasterio import features
    from scipy import ndimage
    from shapely.geometry import shape
    from shapely.ops import transform as stransform
    from pyproj import Transformer
    with rasterio.open(chm_path) as ds:
        a = ds.read(1)
        tr, crs, nd = ds.transform, ds.crs, ds.nodata
    res = abs(tr.a)
    m = (a >= HEIGHT_M) & (a != (255 if nd is None else nd))
    lab, k = ndimage.label(m)
    if k:
        sizes = ndimage.sum(m, lab, range(1, k + 1))
        m = np.isin(lab, 1 + np.flatnonzero(sizes >= MIN_AREA_M2 / res ** 2))
    if EDGE_M > 0:
        m = ndimage.distance_transform_edt(~m) * res <= EDGE_M
    to_ll = Transformer.from_crs(crs, "EPSG:4326", always_xy=True).transform
    out = []
    for g, v in features.shapes(m.astype(np.uint8), mask=m, transform=tr):
        p = shape(g).simplify(1.5)
        if p.is_valid and p.area >= MIN_AREA_M2:
            out.append(stransform(to_ll, p))
    return out


def _holefree(g, min_hole_m2=150.0):
    """polygon -> simple polygons (no interior rings): small pockets filled, big clearings cut open with a slit"""
    from shapely.geometry import Polygon
    from shapely.geometry import box as sbox
    keep = [r for r in g.interiors if Polygon(r).area * 111320.0 ** 2 >= min_hole_m2]
    if not keep:
        return [Polygon(g.exterior)]
    g = Polygon(g.exterior, keep)
    out, todo = [], [g]
    while todo:
        p = todo.pop()
        if p.is_empty:
            continue
        if p.geom_type != "Polygon":
            todo += list(p.geoms)
            continue
        if not p.interiors:
            out.append(p)
            continue
        cx = Polygon(p.interiors[0]).centroid.x
        x0, y0, x1, y1 = p.bounds
        todo += [p.intersection(sbox(x0, y0, cx, y1)), p.intersection(sbox(cx, y0, x1, y1))]
    return [q for q in out if q.area > 0]


def find_chm(package, cache):
    slug = package.get("slug") or (package.get("course") or {}).get("slug")
    for p in (os.path.join(cache, "packages", slug, "canopy", "chm_meta.tif"),
              os.path.join(CD, "vision_any", slug, "raw", "chm_meta.tif")):
        if os.path.exists(p):
            return p
    return None


def add_trees(package, cache, chm=None):
    from shapely.geometry import LineString
    chm = chm or find_chm(package, cache)
    if not chm:
        return 0
    polys = tree_polygons(chm)
    from shapely.strtree import STRtree
    tree = STRtree(polys)
    n = 0
    for h in package["holes"].values():
        line = h.get("hole_line_ll") or [h.get("tee_ll"), h.get("green_ll")]
        line = [p for p in line if p]
        tees = [t["tee_ll"] for t in (h.get("tees") or {}).values() if t.get("tee_ll")]
        if len(line) < 2:
            continue
        lat = line[0][1]
        k = math.cos(math.radians(lat))
        corr = LineString([(x * k, y) for x, y in (tees[:1] + line)]).buffer(190 * 0.9144 / 111320.0)
        h["zones_ll"] = [z for z in (h.get("zones_ll") or []) if z.get("src") != SRC]
        from shapely.affinity import scale
        from shapely.ops import unary_union
        near = [scale(polys[int(i)], xfact=k, yfact=1, origin=(0, 0))
                for i in tree.query(LineString([(x, y) for x, y in (tees[:1] + line)]).buffer(0.004))]
        near = [p for p in near if p.intersects(corr)]
        if not near:
            continue
        # one merged, clipped, simplified tree area per hole: a few polygons instead of hundreds (the solve's lie
        # lookup is per polygon); pockets under 150 m2 inside the canopy are closed
        u = unary_union(near).intersection(corr).simplify(2.0 / 111320.0)
        for g in (u.geoms if hasattr(u, "geoms") else [u]):
            if g.geom_type != "Polygon" or g.area * 111320.0 ** 2 < MIN_AREA_M2:
                continue
            for part in _holefree(g):
                h["zones_ll"].append(dict(lie="recovery", src=SRC,
                                          poly=[[round(x / k, 7), round(y, 7)] for x, y in part.exterior.coords]))
                n += 1
    package.setdefault("stages", {})["trees_meta"] = f"ok: {n} tree zones from Meta canopy height ({os.path.basename(chm)})"
    return n
