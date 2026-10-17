"""Tree-line settings re-fitted with leave-one-course-out cross-validation over all five truth courses.

  python3 course_data/vision_any/v2_trees_cv.py layers --out DIR [--courses ...]
  python3 course_data/vision_any/v2_trees_cv.py score  --dir DIR --rows ROWS.json [--shard i --nshards n]
  python3 course_data/vision_any/v2_trees_cv.py report --rows 'ROWS*.json'   -> v2_trees_cv.{md,json}

Settings (long grass stays off, as in the product): the golfer's trees line = lidar canopy (HAG > 2.5 m, clumps
>= 100 m2) with
  * recency  none | remove | add  (course_data/vision_any/canopy_recency.py: lidar canopy the post-lidar NAIP
             years no longer show as trees removed; 'add' also adds canopy every post-lidar year shows)
  * k        buffer in metres (negative = erode); the product uses +3.
  * fc       product/package.py FIRST_CUT_YDS: a first-cut band of fc yds around the fairway (the hand maps trace
             first cut; course_data/qa/short_club_diagnosis.md finds the fairway / corridor width behind as many
             misses as the trees); the product uses 0.
Each setting: the committed package with only its vision zones replaced (water as committed), OB re-inferred,
product quick decision (n = 8000) per tee shot vs the scoreboard truth (v2_calibrate.rebuild_package /
score_package, the harness of v2_decision_calibration and v2_holdout_calibration).

Selection (report): leave-one-COURSE-out over the 5 courses. For each test course the setting with the most same
clubs (then the least summed regret, then the product setting) on the OTHER four courses is scored on the test
course; the cross-validated number is the sum of those five test scores, so no course is scored with a setting
it helped pick. The adoption rule: the cross-validated same-club count beats the product setting's, and neither
Spirit Hollow nor Mozingo is worse than with the product setting (in cross-validation or with the setting chosen on
all five courses).
"""
import argparse
import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")    # sklearn next to decide.py worker pools: no oversubscription
import glob
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CD = os.path.join(ROOT, "course_data")
sys.path.insert(0, HERE)
import layers as L                                           # noqa: E402

COURSES = {"spirit_hollow": "spirit_hollow", "mozingo": "mozingo_lake", "veenker": "veenker",
           "coldwater": "coldwater", "ellis": "ellis"}         # vision slug -> package / scoreboard slug
NAMES = {"spirit_hollow": "Spirit Hollow", "mozingo_lake": "Mozingo", "veenker": "Veenker", "coldwater": "Coldwater",
         "ellis": "Ellis"}
GRID = dict(rec=["none", "remove", "add"], k=[-1, 0, 1, 2, 3], fc=[0, 4, 8])
PRODUCT = "none_k3_fc0"
HAG, MIN_AREA = 2.5, 100.0
CLUB_ORDER = ["Driver", "2-wood", "3-wood", "4-wood", "5-wood", "Hybrid", "Long iron", "Mid iron", "Short iron"]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sid(s):
    return f"{s['rec']}_k{s['k']}_fc{s.get('fc', 0)}"


def layer_id(s):
    return f"{s['rec']}_k{s['k']}"


def settings(grid=GRID):
    return [dict(rec=r, k=k, fc=f) for r in grid["rec"] for k in grid["k"] for f in grid.get("fc", [0])]


def layer_settings(grid=GRID):
    return [dict(rec=r, k=k) for r in grid["rec"] for k in grid["k"]]


