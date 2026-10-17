"""Calibrate and evaluate OB inference on Spirit Hollow's hand-checked OB (leave-one-hole-out), and measure the
decision impact on the product plan.

  python3 course_data/ob/evaluate.py calibrate [--small]   # -> params.json, eval.json, eval.md (offline, light)
  python3 course_data/ob/evaluate.py decisions             # -> decisions.json, appended to eval.md (Actions: runs
                                                           #    product/decide.py quick for 4 OB variants)
  python3 course_data/ob/evaluate.py apply <slug> ...      # -> course_data/ob/<slug>/ob.geojson + summary.json

Truth: spirit_hollow/hand_zones_ll.json (spirit_hollow/course.py in WGS84). A grid cell is OB when the last hand zone
containing it is 'ob' (tee_strategy.lie_at order) and it lies inside the screenshot footprint.
Grid: the landing corridor of every hand tee shot, 190-335 yds along the hand tee line, +/-55 yds, 5-yd step.
Prediction: union of the OB components (infer.Regions) within CORRIDOR yds of the package hole's line of play,
minus the package hole's fairway / green / water / sand (OB never overrides them).
Score: IoU of OB cells, pooled over holes (sum of intersections / sum of unions), and per hole.
Calibration: grid search over the component parameters (each component's cell mask is computed once per
parameter value, combinations are ORs of masks). Leave-one-hole-out: for each hand hole, parameters fitted on
the other holes predict it; the LOHO pooled IoU is the honest number. params.json holds the all-holes fit.
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, HERE)
import infer  # noqa: E402

HAND = os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")
PKG = os.path.join(CD, "packages", "spirit_hollow", "package.json")
GOLD = os.path.join(ROOT, "spirit_hollow", "output", "final_decision.json")
ALONG = (190, 335)
LAT = 55
STEP = 5

GRID_FULL = dict(
    house=[None] + [(d, c) for d in (0, 10, 20, 30, 40) for c in (0, 30)],
    road=[None] + [(m, ins) for m in (0, 5, 10, 20) for ins in (True, False)],
    res=[None, 0, 10, 20],
    out=[None] + [(o, dv, sr) for o in (-20, -15, -12, -10, -8, -5, 0, 10, 20) for dv in (None, 30, 45, 60, 80, 100)
                  for sr in ("osm", "parcels")],
    parcel=[None] + [(o, md) for o in (-10, -5, 0, 5, 10, 20) for md in ("houses", "all")],
    geom=[None, True])                    # keep the geometry stage's OSM OB too (apply_ob mode 'add')
GRID_SMALL = dict(house=[None, (10, 20), (25, 20)], road=[None, (5, True), (5, False)], res=[None, 0],
                  out=[None, (0, None, "osm"), (-10, 60, "osm"), (-8, None, "parcels")], parcel=[None, (0, "houses")],
                  geom=[None, True])


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def ref_of(key):
    return str(key).rstrip("BF") if str(key)[-1:] in "BF" and str(key)[:-1].isdigit() else str(key)


# ----------------------------------------------------------------------------- truth grid
def hand_grid(hand, P):
    """-> list of dict(key, ref, ll [n,2], xy (course metric) [n,2], truth bool[n])."""
    from shapely import contains_xy
    from shapely.geometry import Polygon
    YardFrame = infer.load_module(os.path.join(CD, "vision_any", "gapfill.py"), "ob_gapfill").YardFrame
    out = []
    xs = np.arange(-LAT, LAT + 0.1, STEP)
    ys = np.arange(ALONG[0], ALONG[1] + 0.1, STEP)
    X, Y = np.meshgrid(xs, -ys)
    X, Y = X.ravel(), Y.ravel()
    for k, h in hand["holes"].items():
        fr = YardFrame(h["tee_ll"], h["dot270_ll"])
        fp = Polygon(fr.ll_to_xy(h["footprint_ll"]))
        keep = contains_xy(fp if fp.is_valid else fp.buffer(0), X, Y)
        x, y = X[keep], Y[keep]
        lie = np.array(["rough"] * len(x), dtype=object)
        for z in h["zones"]:
            p = Polygon(fr.ll_to_xy(z["poly_ll"]))
            lie[contains_xy(p if p.is_valid else p.buffer(0), x, y)] = z["lie"]
        ll = fr.xy_to_ll(np.c_[x, y])
        out.append(dict(key=k, ref=ref_of(k), ll=ll, xy=P.xy(ll), truth=(lie == "ob")))
    return out


def hole_masks(cells, pkg, R):
    """Per hand hole: allowed = inside the package hole's corridor and not protected."""
    from shapely import contains_xy
    for c in cells:
        h = pkg["holes"].get(c["ref"])
        if h is None:
            c["allowed"] = np.zeros(len(c["truth"]), bool)
            continue
        cor = infer.corridor_m(h, R.P)
        prot = infer.protect_m(h, R.P)
        a = contains_xy(cor, c["xy"][:, 0], c["xy"][:, 1]) if cor is not None else np.zeros(len(c["truth"]), bool)
        if prot is not None:
            a &= ~contains_xy(prot, c["xy"][:, 0], c["xy"][:, 1])
        c["allowed"] = a


