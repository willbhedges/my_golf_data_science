"""Build an OSM-labelled NAIP training set from well-mapped courses (GitHub Actions only: Overpass + Planetary
Computer, ~20 s per course).

    python course_data/segment/train/build_dataset.py --out /tmp/golfseg_data [--states IA MO] [--max 160]
    python course_data/segment/train/build_dataset.py --out /tmp/d --courses course_data/segment/train/v2_courses.json \
        --shard 3 --nshards 12 --quality            (v2: the national list from pick_v2.py, one shard per job)

Courses: course_data/packages/_survey/<STATE>.json rows with >= 9 greens and >= 7 fairways (bunkers >= 3),
minus the evaluation courses (Spirit Hollow, Veenker, Mozingo Lake: never trained on). Per course:
  * Overpass: the course outline + every golf=* / natural=water / water=* feature inside it;
  * NAIP (newest year with full cover and a NIR band) on a UTM 0.6 m grid (area-averaged), via
    course_data/vision_any/fetch_any.py's Planetary Computer helpers;
  * label raster: 0 background inside the outline, 1 green, 2 tee, 3 fairway, 4 bunker, 5 water (painted
    fairway < tee < green < water < bunker), 255 = ignore outside the outline (OSM maps nothing there).
Writes <out>/<osm type>_<id>.npz (img uint8 4xHxW, lab uint8 HxW) and <out>/index.json.
v2 (--courses): the image stays the fetched NAIP GeoTIFF (JPEG q88, the same bytes v1 decoded) as <name>.tif and
the npz holds lab only (about 4x smaller); --quality drops courses whose OSM polygons miss holes (quality()).
Labels: OpenStreetMap contributors, ODbL 1.0. Imagery: USDA NAIP (public domain).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = os.path.dirname(HERE)
CD = os.path.dirname(SEG)
ROOT = os.path.dirname(CD)
sys.path[:0] = [os.path.join(CD, "platform"), os.path.join(CD, "vision_any"), CD]

EXCLUDE = {"relation/13353211", "way/44804299", "way/385067034"}      # Spirit Hollow, Veenker, Mozingo Lake
CODE = {"green": 1, "tee": 2, "fairway": 3, "bunker": 4, "water": 5}
PAINT = ["fairway", "tee", "green", "water", "bunker"]


def candidates(states, max_n):
    rows = []
    for st in states:
        d = json.load(open(os.path.join(CD, "packages", "_survey", f"{st}.json")))
        for r in d["courses"]:
            c = r.get("counts", {})
            if r["osm"] in EXCLUDE or c.get("green", 0) < 9 or c.get("fairway", 0) < 7 or c.get("bunker", 0) < 3:
                continue
            rows.append(dict(r, state=st))
    rows.sort(key=lambda r: (-r.get("score", 0), -r["counts"].get("fairway", 0)))
    # interleave states so a cap keeps both
    by = {s: [r for r in rows if r["state"] == s] for s in states}
    out = []
    while any(by.values()) and len(out) < max_n:
        for s in states:
            if by[s] and len(out) < max_n:
                out.append(by[s].pop(0))
    return out


def from_list(path, shard, nshards, max_n):
    d = json.load(open(path))
    rows = [dict(r, score=0) for r in d["courses"] if r["osm"] not in EXCLUDE]
    return rows[shard::nshards][:max_n]


def quality(feats, tr, holes):
    """label completeness from the OSM polygons (projected with tr): bunkers >= 3; with golf=hole ways for >= 80 % of
    the holes, hole ends near a green polygon (25 m) >= 80 %, starts near a tee polygon (30 m) >= 70 %, par 4 / 5
    lines (or >= 230 m without a par) crossing a fairway >= 70 %; without hole ways greens >= 0.9 x holes, tees >=
    holes, fairways >= 0.6 x holes. -> (ok, info)"""
    from shapely.geometry import shape, Point
    from shapely.ops import transform as stransform, unary_union
    P = {c: [] for c in CODE}
    lines = []
    for f in feats:
        g = f["geometry"]
        pr = f["properties"]
        if pr.get("golf") == "hole" and g["type"] == "LineString" and len(g["coordinates"]) >= 2:
            lines.append((stransform(tr, shape(g)), pr.get("par")))
            continue
        c = feature_class(pr)
        if c and g["type"] in ("Polygon", "MultiPolygon"):
            try:
                P[c].append(stransform(tr, shape(g)).buffer(0))
            except Exception:                                   # noqa: BLE001
                pass
    n = {c: len(v) for c, v in P.items()}
    info = dict(n=n, hole_ways=len(lines), holes=holes)
    if n["bunker"] < 3:
        return False, dict(info, why="bunkers < 3")
    if len(lines) >= 0.8 * holes:
        U = {c: unary_union(P[c]) if P[c] else None for c in ("green", "tee", "fairway")}
        def near(pt, c, d):
            return U[c] is not None and U[c].distance(Point(pt)) <= d
        gc = sum(near(l.coords[-1], "green", 25) for l, _ in lines) / len(lines)
        tc = sum(near(l.coords[0], "tee", 30) for l, _ in lines) / len(lines)
        long_ = [l for l, par in lines if (str(par).strip() in ("4", "5", "6")) or (not par and l.length >= 230)]
        fc = (sum(U["fairway"] is not None and l.intersects(U["fairway"]) for l in long_) / len(long_)) if long_ else 1.0
        info.update(green_cov=round(gc, 3), tee_cov=round(tc, 3), fairway_cov=round(fc, 3))
        if gc < 0.8 or tc < 0.7 or fc < 0.7:
            return False, dict(info, why="polygons miss holes")
        return True, info
    if n["green"] < 0.9 * holes or n["tee"] < holes or n["fairway"] < 0.6 * holes:
        return False, dict(info, why="too few polygons (no hole ways)")
    return True, info


def osm_course(osm):
    import fetch_course as FC
    import platform_common as pc
    typ, oid = osm.split("/")
    q = f"""[out:json][timeout:180];
    {typ}({oid})->.c;
    .c out body geom;
    .c map_to_area->.a;
    (nwr["golf"](area.a); nwr["natural"="water"](area.a); nwr["water"](area.a););
    out body geom;"""
    if os.environ.get("SEGDATA_OSM", "overpass") == "overpass":
        try:
            els = pc.overpass(q, timeout=200).get("elements", [])
            fc = FC.to_geojson(els)
            outline = [f for f in fc["features"] if f["properties"].get("osm_id") == int(oid)
                       and f["properties"].get("osm_type") == typ and f["geometry"]["type"] in ("Polygon", "MultiPolygon")]
            return (outline[0] if outline else None), [f for f in fc["features"] if f not in outline]
        except RuntimeError as e:
            print("  overpass failed, OSM API instead:", str(e)[:160], flush=True)
    return osm_course_api(osm)


def osm_course_api(osm):
    """the same answer from the OSM API (fastpath/osm_api.py: <type>/<id>/full + map?bbox=), features kept when
    their representative point lies inside the outline (what Overpass's map_to_area query returns)."""
    import fetch_course as FC
    from shapely.geometry import shape
    sys.path.insert(0, os.path.join(CD, "platform", "fastpath"))
    import osm_api
    cache = os.environ.get("SEGDATA_OSM_CACHE") or os.path.join(tempfile.gettempdir(), "segdata_osm")
    c = osm_api.course_from_row(dict(osm=osm, name="", state="", lat=0.0, lon=0.0), cache)
    if not c.get("boundary") or c["boundary"]["type"] not in ("Polygon", "MultiPolygon"):
        return None, []
    outline = dict(type="Feature", geometry=c["boundary"], properties={})
    og = shape(c["boundary"]).buffer(0)
    w, s, e, n = c["bbox"]
    fc = FC.to_geojson(osm_api.features_data((s, w, n, e), cache).get("elements", []))
    typ, oid = osm.split("/")
    feats = []
    for f in fc["features"]:
        pr = f["properties"]
        if pr.get("osm_id") == int(oid) and pr.get("osm_type") == typ:
            continue
        if not (pr.get("golf") or pr.get("natural") == "water" or pr.get("water")):
            continue
        try:
            if og.contains(shape(f["geometry"]).representative_point()):
                feats.append(f)
        except Exception:                                       # noqa: BLE001
            pass
    return outline, feats


def feature_class(p):
    g = p.get("golf")
    if g in ("green", "tee", "fairway", "bunker"):
        return g
    if g in ("water_hazard", "lateral_water_hazard") or p.get("natural") == "water" or p.get("water"):
        return "water"
    return None


def build_one(row, out_dir, cat, v2=False, check=False):
    import rasterio
    import rasterio.features
    from pyproj import Transformer
    from shapely.geometry import shape
    from shapely.ops import transform as stransform
    import fetch_any as FA
    outline, feats = osm_course(row["osm"])
    if outline is None:
        return dict(error="no outline")
    og = shape(outline["geometry"]).buffer(0)
    w, s, e, n = og.bounds
    g1 = FA.Grid((s, w, n, e), 30.0, 1.0)
    qinfo = None
    if check:
        ok, qinfo = quality(feats, Transformer.from_crs("EPSG:4326", g1.crs, always_xy=True).transform,
                            int(row.get("holes") or 18))
        if not ok:
            return dict(error="quality: " + qinfo["why"], quality=qinfo)
    with tempfile.TemporaryDirectory() as td:
        meta = {}
        FA.fetch_naip(cat, g1, td, meta, n_years=1, res=0.6)
        ys = meta.get("naip", {}).get("years") or []
        if not ys:
            return dict(error="no NAIP with NIR", naip=meta.get("naip"))
        with rasterio.open(os.path.join(td, ys[0]["file"])) as src:
            img = src.read()
            T, crs = src.transform, src.crs
            if v2:
                import shutil
                shutil.copy(os.path.join(td, ys[0]["file"]), os.path.join(out_dir, row["osm"].replace("/", "_") + ".tif"))
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform
    H, W = img.shape[1:]
    lab = np.full((H, W), 255, np.uint8)
    inside = rasterio.features.rasterize([(stransform(tr, og), 1)], out_shape=(H, W), transform=T, fill=0, dtype="uint8")
    lab[inside > 0] = 0
    counts = {}
    for c in PAINT:
        gs = []
        for f in feats:
            if feature_class(f["properties"]) == c and f["geometry"]["type"] in ("Polygon", "MultiPolygon"):
                g = shape(f["geometry"]).buffer(0)
                if not g.is_empty:
                    gs.append((stransform(tr, g), 1))
        counts[c] = len(gs)
        if gs:
            m = rasterio.features.rasterize(gs, out_shape=(H, W), transform=T, fill=0, dtype="uint8")
            lab[m > 0] = CODE[c]
    lab[~img.any(axis=0)] = 255
    name = row["osm"].replace("/", "_")
    if v2:
        np.savez_compressed(os.path.join(out_dir, name + ".npz"), lab=lab)
    else:
        np.savez_compressed(os.path.join(out_dir, name + ".npz"), img=img, lab=lab)
    return dict(file=name + ".npz", image=(name + ".tif") if v2 else None, quality=qinfo,
                shape=[H, W], naip_year=ys[0]["year"], naip_items=ys[0]["items"],
                counts=counts, pixels={k: int((lab == v).sum()) for k, v in CODE.items()},
                inside=int((lab != 255).sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--states", nargs="+", default=["IA", "MO"])
    ap.add_argument("--max", type=int, default=160)
    ap.add_argument("--minutes", type=float, default=100.0, help="stop adding courses after this long")
    ap.add_argument("--courses", help="v2: course list json (pick_v2.py)")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--quality", action="store_true", help="drop courses whose polygons miss holes (quality())")
    a = ap.parse_args()
    import fetch_any as FA
    os.makedirs(a.out, exist_ok=True)
    ip = os.path.join(a.out, "index.json")
    index = json.load(open(ip)) if os.path.exists(ip) else {"courses": {}}
    cat = FA.stac()
    t0 = time.time()
    rows = from_list(a.courses, a.shard, a.nshards, a.max) if a.courses else candidates(a.states, a.max)
    print(f"{len(rows)} candidate courses", flush=True)
    for i, r in enumerate(rows):
        if (time.time() - t0) / 60 > a.minutes:
            print("time budget reached")
            break
        if r["osm"] in index["courses"] and "file" in index["courses"][r["osm"]] \
                and os.path.exists(os.path.join(a.out, index["courses"][r["osm"]]["file"])):
            continue
        if str(index["courses"].get(r["osm"], {}).get("error", "")).startswith("quality"):
            continue
        try:
            res = build_one(r, a.out, cat, v2=bool(a.courses), check=a.quality)
        except Exception as e:  # noqa: BLE001
            res = dict(error=f"{type(e).__name__}: {e}"[:300], tb=traceback.format_exc()[-600:])
        res.update(name=r["name"], state=r["state"], osm=r["osm"])
        index["courses"][r["osm"]] = res
        print(f"[{i + 1}/{len(rows)} {time.time() - t0:.0f}s] {r['state']} {r['name']}: "
              + (res.get("error") or f"{res['shape']} {res['counts']}"), flush=True)
        json.dump(index, open(ip, "w"), indent=1)
    ok = [c for c in index["courses"].values() if "file" in c]
    index.update(n_ok=len(ok), labels="OpenStreetMap contributors (ODbL 1.0)", imagery="USDA NAIP via Planetary Computer",
                 classes=["background", "green", "tee", "fairway", "bunker", "water"], ignore=255,
                 excluded_eval_courses=sorted(EXCLUDE))
    json.dump(index, open(ip, "w"), indent=1)
    print(f"{len(ok)} courses ok")


if __name__ == "__main__":
    main()