# =========================================================================== layers
def course_layers(vslug, out, grid=GRID):
    import run_any as RA
    import canopy_recency as CR
    import v2_model as VM
    from shapely.geometry import mapping
    cdir = RA.course_dir_for(vslug)
    S = L.Stack.load(vslug, cdir)
    M, _ = L.osm_masks(S, json.load(open(os.path.join(cdir, "osm.geojson"))))
    canopy = L.tree_mask(S, M, hag_min=HAG, min_area_m2=10.0)[0]           # as v2_model.prepare
    area = ndimage.binary_dilation(M["course"], L.disk(30)) if M["course"].any() else np.ones_like(canopy)
    R = CR.recency(S, canopy, M, area, add=True)
    info = {k: v for k, v in R.items() if k not in ("removed", "added", "p")}
    info["map_check"] = CR.map_check(S, canopy, R, vslug)
    cur = json.load(open(os.path.join(HERE, vslug, "vision_any.geojson")))
    water = [f for f in cur["features"] if f["properties"]["lie"] == "water"]
    d = os.path.join(out, vslug)
    os.makedirs(d, exist_ok=True)
    for s in layer_settings(grid):
        c = canopy.copy()
        if s["rec"] in ("remove", "add"):
            c &= ~R["removed"]
        if s["rec"] == "add":
            c |= R["added"]
        trees = VM.tree_rule(c, s["k"], MIN_AREA, S.res)
        feats = [dict(type="Feature", geometry=mapping(g), properties=dict(
            lie="recovery", src=f"vision2:lidar_canopy_hag>{HAG}m_recency-{s['rec']}_buffer{s['k']:+d}m", p=0.646))
            for g in L.mask_to_polys(S, trees, min_yd2=150, simplify_yd=2.0)]
        fc = dict(type="FeatureCollection", features=feats + water,
                  properties=dict(schema="vision_any/2", model_id=f"vision_any/2 trees-cv {layer_id(s)}", setting=s))
        json.dump(fc, open(os.path.join(d, layer_id(s) + ".geojson"), "w"), separators=(",", ":"))
    # recency masks as polygons (for review / integration)
    rec = []
    for nm in ("removed", "added"):
        for g in L.mask_to_polys(S, R[nm], min_yd2=20, simplify_yd=1.0):
            rec.append(dict(type="Feature", geometry=mapping(g), properties=dict(kind=nm)))
    json.dump(dict(type="FeatureCollection", features=rec, properties=info), open(os.path.join(d, "recency.geojson"), "w"),
              separators=(",", ":"))
    log(f"[{vslug}] {len(layer_settings(grid))} layers -> {d}")
    return info


def stage_layers(out, courses):
    os.makedirs(out, exist_ok=True)
    info = {}
    for v in courses:
        info[v] = course_layers(v, out)
    p = os.path.join(out, "settings.json")
    old = json.load(open(p)) if os.path.exists(p) else {}
    old.setdefault("recency", {}).update(info)
    old["settings"] = settings()
    json.dump(old, open(p, "w"), indent=1, default=float)


# =========================================================================== score
def stage_score(d, rows_path, shard=0, nshards=1, courses=None, only=None):
    """Score (setting, course) pairs i % nshards == shard; fc sets product/package.py FIRST_CUT_YDS."""
    import v2_calibrate as C
    C.scoreboard()
    import package as PK                                    # the module the scoreboard's product_plan uses
    rows = json.load(open(rows_path)) if os.path.exists(rows_path) else []
    done = {(r["setting"], r["course"]) for r in rows}
    S = json.load(open(os.path.join(d, "settings.json")))
    J = [("committed", None)] + [(sid(s), s) for s in S["settings"]]
    if only:
        J = [j for j in J if j[0] in only]
    pairs = [(i, s, v, p) for i, s in J for v, p in COURSES.items() if not courses or v in courses]
    for j, (ident, s, vslug, pslug) in enumerate(pairs):
        if j % nshards != shard or (ident, pslug) in done:
            continue
        t0 = time.time()
        if ident == "committed":
            pkg = json.load(open(os.path.join(CD, "packages", pslug, "package.json")))
            PK.FIRST_CUT_YDS = 0.0
        else:
            p = os.path.join(d, vslug, layer_id(s) + ".geojson")
            if not os.path.exists(p):
                continue
            pkg = C.rebuild_package(pslug, json.load(open(p)))
            PK.FIRST_CUT_YDS = float(s.get("fc", 0))
        try:
            rr = C.score_package(pslug, pkg)
        except Exception as e:                                  # noqa: BLE001
            log(f"   {ident} {pslug} failed: {type(e).__name__} {e}")
            continue
        finally:
            PK.FIRST_CUT_YDS = 0.0
        for r in rr:
            r.update(setting=ident, course=pslug)
        rows += rr
        json.dump(rows, open(rows_path, "w"), default=float)
        log(f"   {ident:>16} {pslug:>14}: same {sum(bool(r.get('same')) for r in rr)}/"
            f"{sum(1 for r in rr if r.get('truth'))} ({time.time() - t0:.0f}s)")


# =========================================================================== report
def club_rank(c):
    return CLUB_ORDER.index(c) if c in CLUB_ORDER else len(CLUB_ORDER)