def comp_region(R, kind, v):
    if v is None:
        return None
    if kind == "house":
        return R.house(v[0], v[1], unlotted=R.lots is not None)
    if kind == "road":
        return R.road(v[0], v[1])
    if kind == "res":
        return R.residential(v)
    if kind == "out":
        return R.outside(v[0], v[1], v[2])
    if kind == "parcel":
        return R.parcel(v[0], v[1]) if R.private else None
    raise KeyError(kind)


def to_params(sel):
    h, r, s, o, p = (sel.get(k) for k in ("house", "road", "res", "out", "parcel"))
    return dict(mode="add" if sel.get("geom") else "replace",
                house_d=h[0] if h else None, house_close=h[1] if h else 0.0,
                road_margin=r[0] if r else None, road_inside=r[1] if r else True,
                res_off=s, out_off=o[0] if o else None, out_dev=o[1] if o else None, out_src=o[2] if o else "osm",
                parcel_off=p[0] if p else None, parcel_mode=p[1] if p else "houses")


def masks_for(cells, R, grid, geom=None):
    from shapely import contains_xy
    allxy = np.concatenate([c["xy"] for c in cells])
    allow = np.concatenate([c["allowed"] for c in cells])
    M = {}
    for kind, vals in grid.items():
        M[kind] = []
        for v in vals:
            if kind == "geom":
                M[kind].append(np.concatenate(geom) if v and geom is not None else np.zeros(len(allxy), bool))
                continue
            g = comp_region(R, kind, v)
            m = np.zeros(len(allxy), bool) if g is None or g.is_empty else contains_xy(g, allxy[:, 0], allxy[:, 1])
            M[kind].append(m & allow)
    return M


def search(cells, M, grid):
    """-> combos list, I [n_combo, n_hole], U [n_combo, n_hole]."""
    truth = np.concatenate([c["truth"] for c in cells])
    starts = np.cumsum([0] + [len(c["truth"]) for c in cells])[:-1]
    kinds = list(grid)
    idx = list(itertools.product(*[range(len(grid[k])) for k in kinds]))
    I = np.zeros((len(idx), len(cells)), np.int32)
    U = np.zeros_like(I)
    for n, ii in enumerate(idx):
        pred = M[kinds[0]][ii[0]].copy()
        for k, i in zip(kinds[1:], ii[1:]):
            pred |= M[k][i]
        I[n] = np.add.reduceat(pred & truth, starts)
        U[n] = np.add.reduceat(pred | truth, starts)
    return [{k: grid[k][i] for k, i in zip(kinds, ii)} for ii in idx], I, U


def complexity(sel):
    return sum(v is not None for v in sel.values())


def best(combos, I, U, holes_mask):
    i = I[:, holes_mask].sum(1)
    u = U[:, holes_mask].sum(1)
    iou = np.where(u > 0, i / np.maximum(u, 1), 1.0)
    top = iou.max()
    cand = np.flatnonzero(iou >= top - 1e-9)
    j = min(cand, key=lambda c: (complexity(combos[c]), -i[c], c))    # simplest of the ties
    return j, float(top)


def pooled(i, u):
    return float(i.sum() / u.sum()) if u.sum() else None


def baseline_masks(cells, pkg, R, which):
    """Prediction from the package's own zones (which = 'geometry': current OSM OB zones)."""
    from shapely import contains_xy
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    out = []
    for c in cells:
        h = pkg["holes"].get(c["ref"]) or {}
        gs = [infer._valid(Polygon(R.P.xy(z["poly"]))) for z in h.get("zones_ll") or []
              if z.get("lie") in ("ob", "ob_boundary") and infer.is_geometry_ob(z)]
        g = unary_union(gs) if gs else None
        m = contains_xy(g, c["xy"][:, 0], c["xy"][:, 1]) if g is not None else np.zeros(len(c["truth"]), bool)
        out.append(m & c["allowed"] if which == "geometry_clipped" else m)
    return out


