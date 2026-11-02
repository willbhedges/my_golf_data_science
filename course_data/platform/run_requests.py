"""Workflow driver (.github/workflows/course_package.yml): process the request files a push touched.

  python course_data/platform/run_requests.py <changed paths...>

  course_data/requests/package_<slug>.json changed (or no raw/ yet) -> fetch (network) + build
  ... changed, raw/ exists and the request says "refetch": "scorecards" -> web scorecards only + build
  only platform code changed                                      -> offline rebuild of every fetched package
  course_data/requests/survey_*.json changed                      -> survey.py for its states

  --vision (the workflow passes it): a fetched course without the product vision layer (vision_any/2 trees +
  water, course_data/vision_any/<slug>/vision_any.geojson) gets it built - vision_any/build_layers.py, the same
  step course_page_one.yml runs - between the first build and a rebuild, so no fetch path packages a course
  without trees. Every built package whose vision stage is not "ok: vision_any/2" is listed in
  $VISION_GATE (default /tmp/vision_gate.txt): "error" lines for fetched courses (the workflow fails the run),
  "warning" lines for offline rebuilds.
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
        "course_data/tees/lidar_pads.py", "course_data/pipeline.py", "course_data/elevation/adjust.py",
        "course_data/ob/infer.py", "course_data/ob/params.json"]


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
        if req.get("builder") and req["builder"] != "course-package":
            # built by its own workflow (e.g. "nccga-package"): a run here would race it and, committing later
            # with an older request, overwrite the newer package
            out.append((p, "skip"))
            continue
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


def vision_ok(package):
    """The package's vision stage is the product layer (vision_any/2) with zones."""
    return str((package.get("stages") or {}).get("vision", "")).startswith("ok: vision_any/2")


def build_layers_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cdp_build_layers", os.path.join(pc.ROOT, "course_data", "vision_any",
                                                                                   "build_layers.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def with_vision(p, package, build, ensure=None):
    """A fetched package without the product vision layer: build the layer (+ OB evidence), then rebuild.
    -> (package, note). `build(p)` rebuilds; `ensure(slug)` is build_layers.ensure (injectable for tests)."""
    if vision_ok(package):
        return package, "ok"
    slug = package["slug"]
    ensure = ensure or build_layers_module().ensure
    print(f"== {slug}: vision stage '{(package.get('stages') or {}).get('vision', '')[:100]}': building the layer",
          flush=True)
    r = ensure(slug)
    if not r.get("ok"):
        return package, f"layer not built: {r.get('status')} (steps {r.get('steps')})"
    return build(p), "built this run"


def main(changed, vision=False):
    import fetch_package as fp
    import package as pk
    import survey
    lines = ["| request | action | result | course | holes | greens | tee boxes | tree/grass holes | OSM landing share | mean conf | OSM score | vision |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    gate = []
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
                    lines.append(f"| {name} | {action} | **{status}**: {cands or 'no candidates'} | | | | | | | | | |")
                    index[slug] = dict(status=status, request=os.path.relpath(p, pc.ROOT))
                    bad += 1
                    continue
            package = pk.build_request(p, render=bool(req.get("render")))
            vnote = ""
            if vision and action in ("fetch", "scorecards"):
                package, vnote = with_vision(p, package, lambda q: pk.build_request(q, render=bool(req.get("render"))))
            vst = str((package.get("stages") or {}).get("vision", ""))
            if not vision_ok(package):
                level = "error" if action in ("fetch", "scorecards") else "warning"
                gate.append(f"{level}\t{package['slug']}\t{vst[:200]}" + (f" [{vnote}]" if vnote else ""))
            s = package["coverage"]["summary"]
            c = package["course"]
            lines.append(f"| {name} | {action} | ok | {c['name']} ({c.get('town')}, {c.get('state')}) | {s['holes_built']}/{s['holes_mapped']} | "
                         f"{s['greens_found']} | {s['tee_boxes']} | {s['holes_with_trees_or_long_grass_in_landing_zone']}/{s['of_par4_5']} | "
                         f"{s['mean_landing_osm_share']:.0%} | {s['mean_confidence']:.2f} | {s['osm_score']:.2f} | "
                         f"{'ok' if vision_ok(package) else '**CHECK**'}: {vst[:70]} |")
            index[package["slug"]] = dict(status="ok", name=c["name"], town=c.get("town"), state=c.get("state"),
                                          tee_set=package["tee_set"], built=package["built"],
                                          request=os.path.relpath(p, pc.ROOT), summary=s, vision=vst[:160],
                                          package=f"course_data/packages/{package['slug']}/package.json")
        except BaseException as e:                              # noqa: BLE001 - keep going, report
            traceback.print_exc()
            lines.append(f"| {name} | {action} | **failed**: {type(e).__name__}: {str(e)[:200]} | | | | | | | | | |")
            bad += 1
    pc.write_json(os.path.join(pc.PACKAGES, "_index.json"), index)
    with open(os.environ.get("VISION_GATE") or "/tmp/vision_gate.txt", "w") as fh:
        fh.write("".join(g + "\n" for g in gate))
    md = "## Course packages\n\n" + "\n".join(lines) + "\n"
    if gate:
        md += ("\n**Vision layer CHECK** (no vision_any/2 trees: trees / water come from OSM only):\n\n"
               + "\n".join("* " + g.replace("\t", " ") for g in gate) + "\n")
    print(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
            fh.write(md)
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    v = "--vision" in args
    sys.exit(1 if main([a for a in args if a != "--vision"], vision=v) else 0)
