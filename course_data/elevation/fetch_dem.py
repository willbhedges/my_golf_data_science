"""Fetch the USGS 3DEP bare-earth DEM for a golf course (run on GitHub Actions; the dev sandbox is offline).

  python course_data/elevation/fetch_dem.py [--course-dir course_data/spirit_hollow] [--margin 200]
                                            [--out course_data/elevation/spirit_hollow] [--res 1.0]

Sources, in order:
  1. USGS The National Map 3DEPElevation ImageServer `exportImage` (best available = 1 m lidar DEM where it
     exists; Des Moines County IA has statewide 1 m lidar). Requested in the local UTM zone at --res metres.
  2. Microsoft Planetary Computer STAC '3dep-seamless' (1/3 arc-second, ~10 m).
  3. Planetary Computer 'cop-dem-glo-30' (Copernicus 30 m DSM -- includes tree canopy, last resort).
Also queries the TNM Products API for the 1 m DEM tiles/lidar projects covering the bbox (provenance + dates).

Writes to --out:
  dem.tif        float32 metres (NAVD88), DEFLATE + floating-point predictor, UTM CRS
  dem.npz        z_cm (uint16, centimetres above z0_m), z0_m, transform, epsg -- numpy-only consumers
  georef.json    source, CRS, affine transform (GDAL order), bbox, size, elevation range, provenance
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

UA = "my_golf_data_science/elevation (github actions)"
TNM_IMG = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"
TNM_PRODUCTS = "https://tnmaccess.nationalmap.gov/api/v1/products"


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def course_bbox(course_dir):
    s = json.load(open(os.path.join(course_dir, "summary.json")))
    b = s["course"]["bounds"]
    return b["minlat"], b["minlon"], b["maxlat"], b["maxlon"]


def pad_bbox(bbox, m):
    s, w, n, e = bbox
    dlat = m / 111320.0
    dlon = m / (111320.0 * math.cos(math.radians((s + n) / 2)))
    return s - dlat, w - dlon, n + dlat, e + dlon


def utm_epsg(lat, lon):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1


def tnm_products(bbox):
    import requests
    s, w, n, e = bbox
    out = []
    for ds in ("Digital Elevation Model (DEM) 1 meter", "National Elevation Dataset (NED) 1/3 arc-second"):
        try:
            r = requests.get(TNM_PRODUCTS, params=dict(datasets=ds, bbox=f"{w},{s},{e},{n}", max=20,
                                                       outputFormat="JSON"),
                             headers={"User-Agent": UA}, timeout=60)
            for it in r.json().get("items", []):
                out.append(dict(dataset=ds, title=it.get("title"), date=it.get("publicationDate"),
                                last_updated=it.get("lastUpdated"), url=it.get("downloadURL"),
                                meta=it.get("metaUrl")))
        except Exception as ex:                       # provenance only; never fatal
            out.append(dict(dataset=ds, error=repr(ex)[:200]))
    return out


def write_outputs(out, a, crs_epsg, tr, source, extra):
    import rasterio
    from rasterio.crs import CRS
    a = a.astype(np.float32)
    path = os.path.join(out, "dem.tif")
    prof = dict(driver="GTiff", width=a.shape[1], height=a.shape[0], count=1, dtype="float32",
                crs=CRS.from_epsg(crs_epsg), transform=tr, nodata=float("nan"), compress="deflate",
                predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(a, 1)
    z0 = float(math.floor(np.nanmin(a)))
    zc = np.round((a - z0) * 100)
    zc = np.where(np.isfinite(zc), zc, 65535).clip(0, 65535).astype(np.uint16)
    tl = [tr.a, tr.b, tr.c, tr.d, tr.e, tr.f]
    np.savez_compressed(os.path.join(out, "dem.npz"), z_cm=zc, z0_m=z0, nodata=65535,
                        transform=np.array(tl), epsg=crs_epsg)
    meta = dict(source=source, crs=f"EPSG:{crs_epsg}", epsg=crs_epsg, vertical_datum="NAVD88 (metres)",
                transform=tl, transform_convention="GDAL/affine: x = c + a*col + b*row, y = f + d*col + e*row "
                "(pixel top-left corner; +0.5 for centres)",
                width=int(a.shape[1]), height=int(a.shape[0]), resolution_m=abs(tr.a),
                elev_m=[float(np.nanmin(a)), float(np.nanmax(a))], nan_frac=float(np.isnan(a).mean()),
                files=dict(tif="dem.tif", npz="dem.npz"),
                sizes_mb={f: round(os.path.getsize(os.path.join(out, f)) / 1e6, 2) for f in ("dem.tif", "dem.npz")},
                license="Public domain (USGS)", fetched_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    meta.update(extra)
    return meta


def fetch_tnm(bbox, epsg, res):
    import requests
    import rasterio
    from rasterio.warp import transform_bounds
    s, w, n, e = bbox
    x0, y0, x1, y1 = transform_bounds("EPSG:4326", f"EPSG:{epsg}", w, s, e, n, densify_pts=21)
    x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)
    W, H = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
    r = requests.get(TNM_IMG, params=dict(
        bbox=f"{x0},{y0},{x1},{y1}", bboxSR=epsg, imageSR=epsg, size=f"{W},{H}", format="tiff",
        pixelType="F32", noDataInterpretation="esriNoDataMatchAny",
        interpolation="RSP_BilinearInterpolation", f="image"), headers={"User-Agent": UA}, timeout=600)
    if r.status_code != 200 or "tif" not in r.headers.get("content-type", "").lower():
        raise RuntimeError(f"HTTP {r.status_code} {r.headers.get('content-type')} {r.text[:300]!r}")
    from rasterio.io import MemoryFile
    with MemoryFile(r.content) as mf, mf.open() as src:
        a = src.read(1).astype(np.float32)
        tr, nd = src.transform, src.nodata
    if nd is not None:
        a[a == nd] = np.nan
    a[(a < -1000) | (a > 9000)] = np.nan
    return a, tr


def fetch_pc(bbox, collection):
    import planetary_computer
    import pystac_client
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import transform_bounds
    s, w, n, e = bbox
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                                    modifier=planetary_computer.sign_inplace)
    items = list(cat.search(collections=[collection], bbox=[w, s, e, n]).items())
    if not items:
        raise RuntimeError(f"no {collection} items")
    g = min(i.properties.get("gsd", 99) for i in items)
    best = [i for i in items if i.properties.get("gsd", 99) == g]
    srcs = [rasterio.open(i.assets["data"].href) for i in best]
    bd = transform_bounds("EPSG:4326", srcs[0].crs, w, s, e, n)
    a, tr = merge(srcs, bounds=bd)
    return a[0].astype(np.float32), tr, srcs[0].crs, [i.id for i in best]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course-dir", default="course_data/spirit_hollow")
    ap.add_argument("--margin", type=float, default=200.0)
    ap.add_argument("--res", type=float, default=1.0)
    ap.add_argument("--out", default="course_data/elevation/spirit_hollow")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bbox = course_bbox(a.course_dir)
    padded = pad_bbox(bbox, a.margin)
    epsg = utm_epsg((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    extra = dict(course_bbox_snwe=bbox, margin_m=a.margin, padded_bbox_snwe=padded)
    log("bbox", padded, "epsg", epsg)
    extra["tnm_products"] = tnm_products(padded)
    errs = []
    meta = None
    for attempt in range(3):
        try:
            z, tr = fetch_tnm(padded, epsg, a.res)
            if np.isnan(z).mean() > 0.2:
                raise RuntimeError(f"too much nodata {np.isnan(z).mean():.2f}")
            meta = write_outputs(a.out, z, epsg, tr,
                                 "USGS 3DEP via The National Map 3DEPElevation ImageServer exportImage "
                                 f"(best available, resampled bilinear to {a.res} m)", extra)
            break
        except Exception as ex:
            errs.append(repr(ex)[:300])
            log("TNM attempt failed:", errs[-1])
            time.sleep(15 * (attempt + 1))
    if meta is None:
        for coll in ("3dep-seamless", "cop-dem-glo-30"):
            try:
                z, tr, crs, ids = fetch_pc(padded, coll)
                meta = write_outputs(a.out, z, crs.to_epsg(), tr, f"Planetary Computer '{coll}'",
                                     dict(extra, pc_items=ids))
                break
            except Exception as ex:
                errs.append(f"{coll}: {ex!r}"[:300])
                log(errs[-1])
    if meta is None:
        raise SystemExit("all DEM sources failed: " + "; ".join(errs))
    meta["errors"] = errs
    json.dump(meta, open(os.path.join(a.out, "georef.json"), "w"), indent=1)
    log(json.dumps({k: v for k, v in meta.items() if k != "tnm_products"}, indent=1))


if __name__ == "__main__":
    main()