def score(cells, preds):
    rows = []
    for c, p in zip(cells, preds):
        t = c["truth"]
        rows.append(dict(key=c["key"], truth=int(t.sum()), pred=int(p.sum()), inter=int((p & t).sum()),
                         union=int((p | t).sum())))
    I = np.array([r["inter"] for r in rows])
    U = np.array([r["union"] for r in rows])
    return rows, pooled(I, U)


def evidence_precision(cells, R, prm):
    """Precision of each evidence's exclusive cells (priority order), smoothed; n < 8 cells -> default."""
    from shapely import contains_xy
    allxy = np.concatenate([c["xy"] for c in cells])
    allow = np.concatenate([c["allowed"] for c in cells])
    truth = np.concatenate([c["truth"] for c in cells])
    taken = np.zeros(len(allxy), bool)
    out = {}
    for ev, g in R.components(prm):
        m = contains_xy(g, allxy[:, 0], allxy[:, 1]) & allow & ~taken
        taken |= m
        n, tp = int(m.sum()), int((m & truth).sum())
        out[ev] = dict(n=n, tp=tp, p=round((tp + 1) / (n + 2), 3) if n >= 8 else None)
    return out


def calibrate(small=False):
    t0 = time.time()
    hand = json.load(open(HAND))
    pkg = json.load(open(PKG))
    L = infer.load_layers(pkg)
    R = infer.Regions(L)
    cells = hand_grid(hand, R.P)
    hole_masks(cells, pkg, R)
    grid = GRID_SMALL if small else GRID_FULL
    if not R.private:
        grid = dict(grid, parcel=[None])
    if R.course_parcels is None:
        grid = dict(grid, out=[v for v in grid["out"] if v is None or v[2] == "osm"])
    if not R.res or R.res.is_empty if R.res is not None else True:
        grid = dict(grid, res=[None])
    M = masks_for(cells, R, grid, baseline_masks(cells, pkg, R, "geometry"))
    combos, I, U = search(cells, M, grid)
    log(f"  {len(combos)} combinations x {len(cells)} holes in {time.time() - t0:.0f}s")
    keys = [c["key"] for c in cells]
    pos = [i for i, c in enumerate(cells) if c["truth"].any()]
    # all-holes fit
    j_all, iou_all = best(combos, I, U, np.ones(len(cells), bool))
    # LOHO
    loho_rows, li, lu = [], [], []
    for h in range(len(cells)):
        m = np.ones(len(cells), bool)
        m[h] = False
        j, _ = best(combos, I, U, m)
        li.append(I[j, h]), lu.append(U[j, h])
        loho_rows.append(dict(key=keys[h], truth=int(cells[h]["truth"].sum()), inter=int(I[j, h]), union=int(U[j, h]),
                              pred=int(U[j, h] - cells[h]["truth"].sum() + I[j, h]),
                              iou=round(I[j, h] / U[j, h], 3) if U[j, h] else None, params=to_params(combos[j])))
    loho = pooled(np.array(li), np.array(lu))
    # the same LOHO picks scored against the hand OB the corridor rule can reach (within CORRIDOR yds of the
    # package line of play, not under fairway/green/water/sand): the rule's own ceiling is 1.0 there
    ci, cu, reach = [], [], 0
    for h, r in enumerate(loho_rows):
        sel_h = next(c for c in combos if to_params(c) == r["params"])
        pred = np.zeros(len(cells[h]["truth"]), bool)
        off = sum(len(c["truth"]) for c in cells[:h])
        for k, v in sel_h.items():
            pred |= M[k][grid[k].index(v)][off:off + len(cells[h]["truth"])]
        t = cells[h]["truth"] & cells[h]["allowed"]
        reach += int(t.sum())
        ci.append(int((pred & t).sum())), cu.append(int((pred | t).sum()))
        r["inter_reach"], r["union_reach"], r["truth_reach"] = ci[-1], cu[-1], int(t.sum())
    loho_reach = pooled(np.array(ci), np.array(cu))
    # baselines
    base_rows, base_iou = score(cells, baseline_masks(cells, pkg, R, "geometry"))
    basec_rows, basec_iou = score(cells, baseline_masks(cells, pkg, R, "geometry_clipped"))
    # single-source ablations at the all-holes fit
    sel = combos[j_all]
    abl = {}
    for k in grid:
        if sel[k] is None:
            continue
        alt = dict(sel, **{k: None})
        n = next(i for i, c in enumerate(combos) if c == alt)
        abl[f"without {k}"] = pooled(I[n], U[n])
    only = {}
    for k in grid:
        if sel[k] is None:
            continue
        alt = {kk: (sel[kk] if kk == k else None) for kk in grid}
        n = next(i for i, c in enumerate(combos) if c == alt)
        only[f"{k} only"] = pooled(I[n], U[n])
    prm = to_params(sel)
    prec = evidence_precision(cells, R, prm)
    if prm["mode"] == "add":
        g = np.concatenate(baseline_masks(cells, pkg, R, "geometry"))
        t = np.concatenate([c["truth"] for c in cells])
        prec["geometry"] = dict(n=int(g.sum()), tp=int((g & t).sum()), p=None)
    fit_rows = [dict(key=keys[h], truth=int(cells[h]["truth"].sum()), inter=int(I[j_all, h]), union=int(U[j_all, h]),
                     iou=round(I[j_all, h] / U[j_all, h], 3) if U[j_all, h] else None) for h in range(len(cells))]
    res = dict(schema="ob_eval/1", built=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               layers=L["have"], n_houses=len(R.houses), n_private_parcels=len(R.private),
               n_roads=len(R.roads), grid=dict(along=ALONG, lat=LAT, step=STEP, corridor=infer.CORRIDOR),
               holes_with_hand_ob=[keys[i] for i in pos], n_combos=len(combos),
               fit=dict(params=prm, iou_pooled=round(iou_all, 3), rows=fit_rows),
               loho=dict(iou_pooled=round(loho, 3) if loho is not None else None, rows=loho_rows,
                         iou_pooled_reachable=round(loho_reach, 3) if loho_reach is not None else None,
                         truth_cells=int(sum(c["truth"].sum() for c in cells)), reachable_cells=reach),
               baseline_geometry=dict(iou_pooled=round(base_iou, 3) if base_iou is not None else None, rows=base_rows),
               baseline_geometry_in_corridor=dict(iou_pooled=round(basec_iou, 3) if basec_iou is not None else None,
                                                  rows=basec_rows),
               ablation=abl, single_source=only, evidence_precision=prec)
    json.dump(dict(params={k: v for k, v in prm.items() if k != "mode"}, mode=prm["mode"],
                   precision={k: v["p"] for k, v in prec.items() if k != "geometry"},
                   fitted=res["built"], iou_fit=res["fit"]["iou_pooled"], iou_loho=res["loho"]["iou_pooled"],
                   layers=L["have"], note="fitted by course_data/ob/evaluate.py calibrate on Spirit Hollow hand OB"),
              open(os.path.join(HERE, "params.json"), "w"), indent=1)
    json.dump(res, open(os.path.join(HERE, "eval.json"), "w"), indent=1, default=float)
    write_md(res)
    log(f"  fit IoU {iou_all:.3f}, LOHO {loho}, baseline {base_iou}; params {prm}")
    return res


