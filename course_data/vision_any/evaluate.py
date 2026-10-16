"""Landing-zone accuracy of the vision layers against a hand-traced map.

  python3 course_data/vision_any/evaluate.py --slug spirit_hollow [--strategy] [--out report.json]

For every traced hole with a usable registration: the landing-zone grid (220-340 yds along the traced tee
line, +/-45 yds, 5-yd step = 425 points) is laid out in the traced frame, georeferenced, and sampled on
  (a) the raw layers (tree canopy mask, native mask), and
  (b) the composed lie map (OSM fairway/green/tee/bunker/water + vision trees / native / water, later wins:
      rough < native < recovery < fairway < water < sand),
and compared with the traced lie at the same points (first_cut counts as rough). IoU per class per hole,
pooled IoU over all points, precision / recall.

--strategy: tee_strategy.best_aim for Driver / 2-wood / 4-wood on the traced hole as drawn vs the same
traced hole with its recovery + native zones REPLACED by the vision polygons (mapped into the screenshot by
the registration, clipped to the screen). Everything else (fairway, water, sand, OB, tee, green) stays as
traced, so the difference is the vision layer alone.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import truth as TR                                       # noqa: E402

LIES = ["rough", "native", "recovery", "fairway", "water", "sand"]       # composition order (later wins)
WOODS = ["Driver", "2-wood", "4-wood"]


def compose(osm_m, trees, native, water):
    """int8 lie-index grid (index into LIES)."""
    g = np.zeros(trees.shape, np.int8)
    g[native] = 1
    g[trees] = 2
    g[osm_m["fairway"] | osm_m["green"] | osm_m["tee"]] = 3
    g[water] = 4
    g[osm_m["bunker"]] = 5
    return g


def iou(a, b):
    u = np.sum(a | b)
    return None if u == 0 else float(np.sum(a & b) / u)


def prf(pred, true):
    tp = np.sum(pred & true)
    return dict(iou=iou(pred, true), prec=float(tp / pred.sum()) if pred.sum() else None,
                rec=float(tp / true.sum()) if true.sum() else None, n_true=int(true.sum()), n_pred=int(pred.sum()))


def evaluate(S, T, layers_, lie_grid, keys=None):
    """layers_: {"recovery": bool grid, "native": bool grid, "water": bool grid}. -> report dict."""
    rows, pool = [], {c: [[], []] for c in ("recovery", "native", "water", "penal")}
    pool_raw = {c: [[], []] for c in ("recovery", "native")}
    for k in keys or T.keys:
        d = T.landing(k)
        tl = d["lie"]
        lie = np.array([LIES[i] if i >= 0 else "rough" for i in
                        np.nan_to_num(T.S.sample(lie_grid.astype(np.float32), d["ll"]), nan=0).astype(int)], dtype=object)
        row = dict(hole=str(k), reg=T.reg_quality(k), n=len(tl))
        for c in ("recovery", "native", "water"):
            row[c] = prf(lie == c, tl == c)
            pool[c][0].append(lie == c)
            pool[c][1].append(tl == c)
        pen = ("recovery", "native", "water")
        row["penal"] = prf(np.isin(lie, pen), np.isin(tl, pen))
        pool["penal"][0].append(np.isin(lie, pen))
        pool["penal"][1].append(np.isin(tl, pen))
        for c in ("recovery", "native"):
            raw = T.S.sample(layers_[c], d["ll"]).astype(bool)
            row[c + "_raw"] = prf(raw, tl == c)
            pool_raw[c][0].append(raw)
            pool_raw[c][1].append(tl == c)
        row["agree"] = float(np.mean(lie == tl))
        rows.append(row)
    pooled = {c: prf(np.concatenate(v[0]), np.concatenate(v[1])) for c, v in pool.items()}
    pooled.update({c + "_raw": prf(np.concatenate(v[0]), np.concatenate(v[1])) for c, v in pool_raw.items()})
    mean = {}
    for c in ("recovery", "native", "water", "penal"):
        vals = [r[c]["iou"] for r in rows if r[c]["iou"] is not None]
        mean[c] = float(np.mean(vals)) if vals else None
    return dict(holes=rows, pooled=pooled, mean_iou=mean)


# --------------------------------------------------------------------------- strategy impact
def vision_zones_px(T, k, polys_by_lie, clip_y=(0, 2000)):
    """Vision WGS84 polygons -> traced screenshot px, clipped to the screen."""
    from shapely.geometry import Polygon, box
    scr = box(-200, clip_y[0], 1120, clip_y[1])
    out = []
    for lie in ("native", "recovery"):
        for p in polys_by_lie.get(lie, []):
            for g in getattr(p, "geoms", [p]):
                q = Polygon(T.ll_to_px(k, np.asarray(g.exterior.coords)))
                if not q.is_valid:
                    q = q.buffer(0)
                q = q.intersection(scr)
                for qq in getattr(q, "geoms", [q]):
                    if qq.geom_type == "Polygon" and qq.area > 50:
                        out.append((lie, [tuple(map(float, xy)) for xy in np.asarray(qq.exterior.coords)[:-1]]))
    return out


def strategy_impact(T, polys_by_lie, keys=None, n=6000, seed=11):
    t = T.t
    rng = np.random.default_rng(seed)
    z = np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])
    rows = []
    for k in keys or T.keys:
        h = T.HOLES[k]
        hv = dict(h)
        keep = [(nm, p) for nm, p in h["zones"] if nm not in ("recovery", "native")]
        vz = vision_zones_px(T, k, polys_by_lie)
        # order: native < recovery under everything traced (fairway, water, sand, ob drawn on top)
        vz.sort(key=lambda zz: 0 if zz[0] == "native" else 1)
        hv["zones"] = vz + keep
        res = {}
        for name, hh in (("hand", h), ("vision", hv)):
            saved = t.HOLES
            t.HOLES = {k: hh}
            try:
                res[name] = {c: t.best_aim(k, c, z=z) for c in WOODS}
            finally:
                t.HOLES = saved
        bc = {nm: min(r, key=lambda c: r[c]["ev"]) for nm, r in res.items()}
        row = dict(hole=str(k), club_hand=bc["hand"], club_vision=bc["vision"], same_club=bc["hand"] == bc["vision"])
        for c in WOODS:
            row[c] = dict(aim_hand=float(res["hand"][c]["aim"]), aim_vision=float(res["vision"][c]["aim"]),
                          ev_hand=round(float(res["hand"][c]["ev"]), 4), ev_vision=round(float(res["vision"][c]["ev"]), 4))
        # what the hand-map strategy costs if the world were the vision map, and vice versa: use the
        # hand pick's EV evaluated on the hand map vs the vision pick on the hand map
        saved = t.HOLES
        t.HOLES = {k: h}
        try:
            _, _, _, s = t.simulate(k, bc["vision"], res["vision"][bc["vision"]]["aim"], z=z)
            row["ev_loss_on_hand_map"] = round(float(s.mean() - res["hand"][bc["hand"]]["ev"]), 4)
        finally:
            t.HOLES = saved
        rows.append(row)
        print(f"  {k:>3}: hand {bc['hand']:>6} @{res['hand'][bc['hand']]['aim']:+5.1f}  vision {bc['vision']:>6} "
              f"@{res['vision'][bc['vision']]['aim']:+5.1f}  loss {row['ev_loss_on_hand_map']:+.3f}", flush=True)
    same = float(np.mean([r["same_club"] for r in rows])) if rows else None
    aim_d = [abs(r[c]["aim_hand"] - r[c]["aim_vision"]) for r in rows for c in WOODS]
    return dict(holes=rows, same_club=same, median_aim_change_yd=float(np.median(aim_d)) if aim_d else None,
                mean_ev_loss=float(np.mean([r["ev_loss_on_hand_map"] for r in rows])) if rows else None)
