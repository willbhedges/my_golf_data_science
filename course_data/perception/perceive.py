"""Perceive one course from its stack: blind detection -> course_scene/1 (+ evaluation + training tables).

    python course_data/perception/perceive.py <stack dir> [--out DIR] [--tables DIR] [--no-eval] [--models DIR]

Writes <out>/scene.json, scene.geojson, eval.json (when the stack has OSM labels). With --tables, the
feature rows the object models train on (greens, tee boxes, complexes, parking, clubhouse candidates) and a
sample of cart-path pixels, each labelled from OSM (train.py reads them).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detect as DT  # noqa: E402
import features as F  # noqa: E402
import paths as PT  # noqa: E402
import scene as SC  # noqa: E402
import stack as S  # noqa: E402

MODELS = os.path.join(HERE, "models")
PATH_SWEEP = (0.3, 0.5, 0.7, 0.85, 0.95)


def load_models(d=MODELS):
    out = {}
    for p in glob.glob(os.path.join(d, "*.pkl")):
        try:
            out[os.path.basename(p)[:-4]] = pickle.load(open(p, "rb"))
        except Exception as e:                                   # noqa: BLE001
            print("model load failed", p, repr(e)[:200])
    mid = None
    mp = os.path.join(d, "models.json")
    if os.path.exists(mp):
        mid = json.load(open(mp)).get("id")
    return out, mid


def run(st, models=None, log=print):
    models = models or {}
    t0 = time.time()
    L = F.Layers(st)
    D = dict(warnings=[], seconds={})
    if not L["lidar"]:
        D["warnings"].append("no lidar HAG: trees / buildings from imagery only, no tee pads")
    tm = time.time()

    def lap(k):
        nonlocal tm
        D["seconds"][k] = round(time.time() - tm, 1)
        tm = time.time()
    D["greens"], green_lab = DT.greens(st, L, models)
    lap("greens")
    D["boxes"], box_lab = DT.tee_boxes(st, L, green_lab, models)
    D["complexes"] = DT.tee_complexes(st, D["boxes"], box_lab, D["greens"])
    lap("tees")
    if models.get("tee_complex"):
        md = models["tee_complex"]
        rows = [DT.complex_features(c, D["greens"], D["complexes"]) for c in D["complexes"]]
        if rows:
            pr, cl = DT._apply(md["clf"], rows, md["features"], md.get("thr"))
            for c, row in zip(D["complexes"], pr):
                c["p"] = float(row[cl.index(1)])
    D["fairways"], D["fairway_lab"] = DT.fairways(st, L)
    lap("fairways")
    D["bunkers"], D["bunker_lab"] = DT.bunkers(st, L)
    D["water"], D["water_lab"] = DT.water(st, L)
    D["trees"], _ = DT.trees(st, L)
    lap("bunkers_water_trees")
    D["graph"], D["path_prob"], D["road_prob"] = PT.build_graph(L, models.get("path_px"))
    lap("cart_paths")
    D["buildings"], D["building_lab"] = DT.buildings(st, L)
    D["parking"], D["parking_lab"] = DT.parking(st, L, D["building_lab"], D["path_prob"], models)
    ch, D["ch_rows"] = DT.clubhouse(st, D["buildings"], D["parking"], D["greens"], D["complexes"], D["graph"], models)
    D["clubhouse"] = ch
    DT.classify_greens(st, D["greens"], D["complexes"], ch, models, D["parking"], D["buildings"])
    rng = DT.driving_range(st, L, D["complexes"], [g for g in D["greens"] if g["p"] >= 0.5], ch["xy"] if ch else None,
                           D["fairways"])
    D["range"] = rng
    if rng:
        for c in D["complexes"]:
            if c["id"] == rng["complex"]:
                c["p_range_tee"] = rng["p"]
    z = L["dtm"]
    for c in D["complexes"]:
        r, cc = st.xy_to_rc(*c["xy"])
        r, cc = int(np.clip(round(float(r)), 0, st.H - 1)), int(np.clip(round(float(cc)), 0, st.W - 1))
        c["elev"] = float(z[r, cc]) if np.isfinite(z[r, cc]) else None
    lap("buildings_parking_clubhouse_range")
    D["seconds"]["total"] = round(time.time() - t0, 1)
    return L, D


def tables(st, L, D, T, out_dir, rng=None):
    """Labelled feature rows for train.py (OSM labels; only where OSM mapping is complete enough)."""
    import truth as TR  # noqa: F401
    rng = rng or np.random.default_rng(0)
    os.makedirs(out_dir, exist_ok=True)
    meta = dict(slug=st.meta.get("slug"), state=(st.meta.get("course") or {}).get("state") or st.meta.get("state"),
                mapped_holes=T.mapped_holes, n_tees=len(T.tees), n_greens=len(T.greens), lidar=bool(L["lidar"]),
                cart_km=round(T.cart_length_m() / 1000, 3), n_parking=len(T.parking) + len(T.parking_pts),
                clubhouse=T.clubhouse is not None)
    rows = dict(meta=meta)
    nh = T.mapped_holes
    if nh >= 9 and len(T.greens) >= 0.8 * nh:
        rows["green"] = [dict(g["feat"], y={None: 0, "hole": 1, "practice": 2, "unknown": 1}[g.get("_truth")]) for g in D["greens"]]
    if nh >= 9 and len(T.tees) >= 1.5 * nh:
        rows["tee_box"] = [dict(b["feat"], y=int(bool(b.get("_truth")))) for b in D["boxes"]]
        rows["tee_complex"] = [dict(DT.complex_features(c, D["greens"], D["complexes"]), y=int(bool(c.get("_truth"))))
                               for c in D["complexes"]]
    if T.parking or T.parking_pts:
        rows["parking"] = [dict(p["feat"], y=int(bool(p.get("_truth")))) for p in D["parking"] if p.get("_truth") is not None]
    if T.clubhouse is not None and D.get("ch_rows"):
        dd = [np.hypot(r["b"]["xy"][0] - T.clubhouse[0], r["b"]["xy"][1] - T.clubhouse[1]) for r in D["ch_rows"]]
        k = int(np.argmin(dd))
        if dd[k] <= 40:
            rows["clubhouse"] = [dict(r["feat"], y=int(i == k)) for i, r in enumerate(D["ch_rows"])]
    if nh >= 9 and D.get("relations"):
        starts = {h["ref"]: h["start"] for h in T.holes if h["ref"] is not None}
        gref = {g["id"]: g.get("_truth_ref") for g in D["greens"]}
        cx = {c["id"]: c for c in D["complexes"]}
        keep = [r for r in D["relations"] if gref.get(r["green"]) is not None and gref[r["green"]] + 1 in starts]
        feats = SC.edge_features(D["relations"], D["greens"], D["complexes"])
        fmap = {(r["green"], r["tee"]): f for r, f in zip(D["relations"], feats)}
        er = []
        for r in keep:
            s0 = starts[gref[r["green"]] + 1]
            d = min(np.hypot(b["xy"][0] - s0[0], b["xy"][1] - s0[1]) for b in cx[r["tee"]]["boxes"])
            er.append(dict(fmap[(r["green"], r["tee"])], y=int(d <= 30.0), g=r["green"]))
        rows["edge"] = er
    json.dump(rows, open(os.path.join(out_dir, "objects.json"), "w"), default=lambda x: None if x is None else float(x))
    # cart-path pixels: only on courses whose cart paths are mapped densely
    if T.cart_length_m() >= 1500.0 * max(nh, 9) / 18.0:
        X = F.path_feature_stack(L)
        region = T.in_boundary_mask(pad_m=30)
        pos = T.line_raster(T.cart_paths, 2.0) & region
        road = T.line_raster(T.roads, 5.0) & ~pos
        anyway = T.line_raster(T.cart_paths + T.roads, 14.0)
        neg = region & ~anyway & L["valid"]
        idx, ys = [], []
        for m, y, k in ((pos, 1, 12000), (road, 2, 6000), (neg, 0, 30000)):
            ii = np.flatnonzero(m.ravel())
            if len(ii) > k:
                ii = rng.choice(ii, k, replace=False)
            idx.append(ii)
            ys.append(np.full(len(ii), y, np.int8))
        # hard negatives: paved-looking pixels away from any mapped way (roofs, parking, sand)
        hard = np.flatnonzero((neg & (L["paved"] | (st.seg("bunker") > 0.5))).ravel())
        if len(hard) > 8000:
            hard = rng.choice(hard, 8000, replace=False)
        idx.append(hard)
        ys.append(np.zeros(len(hard), np.int8))
        ii = np.concatenate(idx)
        Xs = X.reshape(X.shape[0], -1)[:, ii].T.astype(np.float32)
        np.savez_compressed(os.path.join(out_dir, "path_px.npz"), X=Xs, y=np.concatenate(ys), features=np.array(F.PATH_FEATURES))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stack")
    ap.add_argument("--out")
    ap.add_argument("--tables")
    ap.add_argument("--no-eval", action="store_true")
    ap.add_argument("--models", default=MODELS)
    ap.add_argument("--mode", default="blind")
    a = ap.parse_args()
    st = S.load(a.stack)
    models, mid = load_models(a.models)
    print("models:", sorted(models), mid)
    L, D = run(st, models)
    out = a.out or os.path.join(HERE, "scenes", st.meta.get("slug", "course"))
    os.makedirs(out, exist_ok=True)
    sc = SC.build_scene(st, L, D, mode=a.mode, models_id=mid or "rules-v1", models=models)
    D["relations"] = sc["relations"]["green_to_tee"]
    json.dump(sc, open(os.path.join(out, "scene.json"), "w"), separators=(",", ":"))
    json.dump(SC.to_geojson(sc), open(os.path.join(out, "scene.geojson"), "w"), separators=(",", ":"))
    print(json.dumps(sc["summary"]), D["seconds"])
    if not a.no_eval and st.labels:
        import evaluate as EV
        import truth as TR
        T = TR.Truth(st)
        ev = EV.evaluate(st, L, D, T)
        ev["seconds"] = D["seconds"]
        ev["models"] = mid or "rules-v1"
        ev["lidar"] = bool(L["lidar"])
        ev["summary"] = sc["summary"]
        if models.get("path_px"):                               # threshold sweep (the report picks it on train states)
            region = T.in_boundary_mask(pad_m=40)
            ev["path_sweep"] = {}
            for thr in PATH_SWEEP:
                G = PT.graph_from_prob(L, D["path_prob"], D["road_prob"], thr)
                e = EV.eval_paths(st, T, G, region)
                ev["path_sweep"][str(thr)] = {k: e[k] for k in ("pred_km", "true_km", "length_precision", "length_recall",
                                                                "connectivity_acc", "transitions_osm_connected", "eligible")}
        json.dump(ev, open(os.path.join(out, "eval.json"), "w"), indent=1, default=float)
        print(json.dumps({k: ev[k] for k in ("greens_hole", "tee_complexes", "cart_paths", "clubhouse")}, default=float)[:1500])
        if a.tables:
            tables(st, L, D, T, a.tables)


if __name__ == "__main__":
    main()
