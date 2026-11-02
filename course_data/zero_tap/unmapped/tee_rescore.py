"""Tee-candidate re-scorer for the unmapped tiers: "is this perceived tee complex a real hole's tee?" with hole context.

    python course_data/zero_tap/unmapped/tee_rescore.py --out tee_scores.json        # dev OOF (state folds) + test
    python course_data/zero_tap/unmapped/prep_u.py --out CU_ts --tee-scores tee_scores.json [--t-min 0.05]

Perception's tee complex `p` only sees the box itself. False tees (range tees, forward pads of another hole, mowed
patches) feed about half of the router's mispairs (UNMAPPED.md section 3), so this scores every complex again with
the context a golfer would use: distance to the nearest greens and how many greens sit at a playable hole length,
fairway ends nearby, the clubhouse, crowding by other complexes, the scene's green->tee relations, box count / area,
and the candidate's rank in its course. Label = the complex is within the bench tolerance of a true tee
(bench.Matcher.tee_ok, as in detect_eval). Gradient-boosted trees; dev scores are out-of-fold over 5 folds that
hold out whole STATES (the bench's test states are new states), test scores come from the model fitted on all dev.
The re-scored p replaces the complex's p (p_range_tee set to 0, it is a feature) via `apply`, so scene_fc's
t_min filter and percfeat's p columns use it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ZT]
import bench as B  # noqa: E402

FEATS = ["p", "p_range_tee", "pc", "nbox", "box_area", "box_p_max", "length_m", "virtual", "lidar_only", "has_segment",
         "d_green1", "d_green2", "p_green1", "n_green_near", "n_green_range", "n_green_range_hole",
         "d_fw_end", "fw_end_p", "d_club", "n_tee_60", "n_tee_150", "rel_pnext", "rel_pedge", "rel_aims",
         "pc_rank", "tee_green_ratio"]
NAN = float("nan")


def _xy(ll, lon0, lat0):
    return ((ll[0] - lon0) * 111320.0 * math.cos(math.radians(lat0)), (ll[1] - lat0) * 110540.0)


def _pc(t):
    return float(t.get("p", 1)) * (1 - float(t.get("p_range_tee") or 0))


def features(scene):
    """-> (tee complex ids, X [n, len(FEATS)])."""
    tees = [t for t in scene.get("tee_complexes", []) if t.get("centroid")]
    greens = [g for g in scene.get("greens", []) if g.get("centroid")]
    if not tees:
        return [], np.zeros((0, len(FEATS)))
    allc = [t["centroid"] for t in tees] + [g["centroid"] for g in greens]
    lon0 = float(np.mean([c[0] for c in allc]))
    lat0 = float(np.mean([c[1] for c in allc]))
    T = np.array([_xy(t["centroid"], lon0, lat0) for t in tees])
    G = np.array([_xy(g["centroid"], lon0, lat0) for g in greens]).reshape(-1, 2)
    gp = np.array([float(g.get("p", 1)) for g in greens])
    ghole = np.array([g.get("kind") == "hole" for g in greens])
    ends, endp = [], []
    for f in scene.get("fairways", []) or []:
        for e in f.get("ends") or []:
            ends.append(_xy(e, lon0, lat0))
            endp.append(float(f.get("p", 1)))
    E = np.array(ends).reshape(-1, 2)
    ch = scene.get("clubhouse") or {}
    club = _xy(ch["ll"], lon0, lat0) if ch.get("ll") and float(ch.get("p") or 0) >= 0.5 else None
    rel = {}
    for e in (scene.get("relations") or {}).get("green_to_tee", []) or []:
        r = rel.setdefault(e["tee"], [0.0, 0.0, 0])
        r[0] = max(r[0], float(e.get("p_next") or 0))
        r[1] = max(r[1], float(e.get("p_edge") or 0))
        r[2] += int(bool(e.get("aims_at_green")))
    pcs = np.array([_pc(t) for t in tees])
    rank = (np.argsort(np.argsort(-pcs)) + 0.5) / len(tees)
    n_real_g = max(1, int(np.sum(gp >= 0.5)))
    X = []
    for i, t in enumerate(tees):
        boxes = t.get("boxes") or []
        src = set(t.get("src") or [])
        dT = np.hypot(*(T - T[i]).T)
        row = dict(p=float(t.get("p", 1)), p_range_tee=float(t.get("p_range_tee") or 0), pc=pcs[i], nbox=len(boxes),
                   box_area=sum(float(b.get("area_m2") or 0) for b in boxes),
                   box_p_max=max([float(b.get("p") or 0) for b in boxes], default=NAN),
                   length_m=float(t.get("length_m") or NAN), virtual=float(bool(t.get("virtual"))),
                   lidar_only=float(src == {"lidar_pad"}), has_segment=float("segment" in src),
                   n_tee_60=int(np.sum(dT < 60)) - 1, n_tee_150=int(np.sum(dT < 150)) - 1,
                   pc_rank=rank[i], tee_green_ratio=len(tees) / n_real_g)
        if len(G):
            dG = np.hypot(*(G - T[i]).T)
            o = np.argsort(dG)
            row.update(d_green1=dG[o[0]], d_green2=dG[o[1]] if len(o) > 1 else NAN, p_green1=gp[o[0]],
                       n_green_near=int(np.sum(dG < 60)),
                       n_green_range=int(np.sum((dG >= 90) & (dG <= 550) & (gp >= 0.5))),
                       n_green_range_hole=int(np.sum((dG >= 90) & (dG <= 550) & ghole)))
        if len(E):
            dE = np.hypot(*(E - T[i]).T)
            k = int(np.argmin(dE))
            row.update(d_fw_end=dE[k], fw_end_p=endp[k])
        if club is not None:
            row["d_club"] = math.hypot(T[i][0] - club[0], T[i][1] - club[1])
        r = rel.get(t["id"])
        if r:
            row.update(rel_pnext=r[0], rel_pedge=r[1], rel_aims=r[2])
        else:
            row.update(rel_pnext=0.0, rel_pedge=0.0, rel_aims=0)
        X.append([float(row.get(f, NAN)) for f in FEATS])
    return [t["id"] for t in tees], np.array(X, float)


def labels(scene, truth):
    M = B.Matcher(truth)
    out = []
    for t in scene.get("tee_complexes", []):
        if not t.get("centroid"):
            continue
        pts = [t["centroid"]] + [b["centroid"] for b in t.get("boxes", []) if b.get("centroid")]
        pp = [M.pj.fwd(*q[:2]) for q in pts]
        out.append(int(any(M.tee_ok(j, pp) for j in range(len(M.holes)))))
    return np.array(out, int)


def apply(scene, scores):
    """Scene copy with each scored complex's p replaced by the re-scored p (p_range_tee -> 0). scores=None: unchanged."""
    if not scores:
        return scene
    sc = dict(scene)
    tc = []
    for t in scene.get("tee_complexes", []):
        if t["id"] in scores:
            t = dict(t, p=float(scores[t["id"]]), p_range_tee=0.0, p_raw=t.get("p"), p_range_tee_raw=t.get("p_range_tee"))
        tc.append(t)
    sc["tee_complexes"] = tc
    return sc


