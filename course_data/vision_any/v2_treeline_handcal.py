"""Tree edge vs the HAND tree lines: lidar canopy threshold + buffer, leave-one-course-out over the hand-truth courses.

    OMP_NUM_THREADS=1 python3 course_data/vision_any/v2_treeline_handcal.py      # -> v2_treeline_handcal.{json,md}

Why: platform/ERROR_BUDGET.md finds the auto tree edge short of the hand tree line on the fairway side (median 680
sq yds per landing corridor missing vs 60 extra). v2_trees_cv.py chose the buffer by product decisions on five
scoreboard courses; this calibrates the EDGE itself against the hand-traced tree lines.

Labels: the hand corridor maps of the error-budget truth courses (platform/error_budget.truth_holes: holes_truth
courses + Veenker / Coldwater / Ellis corridors + Spirit Hollow; National KC's hand map is used too, Colbert Hills
has no hand trees, Mozingo's map is in screenshot pixels). These are the ONLY georeferenced hand tree lines in the
repo, so there is no separate training set: the setting is chosen leave-one-course-out (for each course, the
setting best on the other courses is scored on it) and the reported numbers are those held-out scores.

Per hole, inside the traced footprint (the landing corridor), on the 1 m vision_any grid:
  hand trees   the visible 'recovery' region of the hand stack (traced order, later wins)
  auto trees   v2_model.tree_rule(L.tree_mask(HAG > hag), k, 100 m2) minus the auto package's lies that are
               painted over trees (product/package.ORDER: rough, first cut, fairway, green, water, sand), i.e. the
               trees the product sees
  missing / extra (sq yds), IoU, and the edge bias = (extra - missing) / hand tree edge length (yds; + = auto
  trees reach further than the hand line)
Selection: the pooled IoU of the other courses (then the smallest |bias|). The edge optimum is NOT the product
setting: see NOTE (the plans were scored with platform/error_budget.py before adopting anything).
"""
from __future__ import annotations

import json
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(CD, "platform"))

YD = 0.9144
HAGS = [1.5, 2.0, 2.5, 3.0]
KS = [-1, 0, 1, 2, 3, 4, 5, 6, 8]
MIN_AREA = 100.0
COURSES = ["blue_hills", "eagle_knoll", "gateway_national", "national_kc", "hot_springs_arlington", "pine_dunes",
           "veenker", "coldwater", "ellis", "spirit_hollow"]
AFTER_TREES = ("rough", "first_cut", "fairway", "green", "water", "sand")      # product/package.ORDER after recovery
OUT_JSON = os.path.join(HERE, "v2_treeline_handcal.json")
OUT_MD = os.path.join(HERE, "v2_treeline_handcal.md")
NOTE = ("**Not adopted** (model_v2/model.json keeps HAG 2.5 m, buffer -1 m; `treeline_handcal` records why). Every held-out fold chose k = +1 for the EDGE (HAG 2.5 and 3.0 within 0.001 IoU), but the plans get worse: on the error budget's 138 card tee shots (platform/ERROR_BUDGET.md, 'Tees and trees') auto match k -1 / 0 / +1 = 102 / 102 / 100, same club 123 / 122 / 120, regret 2.654 / 2.591 / 2.603, and a decision-level leave-one-course-out over k picks nothing better than -1 (86 vs 89 matches). The +1 layer alone in the truth breaks 4 holes (-1: 10), so the edge itself is closer; the short edge offsets other auto-layer errors (missing long grass, narrow fairways). Re-measure after those fixes: `platform/rebuild_tees_trees.py --layers trees --k 1` + `error_budget.py --auto-dir`. Spirit Hollow is an outlier (IoU 0.28 at every setting: wide hand corridors whose tree lines do not follow the canopy).")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def course_grids(slug):
    """(S, {hag: canopy mask}) on the vision_any 1 m grid, as v2_model.prepare."""
    import layers as L
    import run_any as RA
    cdir = RA.course_dir_for(slug)
    S = L.Stack.load(slug, cdir)
    M, _ = L.osm_masks(S, json.load(open(os.path.join(cdir, "osm.geojson"))))
    return S, {h: L.tree_mask(S, M, hag_min=h, min_area_m2=10.0)[0] for h in HAGS}


