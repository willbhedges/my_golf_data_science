"""Validate the any-course layers against a hand-traced map (Spirit Hollow: NAIP-registered course.py;
Mozingo: tee_strategy.HOLES registered by register_mozingo.py).

  python3 course_data/vision_any/validate.py --slug spirit_hollow [--no-strategy] [--n 6000]

Writes course_data/vision_any/<slug>/validation.json and validation.md:
  * landing-zone IoU / precision / recall per hole for trees (recovery), native and water: the raw layer and
    the composed lie map (OSM + vision), pooled and mean over holes; tree threshold sensitivity (2.5 / 4 m)
  * strategy impact (evaluate.strategy_impact): best club and aim (Driver / 2-wood / 4-wood) on the hand
    map vs the hand map with its trees + native replaced by the vision layer, and vs an OSM-only baseline
    (the hand map with trees + native removed), and the EV cost on the hand map of following the vision pick.
No hand-traced label is used to build the layers (the product path); the hand map is only the reference.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evaluate as E                                   # noqa: E402
import layers as L                                     # noqa: E402
import truth as TR                                     # noqa: E402


def _r(x, n=2):
    return None if x is None else round(float(x), n)


def run(slug, R=None, strategy=True, n=6000):
    import run_any as RA
    from shapely.geometry import shape
    R = R or RA.compute(slug)
    S = R["S"]
    T = TR.for_course(slug, S)
    g = E.compose(R["M"], R["trees"], R["native"], R["water"])
    rep = dict(slug=slug, truth=T.name, holes_evaluated=[str(k) for k in T.keys], trees_how=R["trees_how"],
               native_info={k: v for k, v in R["native_info"].items() if k != "features"})
    rep["landing"] = E.evaluate(S, T, dict(recovery=R["trees"], native=R["native"], water=R["water"]), g)
    # tree threshold sensitivity (raw canopy only)
    sens = {}
    for thr in (2.5, 4.0):
        tr, _, _ = L.tree_mask(S, R["M"], hag_min=thr)
        e = E.evaluate(S, T, dict(recovery=tr, native=R["native"], water=R["water"]),
                       E.compose(R["M"], tr, R["native"], R["water"]))
        sens[str(thr)] = dict(pooled_iou=_r(e["pooled"]["recovery"]["iou"], 3), mean_iou=_r(e["mean_iou"]["recovery"], 3),
                              raw_pooled_iou=_r(e["pooled"]["recovery_raw"]["iou"], 3))
    rep["tree_threshold"] = sens
    # OSM-only baseline in the same lie map (no vision): what acceptance saw before
    none = np.zeros_like(R["trees"])
    b = E.evaluate(S, T, dict(recovery=none, native=none, water=R["M"]["water"]),
                   E.compose(R["M"], none, none, R["M"]["water"]))
    rep["baseline_osm_only"] = dict(pooled={c: _r(b["pooled"][c]["iou"], 3) for c in ("recovery", "native", "water", "penal")})
    if strategy:
        fc = RA.build(slug, R=R, write=False)
        polys = {}
        for f in fc["features"]:
            polys.setdefault(f["properties"]["lie"], []).append(shape(f["geometry"]))
        print("strategy: hand map vs hand map with vision trees + native", flush=True)
        rep["strategy_vision"] = E.strategy_impact(T, polys, n=n)
        print("strategy: hand map vs OSM-only (trees + native removed)", flush=True)
        rep["strategy_osm_only"] = E.strategy_impact(T, {}, n=n)
    d = os.path.join(HERE, slug)
    os.makedirs(d, exist_ok=True)
    json.dump(rep, open(os.path.join(d, "validation.json"), "w"), indent=1, default=float)
    write_md(rep, os.path.join(d, "validation.md"))
    print(open(os.path.join(d, "validation.md")).read())
    return rep


def write_md(rep, path):
    lz = rep["landing"]
    P = lz["pooled"]
    L_ = [f"# vision_any validation: {rep['slug']} vs the hand-traced map", "",
          f"Trees: {rep['trees_how']}. Native: NAIP self-supervised from OSM (seeds {rep['native_info'].get('seed_px')} px). "
          "No hand-traced label was used to build the layers.", "",
          "Landing zone = 220-340 yds along the traced tee line, +/-45 yds, 5-yd grid (425 points per hole), "
          "traced frame, georeferenced by the registration. `composed` = OSM + vision lie map (what the model sees); "
          "`raw` = the layer alone.", "",
          "| class | pooled IoU (composed) | precision | recall | mean IoU over holes | raw pooled IoU | OSM-only pooled IoU |",
          "|---|---|---|---|---|---|---|"]
    for c in ("recovery", "native", "water", "penal"):
        raw = P.get(c + "_raw", {}).get("iou")
        L_.append(f"| {c} | {_r(P[c]['iou'])} | {_r(P[c]['prec'])} | {_r(P[c]['rec'])} | {_r(lz['mean_iou'][c])} | "
                  f"{_r(raw) if raw is not None else '-'} | {rep['baseline_osm_only']['pooled'].get(c)} |")
    for c in ("recovery", "native"):
        t5 = P.get(c + "_tol5") or {}
        L_.append(f"| {c} within 5 yds | - | {_r(t5.get('prec'))} | {_r(t5.get('rec'))} | - | - | - |")
    L_ += ["", "`penal` = any of trees / native / water (is the shot in trouble at all). `within 5 yds`: a point counts "
           "when the other map has the class within one 5-yd grid step (edge offsets from registration and canopy-vs-"
           "trunk tracing).", "",
           "Tree height threshold (pooled IoU composed / raw): " + "; ".join(
               f"{k} m: {v['pooled_iou']} / {v['raw_pooled_iou']}" for k, v in rep["tree_threshold"].items()), "",
           "| hole | registration | trees IoU | trees P / R | native IoU | native P / R | water IoU | penal IoU | agree |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in lz["holes"]:
        reg = r["reg"] or {}
        rs = ", ".join(f"{k} {v}" for k, v in reg.items() if k != "method" and v is not None)
        L_.append(f"| {r['hole']} | {reg.get('method', '')} {rs} | {_r(r['recovery']['iou'])} | "
                  f"{_r(r['recovery']['prec'])} / {_r(r['recovery']['rec'])} | {_r(r['native']['iou'])} | "
                  f"{_r(r['native']['prec'])} / {_r(r['native']['rec'])} | {_r(r['water']['iou'])} | "
                  f"{_r(r['penal']['iou'])} | {_r(r['agree'])} |")
    for key, title in (("strategy_vision", "hand map vs hand map with the vision trees + native"),
                       ("strategy_osm_only", "hand map vs OSM-only (hand map with trees + native removed)")):
        st = rep.get(key)
        if not st:
            continue
        L_ += ["", f"## Strategy: {title}", "",
               f"Same best club (Driver / 2-wood / 4-wood) on **{st['same_club']:.0%}** of {len(st['holes'])} tee shots; "
               f"median aim change {st['median_aim_change_yd']:.1f} yds; mean EV cost on the hand map of following "
               f"the alternative pick {st['mean_ev_loss']:+.3f} strokes.", "",
               "| hole | club hand | club alt | aim hand (D/2w/4w) | aim alt (D/2w/4w) | EV cost |", "|---|---|---|---|---|---|"]
        for r in st["holes"]:
            L_.append(f"| {r['hole']} | {r['club_hand']} | {r['club_vision']} | "
                      + "/".join(f"{r[c]['aim_hand']:+.1f}" for c in E.WOODS) + " | "
                      + "/".join(f"{r[c]['aim_vision']:+.1f}" for c in E.WOODS) + f" | {r['ev_loss_on_hand_map']:+.3f} |")
    open(path, "w").write("\n".join(L_) + "\n")


SWEEP = [dict(seed_z=z, p_min=p, an_floor=f, seed_dist=d)
         for z in (3.0, 4.5) for p in (0.7, 0.85) for f in (None, 1.0, 2.0) for d in (25.0,)]


def sweep(slug, R=None):
    """Native-parameter sweep (landing-zone IoU only). Used to choose the parameters on ONE course (the dev
    course) and report the other as held out."""
    import native as N
    import run_any as RA
    R = R or RA.compute(slug)
    S = R["S"]
    T = TR.for_course(slug, S)
    rows = []
    for cfg in SWEEP:
        nat, p, info = N.predict(S, R["M"], R["Ly"], R["trees"], R["water"], R["X"], R["names"], **cfg)
        nat &= ~R["water"]
        e = E.evaluate(S, T, dict(recovery=R["trees"], native=nat, water=R["water"]),
                       E.compose(R["M"], R["trees"], nat, R["water"]))
        row = dict(cfg, native_iou=_r(e["pooled"]["native"]["iou"], 3), native_prec=_r(e["pooled"]["native"]["prec"], 3),
                   native_rec=_r(e["pooled"]["native"]["rec"], 3), penal_iou=_r(e["pooled"]["penal"]["iou"], 3),
                   agree=_r(np.mean([h["agree"] for h in e["holes"]]), 3), native_frac=_r(info["native_frac_course"], 3))
        rows.append(row)
        print(row, flush=True)
    d = os.path.join(HERE, slug)
    json.dump(rows, open(os.path.join(d, "sweep.json"), "w"), indent=1)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--no-strategy", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--n", type=int, default=6000)
    a = ap.parse_args()
    if a.sweep:
        sweep(a.slug)
    else:
        run(a.slug, strategy=not a.no_strategy, n=a.n)


if __name__ == "__main__":
    main()
