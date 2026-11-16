"""NAIP + 3DEP for one course, fast: the same files and georef.json as imagery/fetch_imagery.py (its own functions;
the same year rule), with the network reads in parallel: every NAIP year scored at once, the chosen year read in
strips by threads, the DEM alongside.

  fetch(bbox_wsen, out_dir, osm_fc=None, year="auto", margin=100) -> georef dict (also written to out_dir/georef.json)
"""
import datetime as dt
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(CD, "imagery"))
import fetch_imagery as fi  # noqa: E402
import naip_years as NY  # noqa: E402

GDAL_ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", VSI_CACHE="TRUE", GDAL_HTTP_MAX_RETRY="2")
STRIPS = 8
SCORE_YEARS = 4
SCORE_RES = 2.4          # metres for the year-scoring reads (naip_years' own is 1.2: 4x the pixels, same ranking signal)


def _item_grid(it):
    """(crs, pixel size) of a NAIP item from its STAC record (proj:code / proj:epsg, proj:transform): no file open
    (a first byte from the blob host is 0.4-0.9 s). None when the record lacks them."""
    from rasterio.crs import CRS
    p = it.properties
    code = p.get("proj:code") or (p.get("proj:epsg") and f"EPSG:{p['proj:epsg']}")
    t = p.get("proj:transform")
    if not code or not t:
        return None
    return CRS.from_string(code), abs(float(t[0]))


