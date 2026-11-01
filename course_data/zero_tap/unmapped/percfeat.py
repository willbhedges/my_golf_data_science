"""Perception evidence as extra pathroute_v2 feature columns (NaN on OSM caches, so OSM + unmapped pools mix).

hole (tee box t, green g):  green p, p_hole, practice flag, raised_m, box p, complex p, boxes in the perceived
                            complex, rank of green p_hole among this tee's candidate greens
walk (green g -> tee t):    perception's own green -> complex `p_next` / `p_edge` (relations.green_to_tee),
                            cart-path walking distance between them (path_m)
tee pair (t1, t2):          same perceived complex
"""
from __future__ import annotations

import gzip
import json
import os

import numpy as np

HOLE_P = ("g_p", "g_phole", "g_practice", "g_raised", "t_p", "t_pcomplex", "t_nbox", "g_phole_rank")
TRANS_P = ("p_next", "p_edge", "path_m")
TPAIR_P = ("same_complex",)
# feature sets: "all"; "geom" = only measurements and grouping that no trained perception score enters
# (lidar raised_m, box count and grouping of the perceived complex). The perception object / edge models were
# trained on 37 of the 55 unmapped courses' OSM, so their p's are in-sample there (see UNMAPPED.md).
SETS = {"all": set(HOLE_P + TRANS_P + TPAIR_P),
        "geom": {"g_raised", "t_nbox", "same_complex"},
        "geom_path": {"g_raised", "t_nbox", "same_complex", "path_m"},
        "no_rel": set(HOLE_P + TPAIR_P)}


def _mask(X, names, keep):
    """keep only the columns of the chosen set (a constant all-NaN column breaks the GBM binning)."""
    X = np.array(X, float).reshape(-1, len(names))
    return X[:, [i for i, n in enumerate(names) if n in keep]]


def _scene(row, root):
    with gzip.open(os.path.join(root, row["files"]["scene"]), "rt") as fh:
        return json.load(fh)


def augment(d, scene, fset="all"):
    keep = SETS[fset]
    gp, tp = d["green_props"], d["tee_props"]
    cx = [p.get("complex") for p in tp]
    nbox = {}
    for c in cx:
        nbox[c] = nbox.get(c, 0) + 1
    G = np.array([[float(p.get("p") or np.nan), float(p.get("p_hole") or np.nan), float(p.get("kind") == "practice"),
                   float(p.get("raised_m")) if p.get("raised_m") is not None else np.nan] for p in gp]).reshape(-1, 4)
    T = np.array([[float(p.get("p") or np.nan), float(p.get("p_complex") or np.nan), float(nbox.get(p.get("complex"), 1))]
                  for p in tp]).reshape(-1, 3)
    rows = []
    by_t = {}
    for k, (ti, gi) in enumerate(d["hp"]):
        by_t.setdefault(ti, []).append(k)
    rank = np.zeros(len(d["hp"]))
    for ti, ks in by_t.items():
        v = np.array([-(G[d["hp"][k][1], 1] if np.isfinite(G[d["hp"][k][1], 1]) else 0) for k in ks])
        rank[ks] = np.argsort(np.argsort(v))
    for k, (ti, gi) in enumerate(d["hp"]):
        rows.append(list(G[gi]) + list(T[ti]) + [rank[k]])
    d["hX"] = np.c_[d["hX"], _mask(np.array(rows).reshape(-1, len(HOLE_P)), HOLE_P, keep)]
    rel = {}
    for e in (scene.get("relations") or {}).get("green_to_tee", []):
        rel[(e["green"], e["tee"])] = e
    gid = [p.get("osm_id") for p in gp]
    tr = []
    for gi, ti in d["tp"]:
        e = rel.get((gid[gi], cx[ti]))
        tr.append([float(e.get("p_next", np.nan)), float(e.get("p_edge", np.nan)),
                   float(e["path_m"]) if e and e.get("path_m") is not None else np.nan] if e else [0.0, 0.0, np.nan])
    d["tX"] = np.c_[d["tX"], _mask(np.array(tr).reshape(-1, len(TRANS_P)), TRANS_P, keep)]
    d["tpX"] = np.c_[d["tpX"], _mask(np.array([[float(cx[a] == cx[b])] for a, b in d["tpp"]]).reshape(-1, 1),
                                     TPAIR_P, keep)]
    return d


def pad_osm(d, fset="all"):
    keep = SETS[fset]
    for key, names in (("hX", HOLE_P), ("tX", TRANS_P), ("tpX", TPAIR_P)):
        d[key] = np.c_[d[key], np.full((len(d[key]), sum(n in keep for n in names)), np.nan)]
    return d
