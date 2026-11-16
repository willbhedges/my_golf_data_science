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
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "fastc", "imaging"))
try:
    import fastimg                      # C kernels (paste, year metrics); each falls back to its numpy reference
except Exception:                                                    # noqa: BLE001
    fastimg = None
import tilecache  # noqa: E402  (the shared block cache of the remote COG reads)

GDAL_ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", VSI_CACHE="TRUE", GDAL_HTTP_MAX_RETRY="2")
STRIPS = 8
SCORE_YEARS = 4
SCORE_RES = 2.4          # metres for the year-scoring reads (naip_years' own is 1.2: 4x the pixels, same ranking signal)


STAC_SEARCH = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS_TOKEN = "https://planetarycomputer.microsoft.com/api/sas/v1/token/{account}/{container}"
PREFETCH_KM = 4.0        # the NAIP search box round the national-index point, started before the course is resolved


def _http():
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = fi.UA
    return s


def stac_search(bbox_wsen, http=None):
    """Every NAIP STAC item intersecting the box, signed: the search POST (paged) and the SAS token GET run at once
    (pystac_client opens the catalog first and planetary_computer fetches the token after the search: about 2.0 s
    serial, 0.8 s this way). -> [pystac.Item]"""
    import pystac
    from urllib.parse import urlparse
    http = http or _http()
    tok = {}

    def token():
        r = http.get(SAS_TOKEN.format(account="naipeuwest", container="naip"), timeout=30)
        r.raise_for_status()
        tok["naipeuwest/naip"] = r.json()["token"]
    with ThreadPoolExecutor(1) as ex:
        ft = ex.submit(token)
        feats, body = [], dict(collections=["naip"], bbox=list(bbox_wsen), limit=250)
        while True:
            r = http.post(STAC_SEARCH, json=body, timeout=60)
            r.raise_for_status()
            j = r.json()
            feats += j.get("features", [])
            nxt = next((ln for ln in j.get("links", []) if ln.get("rel") == "next"), None)
            if not nxt or not j.get("features"):
                break
            body = nxt.get("body") or dict(body, token=(nxt.get("href", "").split("token=") + [""])[1])
        ft.result()
    items = [pystac.Item.from_dict(f) for f in feats]
    for it in items:
        for a in it.assets.values():
            u = urlparse(a.href)
            key = u.netloc.split(".")[0] + "/" + u.path.lstrip("/").split("/")[0]
            if u.netloc.endswith(".blob.core.windows.net") and "?" not in a.href:
                if key not in tok:
                    r = http.get(SAS_TOKEN.format(account=key.split("/")[0], container=key.split("/")[1]), timeout=30)
                    r.raise_for_status()
                    tok[key] = r.json()["token"]
                a.href = a.href + "?" + tok[key]
    return items


def stac_prefetch(lat, lon, km=PREFETCH_KM):
    """the NAIP items round a point (the national index row), searched while the course outline is being resolved
    -> (box [W, S, E, N], items)"""
    dy = km * 1000.0 / 111320.0
    dx = dy / math.cos(math.radians(lat))
    box = (lon - dx, lat - dy, lon + dx, lat + dy)
    return box, stac_search(box)


def list_years(bbox_snwe, prefetch=None):
    """naip_years.list_years (every NAIP acquisition over the box, grouped by year -> [{year, items, dates, coverage,
    gsd_m}]) from stac_search, or from a stac_prefetch result (a Future or the tuple) when its box holds this one
    (the items intersecting the box are the ones a search on the box returns)."""
    from shapely.geometry import box, shape
    from shapely.ops import unary_union
    s, w, n, e = bbox_snwe
    items = None
    if prefetch is not None:
        try:
            (pw, ps, pe, pn), its = prefetch.result() if hasattr(prefetch, "result") else prefetch
            if pw <= w and ps <= s and pe >= e and pn >= n:
                aoi = box(w, s, e, n)
                items = [it for it in its if shape(it.geometry).intersects(aoi)]
        except Exception:                                            # noqa: BLE001
            items = None
    if items is None:
        items = stac_search((w, s, e, n))
    aoi = box(w, s, e, n)
    years = []
    for yr in sorted({it.datetime.year for it in items}):
        its = [it for it in items if it.datetime.year == yr]
        cov = unary_union([shape(it.geometry) for it in its]).intersection(aoi).area / aoi.area
        years.append(dict(year=yr, items=its, dates=sorted({it.datetime.date().isoformat() for it in its}),
                          coverage=round(cov, 4), gsd_m=its[0].properties.get("gsd")))
    return years


