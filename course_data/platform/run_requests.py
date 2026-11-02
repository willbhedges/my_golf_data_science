"""Workflow driver (.github/workflows/course_package.yml): process the request files a push touched.

  python course_data/platform/run_requests.py [--vision] [--phase all|requests|rebuild] [--only <request>]...
         [--shard K/N] [--commit-every N] [--plan-json out.json] <changed paths...>

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

Phases (the workflow runs them as separate jobs so new requests never wait behind the offline rebuild):
  --phase requests   only fetch / scorecards / survey actions (--only <request path> narrows it to one request:
                     the workflow builds each new request in its own matrix job and commits it on its own)
  --phase rebuild    the offline rebuild: every fetched package whose BUILD HASH is stale, whatever the push
                     touched (requests in <changed> are left to the requests phase). --shard K/N keeps the
                     packages with crc32(slug) % N == K, so shards are stable whatever else is stale.
  --phase all        the old single-step behaviour (default)
  --plan-json out    write {"requests": [request paths the requests phase would build], "rebuild": n stale} and exit
  --commit-every N   with $COMMIT_CMD set: after every N built packages write _index.json and run
                     `$COMMIT_CMD <slug>...` (course_data/platform/commit_run.sh), so a job cap keeps the work done

Build hash (packages/<slug>/build_inputs.json, written after every successful build): sha256 over the request
file and the code the build ran - every non-test course_data/platform/*.py, DEPS + DATA, and every course_data
module the build process imported (recorded as "files"). A package is stale when that hash no longer matches
(any of those files changed, a new platform module appeared) or it has no build_inputs.json. Data-only
changes elsewhere (a re-committed vision layer, OB evidence) do not make a package stale - as before, when only
a code change ever triggered an offline rebuild.
"""
import glob
import hashlib
import json
import os
import shlex
import subprocess
import sys
import traceback
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import platform_common as pc  # noqa: E402


# libraries the build imports: a change to one rebuilds every fetched package (offline)
DEPS = ["course_data/vision_any/gapfill.py", "course_data/geometry/build_holes.py", "course_data/tees/place_tee.py",
        "course_data/tees/lidar_pads.py", "course_data/pipeline.py", "course_data/elevation/adjust.py",
        "course_data/ob/infer.py", "course_data/ob/params.json"]
# data the build reads that is not a module (part of the build hash)
DATA = ["course_data/platform/routing_v2_weights.json"]
BUILD_INPUTS = "build_inputs.json"


def _rel(p):
    return os.path.relpath(os.path.abspath(p), pc.ROOT).replace(os.sep, "/")


def base_code_files():
    """Code every build depends on: non-test course_data/platform/*.py + DEPS + DATA (repo-relative)."""
    plat = [_rel(f) for f in glob.glob(os.path.join(pc.ROOT, "course_data", "platform", "*.py"))
            if not os.path.basename(f).startswith("test_")]
    return sorted(set(plat) | set(DEPS) | set(DATA))


def loaded_code_files():
    """course_data modules this process has imported (path-loaded team modules included), repo-relative."""
    cd = os.path.join(os.path.abspath(pc.ROOT), "course_data") + os.sep
    out = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f or not f.endswith(".py"):
            continue
        f = os.path.abspath(f)
        if f.startswith(cd) and not os.path.basename(f).startswith(("test_", "conftest")):
            out.add(_rel(f))
    return sorted(out)


def build_hash(request_path, files):
    h = hashlib.sha256()
    h.update(b"request\0")
    try:
        h.update(open(request_path, "rb").read())
    except OSError:
        h.update(b"missing")
    for f in sorted(set(files)):
        h.update(b"\0" + f.encode() + b"\0")
        try:
            h.update(open(os.path.join(pc.ROOT, f), "rb").read())
        except OSError:
            h.update(b"missing")
    return h.hexdigest()


def inputs_path(slug):
    return os.path.join(pc.PACKAGES, slug, BUILD_INPUTS)


def record_build(slug, request_path, files=None):
    files = sorted(set(base_code_files()) | set(loaded_code_files() if files is None else files))
    rec = dict(schema="build_inputs/1", hash=build_hash(request_path, files), request=_rel(request_path), files=files)
    pc.write_json(inputs_path(slug), rec)
    return rec


def is_stale(slug, request_path):
    """The package was built from other code / another request than what is on disk now (or has no record)."""
    rec = pc.read_json(inputs_path(slug), None)
    if not isinstance(rec, dict) or not rec.get("hash"):
        return True
    files = set(base_code_files()) | set(rec.get("files") or [])
    return build_hash(request_path, files) != rec["hash"]


def shard_of(slug, n):
    return zlib.crc32(slug.encode()) % n


