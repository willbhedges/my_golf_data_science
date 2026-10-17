"""Fetch free, overlay-free overhead imagery (+ elevation) for a golf course.

  python course_data/imagery/fetch_imagery.py --course-dir course_data/spirit_hollow \
      --out course_data/imagery/spirit_hollow
  python course_data/imagery/fetch_imagery.py --name "Spirit Hollow Golf Course, Burlington, Iowa" --out ...
  python course_data/imagery/fetch_imagery.py --bbox S,W,N,E --out ...
  python course_data/imagery/fetch_imagery.py --request course_data/requests/imagery_ia_spirit_hollow.json
      request/1 file (ARCHITECTURE.md 9.4): {"kind": "imagery", "course", "state", "near", optional
      "bbox": [W,S,E,N], "slug", "out"}; bbox from the request, else the platform package
      (course_data/packages/<STATE>/<slug>/package.json), else course_data/<slug>/summary.json, else
      Nominatim; output defaults to course_data/imagery/<slug>.

Bounding box: from <course-dir>/summary.json (OSM course + features, written by
course_data/fetch_course.py), an explicit --bbox, or a Nominatim geocode of --name; then
padded by --margin metres (default 100).

Outputs (in --out):
  naip_rgb.tif       one USDA NAIP year, R,G,B, native resolution (0.3-0.6 m), Cloud-Optimised. Which year:
                     --year auto (default) scores every NAIP year over the course's OSM turf (--osm) and takes
                     the greenest leaf-on one (naip_years.py; recorded in georef.json imagery.selection);
                     without --osm, or with --year latest, the newest covering year (the old rule)
                     GeoTIFF, JPEG q90 (YCbCr), with overviews
  naip_nir.tif       the NAIP near-infrared band, same grid, single-band COG (JPEG q92)
  naip_rgb_lo.jpg    the same imagery resampled to --lo-res metres (default 0.6) as plain JPEG,
  naip_nir_lo.jpg    readable with only Pillow; georeferenced by georef.json["imagery"]["lo"]
  dem.tif            USGS 3DEP bare-earth DEM (1 m if available), float32 metres, same CRS
  preview.jpg        small RGB overview
  georef.json        CRS, affine transforms (GDAL order a,b,c,d,e,f: x = c + a*col + b*row,
                     y = f + d*col + e*row, pixel-corner convention), sizes, bounds, provenance
Fallback: if NAIP fails, Sentinel-2 L2A (10 m, least-cloudy summer scene) -> s2_rgb.tif/s2_nir.tif.

Runs on GitHub Actions (.github/workflows/imagery_fetch.yml); the sandbox can't reach these hosts.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import time
import traceback

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))           # naip_years

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
UA = "my_golf_data_science-imagery/1.0 (github actions; golf course strategy research)"


def log(*a):
    print(*a, flush=True)


# --------------------------------------------------------------------------- bbox
def geocode(q):
    import requests
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params=dict(q=q, format="json", limit=5),
                     headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    res = r.json()
    if not res:
        raise SystemExit(f"Nominatim found nothing for {q!r}")
    for c in res:
        log("  nominatim:", c.get("display_name"), c.get("class"), c.get("type"), c.get("boundingbox"))
    best = next((c for c in res if c.get("type") == "golf_course"), res[0])
    s, n, w, e = map(float, best["boundingbox"])
    return (s, w, n, e), best.get("display_name")


def bbox_from_course_dir(d):
    sm = json.load(open(os.path.join(d, "summary.json")))
    boxes = []
    if sm.get("bbox_wgs84_snwe"):
        boxes.append(sm["bbox_wgs84_snwe"])
    b = (sm.get("course") or {}).get("bounds")
    if b:
        boxes.append([b["minlat"], b["minlon"], b["maxlat"], b["maxlon"]])
    if not boxes:
        raise SystemExit("summary.json has no bbox")
    a = np.array(boxes)
    return ((a[:, 0].min(), a[:, 1].min(), a[:, 2].max(), a[:, 3].max()),
            (sm.get("course") or {}).get("name"))


def utm_epsg(lat, lon):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1


def pad_bbox(bbox, margin_m):
    s, w, n, e = bbox
    lat = (s + n) / 2
    dlat = margin_m / 111_320.0
    dlon = margin_m / (111_320.0 * math.cos(math.radians(lat)))
    return (s - dlat, w - dlon, n + dlat, e + dlon)


# --------------------------------------------------------------------------- writers
def write_cog(path, arr, crs, transform, jpeg_quality=None, nodata=None, overviews=True):
    """Write a COG; JPEG for uint8 imagery, deflate otherwise."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.shutil import copy as rcopy
    count, h, w = arr.shape
    tmp = path + ".tmp.tif"
    prof = dict(driver="GTiff", height=h, width=w, count=count, dtype=arr.dtype, crs=crs,
                transform=transform, tiled=True, blockxsize=512, blockysize=512, nodata=nodata)
    if jpeg_quality:
        prof.update(compress="jpeg", jpeg_quality=jpeg_quality)
        if count == 3:
            prof.update(photometric="ycbcr")
    else:
        prof.update(compress="deflate", predictor=3 if arr.dtype.kind == "f" else 2)
    with rasterio.open(tmp, "w", **prof) as dst:
        dst.write(arr)
        if overviews:
            dst.build_overviews([2, 4, 8, 16], Resampling.average)
    try:
        opts = dict(driver="COG", BLOCKSIZE=512, OVERVIEWS="FORCE_USE_EXISTING")
        if jpeg_quality:
            opts.update(COMPRESS="JPEG", QUALITY=jpeg_quality)
        else:
            opts.update(COMPRESS="DEFLATE", PREDICTOR="YES")
        rcopy(tmp, path, **opts)
        os.remove(tmp)
        kind = "COG"
    except Exception as ex:                                  # old GDAL: keep the tiled GTiff
        log("  COG driver failed, keeping tiled GTiff:", ex)
        os.replace(tmp, path)
        kind = "tiled GTiff"
    return kind, round(os.path.getsize(path) / 1e6, 2)


