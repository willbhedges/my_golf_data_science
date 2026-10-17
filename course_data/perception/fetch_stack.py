"""Per-course raster stack for course perception (runs on GitHub Actions: perception.yml).

    python course_data/perception/fetch_stack.py <slug> [--course course.json] [--out DIR] [--margin 150]
           [--dev-crop 700]        # also write a small crop for local development (course_data/perception/dev/)

One 1 m grid (the WGS84 UTM zone of the course, fetch_any.Grid) holding everything perception reads:

  stack.npz   naip   (4,H,W) uint8  R,G,B,NIR, NAIP 0.6 m area-averaged to 1 m (newest full-coverage year)
              seg    (5,H,W) uint8  U-Net p(green, tee, fairway, bunker, water) x 255 (0.6 m inference, averaged)
              hag    (H,W)   uint8  height above ground, 0.25 m units, 255 = no lidar (3DEP)
              cls    (H,W)   uint8  ASPRS class (2 ground, 3-5 veg, 6 building, 9 water), 0 = none
              inten  (H,W)   uint8  lidar intensity, per-course 1-99 % stretch, 0 = none
              dtm    (H,W)   uint16 bare earth, cm above `dtm_base_m` (meta), 65535 = none
  meta.json   grid, sources (items, dates), stretch, timings
  labels.geojson  OSM features in the grid bbox (golf, building, parking, highway, water, wood): TRUTH ONLY,
              never read by the blind perception path.

The big NAIP / lidar downloads stay in the runner; only stack.npz (~10-25 MB) goes to the Actions cache.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(CD, "vision_any"), os.path.join(CD, "segment"), os.path.join(CD, "platform"), CD]

LABEL_KEYS = ("golf", "building", "amenity", "parking", "highway", "service", "surface", "golf_cart", "natural",
              "water", "waterway", "landuse", "leisure", "name", "ref", "par", "area", "access", "footway",
              "motor_vehicle", "layer", "tunnel", "bridge")


def log(*a):
    print(*a, flush=True)


def course_bbox_snwe(course):
    w, s, e, n = course["bbox"]
    return (s, w, n, e)


def resample(arr, g_src, g_dst, how="average", nodata=None):
    """Same-CRS resample of a 2-D float array from grid g_src to g_dst (rasterio reproject)."""
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    out = np.full((g_dst.H, g_dst.W), np.nan, np.float32)
    src = arr.astype(np.float32)
    reproject(src, out, src_transform=g_src.transform, src_crs=g_src.crs, dst_transform=g_dst.transform,
              dst_crs=g_dst.crs, resampling=getattr(Resampling, how), src_nodata=nodata, dst_nodata=np.nan)
    return out


def read_tif(path):
    import rasterio
    with rasterio.open(path) as s:
        return s.read(), s.nodata


def overpass_labels(ll_bbox):
    """OSM truth for the grid: golf features, buildings, parking, highways (cart paths), water, woods."""
    import fetch_course as fcm
    import platform_common as pc
    w, s, e, n = ll_bbox
    b = f"{s},{w},{n},{e}"
    q = f"""[out:json][timeout:180];
    (
      nwr["golf"]({b});
      nwr["leisure"~"golf_course|pitch"]({b});
      nwr["amenity"="parking"]({b});
      way["building"]({b});
      relation["building"]({b});
      way["highway"]({b});
      nwr["natural"~"water|wood|tree_row|scrub|wetland|tree"]({b});
      nwr["landuse"~"forest|reservoir|basin"]({b});
      nwr["water"]({b});
      way["waterway"]({b});
    );
    out body geom;"""
    data = pc.overpass(q, tries=3)
    fc = fcm.to_geojson(data.get("elements", []))

    def rnd(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
            return [round(float(c[0]), 7), round(float(c[1]), 7)]
        return [rnd(x) for x in c]
    feats = []
    for f in fc["features"]:
        p = f["properties"]
        props = {k: v for k, v in p.items() if k in LABEL_KEYS}
        props["osm"] = f"{p.get('osm_type')}/{p.get('osm_id')}"
        feats.append(dict(type="Feature", properties=props,
                          geometry=dict(type=f["geometry"]["type"], coordinates=rnd(f["geometry"]["coordinates"]))))
    return dict(type="FeatureCollection", features=feats,
                properties=dict(attribution="(c) OpenStreetMap contributors, ODbL 1.0",
                                fetched_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))


def stretch_u8(a, lo_p=1, hi_p=99):
    v = a[np.isfinite(a)]
    if v.size < 100:
        return np.zeros(a.shape, np.uint8), None
    lo, hi = np.percentile(v, [lo_p, hi_p])
    hi = max(hi, lo + 1e-6)
    q = np.where(np.isfinite(a), np.clip(1 + 254 * (a - lo) / (hi - lo), 1, 255), 0).astype(np.uint8)
    return q, [float(lo), float(hi)]


def build(slug, course, out, margin=150.0, segment=True, labels=True):
    import fetch_any as FA
    os.makedirs(out, exist_ok=True)
    raw = os.path.join(out, "raw")
    os.makedirs(raw, exist_ok=True)
    t0 = time.time()
    g1 = FA.Grid(course_bbox_snwe(course), margin, 1.0)
    g2, g06 = g1.at(2.0), g1.at(0.6)
    meta = dict(schema="perception_stack/1", slug=slug, name=course.get("name"), state=course.get("state"),
                bbox_wsen=course["bbox"], grid=g1.json(), built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                seconds={}, errors={})
    log(slug, "grid", g1.json())
    cat = FA.stac()

    # --- lidar (Planetary Computer products, else the EPT point cloud through PDAL)
    t = time.time()
    ok = False
    try:
        ok = FA.fetch_lidar(cat, g1, g2, raw, meta)
    except Exception:                                            # noqa: BLE001
        meta["errors"]["lidar"] = traceback.format_exc()[-1200:]
    if not ok:
        try:
            FA.fetch_ept(g1, g2, raw, meta)
        except Exception:                                        # noqa: BLE001
            meta["errors"]["ept"] = traceback.format_exc()[-1200:]
    inten = None
    try:
        from rasterio.enums import Resampling
        items = FA.search(cat, "3dep-lidar-intensity", g1)
        if items:
            inten, used = FA.mosaic(items, g1, Resampling.bilinear, np.nan)
            meta["intensity"] = dict(items=[u["id"] for u in used], valid=float(np.isfinite(inten).mean()))
    except Exception:                                            # noqa: BLE001
        meta["errors"]["intensity"] = traceback.format_exc()[-1200:]
    meta["seconds"]["lidar"] = round(time.time() - t, 1)

    # --- NAIP (newest full-coverage year with NIR) at 0.6 m
    t = time.time()
    FA.fetch_naip(cat, g1, raw, meta, n_years=1, res=0.6)
    meta["seconds"]["naip"] = round(time.time() - t, 1)
    years = (meta.get("naip") or {}).get("years") or []
    if not years:
        raise SystemExit(f"{slug}: no NAIP with NIR covering the grid")
    naip06, _ = read_tif(os.path.join(raw, years[0]["file"]))
    naip06 = naip06[:4]
    H06, W06 = naip06.shape[1:]
    assert (H06, W06) == (g06.H, g06.W), ((H06, W06), (g06.H, g06.W))
    naip = np.stack([resample(b, g06, g1, nodata=0) for b in naip06])
    naip = np.nan_to_num(naip, nan=0).round().clip(0, 255).astype(np.uint8)

    # --- U-Net (0.6 m) -> 1 m
    seg = np.zeros((5, g1.H, g1.W), np.uint8)
    if segment:
        t = time.time()
        try:
            import model as M
            mdl, _, sha = M.load(threads=os.cpu_count())
            probs = M.predict_raster(mdl, naip06, tta=True, log=None)
            for i, c in enumerate(("green", "tee", "fairway", "bunker", "water")):
                k = M.CLASSES.index(c)
                seg[i] = np.nan_to_num(resample(probs[k], g06, g1) * 255, nan=0).round().clip(0, 255).astype(np.uint8)
            meta["segment"] = dict(model=M.REPO, sha=str(sha)[:12])
            del probs
        except Exception:                                        # noqa: BLE001
            meta["errors"]["segment"] = traceback.format_exc()[-1500:]
        meta["seconds"]["segment"] = round(time.time() - t, 1)

    # --- lidar layers onto the 1 m grid
    hag = np.full((g1.H, g1.W), 255, np.uint8)
    cls = np.zeros((g1.H, g1.W), np.uint8)
    dtm = np.full((g1.H, g1.W), 65535, np.uint16)
    p = os.path.join(raw, "hag.tif")
    if os.path.exists(p):
        a, _ = read_tif(p)
        hag = a[0].astype(np.uint8)
    p = os.path.join(raw, "lidar_class.tif")
    if os.path.exists(p):
        a, _ = read_tif(p)
        cls = a[0].astype(np.uint8)
    p = os.path.join(raw, "dtm.tif")
    base = None
    if os.path.exists(p):
        a, nd = read_tif(p)
        z = a[0].astype(np.float32)
        gz = g2 if z.shape == (g2.H, g2.W) else g1
        z1 = resample(z, gz, g1, how="bilinear", nodata=nd if nd is not None else np.nan) if gz is g2 else z
        if np.isfinite(z1).any():
            base = float(np.floor(np.nanmin(z1)))
            dtm = np.where(np.isfinite(z1), np.clip(np.round((z1 - base) * 100), 0, 65534), 65535).astype(np.uint16)
    meta["dtm_base_m"] = base
    iu8 = np.zeros((g1.H, g1.W), np.uint8)
    if inten is not None:
        iu8, meta["intensity_stretch"] = stretch_u8(inten)
    meta["coverage"] = dict(naip=float(naip.any(axis=0).mean()), hag=float((hag != 255).mean()),
                            cls=float((cls != 0).mean()), dtm=float((dtm != 65535).mean()),
                            intensity=float((iu8 != 0).mean()))
    np.savez_compressed(os.path.join(out, "stack.npz"), naip=naip, seg=seg, hag=hag, cls=cls, inten=iu8, dtm=dtm)

    if labels:
        t = time.time()
        try:
            fc = overpass_labels(g1.ll_bbox)
            json.dump(fc, open(os.path.join(out, "labels.geojson"), "w"))
            meta["labels"] = dict(features=len(fc["features"]))
        except Exception:                                        # noqa: BLE001
            meta["errors"]["labels"] = traceback.format_exc()[-1200:]
        meta["seconds"]["labels"] = round(time.time() - t, 1)
    meta["course"] = {k: course.get(k) for k in ("name", "osm", "center", "bbox", "state", "town")}
    meta["boundary"] = course.get("boundary")
    meta["seconds"]["total"] = round(time.time() - t0, 1)
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), indent=1, default=str)
    log(json.dumps({k: meta.get(k) for k in ("coverage", "seconds", "errors", "segment", "labels")}, default=str)[:3000])
    return meta


def dev_crop(stack_dir, out_dir, size_m=700, center_ll=None):
    """A small crop of a stack (+ its labels) for local development; centred on the clubhouse when OSM has one."""
    import stack as S
    st = S.load(stack_dir)
    if center_ll is None:
        lab = st.labels or {"features": []}
        ch = [f for f in lab["features"] if f["properties"].get("golf") == "clubhouse"
              or f["properties"].get("building") == "clubhouse"]
        if ch:
            c = np.array(S.flat_coords(ch[0]["geometry"]), float)
            center_ll = c.mean(axis=0).tolist()
        else:
            center_ll = st.meta["course"]["center"]
    cr = st.crop(center_ll, size_m)
    cr.save(out_dir)
    return out_dir


def course_from_sample(slug):
    """No course.json yet (generalize has not run it): resolve the sampled OSM element's boundary via Overpass."""
    import fetch_course as fcm
    import platform_common as pc
    entry = next(c for c in json.load(open(os.path.join(CD, "generalize", "sample.json")))["courses"] if c["slug"] == slug)
    typ, oid = entry["osm"].split("/")
    data = pc.overpass(f"[out:json][timeout:120];{typ}({oid});out body geom;", tries=3)
    fc = fcm.to_geojson(data.get("elements", []))
    if not fc["features"]:
        raise SystemExit(f"{slug}: OSM element {entry['osm']} not found")
    geom = fc["features"][0]["geometry"]
    xy = np.array(S_flat(geom), float)
    return dict(schema="course/1", status="ok", name=entry["name"], slug=slug, state=entry["state"],
                osm=dict(type=typ, id=int(oid)), center=entry["center"],
                bbox=[float(xy[:, 0].min()), float(xy[:, 1].min()), float(xy[:, 0].max()), float(xy[:, 1].max())],
                boundary=geom, resolved_by="perception.fetch_stack (sample.json osm element)")


def S_flat(geom):
    import stack as S
    return S.flat_coords(geom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--course", help="course.json (default course_data/generalize/courses/<slug>/course.json)")
    ap.add_argument("--out", help="default course_data/perception/work/<slug>")
    ap.add_argument("--margin", type=float, default=150.0)
    ap.add_argument("--no-segment", action="store_true")
    ap.add_argument("--dev-crop", type=float, default=0)
    a = ap.parse_args()
    cpath = a.course or os.path.join(CD, "generalize", "courses", a.slug, "course.json")
    if os.path.exists(cpath):
        course = json.load(open(cpath))
    else:
        course = course_from_sample(a.slug)
    out = a.out or os.path.join(HERE, "work", a.slug)
    if not os.path.exists(os.path.join(out, "stack.npz")):
        build(a.slug, course, out, a.margin, segment=not a.no_segment)
    else:
        log("stack exists (cache):", out)
    if a.dev_crop:
        dev_crop(out, os.path.join(HERE, "dev", a.slug), a.dev_crop)


if __name__ == "__main__":
    main()
