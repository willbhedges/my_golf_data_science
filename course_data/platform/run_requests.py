"""Workflow driver (.github/workflows/course_package.yml): process the request files a push touched.

  python course_data/platform/run_requests.py <changed paths...>

  course_data/requests/package_<slug>.json changed (or no raw/ yet) -> fetch (network) + build
  ... changed, raw/ exists and the request says "refetch": "scorecards" -> web scorecards only + build
  only platform code changed                                      -> offline rebuild of every fetched package
  course_data/requests/survey_*.json changed                      -> survey.py for its states
Writes a markdown summary (coverage per course) to $GITHUB_STEP_SUMMARY and packages/_index.json.
"""
import glob
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import platform_common as pc  # noqa: E402


# libraries the build imports: a change to one rebuilds every fetched package (offline)
DEPS = ["course_data/vision_any/gapfill.py", "course_data/geometry/build_holes.py", "course_data/tees/place_tee.py",
        "course_data/tees/lidar_pads.py", "course_data/pipeline.py", "course_data/elevation/adjust.py"]


def plan(changed, requests=None):
    """-> list of (request path, action) with action in fetch | build | survey | skip."""
    changed = {os.path.normpath(c) for c in changed}
    rel = lambda p: os.path.normpath(os.path.relpath(p, pc.ROOT))    # noqa: E731
    deps = [os.path.normpath(d) for d in DEPS]
    code = any(c.startswith(os.path.normpath("course_data/platform/")) and c.endswith(".py") and
               "/test_" not in c.replace(os.sep, "/") for c in changed) or \
        any(c.endswith("course_package.yml") or c in deps for c in changed)
    out = []
    if requests is None:
        requests = glob.glob(os.path.join(pc.REQUESTS, pc.REQUEST_PREFIX + "*.json")) + \
            glob.glob(os.path.join(pc.REQUESTS, "survey_*.json"))
    import fetch_package as fp
    for p in sorted(requests):
        r = rel(p)
        name = os.path.basename(p)
        if name.startswith("survey_"):
            out.append((p, "survey" if r in changed else "skip"))
            continue
        req = pc.read_json(p, {}) or {}
        slug = fp.request_slug(req, p)
        fetched = os.path.exists(os.path.join(pc.PACKAGES, slug, "raw", "osm.geojson"))
        if r in changed and fetched and str(req.get("refetch", "")).lower() == "scorecards":
            out.append((p, "scorecards"))
        elif r in changed or not fetched:
            out.append((p, "fetch"))
        elif code:
            out.append((p, "build"))
        else:
            out.append((p, "skip"))
    return out


def main(changed):
    import fetch_package as fp
    import package as pk
    import survey
    lines = ["| request | action | result | course | holes | greens | tee boxes | tree/grass holes | OSM landing share | mean conf | OSM score |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    index = pc.read_json(os.path.join(pc.PACKAGES, "_index.json"), {}) or {}
    bad = 0
    for p, action in plan(changed):
        name = os.path.basename(p)
        print(f"== {name}: {action}", flush=True)
        if action == "skip":
            continue
        try:
            req = pc.read_json(p)
            if action == "survey":
                for st in req.get("survey", []):
                    o = survey.survey(st)
                    lines.append(f"| {name} | survey {st} | {o['n_courses']} courses, {o['n_18_holes']} with 18 holes | "
                                 + " / ".join(f"{r['name']} ({r['score']})" for r in o["courses"][:5]) + " | | | | | | | |")
                continue
            if action in ("fetch", "scorecards"):
                slug, status = fp.fetch(p) if action == "fetch" else fp.fetch_scorecards_only(p)
                if status != "ok":
                    cj = pc.read_json(os.path.join(pc.PACKAGES, slug, "raw", "course.json"), {})
                    cands = "; ".join(f"{c['name']} ({c['town']}, {c['holes']} holes, {c['osm']['type']}/{c['osm']['id']})"
                                      for c in cj.get("candidates", [])[:6])
                    lines.append(f"| {name} | {action} | **{status}**: {cands or 'no candidates'} | | | | | | | | |")
                    index[slug] = dict(status=status, request=os.path.relpath(p, pc.ROOT))
                    bad += 1
                    continue
            package = pk.build_request(p, render=bool(req.get("render")))
            s = package["coverage"]["summary"]
            c = package["course"]
            lines.append(f"| {name} | {action} | ok | {c['name']} ({c.get('town')}, {c.get('state')}) | {s['holes_built']}/{s['holes_mapped']} | "
                         f"{s['greens_found']} | {s['tee_boxes']} | {s['holes_with_trees_or_long_grass_in_landing_zone']}/{s['of_par4_5']} | "
                         f"{s['mean_landing_osm_share']:.0%} | {s['mean_confidence']:.2f} | {s['osm_score']:.2f} |")
            index[package["slug"]] = dict(status="ok", name=c["name"], town=c.get("town"), state=c.get("state"),
                                          tee_set=package["tee_set"], built=package["built"],
                                          request=os.path.relpath(p, pc.ROOT), summary=s,
                                          package=f"course_data/packages/{package['slug']}/package.json")
        except BaseException as e:                              # noqa: BLE001 - keep going, report
            traceback.print_exc()
            lines.append(f"| {name} | {action} | **failed**: {type(e).__name__}: {str(e)[:200]} | | | | | | | | |")
            bad += 1
    pc.write_json(os.path.join(pc.PACKAGES, "_index.json"), index)
    md = "## Course packages\n\n" + "\n".join(lines) + "\n"
    print(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
            fh.write(md)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