def tf_list(t):
    return [t.a, t.b, t.c, t.d, t.e, t.f]


def write_lo(arr, transform, res_lo, out_dir, stem, quality=90):
    """Area-average down to res_lo metres and save plain JPEG(s) for Pillow-only users."""
    from PIL import Image
    from affine import Affine
    k = res_lo / abs(transform.a)
    if k <= 1.05:
        k = 1.0
    h, w = arr.shape[1:]
    W, H = int(round(w / k)), int(round(h / k))
    out = []
    for b in range(arr.shape[0]):
        im = Image.fromarray(arr[b]).resize((W, H), Image.BOX if k > 1 else Image.NEAREST)
        out.append(np.asarray(im))
    lo = np.stack(out)
    tr = transform * Affine.scale(w / W, h / H)
    files = {}
    if lo.shape[0] >= 3:
        p = os.path.join(out_dir, f"{stem}_rgb_lo.jpg")
        Image.fromarray(np.ascontiguousarray(np.moveaxis(lo[:3], 0, -1))).save(p, quality=quality, optimize=True)
        files["rgb"] = os.path.basename(p)
    if lo.shape[0] >= 4:
        p = os.path.join(out_dir, f"{stem}_nir_lo.jpg")
        Image.fromarray(lo[3]).save(p, quality=quality, optimize=True)
        files["nir"] = os.path.basename(p)
    return dict(files=files, width=W, height=H, transform=tf_list(tr), resolution_m=round(abs(tr.a), 4))


# --------------------------------------------------------------------------- NAIP
def stac_client():
    import planetary_computer
    import pystac_client
    return pystac_client.Client.open(STAC, modifier=planetary_computer.sign_inplace)


def latest_covering(years):
    """The old rule (now `--year latest`): the newest year whose acquisitions cover the box, else the newest."""
    for y in reversed(years):
        if y["coverage"] > 0.995:
            return y
    return years[-1]


