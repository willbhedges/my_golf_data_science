"""The shipped (frozen) native_auto model on truth courses OUTSIDE its training set: a true held-out test of the
classifier + course gate. AUTO vs GATED (the S4n product rule) vs GATED+TAP2 (<= 2 confirm taps, classifier p as
priors, answers simulated from the truth) vs ORACLE (the band on every truth "yes" side). Frames = the package's
own corridor frames of the truth tee set (these courses have no mapper folder).

  DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 python3 course_data/mapper/eval_native_auto_frozen.py \
      amana_colonies,tomahawk_hills,national_kc,hot_springs_arlington,wakonda course_data/mapper/eval_native_auto_frozen.json
Truth-bearing output: never shown to a mapper."""
import sys, os, json, time, shutil, tempfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [R + "/mapper", R + "/product"]; sys.path.append(R + "/platform")
import common as M, eval_mapper as EM, eval_native_confirm as ENC, native_auto as NA, native_confirm as NC
import eval_native_auto as ENA
E = EM.eb(); E.ONLY = {"auto", "truth"}
model = NA.load_model()
cache = {}
for p in (R + "/platform/error_budget_cache.json", R + "/platform/error_budget_v2_cache.json", ENC.CACHE):
    cache.update(M.rj(p, {}) or {})
tmp = tempfile.mkdtemp(); E.CACHE_JSON = os.path.join(tmp, "c.json")
want = set(sys.argv[1].split(",")); res = {}
cfgs = [dict(c, set=s) for s in ("v1", "v2") for c in E.SETS[s]() if c["slug"] in want]
for cfg in cfgs:
    s = cfg["slug"]; t0 = time.time()
    try:
        base, _ = EM.base_for(cfg)
        frames = M.make_frames(base, cfg["tees"])
        ans, areas, _ = ENC.truth_answers(E, cfg, base, frames, near=True)
        frames = {r: f for r, f in frames.items() if r in ans}
        rows = NA.side_features(s, base, frames)
        p = NA.predict(model, rows)
        usable = NA.course_usable(rows); share = NA.course_share(p, model["thr"])
        fires = usable and share >= NA.COURSE_GATE
        y = {(r, sd): int(areas[r][sd] >= ENC.MIN_YD2) for r in ans for sd in "LR"}
        sel = {(r, sd): (p.get(r, {}).get(sd, 0) >= model["thr"]) and fires for r in ans for sd in "LR"}
        side = dict(pos=sum(y.values()), tp=sum(y[k] and sel[k] for k in y), fp=sum(sel[k] and not y[k] for k in y))
        gated = NA.apply_sides(base, frames, NA.sides_from_p(p, model["thr"]), p) if fires else base
        oracle = NA.apply_sides(base, frames, {r: [x for x in "LR" if NC.sides_of(v)[x]] for r, v in ans.items()})
        pkgs = {"AUTO": base, "GATED": gated, "ORACLE": oracle}
        asked = []
        if usable:
            D = NC.EBDecider(cfg["tees"], n=4000, cache=cache)
            qs = NC.select(gated, frames, NA.confirm_priors(p), D, cap=99)
            asked = ENC.capped(qs, 2)
            pkgs["GATED+TAP2"] = NC.apply_answers(gated, {r: ans[r] for r in asked if r in ans}, frames)
        sc = ENA.score(E, cfg, pkgs, 4000, cache, tmp)
        res[s] = dict(tees=cfg["tees"], usable=usable, share=round(share, 3), fires=fires, side=side, answers=ans,
                      p=p, asked=asked, scores=sc, secs=round(time.time() - t0))
        print(s, "usable", usable, "share", round(share, 3), "fires", fires, side, "; ".join(f"{k} {v.get('match')}/{v.get('regret')}" for k, v in sc.items()), flush=True)
    except Exception as e:
        import traceback; traceback.print_exc(); res[s] = dict(error=str(e))
    json.dump(res, open(sys.argv[2], "w"), indent=1)
shutil.rmtree(tmp, ignore_errors=True)
