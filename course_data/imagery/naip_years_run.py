"""NAIP year selection for a course package, on GitHub Actions (.github/workflows/naip_years.yml).

  python course_data/imagery/naip_years_run.py <slug> [--apply] [--detect] [--out course_data/imagery/years]

1. score   every NAIP acquisition over the package's course box (naip_years.py via fetch_imagery.choose_year):
           -> <out>/<slug>.json (candidates, chosen year, reason)
2. detect  (--detect) does detection get better with that year, or with several years combined? The NAIP golf
           U-Net (course_data/segment/model.py, the model behind the package's segment fill) and the NIR water
           rule run on the package's current year, the chosen year and the next best years at 0.6 m; pixel IoU /
           precision / recall per class vs the course's OSM polygons inside its boundary (+20 m), painted
           fairway < tee < green < bunker < water as course_data/segment/evaluate.py. "combined" = the mean U-Net
           probabilities of the two (three) best-scoring years. -> <out>/<slug>.json["detect"]
3. apply   (--apply) the chosen year into packages/<slug>/imagery: a different year is re-fetched
           (fetch_imagery.py --year <chosen> --no-dem: the DEM stays), the same year only gets the selection
           record in georef.json. The package rebuild (package.build_request) and the plan re-run are separate
           workflow steps.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE, os.path.join(CD, "segment"), os.path.join(CD, "platform")]
import fetch_imagery as FI  # noqa: E402
import naip_years as NY  # noqa: E402

PAINT = ["fairway", "tee", "green", "bunker", "water"]
CLASSES = ["green", "tee", "fairway", "bunker", "water"]
CODE = {c: i + 1 for i, c in enumerate(CLASSES)}
DET_RES = 0.6
MARGIN_M = 100.0


def log(*a):
    print(*a, flush=True)


def course_box(pdir):
    course = json.load(open(os.path.join(pdir, "raw", "course.json")))
    w, s, e, n = course["bbox"]
    return FI.pad_bbox((s, w, n, e), MARGIN_M), course


def osm_class(p):
    g = p.get("golf")
    if g in ("green", "tee", "fairway", "bunker"):
        return g
    if g in ("water_hazard", "lateral_water_hazard") or p.get("natural") == "water" or p.get("water") \
            or p.get("landuse") in ("reservoir", "basin"):
        return "water"
    return None


def label_map(fc, crs, T, shape):
    from shapely.geometry import shape as shp
    lab = np.zeros(shape, np.uint8)
    for c in PAINT:
        gs = []
        for f in fc["features"]:
            if (f.get("geometry") or {}).get("type") in ("Polygon", "MultiPolygon") and osm_class(f["properties"]) == c:
                try:
                    gs.append(shp(f["geometry"]).buffer(0))
                except Exception:                                # noqa: BLE001
                    pass
        m = NY.rasterize_ll(gs, crs, T, shape)
        lab[m] = CODE[c]
    return lab


def region_mask(course, crs, T, shape):
    from shapely.geometry import shape as shp
    b = course.get("boundary")
    if not b:
        return np.ones(shape, bool)
    from pyproj import Transformer
    from rasterio.features import rasterize
    from shapely.ops import transform as stx
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    g = stx(tr.transform, shp(b).buffer(0)).buffer(20.0)
    return rasterize([g], out_shape=shape, transform=T).astype(bool)


def iou_table(pred, ref, region):
    out = {}
    for c in CLASSES:
        p, r = (pred == CODE[c]) & region, (ref == CODE[c]) & region
        inter, uni = int((p & r).sum()), int((p | r).sum())
        out[c] = dict(iou=round(inter / uni, 3) if uni else None,
                      precision=round(inter / p.sum(), 3) if p.sum() else None,
                      recall=round(inter / r.sum(), 3) if r.sum() else None)
    return out


def predict(mdl, arr):
    import model as M
    return M.predict_raster(mdl, arr, tta=True, log=None)


def labels_from(probs, water):
    import model as M
    am = probs.argmax(0)
    pred = np.zeros(am.shape, np.uint8)
    for c in ("green", "tee", "fairway", "bunker"):
        pred[am == M.CLASSES.index(c)] = CODE[c]
    if water is not None:
        pred[water] = CODE["water"]
    return pred


def detect_eval(years, cands, current, bbox, fc, course):
    """-> {runs: {label: iou table}, mean_iou: {label: mean over green/tee/fairway/bunker/water}}."""
    import model as M
    mdl, _, sha = M.load(threads=os.cpu_count())
    elig = sorted([c for c in cands if c.get("score") is not None], key=lambda c: -c["score"])
    want = [c["year"] for c in elig[:3]]
    if current and current not in want:
        want.append(int(current))
    rows = {y["year"]: y for y in years}
    grid = None
    probs, runs = {}, {}
    for yr in want:
        t = time.time()
        if grid is None:
            arr, crs, T = NY.read_year(rows[yr]["items"], bbox, res=DET_RES)
            grid = (crs, T, arr.shape[1:])
            ref = label_map(fc, crs, T, arr.shape[1:])
            region = region_mask(course, crs, T, arr.shape[1:])
        else:
            arr = read_on(rows[yr]["items"], grid)
        if arr.shape[0] < 4:
            continue
        p = predict(mdl, arr)
        wm, _ = M.nir_water(arr)
        probs[yr] = (p, wm, arr.any(axis=0))
        runs[str(yr)] = iou_table(labels_from(p, wm), ref, region)
        log(f"  detect {yr}: " + " ".join(f"{c} {v['iou']}" for c, v in runs[str(yr)].items()) + f" ({time.time() - t:.0f}s)")
    best =[c["year"] for c in elig if c["year"] in probs]
    for k in (2, 3):
        if len(best) >= k:
            ys = best[:k]
            pm = np.mean([probs[y][0] for y in ys], axis=0)
            wm = np.mean([probs[y][1].astype(np.float32) for y in ys], axis=0) >= 0.5
            runs["+".join(map(str, ys))] = iou_table(labels_from(pm, wm), ref, region)
    mean = {k: round(float(np.mean([v["iou"] for v in t.values() if v["iou"] is not None])), 3) for k, t in runs.items()}
    return dict(model=M.REPO, sha=str(sha)[:12], res_m=DET_RES, reference="OSM polygons inside the course boundary +20 m",
                runs=runs, mean_iou=mean, current=current)


def read_on(items, grid):
    """Read a year onto an existing (crs, transform, shape) grid."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    crs, T, shape = grid
    with rasterio.open(items[0].assets["image"].href) as s0:
        nb = min(s0.count, 4)
    out = np.zeros((nb,) + tuple(shape), np.uint8)
    for it in items:
        with rasterio.open(it.assets["image"].href) as src:
            for b in range(min(nb, src.count)):
                dst = np.zeros(shape, np.uint8)
                reproject(rasterio.band(src, b + 1), dst, src_nodata=0, dst_transform=T, dst_crs=crs, dst_nodata=0,
                          resampling=Resampling.average)
                out[b] = np.where(dst > 0, dst, out[b])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--detect", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "years"))
    a = ap.parse_args()
    pdir = os.path.join(CD, "packages", a.slug)
    import package as pk                                         # the imagery dir the package build reads
    req = json.load(open(os.path.join(ROOT, "course_data", "requests", f"package_{a.slug}.json")))
    img = pk.find_imagery(req, pdir, a.slug) or os.path.join(pdir, "imagery")
    osm_path = os.path.join(pdir, "raw", "osm.geojson")
    fc = json.load(open(osm_path))
    bbox, course = course_box(pdir)
    geo = json.load(open(os.path.join(img, "georef.json"))) if os.path.exists(os.path.join(img, "georef.json")) else {}
    current = (geo.get("imagery") or {}).get("year")
    t0 = time.time()
    years = NY.list_years(bbox)
    log(f"{a.slug}: NAIP years {[(y['year'], y['dates'], y['coverage']) for y in years]}; package has {current}")
    row, rec = FI.choose_year(years, "auto", osm=fc, bbox=bbox, current=current)
    log(f"{a.slug}: chosen {row['year']}: {rec['reason']}")
    doc = dict(schema="naip_years_run/1", slug=a.slug, built=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()),
               bbox_snwe=[round(v, 6) for v in bbox], current=current, chosen=row["year"],
               imagery_dir=os.path.relpath(img, ROOT), selection=rec)
    os.makedirs(a.out, exist_ok=True)
    out_path = os.path.join(a.out, f"{a.slug}.json")
    json.dump(doc, open(out_path, "w"), indent=1)
    if a.detect:
        try:
            doc["detect"] = detect_eval(years, rec["candidates"], current, bbox, fc, course)
        except Exception as e:                                   # noqa: BLE001
            import traceback
            traceback.print_exc()
            doc["detect_error"] = f"{type(e).__name__}: {e}"[:500]
        json.dump(doc, open(out_path, "w"), indent=1)
    if a.apply:
        if current and int(current) == row["year"]:
            geo.setdefault("imagery", {})["selection"] = rec
            json.dump(geo, open(os.path.join(img, "georef.json"), "w"), indent=1)
            doc["applied"] = f"kept {current}; selection recorded in georef.json"
        else:
            w, s, e, n = course["bbox"]
            c = course
            cmd = [sys.executable, os.path.join(HERE, "fetch_imagery.py"), "--bbox", f"{s},{w},{n},{e}",
                   "--name", c.get("name") or a.slug, "--margin", str(int(MARGIN_M)), "--max-mb", "45", "--out", img,
                   "--osm", osm_path, "--year", str(row["year"]), "--no-dem"]
            log(" ".join(cmd))
            r = subprocess.run(cmd, timeout=3000)
            g2 = json.load(open(os.path.join(img, "georef.json")))
            if r.returncode != 0 or (g2.get("imagery") or {}).get("year") != row["year"]:
                raise SystemExit(f"{a.slug}: re-fetch of NAIP {row['year']} failed")
            g2["imagery"]["selection"] = rec                     # the full scored record, not just "requested"
            json.dump(g2, open(os.path.join(img, "georef.json"), "w"), indent=1)
            doc["applied"] = f"re-fetched NAIP {row['year']} (was {current})"
        json.dump(doc, open(out_path, "w"), indent=1)
    log(f"{a.slug}: done in {time.time() - t0:.0f}s: {doc.get('applied', 'scored only')}")
    print(json.dumps(dict(chosen=row["year"], current=current, mean_iou=(doc.get("detect") or {}).get("mean_iou")), indent=1))


if __name__ == "__main__":
    main()