def choose_year(years, want="auto", osm=None, bbox=None, current=None, scorer=None):
    """years: naip_years.list_years() rows (oldest first) -> (row, selection record).
    want: "auto" = naip_years.select (best-scoring leaf-on year on the course's OSM turf; needs `osm`, a GeoJSON
    FeatureCollection), "latest" = the old newest-covering-year rule, or a year. scorer(row) -> candidate dict
    (default: read the year at naip_years.SCORE_RES and score it)."""
    import naip_years as NY
    if str(want).isdigit():
        row = next((y for y in years if y["year"] == int(want)), None)
        if row is None:
            raise RuntimeError(f"NAIP {want} not available here ({[y['year'] for y in years]})")
        return row, dict(schema="naip_years/1", chosen=row["year"], reason=f"requested year {want}", candidates=[])
    if want == "latest" or not osm:
        row = latest_covering(years)
        return row, dict(schema="naip_years/1", chosen=row["year"], method="newest covering year",
                         reason=f"{row['year']}: newest NAIP year covering the course (no year scoring: "
                                f"{'requested' if want == 'latest' else 'no OSM map to score on'})", candidates=[])
    polys = NY.turf_polygons(osm)

    def default_scorer(y):
        arr, crs, tr = NY.read_year(y["items"], bbox)
        return NY._score_array(arr, crs, tr, polys, {})
    cands = []
    for y in years:
        c = dict(year=y["year"], dates=y["dates"], coverage=y["coverage"], gsd_m=y["gsd_m"])
        try:
            c.update((scorer or default_scorer)(y))
        except Exception as ex:                                  # noqa: BLE001
            c.update(has_nir=False, error=repr(ex)[:300])
        log(f"  NAIP {c['year']} {c['dates']} cover {c['coverage']:.3f} gsd {c.get('gsd_m')}: turf NDVI "
            f"{c.get('turf_ndvi')} bare {c.get('bare_turf')} greens bare {c.get('greens_bare_n')} haze {c.get('haze')}")
        cands.append(c)
    best, reason, cands = NY.select(cands, current)
    if best is None:
        row = latest_covering(years)
        return row, dict(NY.record(None, f"{reason}; fell back to the newest covering year {row['year']}", cands),
                         chosen=row["year"])
    return next(y for y in years if y["year"] == best["year"]), NY.record(best, reason, cands)