def plan(changed, requests=None, phase="all", shard=None):
    """-> list of (request path, action) with action in fetch | scorecards | build | survey | skip.
    phase "requests": only fetch / scorecards / survey; "rebuild": build for every fetched package whose build
    hash is stale (requests in `changed` are the requests phase's), shard (k, n) keeps crc32(slug) % n == k."""
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
            out.append((p, "survey" if r in changed and phase != "rebuild" else "skip"))
            continue
        req = pc.read_json(p, {}) or {}
        if req.get("builder") and req["builder"] != "course-package":
            # built by its own workflow (e.g. "nccga-package"): a run here would race it and, committing later
            # with an older request, overwrite the newer package
            out.append((p, "skip"))
            continue
        slug = fp.request_slug(req, p)
        fetched = os.path.exists(os.path.join(pc.PACKAGES, slug, "raw", "osm.geojson"))
        if phase == "rebuild":
            ok = fetched and r not in changed and (shard is None or shard_of(slug, shard[1]) == shard[0])
            out.append((p, "build" if ok and is_stale(slug, p) else "skip"))
            continue
        if r in changed and fetched and str(req.get("refetch", "")).lower() == "scorecards":
            out.append((p, "scorecards"))
        elif r in changed or not fetched:
            out.append((p, "fetch"))
        elif code and phase == "all":
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


def commit_chunk(slugs, index):
    """Publish the packages built so far ($COMMIT_CMD <slug>...); a failure is reported, not fatal."""
    cmd = os.environ.get("COMMIT_CMD")
    if not cmd or not slugs:
        return
    pc.write_json(os.path.join(pc.PACKAGES, "_index.json"), index)
    print(f"== commit {len(slugs)} package(s): {' '.join(slugs)}", flush=True)
    r = subprocess.run(shlex.split(cmd) + list(slugs), cwd=pc.ROOT)
    if r.returncode:
        print(f"! commit command exited {r.returncode}; the packages stay for the next commit", flush=True)


def main(changed, vision=False, phase="all", only=None, shard=None, commit_every=0):
    import fetch_package as fp
    import package as pk
    import survey
    lines = ["| request | action | result | course | holes | greens | tee boxes | tree/grass holes | OSM landing share | mean conf | OSM score | vision |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    gate = []
    index = pc.read_json(os.path.join(pc.PACKAGES, "_index.json"), {}) or {}
    bad = 0
    pending = []
    steps = plan(changed, phase=phase, shard=shard)
    if only:
        keep = {os.path.normpath(o if os.path.isabs(o) else os.path.join(pc.ROOT, o)) for o in only}
        steps = [(p, a) for p, a in steps if os.path.normpath(os.path.abspath(p)) in keep]
    for p, action in steps:
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
            try:
                record_build(package["slug"], p)
            except Exception as e:                              # noqa: BLE001 - only costs a rebuild next time
                print(f"! build hash not recorded for {package['slug']}: {e}", flush=True)
            pending.append(package["slug"])
            if commit_every and len(pending) >= commit_every:
                commit_chunk(pending, index)
                pending = []
        except BaseException as e:                              # noqa: BLE001 - keep going, report
            traceback.print_exc()
            lines.append(f"| {name} | {action} | **failed**: {type(e).__name__}: {str(e)[:200]} | | | | | | | | | |")
            bad += 1
    if commit_every:
        commit_chunk(pending, index)
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


def write_plan(changed, out):
    """The plan job: which requests get their own build job, how many packages the rebuild has to do."""
    reqs = [_rel(p) for p, a in plan(changed, phase="requests") if a != "skip"]
    stale = sum(a == "build" for _, a in plan(changed, phase="rebuild"))
    obj = dict(requests=reqs, rebuild=stale)
    pc.write_json(out, obj)
    print(json.dumps(obj))
    return obj


def parse_args(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--vision", action="store_true")
    ap.add_argument("--phase", choices=("all", "requests", "rebuild"), default="all")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--shard", default=None, help="K/N")
    ap.add_argument("--commit-every", type=int, default=0)
    ap.add_argument("--plan-json", default=None)
    ap.add_argument("changed", nargs="*")
    a = ap.parse_args(argv)
    if a.shard:
        k, n = (int(x) for x in a.shard.split("/"))
        if not 0 <= k < n:
            ap.error(f"bad --shard {a.shard}")
        a.shard = (k, n)
    return a


if __name__ == "__main__":
    a = parse_args(sys.argv[1:])
    if a.plan_json:
        write_plan(a.changed, a.plan_json)
        sys.exit(0)
    sys.exit(1 if main(a.changed, vision=a.vision, phase=a.phase, only=a.only, shard=a.shard,
                       commit_every=a.commit_every) else 0)