def write_md(res, dec=None):
    f = lambda v: "-" if v is None else f"{v:.2f}"          # noqa: E731
    L = ["# OB inference: Spirit Hollow evaluation", "",
         f"Built {res['built']}. Layers: {', '.join(res['layers'])}; {res['n_houses']} houses (non-golf buildings), "
         f"{res['n_private_parcels']} private parcels, {res['n_roads']} public road/rail lines.",
         f"Grid: hand tee line {res['grid']['along'][0]}-{res['grid']['along'][1]} yds, +/-{res['grid']['lat']} yds, "
         f"{res['grid']['step']}-yd cells inside the screenshot footprint; prediction limited to {res['grid']['corridor']:.0f} "
         f"yds of the package line of play, minus fairway/green/water/sand. Hand OB in the corridor on: "
         f"{', '.join(res['holes_with_hand_ob'])}.", "",
         "| | pooled IoU |", "|---|---|",
         f"| geometry stage OB today (outline + OSM buildings/roads, as packaged) | {f(res['baseline_geometry']['iou_pooled'])} |",
         f"| same, clipped to the corridor rule | {f(res['baseline_geometry_in_corridor']['iou_pooled'])} |",
         f"| inferred, fitted on all holes (in-sample) | {f(res['fit']['iou_pooled'])} |",
         f"| **inferred, leave-one-hole-out** | **{f(res['loho']['iou_pooled'])}** |",
         f"| inferred, leave-one-hole-out, vs the hand OB inside the corridor rule "
         f"({res['loho'].get('reachable_cells')}/{res['loho'].get('truth_cells')} hand OB cells) | "
         f"{f(res['loho'].get('iou_pooled_reachable'))} |", "",
         f"Fitted parameters ({res['n_combos']} combinations searched): `{json.dumps(res['fit']['params'])}`", "",
         "Ablation at the fit (pooled IoU): " + ", ".join(f"{k} {f(v)}" for k, v in {**res['ablation'], **res['single_source']}.items()), "",
         "Evidence precision (exclusive cells, priority order; p used as confidence): "
         + ", ".join(f"{k} {v['tp']}/{v['n']} -> {v['p']}" for k, v in res["evidence_precision"].items()), "",
         "| hole | hand OB cells | geometry today: pred / IoU | LOHO: pred / IoU | LOHO params (house d/close, road, outside, mode) |",
         "|---|---|---|---|---|"]
    for b, l in zip(res["baseline_geometry"]["rows"], res["loho"]["rows"]):
        p = l["params"]
        bi = b["inter"] / b["union"] if b["union"] else None
        L.append(f"| {l['key']} | {l['truth']} | {b['pred']} / {f(bi)} | {l['pred']} / {f(l['iou'])} | "
                 f"{p['house_d']}/{p['house_close']}, {p['road_margin']}{'' if p['road_inside'] else ' (outside only)'}, "
                 f"{p['out_off']} {p['out_src']}{'' if p['out_dev'] is None else ' dev ' + str(p['out_dev'])}, {p['mode']} |")
    L += ["", "IoU is undefined (shown -) on holes with no OB in either; cells predicted there are false positives "
              "(the 'pred' column)."]
    if dec:
        L += ["", "## Decision impact (product decide.py quick, Black tees vs spirit_hollow/output/final_decision.json)", "",
              "| OB variant | same club | changed clubs vs no OB | expected strokes vs no OB (holes with |d| >= 0.005) |",
              "|---|---|---|---|"]
        for v, d in dec["variants"].items():
            ev = ", ".join(f"{k} {x:+.3f}" for k, x in (d.get("ev_vs_none") or {}).items() if abs(x) >= 0.005)
            L.append(f"| {v} | {d['same']}/{d['n']} | {', '.join(d['changed_vs_none']) or '-'} | {ev or '-'} |")
        L += ["", "'hand map' rows run the same quick decision on spirit_hollow/course.py itself (keys 2B/2F/9B/9F), "
                  "with and without its OB zones: the OB sensitivity of the truth map."]
        L += ["", "| hole | final_decision | " + " | ".join(dec["variants"]) + " |",
              "|---|---|" + "---|" * len(dec["variants"])]
        for k in sorted(set(dec["holes"]) | {k for d in dec["variants"].values() for k in d["picks"]},
                        key=lambda s: (len(s), s)):
            L.append(f"| {k} | {dec['gold'].get(k, '-')} | " + " | ".join(
                f"{d['picks'].get(k, '-')}" for d in dec["variants"].values()) + " |")
    open(os.path.join(HERE, "eval.md"), "w").write("\n".join(L) + "\n")


