"""Unmapped back-tee ("tips") candidates for tees/cardless.py: find the tee boxes OSM does not map, without a card.

    import tip_candidates as TC
    cands = TC.load_candidates(files)                       # lidar pads + NAIP segment tees + perception scene tees
    extra, diag = TC.select_tips(holes, osm_tees, cands)    # per hole: [] or [accepted tee box (source-flagged)]
    card = cardless.infer_card(holes, osm_tees, pads, extra_boxes=extra)

How a human finds the tips: behind the back mapped box, on the hole axis, a flat (lidar) pad of mown grass (NAIP)
that is not a green, path or building. Here every candidate pad assigned to a hole (place_tee.assign_tees_to_holes)
that lies behind the hole's farthest OSM box is scored with a logistic model (fitted on the zero_tap DEV split: is
the card's back yardage inside this candidate, +-5 yds, while no OSM box holds it?). Features: how far behind the
back box (its back edge beyond the box's back edge; it may overlap the box), offset from the first leg, source (lidar / segment / scene), detector probability, area, how many
independent sources agree on the spot, distance to the nearest green, whether the routed line start lies on it.
Per hole the best candidate is accepted when its probability clears TIP_MODEL["thr"]. Holes without any OSM box are
left to cardless's own pad fallback.

Evaluation: eval_tips.py -> eval_tips.json, summary in CARDLESS.md ("Unmapped tips: candidate search"). Result: on the
zero_tap imagery subset the candidates do not clear the break-even precision, so the dev-fitted threshold accepts
(almost) nothing and cardless output is unchanged by default.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE] if HERE not in sys.path else []
import cardless as CL  # noqa: E402
import place_tee as pt  # noqa: E402

MODEL_PATH = os.path.join(HERE, "tip_model.json")
MAX_BEHIND_YD = 80.0        # a candidate further behind the back box than this is not a tip
MIN_BEHIND_YD = 4.0         # ... nearer than this is the back box itself
AGREE_YD = 10.0
HIT_YD = 5.0
SOURCES = ("lidar", "segment", "scene")
FEATURES = ("bias", "gap", "gap2", "absoff", "is_lidar", "is_segment", "is_scene", "p", "logarea", "n_src",
            "green_yd", "line_on", "n_osm", "rank", "len", "overlaps_osm", "overlaps_osm_lidar")


def _rdjson(path):
    import gzip
    raw = open(path, "rb").read()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def load_candidates(files, resolve=lambda p: p):
    """Candidate tee pads of a course from the files the bench / pipeline has: lidar pads (pads.json, (lat, lon)),
    NAIP segment model tees (segment.geojson class=tee) and perception scene tee boxes (scene.json.gz, blind mode:
    built without OSM). -> [{id, coords [(lat, lon)], source, p, area}]"""
    out = []
    f = files or {}
    pp = resolve(f["pads"]) if f.get("pads") else None
    if pp and os.path.exists(pp):
        for q in _rdjson(pp) or []:
            out.append(dict(id=q.get("id"), coords=[tuple(c) for c in q["coords"]], source="lidar", p=None,
                            area=q.get("area_m2")))
    sp = resolve(f["segment"]) if f.get("segment") else None
    if sp and os.path.exists(sp):
        for i, g in enumerate(_rdjson(sp).get("features") or []):
            p, gm = g.get("properties") or {}, g.get("geometry") or {}
            if p.get("class") != "tee" or gm.get("type") not in ("Polygon", "MultiPolygon"):
                continue
            cs = gm["coordinates"][0] if gm["type"] == "Polygon" else gm["coordinates"][0][0]
            out.append(dict(id=f"segment:{i}", coords=[(c[1], c[0]) for c in cs], source="segment", p=p.get("p"),
                            area=p.get("area_m2")))
    cp = resolve(f["scene"]) if f.get("scene") else None
    if cp and os.path.exists(cp):
        for t in _rdjson(cp).get("tee_complexes") or []:
            if t.get("virtual"):
                continue
            for b in t.get("boxes") or []:
                out.append(dict(id=f"scene:{b['id']}", coords=[(c[1], c[0]) for c in b["polygon"]], source="scene",
                                p=(b.get("p") or 0) * (1 - (t.get("p_range_tee") or 0)), area=b.get("area_m2")))
    return out


def load_model(path=MODEL_PATH):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def candidate_rows(holes, tees, cands, osm_boxes=None):
    """Per hole: (top, [row]) where top = back edge yardage of the farthest OSM box (None: no box) and each row is a
    candidate behind it with its features and tee dict."""
    osm_boxes = osm_boxes if osm_boxes is not None else CL.tee_complexes(holes, tees)
    lines = {str(h["ref"]) + "#" + str(i): [tuple(p) for p in h["line"][:-1]] + [tuple(h.get("green") or h["line"][-1])]
             for i, h in enumerate(holes)}
    by = pt.assign_tees_to_holes(lines, cands) if cands else {}
    fr0 = pt.Frame(holes[0]["green"][0], holes[0]["green"][1]) if holes else None
    greens = [fr0.fwd(*h["green"]) for h in holes] if holes else []
    gr = [h.get("green_r_yd") or 15.0 for h in holes]
    out = []
    for i, (k, h) in enumerate(zip(lines, holes)):
        bx = osm_boxes[i]
        if not bx:
            out.append((None, []))
            continue
        top = max(b["d_back"] for b in bx)
        line_yd = CL.hole_geometry(h)[2]["line_yd"]
        meas = []
        for t in by.get(k, []):
            m = CL.measure_boxes(h, [t], source=t["source"])
            if not m:
                continue
            m = m[0]
            gap = m["d_back"] - top                         # how far it reaches behind the back box
            if not (MIN_BEHIND_YD <= gap <= MAX_BEHIND_YD):
                continue
            # a lidar pad often covers the whole levelled complex: the mapped box AND the unmapped tips behind it
            ovl = float(m["d_front"] < top - 1)
            ring = [fr0.fwd(*p) for p in t["coords"]]
            c = pt.polygon_centroid(ring) if len(ring) >= 3 else ring[0]
            gyd = min((math.hypot(c[0] - g[0], c[1] - g[1]) - r for j, (g, r) in enumerate(zip(greens, gr))),
                      default=200.0)
            meas.append(dict(m, tee=t, gap=gap, p=t.get("p"), area=t.get("area") or 0.0, green_yd=gyd,
                             line_on=float(m["d_front"] - 5 <= line_yd <= m["d_back"] + 5), ovl=ovl))
        meas.sort(key=lambda r: r["gap"])
        for r_, m in enumerate(meas):
            srcs = {o["source"] for o in meas if abs(o["d_back"] - m["d_back"]) <= AGREE_YD}
            m["n_src"] = len(srcs)
            m["rank"] = r_
            m["n_osm"] = len(bx)
            m["x"] = featurize(m)
        out.append((top, meas))
    return out


def featurize(m):
    g = m["gap"] / 30.0
    p = m["p"] if m["p"] is not None else 0.5
    return [1.0, g, g * g, abs(m["offset"]) / 20.0, float(m["source"] == "lidar"), float(m["source"] == "segment"),
            float(m["source"] == "scene"), p, math.log(max(m["area"], 10.0)) / 5.0, (m["n_src"] - 1) / 2.0,
            min(m["green_yd"], 60.0) / 30.0, m["line_on"], min(m["n_osm"], 5) / 5.0, min(m["rank"], 3) / 3.0,
            min(m["len"], 60.0) / 30.0, m["ovl"], m["ovl"] * float(m["source"] == "lidar")]


def prob(x, w):
    z = sum(a * b for a, b in zip(w, x))
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))


def select_tips(holes, tees, cands, model=None, thr=None, osm_boxes=None):
    """-> (extra: per hole [] or [tee dict, source-flagged 'tip:<src>'], diag: per hole dict)."""
    model = model or load_model()
    extra, diag = [], []
    if not model or not cands:
        return [[] for _ in holes], [{} for _ in holes]
    thr = model["thr"] if thr is None else thr
    for top, rows in candidate_rows(holes, tees, cands, osm_boxes):
        best = None
        for r in rows:
            pr = prob(r["x"], model["w"])
            if best is None or pr > best[0]:
                best = (pr, r)
        if best and best[0] >= thr:
            t = dict(best[1]["tee"])
            t["source"] = "tip:" + best[1]["source"]
            t["tip_p"] = round(best[0], 3)
            extra.append([t])
            diag.append(dict(p=round(best[0], 3), gap=round(best[1]["gap"], 1), source=best[1]["source"]))
        else:
            extra.append([])
            diag.append(dict(p=round(best[0], 3)) if best else {})
    return extra, diag


def fit_logistic(X, Y, l2=1e-2, iters=4000, lr=0.3, pos_w=1.0):
    import numpy as np
    X, Y = np.array(X, float), np.array(Y, float)
    w = np.zeros(X.shape[1])
    sw = np.where(Y > 0, pos_w, 1.0)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))
        g = X.T @ ((p - Y) * sw) / len(X) + l2 * np.r_[0, w[1:]]
        w -= lr * g
    return [round(float(v), 5) for v in w]
