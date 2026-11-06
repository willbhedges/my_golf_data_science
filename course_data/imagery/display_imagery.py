"""Display imagery for a course page: the sharpest leaf-on NAIP year over the course, used for the photos only (the
truth map, picks and wind grids are unchanged). Runs on GitHub Actions (the sandbox cannot reach Planetary Computer).

  python course_data/imagery/display_imagery.py scan  --slug S [--out course_data/imagery/years/S_display.json]
  python course_data/imagery/display_imagery.py fetch --slug S --year best|YYYY --dir /tmp/disp_S

scan: every NAIP year over the course box (Planetary Computer STAC: dates, ground sample distance, coverage, leaf-on)
plus a sharpness measure on one 240 x 240 m patch at the course centre, every year resampled to the same 0.3 m grid
(the mean absolute Laplacian of the grey image: a 0.6 m year upsampled scores well below a 0.3 m year of the same
ground), and the USDA APFO NAIP image service's newest catalog item at the centre (a year newer than the STAC
catalog shows up there first). best = among leaf-on years covering the course, the smallest GSD, then the sharpest,
then the newest.

fetch: fetch_imagery.py --year Y --lo-res <gsd> --no-dem over the package box (+150 m: the hole frames reach past it) into --dir (not committed).
v2_course.py reads it through config "display_imagery" {"year": Y} (prepare renders the page photos from it).
"""
import argparse
import json
import math
import os
import subprocess
import sys
import urllib.parse
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, HERE)


def course_bbox(slug):
    """(S, W, N, E) of the package course box."""
    p = json.load(open(os.path.join(CD, "packages", slug, "package.json")))
    w, s, e, n = p["course"]["bbox"]
    return s, w, n, e


def leaf_on(date):
    m = int(date[5:7])
    return 5 <= m <= 9


