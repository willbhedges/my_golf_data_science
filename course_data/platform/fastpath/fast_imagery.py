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
                    arr, crs, tr = NY.read_year(y["items"], bbox, res=SCORE_RES)
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
    with rasterio.Env(**GDAL_ENV):
        with rasterio.open(its[0].assets["image"].href) as s0:
            crs, res = s0.crs, abs(s0.transform.a)
    b = transform_bounds("EPSG:4326", crs, w, s, e, n, densify_pts=21)
    x0, y0 = math.floor(b[0] / res) * res, math.floor(b[1] / res) * res
    x1, y1 = math.ceil(b[2] / res) * res, math.ceil(b[3] / res) * res
    arr, tr, crs = _read_strips(its, (x0, y0, x1, y1), res)
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
    """bbox_wsen: the course bbox [W, S, E, N] (course.json). -> (georef dict, timings)"""
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