def tree_masks(canopy, res):
    """{k: v2_model.tree_rule(canopy, k, MIN_AREA)} from two distance transforms."""
    import layers as L
    m = L.remove_small(canopy, MIN_AREA / res ** 2)
    dout = ndimage.distance_transform_edt(~m) * res
    din = ndimage.distance_transform_edt(m) * res
    return {k: (dout <= k) if k > 0 else (din > -k) if k < 0 else m for k in KS}


def rasterize(S, geoms):
    from rasterio.features import rasterize as rz
    from shapely.ops import transform as stransform
    S.ll_to_rc([[0, 0]])
    gg = [stransform(lambda x, y: S._fwd.transform(x, y), g) for g in geoms if g is not None and not g.is_empty]
    if not gg:
        return np.zeros((S.H, S.W), bool)
    return rz([(g, 1) for g in gg], out_shape=(S.H, S.W), transform=S.transform, fill=0, dtype="uint8").astype(bool)


def hole_labels(slug, S):
    """[(ref, footprint mask, hand trees mask, hand tree edge length yds)] + the auto 'painted over trees' mask."""
    import error_budget as E
    from shapely.geometry import Polygon
    cfg = next(c for c in E.COURSES if c["slug"] == slug)
    truth = E.truth_holes(cfg)
    pkg = json.load(open(os.path.join(ROOT, cfg["package"]) if cfg.get("package") else
                         os.path.join(CD, "packages", slug, "package.json")))
    P = E.PK()
    over = []
    for h in pkg["holes"].values():
        for z in h.get("zones_ll") or []:
            lie = P.LIE_MAP.get(z.get("lie"), z.get("lie"))
            if lie in AFTER_TREES and z.get("poly") and len(z["poly"]) >= 3:
                over.append(E._geom(E._ring(z["poly"])))
    over_m = rasterize(S, over)
    rows = []
    for ref, td in truth.items():
        if not td.get("hand"):
            continue
        fp = E._geom(E._ring(td["hand"]["footprint"]))
        st = E.truth_stack([], td)
        eff = E.effective(st)
        ht = eff.get("recovery")
        F = rasterize(S, [fp])
        if F.sum() < 100:
            continue
        H = rasterize(S, [ht.intersection(fp)]) if ht is not None and not ht.is_empty else np.zeros_like(F)
        H &= F
        edge = (H & ~ndimage.binary_erosion(H)).sum() * S.res / YD if H.any() else 0.0
        rows.append((ref, F, H, edge))
    return rows, over_m


def course_metrics(slug):
    t0 = time.time()
    S, can = course_grids(slug)
    rows, over = hole_labels(slug, S)
    a = (S.res / YD) ** 2
    out = {}
    for hg, c in can.items():
        for k, T in tree_masks(c, S.res).items():
            vis = T & ~over
            per = []
            for ref, F, H, edge in rows:
                A = vis & F
                per.append(dict(ref=ref, missing=float((H & ~A).sum() * a), extra=float((A & ~H).sum() * a),
                                inter=float((H & A).sum() * a), union=float((H | A).sum() * a), edge=float(edge)))
            out[f"{hg}_{k}"] = per
    log(f"[{slug}] {len(rows)} corridors, {time.time() - t0:.0f} s")
    return out


def agg(per):
    m = sum(p["missing"] for p in per)
    e = sum(p["extra"] for p in per)
    i = sum(p["inter"] for p in per)
    u = sum(p["union"] for p in per)
    ed = sum(p["edge"] for p in per)
    return dict(missing=round(m), extra=round(e), iou=round(i / u, 3) if u else None,
                bias_yd=round((e - m) / ed, 2) if ed else None, n=len(per),
                med_missing=round(float(np.median([p["missing"] for p in per])), 0) if per else None,
                med_extra=round(float(np.median([p["extra"] for p in per])), 0) if per else None)