def fetch_naip(bbox, out_dir, lo_res, year="auto", osm=None, current=None):
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import transform_bounds
    import naip_years as NY

    s, w, n, e = bbox
    years = NY.list_years(bbox)
    if not years:
        raise RuntimeError("no NAIP items intersect the bbox")
    log("  NAIP years:", [(y["year"], y["coverage"]) for y in years])
    row, selection = choose_year(years, year, osm, bbox, current)
    yr, its = row["year"], row["items"]
    log(f"  chosen NAIP {yr}: {selection.get('reason')}")
    srcs = [rasterio.open(it.assets["image"].href) for it in its]
    crs = srcs[0].crs
    srcs = [sr for sr in srcs if sr.crs == crs]
    bounds = transform_bounds("EPSG:4326", crs, w, s, e, n, densify_pts=21)
    res = abs(srcs[0].transform.a)
    x0 = math.floor(bounds[0] / res) * res                # snap to the native pixel grid
    y0 = math.floor(bounds[1] / res) * res
    x1 = math.ceil(bounds[2] / res) * res
    y1 = math.ceil(bounds[3] / res) * res
    log(f"  merging {len(srcs)} tiles at {res} m, CRS {crs}")
    arr, tr = merge(srcs, bounds=(x0, y0, x1, y1), res=res, nodata=0)
    nb = arr.shape[0]
    log("  mosaic", arr.shape, arr.dtype)
    kind, mb_rgb = write_cog(os.path.join(out_dir, "naip_rgb.tif"), arr[:3], crs, tr, jpeg_quality=90)
    files = {"rgb": "naip_rgb.tif"}
    sizes = {"naip_rgb.tif": mb_rgb}
    if nb >= 4:
        _, mb_nir = write_cog(os.path.join(out_dir, "naip_nir.tif"), arr[3:4], crs, tr, jpeg_quality=92)
        files["nir"] = "naip_nir.tif"
        sizes["naip_nir.tif"] = mb_nir
    lo = write_lo(arr, tr, lo_res, out_dir, "naip")
    for f in lo["files"].values():
        sizes[f] = round(os.path.getsize(os.path.join(out_dir, f)) / 1e6, 2)
    from PIL import Image
    prev = Image.fromarray(np.ascontiguousarray(np.moveaxis(arr[:3], 0, -1)))
    kp = max(1, math.ceil(max(prev.size) / 1600))
    prev.resize((prev.width // kp, prev.height // kp), Image.LANCZOS).save(
        os.path.join(out_dir, "preview.jpg"), quality=85)
    acq = sorted({it.datetime.date().isoformat() for it in its})
    return dict(
        source="USDA NAIP via Microsoft Planetary Computer (collection 'naip')",
        year=yr, years_available=[y["year"] for y in years], acquired=acq, items=[it.id for it in its],
        selection=selection,
        gsd_m=its[0].properties.get("gsd"), resolution_m=round(res, 4),
        bands=["red", "green", "blue"] + (["nir"] if nb >= 4 else []),
        crs=crs.to_string(), epsg=crs.to_epsg(), width=int(arr.shape[2]), height=int(arr.shape[1]),
        transform=tf_list(tr), bounds_crs=[x0, y0, x1, y1], files=files, format=kind,
        lo=lo, sizes_mb=sizes, preview="preview.jpg", preview_scale=kp,
        license="Public domain (USDA FSA)")


# --------------------------------------------------------------------------- Sentinel-2 fallback
def fetch_s2(bbox, out_dir):
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import transform_bounds
    s, w, n, e = bbox
    cat = stac_client()
    yr = dt.date.today().year
    items = []
    for y in (yr, yr - 1, yr - 2):
        items = list(cat.search(collections=["sentinel-2-l2a"], bbox=[w, s, e, n],
                                datetime=f"{y}-05-01/{y}-09-30",
                                query={"eo:cloud_cover": {"lt": 10}}).items())
        if items:
            break
    if not items:
        raise RuntimeError("no Sentinel-2 scenes")
    it = min(items, key=lambda i: i.properties["eo:cloud_cover"])
    bands = []
    tr = crs = None
    for b in ("B04", "B03", "B02", "B08"):
        with rasterio.open(it.assets[b].href) as src:
            crs = src.crs
            bd = transform_bounds("EPSG:4326", crs, w, s, e, n)
            a, tr = merge([src], bounds=bd)
            bands.append(a[0])
    arr = np.stack(bands).astype(np.float32)
    rgb = np.clip(arr[:3] / 3000 * 255, 0, 255).astype(np.uint8)
    nir = np.clip(arr[3:4] / 5000 * 255, 0, 255).astype(np.uint8)
    write_cog(os.path.join(out_dir, "s2_rgb.tif"), rgb, crs, tr, overviews=False)
    write_cog(os.path.join(out_dir, "s2_nir.tif"), nir, crs, tr, overviews=False)
    return dict(source="Sentinel-2 L2A via Planetary Computer", item=it.id,
                acquired=it.datetime.date().isoformat(), resolution_m=10, crs=crs.to_string(),
                epsg=crs.to_epsg(), width=int(arr.shape[2]), height=int(arr.shape[1]),
                transform=tf_list(tr), files={"rgb": "s2_rgb.tif", "nir": "s2_nir.tif"},
                bands=["red", "green", "blue", "nir"])


# --------------------------------------------------------------------------- DEM
def fetch_dem(bbox, out_dir, epsg, res=1.0):
    """USGS 3DEP via The National Map ImageServer (1 m where lidar exists); PC 3dep-seamless fallback."""
    import rasterio
    import requests
    from rasterio.crs import CRS
    from rasterio.warp import transform_bounds
    s, w, n, e = bbox
    x0, y0, x1, y1 = transform_bounds("EPSG:4326", f"EPSG:{epsg}", w, s, e, n, densify_pts=21)
    x0, y0 = math.floor(x0), math.floor(y0)
    x1, y1 = math.ceil(x1), math.ceil(y1)
    W, H = int((x1 - x0) / res), int((y1 - y0) / res)
    url = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"
    path = os.path.join(out_dir, "dem.tif")
    errs = []
    for attempt in range(3):
        try:
            r = requests.get(url, params=dict(
                bbox=f"{x0},{y0},{x1},{y1}", bboxSR=epsg, imageSR=epsg, size=f"{W},{H}",
                format="tiff", pixelType="F32", noDataInterpretation="esriNoDataMatchAny",
                interpolation="RSP_BilinearInterpolation", f="image"),
                headers={"User-Agent": UA}, timeout=300)
            ctype = r.headers.get("content-type", "")
            if r.status_code != 200 or "tif" not in ctype.lower():
                raise RuntimeError(f"HTTP {r.status_code} {ctype} {r.text[:300]!r}")
            raw = path + ".raw.tif"
            with open(raw, "wb") as fh:
                fh.write(r.content)
            with rasterio.open(raw) as src:
                a = src.read(1).astype(np.float32)
                tr = src.transform
                crs = src.crs or CRS.from_epsg(epsg)
                nd = src.nodata
            if nd is not None:
                a[a == nd] = np.nan
            a[a < -1000] = np.nan
            kind, mb = write_cog(path, a[None], crs, tr, nodata=float("nan"))
            os.remove(raw)
            return dict(source="USGS 3DEP (The National Map 3DEPElevation ImageServer, best available)",
                        resolution_m=res, crs=f"EPSG:{epsg}", width=W, height=H, transform=tf_list(tr),
                        file="dem.tif", size_mb=mb, format=kind,
                        elev_m=[float(np.nanmin(a)), float(np.nanmax(a))],
                        nan_frac=float(np.isnan(a).mean()), license="Public domain (USGS)")
        except Exception as ex:
            errs.append(repr(ex)[:300])
            log("  TNM DEM attempt failed:", errs[-1])
            time.sleep(10 * (attempt + 1))
    from rasterio.merge import merge                      # fallback: PC 3dep-seamless (10 m)
    cat = stac_client()
    items = list(cat.search(collections=["3dep-seamless"], bbox=[w, s, e, n]).items())
    items = sorted(items, key=lambda i: i.properties.get("gsd", 99))
    if not items:
        raise RuntimeError("DEM failed: " + "; ".join(errs))
    best = [i for i in items if i.properties.get("gsd") == items[0].properties.get("gsd")]
    srcs = [rasterio.open(i.assets["data"].href) for i in best]
    bd = transform_bounds("EPSG:4326", srcs[0].crs, w, s, e, n)
    a, tr = merge(srcs, bounds=bd)
    kind, mb = write_cog(path, a[:1].astype(np.float32), srcs[0].crs, tr)
    return dict(source="USGS 3DEP seamless via Planetary Computer", resolution_m=abs(tr.a),
                crs=srcs[0].crs.to_string(), transform=tf_list(tr), file="dem.tif", size_mb=mb,
                tnm_errors=errs)


# --------------------------------------------------------------------------- request files
def _slugify(name):
    import re
    s = re.sub(r"[^a-z0-9 ]+", " ", str(name).lower().replace("&", " and "))
    s = re.sub(r"\b(golf|course|club|country|gc|cc|links|the|and|of|at|g\s*c|c\s*c|golf\s*club)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "_", " ".join(s.split())).strip("_") or "course"


def _find_bbox(obj):
    """Look for a [W,S,E,N] bbox in a package-like dict."""
    if isinstance(obj, dict):
        for k in ("bbox", "bbox_wgs84"):
            v = obj.get(k)
            if isinstance(v, (list, tuple)) and len(v) == 4:
                return list(map(float, v))
        for k in ("course", "resolve", "osm"):
            if k in obj:
                b = _find_bbox(obj[k])
                if b:
                    return b
    return None


def resolve_request(path, root):
    rq = json.load(open(path))
    slug = rq.get("slug") or _slugify(rq["course"])
    state = str(rq.get("state", "")).upper()
    out = rq.get("out") or os.path.join(root, "course_data", "imagery", slug)
    b = rq.get("bbox")
    src = "request"
    if not b:
        for pk in (os.path.join(root, "course_data", "packages", state, slug, "package.json"),
                   os.path.join(root, "courses", state, slug, "package.json")):
            if os.path.exists(pk):
                b, src = _find_bbox(json.load(open(pk))), pk
                if b:
                    break
    if b:
        w, s_, e, n = b
        return (s_, w, n, e), rq["course"], out, src
    cd = os.path.join(root, "course_data", slug)
    if os.path.exists(os.path.join(cd, "summary.json")):
        bb, label = bbox_from_course_dir(cd)
        return bb, label, out, cd
    q = f"{rq['course']}, {rq.get('state', '')}, USA"
    bb, label = geocode(q)
    return bb, label, out, "nominatim"


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course-dir")
    ap.add_argument("--bbox", help="S,W,N,E (WGS84)")
    ap.add_argument("--name")
    ap.add_argument("--margin", type=float, default=100.0)
    ap.add_argument("--lo-res", type=float, default=0.6)
    ap.add_argument("--max-mb", type=float, default=60.0)
    ap.add_argument("--no-dem", action="store_true")
    ap.add_argument("--request")
    ap.add_argument("--out")
    ap.add_argument("--year", default="auto",
                    help="NAIP year: auto (best-scoring leaf-on year on the --osm turf, naip_years.py), latest, or YYYY")
    ap.add_argument("--osm", help="osm.geojson of the course (golf=fairway / green / tee) for --year auto")
    a = ap.parse_args()
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    bbox_src = None
    if a.request:
        bbox, label, out, bbox_src = resolve_request(a.request, root)
        a.out = a.out or out
    if not a.out:
        raise SystemExit("--out (or --request) is required")
    os.makedirs(a.out, exist_ok=True)

    if a.request:
        pass
    elif a.bbox:
        bbox, label = tuple(map(float, a.bbox.split(","))), a.name
    elif a.course_dir and os.path.exists(os.path.join(a.course_dir, "summary.json")):
        bbox, label = bbox_from_course_dir(a.course_dir)
    elif a.name:
        bbox, label = geocode(a.name)
    else:
        raise SystemExit("need --bbox, --course-dir or --name")
    padded = pad_bbox(bbox, a.margin)
    lat, lon = (padded[0] + padded[2]) / 2, (padded[1] + padded[3]) / 2
    log("course:", label, "bbox", bbox, "padded", padded)

    meta = dict(course=label, bbox_wgs84_snwe=list(bbox), bbox_source=bbox_src or (
                    "--bbox" if a.bbox else a.course_dir or "nominatim"), margin_m=a.margin,
                request=a.request,
                padded_bbox_wgs84_snwe=list(padded),
                fetched_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                transform_convention="GDAL/affine: x = c + a*col + b*row, y = f + d*col + e*row "
                                     "(col,row of the pixel's top-left corner; +0.5 for centres)")
    prev = {}
    if os.path.exists(os.path.join(a.out, "georef.json")):
        try:
            prev = json.load(open(os.path.join(a.out, "georef.json")))
        except ValueError:
            prev = {}
    osm = json.load(open(a.osm)) if a.osm and os.path.exists(a.osm) else None
    try:
        meta["imagery"] = fetch_naip(padded, a.out, a.lo_res, year=a.year, osm=osm,
                                     current=(prev.get("imagery") or {}).get("year"))
    except Exception:
        tb = traceback.format_exc()
        log("NAIP failed:\n", tb)
        meta["naip_error"] = tb[-1500:]
        try:
            meta["imagery"] = fetch_s2(padded, a.out)
        except Exception:
            meta["s2_error"] = traceback.format_exc()[-1500:]
    if a.no_dem and prev.get("dem") and os.path.exists(os.path.join(a.out, prev["dem"].get("file", "dem.tif"))):
        meta["dem"] = prev["dem"]                                # NAIP-only refetch keeps the fetched DEM
    if not a.no_dem:
        try:
            epsg = (meta.get("imagery") or {}).get("epsg") or utm_epsg(lat, lon)
            meta["dem"] = fetch_dem(padded, a.out, epsg)
        except Exception:
            meta["dem_error"] = traceback.format_exc()[-1500:]
            log("DEM failed:\n", meta["dem_error"])

    for f in os.listdir(a.out):                              # leftovers from failed writes
        if f.endswith((".tmp.tif", ".raw.tif")):
            os.remove(os.path.join(a.out, f))
    total = sum(os.path.getsize(os.path.join(a.out, f)) for f in os.listdir(a.out)) / 1e6
    meta["total_mb"] = round(total, 1)
    if total > a.max_mb and "lo" in (meta.get("imagery") or {}):
        log(f"WARNING: {total:.1f} MB > {a.max_mb} MB; dropping the lo-res JPEGs")
        for f in meta["imagery"]["lo"]["files"].values():
            os.remove(os.path.join(a.out, f))
        meta["imagery"]["lo"]["dropped"] = True
    json.dump(meta, open(os.path.join(a.out, "georef.json"), "w"), indent=1)
    log(json.dumps(meta, indent=1)[:4000])
    if "imagery" not in meta:
        sys.exit(1)


if __name__ == "__main__":
    main()
