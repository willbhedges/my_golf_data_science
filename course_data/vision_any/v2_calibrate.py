"""Decision-level calibration of the vision_any v2 long-grass / tree layers (and the OB offset) on the hand maps.

The map metrics (IoU, edges) do not say which way a layer moves the club: v2 long grass in the Driver landing zone
turned Driver into 4-wood / 2-wood on most scoreboard misses. Here every candidate setting is scored the way the
product is scored (course_data/qa/scoreboard.py): the committed package with ONLY its vision zones (trees, long
grass, vision water) replaced by the setting's layer, OB re-inferred (ob/infer.apply_ob, optional out_off), then
product/decide.run quick (n = 8000) per tee shot vs the truth (Spirit Hollow final_decision.json, Mozingo hand map
through the quick decision).

Stages (Actions, .github/workflows/vision_any_v2_calib.yml; request course_data/requests/vision_v2_calib.json):
  layers  python v2_calibrate.py layers --out DIR
          p(native) per course from (a) the model trained on the OTHER course only (leave-one-course-out, used
          for selection) and (b) the product model (both hand maps); one geojson per setting in DIR/<psrc>/<slug>/
  score   python v2_calibrate.py score --dir DIR --shard i --nshards n --out rows_i.json
  report  python v2_calibrate.py report --rows 'rows_*.json' [--integrate gate]
          selection: leave-one-COURSE-out (settings chosen on one course, scored on the other) and leave-one-
          HOLE-out (settings chosen on every other tee shot of both courses); bias = misses toward a shorter vs
          a longer club; the merge gate (decision level, vs the committed packages scored in the same harness).

Held-out truth courses (hand-checked corridor maps, course_data/truth/<slug>/hand_zones_ll.json; never used to
train or select anything here). Workflow vision_any_v2_holdout.yml; request course_data/requests/vision_v2_holdout.json:
  layers   python v2_calibrate.py layers --holdout --out DIR     (product model only: trained on SH + Mozingo, so it
           is out of sample on every held-out course)
  score    python v2_calibrate.py score --holdout --dir DIR --shard i --nshards n --out rows_i.json
  report   python v2_calibrate.py holdout-report --rows 'rows_*.json'  -> v2_holdout_calibration.{md,json}
           (does not touch v2_decision_calibration.* and never integrates)

Settings: native threshold (incl. off), native eligibility (strict: never on canopy / relaxed), tree buffer k m,
native minimum distance from OSM fairway (the Driver landing zone is mostly mown rough on the hand maps),
OB out_off (yds, ob/params.json; None = the calibrated value).
"""
import argparse
import copy
import glob
import itertools
import json
import os
import sys
import tempfile
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CD = os.path.join(ROOT, "course_data")
sys.path.insert(0, HERE)
import layers as L                                           # noqa: E402

YD = 0.9144
EVAL = {"spirit_hollow": "spirit_hollow", "mozingo": "mozingo_lake"}          # vision slug -> scoreboard slug
HOLDOUT = {"veenker": "veenker", "coldwater": "coldwater", "ellis": "ellis"}  # held-out truth courses
ADOPTED = "throff_strict_k3_d0"           # the integrated product setting (no long grass, trees = canopy + 3 m)
PREV_PICK = "thr0.5_relaxed_k0_d0"        # the in-sample product-map pick it replaced


def holdouts(need_raw2=False):
    """{vision slug: scoreboard slug} of the held-out courses with a hand map (and raw2, for layers)."""
    out = {}
    for v, p in HOLDOUT.items():
        if not os.path.exists(os.path.join(CD, "truth", p, "hand_zones_ll.json")):
            continue
        if need_raw2 and not os.path.exists(os.path.join(HERE, v, "raw2", "meta2.json")):
            log(f"  holdout {v}: no raw2 (skipped)")
            continue
        out[v] = p
    return out
CLUB_ORDER = ["Driver", "2-wood", "3-wood", "4-wood", "5-wood", "Hybrid", "Long iron", "Mid iron", "Short iron"]

GRID = dict(thr=[None, 0.04, 0.15, 0.3, 0.5], mode=["strict", "relaxed"], k=[0, 3, 5], dmin=[0, 20])
OB_OFF = [0, 10, 25]            # ob/params.json out_off alternatives (calibrated: -8), with the committed vision layer


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sid(s):
    return "thr{}_{}_k{}_d{}".format("off" if s["thr"] is None else s["thr"], s["mode"], s["k"], s["dmin"])


def settings():
    out = []
    for thr, mode, k, dmin in itertools.product(GRID["thr"], GRID["mode"], GRID["k"], GRID["dmin"]):
        if thr is None and (mode != "strict" or dmin):
            continue                        # native off: eligibility / distance irrelevant
        out.append(dict(thr=thr, mode=mode, k=k, dmin=dmin))
    return out