def _warp_cached(key, opener, m, dst_tr, dst_crs, dst_shape, src_nodata, resampling, dst_nodata=0, dtype=np.uint8,
                 bands=None):
    """reproject(dataset -> dst grid) with the source pixels from tilecache: the source window under the dst grid
    (+ PAD px) is read through the cache, then warped from memory. Equal to warping from the dataset itself
    (test_fastpath / the session checks: Yorba Linda NAIP overview + Meta canopy, bit-identical)."""
    from affine import Affine
    from rasterio.crs import CRS
    from rasterio.warp import reproject, transform_bounds
    from rasterio.windows import from_bounds
    PAD = 4
    T, scrs = Affine(*m["transform"]), CRS.from_wkt(m["crs"])
    sh, sw = m["shape"]
    nb, H, W = dst_shape
    x0, y1 = dst_tr.c, dst_tr.f
    x1, y0 = x0 + dst_tr.a * W, y1 + dst_tr.e * H
    b = transform_bounds(dst_crs, scrs, x0, y0, x1, y1, densify_pts=21) if scrs != dst_crs else (x0, y0, x1, y1)
    win = from_bounds(*b, transform=T)
    r0 = max(int(math.floor(win.row_off)) - PAD, 0)
    c0 = max(int(math.floor(win.col_off)) - PAD, 0)
    r1 = min(int(math.ceil(win.row_off + win.height)) + PAD, sh)
    c1 = min(int(math.ceil(win.col_off + win.width)) + PAD, sw)
    dst = np.full(dst_shape, dst_nodata, dtype)
    if r1 <= r0 or c1 <= c0:
        return dst
    a, _ = tilecache.read(key, opener, (r0, c0, r1 - r0, c1 - c0), m)
    a = a[bands] if bands is not None else a[:nb]
    reproject(a, dst, src_transform=T * Affine.translation(c0, r0), src_crs=scrs, src_nodata=src_nodata,
              dst_transform=dst_tr, dst_crs=dst_crs, dst_nodata=dst_nodata, resampling=resampling)
    return dst


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
    env = rasterio.env.getenv() if rasterio.env.hasenv() else {}

    def one(it):                        # the items at once (each open is a 0.4-0.9 s round trip)
        href = it.assets["image"].href
        with rasterio.Env(**env):
            for lv in ((lvl, -1) if lvl >= 0 else (-1,)):
                kw = {} if lv < 0 else dict(overview_level=lv)
                key = f"naip/{it.id}/" + ("full" if lv < 0 else f"ovr{lv}")
                try:
                    m = tilecache.meta(key, lambda: rasterio.open(href, **kw))
                    break
                except rasterio.errors.RasterioIOError:
                    if lv < 0:
                        raise                # (no such overview: the warp reads full resolution)
            return _warp_cached(key, lambda: rasterio.open(href, **kw), m, tr, crs, (min(m["count"], 4), H, W),
                                0, Resampling.average)
    with ThreadPoolExecutor(len(its)) as ex:
        parts = list(ex.map(one, its))
    out = np.zeros((parts[0].shape[0], H, W), np.uint8)
    for dst in parts:                   # in item order: a later item's valid pixels win, as naip_years.read_year
        _paste(out, dst, 0, 0, "last")
    return out, crs, tr


def _paste(dst, src, r0, c0, mode):
    """fastimg.paste (C) or its numpy reference: 'first' = rasterio.merge(method='first', nodata=0) per element,
    'last' = np.where(src > 0, src, dst)"""
    if fastimg is not None:
        return fastimg.paste(dst, src, r0, c0, mode)
    cur = dst[:src.shape[0], r0:r0 + src.shape[1], c0:c0 + src.shape[2]]
    m = (cur == 0) & (src != 0) if mode == "first" else src > 0
    cur[m] = src[m]


