"""Product pick agreement on the 5 truth courses (qa/scoreboard.py) for the previous package.py defaults vs the
any-course pipeline: each package is rebuilt offline from its committed raw/ + imagery/ into a scratch dir under
both settings, then scored exactly as the scoreboard does (scoreboard.score_course: product quick decision n=8000
vs the course's truth; hand-map truths put into that same package).

  python course_data/platform/picks_pipeline.py --out-dir /tmp/picks [--courses spirit_hollow,veenker] [--n 8000]
  -> course_data/platform/pipeline_picks.json

Variants
  previous   request "tee_localizer": "v1" (place_tee.place_course_sets), holes: OSM (all 5 map every hole)
  pipeline   the defaults now: tees/localize.py v2, stage selector (holes: OSM on all 5 -> unchanged)
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import package as P  # noqa: E402
import platform_common as pc  # noqa: E402

VARIANTS = {"previous": dict(tee_localizer="v1"), "pipeline": {}}


def build(slug, out_root, variant):
    src = os.path.join(CD, "packages", slug)
    dst = os.path.join(out_root, variant, slug)
    os.makedirs(dst, exist_ok=True)
    for d in ("raw", "imagery"):
        if os.path.exists(os.path.join(src, d)) and not os.path.exists(os.path.join(dst, d)):
            os.symlink(os.path.join(src, d), os.path.join(dst, d))
    req = pc.read_json(os.path.join(CD, "requests", f"package_{slug}.json")) or {}
    req = dict(req, **VARIANTS[variant])
    with contextlib.redirect_stdout(io.StringIO()):
        pkg = P.build_package(req, dst)
        P.write(pkg, dst)
    return os.path.join(dst, "package.json"), pkg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--courses")
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--build", nargs=2, metavar=("SLUG", "VARIANT"))
    a = ap.parse_args()
    if a.build:
        build(a.build[0], a.out_dir, a.build[1])
        return
    sys.path.insert(0, os.path.join(CD, "qa"))
    # product/package.py is also named "package": drop the platform one before the scoreboard imports it
    sys.modules.pop("package", None)
    sys.path.remove(HERE)
    import copy
    import scoreboard as SB
    import tee_strategy as TS
    SB.HAND_HOLES = copy.deepcopy(TS.HOLES)                # as scoreboard.main: Mozingo's hand map
    prev = json.load(open(SB.OUT_JSON)) if os.path.exists(SB.OUT_JSON) else {}
    sa = types.SimpleNamespace(n=a.n, workers=a.workers, from_out=False, holes=None, no_hand_quick=False,
                               dry_run=False, full=False, full_S=64, full_N=3000)
    want = set(a.courses.split(",")) if a.courses else None
    out = dict(schema="pipeline_picks/1", made_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), n=a.n,
               variants=VARIANTS, courses={})
    for cfg in SB.COURSES:
        if want and cfg["slug"] not in want:
            continue
        rec = {}
        for v in VARIANTS:
            # build in a child process: platform/package.py and product/package.py share the module name
            import subprocess
            subprocess.run([sys.executable, os.path.abspath(__file__), "--build", cfg["slug"], v, "--out-dir", a.out_dir],
                           check=True, stdout=subprocess.DEVNULL)
            path = os.path.join(a.out_dir, v, cfg["slug"], "package.json")
            pkg = json.load(open(path))
            c2 = dict(cfg, package=os.path.relpath(path, ROOT))
            r = SB.score_course(c2, sa, prev)
            s = r["summary"]
            rec[v] = dict(summary=s, tees=pkg["stages"].get("tees"), holes_method=(pkg.get("pipeline") or {}).get("holes"),
                          picks={h["hole"]: h.get("pick") for h in r["holes"]},
                          same={h["hole"]: h.get("same") for h in r["holes"]})
            print(cfg["slug"], v, {k: s.get(k) for k in ("same", "same_or_tie", "n_truth")}, flush=True)
        rec["changed"] = sorted(k for k in rec["pipeline"]["picks"] if rec["pipeline"]["picks"][k] != rec["previous"]["picks"].get(k))
        out["courses"][cfg["slug"]] = rec
        json.dump(out, open(os.path.join(HERE, "pipeline_picks.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