# =========================================================================== layers
def layer_fc(D, p, s, water_feats, tb):
    """One setting -> vision FeatureCollection (same schema as vision_any.geojson v2)."""
    S, M = D["S"], D["M"]
    trees = L.remove_small(D["canopy"][tb["hag"]], tb["min_area_m2"] / S.res ** 2)
    if s["k"] > 0:
        trees = ndimage.distance_transform_edt(~trees) * S.res <= s["k"]
    import v2_model as VM
    if s["thr"] is None:
        nat = np.zeros_like(trees)
    else:
        E = D["elig_rel"] if s["mode"] == "relaxed" else D["elig"]
        el = E & D["course"] & ~D["water0"]
        if s["mode"] != "relaxed":
            el &= ~trees
        if s["dmin"]:
            el &= ndimage.distance_transform_edt(~M["fairway"]) * S.res >= s["dmin"] * YD
        nat = VM.native_mask(p, el, s["thr"], S.res)
        if s["mode"] == "relaxed":
            trees = trees & ~nat
    from shapely.geometry import mapping
    feats = []
    for g in L.mask_to_polys(S, trees, min_yd2=150, simplify_yd=2.0):
        feats.append(dict(type="Feature", geometry=mapping(g), properties=dict(
            lie="recovery", src=f"vision2:lidar_canopy_hag>{tb['hag']}m_buffer+{s['k']}m", p=0.646)))
    for g in L.mask_to_polys(S, nat, min_yd2=150, simplify_yd=2.0):
        feats.append(dict(type="Feature", geometry=mapping(g), properties=dict(
            lie="native", src="vision2:lgbm_naip_multiyear+lidar", p=float(s["thr"] or 0))))
    feats += water_feats
    return dict(type="FeatureCollection", features=feats,
                properties=dict(schema="vision_any/2", model_id=f"vision_any/2 calib {sid(s)}", setting=s,
                                trained_on="calibration candidate", trees_how="lidar canopy", native_how=sid(s)))


def stage_layers_holdout(out):
    """Product-model layers for every setting on the held-out courses (one course in memory at a time)."""
    import v2_model as VM
    clf_prod, meta = VM.load_model()
    names = meta["features"]
    tb = meta["settings"]["trees"]
    done = []
    for slug in holdouts(need_raw2=True):
        D = VM.prepare(slug)
        region = D["elig_rel"] & D["course"]
        p = VM.predict_grid(D, clf_prod, names, region)
        p = np.where(np.isfinite(p), p, 0).astype(np.float32)
        cp = os.path.join(HERE, slug, "vision_any.geojson")
        water = [f for f in json.load(open(cp))["features"] if f["properties"]["lie"] == "water"] if os.path.exists(cp) else []
        d = os.path.join(out, "prod", slug)
        os.makedirs(d, exist_ok=True)
        for st in settings():
            json.dump(layer_fc(D, p, st, water, tb), open(os.path.join(d, sid(st) + ".geojson"), "w"), separators=(",", ":"))
        log(f"[{slug}] holdout prod: {len(settings())} layers")
        done.append(slug)
        del D
    json.dump(dict(settings=settings(), trees=tb, ob_off=[], holdout=done), open(os.path.join(out, "settings.json"), "w"),
              indent=1)


def stage_layers(out):
    import v2_model as VM
    Ds, H = {}, {}
    for slug in EVAL:
        Ds[slug] = VM.prepare(slug)
        H[slug] = VM.hole_data(Ds[slug])
    clf_prod, meta = VM.load_model()
    names = meta["features"]
    tb = meta["settings"]["trees"]
    for slug, D in Ds.items():
        other = [s for s in Ds if s != slug][0]
        idx, y = VM.balanced(*VM.task_xy(H[other], "native"))
        clf_loco = VM.fit([(Ds[other], idx, y)], names)
        region = D["elig_rel"] & D["course"]
        P = {"loco": VM.predict_grid(D, clf_loco, names, region), "prod": VM.predict_grid(D, clf_prod, names, region)}
        cur = json.load(open(os.path.join(HERE, slug, "vision_any.geojson")))
        water = [f for f in cur["features"] if f["properties"]["lie"] == "water"]
        for psrc, p in P.items():
            p = np.where(np.isfinite(p), p, 0).astype(np.float32)
            d = os.path.join(out, psrc, slug)
            os.makedirs(d, exist_ok=True)
            for s in settings():
                json.dump(layer_fc(D, p, s, water, tb), open(os.path.join(d, sid(s) + ".geojson"), "w"),
                          separators=(",", ":"))
            log(f"[{slug}] {psrc}: {len(settings())} layers")
    json.dump(dict(settings=settings(), trees=tb, ob_off=OB_OFF), open(os.path.join(out, "settings.json"), "w"), indent=1)


