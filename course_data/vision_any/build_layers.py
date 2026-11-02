"""The product vision layer + OB evidence for a course package, in one place (network: GitHub Actions only).

    python course_data/vision_any/build_layers.py <slug> [<slug> ...] [--course-dir DIR] [--refresh] [--require]

Every build path that makes a package calls this between the first package build (OSM, card, NAIP, DEM: it gives
the course outline and bbox) and the rebuild that merges the layers, so they cannot drift:

  .github/workflows/course_page_one.yml   (library pages; via .github/actions/vision-layers)
  .github/workflows/course_package.yml    (package_*.json requests; course_data/platform/run_requests.py --vision)

Steps, each one recorded and none fatal by itself:
  1. raw/   3DEP lidar HAG + 2 NAIP years on the course grid (fetch_any.py), if raw/meta.json is missing
  2. raw2/  multi-year NAIP 1 m + lidar point statistics via PDAL (v2_fetch.py; $PDAL_BIN), if raw2/meta2.json is
            missing (raw2 is never committed: the library workflow keeps it in the Actions cache)
  3. v2     v2_model.py --infer <slug> --integrate yes: vision_any.geojson = vision_any/2 (trees = lidar canopy
            buffered -1 m, water; long grass off while model_v2/model.json has native_thr null)
  4. OB     course_data/ob/fetch.py <slug> (OSM buildings / roads / parcels; skips sources already fetched)

Then layer_status(slug) says whether the product layer is there. With --require the command exits 1 when a slug
has no vision_any/2 layer, so a missing tree layer is never silent.

`--refresh` re-runs the v2 inference even when a vision_any/2 layer exists (the library build does: the OSM
outline may have changed); without it a course that already has the product layer is left alone.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
PRODUCT_SCHEMA = "vision_any/2"


def log(*a):
    print(*a, flush=True)


def layer_path(slug):
    return os.path.join(HERE, slug, "vision_any.geojson")


def layer_status(slug):
    """-> (ok, text): ok iff course_data/vision_any/<slug>/vision_any.geojson is the product layer (vision_any/2)
    with at least one tree polygon."""
    p = layer_path(slug)
    if not os.path.exists(p):
        why = "raw (not fetched)" if not os.path.exists(os.path.join(HERE, slug, "raw", "meta.json")) else \
            "raw/ fetched but no v2 inference"
        return False, f"no {PRODUCT_SCHEMA} layer for '{slug}': {why}"
    try:
        fc = json.load(open(p))
    except Exception as e:                                       # noqa: BLE001
        return False, f"unreadable {os.path.relpath(p, ROOT)}: {type(e).__name__}: {e}"[:200]
    schema = (fc.get("properties") or {}).get("schema", "vision_any/1")
    if schema != PRODUCT_SCHEMA:
        return False, f"{os.path.relpath(p, ROOT)} is {schema}, not the product {PRODUCT_SCHEMA}"
    n = {}
    for f in fc.get("features") or []:
        lie = (f.get("properties") or {}).get("lie")
        n[lie] = n.get(lie, 0) + 1
    if not n.get("recovery"):
        return False, f"{PRODUCT_SCHEMA} layer for '{slug}' has no tree polygons ({n})"
    return True, f"{PRODUCT_SCHEMA}: " + ", ".join(f"{k} {v}" for k, v in sorted(n.items(), key=lambda kv: str(kv[0])))


def committed_paths(slug):
    """What a package run commits for the layers (small enough for the repo; raw2/ never)."""
    d = os.path.join("course_data", "vision_any", slug)
    return [os.path.join(d, "raw"), os.path.join(d, "vision_any.geojson"), os.path.join(d, "vision_any_v2.geojson"),
            os.path.join(d, "vision_any_v1.geojson"), os.path.join(d, "layers_v2.tif"),
            os.path.join(d, "classes_v2.jpg"), os.path.join("course_data", "ob", slug)]


def _run(cmd, timeout):
    log("  $", " ".join(cmd))
    try:
        r = subprocess.run(cmd, cwd=ROOT, timeout=timeout)
        return "ok" if r.returncode == 0 else f"failed (rc {r.returncode})"
    except subprocess.TimeoutExpired:
        return f"failed (timed out after {timeout // 60} min)"
    except Exception as e:                                       # noqa: BLE001
        return f"failed ({type(e).__name__}: {e})"[:200]


def ensure(slug, course_dir=None, refresh=False, ob=True, timeout=45 * 60, run=None):
    """Build whatever is missing of the product vision layer + OB evidence for <slug>.
    -> dict(ok, status, steps={raw, raw2, infer, ob}). `run(cmd, timeout)` is injectable for tests."""
    run = run or _run
    py = sys.executable or "python3"
    d = os.path.join(HERE, slug)
    cdir = course_dir or os.path.join(CD, "packages", slug, "raw")
    steps = {}
    ok0, _ = layer_status(slug)
    if ok0 and not refresh:
        steps["infer"] = "kept (vision_any/2 layer already built)"
    else:
        if os.path.exists(os.path.join(d, "raw", "meta.json")):
            steps["raw"] = "kept"
        else:
            steps["raw"] = run([py, "-u", os.path.join(HERE, "fetch_any.py"), "--course-dir", cdir, "--slug", slug],
                               timeout)
        if os.path.exists(os.path.join(d, "raw2", "meta2.json")):
            steps["raw2"] = "kept (cache)"
        elif not os.path.exists(os.path.join(d, "raw", "meta.json")):
            steps["raw2"] = "skipped: no raw/"
        else:
            if not os.environ.get("PDAL_BIN"):
                log("  ! PDAL_BIN not set: v2_fetch.py has no lidar point statistics")
            steps["raw2"] = run([py, "-u", os.path.join(HERE, "v2_fetch.py"), "--slug", slug], timeout)
        if os.path.exists(os.path.join(d, "raw", "meta.json")):
            steps["infer"] = run([py, "-u", os.path.join(HERE, "v2_model.py"), "--infer", slug, "--integrate", "yes"],
                                 timeout)
        else:
            steps["infer"] = "skipped: no raw/"
    if ob:
        if os.path.exists(os.path.join(CD, "packages", slug, "package.json")):
            steps["ob"] = run([py, "-u", os.path.join(CD, "ob", "fetch.py"), slug], timeout)
        else:
            steps["ob"] = "skipped: no package.json (OB fetch reads its bbox)"
        shutil.rmtree(os.path.join(CD, "ob", "_work"), ignore_errors=True)
    ok, status = layer_status(slug)
    log(f"[{slug}] vision layer: {'ok' if ok else 'MISSING'}: {status}; steps {steps}")
    return dict(ok=ok, status=status, steps=steps)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--course-dir", help="course raw dir for fetch_any (default course_data/packages/<slug>/raw)")
    ap.add_argument("--refresh", action="store_true", help="re-run the v2 inference even if the layer exists")
    ap.add_argument("--no-ob", action="store_true")
    ap.add_argument("--require", action="store_true", help="exit 1 if a slug ends without a vision_any/2 layer")
    a = ap.parse_args(argv)
    bad = []
    for s in a.slugs:
        r = ensure(s, course_dir=a.course_dir, refresh=a.refresh, ob=not a.no_ob)
        if not r["ok"]:
            bad.append(s)
            print(f"::error title=vision layer missing::{s}: {r['status']} (steps {r['steps']})", flush=True)
    return 1 if (bad and a.require) else 0


if __name__ == "__main__":
    sys.exit(main())
