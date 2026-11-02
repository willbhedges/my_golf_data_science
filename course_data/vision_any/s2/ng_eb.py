"""error_budget.score_course (configs auto / truth) on variant packages, v1 + v2 sets.
python3 ng_eb.py <wt> <variant dir> <out.json> slug,..."""
import os, sys, json, shutil, importlib.util
os.environ.setdefault("OMP_NUM_THREADS", "1")
WT, VAR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; want = sys.argv[4].split(",")
spec = importlib.util.spec_from_file_location("eb", os.path.join(WT, "course_data/platform/error_budget.py"))
EB = importlib.util.module_from_spec(spec); sys.modules["eb"] = EB; spec.loader.exec_module(EB)
EB.CACHE_JSON = os.path.join(os.path.dirname(OUT), "shared.cache.json")
if not os.path.exists(EB.CACHE_JSON):
    shutil.copy(os.path.join(WT, "course_data/platform/error_budget_cache.json"), EB.CACHE_JSON)
EB.configs = lambda: [("auto", "ref", set()), ("truth", "ref", set(EB.LAYERS)), ("+routing", "forward", {"routing"})]
cfgs = {c["slug"]: c for s in ("v1", "v2") for c in EB.SETS[s]()}
cache = EB.rj(EB.CACHE_JSON, {}); res = EB.rj(OUT, {}) or {}
for s in want:
    cfg = cfgs[s]; p = os.path.join(VAR, s, "package.json")
    if not os.path.exists(p): print("skip", s); continue
    cfg = dict(cfg, package=p)
    res[s] = EB.score_course(cfg, 4000, 1, cache)
    json.dump(cache, open(EB.CACHE_JSON, "w")); json.dump(res, open(OUT, "w"), default=float)
    r = res[s]["rows"]
    print(s, "auto match", sum(x["configs"]["auto"]["match"] for x in r), "/", len(r),
          "regret %.3f" % sum(x["configs"]["auto"]["regret"] or 0 for x in r), flush=True)
