"""Sentinel-2 L2A seasonal stack per course (Planetary Computer), for the unirrigated-grass test (s2_longgrass.md).

  python course_data/vision_any/s2/fetch_s2_stack.py --slugs gateway_national,annbriar --start 2023-03-01 --end 2025-11-30

Grid: the course's vision_any/<slug>/raw/meta.json grid (UTM), coarsened to 10 m (bounds snapped outward to 10 m).
Each scene's bands are warped onto that grid (bilinear; SCL nearest). Clear = SCL 4/5/6 (vegetation, bare, water),
with cloud / shadow / cirrus (SCL 3, 8, 9, 10) dilated by 2 px; a scene is kept if >= 40 % of the grid is clear.
One scene per date (the overlapping MGRS tile with the most valid pixels). Reflectance offset -1000 for processing
baseline >= 04.00.

Output (course_data/vision_any/s2/<slug>/s2_stack.npz, small enough to commit):
  months   (M,) "YYYY-MM" composite slots (Mar-Nov of each year)
  idx      (M, K, H, W) int8: monthly median of clear observations of each index x 100 (-128 = no clear obs)
  inames   (K,) index names: ndvi, ndre (B8A,B05), ndmi (B8A,B11), psri ((B04-B02)/B06), nbr2 (B11,B12)
  nobs     (M, H, W) uint8 clear observations per slot
  ndvi_obs (T, H, W) int8: every clear scene's NDVI x 100 (-128 masked) and `dates` (T,): for variance / timing
  summer   (B, H, W) uint16: Jun-Aug median reflectance of the 10 bands over all years (`bands`)
  transform, crs, shape
and s2_meta.json (scenes used, clear shares).
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
VA = os.path.dirname(HERE)
BANDS = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]
INAMES = ["ndvi", "ndre", "ndmi", "psri", "nbr2"]
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("GDAL_HTTP_MULTIPLEX", "YES")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "4")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")
os.environ.setdefault("VSI_CACHE", "TRUE")


def log(*a):
    print(*a, flush=True)


def grid(slug):
    m = json.load(open(os.path.join(VA, slug, "raw", "meta.json")))
    g = m["grid"]
    x0, y0, x1, y1 = g["bounds"]
    x0 = np.floor(x0 / 10) * 10; y0 = np.floor(y0 / 10) * 10
    x1 = np.ceil(x1 / 10) * 10; y1 = np.ceil(y1 / 10) * 10
    W, H = int((x1 - x0) / 10), int((y1 - y0) / 10)
    return g["crs"], (10.0, 0.0, float(x0), 0.0, -10.0, float(y1)), W, H, g["ll_bbox_wsen"]


def ratio(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        return (a - b) / (a + b)


def indices(B):
    """B: dict band -> float32 reflectance (0-1). Returns (K, H, W) float32."""
    with np.errstate(divide="ignore", invalid="ignore"):
        psri = np.clip((B["B04"] - B["B02"]) / np.maximum(B["B06"], 0.01), -1, 1)
    return np.stack([ratio(B["B08"], B["B04"]), ratio(B["B8A"], B["B05"]), ratio(B["B8A"], B["B11"]), psri,
                     ratio(B["B11"], B["B12"])]).astype(np.float32)


def read_asset(href, crs, tf, W, H, nearest=False):
    import rasterio
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    from affine import Affine
    for k in range(4):
        try:
            with rasterio.open(href) as src, WarpedVRT(src, crs=crs, transform=Affine(*tf), width=W, height=H,
                                                       resampling=Resampling.nearest if nearest else Resampling.bilinear) as v:
                return v.read(1)
        except Exception as e:  # noqa
            if k == 3:
                raise
            time.sleep(3 * (k + 1))


def course(slug, start, end, max_cloud, workers, out_root):
    import planetary_computer
    import pystac_client
    from scipy import ndimage
    crs, tf, W, H, (w, s, e, n) = grid(slug)
    cat = pystac_client.Client.open(STAC, modifier=planetary_computer.sign_inplace)
    items = list(cat.search(collections=["sentinel-2-l2a"], bbox=[w, s, e, n], datetime=f"{start}/{end}",
                            query={"eo:cloud_cover": {"lt": max_cloud}}).items())
    items = [i for i in items if 3 <= i.datetime.month <= 11]
    log(f"{slug}: {len(items)} items ({W}x{H} px)")
    bydate = {}
    for it in items:
        bydate.setdefault(it.datetime.date().isoformat(), []).append(it)

    def scl_for(it):
        try:
            return it, read_asset(planetary_computer.sign(it.assets["SCL"].href), crs, tf, W, H, nearest=True)
        except Exception as ex:  # noqa
            log("  scl fail", it.id, ex)
            return it, None

    def scene(date):
        best = None
        for it, scl in map(scl_for, bydate[date]):
            if scl is None:
                continue
            v = (scl > 0).mean()
            if best is None or v > best[2]:
                best = (it, scl, v)
        if best is None or best[2] < 0.95:
            return date, None, "nodata"
        it, scl, _ = best
        bad = ndimage.binary_dilation(np.isin(scl, [3, 8, 9, 10]), iterations=2)
        clear = np.isin(scl, [4, 5, 6]) & ~bad
        cf = float(clear.mean())
        if cf < 0.40:
            return date, None, f"clear {cf:.2f}"
        off = 1000.0 if str(it.properties.get("s2:processing_baseline", "05.00")) >= "04.00" else 0.0
        B = {}
        for b in BANDS:
            a = read_asset(planetary_computer.sign(it.assets[b].href), crs, tf, W, H).astype(np.float32)
            B[b] = (a - off) / 10000.0
        return date, dict(id=it.id, clear=clear, B=B, cf=cf), "ok"

    res = {}
    with ThreadPoolExecutor(workers) as ex:
        for date, r, why in ex.map(scene, sorted(bydate)):
            log(f"  {slug} {date} {why}{'' if r is None else ' clear %.2f' % r['cf']}")
            if r is not None:
                res[date] = r
    dates = sorted(res)
    if not dates:
        raise RuntimeError(f"{slug}: no clear scenes")
    years = sorted({d[:4] for d in dates})
    months = [f"{y}-{m:02d}" for y in years for m in range(3, 12)]
    K = len(INAMES)
    idx = np.full((len(months), K, H, W), -128, np.int8)
    nobs = np.zeros((len(months), H, W), np.uint8)
    ndvi_obs = np.full((len(dates), H, W), -128, np.int8)
    per = {}
    for t, d in enumerate(dates):
        r = res[d]
        I = indices(r["B"]); I[:, ~r["clear"]] = np.nan
        ndvi_obs[t] = np.where(np.isfinite(I[0]), np.clip(np.round(I[0] * 100), -127, 127), -128)
        per.setdefault(d[:7], []).append(I)
    for mi, mo in enumerate(months):
        if mo not in per:
            continue
        st = np.stack(per[mo])
        nobs[mi] = np.isfinite(st[:, 0]).sum(0)
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                med = np.nanmedian(st, axis=0)
        idx[mi] = np.where(np.isfinite(med), np.clip(np.round(med * 100), -127, 127), -128)
    summ = [d for d in dates if d[5:7] in ("06", "07", "08")]
    summer = np.zeros((len(BANDS), H, W), np.uint16)
    if summ:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for bi, b in enumerate(BANDS):
                st = np.stack([np.where(res[d]["clear"], res[d]["B"][b], np.nan) for d in summ])
                summer[bi] = np.nan_to_num(np.clip(np.nanmedian(st, 0) * 10000, 0, 65535)).astype(np.uint16)
    od = os.path.join(out_root, slug); os.makedirs(od, exist_ok=True)
    np.savez_compressed(os.path.join(od, "s2_stack.npz"), months=np.array(months), idx=idx, inames=np.array(INAMES),
                        nobs=nobs, ndvi_obs=ndvi_obs, dates=np.array(dates), summer=summer, bands=np.array(BANDS),
                        transform=np.array(tf), crs=np.array(crs), shape=np.array([H, W]))
    meta = dict(schema="s2_stack/1", slug=slug, source="Planetary Computer sentinel-2-l2a", start=start, end=end,
                max_cloud=max_cloud, crs=crs, transform=tf, width=W, height=H, n_items=len(items),
                n_dates=len(bydate), scenes=[dict(date=d, id=res[d]["id"], clear=round(res[d]["cf"], 3)) for d in dates],
                fetched_utc=dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    json.dump(meta, open(os.path.join(od, "s2_meta.json"), "w"), indent=1)
    log(f"{slug}: {len(dates)} clear scenes, {os.path.getsize(os.path.join(od, 's2_stack.npz')) / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs", required=True)
    ap.add_argument("--start", default="2023-03-01")
    ap.add_argument("--end", default="2025-11-30")
    ap.add_argument("--max-cloud", type=float, default=60)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    fails = []
    for slug in a.slugs.split(","):
        t0 = time.time()
        try:
            course(slug, a.start, a.end, a.max_cloud, a.workers, a.out)
        except Exception as ex:  # noqa
            import traceback; traceback.print_exc(); fails.append(slug)
        log(f"{slug}: {time.time() - t0:.0f} s")
    if fails:
        log("FAILED:", fails)
        sys.exit(1 if len(fails) == len(a.slugs.split(",")) else 0)


if __name__ == "__main__":
    main()