# =========================================================================== scoring
_SB = None


def scoreboard():
    global _SB
    if _SB is None:
        sys.path.insert(0, os.path.join(CD, "qa"))
        import scoreboard as SB
        import tee_strategy as t
        SB.HAND_HOLES = copy.deepcopy(t.HOLES)
        _SB = SB
    return _SB


def rebuild_package(pkg_slug, fc, ob_off=None):
    """Committed package with its vision zones replaced by fc and OB re-inferred -> package dict."""
    import importlib.util

    def load(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        sys.modules[name] = m
        spec.loader.exec_module(m)
        return m
    G = load(os.path.join(HERE, "gapfill.py"), "calib_gapfill")
    OB = load(os.path.join(CD, "ob", "infer.py"), "calib_ob_infer")
    pkg = json.load(open(os.path.join(CD, "packages", pkg_slug, "package.json")))
    G.load_layers = lambda slug, imagery_dir=None, course_dir=None: (fc, fc.get("properties", {}))
    out = G.gapfill(pkg)
    params = {} if ob_off is None else {"out_off": ob_off}
    return OB.apply_ob(out, params=params)


_PREV = None


def score_package(pkg_slug, pkg, n=8000, workers=None, holes=None):
    """scoreboard.score_course on a package dict -> list of row dicts."""
    global _PREV
    SB = scoreboard()
    cfg = next(c for c in SB.COURSES if c["slug"] == pkg_slug)
    if _PREV is None:
        _PREV = json.load(open(SB.OUT_JSON)) if os.path.exists(SB.OUT_JSON) else {}
    prev = _PREV
    prev.setdefault("truth_cache", {}).update(SB.TRUTH_RAW)         # hand-map truth computed once per process
    with tempfile.TemporaryDirectory(dir=os.path.join(CD, "packages", pkg_slug)) as td:
        p = os.path.join(td, "package.json")
        json.dump(pkg, open(p, "w"))
        cfg = dict(cfg, package=p)
        a = argparse.Namespace(n=n, workers=workers, from_out=False, holes=holes, no_hand_quick=False, dry_run=False,
                               full=False, full_S=64, full_N=3000)
        out = SB.score_course(cfg, a, prev)
    keep = ("hole", "tee_set", "pick", "aim", "tie", "runner", "margin", "truth", "truth_tie", "truth_runner", "same",
            "same_or_tie", "regret", "hand_quick", "same_hand_quick", "regret_hand_quick", "iou")
    return [{k: r.get(k) for k in keep if k in r} for r in out["holes"]]


def jobs(d):
    S = json.load(open(os.path.join(d, "settings.json")))
    J = [("current", None, None, None)]                         # the committed packages (baseline)
    J += [("obonly", "committed_vision", None, o) for o in S.get("ob_off", OB_OFF)]
    for psrc in ("loco", "prod"):
        for s in S["settings"]:
            J.append((psrc, sid(s), s, None))
    return J


def stage_score_holdout(d, shard, nshards, out):
    S = json.load(open(os.path.join(d, "settings.json")))
    J = [("current", None)] + [("prod", sid(st)) for st in S["settings"]]
    rows = []
    for j, (psrc, ident) in enumerate(J):
        if j % nshards != shard:
            continue
        for vslug in S.get("holdout", []):
            pslug = HOLDOUT[vslug]
            t0 = time.time()
            if psrc == "current":
                pkg = json.load(open(os.path.join(CD, "packages", pslug, "package.json")))
            else:
                pkg = rebuild_package(pslug, json.load(open(os.path.join(d, psrc, vslug, ident + ".geojson"))))
            try:
                rr = score_package(pslug, pkg)
            except Exception as e:                              # noqa: BLE001
                log(f"   {psrc} {ident} {pslug} failed: {type(e).__name__} {e}")
                continue
            for r in rr:
                r.update(psrc=psrc, setting=ident, ob_off=None, course=pslug)
            rows += rr
            log(f"   {psrc:>7} {ident or 'committed':>28} {pslug:>10}: same {sum(bool(r.get('same')) for r in rr)}/"
                f"{sum(1 for r in rr if r.get('truth'))} ({time.time() - t0:.0f}s)")
        json.dump(rows, open(out, "w"), default=float)
    json.dump(rows, open(out, "w"), default=float)


def stage_score(d, shard, nshards, out, extra=None):
    rows = []
    J = jobs(d)
    if extra:                                                   # (psrc, sid, ob_off) triples (stage 2)
        J = [(p, i, None, o) for p, i, o in extra]
    for j, (psrc, ident, s, ob_off) in enumerate(J):
        if j % nshards != shard:
            continue
        for vslug, pslug in EVAL.items():
            t0 = time.time()
            if psrc == "current":
                pkg = json.load(open(os.path.join(CD, "packages", pslug, "package.json")))
            elif psrc == "obonly":
                pkg = rebuild_package(pslug, json.load(open(os.path.join(HERE, vslug, "vision_any.geojson"))), ob_off)
            else:
                fc = json.load(open(os.path.join(d, psrc, vslug, ident + ".geojson")))
                pkg = rebuild_package(pslug, fc, ob_off)
            try:
                rr = score_package(pslug, pkg)
            except Exception as e:                              # noqa: BLE001
                log(f"   {psrc} {ident} {pslug} failed: {type(e).__name__} {e}")
                continue
            for r in rr:
                r.update(psrc=psrc, setting=ident, ob_off=ob_off, course=pslug)
            rows += rr
            ns = sum(bool(r.get("same")) for r in rr)
            log(f"   {psrc:>7} {ident or 'committed':>28} ob {ob_off} {pslug:>14}: same {ns}/{len(rr)} "
                f"({time.time() - t0:.0f}s)")
        json.dump(rows, open(out, "w"), default=float)


# =========================================================================== report
def club_rank(c):
    return CLUB_ORDER.index(c) if c in CLUB_ORDER else len(CLUB_ORDER)


def score_rows(rows):
    """-> dict(same, n, regret, shorter, longer, same_hq) over rows."""
    sc = [r for r in rows if r.get("truth")]
    same = sum(bool(r["same"]) for r in sc)
    rg = [r["regret"] for r in sc if r.get("regret") is not None]
    miss = [r for r in sc if not r["same"]]
    shorter = sum(club_rank(r["pick"]) > club_rank(r["truth"]) for r in miss)
    longer = sum(club_rank(r["pick"]) < club_rank(r["truth"]) for r in miss)
    hq = [r for r in rows if r.get("hand_quick")]
    return dict(same=same, n=len(sc), same_or_tie=sum(bool(r["same_or_tie"]) for r in sc),
                regret=float(np.mean(rg)) if rg else None, sum_regret=float(np.sum(rg)) if rg else 0.0,
                shorter=shorter, longer=longer,
                same_hand_quick=sum(bool(r.get("same_hand_quick")) for r in hq) if hq else None, n_hq=len(hq))


def objective(s):
    """Higher is better: club agreement first, then regret."""
    return (s["same"], -s["sum_regret"])


def stage_report(pattern, out_md, out_json):
    rows = []
    for f in sorted(glob.glob(pattern)):
        rows += json.load(open(f))
    by = {}
    for r in rows:
        by.setdefault((r["psrc"], r["setting"], r.get("ob_off")), []).append(r)
    res = dict(settings={}, selection={})
    for key, rr in by.items():
        res["settings"]["|".join(map(str, key))] = {c: score_rows([r for r in rr if r["course"] == c]) for c in EVAL.values()} | \
            dict(both=score_rows(rr))
    base = by.get(("current", None, None), [])
    res["current"] = {c: score_rows([r for r in base if r["course"] == c]) for c in EVAL.values()} | dict(both=score_rows(base))
    # ---- leave-one-course-out (selection on LOCO maps)
    cand = {k: v for k, v in by.items() if k[0] == "loco"}
    if not cand:
        raise SystemExit("no loco rows")
    loco = {}
    for test in EVAL.values():
        train = [c for c in EVAL.values() if c != test][0]
        best = max(cand, key=lambda k: objective(score_rows([r for r in cand[k] if r["course"] == train])))
        loco[test] = dict(chosen_on=train, setting=best[1], ob_off=best[2],
                          score=score_rows([r for r in cand[best] if r["course"] == test]))
    res["selection"]["loco"] = loco
    # ---- leave-one-hole-out (selection on the other tee shots of both courses, LOCO maps)
    loho_rows = []
    keys = sorted({(r["course"], r["hole"]) for r in base})
    for ck in keys:
        best = max(cand, key=lambda k: objective(score_rows([r for r in cand[k] if (r["course"], r["hole"]) != ck])))
        loho_rows += [dict(r, chosen=best[1]) for r in cand[best] if (r["course"], r["hole"]) == ck]
    res["selection"]["loho"] = {c: score_rows([r for r in loho_rows if r["course"] == c]) for c in EVAL.values()} | \
        dict(both=score_rows(loho_rows), chosen=sorted({r["chosen"] for r in loho_rows}))
    # ---- product: best on both courses with the product maps
    prod = {k: v for k, v in by.items() if k[0] == "prod"}
    pbest = max(prod, key=lambda k: objective(score_rows(prod[k])))
    lbest = max(cand, key=lambda k: objective(score_rows(cand[k])))
    # the product setting is chosen on the LOCO maps (out of sample for the long-grass model); choosing on the
    # product maps would pick up the model's in-sample fit to these two hand maps (it did: thr0.5_relaxed_k0,
    # 22/30 on product maps but 20/30 on LOCO maps). It is then scored with the product maps.
    pk = ("prod", lbest[1], lbest[2])
    res["selection"]["product"] = dict(setting=lbest[1], ob_off=lbest[2], score=res["settings"]["|".join(map(str, pk))],
                                       chosen_on="loco maps, both courses pooled")
    res["selection"]["product_maps_in_sample_best"] = dict(setting=pbest[1], ob_off=pbest[2],
                                                           score=res["settings"]["|".join(map(str, pbest))])
    res["selection"]["loco_pooled_best"] = dict(setting=lbest[1], ob_off=lbest[2], score=res["settings"]["|".join(map(str, lbest))])
    res["ob"] = {str(k[2]): res["settings"]["|".join(map(str, k))] for k in by if k[0] == "obonly"}
    res["gate"] = gate(res["selection"]["product"]["score"], res["current"])
    json.dump(res, open(out_json, "w"), indent=1, default=float)
    write_md(res, by, out_md)
    return res


def gate(cand, cur):
    """Merge gate (decision level, same harness): pooled same club >= the committed packages', on EACH truth course
    not more than one tee shot below, and pooled mean regret not higher (+0.002 noise)."""
    why, ok = [], True
    a, b = cand["both"], cur["both"]
    why.append(f"pooled same club {a['same']}/{a['n']} vs committed {b['same']}/{b['n']}")
    ok &= a["same"] >= b["same"]
    for c in EVAL.values():
        why.append(f"{c} {cand[c]['same']}/{cand[c]['n']} vs {cur[c]['same']}/{cur[c]['n']}")
        ok &= cand[c]["same"] >= cur[c]["same"] - 1
    ra, rb = a["regret"] or 0, b["regret"] or 0
    why.append(f"mean regret {ra:.4f} vs {rb:.4f}")
    ok &= ra <= rb + 0.002
    return dict(pass_=bool(ok), why=why)


def _row(name, s):
    hq = f"{s['same_hand_quick']}/{s['n_hq']}" if s.get("n_hq") else "-"
    return (f"| {name} | {s['same']}/{s['n']} | {s['same_or_tie']}/{s['n']} | "
            f"{'-' if s['regret'] is None else round(s['regret'], 4)} | "
            f"{s['shorter']} / {s['longer']} | {hq} |")


def write_md(res, by, path):
    Lm = ["# vision_any v2: decision-level calibration (long grass, tree buffer, OB offset)", "",
          "Generated by `course_data/vision_any/v2_calibrate.py` on Actions (vision_any_v2_calib.yml). Each setting: the "
          "committed package with only its vision zones replaced, OB re-inferred, product quick decision (n = 8000) vs "
          "the scoreboard truth (Spirit Hollow final_decision.json; Mozingo hand map, quick). `loco` maps = long-grass "
          "model trained on the other course only; `prod` = the product model (both hand maps, in sample). "
          "Misses: shorter / longer = the product's club is shorter / longer than the truth's.", "",
          "| setting | same club | same or tie | mean regret | misses shorter / longer | same as hand map (quick) |",
          "|---|---|---|---|---|---|"]
    cur = res["current"]
    for c in list(EVAL.values()) + ["both"]:
        Lm.append(_row(f"committed packages, {c}", cur[c]))
    Lm += ["", "## Selection", ""]
    for test, v in res["selection"]["loco"].items():
        Lm.append(f"* leave-one-course-out: chosen on {v['chosen_on']} -> `{v['setting']}` (OB {v['ob_off']}); on {test}: "
                  f"same {v['score']['same']}/{v['score']['n']}, regret {v['score']['regret']:.4f}, misses shorter/longer "
                  f"{v['score']['shorter']}/{v['score']['longer']} (committed: {cur[test]['same']}/{cur[test]['n']}).")
    lh = res["selection"]["loho"]
    Lm.append(f"* leave-one-hole-out (both courses, LOCO maps): same {lh['both']['same']}/{lh['both']['n']} "
              f"(SH {lh['spirit_hollow']['same']}/{lh['spirit_hollow']['n']}, Mozingo {lh['mozingo_lake']['same']}/"
              f"{lh['mozingo_lake']['n']}), regret {lh['both']['regret']:.4f}, shorter/longer {lh['both']['shorter']}/"
              f"{lh['both']['longer']}; settings chosen: {', '.join(lh['chosen'])}.")
    for nm in ("loco_pooled_best", "product_maps_in_sample_best", "product"):
        v = res["selection"][nm]
        Lm.append(f"* {nm}: `{v['setting']}` (OB {v['ob_off']}): both {v['score']['both']['same']}/{v['score']['both']['n']}, "
                  f"SH {v['score']['spirit_hollow']['same']}, Mozingo {v['score']['mozingo_lake']['same']}, regret "
                  f"{v['score']['both']['regret']:.4f}.")
    if res.get("ob"):
        Lm += ["", "## OB offset (ob/params.json out_off, committed vision layer; calibrated value -8 = committed row)", "",
               "| out_off yds | SH same | Mozingo same | both | mean regret | shorter / longer |", "|---|---|---|---|---|---|"]
        for o, v in sorted(res["ob"].items(), key=lambda kv: float(kv[0])):
            Lm.append(f"| {o} | {v['spirit_hollow']['same']}/{v['spirit_hollow']['n']} | {v['mozingo_lake']['same']}/"
                      f"{v['mozingo_lake']['n']} | {v['both']['same']}/{v['both']['n']} | {v['both']['regret']:.4f} | "
                      f"{v['both']['shorter']} / {v['both']['longer']} |")
    g = res["gate"]
    Lm += ["", f"**Merge gate: {'PASS' if g['pass_'] else 'FAIL'}** (" + "; ".join(g["why"]) + ")", "",
           "## Every setting (both courses)", "",
           "| maps | setting | OB off | SH same | Mozingo same | both same | mean regret | shorter / longer |", "|---|---|---|---|---|---|---|---|"]
    items = sorted(res["settings"].items(), key=lambda kv: (-kv[1]["both"]["same"], kv[1]["both"]["sum_regret"]))
    for k, v in items:
        ps, st, ob = k.split("|")
        Lm.append(f"| {ps} | {st} | {ob} | {v['spirit_hollow']['same']}/{v['spirit_hollow']['n']} | "
                  f"{v['mozingo_lake']['same']}/{v['mozingo_lake']['n']} | {v['both']['same']}/{v['both']['n']} | "
                  f"{v['both']['regret']:.4f} | {v['both']['shorter']} / {v['both']['longer']} |")
    open(path, "w").write("\n".join(Lm) + "\n")


def stage_holdout_report(pattern, out_md, out_json, train_json=os.path.join(HERE, "v2_decision_calibration.json")):
    """Every setting on the held-out truth courses (product model, out of sample), pooled with the two training
    courses' scores from the committed calibration report; the long-grass question: off vs on."""
    rows = []
    for f in sorted(glob.glob(pattern)):
        rows += json.load(open(f))
    courses = [c for c in HOLDOUT.values() if any(r["course"] == c for r in rows)]
    by = {}
    for r in rows:
        by.setdefault(r["setting"] or "committed", []).append(r)
    train = json.load(open(train_json)) if os.path.exists(train_json) else {}
    tset = train.get("settings", {})
    res = dict(courses=courses, settings={}, train_report=os.path.relpath(train_json, ROOT))
    for k, rr in by.items():
        e = {c: score_rows([r for r in rr if r["course"] == c]) for c in courses}
        e["holdout"] = score_rows(rr)
        t = tset.get(f"prod|{k}|None") if k != "committed" else train.get("current")
        if t:
            e["train"] = t["both"]
            e["all"] = dict(same=e["holdout"]["same"] + t["both"]["same"], n=e["holdout"]["n"] + t["both"]["n"],
                            sum_regret=e["holdout"]["sum_regret"] + t["both"]["sum_regret"])
            e["all"]["regret"] = e["all"]["sum_regret"] / max(e["all"]["n"], 1)
        res["settings"][k] = e
    off = {k: v for k, v in res["settings"].items() if k.startswith("throff")}
    on = {k: v for k, v in res["settings"].items() if k.startswith("thr") and not k.startswith("throff")}

    def best(dct, key="holdout"):
        return max(dct.items(), key=lambda kv: (kv[1][key]["same"], -kv[1][key]["sum_regret"])) if dct else (None, None)
    res["question"] = dict(
        adopted=ADOPTED, previous=PREV_PICK,
        best_off=best(off)[0], best_on=best(on)[0],
        mean_same_off=float(np.mean([v["holdout"]["same"] for v in off.values()])) if off else None,
        mean_same_on=float(np.mean([v["holdout"]["same"] for v in on.values()])) if on else None,
        on_beating_adopted=sorted(k for k, v in on.items() if ADOPTED in res["settings"] and
                                  v["holdout"]["same"] > res["settings"][ADOPTED]["holdout"]["same"]),
        by_threshold={})
    for thr in GRID["thr"]:
        tag = "throff" if thr is None else f"thr{thr}_"
        sub = {k: v for k, v in res["settings"].items() if k.startswith(tag)}
        if sub:
            b = best(sub)
            res["question"]["by_threshold"][str(thr)] = dict(best=b[0], same=b[1]["holdout"]["same"], n=b[1]["holdout"]["n"],
                                                             mean_same=float(np.mean([v["holdout"]["same"] for v in sub.values()])))
    json.dump(res, open(out_json, "w"), indent=1, default=float)
    write_holdout_md(res, out_md)
    return res


def write_holdout_md(res, path):
    C = res["courses"]
    S = res["settings"]
    Q = res["question"]

    def cell(v):
        return f"{v['same']}/{v['n']}"
    Lm = ["# vision_any v2: long-grass / tree settings on held-out hand-checked courses", "",
          "Generated by `course_data/vision_any/v2_calibrate.py holdout-report` on Actions (vision_any_v2_holdout.yml). "
          "Truth: the hand-checked landing-corridor maps `course_data/truth/<slug>/hand_zones_ll.json` through the "
          "product's quick decision (scoreboard 'hand map, quick'). Layers: the product long-grass model (trained on "
          "Spirit Hollow + Mozingo only, so out of sample here) at every calibration setting; each committed package "
          "with only its vision zones replaced, OB re-inferred, product quick decision (n = 8000). `train` = the same "
          f"setting on SH + Mozingo from `{res['train_report']}` (product maps). Nothing here is used to select or "
          "integrate a setting.", "",
          "## The long-grass question", "",
          f"* adopted `{Q['adopted']}` (no long grass): " + (f"held-out {cell(S[Q['adopted']]['holdout'])}, mean regret "
          f"{S[Q['adopted']]['holdout']['regret']:.4f}" if Q['adopted'] in S else "not scored") + ".",
          f"* previous in-sample pick `{Q['previous']}`: " + (f"held-out {cell(S[Q['previous']]['holdout'])}, mean regret "
          f"{S[Q['previous']]['holdout']['regret']:.4f}" if Q['previous'] in S else "not scored") + ".",
          f"* best long-grass-off setting on the held-out courses: `{Q['best_off']}`; best long-grass-on: `{Q['best_on']}`.",
          f"* mean same club over settings: off {Q['mean_same_off']:.2f}, on {Q['mean_same_on']:.2f}." if Q["mean_same_on"] is not None else "",
          f"* long-grass-on settings that beat the adopted one on the held-out courses: {len(Q['on_beating_adopted'])}"
          + (f" ({', '.join(Q['on_beating_adopted'][:8])})" if Q['on_beating_adopted'] else "") + ".", "",
          "| native threshold | best setting | held-out same (best) | mean same over its settings |", "|---|---|---|---|"]
    for thr, v in Q["by_threshold"].items():
        Lm.append(f"| {'off' if thr == 'None' else thr} | `{v['best']}` | {v['same']}/{v['n']} | {v['mean_same']:.2f} |")
    if "committed" in S:
        v = S["committed"]
        Lm += ["", "Committed packages: " + ", ".join(f"{c} {cell(v[c])}" for c in C) + f"; held-out {cell(v['holdout'])}, "
               f"mean regret {v['holdout']['regret']:.4f}."]
    Lm += ["", "## Every setting", "", "| setting | " + " | ".join(C) + " | held-out | mean regret | shorter / longer | "
           "SH + Mozingo (train) | all courses |", "|---|" + "---|" * len(C) + "---|---|---|---|---|"]
    items = sorted(S.items(), key=lambda kv: (-kv[1]["holdout"]["same"], kv[1]["holdout"]["sum_regret"]))
    for k, v in items:
        h = v["holdout"]
        Lm.append(f"| `{k}` | " + " | ".join(cell(v[c]) for c in C) + f" | {cell(h)} | "
                  f"{'-' if h['regret'] is None else round(h['regret'], 4)} | {h['shorter']} / {h['longer']} | "
                  f"{cell(v['train']) if v.get('train') else '-'} | {cell(v['all']) if v.get('all') else '-'} |")
    open(path, "w").write("\n".join(x for x in Lm if x is not None) + "\n")


def stage_integrate(res_json, slugs=("spirit_hollow", "mozingo", "veenker")):
    """Adopt the product selection if the merge gate passed: model_v2/model.json settings, v2 layers for every
    course (v2_model.infer, integrated), and the committed packages' vision zones rebuilt (OB re-inferred with
    ob/params.json as committed)."""
    import v2_model as VM
    R = json.load(open(res_json))
    if not R["gate"]["pass_"]:
        log("merge gate FAILED: nothing integrated: " + "; ".join(R["gate"]["why"]))
        return False
    st = next(s for s in settings() if sid(s) == R["selection"]["product"]["setting"])
    mp = os.path.join(VM.MODEL_DIR, "model.json")
    meta = json.load(open(mp))
    old = dict(meta["settings"])
    meta["settings"].update(native_thr=st["thr"], native_mode=st["mode"], native_dmin_yd=st["dmin"])
    meta["settings"]["trees"] = dict(meta["settings"]["trees"], k_m=st["k"])
    meta["decision_calibration"] = dict(previous=old, chosen=sid(st), gate=R["gate"],
                                        report="course_data/vision_any/v2_decision_calibration.md")
    json.dump(meta, open(mp, "w"), indent=1)
    for slug in slugs:
        VM.infer(slug, integrate=True)
    for vslug, pslug in (("spirit_hollow", "spirit_hollow"), ("mozingo", "mozingo_lake"), ("veenker", "veenker")):
        pp = os.path.join(CD, "packages", pslug, "package.json")
        if not os.path.exists(pp):
            continue
        fc = json.load(open(os.path.join(HERE, vslug, "vision_any.geojson")))
        pkg = rebuild_package(pslug, fc)
        pkg.setdefault("stages", {})["vision"] += f" (decision-calibrated {sid(st)}; zones_ll rebuilt by v2_calibrate.py)"
        json.dump(pkg, open(pp, "w"))
        log(f"rebuilt {os.path.relpath(pp, ROOT)}")
    return True


def stage_adopt(res_json, setting, md):
    """Re-select the product setting from an existing report (no re-scoring), re-gate, integrate if it passes."""
    R = json.load(open(res_json))
    k = f"prod|{setting}|None"
    R["selection"]["product"] = dict(setting=setting, ob_off=None, score=R["settings"][k], chosen_on="adopt (request)")
    R["gate"] = gate(R["settings"][k], R["current"])
    json.dump(R, open(res_json, "w"), indent=1, default=float)
    s = R["settings"][k]
    with open(md, "a") as fh:
        fh.write(f"\n## Adopted: `{setting}`\n\nProduct maps: SH {s['spirit_hollow']['same']}/{s['spirit_hollow']['n']}, "
                 f"Mozingo {s['mozingo_lake']['same']}/{s['mozingo_lake']['n']}, both {s['both']['same']}/{s['both']['n']}, "
                 f"mean regret {s['both']['regret']:.4f}, misses shorter / longer {s['both']['shorter']} / {s['both']['longer']}. "
                 f"Merge gate: {'PASS' if R['gate']['pass_'] else 'FAIL'} ({'; '.join(R['gate']['why'])}).\n")
    return stage_integrate(res_json)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    a1 = sp.add_parser("layers")
    a1.add_argument("--out", required=True)
    a1.add_argument("--holdout", action="store_true")
    a2 = sp.add_parser("score")
    a2.add_argument("--dir", required=True)
    a2.add_argument("--shard", type=int, default=0)
    a2.add_argument("--nshards", type=int, default=1)
    a2.add_argument("--out", required=True)
    a2.add_argument("--holdout", action="store_true")
    a5 = sp.add_parser("holdout-report")
    a5.add_argument("--rows", required=True)
    a5.add_argument("--md", default=os.path.join(HERE, "v2_holdout_calibration.md"))
    a5.add_argument("--json", default=os.path.join(HERE, "v2_holdout_calibration.json"))
    a3 = sp.add_parser("report")
    a3.add_argument("--rows", required=True)
    a3.add_argument("--md", default=os.path.join(HERE, "v2_decision_calibration.md"))
    a3.add_argument("--json", default=os.path.join(HERE, "v2_decision_calibration.json"))
    a3.add_argument("--integrate", action="store_true", help="adopt the product selection if the merge gate passes")
    a4 = sp.add_parser("adopt")
    a4.add_argument("--setting", required=True)
    a4.add_argument("--md", default=os.path.join(HERE, "v2_decision_calibration.md"))
    a4.add_argument("--json", default=os.path.join(HERE, "v2_decision_calibration.json"))
    a = ap.parse_args()
    if a.cmd == "layers":
        stage_layers_holdout(a.out) if a.holdout else stage_layers(a.out)
    elif a.cmd == "score" and a.holdout:
        stage_score_holdout(a.dir, a.shard, a.nshards, a.out)
    elif a.cmd == "holdout-report":
        stage_holdout_report(a.rows, a.md, a.json)
        print(open(a.md).read())
    elif a.cmd == "score":
        extra = None
        stage_score(a.dir, a.shard, a.nshards, a.out, extra)
    elif a.cmd == "adopt":
        stage_adopt(a.json, a.setting, a.md)
    elif a.cmd == "report":
        r = stage_report(a.rows, a.md, a.json)
        print(open(a.md).read())
        print(json.dumps(r["gate"]))
        if a.integrate:
            stage_integrate(a.json)


if __name__ == "__main__":
    main()
