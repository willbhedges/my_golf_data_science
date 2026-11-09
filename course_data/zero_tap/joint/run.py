"""joint routing: fit the local models, solve every course, score.

    python course_data/zero_tap/joint/run.py scores --cache CACHE --source scene|truth|osm      # models -> CACHE/sc_<source>.pkl
    python course_data/zero_tap/joint/run.py eval   --cache CACHE --source scene --split dev [--card 1] [--answer 0]
    python course_data/zero_tap/joint/run.py final  --cache CACHE --out course_data/zero_tap/joint/eval

Dev scores of the local models are out-of-fold by state; test scores come from the all-dev fit. Weights
(joint/params.json) and the confidence calibration are chosen on dev only; `final` runs test once.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ZT]
import bench as B  # noqa: E402
import prep  # noqa: E402
import models as M  # noqa: E402
import solve as S  # noqa: E402
import propose as PR  # noqa: E402

PARAMS = os.path.join(HERE, "params.json")


def load_params(source, card):
    if os.path.exists(PARAMS):
        return json.load(open(PARAMS)).get("%s_%s" % (source, "card" if card else "nocard"), {})
    return {}


def number_of(i, kind):
    L = 18 if kind in (18, 36) else 9
    return i % L + 1


def first_tee(d):
    """The golfer's one answer: the tee complex of hole 1 (nearest detected complex that is a tee of hole 1)."""
    lab = d["lab"]
    j1 = [j for j, (r, c) in enumerate(lab["refs"]) if r == 1]
    if not j1:
        return None
    j1 = j1[0]
    ts = [t for t, s in enumerate(lab["t2h"]) if j1 in s]
    if not ts:
        return None
    t = B.truth(d["row"]["slug"])
    co = d["co"]
    p = np.array(co["pj"].fwd(*t["holes"][j1]["line"][0]))
    return min(ts, key=lambda k: float(np.hypot(*(d["geo"]["Tc"][k] - p))))


def run_course(d, use_card=True, answer=False, params=None, want_margins=True):
    """Solve one cached course. -> dict(result (zero_tap_result/1), quick metrics, confidence features)."""
    card = d["card"] if use_card else None
    fix = None
    if answer:
        t1 = first_tee(d)
        fix = {0: t1} if t1 is not None else None
    try:
        sol = S.solve(d, card, params, fix)
    except Exception as e:
        return dict(slug=d["row"]["slug"], error=repr(e), holes=[], feat=None, ok=[], n=d["kind"])
    pr, co = sol["pr"], d["co"]
    mg = S.margins(sol, fix) if (want_margins and sol["seq"]) else [0.0] * len(sol["seq"])
    lab = d["lab"]
    holes, ok, res_y = [], [], []
    props = PR.propose(d, sol)
    for i, (c, (t, g)) in enumerate(zip(sol["seq"], sol["holes"])):
        num = number_of(i, d["kind"])
        h = dict(number=num, virtual=bool(t < 0 or g < 0), margin=round(float(mg[i]), 3))
        if g >= 0:
            h["green_ll"] = [round(v, 7) for v in co["pj"].inv(*co["G"][g])]
            h["green_id"] = co["Gid"][g]
        elif props.get(i, {}).get("green") is not None:
            h["green_ll"] = [round(v, 7) for v in co["pj"].inv(*props[i]["green"])]
        if t >= 0:
            tc = co["T"][t]
            far = int(np.argmax(np.hypot(*(tc["pts"] - co["G"][g]).T)))
            h["tee_ll"] = [round(v, 7) for v in co["pj"].inv(*tc["pts"][far])]
            h["tee_boxes_ll"] = [[round(v, 7) for v in co["pj"].inv(*q)] for q in tc["pts"]]
            h["tee_id"] = tc["id"]
        elif props.get(i, {}).get("tee") is not None:
            h["tee_ll"] = [round(v, 7) for v in co["pj"].inv(*props[i]["tee"])]
        if pr.Y is not None:
            k = pr.kstar if pr.kstar is not None else 0
            y = float(pr.Y[k, i])
            h["par"] = None
            h["yards"] = y
            if c < pr.real:
                res_y.append(float(np.nanmin(pr.R[:, i, c])))
        if d["card"] and use_card and d["card"].get("par") and len(d["card"]["par"]) >= 1:
            pp = d["card"]["par"]
            h["par"] = pp[i % len(pp)]
        elif g >= 0 and t >= 0:
            L = d["geo"]["P"][t, g]
            h["par"] = 3 if L < 245 else (4 if L < 470 else 5)
        # quick truth check (the bench scorer is the official one)
        j = lab["g2h"][g] if g >= 0 else -1
        ok.append(bool(j >= 0 and t >= 0 and j in lab["t2h"][t] and lab["refs"][j][0] == num))
        holes.append(h)
    nv = sum(1 for t, g in sol["holes"] if t < 0 and g >= 0)
    nm = sum(1 for t, g in sol["holes"] if g < 0)
    n = max(len(holes), 1)
    mga = np.array(mg) if len(mg) else np.zeros(1)
    feat = dict(min_margin=float(mga.min()), mean_margin=float(np.minimum(mga, 20).mean()),
                p10_margin=float(np.percentile(np.minimum(mga, 20), 10)), n_virtual=nv, n_missing=nm,
                cost_per_hole=float(sol["cost"] or 0) / n,
                card_med=float(np.median(res_y)) if res_y else -1.0,
                card_ok=float(np.mean(np.array(res_y) < 15)) if res_y else -1.0,
                n_extra_green=int(np.sum(d["co"]["Gp"] > 0.5)) - d["kind"],
                club=float(d["co"].get("club") is not None), N=d["kind"])
    res = dict(schema="zero_tap_result/1", method="joint", tier=None, slug=d["row"]["slug"], certain=False,
               confidence=0.0, holes=holes, error=None)
    return dict(slug=d["row"]["slug"], result=res, feat=feat, ok=ok, n=d["kind"], split=d["row"]["split"],
                has_card=pr.Y is not None, answered=bool(fix))


