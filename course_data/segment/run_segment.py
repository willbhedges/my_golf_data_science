"""Run the NAIP golf segmentation for every request file course_data/requests/segment_<slug>.json (Actions).

Request body (ARCHITECTURE 9.4):
  {"schema": "request/1", "kind": "segment", "slug": "veenker",
   "naip": "course_data/vision_any/veenker/raw/naip_2023.tif",      # 4-band R,G,B,NIR uint8, ~0.6 m
   "package": "course_data/packages/veenker/package.json"}           # optional (evaluation, gap-fill)

Writes course_data/segment/<slug>/:
  segment.geojson   WGS84 polygons {class, src, p, area_m2} for green/tee/fairway/bunker/water
  probs.tif         uint8 probability x 250 for green, tee, fairway, bunker, water (5 bands, NAIP grid)
  preview.jpg       NAIP with the argmax classes over it
  meta.json         model id + Hub sha, request, imagery, timings
A course is skipped when its meta.json already records the same request and model sha (--force to redo).
Afterwards evaluate.py runs (light) and writes course_data/segment/eval.{json,md}.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import model as M  # noqa: E402
import polygons as P  # noqa: E402

COLORS = {1: (0, 200, 0), 2: (255, 0, 255), 3: (150, 255, 80), 4: (255, 230, 120), 5: (40, 120, 255)}


def requests():
    out = []
    for f in sorted(glob.glob(os.path.join(CD, "requests", "segment_*.json"))):
        r = json.load(open(f))
        if r.get("slug") and r.get("naip"):
            r["_file"] = os.path.relpath(f, ROOT)
            r["_hash"] = hashlib.sha1(json.dumps({k: v for k, v in r.items() if not k.startswith("_")},
                                                 sort_keys=True).encode()).hexdigest()[:12]
            out.append(r)
    return out


def preview(img, probs, path, max_px=2000):
    from PIL import Image
    rgb = np.moveaxis(img[:3], 0, -1).astype(np.float32)
    am = probs.argmax(0)
    for c, col in COLORS.items():
        m = am == c
        rgb[m] = 0.45 * rgb[m] + 0.55 * np.asarray(col, np.float32)
    im = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))
    s = max_px / max(im.size)
    if s < 1:
        im = im.resize((int(im.size[0] * s), int(im.size[1] * s)))
    im.save(path, quality=85)


def run_one(r, mdl, sha, force=False, tta=True):
    import rasterio
    slug = r["slug"]
    od = os.path.join(HERE, slug)
    os.makedirs(od, exist_ok=True)
    mp = os.path.join(od, "meta.json")
    if not force and os.path.exists(mp):
        m = json.load(open(mp))
        if m.get("request_hash") == r["_hash"] and m.get("model_sha") == sha:
            print(f"{slug}: up to date")
            return m
    t0 = time.time()
    with rasterio.open(os.path.join(ROOT, r["naip"])) as src:
        img = src.read()
        T, crs, prof = src.transform, src.crs, src.profile
    assert img.shape[0] == 4 and img.dtype == np.uint8, (img.shape, img.dtype)
    res = abs(T.a)
    print(f"{slug}: {img.shape} res {res} m {crs}", flush=True)
    if abs(res - M.GSD_M) > 0.05:
        print(f"  WARNING: {res} m pixels, model expects {M.GSD_M} m")
    probs = M.predict_raster(mdl, img, tta=tta)
    t1 = time.time()
    valid = img.any(axis=0)
    wmask, ndwi = M.ndwi_water(img)
    wscore = np.clip((ndwi - 0.05) / 0.3, 0, 1)
    feats = P.polygonize(probs, T, crs, src=f"segment:ariadgolf-v4@{sha[:8]}", water=(wmask, wscore), valid=valid)
    json.dump({"type": "FeatureCollection", "features": feats,
               "properties": {"model": M.REPO, "model_sha": sha, "naip": r["naip"],
                              "licence": "model weights: no licence granted (research/evaluation only); "
                                         "labels OSM ODbL; imagery USDA NAIP (public domain)"}},
              open(os.path.join(od, "segment.geojson"), "w"))
    q = (probs[1:] * 250).round().astype(np.uint8)
    prof.update(count=5, dtype="uint8", compress="deflate", predictor=2, nodata=None, photometric=None)
    prof.pop("photometric", None)
    with rasterio.open(os.path.join(od, "probs.tif"), "w", **prof) as dst:
        dst.write(q)
        for i, c in enumerate(M.CLASSES[1:]):
            dst.set_band_description(i + 1, c)
    preview(img, probs, os.path.join(od, "preview.jpg"))
    counts = {}
    for f in feats:
        k = f"{f['properties']['class']}:{f['properties']['src'].split(':')[1].split('@')[0]}"
        counts[k] = counts.get(k, 0) + 1
    m = dict(slug=slug, request=r["_file"], request_hash=r["_hash"], model=M.REPO, model_sha=sha, tta=tta,
             naip=r["naip"], shape=list(img.shape), res_m=res, crs=str(crs),
             seconds_infer=round(t1 - t0, 1), seconds_total=round(time.time() - t0, 1), features=counts,
             pixel_share={c: round(float((probs.argmax(0) == i)[valid].mean()), 4) for i, c in enumerate(M.CLASSES)})
    json.dump(m, open(mp, "w"), indent=1)
    print(json.dumps(m)[:600], flush=True)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-tta", action="store_true")
    ap.add_argument("--slug", nargs="*")
    a = ap.parse_args()
    rs = [r for r in requests() if not a.slug or r["slug"] in a.slug]
    print("requests:", [r["slug"] for r in rs])
    if not rs:
        return
    mdl, cfg, sha = M.load(threads=os.cpu_count())
    for r in rs:
        try:
            run_one(r, mdl, sha, force=a.force, tta=not a.no_tta)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            print(f"{r['slug']}: FAILED {e}")


if __name__ == "__main__":
    main()
