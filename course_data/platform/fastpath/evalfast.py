"""Fast held-out accuracy check: error_budget.score_course (auto vs truth only) on the truth courses, decisions cached
by hole fingerprint, holes in parallel. A re-score after an algorithm change only re-decides the holes that changed.

  python3 evalfast.py [--auto-dir cache/variants/NAME] [--tag NAME] [--n 4000] [--courses a,b] [--workers 4]
  -> cache/eval/<tag>.json + one line: match / shots, regret, regret per 14-shot round, wall seconds
"""
import argparse
import json
import os
import shutil
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CACHE = os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache")
sys.path.insert(0, PLAT)
import error_budget as EB  # noqa: E402

NOT_COUNTED = ("national_kc",)          # no card: not counted in the error budget headline either


def run(auto_dir=None, tag="full", n=4000, courses=None, workers=4, log=print, exact=False):
    t0 = time.time()
    os.makedirs(os.path.join(CACHE, "eval"), exist_ok=True)
    EB.CACHE_JSON = os.path.join(CACHE, "eval", f"decisions_{'exact' if exact else 'raster'}_{n}.json")
    if not exact:                      # the lie raster (solve.raster_lie_at): ~4x faster, EVs within 0.001 strokes
        sys.path.insert(0, HERE)
        import solve as SV
        EB.use_fast_lie_at = SV.use_raster
        SV.use_raster()                # truth_ev (regret) runs in this process
    cache = EB.rj(EB.CACHE_JSON, {}) or {}
    EB.configs = lambda: [("auto", "ref", set()), ("truth", "ref", set(EB.LAYERS)), ("+routing", "forward", set())]      # = auto (score_course needs the key; no extra decisions)
    res = []
    for cfg in EB.COURSES + EB.courses_v2():
        if courses and cfg["slug"] not in courses or cfg["slug"] in NOT_COUNTED:
            continue
        if auto_dir:
            p = os.path.join(auto_dir, cfg["slug"], "package.json")
            if not os.path.exists(p):
                continue
            cfg = dict(cfg, package=p)
        try:
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                r = EB.score_course(cfg, n, workers, cache)
        except Exception as e:                                       # noqa: BLE001
            log(f"  {cfg['slug']}: {type(e).__name__}: {e}")
            continue
        res.append(r)
    json.dump(cache, open(EB.CACHE_JSON, "w"))
    rows = [(c["slug"], r) for c in res if "rows" in c for r in c["rows"]]
    shots = len(rows)
    match = sum(bool(r["configs"]["auto"]["match"]) for _, r in rows)
    reg = sum(r["configs"]["auto"]["regret"] or 0 for _, r in rows)
    big = sum(1 for _, r in rows if not r["configs"]["auto"]["match"] and (r["configs"]["auto"]["regret"] or 0) > 0.02)
    out = dict(tag=tag, n=n, courses=len(res), shots=shots, match=match, match_pct=round(100 * match / max(shots, 1), 1),
               regret=round(reg, 3), regret_round=round(14 * reg / max(shots, 1), 3), misses_over_0_02=big,
               wall_s=round(time.time() - t0, 1),
               per_course={c["slug"]: [sum(bool(r["configs"]["auto"]["match"]) for r in c["rows"]), len(c["rows"]),
                                       round(sum(r["configs"]["auto"]["regret"] or 0 for r in c["rows"]), 3)] for c in res if "rows" in c},
               picks={f"{s}:{r['hole']}": [r["configs"]["auto"]["pick"], r["configs"]["auto"]["aim"], r["truth"]["pick"], r["truth"]["aim"],
                                           r["configs"]["auto"]["regret"]] for s, r in rows})
    json.dump(out, open(os.path.join(CACHE, "eval", f"{tag}_{n}{'_exact' if exact else ''}.json"), "w"), indent=1)
    log(f"{tag} n={n}: {match}/{shots} match ({out['match_pct']} %), regret {out['regret']} = {out['regret_round']} / round, "
        f"{big} misses > 0.02, {len(res)} courses, {out['wall_s']} s")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-dir")
    ap.add_argument("--tag", default="full")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--courses")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--exact", action="store_true", help="polygon lie tests (the slow cross-check)")
    a = ap.parse_args()
    run(a.auto_dir, a.tag, a.n, a.courses.split(",") if a.courses else None, a.workers, exact=a.exact)
