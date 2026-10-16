"""Fetch the free rasters the any-course hazard vision needs, for one course bbox (runs on GitHub Actions).

  python course_data/vision_any/fetch_any.py --course-dir course_data/mozingo --slug mozingo
  python course_data/vision_any/fetch_any.py --bbox S,W,N,E --slug some_course

All layers are written on ONE grid: the WGS84 UTM zone of the course centre, snapped to whole metres,
bbox padded by --margin (default 120 m). Outputs in course_data/vision_any/<slug>/raw/:

  hag.tif       uint8, height above ground in 0.25 m units (0..63.75 m), 1 m grid, 255 = nodata.
                Source order: Planetary Computer '3dep-lidar-hag' (USGS 3DEP lidar, 2 m products),
                else '3dep-lidar-dsm' - '3dep-lidar-dtm', else the raw 3DEP point cloud (Entwine/EPT on
                AWS usgs-lidar-public) through PDAL (hag_nn, max per 1 m cell). No lidar at all: only
                chm_meta.tif (Meta/WRI 1 m global canopy height) is available.
  lidar_class.tif  uint8 ASPRS class (2 ground, 3-5 vegetation, 6 building, 9 water), 1 m grid, 0 = nodata
                ('3dep-lidar-classification'; majority class of the returns per 2 m cell).
  dtm.tif       float32 bare-earth metres, 2 m grid ('3dep-lidar-dtm'; fallback 3dep-seamless 10 m).
  chm_meta.tif  uint8 metres, 1 m grid (Meta global canopy height). Always tried: it is the no-lidar
                fallback and a cross-check.
  worldcover.tif uint8 ESA WorldCover 10 m class (10 tree, 30 grass, 80 water, ...), resampled nearest.
  naip_<year>.tif  uint8 R,G,B,NIR, 0.6 m grid (area-averaged), JPEG-compressed COG: the latest 2 NAIP
                years that cover the bbox (two seasons/years make native grass easier to separate).
  meta.json     grid, per-layer source items, dates, survey ids, errors.

The sandbox can't reach these hosts; .github/workflows/vision_any.yml runs this and commits raw/.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import traceback

import numpy as np

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
META_CHM = "https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/chm/{qk}.tif"


def log(*a):
    print(*a, flush=True)


def bbox_from_course_dir(d):
    sm = json.load(open(os.path.join(d, "summary.json")))
    b = (sm.get("course") or {}).get("bounds")
    boxes = []
    if b:
        boxes.append([b["minlat"], b["minlon"], b["maxlat"], b["maxlon"]])
    if sm.get("bbox_wgs84_snwe"):
        boxes.append(sm["bbox_wgs84_snwe"])
    geo = os.path.join(d, "osm.geojson")
    if os.path.exists(geo):                                   # every feature inside the course
        fc = json.load(open(geo))
        xy = []
        for f in fc["features"]:
            pr = f["properties"]
            if not pr.get("golf") or pr.get("golf") == "cartpath" or not f.get("geometry"):
                continue                                  # golf features only (roads tagged inside run for km)
            c = np.array(_coords(f["geometry"]), float)
            if len(c):
                xy.append([c[:, 1].min(), c[:, 0].min(), c[:, 1].max(), c[:, 0].max()])
        if xy:
            a = np.array(xy)
            boxes.append([a[:, 0].min(), a[:, 1].min(), a[:, 2].max(), a[:, 3].max()])
    if not boxes:
        raise SystemExit("no bbox in " + d)
    a = np.array(boxes)
    return (a[:, 0].min(), a[:, 1].min(), a[:, 2].max(), a[:, 3].max()), (sm.get("course") or {}).get("name")


def _coords(g):
    t, c = g["type"], g["coordinates"]
    if t == "Point":
        return [c]
    if t in ("LineString", "MultiPoint"):
        return c
    if t in ("Polygon", "MultiLineString"):
        return [p for r in c for p in r]
    if t == "MultiPolygon":
        return [p for poly in c for r in poly for p in r]
    return []


# --------------------------------------------------------------------------- grid
class Grid:
    def __init__(self, bbox, margin, res):
        from pyproj import Transformer
        from affine import Affine
        s, w, n, e = bbox
        lat, lon = (s + n) / 2, (w + e) / 2
        self.epsg = (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1
        t = Transformer.from_crs("EPSG:4326", f"EPSG:{self.epsg}", always_xy=True)
        xs, ys = t.transform([w, e, w, e], [s, s, n, n])
        self.x0 = math.floor((min(xs) - margin) / 2) * 2
        self.y1 = math.ceil((max(ys) + margin) / 2) * 2
        self.x1 = math.ceil((max(xs) + margin) / 2) * 2
        self.y0 = math.floor((min(ys) - margin) / 2) * 2
        self.res = res
        self.W = int(round((self.x1 - self.x0) / res))
        self.H = int(round((self.y1 - self.y0) / res))
        self.transform = Affine(res, 0, self.x0, 0, -res, self.y1)
        self.crs = f"EPSG:{self.epsg}"
        tb = Transformer.from_crs(f"EPSG:{self.epsg}", "EPSG:4326", always_xy=True)
        lo, la = tb.transform([self.x0, self.x1, self.x0, self.x1], [self.y0, self.y0, self.y1, self.y1])
        self.ll_bbox = [min(lo), min(la), max(lo), max(la)]          # W, S, E, N

    def at(self, res):
        g = Grid.__new__(Grid)
        g.__dict__.update(self.__dict__)
        from affine import Affine
        g.res = res
        g.W = int(round((self.x1 - self.x0) / res))
        g.H = int(round((self.y1 - self.y0) / res))
        g.transform = Affine(res, 0, self.x0, 0, -res, self.y1)
        return g

    def json(self):
        return dict(crs=self.crs, res_m=self.res, width=self.W, height=self.H, bounds=[self.x0, self.y0, self.x1, self.y1],
                    transform=list(self.transform)[:6], ll_bbox_wsen=self.ll_bbox)


def write_tif(path, arr, g, nodata=None, jpeg=None, tags=None):
    import rasterio
    from rasterio.enums import Resampling
    arr = np.asarray(arr)
    if arr.ndim == 2:
        arr = arr[None]
    prof = dict(driver="GTiff", height=arr.shape[1], width=arr.shape[2], count=arr.shape[0], dtype=arr.dtype,
                crs=g.crs, transform=g.transform, tiled=True, blockxsize=256, blockysize=256, nodata=nodata)
    if jpeg:
        prof.update(compress="jpeg", jpeg_quality=jpeg, interleave="pixel")
    else:
        prof.update(compress="deflate", predictor=3 if arr.dtype.kind == "f" else 2, zlevel=9)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr)
        if tags:
            dst.update_tags(**{k: str(v) for k, v in tags.items()})
        dst.build_overviews([2, 4, 8], Resampling.average if jpeg else Resampling.nearest)
    return round(os.path.getsize(path) / 1e6, 2)


def stac():
    import planetary_computer
    import pystac_client
    return pystac_client.Client.open(STAC, modifier=planetary_computer.sign_inplace)


def _when(it):
    p = it.properties
    return p.get("end_datetime") or p.get("datetime") or p.get("start_datetime") or ""


def _asset(it):
    for k in ("data", "image", "map", "cog"):
        if k in it.assets:
            return it.assets[k].href
    for a in it.assets.values():
        if "tiff" in (a.media_type or ""):
            return a.href
    raise KeyError(f"no raster asset in {it.id}: {list(it.assets)}")


def mosaic(items, g, resampling, nodata_out, dtype=np.float32, src_nodata=None):
    """Reproject items (newest first) onto grid g; later items only fill cells still empty."""
    import rasterio
    from rasterio.warp import reproject
    out = np.full((g.H, g.W), np.nan, np.float32)
    used = []
    for it in items:
        href = _asset(it)
        try:
            with rasterio.open(href) as src:
                tmp = np.full((g.H, g.W), np.nan, np.float32)
                nd = src.nodata if src.nodata is not None else src_nodata
                reproject(rasterio.band(src, 1), tmp, src_nodata=nd, dst_nodata=np.nan,
                          dst_transform=g.transform, dst_crs=g.crs, resampling=resampling)
            fill = np.isnan(out) & np.isfinite(tmp)
            if fill.any():
                out[fill] = tmp[fill]
                used.append(dict(id=it.id, when=_when(it), cells=int(fill.sum()),
                                 props={k: v for k, v in it.properties.items()
                                        if k.startswith("3dep") or k in ("datetime", "start_datetime", "end_datetime", "gsd")}))
            log(f"    {it.id}: +{int(fill.sum())} cells")
        except Exception as ex:                                # noqa: BLE001
            log(f"    {it.id}: FAILED {ex!r}"[:300])
        if np.isfinite(out).all():
            break
    return out, used


def search(cat, coll, g, **kw):
    w, s, e, n = g.ll_bbox
    items = list(cat.search(collections=[coll], bbox=[w, s, e, n], **kw).items())
    items.sort(key=_when, reverse=True)
    log(f"  {coll}: {len(items)} items " + ", ".join(f"{i.id}@{_when(i)[:10]}" for i in items[:12]))
    return items


# --------------------------------------------------------------------------- layers
def fetch_lidar(cat, g1, g2, out, meta):
    from rasterio.enums import Resampling
    info = {}
    hag = None
    try:
        items = search(cat, "3dep-lidar-hag", g1)
        if items:
            hag, used = mosaic(items, g1, Resampling.bilinear, np.nan)
            info["hag"] = dict(source="planetary-computer 3dep-lidar-hag", items=used,
                               valid=float(np.isfinite(hag).mean()))
    except Exception:
        info["hag_error"] = traceback.format_exc()[-1500:]
        log(info["hag_error"])
    dtm = None
    try:
        items = search(cat, "3dep-lidar-dtm", g2)
        if items:
            dtm, used = mosaic(items, g2, Resampling.bilinear, np.nan)
            info["dtm"] = dict(source="planetary-computer 3dep-lidar-dtm", items=used, valid=float(np.isfinite(dtm).mean()))
    except Exception:
        info["dtm_error"] = traceback.format_exc()[-1500:]
        log(info["dtm_error"])
    if hag is None or np.isfinite(hag).mean() < 0.5:
        try:                                                    # DSM - DTM
            items = search(cat, "3dep-lidar-dsm", g1)
            if items and dtm is not None:
                dsm, used = mosaic(items, g1, Resampling.bilinear, np.nan)
                import rasterio
                from rasterio.warp import reproject
                d1 = np.full((g1.H, g1.W), np.nan, np.float32)
                reproject(dtm, d1, src_transform=g2.transform, src_crs=g2.crs, dst_transform=g1.transform,
                          dst_crs=g1.crs, resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
                h2 = dsm - d1
                if hag is None:
                    hag = h2
                else:
                    hag = np.where(np.isfinite(hag), hag, h2)
                info["hag_dsm_dtm"] = dict(items=used)
        except Exception:
            info["dsm_error"] = traceback.format_exc()[-1500:]
            log(info["dsm_error"])
    if hag is not None and np.isfinite(hag).mean() < 0.5:
        info["hag_note"] = f"PC lidar covers {np.isfinite(hag).mean():.0%} of the grid; trying EPT"
        hag = None
    if dtm is not None and np.isfinite(dtm).mean() < 0.5:
        dtm = None
    if hag is None:
        meta["lidar"] = info
        return False
    if hag is not None:
        q = np.where(np.isfinite(hag), np.clip(np.round(np.maximum(hag, 0) * 4), 0, 254), 255).astype(np.uint8)
        info.setdefault("hag", {})["file"] = "hag.tif"
        info["hag"]["mb"] = write_tif(os.path.join(out, "hag.tif"), q, g1, nodata=255,
                                      tags=dict(units="0.25 m", nodata=255))
        info["hag"]["frac_gt_2_5m"] = float(np.nanmean(hag > 2.5))
    if dtm is not None:
        info["dtm"]["mb"] = write_tif(os.path.join(out, "dtm.tif"), dtm.astype(np.float32), g2, nodata=float("nan"))
    try:
        items = search(cat, "3dep-lidar-classification", g1)
        if items:
            cl, used = mosaic(items, g1, Resampling.nearest, np.nan)
            q = np.where(np.isfinite(cl), np.clip(cl, 0, 254), 0).astype(np.uint8)
            info["classification"] = dict(source="planetary-computer 3dep-lidar-classification", items=used,
                                          mb=write_tif(os.path.join(out, "lidar_class.tif"), q, g1, nodata=0),
                                          counts={int(k): int(v) for k, v in zip(*np.unique(q, return_counts=True))})
    except Exception:
        info["class_error"] = traceback.format_exc()[-1500:]
        log(info["class_error"])
    meta["lidar"] = info
    return True


EPT_INDEX = "https://raw.githubusercontent.com/hobuinc/usgs-lidar/master/boundaries/resources.geojson"


def fetch_ept(g1, g2, out, meta, max_projects=3):
    """USGS 3DEP point clouds (Entwine/EPT on AWS, s3 usgs-lidar-public) -> PDAL: drop noise, height above
    ground (filters.hag_nn), max per 1 m cell; ground Z per 2 m cell; building (class 6) return count.
    Used where Planetary Computer has no 3dep-lidar-* items (e.g. Iowa). Needs the `pdal` CLI."""
    import re
    import shutil
    import subprocess
    import requests
    import rasterio
    from pyproj import Transformer
    from shapely.geometry import box, shape
    info = dict(source="USGS 3DEP lidar point cloud, EPT on AWS (usgs-lidar-public) via PDAL")
    if not shutil.which("pdal"):
        info["error"] = "pdal CLI not installed"
        meta["ept"] = info
        return None
    idx = requests.get(EPT_INDEX, timeout=120).json()
    t = Transformer.from_crs(g1.crs, "EPSG:3857", always_xy=True)
    xs, ys = t.transform([g1.x0, g1.x1, g1.x0, g1.x1], [g1.y0, g1.y0, g1.y1, g1.y1])
    b3857 = (min(xs) - 20, min(ys) - 20, max(xs) + 20, max(ys) + 20)
    aoi_ll = box(*g1.ll_bbox)
    aoi_m = box(*b3857)
    cands = []
    for f in idx["features"]:
        try:
            geom = shape(f["geometry"])
        except Exception:                                      # noqa: BLE001
            continue
        aoi = aoi_ll if abs(geom.bounds[0]) <= 180 else aoi_m
        if not geom.intersects(aoi):
            continue
        cov = geom.intersection(aoi).area / aoi.area
        nm = f["properties"].get("name", "")
        yrs = [int(y) for y in re.findall(r"(?<!\d)(20[0-2]\d|199\d)(?!\d)", nm)]
        cands.append(dict(name=nm, url=f["properties"].get("url"), cov=round(cov, 3), year=max(yrs) if yrs else 0,
                          count=f["properties"].get("count")))
    cands.sort(key=lambda c: (c["cov"] > 0.9, c["year"]), reverse=True)
    info["candidates"] = cands[:10]
    log("  EPT candidates:", cands[:10])
    hag = np.full((g1.H, g1.W), np.nan, np.float32)
    dtm = np.full((g2.H, g2.W), np.nan, np.float32)
    bld = np.zeros((g1.H, g1.W), np.float32)
    used = []
    for c in cands[:max_projects]:
        url = c["url"] or f"https://s3-us-west-2.amazonaws.com/usgs-lidar-public/{c['name']}/ept.json"
        tmp = os.path.join(out, "_ept")
        os.makedirs(tmp, exist_ok=True)
        common = dict(origin_x=g1.x0, origin_y=g1.y0, width=g1.W, height=g1.H, resolution=1.0, nodata=-9999)
        pipe = [
            dict(type="readers.ept", filename=url, bounds=f"([{b3857[0]},{b3857[2]}],[{b3857[1]},{b3857[3]}])",
                 threads=8),
            dict(type="filters.range", limits="Classification![7:7],Classification![18:18]"),
            dict(type="filters.reprojection", out_srs=g1.crs, tag="pts"),
            dict(type="filters.hag_nn", inputs=["pts"], tag="hag"),
            dict(type="writers.gdal", inputs=["hag"], filename=os.path.join(tmp, "hag.tif"),
                 dimension="HeightAboveGround", output_type="max", **common),
            dict(type="filters.range", inputs=["pts"], limits="Classification[2:2]", tag="ground"),
            dict(type="writers.gdal", inputs=["ground"], filename=os.path.join(tmp, "dtm.tif"), dimension="Z",
                 output_type="mean", origin_x=g2.x0, origin_y=g2.y0, width=g2.W, height=g2.H, resolution=2.0,
                 nodata=-9999, window_size=3),
            dict(type="filters.range", inputs=["pts"], limits="Classification[6:6]", tag="bld"),
            dict(type="writers.gdal", inputs=["bld"], filename=os.path.join(tmp, "bld.tif"), dimension="Z",
                 output_type="count", **common),
        ]
        pj = os.path.join(tmp, "pipe.json")
        json.dump(pipe, open(pj, "w"))
        log("  PDAL", c["name"])
        r = subprocess.run(["pdal", "pipeline", pj], capture_output=True, text=True, timeout=2400)
        if r.returncode != 0:
            log("   PDAL failed:", r.stderr[-1500:])
            info.setdefault("errors", []).append(dict(name=c["name"], err=r.stderr[-800:]))
            continue
        with rasterio.open(os.path.join(tmp, "hag.tif")) as src:
            a = src.read(1).astype(np.float32)
            a[a == -9999] = np.nan
        f = np.isnan(hag) & np.isfinite(a)
        hag[f] = a[f]
        p = os.path.join(tmp, "dtm.tif")
        if os.path.exists(p):
            with rasterio.open(p) as src:
                a = src.read(1).astype(np.float32)
                a[a == -9999] = np.nan
            f2 = np.isnan(dtm) & np.isfinite(a)
            dtm[f2] = a[f2]
        p = os.path.join(tmp, "bld.tif")
        if os.path.exists(p):
            with rasterio.open(p) as src:
                a = src.read(1).astype(np.float32)
            bld = np.maximum(bld, np.where(a > 0, a, 0))
        used.append(dict(c, cells=int(f.sum())))
        shutil.rmtree(tmp, ignore_errors=True)
        if np.isfinite(hag).mean() > 0.97:
            break
    info["used"] = used
    if not used:
        meta["ept"] = info
        return None
    # cells with no return at all (water, gaps): leave nodata; the canopy step treats them as open
    info["valid"] = float(np.isfinite(hag).mean())
    q = np.where(np.isfinite(hag), np.clip(np.round(np.maximum(hag, 0) * 4), 0, 254), 255).astype(np.uint8)
    info["hag_mb"] = write_tif(os.path.join(out, "hag.tif"), q, g1, nodata=255, tags=dict(units="0.25 m", nodata=255))
    info["frac_gt_2_5m"] = float(np.nanmean(hag > 2.5))
    if np.isfinite(dtm).mean() > 0.3:
        info["dtm_mb"] = write_tif(os.path.join(out, "dtm.tif"), dtm, g2, nodata=float("nan"))
    cl = np.where(bld > 0, 6, np.where(np.isfinite(hag), 1, 0)).astype(np.uint8)
    info["class_mb"] = write_tif(os.path.join(out, "lidar_class.tif"), cl, g1, nodata=0,
                                 tags=dict(note="6 = building returns present, 1 = other (EPT path)"))
    meta["ept"] = info
    return hag


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
                d = 0
                m = 1 << (i - 1)
                if x & m:
                    d += 1
                if y & m:
                    d += 2
                q += str(d)
            out.append(q)
    return out


def fetch_meta_chm(g1, out, meta):
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    info = dict(source="Meta/WRI high-resolution canopy height (Tolan et al. 2024), s3 dataforgood-fb-data")
    arr = np.full((g1.H, g1.W), np.nan, np.float32)
    try:
        for qk in quadkeys(g1.ll_bbox):
            url = META_CHM.format(qk=qk)
            log("  meta chm", url)
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", AWS_NO_SIGN_REQUEST="YES"):
                with rasterio.open("/vsicurl/" + url) as src:
                    tmp = np.full((g1.H, g1.W), np.nan, np.float32)
                    reproject(rasterio.band(src, 1), tmp, src_nodata=src.nodata, dst_nodata=np.nan,
                              dst_transform=g1.transform, dst_crs=g1.crs, resampling=Resampling.bilinear)
            f = np.isnan(arr) & np.isfinite(tmp)
            arr[f] = tmp[f]
            info.setdefault("tiles", []).append(qk)
        q = np.where(np.isfinite(arr), np.clip(np.round(arr), 0, 254), 255).astype(np.uint8)
        info["mb"] = write_tif(os.path.join(out, "chm_meta.tif"), q, g1, nodata=255, tags=dict(units="m"))
        info["file"] = "chm_meta.tif"
        info["valid"] = float(np.isfinite(arr).mean())
    except Exception:
        info["error"] = traceback.format_exc()[-1500:]
        log(info["error"])
    meta["meta_chm"] = info


def fetch_worldcover(cat, g1, out, meta):
    from rasterio.enums import Resampling
    info = {}
    try:
        items = search(cat, "esa-worldcover", g1)
        if items:
            g10 = g1.at(2.0)
            wc, used = mosaic(items, g10, Resampling.nearest, np.nan)
            q = np.where(np.isfinite(wc), wc, 0).astype(np.uint8)
            info = dict(source="ESA WorldCover via planetary-computer", items=used, file="worldcover.tif",
                        mb=write_tif(os.path.join(out, "worldcover.tif"), q, g10, nodata=0))
    except Exception:
        info["error"] = traceback.format_exc()[-1500:]
        log(info["error"])
    meta["worldcover"] = info


def fetch_naip(cat, g1, out, meta, n_years=2, res=0.6):
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    from shapely.geometry import box, shape
    from shapely.ops import unary_union
    info = dict(years=[])
    try:
        items = search(cat, "naip", g1)
        aoi = box(*g1.ll_bbox)
        years = sorted({i.datetime.year for i in items}, reverse=True)
        gn = g1.at(res)
        for yr in years:
            its = [i for i in items if i.datetime.year == yr]
            cov = unary_union([shape(i.geometry) for i in its]).intersection(aoi).area / aoi.area
            log(f"  NAIP {yr}: {len(its)} items, coverage {cov:.3f}")
            if cov < 0.98:
                continue
            bands = np.zeros((4, gn.H, gn.W), np.uint8)
            nb = 0
            for it in its:
                with rasterio.open(it.assets["image"].href) as src:
                    nb = max(nb, src.count)
                    for b in range(1, min(src.count, 4) + 1):
                        tmp = np.zeros((gn.H, gn.W), np.uint8)
                        reproject(rasterio.band(src, b), tmp, src_nodata=0, dst_nodata=0, dst_transform=gn.transform,
                                  dst_crs=gn.crs, resampling=Resampling.average)
                        f = (bands[b - 1] == 0) & (tmp > 0)
                        bands[b - 1][f] = tmp[f]
            if nb < 4:
                log("   no NIR band, skipping year")
                continue
            fn = f"naip_{yr}.tif"
            mb = write_tif(os.path.join(out, fn), bands, gn, jpeg=88)
            info["years"].append(dict(year=yr, file=fn, mb=mb, items=[i.id for i in its],
                                      acquired=sorted({i.datetime.date().isoformat() for i in its}),
                                      gsd_m=its[0].properties.get("gsd"), res_m=res))
            if len(info["years"]) >= n_years:
                break
    except Exception:
        info["error"] = traceback.format_exc()[-1500:]
        log(info["error"])
    meta["naip"] = info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course-dir")
    ap.add_argument("--bbox", help="S,W,N,E")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--margin", type=float, default=120.0)
    ap.add_argument("--naip-years", type=int, default=2)
    ap.add_argument("--skip", default="", help="comma list of lidar,meta,worldcover,naip")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, a.slug, "raw")
    os.makedirs(out, exist_ok=True)
    if a.bbox:
        bbox, name = tuple(map(float, a.bbox.split(","))), a.slug
    else:
        bbox, name = bbox_from_course_dir(a.course_dir)
    g1 = Grid(bbox, a.margin, 1.0)
    g2 = g1.at(2.0)
    log("course", name, "bbox", bbox, "grid", g1.json())
    meta = dict(schema="vision_any_raw/1", slug=a.slug, course=name, bbox_snwe=list(bbox), grid=g1.json(),
                fetched_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    skip = set(a.skip.split(","))
    cat = stac()
    for f in ("hag.tif", "dtm.tif", "lidar_class.tif"):           # stale layers from an earlier run
        if os.path.exists(os.path.join(out, f)):
            os.remove(os.path.join(out, f))
    if "lidar" not in skip:
        ok = False
        try:
            ok = fetch_lidar(cat, g1, g2, out, meta)
        except Exception:
            meta["lidar_error"] = traceback.format_exc()[-1500:]
        if not ok and "ept" not in skip:
            try:
                fetch_ept(g1, g2, out, meta)
            except Exception:
                meta["ept_error"] = traceback.format_exc()[-1500:]
                log(meta["ept_error"])
    if "meta" not in skip:
        fetch_meta_chm(g1, out, meta)
    if "worldcover" not in skip:
        fetch_worldcover(cat, g1, out, meta)
    if "naip" not in skip:
        fetch_naip(cat, g1, out, meta, a.naip_years)
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), indent=1, default=str)
    log(json.dumps(meta, indent=1, default=str)[:6000])
    ok = os.path.exists(os.path.join(out, "hag.tif")) or os.path.exists(os.path.join(out, "chm_meta.tif"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
