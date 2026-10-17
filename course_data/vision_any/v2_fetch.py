"""Extra rasters for the long-grass + tree-edge model v2 (runs on GitHub Actions, vision_any_v2.yml).

  python course_data/vision_any/v2_fetch.py --slug spirit_hollow [--naip-years 6] [--skip naip,lidar]

Same grid as fetch_any.py (raw/meta.json). Writes course_data/vision_any/<slug>/raw2/ (NOT committed: the
workflow keeps it in the Actions cache):

  naip_<year>.tif  R,G,B,NIR at 1.0 m (area-averaged) for up to --naip-years NAIP years with NIR and full
                   coverage, newest first (2023/2021/2019/2017/... in Iowa; 2022/2020/2018/... in Missouri).
                   Several years = mowing persistence: native stays unmown and straw-coloured across years,
                   mown rough does not.
  lidar_v2.tif     float32 bands from the raw USGS 3DEP point cloud (EPT on AWS, via PDAL), 1 m cells:
                   see LIDAR_BANDS. Heights are above ground (filters.hag_nn), noise (class 7/18) dropped.
  meta2.json       items, years, dates, EPT project, errors.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# (band name, PDAL range filter on the hag-tagged points or None, dimension, output_type)
LIDAR_BANDS = [
    ("hag_max", None, "HeightAboveGround", "max"),
    ("hag_mean", None, "HeightAboveGround", "mean"),
    ("hag_std", None, "HeightAboveGround", "stdev"),
    ("n_all", None, "HeightAboveGround", "count"),
    ("n_vlow", "HeightAboveGround[0.05:0.3]", "HeightAboveGround", "count"),     # stubble / mown turf texture
    ("n_low", "HeightAboveGround[0.3:1.5]", "HeightAboveGround", "count"),       # tall grass, shrubs
    ("n_mid", "HeightAboveGround[1.5:4]", "HeightAboveGround", "count"),         # shrubs, low branches
    ("n_ground", "Classification[2:2]", "HeightAboveGround", "count"),
    ("n_multi", "NumberOfReturns[2:20]", "HeightAboveGround", "count"),          # penetrable vegetation
    ("int_mean", None, "Intensity", "mean"),
    ("int_ground", "Classification[2:2]", "Intensity", "mean"),
    ("dtm1", "Classification[2:2]", "Z", "mean"),
]


def log(*a):
    print(*a, flush=True)


def grid_from_meta(slug):
    import fetch_any as FA
    m = json.load(open(os.path.join(HERE, slug, "raw", "meta.json")))
    g = m["grid"]
    G = FA.Grid.__new__(FA.Grid)
    from affine import Affine
    G.x0, G.y0, G.x1, G.y1 = g["bounds"]
    G.crs, G.res, G.W, G.H = g["crs"], g["res_m"], g["width"], g["height"]
    G.epsg = int(G.crs.split(":")[1])
    G.transform = Affine(G.res, 0, G.x0, 0, -G.res, G.y1)
    G.ll_bbox = g["ll_bbox_wsen"]
    return G


def fetch_naip_years(g, out, meta, n_years=6, res=1.0, min_year=2012):
    """Like fetch_any.fetch_naip, but more years and 1 m (the analysis grid)."""
    import fetch_any as FA
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    from shapely.geometry import box, shape
    from shapely.ops import unary_union
    info = dict(years=[])
    cat = FA.stac()
    items = FA.search(cat, "naip", g)
    aoi = box(*g.ll_bbox)
    gn = g.at(res)
    for yr in sorted({i.datetime.year for i in items}, reverse=True):
        if yr < min_year or len(info["years"]) >= n_years:
            break
        its = [i for i in items if i.datetime.year == yr]
        cov = unary_union([shape(i.geometry) for i in its]).intersection(aoi).area / aoi.area
        log(f"  NAIP {yr}: {len(its)} items, coverage {cov:.3f}")
        if cov < 0.98:
            continue
        try:
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
            mb = FA.write_tif(os.path.join(out, fn), bands, gn, jpeg=90)
            info["years"].append(dict(year=yr, file=fn, mb=mb, items=[i.id for i in its],
                                      acquired=sorted({i.datetime.date().isoformat() for i in its}),
                                      gsd_m=its[0].properties.get("gsd"), res_m=res))
        except Exception:                                    # noqa: BLE001
            info.setdefault("errors", []).append(dict(year=yr, err=traceback.format_exc()[-600:]))
            log(traceback.format_exc()[-600:])
    meta["naip"] = info


def ept_candidates(g):
    import fetch_any as FA
    import re
    import requests
    from pyproj import Transformer
    from shapely.geometry import box, shape
    idx = requests.get(FA.EPT_INDEX, timeout=120).json()
    t = Transformer.from_crs(g.crs, "EPSG:3857", always_xy=True)
    xs, ys = t.transform([g.x0, g.x1, g.x0, g.x1], [g.y0, g.y0, g.y1, g.y1])
    b3857 = (min(xs) - 20, min(ys) - 20, max(xs) + 20, max(ys) + 20)
    aoi_ll, aoi_m = box(*g.ll_bbox), box(*b3857)
    cands = []
    for f in idx["features"]:
        try:
            geom = shape(f["geometry"])
        except Exception:                                    # noqa: BLE001
            continue
        aoi = aoi_ll if abs(geom.bounds[0]) <= 180 else aoi_m
        if not geom.intersects(aoi):
            continue
        nm = f["properties"].get("name", "")
        yrs = [int(y) for y in re.findall(r"(?<!\d)(20[0-2]\d|199\d)(?!\d)", nm)]
        cands.append(dict(name=nm, url=f["properties"].get("url"), cov=round(geom.intersection(aoi).area / aoi.area, 3),
                          year=max(yrs) if yrs else 0, count=f["properties"].get("count")))
    cands.sort(key=lambda c: (c["cov"] > 0.9, c["year"]), reverse=True)
    return cands, b3857


def pipelines(url, b3857, g, tmp):
    """PDAL runs only ONE branch of a multi-writer pipeline, so: (1) EPT -> noise out -> UTM -> HAG -> one
    local LAZ with HeightAboveGround as an extra dimension; (2) one short linear pipeline per band."""
    laz = os.path.join(tmp, "pts.laz")
    first = [dict(type="readers.ept", filename=url, bounds=f"([{b3857[0]},{b3857[2]}],[{b3857[1]},{b3857[3]}])",
                  threads=8),
             dict(type="filters.range", limits="Classification![7:7],Classification![18:18]"),
             dict(type="filters.reprojection", out_srs=g.crs),
             dict(type="filters.hag_nn"),
             dict(type="writers.las", filename=laz, extra_dims="HeightAboveGround=float", minor_version=4)]
    common = dict(origin_x=g.x0, origin_y=g.y0, width=g.W, height=g.H, resolution=1.0, nodata=-9999)
    bands = []
    for name, rng, dim, ot in LIDAR_BANDS:
        st = [dict(type="readers.las", filename=laz)]
        if rng:
            st.append(dict(type="filters.range", limits=rng))
        kw = dict(common)
        if name == "dtm1":
            kw["window_size"] = 2
        st.append(dict(type="writers.gdal", filename=os.path.join(tmp, f"{name}.tif"), dimension=dim, output_type=ot, **kw))
        bands.append((name, st))
    return first, bands


def run_pdal(pdal, pipe, path, timeout=3000):
    json.dump(pipe, open(path, "w"))
    r = subprocess.run([pdal, "pipeline", path], capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stderr or "")[-800:] + (r.stdout or "")[-300:]


def fetch_lidar_v2(g, out, meta, max_projects=2):
    import rasterio
    info = dict(source="USGS 3DEP lidar point cloud, EPT on AWS (usgs-lidar-public) via PDAL", bands=[b[0] for b in LIDAR_BANDS])
    pdal = os.environ.get("PDAL_BIN") or shutil.which("pdal")
    if not pdal or not os.path.exists(pdal):
        info["error"] = "pdal CLI not installed"
        meta["lidar_v2"] = info
        return
    cands, b3857 = ept_candidates(g)
    info["candidates"] = cands[:8]
    log("  EPT candidates:", cands[:8])
    acc = {b[0]: np.full((g.H, g.W), np.nan, np.float32) for b in LIDAR_BANDS}
    used = []
    for c in cands[:max_projects]:
        url = c["url"] or f"https://s3-us-west-2.amazonaws.com/usgs-lidar-public/{c['name']}/ept.json"
        tmp = os.path.join(out, "_ept2")
        os.makedirs(tmp, exist_ok=True)
        first, bands = pipelines(url, b3857, g, tmp)
        log("  PDAL", c["name"])
        t0 = dt.datetime.now()
        rc, err = run_pdal(pdal, first, os.path.join(tmp, "p0.json"))
        laz = os.path.join(tmp, "pts.laz")
        if rc != 0 or not os.path.exists(laz):
            log("   PDAL read failed:", err)
            info.setdefault("errors", []).append(dict(name=c["name"], err=err))
            shutil.rmtree(tmp, ignore_errors=True)
            continue
        log(f"   points -> {os.path.getsize(laz) / 1e6:.0f} MB laz in {(dt.datetime.now() - t0).seconds}s")
        for name, st in bands:
            rc, err = run_pdal(pdal, st, os.path.join(tmp, f"p_{name}.json"))
            if rc != 0:
                log(f"   band {name} failed:", err)
                info.setdefault("errors", []).append(dict(name=c["name"], band=name, err=err))
        if not os.path.exists(os.path.join(tmp, "n_all.tif")):
            shutil.rmtree(tmp, ignore_errors=True)
            continue
        # cells this project covers = cells with any return; counts stay 0 elsewhere inside its footprint
        with rasterio.open(os.path.join(tmp, "n_all.tif")) as src:
            nall = src.read(1).astype(np.float32)
        cov = (nall > 0) & np.isnan(acc["n_all"])
        for name, *_ in LIDAR_BANDS:
            p = os.path.join(tmp, f"{name}.tif")
            if not os.path.exists(p):
                continue
            with rasterio.open(p) as src:
                a = src.read(1).astype(np.float32)
            if name.startswith("n_"):
                a = np.where(a < 0, 0, a)
            else:
                a[a == -9999] = np.nan
            acc[name][cov] = a[cov]
        used.append(dict(c, cells=int(cov.sum()), seconds=(dt.datetime.now() - t0).seconds))
        shutil.rmtree(tmp, ignore_errors=True)
        if np.isfinite(acc["n_all"]).mean() > 0.97:
            break
    info["used"] = used
    if used:
        import fetch_any as FA
        arr = np.stack([acc[b[0]] for b in LIDAR_BANDS]).astype(np.float32)
        info["mb"] = FA.write_tif(os.path.join(out, "lidar_v2.tif"), arr, g, nodata=float("nan"),
                                  tags=dict(bands=",".join(b[0] for b in LIDAR_BANDS)))
        info["valid"] = float(np.isfinite(acc["n_all"]).mean())
        info["pts_per_m2_median"] = float(np.nanmedian(acc["n_all"]))
    meta["lidar_v2"] = info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--naip-years", type=int, default=6)
    ap.add_argument("--skip", default="")
    a = ap.parse_args()
    out = os.path.join(HERE, a.slug, "raw2")
    os.makedirs(out, exist_ok=True)
    g = grid_from_meta(a.slug)
    mp = os.path.join(out, "meta2.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    meta.update(schema="vision_any_raw2/1", slug=a.slug, grid=dict(crs=g.crs, bounds=[g.x0, g.y0, g.x1, g.y1]),
                fetched_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    skip = set(a.skip.split(","))
    if "naip" not in skip:
        try:
            fetch_naip_years(g, out, meta, a.naip_years)
        except Exception:                                    # noqa: BLE001
            meta["naip_error"] = traceback.format_exc()[-1500:]
            log(meta["naip_error"])
    if "lidar" not in skip:
        try:
            fetch_lidar_v2(g, out, meta)
        except Exception:                                    # noqa: BLE001
            meta["lidar_v2_error"] = traceback.format_exc()[-1500:]
            log(meta["lidar_v2_error"])
    json.dump(meta, open(mp, "w"), indent=1, default=str)
    log(json.dumps(meta, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