def _job(a):
    d, kw = a
    return run_course(d, **kw)


def run_all(ds, procs=3, **kw):
    if procs <= 1:
        return [run_course(d, **kw) for d in ds]
    with Pool(procs) as pool:
        return pool.map(_job, [(d, kw) for d in ds], chunksize=2)


def quick(rs):
    """Quick metrics from the label check: holes numbered right, courses with every hole right."""
    H = sum(r["n"] for r in rs)
    return dict(courses=len(rs), holes_right=round(sum(sum(r["ok"]) for r in rs) / max(H, 1), 4),
                all_right=round(float(np.mean([len(r["ok"]) == r["n"] and all(r["ok"]) for r in rs])), 4) if rs else 0)


def get_scored(cache, source):
    p = os.path.join(cache, "sc_%s.pkl" % source)
    if os.path.exists(p):
        return pickle.load(open(p, "rb"))
    dev = prep.load(cache, source, "dev")
    test = prep.load(cache, source, "test")
    M.fit_predict(dev, test)
    pickle.dump((dev, test), open(p, "wb"))
    return dev, test


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--cache", required=True)
    ap.add_argument("--source", default="scene")
    ap.add_argument("--split", default="dev")
    ap.add_argument("--card", type=int, default=1)
    ap.add_argument("--answer", type=int, default=0)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--set", default="")
    a = ap.parse_args()
    dev, test = get_scored(a.cache, a.source)
    if a.cmd == "scores":
        from sklearn.metrics import roc_auc_score
        for nm, ds in (("dev", dev), ("test", test)):
            yh = np.concatenate([M.labels(d)[0] for d in ds])
            yw = np.concatenate([M.labels(d)[1] for d in ds])
            print(nm, len(ds), "hole AUC %.3f walk AUC %.3f" % (
                roc_auc_score(yh, np.concatenate([d["sc"]["ph"] for d in ds])),
                roc_auc_score(yw, np.concatenate([d["sc"]["pw"] for d in ds]))))
        return
    ds = dev if a.split == "dev" else test
    if a.card:
        ds = [d for d in ds if d["card"]]
    P = load_params(a.source, a.card)
    for kv in a.set.split(","):
        if kv:
            k, v = kv.split("=")
            P[k] = float(v) if "." in v or "e" in v else int(v)
    rs = run_all(ds, a.procs, use_card=bool(a.card), answer=bool(a.answer), params=P, want_margins=False)
    print(a.source, a.split, "card" if a.card else "nocard", "answer" if a.answer else "", a.set, quick(rs))


if __name__ == "__main__":
    main()
