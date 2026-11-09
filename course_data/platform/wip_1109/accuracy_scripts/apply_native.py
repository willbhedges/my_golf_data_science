"""S4n on rebuilt auto packages, held out.
python3 apply_native.py WT IN_DIR OUT_DIR v1|v2
Courses in mapper/eval_native_auto.json: leave-one-course-out p + nested threshold + course gate (as the eval's
GATED variant; the shipped model saw these courses). Others: native_auto.build_layer with the shipped model (it
never saw them). The package is reframed as package.call_native_auto does."""
import importlib.util, json, os, shutil, sys
WT, IN, OUT, SV = sys.argv[1:5]
CD = os.path.join(WT, "course_data")
sys.path.insert(0, os.path.join(CD, "mapper"))
sys.path.insert(0, os.path.join(CD, "product"))
sys.path.insert(0, os.path.join(CD, "platform"))
import common as M
import native_auto as NA
import error_budget as E
spec = importlib.util.spec_from_file_location("bud_platform_package", os.path.join(CD, "platform", "package.py"))
PP = importlib.util.module_from_spec(spec); sys.modules["bud_platform_package"] = PP; spec.loader.exec_module(PP)
EV = json.load(open(os.path.join(CD, "mapper", "eval_native_auto.json")))["courses"]
log = {}
for cfg in E.SETS[SV]():
    slug = cfg["slug"]
    src = os.path.join(IN, slug, "package.json")
    if not os.path.exists(src):
        continue
    pkg = M.rj(src)
    os.makedirs(os.path.join(OUT, slug), exist_ok=True)
    dst = os.path.join(OUT, slug, "package.json")
    if slug in EV:
        e = EV[slug]
        if e["fires"]:
            frames = M.make_frames(pkg, M.tee_set_of(pkg, cfg["tees"]) if any(k.lower() == cfg["tees"].lower() for k in pkg.get("tee_sets") or {}) else M.tee_set_of(pkg))
            sides = NA.sides_from_p(e["p"], e["thr"])
            out = PP.reframe(NA.apply_sides(pkg, frames, sides, e["p"]))
            log[slug] = dict(how="loco", thr=e["thr"], share=e["share"], sides={r: v for r, v in sides.items() if v})
        else:
            out = pkg
            log[slug] = dict(how="loco", thr=e["thr"], share=e["share"], sides={}, why="gate shut")
    else:
        try:
            out, info = NA.build_layer(slug, pkg)
            if info.get("why") == "added":
                out = PP.reframe(out)
            log[slug] = dict(how="shipped model (unseen course)", why=info.get("why"), share=info.get("share"),
                             sides=info.get("sides") or {})
        except Exception as ex:  # noqa
            out = pkg
            log[slug] = dict(how="shipped", why=f"error {ex}")
    json.dump(out, open(dst, "w"))
    print(slug, json.dumps(log[slug])[:300], flush=True)
json.dump(log, open(os.path.join(OUT, "native_log.json"), "w"), indent=1)