def score_rows(rows):
    sc = [r for r in rows if r.get("truth")]
    miss = [r for r in sc if not r["same"]]
    rg = [r["regret"] for r in sc if r.get("regret") is not None]
    return dict(same=sum(bool(r["same"]) for r in sc), n=len(sc), same_or_tie=sum(bool(r["same_or_tie"]) for r in sc),
                sum_regret=float(np.sum(rg)) if rg else 0.0, regret=float(np.mean(rg)) if rg else None,
                shorter=sum(club_rank(r["pick"]) > club_rank(r["truth"]) for r in miss),
                longer=sum(club_rank(r["pick"]) < club_rank(r["truth"]) for r in miss))


def add(a, b):
    out = {k: a[k] + b[k] for k in ("same", "n", "same_or_tie", "sum_regret", "shorter", "longer")}
    out["regret"] = out["sum_regret"] / max(out["n"], 1)
    return out


ZERO = dict(same=0, n=0, same_or_tie=0, sum_regret=0.0, shorter=0, longer=0, regret=None)


def objective(s, ident):
    return (s["same"], -round(s["sum_regret"], 6), ident == PRODUCT)


def stage_report(pattern, out_md, out_json, layers_info=None):
    rows = []
    for f in sorted(glob.glob(pattern)):
        rows += json.load(open(f))
    seen = {}
    for r in rows:                                        # de-duplicate (setting, course, hole)
        seen[(r["setting"], r["course"], str(r["hole"]))] = r
    rows = list(seen.values())
    courses = [c for c in COURSES.values() if any(r["course"] == c for r in rows)]
    by = {}
    for r in rows:
        by.setdefault(r["setting"], {}).setdefault(r["course"], []).append(r)
    T = {k: {c: score_rows(v.get(c, [])) for c in courses} for k, v in by.items()
         if all(c in v for c in courses)}                  # only settings scored on every course
    for k, v in T.items():
        tot = dict(ZERO)
        for c in courses:
            tot = add(tot, v[c])
        v["all"] = tot
    cand = [k for k in T if k != "committed"]
    loco = {}
    cv = dict(ZERO)
    for test in courses:
        train = [c for c in courses if c != test]

        def tr(k):
            s = dict(ZERO)
            for c in train:
                s = add(s, T[k][c])
            return s
        best = max(cand, key=lambda k: objective(tr(k), k))
        loco[test] = dict(chosen=best, train=tr(best), test=T[best][test], product=T[PRODUCT][test] if PRODUCT in T else None)
        cv = add(cv, T[best][test])
    full = max(cand, key=lambda k: objective(T[k]["all"], k))
    base = T.get(PRODUCT)
    ok = base is not None and cv["same"] > base["all"]["same"]
    why = [f"cross-validated {cv['same']}/{cv['n']} vs product setting {base['all']['same']}/{base['all']['n']}" if base else "no product row"]
    for c in ("spirit_hollow", "mozingo_lake"):
        if base and c in courses:
            a_, b_, f_ = loco[c]["test"]["same"], base[c]["same"], T[full][c]["same"]
            why.append(f"{NAMES[c]}: CV {a_} / chosen-on-all {f_} vs product {b_}")
            ok &= a_ >= b_ and f_ >= b_
    res = dict(courses=courses, settings=T, loco=loco, cv=cv, chosen_on_all=full, product=PRODUCT,
               adopt=bool(ok and full != PRODUCT), why=why, layers=layers_info or {})
    json.dump(res, open(out_json, "w"), indent=1, default=float)
    write_md(res, out_md)
    return res


