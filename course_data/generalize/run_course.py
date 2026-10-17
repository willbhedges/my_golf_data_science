"""One sampled course end to end on GitHub Actions: resolve, fetch, segment, package, routing.

  python course_data/generalize/run_course.py <slug> [--sample course_data/generalize/sample.json] [--no-segment]

Work files (big: NAIP, DEM, raw OSM) go to course_data/generalize/work/<slug>/ (not committed). Small outputs
go to course_data/generalize/courses/<slug>/ (committed by the workflow's report job):
  result.json        what we measured: resolve by name, OSM coverage, scorecard, segment, lidar, the package
                     built today (per hole: hole line, green polygon, tee), the package built with routing
  osm_golf.geojson   the course's OSM golf / parking / building features (routing inputs; ODbL)
  segment.geojson    NAIP U-Net greens / tees / fairways (p, area) inside the course (+60 m)
  pads.json          lidar flat-pad tee candidates (tees/lidar_pads.py on the 3DEP DEM, all of them)
  scorecard.json     the web cards found (normalised) + what was tried
  course.json        resolve output (boundary, candidates)
report.py recomputes routing and its validation from these files offline.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [os.path.join(CD, "platform"), CD]
import platform_common as pc  # noqa: E402

WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "courses")
KEEP_PROPS = ("golf", "ref", "par", "name", "osm_id", "osm_type", "inside_course", "amenity", "service", "building",
              "leisure", "handicap", "tee", "golf:tee", "colour", "color", "parking", "club", "landuse", "natural",
              "surface", "access")


def log(*a):
    print(*a, flush=True)


def timed(res, key, fn, *a, **k):
    t0 = time.time()
    try:
        return fn(*a, **k)
    except SystemExit as e:
        res.setdefault("errors", {})[key] = f"SystemExit: {e}"[:600]
    except Exception as e:                                       # noqa: BLE001
        traceback.print_exc()
        res.setdefault("errors", {})[key] = f"{type(e).__name__}: {e}"[:600]
    finally:
        res.setdefault("seconds", {})[key] = round(time.time() - t0, 1)
    return None


def golf_subset(fc):
    keep = []
    for f in fc["features"]:
        p = f["properties"]
        if p.get("golf") or p.get("amenity") == "parking" or p.get("service") == "parking_aisle" or \
                p.get("leisure") == "golf_course" or (p.get("building") and p.get("inside_course") is not False):
            keep.append(dict(type="Feature", geometry=f["geometry"],
                             properties={k: v for k, v in p.items() if k in KEEP_PROPS}))
    return dict(type="FeatureCollection", features=keep)


def parking(course):
    w, s, e, n = course["bbox"]
    d = 0.003
    q = f"""[out:json][timeout:90];
    (nwr["amenity"="parking"]({s - d},{w - d},{n + d},{e + d}););
    out tags center;"""
    feats = []
    for el in pc.overpass(q, tries=2).get("elements", []):
        c = el.get("center") or ({"lat": el["lat"], "lon": el["lon"]} if "lat" in el else None)
        if c:
            feats.append(dict(type="Feature", geometry=dict(type="Point", coordinates=[c["lon"], c["lat"]]),
                              properties=dict(amenity="parking", osm_type=el["type"], osm_id=el["id"],
                                              **{k: v for k, v in el.get("tags", {}).items() if k in ("name", "access")})))
    return feats


def naip4(img_dir, out_path, res=0.6):
    """naip_rgb.tif + naip_nir.tif (native grid) -> 4-band uint8 R,G,B,NIR GeoTIFF at `res` m (area average)."""
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import Affine
    with rasterio.open(os.path.join(img_dir, "naip_rgb.tif")) as s:
        r0 = abs(s.transform.a)
        f = max(1, int(round(res / r0)))
        H, W = s.height // f, s.width // f
        rgb = s.read(out_shape=(3, H, W), resampling=Resampling.average)
        T = s.transform * Affine.scale(s.width / W, s.height / H)
        crs = s.crs
    with rasterio.open(os.path.join(img_dir, "naip_nir.tif")) as s:
        nir = s.read(1, out_shape=(H, W), resampling=Resampling.average)
    arr = np.concatenate([rgb, nir[None]]).astype(np.uint8)
    prof = dict(driver="GTiff", width=W, height=H, count=4, dtype="uint8", crs=crs, transform=T, compress="deflate")
    with rasterio.open(out_path, "w", **prof) as d:
        d.write(arr)
    return dict(res_m=round(abs(T.a), 3), native_m=round(r0, 3), shape=[4, H, W])


def run_segment(naip_path, boundary):
    import numpy as np
    import rasterio
    sys.path.insert(0, os.path.join(CD, "segment"))
    import model as M
    import polygons as P
    with rasterio.open(naip_path) as s:
        img = s.read()
        T, crs = s.transform, s.crs
    mdl, _, sha = M.load(threads=os.cpu_count())
    t0 = time.time()
    probs = M.predict_raster(mdl, img, tta=True, log=None)
    valid = img.any(axis=0)
    wm, ws = M.nir_water(img)
    feats = P.polygonize(probs, T, crs, src=f"segment:ariadgolf-v4@{str(sha)[:8]}", water=(wm, ws), valid=valid)
    import routing as R
    rings = R._outer_rings(boundary) if boundary else []
    keep = [f for f in feats if f["properties"]["class"] in ("green", "tee", "fairway", "bunker")
            and (not rings or R._near_rings(R._ll_of(f["geometry"]), rings, 60))]
    for f in keep:
        f["geometry"]["coordinates"] = _round(f["geometry"]["coordinates"])
    return dict(type="FeatureCollection", features=keep,
                properties=dict(model=M.REPO, model_sha=sha, seconds_infer=round(time.time() - t0, 1),
                                licence="ariadgolf weights: research/evaluation only (no licence granted)"))


def _round(c):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
        return [round(float(c[0]), 7), round(float(c[1]), 7)]
    return [_round(x) for x in c]


def today_metrics(package):
    """Per hole from a built package: hole line, green polygon (OSM / segment), tee from a box / pad."""
    holes = package.get("holes", {})
    per = {}
    for k, h in holes.items():
        t = (h.get("tees") or {}).get(package.get("tee_set")) or next(iter((h.get("tees") or {}).values()), {})
        meth = str(t.get("method", ""))
        per[k] = dict(par=h.get("par"), line=bool(h.get("hole_line_ll")), green_polygon=bool(h.get("green_polygon_ll")),
                      green_src=h.get("provenance", {}).get("green"),
                      tee=bool(t.get("tee_ll")) and not any(x in meth for x in ("walkback", "hole-line start", "hole line start")),
                      tee_method=meth, measured=t.get("measured_yards"), card=t.get("card_yards"))
    return dict(holes_built=len(holes), with_green_polygon=sum(v["green_polygon"] for v in per.values()),
                green_osm=sum(str(v["green_src"]).startswith("osm") for v in per.values()),
                green_segment=sum(v["green_src"] == "segment" for v in per.values()),
                with_tee_box=sum(v["tee"] for v in per.values()), stages=package.get("stages"),
                tee_set=package.get("tee_set"), per_hole=per)


def build(pkg_dir, req, seg_path=None):
    import package as pk
    p = pk.build_package(req, pkg_dir, render=False, gapfill=False)
    if seg_path and os.path.exists(seg_path):
        mod = pk.load(os.path.join(CD, "segment", "gapfill.py"), "cdp_segment_gapfill")
        try:
            p = mod.segment_gapfill(p, seg_path, reframe=False, log=lambda *a: None)
        except Exception as e:                                   # noqa: BLE001
            p.setdefault("stages", {})["segment"] = f"failed: {e!r}"[:200]
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--sample", default=os.path.join(HERE, "sample.json"))
    ap.add_argument("--no-segment", action="store_true")
    ap.add_argument("--no-imagery", action="store_true")
    a = ap.parse_args()
    entry = next(c for c in json.load(open(a.sample))["courses"] if c["slug"] == a.slug)
    pc.PACKAGES = WORK                                    # packages of this study stay out of course_data/packages
    work = os.path.join(WORK, a.slug)
    raw = os.path.join(work, "raw")
    out = os.path.join(OUT, a.slug)
    os.makedirs(raw, exist_ok=True)
    os.makedirs(out, exist_ok=True)
    res = dict(slug=a.slug, sample=entry, run_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    import fetch_package as fp
    import resolve as rs

    # 1. found by name + state (what a golfer types), then the sampled element itself
    byname = timed(res, "resolve_by_name", rs.resolve, entry["name"], entry["state"])
    if byname:
        top = byname.get("osm") or {}
        res["resolve_by_name"] = dict(status=byname["status"], osm=top, name=byname.get("name"),
                                      same_element=f"{top.get('type')}/{top.get('id')}" == entry["osm"],
                                      candidates=[(c["name"], c.get("town"), c.get("holes"), f"{c['osm']['type']}/{c['osm']['id']}")
                                                  for c in byname.get("candidates", [])[:6]])
    course = byname if (byname and res["resolve_by_name"]["same_element"]) else \
        timed(res, "resolve_osm", rs.resolve, entry["name"], entry["state"], osm=entry["osm"])
    if not course or course.get("status") != "ok":
        res["fatal"] = "could not resolve the sampled element"
        json.dump(res, open(os.path.join(out, "result.json"), "w"), indent=1)
        return
    pc.write_json(os.path.join(raw, "course.json"), course)
    pc.write_json(os.path.join(out, "course.json"), course)

    # 2. OSM features (+ car parks for the clubhouse prior)
    got = timed(res, "osm", fp.fetch_osm, course, raw)
    if not got:
        res["fatal"] = "OSM fetch failed"
        json.dump(res, open(os.path.join(out, "result.json"), "w"), indent=1)
        return
    fc, summ = got
    pk_feats = timed(res, "parking", parking, course) or []
    fc["features"] += pk_feats
    pc.write_json(os.path.join(raw, "osm.geojson"), fc, indent=None)
    pc.write_json(os.path.join(out, "osm_golf.geojson"), golf_subset(fc), indent=None)
    import osm_coverage
    res["osm"] = dict(features=osm_coverage.feature_counts(fc), hole_refs=sorted(
        {str(f["properties"].get("ref")) for f in fc["features"] if f["properties"].get("golf") == "hole"
         and f["properties"].get("inside_course") is not False}), parking=len(pk_feats))

    # 3. scorecards
    req = dict(schema="request/1", kind="package", course=entry["name"], state=entry["state"], osm=entry["osm"],
               tees="back", allow_substitute=True, slug=a.slug)
    sw = timed(res, "scorecard", fp.fetch_scorecards, req, course, summ, raw) or {}
    res["scorecard"] = dict(found=[c["source"] for c in sw.get("cards", [])], tried=sw.get("tried"))
    import scorecard as scm
    cards = [dict(source=c["source"], url=c.get("url"), card=scm.normalise(c["card"])) for c in sw.get("cards", [])]
    pick = scm.choose_card([(c["source"], c["card"], c.get("url")) for c in cards]) if cards else None
    res["scorecard"]["chosen"] = pick[0] if pick else None
    if pick:
        n, pars = len(pick[1].get("par") or []), pick[1].get("par")
        res["scorecard"].update(holes=n or None, par_total=sum(int(p) for p in pars if str(p).isdigit()) if pars else None,
                                sets=list((pick[1].get("tee_sets") or {}).keys()))
    pc.write_json(os.path.join(out, "scorecard.json"), dict(cards=cards, chosen=pick[0] if pick else None,
                                                             tried=sw.get("tried")))

    # 4. imagery (NAIP + 3DEP DEM), segment model, lidar pads
    img = os.path.join(work, "imagery")
    if not a.no_imagery:
        ok = timed(res, "imagery", fp.fetch_imagery, course, work)
        res["imagery"] = dict(ok=bool(ok), files=sorted(os.listdir(img)) if os.path.isdir(img) else [])
        g = pc.read_json(os.path.join(img, "georef.json"), {}) or {}
        im = g.get("imagery") or {}
        res["imagery"].update(source=im.get("source"), year=im.get("year"), gsd_m=im.get("gsd_m"),
                              dem=(g.get("dem") or {}).get("source") if isinstance(g.get("dem"), dict) else None)
    seg_path = os.path.join(out, "segment.geojson")
    if not a.no_segment and os.path.exists(os.path.join(img, "naip_nir.tif")):
        n4 = os.path.join(work, "naip4_06m.tif")
        res["naip4"] = timed(res, "naip4", naip4, img, n4)
        seg = timed(res, "segment", run_segment, n4, course.get("boundary")) if res.get("naip4") else None
        if seg:
            pc.write_json(seg_path, seg, indent=None)
            from collections import Counter
            res["segment"] = dict(counts=dict(Counter(f["properties"]["class"] for f in seg["features"])),
                                  greens_p06=sum(1 for f in seg["features"] if f["properties"]["class"] == "green"
                                                 and f["properties"]["p"] >= 0.6),
                                  seconds_infer=seg["properties"]["seconds_infer"])
    dem = os.path.join(img, "dem.tif")
    if os.path.exists(dem):
        import package as pk
        lp = pk.load(os.path.join(CD, "tees", "lidar_pads.py"), "cdp_lidar_pads")
        _, _, greens = pk.osm_tee_inputs(fc)
        pads = timed(res, "lidar_pads", lp.detect_pads, dem, greens=greens, lines=None) if lp else None
        if pads is not None:
            pc.write_json(os.path.join(out, "pads.json"), [dict(id=p["id"], centroid=p["centroid"], coords=[
                [round(x, 7), round(y, 7)] for x, y in p["coords"]], area_m2=p["area_m2"]) for p in pads])
            res["lidar_pads"] = len(pads)

    # 5. the package as built today (OSM hole ways only), + segment gap-fill of greens
    pk_today = timed(res, "package_today", build, work, req, seg_path)
    res["today"] = today_metrics(pk_today) if pk_today else dict(holes_built=0, reason=res.get("errors", {}).get("package_today"))

    # 6. routing (production: mapped holes are anchors) and the package built on it
    import routing as R
    rd = lambda p: pc.read_json(p) if os.path.exists(p) else None       # noqa: E731
    seg_fc, pads_js = rd(seg_path), rd(os.path.join(out, "pads.json"))
    pads_in = [dict(id=p["id"], centroid=p["centroid"], coords=[tuple(c) for c in p["coords"]]) for p in (pads_js or [])]
    inp = R.inputs_from_fc(fc, segment=seg_fc, pads=pads_in, boundary=course.get("boundary"))
    rt = timed(res, "routing", R.route, inp, pick[1] if pick else None)
    if rt:
        res["routing"] = {k: v for k, v in rt.items() if k != "holes"}
        res["routing"]["holes"] = {k: {kk: v.get(kk) for kk in ("status", "flags", "green_src", "tee_src", "straight_yd",
                                                                "card_yards", "p_green", "anchored")}
                                   for k, v in rt["holes"].items()}
        fc2 = R.to_hole_features(rt, fc, inp)
        wr = os.path.join(WORK, a.slug + "__routed")
        os.makedirs(os.path.join(wr, "raw"), exist_ok=True)
        for f in ("course.json", "summary.json", "scorecard_web.json"):
            if os.path.exists(os.path.join(raw, f)):
                shutil.copy(os.path.join(raw, f), os.path.join(wr, "raw", f))
        pc.write_json(os.path.join(wr, "raw", "osm.geojson"), fc2, indent=None)
        if os.path.isdir(img) and not os.path.exists(os.path.join(wr, "imagery")):
            os.symlink(img, os.path.join(wr, "imagery"))
        pk_routed = timed(res, "package_routed", build, wr, dict(req, slug=a.slug + "__routed"), seg_path)
        res["with_routing"] = today_metrics(pk_routed) if pk_routed else dict(holes_built=0)
    json.dump(res, open(os.path.join(out, "result.json"), "w"), indent=1, default=str)
    log(json.dumps({k: res.get(k) for k in ("resolve_by_name", "scorecard", "segment", "lidar_pads", "seconds", "errors")},
                   default=str)[:3000])
    log("today:", {k: v for k, v in res["today"].items() if k not in ("per_hole", "stages")})
    log("routed:", {k: v for k, v in (res.get("with_routing") or {}).items() if k not in ("per_hole", "stages")})


if __name__ == "__main__":
    main()
