"""Train the perception models from the per-course tables (perceive.py --tables), geographic hold-out by state.

    python course_data/perception/train.py --tables DIR [--out course_data/perception/models]

Models (sklearn HistGradientBoosting, pinned scikit-learn==1.9.1 in perception.yml; pickles in models/):
  path_px      per-pixel cart path (1) / road (2) / other (0) on PATH_FEATURES
  green        per green candidate: false (0) / hole green (1) / practice green (2)
  tee_box      per tee-box candidate: matches an OSM tee box within 8 m
  tee_complex  per complex: within 25 m of an OSM tee box or hole start
  parking      per paved blob: overlaps an OSM car park
  clubhouse    per building: is the OSM clubhouse (ranked; the arg-max is the clubhouse)
Training uses only TRAIN states; TEST_STATES are never seen (their numbers in models.json are the held-out
check of the object models on the candidates the CURRENT detectors produced).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import pickle
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TEST_STATES = ("GA", "KY", "MN", "UT", "ME", "WY")       # geographic hold-out (never used for training)
OBJ_MODELS = ("green", "tee_box", "tee_complex", "parking", "clubhouse")


def split_of(state):
    return "test" if str(state or "").upper() in TEST_STATES else "train"


def load_tables(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "*", "objects.json"))):
        o = json.load(open(p))
        o["dir"] = os.path.dirname(p)
        out.append(o)
    return out


def _xy(rows, feats):
    X = np.array([[np.nan if r.get(f) is None else r.get(f) for f in feats] for r in rows], float)
    y = np.array([r["y"] for r in rows], int)
    return X, y


def fit(X, y, seed=0, max_iter=250, balanced=True):
    from sklearn.ensemble import HistGradientBoostingClassifier
    clf = HistGradientBoostingClassifier(max_iter=max_iter, learning_rate=0.08, max_leaf_nodes=15, min_samples_leaf=20,
                                         l2_regularization=1.0, class_weight="balanced" if balanced else None,
                                         random_state=seed)
    clf.fit(X, y)
    return clf


def _metrics(clf, X, y, thr=None, pos=1):
    from sklearn.metrics import roc_auc_score
    if len(y) == 0:
        return {}
    pr = clf.predict_proba(X)
    cl = list(clf.classes_)
    pred = np.array(cl)[pr.argmax(1)]
    if thr is not None and len(cl) == 2:
        pred = np.where(pr[:, 1] >= thr, cl[1], cl[0])
    out = dict(n=int(len(y)), acc=round(float((pred == y).mean()), 4))
    if pos in cl and len(set(y)) > 1:
        try:
            out["auc_pos"] = round(float(roc_auc_score(y == pos, pr[:, cl.index(pos)])), 4)
        except ValueError:
            pass
        tp = int(((pred == pos) & (y == pos)).sum())
        out["precision_pos"] = round(tp / max(int((pred == pos).sum()), 1), 4)
        out["recall_pos"] = round(tp / max(int((y == pos).sum()), 1), 4)
    return out


def oof_threshold(train_tabs, name, feats, k=3):
    """F1-optimal decision threshold from course-grouped k-fold out-of-fold predictions on the train states."""
    groups = [t for t in train_tabs if t.get(name)]
    if len(groups) < k:
        return None
    ps, ys = [], []
    for f in range(k):
        tr = [r for i, t in enumerate(groups) if i % k != f for r in t[name]]
        te = [r for i, t in enumerate(groups) if i % k == f for r in t[name]]
        if not te or len({r["y"] for r in tr}) < 2:
            continue
        X, y = _xy(tr, feats)
        c = fit(X, y, balanced=False, max_iter=150)
        Xe, ye = _xy(te, feats)
        ps.append(c.predict_proba(Xe)[:, list(c.classes_).index(1)])
        ys.append(ye)
    if not ps:
        return None
    p, y = np.concatenate(ps), np.concatenate(ys)
    best, bt = -1, 0.5
    for th in np.linspace(0.05, 0.9, 35):
        tp = float(((p >= th) & (y == 1)).sum())
        f1 = 2 * tp / max(float((p >= th).sum() + (y == 1).sum()), 1)
        if f1 > best:
            best, bt = f1, float(th)
    return round(bt, 3)


def train_objects(tabs, out_dir, log=print):
    res = {}
    for name in OBJ_MODELS:
        tr = [r for t in tabs if split_of(t["meta"].get("state")) == "train" for r in t.get(name, [])]
        te = [r for t in tabs if split_of(t["meta"].get("state")) == "test" for r in t.get(name, [])]
        if len(tr) < 40 or len({r["y"] for r in tr}) < 2:
            log(name, "too few rows", len(tr))
            res[name] = dict(skipped=f"{len(tr)} train rows")
            continue
        feats = sorted({k for r in tr for k in r if k != "y"})
        Xtr, ytr = _xy(tr, feats)
        clf = fit(Xtr, ytr, balanced=(name == "clubhouse"))     # unweighted = calibrated-ish p; clubhouse is a ranking
        thr = None
        if name in ("parking", "tee_box", "tee_complex"):
            thr = oof_threshold([t for t in tabs if split_of(t["meta"].get("state")) == "train"], name, feats)
        Xte, yte = _xy(te, feats) if te else (np.zeros((0, len(feats))), np.zeros(0, int))
        res[name] = dict(features=feats, n_train=len(tr), n_test=len(te),
                         train_class_counts={int(k): int(v) for k, v in zip(*np.unique(ytr, return_counts=True))},
                         thr=thr, train=_metrics(clf, Xtr, ytr), test=_metrics(clf, Xte, yte, thr) if len(te) else {})
        if name == "clubhouse" and te:                          # ranking: top-1 per course
            hit = n = 0
            for t in tabs:
                if split_of(t["meta"].get("state")) != "test" or not t.get(name):
                    continue
                X, y = _xy(t[name], feats)
                pr = clf.predict_proba(X)[:, list(clf.classes_).index(1)]
                n += 1
                hit += int(y[int(pr.argmax())] == 1)
            res[name]["test"]["top1"] = round(hit / max(n, 1), 4)
            res[name]["test"]["courses"] = n
        pickle.dump(dict(clf=clf, features=feats, thr=thr), open(os.path.join(out_dir, f"{name}.pkl"), "wb"))
        log(name, json.dumps(res[name])[:600])
    return res


def train_paths(tabs, out_dir, max_rows=1_500_000, log=print):
    """Pixel model on the features every table has (tables from different code versions may differ)."""
    import features as F
    zs = []
    for t in tabs:
        p = os.path.join(t["dir"], "path_px.npz")
        if os.path.exists(p):
            z = np.load(p, allow_pickle=False)
            zs.append((t, [str(f) for f in z["features"]], z["X"], z["y"]))
    if not zs:
        return dict(skipped="no path tables")
    common = [f for f in F.PATH_FEATURES if all(f in names for _, names, _, _ in zs)]
    Xs, ys, te_X, te_y = [], [], [], []
    for t, names, X, y in zs:
        X = X[:, [names.index(f) for f in common]]
        test = split_of(t["meta"].get("state")) == "test"
        (te_X if test else Xs).append(X)
        (te_y if test else ys).append(y)
    if not Xs:
        return dict(skipped="no train-state path tables")
    X, y = np.vstack(Xs), np.concatenate(ys)
    if len(y) > max_rows:
        ii = np.random.default_rng(0).choice(len(y), max_rows, replace=False)
        X, y = X[ii], y[ii]
    t0 = time.time()
    clf = fit(X, y, max_iter=300, balanced=False)
    res = dict(features=common, n_train=int(len(y)), courses_train=len(Xs), courses_test=len(te_X),
               seconds=round(time.time() - t0, 1), train=_metrics(clf, X, y))
    if te_X:
        res["test"] = _metrics(clf, np.vstack(te_X), np.concatenate(te_y))
    thr = choose_path_threshold()
    res["thr"] = thr
    pickle.dump(dict(clf=clf, features=common, thr=thr), open(os.path.join(out_dir, "path_px.pkl"), "wb"))
    log("path_px", json.dumps(res)[:800])
    return res


def choose_path_threshold(scenes=os.path.join(HERE, "scenes"), default=0.5):
    """Graph threshold with the best length F1 (+ connectivity) over the TRAIN-state courses' sweeps of the last run."""
    acc = {}
    for p in glob.glob(os.path.join(scenes, "*", "eval.json")):
        e = json.load(open(p))
        if split_of(e.get("state")) != "train":
            continue
        for thr, v in (e.get("path_sweep") or {}).items():
            if not v.get("eligible") or v.get("length_precision") is None or v.get("length_recall") is None:
                continue
            P, R = v["length_precision"], v["length_recall"]
            f1 = 2 * P * R / max(P + R, 1e-9)
            acc.setdefault(thr, []).append(f1 + 0.5 * (v.get("connectivity_acc") or 0))
    if not acc:
        return default
    return float(max(acc, key=lambda k: np.mean(acc[k])))


def main():
    import sys
    sys.path.insert(0, HERE)
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "models"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tabs = load_tables(a.tables)
    print(len(tabs), "course tables;", sum(split_of(t["meta"].get("state")) == "test" for t in tabs), "in test states")
    import sklearn
    res = dict(id="perception-" + time.strftime("%Y%m%d-%H%M", time.gmtime()), sklearn=sklearn.__version__,
               test_states=list(TEST_STATES),
               courses=dict(train=sorted(t["meta"]["slug"] for t in tabs if split_of(t["meta"].get("state")) == "train"),
                            test=sorted(t["meta"]["slug"] for t in tabs if split_of(t["meta"].get("state")) == "test")),
               objects=train_objects(tabs, a.out), path_px=train_paths(tabs, a.out))
    json.dump(res, open(os.path.join(a.out, "models.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
