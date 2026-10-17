"""hole_pairs/1: calibrated P(tee complex -> green) for one course (contract in README.md).

    python course_data/zero_tap/formation/hole_pairs.py --osm osm.geojson[.gz] [--course course.json] \
           [--card scorecard.json] [--aux aux.npz] --out hole_pairs.json
    python course_data/zero_tap/formation/hole_pairs.py --scene scene.json[.gz] [--card ...] [--aux ...] --out ...

    from hole_pairs import hole_pairs
    hp = hole_pairs(scene, card=None, aux_path=None)       # scene: structure.scene.Scene (OSM or perception)
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import assign as A                                                   # noqa: E402
import data as D                                                     # noqa: E402

MODEL = os.path.join(HERE, "model.pkl")
_M = {}
P_MIN = 0.005


def load_model(path=MODEL):
    if path not in _M:
        _M[path] = pickle.load(open(path, "rb"))
    return _M[path]


def hole_pairs(sc, card=None, aux_path=None, model_path=MODEL, slug=None):
    import solver as V
    import formation as FM
    m = load_model(model_path)
    clf, clf2, cal = m["clf"], m.get("clf2"), m["cal"]
    geo = V.Geo(sc)
    D.add_virtual_tees(sc, geo)
    aux = D.Aux(aux_path, sc.proj) if aux_path and os.path.exists(aux_path) else None
    pairs = D.pair_features(sc, geo, aux, card)
    perc = sc.source.startswith("perception")
    nG, nC = len(geo.G), len(geo.C)
    S = np.full((nG, nC), -np.inf)
    r = dict(mode="perc" if perc else "osm", nG=nG, nC=nC, G=geo.G, C=geo.C,
             gi=np.array([p["gi"] for p in pairs], int), k=np.array([p["k"] for p in pairs], int),
             D=np.array([p["D"] for p in pairs], float), cover=[p["cover"] for p in pairs],
             X=np.array([[p["f"][n] for n in D.FEATS] for p in pairs], float).reshape(-1, len(D.FEATS)),
             greens=[dict(p=float(g.get("p_hole", g.get("conf", 1.0)))) for g in sc.greens],
             cands=[dict(xy=np.asarray(c["xy"]), virtual=bool(c.get("virtual"))) for c in geo.cx])
    if pairs:
        z = FM.pair_logit(clf, r)
        if clf2 is not None:
            z = FM.stage2_logit(clf2, r, z, card)
        S[r["gi"], r["k"]] = z
    ph = np.clip(np.array([g["p"] for g in r["greens"]], float), 0.02, 0.999)
    slack = cal["b0"] + cal["b1"] * (np.log1p(-ph) - np.log(ph))
    P, ps = A.sinkhorn(S, slack, temp=cal["temp"])
    amap = dict(A.map_assign(S, slack)) if nG else {}
    pj = sc.proj
    cid = [c["id"] for c in geo.cx]
    out_pairs = []
    for p in pairs:
        gi, k = p["gi"], p["k"]
        if P[gi, k] < P_MIN:
            continue
        g, t = geo.G[gi], np.asarray(p["tee"], float)
        out_pairs.append(dict(green=sc.greens[gi]["id"], tee=cid[k], p=round(float(P[gi, k]), 4),
                              logit=round(float(S[gi, k]), 3), length_yd=round(float(p["D"]), 1),
                              bearing_deg=round((90.0 - math.degrees(math.atan2(g[1] - t[1], g[0] - t[0]))) % 360, 1),
                              green_ll=pj.ll(g), tee_ll=pj.ll(t),
                              tee_boxes_ll=[pj.ll(b) for b in np.asarray(geo.cx[k]["xy"])],
                              p_corridor=round(FM.corridor_mass(geo.G, geo.C, P[gi], gi, k), 4),
                              covers=[cid[c] for c in p.get("cover", []) if c != k]))
    out_pairs.sort(key=lambda r: (r["green"], -r["p"]))
    greens = []
    for gi, g in enumerate(sc.greens):
        k = amap.get(gi)
        greens.append(dict(id=g["id"], ll=pj.ll(geo.G[gi]), p_hole_input=round(float(ph[gi]), 3),
                           p_no_tee=round(float(ps[gi]), 4), p_paired=round(float(1 - ps[gi]), 4),
                           map_tee=cid[k] if k is not None else None,
                           p_map=round(float(P[gi, k]), 4) if k is not None else None,
                           p_map_corridor=round(FM.corridor_mass(geo.G, geo.C, P[gi], gi, k), 4) if k is not None else None))
    tees = []
    used = P.sum(0) if nG else np.zeros(nC)
    for k, c in enumerate(geo.cx):
        tees.append(dict(id=cid[k], ll=pj.ll(np.asarray(c["c"])), boxes_ll=[pj.ll(b) for b in np.asarray(c["xy"])],
                         virtual=bool(c.get("virtual")), p_input=round(float(c.get("conf", 1.0)), 3),
                         p_starts_hole=round(float(min(1.0, used[k])), 4)))
    return dict(schema="hole_pairs/1", slug=slug, input="perception" if perc else "osm", card_used=bool(card),
                aux_used=aux is not None, model=f"formation-v2@{m.get('trained_utc', '?')}",
                built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                greens=greens, tees=tees, pairs=out_pairs,
                map=[dict(green=sc.greens[gi]["id"], tee=cid[k], p=round(float(P[gi, k]), 4),
                          p_corridor=round(FM.corridor_mass(geo.G, geo.C, P[gi], gi, k), 4),
                          green_ll=pj.ll(geo.G[gi]), tee_ll=pj.ll(np.asarray(geo.cx[k]["xy"])[
                              int(np.argmax(np.hypot(*(np.asarray(geo.cx[k]["xy"]) - geo.G[gi]).T)))]),
                          tee_boxes_ll=[pj.ll(b) for b in np.asarray(geo.cx[k]["xy"])],
                          length_yd=round(float(np.hypot(*(np.asarray(geo.cx[k]["xy"]) - geo.G[gi]).T).max()), 1))
                     for gi, k in sorted(amap.items()) if k is not None],
                summary=dict(n_greens=nG, n_tees=nC, n_virtual=sum(1 for c in geo.cx if c.get("virtual")),
                             expected_holes=round(float((1 - ps).sum()), 2), map_holes=sum(1 for k in amap.values() if k is not None)))


def main():
    import scene as S
    ap = argparse.ArgumentParser()
    ap.add_argument("--osm")
    ap.add_argument("--course")
    ap.add_argument("--scene")
    ap.add_argument("--card", help="scorecard/1 json, or a generalize-style {cards, chosen} file")
    ap.add_argument("--aux")
    ap.add_argument("--slug")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.osm:
        fc = S.load_fc(a.osm)
        course = json.load(open(a.course)) if a.course else {}
        sc = S.scene_from_osm(fc, course.get("boundary"))
    else:
        op = gzip.open if a.scene.endswith(".gz") else open
        with op(a.scene, "rt") as fh:
            sc = S.scene_from_perception(json.load(fh))
    card = None
    if a.card:
        obj = json.load(open(a.card))
        if "cards" in obj:
            cs = obj["cards"]
            card = next((c["card"] for c in cs if c["source"] == obj.get("chosen")), cs[0]["card"] if cs else None)
        else:
            card = obj
    hp = hole_pairs(sc, card, a.aux, slug=a.slug)
    json.dump(hp, open(a.out, "w"), indent=1)
    print(json.dumps(hp["summary"]))


if __name__ == "__main__":
    main()
