"""Build the any-course hazard layers for one course (offline, after fetch_any.py ran on Actions).

  python3 course_data/vision_any/run_any.py --slug mozingo [--course-dir course_data/mozingo] [--eval]

Writes course_data/vision_any/<slug>/:
  vision_any.geojson   WGS84 polygons, properties {lie: recovery|native|water, src, p, area_yd2}; the
                       FeatureCollection `properties` record sources, dates and how each layer was made
  classes.png          preview: NAIP with trees (magenta), native (yellow), vision water (cyan), OSM fairway
                       outline (white)
  layers.tif           uint8 per 1 m cell: 0 none, 1 native, 2 trees, 3 water (+ p_native x255 band 2)
--eval also scores the result against the course's hand map (evaluate.py) if one exists.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import layers as L                                   # noqa: E402
import native as N                                   # noqa: E402

YD = 0.9144


def course_dir_for(slug):
    for d in (os.path.join(ROOT, "course_data", "packages", slug, "raw"), os.path.join(ROOT, "course_data", slug)):
        if os.path.exists(os.path.join(d, "osm.geojson")):
            return d
    raise SystemExit(f"no osm.geojson for {slug}")


def compute(slug, course_dir=None, imagery_dir=None, tree_hag=L.TREE_HAG_M):
    """-> dict of grids + stack + osm (everything the evaluation and the polygons need)."""
    t0 = time.time()
    cdir = course_dir or course_dir_for(slug)
    S = L.Stack.load(slug, cdir)
    fc = json.load(open(os.path.join(cdir, "osm.geojson")))
    M, Ly = L.osm_masks(S, fc)
    L.log(f"  stack+osm {time.time() - t0:.0f}s")
    trees, trees_how, height = L.tree_mask(S, M, hag_min=tree_hag)
    L.log(f"  trees {time.time() - t0:.0f}s")
    X, names = L.features(S, M, trees)
    L.log(f"  features {X.shape} {time.time() - t0:.0f}s")
    # first pass water without banks (banks need the mown probability -> use native's p)
    water0, _ = L.water_mask(S, Ly, M)
    L.log(f"  water0 {time.time() - t0:.0f}s")
    nat, p_nat, ninfo = N.predict(S, M, Ly, trees, water0, X, names)
    L.log(f"  native {time.time() - t0:.0f}s")
    water, wparts = L.water_mask(S, Ly, M, mown_p=1 - p_nat, trees=trees)
    nat &= ~water
    L.log(f"[{slug}] trees {trees.mean():.1%} ({trees_how}); native {nat.mean():.1%} {ninfo.get('seed_px')} seeds; "
          f"water {water.mean():.1%} ({', '.join(f'{k} {v.sum()}' for k, v in wparts.items())}) in {time.time() - t0:.0f}s")
    return dict(S=S, M=M, Ly=Ly, fc=fc, trees=trees, trees_how=trees_how, native=nat, p_native=p_nat,
                native_info=ninfo, water=water, water_parts=wparts, X=X, names=names)


def polygons(R):
    S, M = R["S"], R["M"]
    feats = []
    trees_src = "vision:lidar_hag" if "lidar" in R["trees_how"].lower() else (
        "vision:meta_chm" if "Meta" in R["trees_how"] else "vision:naip")
    # trees: close 3 m so a tree line is one zone; p = 0.95 lidar, 0.8 other
    tm = ndimage.binary_closing(R["trees"], L.disk(3))
    for g in L.mask_to_polys(S, tm, min_yd2=150, simplify_yd=2.0):
        feats.append(("recovery", g, trees_src, 0.95 if "lidar" in trees_src else 0.8))
    pn = R["p_native"]
    for g in L.mask_to_polys(S, R["native"], min_yd2=150, simplify_yd=2.0):
        feats.append(("native", g, "vision:naip", None))
    vw = R["water"] & ~M["water"]                       # only what OSM doesn't already have
    for g in L.mask_to_polys(S, vw, min_yd2=150, simplify_yd=2.0):
        feats.append(("water", g, "vision:naip_ndwi+dtm+osm_stream", 0.8))
    out = []
    from shapely.geometry import mapping
    for lie, g, src, p in feats:
        if p is None:                                    # mean p over the polygon
            rc = S.ll_to_rc(np.asarray(g.representative_point().coords))
            c, r = int(rc[0, 0]), int(rc[0, 1])
            p = float(pn[max(r - 2, 0):r + 3, max(c - 2, 0):c + 3].mean()) if 0 <= r < S.H and 0 <= c < S.W else 0.7
            p = max(p, N.P_MIN)
        S.ll_to_rc([[0, 0]])
        from shapely.ops import transform
        gm = transform(lambda x, y: S._fwd.transform(x, y), g)
        out.append(dict(type="Feature", geometry=mapping(g),
                        properties=dict(lie=lie, src=src, p=round(float(p), 3), area_yd2=round(gm.area / YD ** 2))))
    return out


def meta_props(R):
    S = R["S"]
    naip = S.meta.get("naip", {}).get("years") or []
    dates = [d for y in naip for d in y.get("acquired", [])] or [k for k in S.src if k.startswith("naip")]
    lid = S.src.get("hag")
    return dict(schema="vision_any/1", slug=S.slug, built=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()),
                trees_how=R["trees_how"], lidar=lid,
                native_how="NAIP self-supervised vs OSM mown turf (native.py): " + json.dumps(
                    {k: v for k, v in R["native_info"].items() if k != "features"}),
                water_how="OSM water + NDWI open water near OSM water/streams + DTM channel of OSM streams + unmown banks",
                naip_dates=dates, sources=S.src, grid=dict(crs=S.crs, res_m=S.res, bounds=S.bounds),
                rules="ARCHITECTURE.md 3.6: >= 150 yd2, simplified to 2 yds, never over OSM fairway/green/tee/bunker")


def preview(R, path):
    import cv2
    S = R["S"]
    b = np.clip(S.naip[0][1][..., :3] * 1.25, 0, 1) if S.naip else np.zeros((S.H, S.W, 3))
    img = (b * 255).astype(np.uint8).copy()
    for m, col in ((R["native"], (255, 220, 0)), (R["trees"], (200, 0, 200)), (R["water"], (0, 200, 255))):
        img[m] = (0.45 * img[m] + 0.55 * np.array(col)).astype(np.uint8)
    edge = R["M"]["fairway"] & ~ndimage.binary_erosion(R["M"]["fairway"], iterations=1)
    img[ndimage.binary_dilation(edge)] = 255
    k = max(1, int(np.ceil(max(S.W, S.H) / 1800)))
    from PIL import Image
    Image.fromarray(img).resize((S.W // k, S.H // k), Image.LANCZOS).save(path, quality=85)


def write_raster(R, path):
    import rasterio
    S = R["S"]
    cls = np.zeros((S.H, S.W), np.uint8)
    cls[R["native"]] = 1
    cls[R["trees"]] = 2
    cls[R["water"]] = 3
    prof = dict(driver="GTiff", height=S.H, width=S.W, count=2, dtype="uint8", crs=S.crs, transform=S.transform,
                compress="deflate", tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(cls, 1)
        dst.write((np.clip(R["p_native"], 0, 1) * 255).astype(np.uint8), 2)
        dst.update_tags(band1="0 none, 1 native, 2 trees (canopy), 3 water", band2="p_native x255")


def build(slug, course_dir=None, imagery_dir=None, write=True, R=None):
    R = R or compute(slug, course_dir, imagery_dir)
    fc = dict(type="FeatureCollection", features=polygons(R), properties=meta_props(R))
    if write:
        d = os.path.join(HERE, slug)
        os.makedirs(d, exist_ok=True)
        json.dump(fc, open(os.path.join(d, "vision_any.geojson"), "w"), separators=(",", ":"))
        preview(R, os.path.join(d, "classes.jpg"))
        write_raster(R, os.path.join(d, "layers.tif"))
        n = {}
        for f in fc["features"]:
            n[f["properties"]["lie"]] = n.get(f["properties"]["lie"], 0) + 1
        L.log(f"[{slug}] wrote vision_any.geojson {n}, classes.jpg, layers.tif")
    return fc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--course-dir")
    ap.add_argument("--eval", action="store_true")
    a = ap.parse_args()
    R = compute(a.slug, a.course_dir)
    build(a.slug, R=R)
    if a.eval:
        import validate
        validate.run(a.slug, R)


if __name__ == "__main__":
    main()
