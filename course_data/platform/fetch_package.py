"""S1 fetch for a course request (GitHub Actions only: Overpass, Nominatim, scorecard sites, NAIP, 3DEP).

  python course_data/platform/fetch_package.py course_data/requests/package_mozingo_lake.json

Writes course_data/packages/<slug>/raw/:
  course.json        resolve.py output (status, OSM id, boundary, bbox, town, candidates)
  osm_raw.json       Overpass response for the boundary bbox + buffer
  osm_source.json    which mirror / cached snapshot the OSM came from and why (osm_guard.py; also summary.json)
  osm.geojson        WGS84 features with raw tags + inside_course (fetch_course.to_geojson / summarise)
  summary.json       fetch_course-style summary (tag counts, holes, tees)
  scorecard_web.json scorecards found on the web (club site, golfify, OpenGolfAPI) + what was tried
                     (a request with "refetch": "scorecards" and an existing raw/ re-runs only this step:
                     fetch_scorecards_only)
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


def fetch_osm(course, raw, drop_holes=False, supplement=None):
    import fetch_course as fcm
    import osm_guard as og
    snwe = pad(course["bbox"], BUFFER_M)
    # mirror by mirror, rejecting partial (Overpass remark) / stale / thin answers; falls back to the newest cached
    # snapshot of this course (merged in) rather than silently building from fewer features (osm_guard.py)
    data, fc, src = og.fetch_guarded(snwe, course, slug=os.path.basename(os.path.dirname(os.path.abspath(raw))))
    if data is not None:
        pc.write_json(os.path.join(raw, "osm_raw.json"), data, indent=None)
    pc.write_json(os.path.join(raw, "osm_source.json"), src)
    if src["source"] != "overpass" or src.get("thin"):
        pc.log("osm_guard:", src["source"], "-", src["reason"])
    if drop_holes:     # request "ignore_osm_holes": the OSM golf=hole ways belong to another course of the club
        fc["features"] = [f for f in fc["features"] if (f.get("properties") or {}).get("golf") != "hole"]
    if supplement:
        # request "osm_supplement": hand-mapped golf=hole / green / tee features (GeoJSON, repo path) for a course
        # OSM barely maps (The Oaks MO: 0 greens); they enter the build exactly like OSM features, tagged src=hand
        sp = supplement if os.path.isabs(supplement) else os.path.join(pc.ROOT, supplement)
        extra = pc.read_json(sp)["features"]
        for f in extra:
            f.setdefault("properties", {})["src"] = "hand"
        fc["features"] += extra
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
    summ["osm_source"] = {k: src[k] for k in ("source", "reason", "mirror", "osm_base", "snapshot", "snapshot_date",
                                              "merged_features", "counts", "thin", "note", "mirrors_tried") if k in src}
    pc.write_json(os.path.join(raw, "osm.geojson"), fc, indent=None)
    pc.write_json(os.path.join(raw, "summary.json"), summ)
    return fc, summ


def fetch_scorecards(req, course, summ, raw):
    out = dict(fetched_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), tried=[], cards=[])
    rawdir = os.path.join(raw, "scorecard")
    lengths = {str(h["ref"]): h["length_yd"] for h in summ.get("holes", []) if h.get("length_yd")}
    n = len(lengths) or None
    for label, fn in (("golfify", lambda: scm.fetch_golfify(course["name"], course["state"], course.get("town"), rawdir,
                                                            course.get("center"))),
                      ("allsquare", lambda: scm.fetch_allsquare(course["name"], course["state"], course.get("town"), rawdir,
                                                                course.get("center"))),
                      ("club_site", lambda: scm.fetch_club_site(req.get("website") or course.get("website"), rawdir,
                                                                n, lengths)),
                      ("opengolfapi", lambda: scm.fetch_opengolfapi(course["name"], course["state"], course.get("center"),
                                                                    rawdir, course_id=req.get("opengolfapi_id")))):
        if label == "opengolfapi" and not req.get("opengolfapi", True):
            continue
        try:
            card, info = fn()
        except Exception as e:                                # noqa: BLE001
            card, info = None, f"{label} crashed: {e!r}"[:300]
            traceback.print_exc()
        if card and not scm.plausible(card, n, lengths) and not (label == "opengolfapi" and req.get("opengolfapi_id")):
            info, card = f"{label}: card at {info} rejected (hole count / lengths don't fit OSM)", None
        out["tried"].append(dict(source=label, ok=bool(card), info=info))
        if card:
            out["cards"].append(dict(source=label, url=info, card=card))
    # no consistent card yet: the course directories (BlueGolf, GolfPass, AllSquare), most reliable first
    if req.get("directories", True) and not any(scm.consistency(scm.normalise(c["card"]))["ok"] for c in out["cards"]):
        for label in scm.DIRECTORIES:
            try:
                card, info = scm.fetch_directory(label, course["name"], course["state"], course.get("town"), rawdir,
                                                 n, lengths)
            except Exception as e:                            # noqa: BLE001
                card, info = None, f"{label} crashed: {e!r}"[:300]
                traceback.print_exc()
            out["tried"].append(dict(source=label, ok=bool(card), info=info))
            if card:
                out["cards"].append(dict(source=label, url=info, card=card))
                if scm.consistency(scm.normalise(card))["ok"]:
                    break
    try:                                                      # advisory: cards settled on the OSM hole lines
        import card_consensus as ccs
        r = ccs.consensus([(c["source"], c["card"], c["url"]) for c in out["cards"]], ccs.ground_from_summary(summ))
        if r:
            out["consensus"] = {k: r[k] for k in ("base", "base_url", "changes", "flags", "scores")}
    except Exception as e:                                    # noqa: BLE001
        out["consensus"] = dict(error=repr(e)[:200])
    pc.write_json(os.path.join(raw, "scorecard_web.json"), out)
    return out


def fetch_scorecards_only(req_path):
    """Re-run only the web scorecard step for a request whose raw/ already exists (request "refetch":
    "scorecards"): keeps the fetched OSM so a rebuild changes nothing but the cards. -> (slug, status)."""
    req = pc.read_json(req_path)
    slug = request_slug(req, req_path)
    raw = os.path.join(pc.PACKAGES, slug, "raw")
    course = pc.read_json(os.path.join(raw, "course.json"))
    summ = pc.read_json(os.path.join(raw, "summary.json"), {}) or {}
    if not course or course.get("status") != "ok":
        return slug, "no resolved raw/course.json: run a full fetch"
    sw = fetch_scorecards(req, course, summ, raw)
    pc.log("scorecards:", json.dumps(sw["tried"]))
    return slug, "ok"


def fetch_imagery(course, pkg, year="auto"):
    """NAIP (+ DEM) for the package; year: "auto" = the best-scoring leaf-on NAIP year on the course's OSM turf
    (imagery/naip_years.py), "latest", or a year (request "naip_year")."""
    img = os.path.join(pkg, "imagery")
    w, s, e, n = course["bbox"]
    cmd = [sys.executable, os.path.join(pc.COURSE_DATA, "imagery", "fetch_imagery.py"),
           "--bbox", f"{s},{w},{n},{e}", "--name", course["name"], "--margin", "100", "--max-mb", "45",
           "--out", img, "--osm", os.path.join(pkg, "raw", "osm.geojson"), "--year", str(year or "auto")]
    pc.log("imagery:", " ".join(cmd))
    r = subprocess.run(cmd, timeout=2400)
    return r.returncode == 0


def geocode_address(address):
    """Request "address" (the club's street address, what a golfer can always find) -> "lat,lon" for resolve's
    `near` fallbacks (a course OSM maps unnamed or under another name: Kokopelli GC, Marion IL), or None."""
    hits = pc.nominatim("search", q=address, countrycodes="us", limit=1) or []
    if not hits:
        pc.log("address: no geocode for", address)
        return None
    near = f"{float(hits[0]['lat']):.6f},{float(hits[0]['lon']):.6f}"
    pc.log("address:", address, "->", near, hits[0].get("display_name", "")[:120])
    return near


def fetch(req_path):
    req = pc.read_json(req_path)
    slug = request_slug(req, req_path)
    pkg = os.path.join(pc.PACKAGES, slug)
    raw = os.path.join(pkg, "raw")
    os.makedirs(raw, exist_ok=True)
    if not req.get("near") and req.get("address"):
        req["near"] = geocode_address(req["address"])
    course = rs.resolve(req["course"], req["state"], req.get("town"), req.get("osm"), near=req.get("near"))
    if req.get("boundary_ll") or (req.get("near") and req.get("no_osm_course")) or \
            (course["status"] != "ok" and req.get("near") and req.get("no_osm_ok")):
        # the course is not in OSM (or OSM's outline holds two courses of one club): work from the request's own
        # location / hand outline (resolve.from_near); OSM golf features inside it are still used
        pc.log("resolve:", course["status"], "-> request location (near / boundary_ll)")
        course = rs.from_near(req["course"], req["state"], req.get("near") or "%f,%f" % tuple(
            reversed(req["boundary_ll"][0][:2])), float(req.get("near_radius_m", 1200)), req.get("boundary_ll"),
            req.get("town"))
    pc.write_json(os.path.join(raw, "course.json"), course)
    pc.log("resolve:", course["status"], course.get("name"), course.get("osm"),
           [(c["name"], c["town"], c["holes"]) for c in course["candidates"][:5]])
    if course["status"] == "closed":
        return slug, f"closed: {course.get('closed')} (the course has closed; nothing to build)"
    if course["status"] != "ok":
        return slug, course["status"]
    fc, summ = fetch_osm(course, raw, drop_holes=bool(req.get("ignore_osm_holes")), supplement=req.get("osm_supplement"))
    pc.log("osm:", len(fc["features"]), "features;", summ["golf_tag_counts_inside_course"])
    if req.get("web_scorecard", True):
        sw = fetch_scorecards(req, course, summ, raw)
        pc.log("scorecards:", json.dumps(sw["tried"]))
    import package as pk
    if req.get("imagery", True) and not pk.find_imagery(req, pkg, slug):
        ok = fetch_imagery(course, pkg, req.get("naip_year", "auto"))
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