def read_window(items, bounds, res):
    """the year's mosaic over bounds (x0, y0, x1, y1) in the items' CRS at their own pixel size: each item opened
    once, one read of the block-aligned window (all bands; GDAL_NUM_THREADS fetches and inflates the tiles in
    parallel, each tile once; blocks already in tilecache are not read), pasted like rasterio.merge(method='first',
    nodata=0). Bit-identical to the strip read
    (_read_strips) on Yorba Linda 2018: 35 MB / 3.0 s instead of 99 MB / 3.9 s (the strips re-read tiles at their
    seams). None when an item's grid is not aligned to the output grid (then _read_strips resamples, as before)."""
    import rasterio
    from rasterio.windows import Window
    x0, y0, x1, y1 = bounds
    W, H = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))

    def one(it):
        from affine import Affine
        from rasterio.crs import CRS
        href = it.assets["image"].href
        with rasterio.Env(**dict(GDAL_ENV, GDAL_NUM_THREADS="ALL_CPUS")):
            key = f"naip/{it.id}/full"
            m = tilecache.meta(key, lambda: rasterio.open(href))
            T, crs = Affine(*m["transform"]), CRS.from_wkt(m["crs"])
            (sh, sw) = m["shape"]
            fc, fr = (x0 - T.c) / res, (T.f - y1) / res
            if abs(abs(T.a) - res) > 1e-9 or abs(fc - round(fc)) > 1e-6 or abs(fr - round(fr)) > 1e-6 or T.b or T.d:
                return None
            c0, r0 = int(round(fc)), int(round(fr))
            ca, ra = max(c0, 0), max(r0, 0)
            cb, rb = min(c0 + W, sw), min(r0 + H, sh)
            if cb <= ca or rb <= ra:
                return crs, None, None
            # the 512 blocks the window touches: cached ones from disk, the rest in one GDAL read (GDAL_NUM_THREADS
            # fetches and inflates those tiles in parallel, each once)
            a, _ = tilecache.read(key, lambda: rasterio.open(href), (ra, ca, rb - ra, cb - ca), m)
            return crs, a, (ra - r0, ca - c0)
    with ThreadPoolExecutor(len(items)) as ex:
        parts = list(ex.map(one, items))
    if any(p is None for p in parts):
        return None
    crs = parts[0][0]
    parts = [p for p in parts if p[0] == crs and p[1] is not None]   # the first item's CRS only (as _read_strips)
    nb = max(p[1].shape[0] for p in parts)
    arr = np.zeros((nb, H, W), np.uint8)
    for _, a, (r, c) in parts:
        _paste(arr, a, r, c, "first")
    return arr, rasterio.transform.from_origin(x0, y1, res, res), crs


def write_cog(path, arr, crs, transform, jpeg_quality):
    """fetch_imagery.write_cog for the NAIP JPEG COGs in one pass: the array goes to an uncompressed /vsimem tiff and
    the COG driver encodes it once, its overviews (2, 4, 8, ... average) included, on all cores. The old way encoded
    a tiled tmp file, built its overviews, then re-encoded it as the COG. Same layout (512 blocks, YCbCr JPEG at the
    same quality, the same overview levels), same error against the raw mosaic; Yorba Linda RGB + NIR 2.2 -> 0.5 s.
    -> (format, MB). Falls back to fetch_imagery.write_cog."""
    import rasterio
    import rasterio.shutil
    from rasterio.shutil import copy as rcopy
    count, h, w = arr.shape
    mem = f"/vsimem/{os.getpid()}_{id(arr)}_{os.path.basename(path)}"
    try:
        with rasterio.open(mem, "w", driver="GTiff", height=h, width=w, count=count, dtype=arr.dtype, crs=crs,
                           transform=transform, tiled=True, blockxsize=512, blockysize=512) as dst:
            dst.write(arr)
        rcopy(mem, path + ".tmp.tif", driver="COG", BLOCKSIZE=512, COMPRESS="JPEG", QUALITY=jpeg_quality,
              OVERVIEW_RESAMPLING="AVERAGE", OVERVIEW_COUNT=4, NUM_THREADS="ALL_CPUS")   # 2, 4, 8, 16 as before
        os.replace(path + ".tmp.tif", path)
    except Exception:                                                # noqa: BLE001
        return fi.write_cog(path, arr, crs, transform, jpeg_quality=jpeg_quality)
    finally:
        try:
            rasterio.shutil.delete(mem)
        except Exception:                                            # noqa: BLE001
            pass
    return "COG", round(os.path.getsize(path) / 1e6, 2)


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


