"""error_budget.score_course on variant packages (configs auto / truth / +routing / +long_grass only).

  python3 course_data/platform/error_budget_variant.py <repo root> <variant dir | committed> <out.json> [slugs]
  variant dir: <dir>/<slug>/package.json (vision_any/v2_longgrass_eb_build.py); decisions cached in <out.json>.cache.json
  python3 course_data/platform/error_budget_variant_report.py <dir with eb_<variant>.json> control t0.04 ...
"""
import os, sys, json, shutil, importlib.util
os.environ.setdefault("OMP_NUM_THREADS", "1")
WT, VAR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
want = sys.argv[4].split(",") if len(sys.argv) > 4 else None
spec = importlib.util.spec_from_file_location("eb", os.path.join(WT, "course_data/platform/error_budget.py"))
EB = importlib.util.module_from_spec(spec); sys.modules["eb"] = EB; spec.loader.exec_module(EB)
EB.CACHE_JSON = OUT + ".cache.json"
if not os.path.exists(EB.CACHE_JSON):
    shutil.copy(os.path.join(WT, "course_data/platform/error_budget_cache.json"), EB.CACHE_JSON)
EB.configs = lambda: [("auto", "ref", set()), ("truth", "ref", set(EB.LAYERS)), ("+routing", "forward", {"routing"}),
                      ("+long_grass", "forward", {"long_grass"})]
cache = EB.rj(EB.CACHE_JSON, {})
res = EB.rj(OUT, {}) or {}
for cfg in EB.COURSES:
    if want and cfg["slug"] not in want:
        continue
    if VAR != "committed":
        p = os.path.join(VAR, cfg["slug"], "package.json")
        if not os.path.exists(p):
            print("skip (no variant)", cfg["slug"]); continue
        cfg = dict(cfg, package=p)
    print("==", cfg["slug"], flush=True)
    res[cfg["slug"]] = EB.score_course(cfg, 4000, 1, cache)
    json.dump(cache, open(EB.CACHE_JSON, "w"))
    json.dump(res, open(OUT, "w"), default=float)
    r = res[cfg["slug"]]["rows"]
    print(cfg["slug"], "auto match", sum(x["configs"]["auto"]["match"] for x in r), "/", len(r), flush=True)