def sharpness(its, center, half_m=120.0, res=0.3):
    """Mean |Laplacian| of the grey patch around center (lon, lat) at `res` m, every year on the same grid."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import transform
    from rasterio.windows import from_bounds
    from shapely.geometry import Point, shape
    import cv2
    it = next((i for i in its if shape(i.geometry).contains(Point(center))), its[0])
    n = int(round(2 * half_m / res))
    with rasterio.open(it.assets["image"].href) as src:
        xs, ys = transform("EPSG:4326", src.crs, [center[0]], [center[1]])
        win = from_bounds(xs[0] - half_m, ys[0] - half_m, xs[0] + half_m, ys[0] + half_m, src.transform)
        out = src.read([1, 2, 3], window=win, out_shape=(3, n, n), resampling=Resampling.bilinear,
                       boundless=True, fill_value=0).astype(np.float32)
    g = out.mean(0)
    valid = (out > 0).all(0)
    if valid.mean() < 0.5:
        return None
    lap = np.abs(cv2.Laplacian(g, cv2.CV_32F, ksize=1))
    return round(float(lap[valid].mean()), 3)


def apfo(center):
    """USDA APFO NAIP image service, catalog items at the point (newest first): year / date / GSD attributes."""
    base = "https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/identify"
    q = dict(geometry=json.dumps(dict(x=center[0], y=center[1], spatialReference=dict(wkid=4326))),
             geometryType="esriGeometryPoint", returnGeometry="false", returnCatalogItems="true", f="json")
    try:
        r = urllib.request.urlopen(base + "?" + urllib.parse.urlencode(q), timeout=40).read()
        d = json.loads(r)
        items = [f.get("attributes", {}) for f in (d.get("catalogItems") or {}).get("features", [])]
        keep = [{k: v for k, v in a.items() if any(t in k.lower() for t in ("year", "date", "gsd", "res", "name",
                                                                              "state", "vintage"))} for a in items]
        return dict(ok=True, items=keep[:12])
    except Exception as e:                                   # noqa: BLE001
        return dict(ok=False, error=str(e)[:300])


def scan(slug, out=None):
    import naip_years as NY
    bbox = course_bbox(slug)
    s, w, n, e = bbox
    center = ((w + e) / 2, (s + n) / 2)
    years = NY.list_years(bbox)
    rows = []
    for y in years:
        r = dict(year=y["year"], dates=y["dates"], coverage=y["coverage"], gsd_m=y["gsd_m"],
                 leaf_on=all(leaf_on(d) for d in y["dates"]), items=[it.id for it in y["items"]])
        try:
            r["sharpness"] = sharpness(y["items"], center)
        except Exception as ex:                              # noqa: BLE001
            r["sharpness"], r["error"] = None, repr(ex)[:200]
        print(r, flush=True)
        rows.append(r)
    ok = [r for r in rows if r["leaf_on"] and r["coverage"] > 0.99 and r.get("gsd_m")]
    best = min(ok, key=lambda r: (round(float(r["gsd_m"]), 2), -(r.get("sharpness") or 0), -r["year"])) if ok else None
    doc = dict(schema="display_years/1", slug=slug, bbox_snwe=list(bbox), center=list(center), years=rows,
               best=best and best["year"], rule="leaf-on (May-Sep), covers the course; smallest GSD, then the "
               "sharpest (mean |Laplacian| at 0.3 m on a 240 m centre patch), then the newest",
               apfo=apfo(center))
    out = out or os.path.join(HERE, "years", f"{slug}_display.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(doc, open(out, "w"), indent=1)
    print("best:", doc["best"], json.dumps(doc["apfo"])[:600])
    return doc


def fetch(slug, year, d, margin=150.0):
    if str(year).lower() == "naipplus":
        try:
            return fetch_naipplus(slug, d, margin)
        except Exception as ex:                              # noqa: BLE001
            # the page must still build (its other fixes ship): fall back to the best Planetary Computer NAIP year
            print("!! NAIP Plus fetch failed, falling back to a 0.6 m NAIP year:", repr(ex)[:300], flush=True)
            for f in ("naip_rgb.tif", "georef.json"):
                if os.path.exists(os.path.join(d, f)):
                    os.remove(os.path.join(d, f))
            # config display_imagery "fallback_year" (Eagle Knoll: 2022, registered on the truth map; 2020 is shifted
            # 10-15 yds on 17), else the scan's best year
            try:
                cfgp = os.path.join(CD, "courses", slug, "config.json")
                year = str((json.load(open(cfgp)).get("display_imagery") or {}).get("fallback_year") or "best")
            except Exception:                                # noqa: BLE001
                year = "best"
    if year == "best":
        p = os.path.join(HERE, "years", f"{slug}_display.json")
        doc = json.load(open(p)) if os.path.exists(p) else scan(slug)
        year = doc["best"]
    s, w, n, e = course_bbox(slug)
    gsd = 0.3
    try:
        doc = json.load(open(os.path.join(HERE, "years", f"{slug}_display.json")))
        gsd = float(next(r["gsd_m"] for r in doc["years"] if r["year"] == int(year)))
    except Exception:                                        # noqa: BLE001
        pass
    os.makedirs(d, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, "fetch_imagery.py"), "--bbox", f"{s},{w},{n},{e}",
                    "--margin", str(margin), "--year", str(year), "--lo-res", str(max(gsd, 0.3)), "--no-dem",
                    "--name", slug, "--out", d], check=True)
    g = json.load(open(os.path.join(d, "georef.json")))["imagery"]
    print("display imagery:", d, g.get("year"), g.get("acquired"), g.get("resolution_m"))
    return d


NAIPPLUS = "https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer"


def _naipplus_tile(x0, y1, tw, th, res, epsg, log=print, depth=0):
    """One exportImage tile (tw x th px, top-left corner x0, y1 in EPSG:epsg) -> uint8 (3, th, tw). PNG24 first (the
    probe's 2000 px JPEG worked; 3600 px TIFFs timed out at the gateway, run 42246942328), TIFF as the second format;
    retries back off; a tile that keeps failing is fetched as four quarters (down to ~400 px)."""
    import io
    import time
    from PIL import Image
    bb = f"{x0},{y1 - th * res},{x0 + tw * res},{y1}"
    last = None
    for attempt in range(5):
        fmt = "png24" if attempt % 2 == 0 else "tiff"
        q = urllib.parse.urlencode(dict(bbox=bb, bboxSR=epsg, imageSR=epsg, size=f"{tw},{th}", format=fmt,
                                        pixelType="U8", bandIds="0,1,2", interpolation="RSP_CubicConvolution",
                                        f="image"))
        try:
            raw = urllib.request.urlopen(f"{NAIPPLUS}/exportImage?{q}", timeout=150).read()
            if fmt == "tiff":
                import rasterio
                with rasterio.open(io.BytesIO(raw)) as t:
                    a = t.read()[:3]
            else:
                a = np.moveaxis(np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")), -1, 0)
            if a.shape[1] < th or a.shape[2] < tw:
                raise ValueError(f"tile came back {a.shape}, asked {th}x{tw}")
            return a[:, :th, :tw]
        except Exception as ex:                               # noqa: BLE001
            last = ex
            log(f"  tile {tw}x{th} at {x0:.0f},{y1:.0f} attempt {attempt} ({fmt}): {str(ex)[:160]}")
            time.sleep(min(60, 8 * (attempt + 1)))
    if min(tw, th) < 800:
        raise RuntimeError(f"NAIP Plus tile failed: {last}")
    out = np.zeros((3, th, tw), np.uint8)                     # split in four and try again
    hw, hh = tw // 2, th // 2
    for c0, cw in ((0, hw), (hw, tw - hw)):
        for r0, rh in ((0, hh), (hh, th - hh)):
            out[:, r0:r0 + rh, c0:c0 + cw] = _naipplus_tile(x0 + c0 * res, y1 - r0 * res, cw, rh, res, epsg, log,
                                                            depth + 1)
    return out


def fetch_naipplus(slug, d, margin=150.0, res=0.3, tile=1500, epsg=26915, workers=3):
    """USGS NAIP Plus (The National Map: NAIP + state high-resolution orthoimagery, public domain) at `res` m over the
    package box + margin, mosaicked from exportImage tiles (service limit 4000 px; 1500 px tiles, 3 at a time) into
    d/naip_rgb.tif + georef.json, the layout v2_course's display imagery reads. Missouri carries 0.3 m imagery here,
    twice the detail of the 0.6 m Planetary Computer NAIP years (Eagle Knoll 2026-11-06: the page photos looked
    blurry)."""
    from concurrent.futures import ThreadPoolExecutor
    import rasterio
    from rasterio.transform import from_origin
    from pyproj import Transformer
    s, w, n, e = course_bbox(slug)
    T = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    xs, ys = zip(*[T.transform(x, y) for x, y in ((w, s), (w, n), (e, s), (e, n))])
    x0, x1 = math.floor(min(xs) - margin), math.ceil(max(xs) + margin)
    y0, y1 = math.floor(min(ys) - margin), math.ceil(max(ys) + margin)
    W, H = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
    out = np.zeros((3, H, W), np.uint8)
    jobs = [(r0, c0, min(tile, W - c0), min(tile, H - r0)) for r0 in range(0, H, tile) for c0 in range(0, W, tile)]
    print(f"NAIP Plus: {W} x {H} px at {res} m, {len(jobs)} tiles", flush=True)

    def one(j):
        r0, c0, tw, th = j
        a = _naipplus_tile(x0 + c0 * res, y1 - r0 * res, tw, th, res, epsg)
        out[:, r0:r0 + th, c0:c0 + tw] = a
        print("tile", r0, c0, a.shape, flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, jobs))
    if (out.max(0) == 0).mean() > 0.02:
        print(f"! {(out.max(0) == 0).mean():.1%} of the mosaic is empty (no data)")
    os.makedirs(d, exist_ok=True)
    tr = from_origin(x0, y1, res, res)
    prof = dict(driver="GTiff", width=W, height=H, count=3, dtype="uint8", crs=f"EPSG:{epsg}", transform=tr,
                tiled=True, blockxsize=512, blockysize=512, compress="deflate", predictor=2)   # lossless: no extra JPEG pass
    with rasterio.open(os.path.join(d, "naip_rgb.tif"), "w", **prof) as dst:
        dst.write(out)
    acq, items = [], []
    try:                                                     # acquisition date of the mosaic item at the centre
        cx, cy = T.transform((w + e) / 2, (s + n) / 2)
        q = urllib.parse.urlencode(dict(geometry=f"{cx},{cy}", geometryType="esriGeometryPoint", sr=epsg,
                                        returnCatalogItems="true", f="json"))
        j = json.load(urllib.request.urlopen(f"{NAIPPLUS}/identify?{q}", timeout=60))
        for f in (j.get("catalogItems") or {}).get("features", [])[:3]:
            a = f.get("attributes", {})
            items.append({k: a.get(k) for k in ("Name", "Year", "agency", "resolution_value", "resolution_units")})
            if a.get("acquisition_date"):
                import datetime
                acq.append(datetime.datetime.utcfromtimestamp(a["acquisition_date"] / 1000).strftime("%Y-%m-%d"))
    except Exception as ex:                                  # noqa: BLE001
        print("identify failed:", ex)
    year = (items[0].get("Year") if items else None)
    meta = dict(course=slug, imagery=dict(source="USGS NAIP Plus (The National Map, public domain)", year=year,
                acquired=acq or [f"NAIP Plus {year or ''}".strip()], items=items, gsd_m=res, resolution_m=res, bands=["red", "green", "blue"],
                crs=f"EPSG:{epsg}", epsg=epsg, width=W, height=H, transform=list(tr)[:6],
                files=dict(rgb="naip_rgb.tif")))
    json.dump(meta, open(os.path.join(d, "georef.json"), "w"), indent=1)
    print("display imagery (NAIP Plus):", d, W, H, year, acq, items[:1])
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["scan", "fetch"])
    ap.add_argument("--slug", required=True)
    ap.add_argument("--year", default="best")
    ap.add_argument("--dir")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "scan":
        scan(a.slug, a.out)
    else:
        fetch(a.slug, a.year, a.dir or f"/tmp/disp_{a.slug}")


if __name__ == "__main__":
    main()