def write_md(res, path):
    C, T = res["courses"], res["settings"]

    def cell(v):
        return f"{v['same']}/{v['n']}"
    Lm = ["# Tree line (buffer + canopy recency): leave-one-course-out over the five truth courses", "",
          "Generated by `course_data/vision_any/v2_trees_cv.py`. Each setting: the committed package with only its tree "
          "zones rebuilt (lidar canopy HAG > 2.5 m, clumps >= 100 m2, canopy recency, buffer k m; long grass off, water as "
          "committed), OB re-inferred, product quick decision (n = 8000) vs the scoreboard truth on Spirit Hollow, Mozingo, "
          "Veenker, Coldwater, Ellis. Recency: `canopy_recency.py` (lidar canopy no post-lidar NAIP year shows as trees "
          "removed; `add` also adds canopy all post-lidar years show).", "",
          "## Cross-validation (leave one course out)", "",
          "| test course | setting chosen on the other four | train same | test same | product setting on test |",
          "|---|---|---|---|---|"]
    for c, v in res["loco"].items():
        Lm.append(f"| {NAMES[c]} | `{v['chosen']}` | {cell(v['train'])} | {cell(v['test'])} | "
                  f"{cell(v['product']) if v['product'] else '-'} |")
    b = T.get(res["product"], {}).get("all")
    cv = res["cv"]
    Lm += ["", f"**Cross-validated: {cell(cv)} same club (mean regret {cv['regret']:.4f}, misses shorter / longer "
           f"{cv['shorter']} / {cv['longer']})** vs the product setting `{res['product']}` "
           + (f"{cell(b)} (mean regret {b['regret']:.4f}, shorter / longer {b['shorter']} / {b['longer']})." if b else "-."),
           f"Chosen on all five: `{res['chosen_on_all']}`. Adopt: **{'yes' if res['adopt'] else 'no'}** ("
           + "; ".join(res["why"]) + ").", ""]
    if res.get("layers"):
        Lm += ["## Canopy recency per course", "",
               "| course | lidar | post-lidar NAIP | canopy m2 | removed | added | removed inside hand footprints: share hand-traced trees | "
               "tree IoU in footprints: lidar -> recency | precision: lidar -> recency |", "|---|---|---|---|---|---|---|---|---|"]
        for v, i in res["layers"].items():
            mc = i.get("map_check") or {}
            Lm.append(f"| {v} | {i.get('lidar_year')} | {i.get('post_years')} | {i.get('canopy_m2', 0):.0f} | "
                      f"{i.get('removed_m2', 0):.0f} ({i.get('removed_m2', 0) / max(i.get('canopy_m2', 1), 1):.1%}) | "
                      f"{i.get('added_m2', 0):.0f} | "
                      + (f"{mc.get('removed_in_footprint_m2', 0):.0f} m2: {mc.get('removed_hand_trees_share', 0):.0%} | "
                         f"{mc.get('iou_lidar', 0):.3f} -> {mc.get('iou_recency', 0):.3f} | "
                         f"{mc.get('precision_lidar', 0):.3f} -> {mc.get('precision_recency', 0):.3f} |" if mc else "- | - | - |"))
        Lm.append("")
    Lm += ["## Every setting", "", "| setting | " + " | ".join(NAMES[c] for c in C) + " | all | mean regret | shorter / longer |",
           "|---|" + "---|" * len(C) + "---|---|---|"]
    for k, v in sorted(T.items(), key=lambda kv: (-kv[1]["all"]["same"], kv[1]["all"]["sum_regret"])):
        a = v["all"]
        Lm.append(f"| `{k}`{' (product)' if k == res['product'] else ''} | " + " | ".join(cell(v[c]) for c in C) +
                  f" | {cell(a)} | {a['regret']:.4f} | {a['shorter']} / {a['longer']} |")
    open(path, "w").write("\n".join(Lm) + "\n")


