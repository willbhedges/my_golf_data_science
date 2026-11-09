"""Rebuild the truth courses' packages with the CURRENT pipeline code from their committed raw data (no network), for
the regression check after a fix that touches shared code:

  python3 rebuild_truth.py [--courses a,b] [--workers 4]  -> cache/variants/rebuilt/<slug>/package.json
  python3 evalfast.py --tag rebuilt --auto-dir cache/variants/rebuilt
The shipped native band (S4n) is stripped as in the held-out baseline (it was trained on these courses).
"""
import argparse
import contextlib
import io
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
ROOT = os.path.dirname(CD)
CACHE = os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache")
sys.path[:0] = [HERE, PLAT]


def one(slug):
    import platform_common as pc
    import package as pk
    t0 = time.time()
    d = os.path.join(pc.PACKAGES, slug)
    old = pc.read_json(os.path.join(d, "package.json")) or {}
    req = old.get("request") or pc.read_json(os.path.join(CD, "requests", f"package_{slug}.json"))
    if not req or not os.path.exists(os.path.join(d, "raw", "osm.geojson")):
        return slug, "skipped: no request / raw", 0
    req = dict(req, native_auto=False)
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            p = pk.build_package(req, d)
            for h in p["holes"].values():
                h["zones_ll"] = [z for z in (h.get("zones_ll") or []) if not str(z.get("src", "")).startswith("auto:native_side")]
            p = pk.reframe(p)
    except BaseException as e:                                       # noqa: BLE001
        return slug, f"failed: {type(e).__name__}: {str(e)[:150]}", round(time.time() - t0, 1)
    out = os.path.join(CACHE, "variants", "rebuilt", slug)
    os.makedirs(out, exist_ok=True)
    json.dump(p, open(os.path.join(out, "package.json"), "w"))
    return slug, f"ok {len(p['holes'])} holes, set {p.get('tee_set')}", round(time.time() - t0, 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--courses")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    import variants
    slugs = [c["slug"] for c in variants.truth_courses() if not a.courses or c["slug"] in a.courses.split(",")]
    t0 = time.time()
    with mp.get_context("fork").Pool(a.workers) as pool:
        for s, st, dt in pool.imap_unordered(one, slugs):
            print(s, st, dt, flush=True)
    print("rebuilt in", round(time.time() - t0, 1), "s")
