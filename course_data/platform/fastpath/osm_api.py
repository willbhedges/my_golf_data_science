"""OSM for one course from the OSM API (api.openstreetmap.org), in the shapes the package build already reads.

Why: the public Overpass mirrors time out under load (osm_extract.py's header) and a Geofabrik state file is a
0.1-1.2 GB download; the OSM API answers `map?bbox=` for one course in 1-3 s and `<type>/<id>/full` in < 1 s.

  course_from_row(row, cache)       national-index row (library/us_courses.json.gz) -> course.json dict (resolve.py's)
  features(course, raw_dir, cache)  -> (FeatureCollection, summary): writes raw/osm.geojson, summary.json,
                                     osm_source.json through fetch_package.fetch_osm (the pipeline's own code;
                                     only the transport is replaced)
Every response is kept on disk (cache/osm/...): a re-run reads no network.
"""
import hashlib
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
for p in (PLAT, CD):
    if p not in sys.path:
        sys.path.insert(0, p)
import platform_common as pc  # noqa: E402
import osm_extract as ox  # noqa: E402

API = "https://api.openstreetmap.org/api/0.6/"
UA = {"User-Agent": "golf-course-strategy-research/1.0 (fast path; one course per request)"}
MAX_SPLIT = 3


def _get(url, path, timeout=60):
    """-> (path, seconds, from_cache). Raises RuntimeError('HTTP <code> ...') on an error status."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path, 0.0, True
    import requests
    t0 = time.time()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r = requests.get(url, headers=UA, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} {r.text[:200]}")
    with open(path + ".tmp", "wb") as fh:
        fh.write(r.content)
    os.replace(path + ".tmp", path)
    return path, time.time() - t0, False


def course_from_row(row, cache):
    """row: dict(name, city, state, lat, lon, osm 'way/123', osm_holes, ...) -> resolve.py's course dict."""
    import fetch_course as fcm
    typ, oid = row["osm"].split("/")
    oid = int(oid)
    geom = b = None
    tags = {}
    if typ in ("way", "relation"):
        p, _, _ = _get(f"{API}{typ}/{oid}/full", os.path.join(cache, "osm", f"{typ}_{oid}_full.xml"))
        osm = ox.read_osm(p)
        el = ox.element(osm, typ, oid, geom=True)
        tags = el.get("tags") or {}
        feats = fcm.to_geojson([el])["features"]
        geom = feats[0]["geometry"] if feats else None
        if geom and geom["type"] == "LineString":
            c = geom["coordinates"]
            geom = {"type": "Polygon", "coordinates": [c + [c[0]]]}
        b = fcm.bounds_of(el)
    else:
        p, _, _ = _get(f"{API}node/{oid}", os.path.join(cache, "osm", f"node_{oid}.xml"))
        osm = ox.read_osm(p)
        tags = osm["nodes"][oid][2]
    lat, lon = row["lat"], row["lon"]
    note = None
    if b is None:
        d = 800 / 111320.0
        b = dict(minlat=lat - d, maxlat=lat + d, minlon=lon - d / math.cos(math.radians(lat)),
                 maxlon=lon + d / math.cos(math.radians(lat)))
        note = "course mapped as a point: bbox is 800 m around it"
    import resolve as rs
    keep = {k: v for k, v in tags.items() if k.startswith(("addr:", "name", "operator", "access", "golf:", "holes", "par"))
            or k in rs.CLOSED_TAGS}
    cand = dict(name=tags.get("name") or row["name"], osm=dict(type=typ, id=oid), tags=keep)
    why = rs.closed_reason(cand, row["name"])
    out = dict(schema="course/1", query=dict(name=row["name"], state=row["state"], town=row.get("city"), osm=row["osm"],
                                             near=f"{lat},{lon}"),
               status="closed" if why else "ok", candidates=[dict(name=cand["name"], town=row.get("city"), holes=row.get("osm_holes"),
                                                                  osm=cand["osm"], center=[lon, lat], score=None)],
               name=tags.get("name") or row["name"], osm_name=tags.get("name"), slug=pc.slugify(tags.get("name") or row["name"]),
               osm=dict(type=typ, id=oid), center=[(b["minlon"] + b["maxlon"]) / 2, (b["minlat"] + b["maxlat"]) / 2],
               bbox=[b["minlon"], b["minlat"], b["maxlon"], b["maxlat"]],
               address=", ".join(x for x in (row.get("city"), row["state"]) if x), town=row.get("city") or None,
               state=row["state"], holes_mapped=row.get("osm_holes"),
               website=tags.get("website") or tags.get("contact:website") or tags.get("url"), tags=keep, boundary=geom,
               boundary_note=note, site=None, resolved_by="national index + OSM API (fastpath/osm_api.py)")
    if why:
        out["closed"] = f"{cand['name']} ({typ}/{oid}): {why}"
    return out


def _map(snwe, cache, depth=0):
    """OSM XML files covering the box (split in four when the API refuses it: > 50,000 nodes)."""
    s, w, n, e = snwe
    key = hashlib.sha1(f"{s:.6f},{w:.6f},{n:.6f},{e:.6f}".encode()).hexdigest()[:16]
    path = os.path.join(cache, "osm", f"map_{key}.xml")
    try:
        p, dt, hit = _get(f"{API}map?bbox={w:.7f},{s:.7f},{e:.7f},{n:.7f}", path, timeout=120)
        return [p]
    except RuntimeError as ex:
        if depth >= MAX_SPLIT or "HTTP 400" not in str(ex):
            raise
    ms, mw = (s + n) / 2, (w + e) / 2
    out = []
    for q in ((s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e)):
        out += _map(q, cache, depth + 1)
    return out


def features_data(snwe, cache):
    """the features query's answer (Overpass shape) for the box, from the OSM API"""
    files = _map(ox.pad_snwe(snwe, 60.0), cache)
    if len(files) == 1:
        return ox.overpass_shape(ox.select(ox.read_osm(files[0]), snwe, ox.query_filters(None)), None,
                                 generator="OSM API map call (course_data/platform/fastpath/osm_api.py)")
    merged = dict(nodes={}, ways={}, rels={})
    for f in files:
        o = ox.read_osm(f)
        for k in merged:
            merged[k].update(o[k])
    return ox.overpass_shape(ox.select(merged, snwe, ox.query_filters(None)), None,
                             generator="OSM API map call, tiled (course_data/platform/fastpath/osm_api.py)")


def features(course, raw_dir, cache, req=None):
    """raw/osm.geojson + summary.json + osm_source.json exactly as fetch_package.fetch_osm writes them"""
    import fetch_course as fcm
    import fetch_package as fp
    import osm_guard as og

    def guarded(snwe, course=None, slug=None, **kw):
        data = features_data(snwe, cache)
        fc = fcm.to_geojson(data.get("elements", []))
        c = og.golf_counts(fc)
        return data, fc, dict(schema="osm_source/1", fetched_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                              source="overpass", mirror=API + "map", osm_base=None, counts=c, reason="complete",
                              mirrors_tried=[API + "map"], note="OSM API bbox call (fast path)")
    old = og.fetch_guarded
    og.fetch_guarded = guarded
    try:
        req = req or {}
        return fp.fetch_osm(course, raw_dir, drop_holes=bool(req.get("ignore_osm_holes")), supplement=req.get("osm_supplement"))
    finally:
        og.fetch_guarded = old