# ----------------------------------------------------------------------------- decision impact (Actions)
def _variant(pkg, kind, hand=None):
    import copy
    p = copy.deepcopy(pkg)
    if kind == "geometry":
        return p
    for h in p["holes"].values():
        h["zones_ll"] = [z for z in h.get("zones_ll") or [] if z.get("lie") not in ("ob", "ob_boundary")]
    if kind == "none":
        return p
    if kind == "inferred":
        return infer.apply_ob(pkg, use_reframe=False)
    if kind == "hand":
        for k, hh in hand["holes"].items():
            h = p["holes"].get(ref_of(k))
            if h is None or (k.endswith("B")):
                continue
            for z in hh["zones"]:
                if z["lie"] == "ob":
                    h["zones_ll"].append(dict(lie="ob", poly=z["poly_ll"], src="hand", p=1.0))
        return p
    raise KeyError(kind)


def _summ(res, gold, tees, gold_out):
    picks = {str(k): r["pick"] for k, r in res.items()}
    box = "B" if str(tees).lower() == "gold" else "F"
    same, n = 0, 0
    for k, c in picks.items():
        g = gold.get(k) if tees == "hand" else (gold.get(k) or gold.get(k + box))
        if g is None:
            continue
        gold_out.setdefault(k if tees != "hand" else k, g["pick"])
        n += 1
        same += c == g["pick"]
    return dict(picks=picks, same=same, n=n, aims={str(k): round(r["aim"], 1) for k, r in res.items()},
                ev={str(k): round(float(r["ev"]), 4) for k, r in res.items()},
                margin={str(k): round(float(r["margin"]), 4) for k, r in res.items()})


