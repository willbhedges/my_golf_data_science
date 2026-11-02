"""platform/error_budget_variant.py with the truth_sets_v2 courses (Annbriar, Amana Colonies) added as holes_truth courses.
python3 s2_eb.py <wt> <variant dir | committed> <out.json> slug,..."""
import os, sys, json, shutil, importlib.util
os.environ.setdefault("OMP_NUM_THREADS", "1")
WT, VAR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
want = sys.argv[4].split(",")
spec = importlib.util.spec_from_file_location("eb", os.path.join(WT, "course_data/platform/error_budget.py"))
EB = importlib.util.module_from_spec(spec); sys.modules["eb"] = EB; spec.loader.exec_module(EB)
EB.CACHE_JSON = OUT + ".cache.json"
if not os.path.exists(EB.CACHE_JSON):
    shutil.copy(os.path.join(WT, "course_data/platform/error_budget_cache.json"), EB.CACHE_JSON)
EB.configs = lambda: [("auto", "ref", set()), ("truth", "ref", set(EB.LAYERS)), ("+routing", "forward", {"routing"}), ("+long_grass", "forward", {"long_grass"})]
TS2 = json.load(open(os.path.join(WT, "course_data/truth_sets_v2/index.json")))["courses"]
for s in ("annbriar", "amana_colonies"):
    EB.COURSES.append(dict(slug=s, tees=TS2[s]["corridor_set"], kind="tsv2"))
_orig = EB.truth_holes


def truth_holes(cfg):
    if cfg["kind"] != "tsv2":
        return _orig(cfg)
    rj0 = EB.rj; s = cfg["slug"]
    EB.rj = lambda p, d=None: rj0(p.replace(f"/truth/{s}/", f"/truth_sets_v2/{s}/"), d)
    try:
        return _orig(dict(cfg, kind="holes_truth"))
    finally:
        EB.rj = rj0


EB.truth_holes = truth_holes
cache = EB.rj(EB.CACHE_JSON, {})
res = EB.rj(OUT, {}) or {}
for cfg in EB.COURSES:
    if cfg["slug"] not in want:
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
    print(cfg["slug"], "auto match", sum(x["configs"]["auto"]["match"] for x in r), "/", len(r),
          "regret %.3f" % sum(x["configs"]["auto"]["regret"] or 0 for x in r), flush=True)
