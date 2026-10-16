"""S1 fetch for a course request (GitHub Actions only: Overpass, Nominatim, scorecard sites, NAIP, 3DEP).

  python course_data/platform/fetch_package.py course_data/requests/package_mozingo_lake.json

Writes course_data/packages/<slug>/raw/:
  course.json        resolve.py output (status, OSM id, boundary, bbox, town, candidates)
  osm_raw.json       Overpass response for the boundary bbox + buffer
  osm.geojson        WGS84 features with raw tags + inside_course (fetch_course.to_geojson / summarise)
  summary.json       fetch_course-style summary (tag counts, holes, tees)
  scorecard_web.json scorecards found on the web (golfify, club site) + what was tried
  scorecard/         raw page texts (audit trail)
and packages/<slug>/imagery/ (NAIP RGB + NIR COGs, 3DEP DEM, georef.json) via imagery/fetch_imagery.py,
unless the request names an existing `imagery_dir` or sets "imagery": false.
"""
import json
import math
import os
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import platform_common as pc  # noqa: E402
import resolve as rs  # noqa: E402
import scorecard as scm  # noqa: E402

BUFFER_M = 150.0


def request_slug(req, path=None):
    """slug: request "slug" > file name requests/package_<slug>.json > slug of the course name."""
    if req.get("slug"):
        return req["slug"]
    if path:
        stem = os.path.splitext(os.path.basename(path))[0]
        return stem[len(pc.REQUEST_PREFIX):] if stem.startswith(pc.REQUEST_PREFIX) else stem
    return pc.slugify(req["course"])


def pad(bbox, m):
    w, s, e, n = bbox
    dlat = m / 111320.0
    dlon = dlat / math.cos(math.radians((s + n) / 2))
    return (s - dlat, w - dlon, n + dlat, e + dlon)              # S, W, N, E (Overpass order)


def fetch_osm(course, raw):
    import fetch_course as fcm
    snwe = pad(course["bbox"], BUFFER_M)
    data = fcm.fetch_features(snwe)
    pc.write_json(os.path.join(raw, "osm_raw.json"), data, indent=None)
    fc = fcm.to_geojson(data["elements"])
    rings = fcm.outer_rings(course["boundary"]) if course.get("boundary") else []
    w, s, e, n = course["bbox"]
    el = dict(type=course["osm"]["type"], id=course["osm"]["id"], tags=dict(course.get("tags") or {},
              name=course["name"], leisure="golf_course"),
              center=dict(lon=course["center"][0], lat=course["center"][1]),
              bounds=dict(minlat=s, minlon=w, maxlat=n, maxlon=e))
    summ = fcm.summarise(fc, el, [el], rings)
    summ["bbox_wgs84_snwe"] = [round(v, 6) for v in snwe]
    summ["fetched_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    summ["osm_attribution"] = "(c) OpenStreetMap contributors, ODbL 1.0"
    pc.write_json(os.path.join(raw, "osm.geojson"), fc, indent=None)
    pc.write_json(os.path.join(raw, "summary.json"), summ)
    return fc, summ


def fetch_scorecards(req, course, summ, raw):
    out = dict(fetched_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), tried=[], cards=[])
    rawdir = os.path.join(raw, "scorecard")
    lengths = {str(h["ref"]): h["length_yd"] for h in summ.get("holes", []) if h.get("length_yd")}
    n = len(lengths) or None
    for label, fn in (("golfify", lambda: scm.fetch_golfify(course["name"], course["state"], course.get("town"), rawdir)),
                      ("club_site", lambda: scm.fetch_club_site(req.get("website") or course.get("website"), rawdir,
                                                                n, lengths))):
        try:
            card, info = fn()
        except Exception as e:                                # noqa: BLE001
            card, info = None, f"{label} crashed: {e!r}"[:300]
            traceback.print_exc()
        if card and not scm.plausible(card, n, lengths):
            info, card = f"{label}: card at {info} rejected (hole count / lengths don't fit OSM)", None
        out["tried"].append(dict(source=label, ok=bool(card), info=info))
        if card:
            out["cards"].append(dict(source=label, url=info, card=card))
    pc.write_json(os.path.join(raw, "scorecard_web.json"), out)
    return out


def fetch_imagery(course, pkg):
    img = os.path.join(pkg, "imagery")
    w, s, e, n = course["bbox"]
    cmd = [sys.executable, os.path.join(pc.COURSE_DATA, "imagery", "fetch_imagery.py"),
           "--bbox", f"{s},{w},{n},{e}", "--name", course["name"], "--margin", "100", "--max-mb", "45",
           "--out", img]
    pc.log("imagery:", " ".join(cmd))
    r = subprocess.run(cmd, timeout=2400)
    return r.returncode == 0


def fetch(req_path):
    req = pc.read_json(req_path)
    slug = request_slug(req, req_path)
    pkg = os.path.join(pc.PACKAGES, slug)
    raw = os.path.join(pkg, "raw")
    os.makedirs(raw, exist_ok=True)
    course = rs.resolve(req["course"], req["state"], req.get("town"), req.get("osm"), near=req.get("near"))
    pc.write_json(os.path.join(raw, "course.json"), course)
    pc.log("resolve:", course["status"], course.get("name"), course.get("osm"),
           [(c["name"], c["town"], c["holes"]) for c in course["candidates"][:5]])
    if course["status"] != "ok":
        return slug, course["status"]
    fc, summ = fetch_osm(course, raw)
    pc.log("osm:", len(fc["features"]), "features;", summ["golf_tag_counts_inside_course"])
    if req.get("web_scorecard", True):
        sw = fetch_scorecards(req, course, summ, raw)
        pc.log("scorecards:", json.dumps(sw["tried"]))
    import package as pk
    if req.get("imagery", True) and not pk.find_imagery(req, pkg, slug):
        ok = fetch_imagery(course, pkg)
        pc.log("imagery ok:", ok)
    return slug, "ok"


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(fetch(p))


def seed_from_dir(src_dir, pkg_dir):
    """Offline: make packages/<slug>/raw/ from an existing fetch_course.py output dir (summary.json +
    osm.geojson), e.g. course_data/spirit_hollow. The boundary comes from the course feature."""
    summ = pc.read_json(os.path.join(src_dir, "summary.json"))
    fc = pc.read_json(os.path.join(src_dir, "osm.geojson"))
    c = summ["course"]
    b = c["bounds"]
    geom = next((f["geometry"] for f in fc["features"] if f["properties"].get("osm_id") == c["osm_id"]
                 and f["properties"].get("osm_type") == c["osm_type"]), None)
    t = c.get("tags", {})
    course = dict(schema="course/1", status="ok", query=dict(name=c["name"], state=None, seeded_from=src_dir),
                  name=c["name"], slug=pc.slugify(c["name"]), osm=dict(type=c["osm_type"], id=c["osm_id"]),
                  center=[c["center"]["lon"], c["center"]["lat"]],
                  bbox=[b["minlon"], b["minlat"], b["maxlon"], b["maxlat"]], town=t.get("addr:city"), state=None,
                  website=t.get("website"), tags=t, holes_mapped=summ.get("hole_centrelines"), boundary=geom,
                  candidates=[])
    raw = os.path.join(pkg_dir, "raw")
    pc.write_json(os.path.join(raw, "course.json"), course)
    pc.write_json(os.path.join(raw, "osm.geojson"), fc, indent=None)
    pc.write_json(os.path.join(raw, "summary.json"), summ)
    return course