def select(R, courses):
    keys = list(next(iter(R.values())))

    def score(k, cs):
        a = agg([p for c in cs for p in R[c][k]])
        return (a["iou"] or 0, -abs(a["bias_yd"] or 0))
    loco = {}
    for c in courses:
        others = [o for o in courses if o != c]
        best = max(keys, key=lambda k: score(k, others))
        loco[c] = dict(chosen=best, test=agg(R[c][best]), product=agg(R[c]["2.5_-1"]))
    allbest = max(keys, key=lambda k: score(k, courses))
    return loco, allbest


def main():
    R = {}
    for c in COURSES:
        try:
            R[c] = course_metrics(c)
        except (SystemExit, FileNotFoundError, KeyError) as e:
            log(f"[{c}] skipped: {e}")
    courses = list(R)
    loco, allbest = select(R, courses)
    keys = list(next(iter(R.values())))
    pooled = {k: agg([p for c in courses for p in R[c][k]]) for k in keys}
    cv = agg([p for c in courses for p in R[c][loco[c]["chosen"]]])
    prod = pooled["2.5_-1"]
    res = dict(courses=courses, hags=HAGS, ks=KS, loco=loco, chosen_on_all=allbest, cv=cv, product=prod,
               pooled=pooled, per_course={c: {k: agg(R[c][k]) for k in keys} for c in courses})
    json.dump(res, open(OUT_JSON, "w"), indent=1)
    L = ["# Tree edge vs the hand tree lines (leave-one-course-out)", "",
         "Generated by `course_data/vision_any/v2_treeline_handcal.py` (see its docstring). Inside the hand landing "
         f"corridors of {len(courses)} hand-truth courses: hand-traced trees vs the trees the product sees "
         "(lidar canopy HAG > h m, clumps >= 100 m2, buffered k m; minus the package's fairway / green / water / sand / "
         "rough painted over trees). Bias = (extra - missing) / hand tree-edge length, yds (+ = auto reaches further). "
         "The hand maps are the only georeferenced tree labels, so the setting is chosen leave-one-course-out "
         "(pooled IoU on the other courses).", "",
         "## Held-out (leave one course out)", "",
         "| test course | setting chosen on the others (HAG_k) | test IoU | test bias yds | test missing / extra sq yds (median per corridor) | product 2.5_-1: IoU | bias | missing / extra |",
         "|---|---|---|---|---|---|---|---|"]
    for c in courses:
        t, p = loco[c]["test"], loco[c]["product"]
        L.append(f"| {c} | `{loco[c]['chosen']}` | {t['iou']} | {t['bias_yd']:+.2f} | {t['med_missing']:.0f} / {t['med_extra']:.0f} | "
                 f"{p['iou']} | {p['bias_yd']:+.2f} | {p['med_missing']:.0f} / {p['med_extra']:.0f} |")
    L += ["", f"**Cross-validated (pooled over the held-out courses): IoU {cv['iou']}, bias {cv['bias_yd']:+.2f} yds, "
          f"median per corridor {cv['med_missing']:.0f} sq yds missing / {cv['med_extra']:.0f} extra** vs the product "
          f"setting 2.5_-1: IoU {prod['iou']}, bias {prod['bias_yd']:+.2f} yds, {prod['med_missing']:.0f} / "
          f"{prod['med_extra']:.0f}. Chosen on all courses: `{allbest}`.", "",
          NOTE, "",
          "## Every setting (pooled over all courses, in-sample)", "",
          "| HAG_k | IoU | bias yds | missing / extra sq yds (sum) | median per corridor missing / extra |", "|---|---|---|---|---|"]
    for k in sorted(keys, key=lambda k: -(pooled[k]["iou"] or 0)):
        a = pooled[k]
        L.append(f"| `{k}` | {a['iou']} | {a['bias_yd']:+.2f} | {a['missing']} / {a['extra']} | {a['med_missing']:.0f} / {a['med_extra']:.0f} |")
    open(OUT_MD, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:20 + len(courses)]))


if __name__ == "__main__":
    main()