def state_folds(rows, k=5):
    """slug -> fold, whole states per fold, balanced by course count (greedy, deterministic)."""
    by = {}
    for r in rows:
        by.setdefault(r["state"], []).append(r["slug"])
    load = [0] * k
    out = {}
    for st in sorted(by, key=lambda s: (-len(by[s]), s)):
        f = int(np.argmin(load))
        load[f] += len(by[st])
        for s in by[st]:
            out[s] = f
    return out


def _model():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=40,
                                          l2_regularization=1.0, random_state=0)


def _load(split):
    sys.path.insert(0, HERE)
    import detect_eval as DE
    data = []
    for r in B.courses(split, tier="unmapped_card"):
        sc = DE.load_scene(r)
        ids, X = features(sc)
        y = labels(sc, B.truth(r["slug"]))
        data.append(dict(slug=r["slug"], state=r["state"], ids=ids, X=X, y=y, pc=X[:, FEATS.index("pc")] if len(X) else X))
    return data


def _auc(y, s):
    from sklearn.metrics import average_precision_score, roc_auc_score
    return roc_auc_score(y, s), average_precision_score(y, s)


def report(name, data, key):
    y = np.concatenate([d["y"] for d in data])
    raw = np.concatenate([d["pc"] for d in data])
    new = np.concatenate([d[key] for d in data])
    a0, ap0 = _auc(y, raw)
    a1, ap1 = _auc(y, new)
    print(f"{name}: {len(y)} complexes, {y.mean():.3f} real | raw pc AUC {a0:.3f} AP {ap0:.3f} | re-scored AUC {a1:.3f} AP {ap1:.3f}")
    for cut in (0.02, 0.05, 0.1, 0.2):
        keep = new >= cut
        print(f"   re-scored >= {cut:.2f}: keeps {keep.mean():.3f} of complexes, {y[keep].sum() / max(1, y.sum()):.3f} of real "
              f"tees, precision {y[keep].mean():.3f}")
    return dict(n=int(len(y)), real=float(y.mean()), raw_auc=a0, raw_ap=ap0, auc=a1, ap=ap1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()
    dev, test = _load("dev"), _load("test")
    folds = state_folds(dev, a.k)
    for f in range(a.k):
        tr = [d for d in dev if folds[d["slug"]] != f and len(d["X"])]
        m = _model().fit(np.vstack([d["X"] for d in tr]), np.concatenate([d["y"] for d in tr]))
        for d in dev:
            if folds[d["slug"]] == f and len(d["X"]):
                d["s"] = m.predict_proba(d["X"])[:, 1]
    m = _model().fit(np.vstack([d["X"] for d in dev if len(d["X"])]), np.concatenate([d["y"] for d in dev if len(d["X"])]))
    for d in test:
        d["s"] = m.predict_proba(d["X"])[:, 1] if len(d["X"]) else np.zeros(0)
    for d in dev + test:
        d.setdefault("s", np.zeros(0))
    summ = dict(dev_oof=report("dev OOF (state folds)", dev, "s"), test=report("test (fit on all dev, once)", test, "s"))
    out = dict(schema="tee_rescore/1", feats=FEATS, folds=folds, summary=summ,
               scores={d["slug"]: {i: round(float(v), 4) for i, v in zip(d["ids"], d["s"])} for d in dev + test})
    json.dump(out, open(a.out, "w"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
