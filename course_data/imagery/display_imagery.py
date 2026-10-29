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