def fetch_naip(bbox, out_dir, lo_res=0.6, year="auto", osm=None, T=None, prefetch=None):
    import rasterio
    from rasterio.warp import transform_bounds
    T = T if T is not None else {}
    s, w, n, e = bbox
    t0 = time.time()
    try:
        years = list_years(bbox, prefetch)
    except Exception:                                                # noqa: BLE001
        years = NY.list_years(bbox)     # pystac_client + planetary_computer, as before
    if not years:
        raise RuntimeError("no NAIP items intersect the bbox")
    T["naip_list"] = round(time.time() - t0, 2)
    t0 = time.time()
    cov = [y for y in years if y["coverage"] > 0.9] or years
    years = cov[-SCORE_YEARS:]          # only the newest few years compete (older flights predate renovations anyway)
    pool = ThreadPoolExecutor(max(1, len(years)))

    def rd(y):                          # the overview reads start before the OSM turf is in (they need only the box)
        try:
            with rasterio.Env(**GDAL_ENV):
                return read_year_ovr(y["items"], bbox)
        except Exception as ex:                                      # noqa: BLE001
            return ex
    reads = {y["year"]: pool.submit(rd, y) for y in years} if year == "auto" and osm is not None else {}
    if hasattr(osm, "result"):          # a Future: the listing and reads ran while the OSM features were on their way
        t1 = time.time()
        osm = osm.result()
        T["naip_wait_osm"] = round(time.time() - t1, 2)
    scores = {}
    polys = NY.turf_polygons(osm) if (year == "auto" and osm) else None
    if polys is not None and not any(polys.values()):
        year = "latest"                 # no OSM turf to score on (unmapped course): the newest covering year, no reads
    if year == "auto" and osm:

        def sc(y):
            got = reads[y["year"]].result()
            if isinstance(got, Exception):
                return y["year"], got
            try:
                return y["year"], (fastimg.score_array if fastimg is not None else NY._score_array)(*got, polys, {})
            except Exception as ex:                                  # noqa: BLE001
                return y["year"], ex
        scores = dict(pool.map(sc, years))
    pool.shutdown(wait=False, cancel_futures=True)

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
    with ThreadPoolExecutor(3) as ex:   # the two COGs and the plain JPEGs at once (GDAL / Pillow release the GIL)
        f_rgb = ex.submit(write_cog, os.path.join(out_dir, "naip_rgb.tif"), arr[:3], crs, tr, 90)
        f_nir = ex.submit(write_cog, os.path.join(out_dir, "naip_nir.tif"), arr[3:4], crs, tr, 92) if nb >= 4 else None
        f_lo = ex.submit(fi.write_lo, arr, tr, lo_res, out_dir, "naip")
        kind, mb_rgb = f_rgb.result()
        files, sizes = {"rgb": "naip_rgb.tif"}, {"naip_rgb.tif": mb_rgb}
        if f_nir is not None:
            files["nir"], sizes["naip_nir.tif"] = "naip_nir.tif", f_nir.result()[1]
        lo = f_lo.result()
    T["naip_write"] = round(time.time() - t0, 2)
    return dict(source="USDA NAIP via Microsoft Planetary Computer (collection 'naip')", year=yr,
                years_available=[y["year"] for y in years], acquired=sorted({it.datetime.date().isoformat() for it in its}),
                items=[it.id for it in its], selection=selection, gsd_m=its[0].properties.get("gsd"), resolution_m=round(res, 4),
                bands=["red", "green", "blue"] + (["nir"] if nb >= 4 else []), crs=crs.to_string(), epsg=crs.to_epsg(),
                width=int(arr.shape[2]), height=int(arr.shape[1]), transform=fi.tf_list(tr), bounds_crs=[x0, y0, x1, y1],
                files=files, format=kind, lo=lo, sizes_mb=sizes, license="Public domain (USDA FSA)")


def fetch_dem_cached(padded, out_dir, epsg):
    """fetch_imagery.fetch_dem (3DEP exportImage at 1 m) with its answer kept in the shared cache, keyed by the exact
    request (box, CRS): a re-run under another slug copies dem.tif instead of downloading it"""
    import hashlib
    import shutil
    key = json.dumps(dict(bbox=[round(v, 9) for v in padded], epsg=epsg, res=1.0, v=1), sort_keys=True)
    d = os.path.join(tilecache.root(), "dem", hashlib.sha1(key.encode()).hexdigest()[:20])
    try:
        with open(os.path.join(d, "meta.json")) as fh:
            meta = json.load(fh)
        shutil.copyfile(os.path.join(d, "dem.tif"), os.path.join(out_dir, "dem.tif"))
        os.utime(os.path.join(d, "dem.tif"))          # last use, for tilecache.prune
        return meta
    except (OSError, ValueError):
        pass
    meta = fi.fetch_dem(padded, out_dir, epsg)
    if tilecache.enabled() and meta.get("file") == "dem.tif" and "tnm_errors" not in meta:   # the 1 m TNM answer only
        try:
            os.makedirs(d, exist_ok=True)
            shutil.copyfile(os.path.join(out_dir, "dem.tif"), os.path.join(d, "dem.tif.tmp"))
            os.replace(os.path.join(d, "dem.tif.tmp"), os.path.join(d, "dem.tif"))
            with open(os.path.join(d, "meta.json"), "w") as fh:
                json.dump(meta, fh)
        except OSError:
            pass
    return meta


def fetch(bbox_wsen, out_dir, osm_fc=None, year="auto", margin=100.0, label=None, quiet=True, prefetch=None):
    """bbox_wsen: the course bbox [W, S, E, N] (course.json); osm_fc: the OSM FeatureCollection, or a Future of it
    (needed only for the year scoring, after the NAIP listing); prefetch: stac_prefetch's result or Future.
    -> (georef dict, timings)"""
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
            return fetch_dem_cached(padded, out_dir, epsg0)
        finally:
            T["dem"] = round(time.time() - t0, 2)

    def naip():
        return fetch_naip(padded, out_dir, 0.6, year, osm_fc, T, prefetch)
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