def decisions(variants=("none", "geometry", "inferred", "hand"), tees="Black"):
    reframe = infer.platform_reframe()
    sys.path.insert(0, os.path.join(CD, "product"))
    import decide
    import package as PKm                                     # product/package.py
    assert hasattr(PKm, "write_module"), PKm.__file__
    pkg = json.load(open(PKG))
    hand = json.load(open(HAND))
    gold = json.load(open(GOLD))
    tmp = os.path.join(HERE, "_work")
    os.makedirs(tmp, exist_ok=True)
    out = dict(schema="ob_decisions/1", tees=tees, variants={}, gold={})
    for v in variants:
        p = reframe(_variant(pkg, v, hand))
        path = os.path.join(tmp, f"package_{v}.json")
        json.dump(p, open(path, "w"))
        C = PKm.load(path, tees)
        mp = os.path.join(tmp, f"course_{v}.py")
        PKm.write_module(C, mp)
        mod = PKm.import_module(mp, name=f"ob_course_{v}")
        res = decide.run(mod.HOLES, "quick", log=log, n=8000)
        out["variants"][v] = _summ(res, gold, tees, out["gold"])
        log(f"  {v}: same club {out['variants'][v]['same']}/{out['variants'][v]['n']}")
    # the hand map itself (spirit_hollow/course.py, the truth the final decision was made on), with and without OB
    try:
        hm = infer.load_module(os.path.join(ROOT, "spirit_hollow", "course.py"), "ob_sh_course")
        import copy as _copy
        for v, keep in (("hand map", True), ("hand map without OB", False)):
            H = _copy.deepcopy(hm.HOLES)
            if not keep:
                for h in H.values():
                    h["zones"] = [z for z in h["zones"] if z[0] != "ob"]
            res = decide.run(H, "quick", log=log, n=8000)
            out["variants"][v] = _summ(res, gold, "hand", out["gold"])
    except Exception as e:                                     # noqa: BLE001
        log("  hand-map decisions failed:", type(e).__name__, e)
    for v, d in out["variants"].items():
        ref = out["variants"].get("hand map without OB" if v.startswith("hand map") else "none", {})
        d["changed_vs_none"] = [f"{k} {ref['picks'].get(k)}->{c}" for k, c in d["picks"].items()
                                if ref.get("picks", {}).get(k) not in (None, c)]
        d["ev_vs_none"] = {k: round(e - ref["ev"][k], 4) for k, e in d["ev"].items() if k in ref.get("ev", {})}
    out["holes"] = sorted({k for d in out["variants"].values() for k in d["picks"]}, key=lambda s: (len(s), s))
    json.dump(out, open(os.path.join(HERE, "decisions.json"), "w"), indent=1)
    res = json.load(open(os.path.join(HERE, "eval.json")))
    write_md(res, out)
    return out


# ----------------------------------------------------------------------------- per-course apply (report)
def apply_report(slug):
    pkg = json.load(open(os.path.join(CD, "packages", slug, "package.json")))
    o = infer.apply_ob(pkg, use_reframe=False)
    d = os.path.join(HERE, slug)
    os.makedirs(d, exist_ok=True)
    json.dump(infer.to_geojson(o), open(os.path.join(d, "ob.geojson"), "w"))
    holes = {k: h["ob_inferred"] for k, h in o["holes"].items()}
    before = {k: sum(1 for z in h.get("zones_ll") or [] if infer.is_geometry_ob(z)) for k, h in pkg["holes"].items()}
    s = dict(slug=slug, stage=o["stages"].get("ob"), sources=o["sources"].get("ob"), holes=holes,
             geometry_ob_polygons_before=before)
    json.dump(s, open(os.path.join(d, "summary.json"), "w"), indent=1, default=float)
    log(f"  {slug}: {s['stage']}")
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["calibrate", "decisions", "apply"])
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--small", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "calibrate":
        calibrate(a.small)
    elif a.cmd == "decisions":
        decisions()
    else:
        for s in a.slugs:
            apply_report(s)


if __name__ == "__main__":
    main()
