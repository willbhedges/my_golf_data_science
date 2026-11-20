"""Tree masks for the training set (v3 --tee-focus wood): Meta / WRI canopy height (dataforgood-fb-data COGs, free,
1 m) warped bilinear onto each course's NAIP GeoTIFF grid, tree = height >= 3 m (the routing bench's tree rule,
route_learn.TREE_M), saved as <out>/<name>_chm.npz (tree uint8 bit-packed, shape). GitHub Actions or local.

    python course_data/segment/train/chm_add.py --data D [--out D] [--threads 8] [--minutes 120]

Reads every index*.json under --data (build_dataset.py --courses rows with an image); skips files already there.
Canopy: Meta / WRI high-resolution canopy height (Tolan et al. 2024), CC BY 4.0.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(CD, "vision_any"))
META_CHM = "https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/chm/{qk}.tif"
TREE_M = 3.0


def quadkeys(ll_bbox, z=9):
    import math
    w, s, e, n = ll_bbox

    def tile(lon, lat):
        return (int((lon + 180) / 360 * 2 ** z),
                int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2 ** z))
    x0, y0 = tile(w, n)
    x1, y1 = tile(e, s)
    out = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            out.append("".join(str((1 if x & (1 << (i - 1)) else 0) + (2 if y & (1 << (i - 1)) else 0))
                               for i in range(z, 0, -1)))
    return out


def one(tif, dst):
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject, transform_bounds
    with rasterio.open(tif) as src:
        crs, tr, H, W = src.crs, src.transform, src.height, src.width
        bb = transform_bounds(crs, "EPSG:4326", *src.bounds, densify_pts=21)
    arr = np.full((H, W), np.nan, np.float32)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", AWS_NO_SIGN_REQUEST="YES", VSI_CACHE="TRUE",
                      GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                      GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2"):
        for qk in quadkeys(bb):
            tmp = np.full((H, W), np.nan, np.float32)
            with rasterio.open("/vsicurl/" + META_CHM.format(qk=qk)) as s:
                reproject(rasterio.band(s, 1), tmp, src_nodata=s.nodata, dst_nodata=np.nan, dst_transform=tr,
                          dst_crs=crs, resampling=Resampling.bilinear)
            f = np.isnan(arr) & np.isfinite(tmp)
            arr[f] = tmp[f]
    tree = np.nan_to_num(arr, nan=0.0) >= TREE_M
    np.savez_compressed(dst + ".tmp.npz", tree=np.packbits(tree.ravel()), shape=np.array([H, W]),
                        valid=np.float32(np.isfinite(arr).mean()))
    os.replace(dst + ".tmp.npz", dst)
    return float(tree.mean()), float(np.isfinite(arr).mean())


def load_tree(path, shape):
    """bool HxW tree mask from a chm_add npz, or None if it does not match shape"""
    z = np.load(path)
    H, W = (int(v) for v in z["shape"])
    if (H, W) != tuple(shape) or float(z["valid"]) < 0.5:
        return None
    return np.unpackbits(z["tree"])[:H * W].reshape(H, W).astype(bool)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", help="default: next to each image")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--minutes", type=float, default=120.0)
    ap.add_argument("--max", type=int, default=0)
    a = ap.parse_args()
    jobs = []
    for p in sorted(glob.glob(os.path.join(a.data, "**", "index*.json"), recursive=True)):
        for k, c in json.load(open(p))["courses"].items():
            if c.get("image") and os.path.exists(os.path.join(os.path.dirname(p), c["image"])):
                name = c["image"][:-4]
                od = a.out or os.path.dirname(p)
                dst = os.path.join(od, name + "_chm.npz")
                if not os.path.exists(dst):
                    jobs.append((os.path.join(os.path.dirname(p), c["image"]), dst))
    if a.max:
        jobs = jobs[:a.max]
    if a.out:
        os.makedirs(a.out, exist_ok=True)
    print(len(jobs), "courses without a tree mask", flush=True)
    t0 = time.time()
    ok = bad = 0
    with cf.ThreadPoolExecutor(a.threads) as ex:
        fut = {}
        for j in jobs:
            fut[ex.submit(lambda j=j: None if (time.time() - t0) / 60 > a.minutes else one(*j))] = j
        for f in cf.as_completed(fut):
            try:
                r = f.result()
                if r is None:
                    continue
                ok += 1
                if ok % 50 == 0:
                    print(f"{ok} done {time.time() - t0:.0f}s (last tree {r[0]:.3f} valid {r[1]:.2f})", flush=True)
            except Exception as e:                              # noqa: BLE001
                bad += 1
                print("failed", os.path.basename(fut[f][0]), repr(e)[:200], flush=True)
    print(f"{ok} tree masks, {bad} failed, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