def read_year_ovr(its, bbox_snwe, res=SCORE_RES):
    """naip_years.read_year (the year's mosaic over the box at `res` m, Resampling.average) read from the COG
    overview whose pixel is closest to `res` without being coarser (0.6 m NAIP: the 4x level is exactly 2.4 m), all
    bands in one warp, each item opened once. GDAL's warp never uses overviews by itself: the full-resolution read
    was 4 years x ~40 MB, this is ~3 MB a year (Yorba Linda: 155 -> 13 MB, 14.8 -> 3.2 s; scores within 0.002,
    same year; 16 cached courses: same year, scores within 0.03)."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject, transform_bounds
    s, w, n, e = bbox_snwe
    g = _item_grid(its[0])
    if g is None:
        with rasterio.open(its[0].assets["image"].href) as s0:
            g = s0.crs, abs(s0.transform.a)
    crs, sres = g
    x0, y0, x1, y1 = transform_bounds("EPSG:4326", crs, w, s, e, n, densify_pts=21)
    W, H = int(math.ceil((x1 - x0) / res)), int(math.ceil((y1 - y0) / res))
    tr = rasterio.transform.from_origin(x0, y1, res, res)
    # NAIP overviews are the factors 2, 4, 8, ...: level i is factor 2 ** (i + 1); -1 is full resolution
    lvl = int(math.floor(math.log2(res / sres * 1.001))) - 1 if res > sres else -1
    out = None
    for it in its:
        try:
            src = rasterio.open(it.assets["image"].href, **({} if lvl < 0 else dict(overview_level=lvl)))
        except rasterio.errors.RasterioIOError:
            if lvl < 0:
                raise
            src = rasterio.open(it.assets["image"].href)             # no such overview: the warp reads full resolution
        with src:
            nb = min(src.count, 4)
            if out is None:
                out = np.zeros((nb, H, W), np.uint8)
            dst = np.zeros((nb, H, W), np.uint8)
            reproject(rasterio.band(src, list(range(1, nb + 1))), dst, src_nodata=0, dst_transform=tr, dst_crs=crs,
                      dst_nodata=0, resampling=Resampling.average)
            out[:nb] = np.where(dst > 0, dst, out[:nb])
    return out, crs, tr


def read_window(items, bounds, res):
    """the year's mosaic over bounds (x0, y0, x1, y1) in the items' CRS at their own pixel size: each item opened
    once, one read of the block-aligned window (all bands; GDAL_NUM_THREADS fetches and inflates the tiles in
    parallel, each tile once), pasted like rasterio.merge(method='first', nodata=0). Bit-identical to the strip read
    (_read_strips) on Yorba Linda 2018: 35 MB / 3.0 s instead of 99 MB / 3.9 s (the strips re-read tiles at their
    seams). None when an item's grid is not aligned to the output grid (then _read_strips resamples, as before)."""
    import rasterio
    from rasterio.windows import Window
    x0, y0, x1, y1 = bounds
    W, H = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))

    def one(it):
        with rasterio.Env(**dict(GDAL_ENV, GDAL_NUM_THREADS="ALL_CPUS")):
            with rasterio.open(it.assets["image"].href) as src:
                T = src.transform
                fc, fr = (x0 - T.c) / res, (T.f - y1) / res
                if abs(abs(T.a) - res) > 1e-9 or abs(fc - round(fc)) > 1e-6 or abs(fr - round(fr)) > 1e-6 or T.b or T.d:
                    return None
                c0, r0 = int(round(fc)), int(round(fr))
                ca, ra = max(c0, 0), max(r0, 0)
                cb, rb = min(c0 + W, src.width), min(r0 + H, src.height)
                if cb <= ca or rb <= ra:
                    return src.crs, None, None
                bh, bw = src.block_shapes[0]
                CA, RA = ca // bw * bw, ra // bh * bh
                CB, RB = min(-(-cb // bw) * bw, src.width), min(-(-rb // bh) * bh, src.height)
                a = src.read(window=Window(CA, RA, CB - CA, RB - RA))
                return src.crs, a[:, ra - RA:rb - RA, ca - CA:cb - CA], (ra - r0, ca - c0)
    with ThreadPoolExecutor(len(items)) as ex:
        parts = list(ex.map(one, items))
    if any(p is None for p in parts):
        return None
    crs = parts[0][0]
    parts = [p for p in parts if p[0] == crs and p[1] is not None]   # the first item's CRS only (as _read_strips)
    nb = max(p[1].shape[0] for p in parts)
    arr = np.zeros((nb, H, W), np.uint8)
    for _, a, (r, c) in parts:
        cur = arr[:a.shape[0], r:r + a.shape[1], c:c + a.shape[2]]
        m = (cur == 0) & (a != 0)
        cur[m] = a[m]
    return arr, rasterio.transform.from_origin(x0, y1, res, res), crs


def _read_strips(items, bounds, res):
    """the year's mosaic over bounds (x0, y0, x1, y1) in the items' CRS: horizontal strips read by threads"""
    import rasterio
    from rasterio.merge import merge
    x0, y0, x1, y1 = bounds
    rows = int(round((y1 - y0) / res))
    cuts = [y1 - res * int(round(rows * k / STRIPS)) for k in range(STRIPS + 1)]
    hrefs = [it.assets["image"].href for it in items]

    def one(k):
        with rasterio.Env(**GDAL_ENV):
            srcs = [rasterio.open(h) for h in hrefs]
            crs = srcs[0].crs
            srcs = [s for s in srcs if s.crs == crs]
            a, tr = merge(srcs, bounds=(x0, cuts[k + 1], x1, cuts[k]), res=res, nodata=0)
            for s in srcs:
                s.close()
            return a, tr, crs
    with ThreadPoolExecutor(STRIPS) as ex:
        parts = list(ex.map(one, range(STRIPS)))
    return np.concatenate([p[0] for p in parts], axis=1), parts[0][1], parts[0][2]


def fetch_naip(bbox, out_dir, lo_res=0.6, year="auto", osm=None, T=None):
    import rasterio
    from rasterio.warp import transform_bounds
    T = T if T is not None else {}
    s, w, n, e = bbox
    t0 = time.time()
    years = NY.list_years(bbox)
    if not years:
        raise RuntimeError("no NAIP items intersect the bbox")
    T["naip_list"] = round(time.time() - t0, 2)
    if hasattr(osm, "result"):          # a Future: the listing ran while the OSM features were still on their way
        t1 = time.time()
        osm = osm.result()
        T["naip_wait_osm"] = round(time.time() - t1, 2)
    t0 = time.time()
    scores = {}
    polys = NY.turf_polygons(osm) if (year == "auto" and osm) else None
    if polys is not None and not any(polys.values()):
        year = "latest"                 # no OSM turf to score on (unmapped course): the newest covering year, no reads
    cov = [y for y in years if y["coverage"] > 0.9] or years
    years = cov[-SCORE_YEARS:]          # only the newest few years compete (older flights predate renovations anyway)
    if year == "auto" and osm:

        def sc(y):
            try:
                with rasterio.Env(**GDAL_ENV):
                    arr, crs, tr = read_year_ovr(y["items"], bbox)
                return y["year"], NY._score_array(arr, crs, tr, polys, {})
            except Exception as ex:                                  # noqa: BLE001
                return y["year"], ex
        with ThreadPoolExecutor(max(1, len(years))) as ex:
            scores = dict(ex.map(sc, years))

    def scorer(y):
        v = scores[y["year"]]
        if isinstance(v, Exception):
            raise v
        return v
    row, selection = fi.choose_year(years, year, osm, bbox, None, scorer=scorer if scores else None)
    T["naip_year_scoring"] = round(time.time() - t0, 2)
    t0 = time.time()
    yr, its = row["year"], row["items"]
    g = _item_grid(its[0])
    if g is None:
        with rasterio.Env(**GDAL_ENV):
            with rasterio.open(its[0].assets["image"].href) as s0:
                g = s0.crs, abs(s0.transform.a)
    crs, res = g
    b = transform_bounds("EPSG:4326", crs, w, s, e, n, densify_pts=21)
    x0, y0 = math.floor(b[0] / res) * res, math.floor(b[1] / res) * res
    x1, y1 = math.ceil(b[2] / res) * res, math.ceil(b[3] / res) * res
    got = read_window(its, (x0, y0, x1, y1), res)
    arr, tr, crs = got if got is not None else _read_strips(its, (x0, y0, x1, y1), res)
    T["naip_read"] = round(time.time() - t0, 2)
    t0 = time.time()
    nb = arr.shape[0]
    kind, mb_rgb = fi.write_cog(os.path.join(out_dir, "naip_rgb.tif"), arr[:3], crs, tr, jpeg_quality=90)
    files, sizes = {"rgb": "naip_rgb.tif"}, {"naip_rgb.tif": mb_rgb}
    if nb >= 4:
        _, mb = fi.write_cog(os.path.join(out_dir, "naip_nir.tif"), arr[3:4], crs, tr, jpeg_quality=92)
        files["nir"], sizes["naip_nir.tif"] = "naip_nir.tif", mb
    lo = fi.write_lo(arr, tr, lo_res, out_dir, "naip")
    T["naip_write"] = round(time.time() - t0, 2)
    return dict(source="USDA NAIP via Microsoft Planetary Computer (collection 'naip')", year=yr,
                years_available=[y["year"] for y in years], acquired=sorted({it.datetime.date().isoformat() for it in its}),
                items=[it.id for it in its], selection=selection, gsd_m=its[0].properties.get("gsd"), resolution_m=round(res, 4),
                bands=["red", "green", "blue"] + (["nir"] if nb >= 4 else []), crs=crs.to_string(), epsg=crs.to_epsg(),
                width=int(arr.shape[2]), height=int(arr.shape[1]), transform=fi.tf_list(tr), bounds_crs=[x0, y0, x1, y1],
                files=files, format=kind, lo=lo, sizes_mb=sizes, license="Public domain (USDA FSA)")


def fetch(bbox_wsen, out_dir, osm_fc=None, year="auto", margin=100.0, label=None, quiet=True):
    """bbox_wsen: the course bbox [W, S, E, N] (course.json); osm_fc: the OSM FeatureCollection, or a Future of it
    (needed only for the year scoring, after the NAIP listing). -> (georef dict, timings)"""
    if quiet:
        fi.log = lambda *a: None
    os.makedirs(out_dir, exist_ok=True)
    w, s, e, n = bbox_wsen
    bbox = (s, w, n, e)
    padded = fi.pad_bbox(bbox, margin)
    lat, lon = (padded[0] + padded[2]) / 2, (padded[1] + padded[3]) / 2
    T = {}
    meta = dict(course=label, bbox_wgs84_snwe=list(bbox), bbox_source="--bbox", margin_m=margin, request=None,
                padded_bbox_wgs84_snwe=list(padded),
                fetched_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                transform_convention="GDAL/affine: x = c + a*col + b*row, y = f + d*col + e*row "
                                     "(col,row of the pixel's top-left corner; +0.5 for centres)")
    epsg0 = fi.utm_epsg(lat, lon)

    def dem():
        t0 = time.time()
        try:
            return fi.fetch_dem(padded, out_dir, epsg0)
        finally:
            T["dem"] = round(time.time() - t0, 2)

    def naip():
        return fetch_naip(padded, out_dir, 0.6, year, osm_fc, T)
    with ThreadPoolExecutor(2) as ex:
        fd, fn = ex.submit(dem), ex.submit(naip)
        try:
            meta["imagery"] = fn.result()
        except Exception as ex_:                                     # noqa: BLE001
            meta["naip_error"] = repr(ex_)[:800]
        try:
            meta["dem"] = fd.result()
        except Exception as ex_:                                     # noqa: BLE001
            meta["dem_error"] = repr(ex_)[:800]
    json.dump(meta, open(os.path.join(out_dir, "georef.json"), "w"), indent=1)
    return meta, T