def stage_integrate(res_json, slugs=("spirit_hollow", "mozingo", "veenker", "coldwater", "ellis", "wakonda")):
    """Adopt the report's chosen-on-all setting (only if its adoption rule passed): model_v2/model.json trees settings,
    the tree zones of every course's vision_any.geojson rebuilt (water / other zones as committed), and the committed
    packages' vision zones rebuilt with OB re-inferred (v2_calibrate.rebuild_package, the harness that scored it)."""
    import run_any as RA
    import v2_calibrate as C
    import v2_model as VM
    from shapely.geometry import mapping
    R = json.load(open(res_json))
    if not R.get("adopt"):
        log("adoption rule failed: nothing integrated: " + "; ".join(R.get("why", [])))
        return False
    st = next(s for s in settings() if sid(s) == R["chosen_on_all"])
    if st.get("fc"):
        raise SystemExit("a first-cut band setting is a product/package.py change: integrate it by hand")
    mp = os.path.join(VM.MODEL_DIR, "model.json")
    meta = json.load(open(mp))
    old = dict(meta["settings"]["trees"])
    meta["settings"]["trees"] = dict(old, k_m=int(st["k"]), recency=st["rec"])
    meta["trees_cv"] = dict(previous=old, chosen=sid(st), cv=R["cv"], why=R["why"],
                            report="course_data/vision_any/v2_trees_cv.md")
    json.dump(meta, open(mp, "w"), indent=1)
    for vslug in slugs:
        cp = os.path.join(HERE, vslug, "vision_any.geojson")
        if not os.path.exists(cp):
            continue
        cdir = RA.course_dir_for(vslug)
        S = L.Stack.load(vslug, cdir)
        M, _ = L.osm_masks(S, json.load(open(os.path.join(cdir, "osm.geojson"))))
        canopy = L.tree_mask(S, M, hag_min=HAG, min_area_m2=10.0)[0]
        if st["rec"] != "none":
            import canopy_recency as CR
            area = ndimage.binary_dilation(M["course"], L.disk(30)) if M["course"].any() else np.ones_like(canopy)
            Rr = CR.recency(S, canopy, M, area, add=st["rec"] == "add")
            canopy = (canopy & ~Rr["removed"]) | (Rr["added"] if st["rec"] == "add" else False)
        trees = VM.tree_rule(canopy, st["k"], MIN_AREA, S.res)
        fc = json.load(open(cp))
        src = f"vision2:lidar_canopy_hag>{HAG}m_buffer{int(st['k']):+d}m" + ("" if st["rec"] == "none" else f"_recency-{st['rec']}")
        S.ll_to_rc([[0, 0]])
        from shapely.ops import transform
        new = []
        for g in L.mask_to_polys(S, trees, min_yd2=150, simplify_yd=2.0):
            gm = transform(lambda x, y: S._fwd.transform(x, y), g)
            new.append(dict(type="Feature", geometry=mapping(g), properties=dict(
                lie="recovery", src=src, p=0.8, area_yd2=round(gm.area / 0.9144 ** 2), model="vision_any/2")))
        p_old = [f["properties"].get("p") for f in fc["features"] if f["properties"]["lie"] == "recovery"]
        if p_old:
            for f in new:
                f["properties"]["p"] = p_old[0]
        fc["features"] = new + [f for f in fc["features"] if f["properties"]["lie"] != "recovery"]
        pr = fc.setdefault("properties", {})
        pr["trees_how"] = (pr.get("trees_how", "").split("; golfer trees line")[0] +
                           f"; golfer trees line = canopy (HAG > {HAG} m, clumps >= {MIN_AREA:g} m2) buffered "
                           f"{int(st['k']):+d} m, recency {st['rec']} (leave-one-course-out over the five truth courses, "
                           "course_data/vision_any/v2_trees_cv.md)")
        pr["trees_cv"] = sid(st)
        json.dump(fc, open(cp, "w"), separators=(",", ":"))
        log(f"[{vslug}] vision_any.geojson: {len(new)} tree polygons ({sid(st)})")
        pslug = COURSES.get(vslug, vslug)
        pp = os.path.join(CD, "packages", pslug, "package.json")
        if os.path.exists(pp):
            pkg = C.rebuild_package(pslug, fc)
            pkg.setdefault("stages", {})["vision"] = pkg.get("stages", {}).get("vision", "") + \
                f" (trees re-fitted {sid(st)}; zones_ll rebuilt by v2_trees_cv.py)"
            json.dump(pkg, open(pp, "w"))
            log(f"rebuilt {os.path.relpath(pp, ROOT)}")
    return True


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    a1 = sp.add_parser("layers")
    a1.add_argument("--out", required=True)
    a1.add_argument("--courses")
    a2 = sp.add_parser("score")
    a2.add_argument("--dir", required=True)
    a2.add_argument("--rows", required=True)
    a2.add_argument("--shard", type=int, default=0)
    a2.add_argument("--nshards", type=int, default=1)
    a2.add_argument("--courses")
    a2.add_argument("--only")
    a3 = sp.add_parser("report")
    a3.add_argument("--rows", required=True)
    a3.add_argument("--dir")
    a3.add_argument("--md", default=os.path.join(HERE, "v2_trees_cv.md"))
    a3.add_argument("--json", default=os.path.join(HERE, "v2_trees_cv.json"))
    a4 = sp.add_parser("integrate")
    a4.add_argument("--json", default=os.path.join(HERE, "v2_trees_cv.json"))
    a = ap.parse_args()
    if a.cmd == "integrate":
        stage_integrate(a.json)
    elif a.cmd == "layers":
        stage_layers(a.out, a.courses.split(",") if a.courses else list(COURSES))
    elif a.cmd == "score":
        stage_score(a.dir, a.rows, a.shard, a.nshards, a.courses.split(",") if a.courses else None,
                    set(a.only.split(",")) if a.only else None)
    elif a.cmd == "report":
        info = json.load(open(os.path.join(a.dir, "settings.json"))).get("recency") if a.dir else None
        stage_report(a.rows, a.md, a.json, info)
        print(open(a.md).read())


if __name__ == "__main__":
    main()
