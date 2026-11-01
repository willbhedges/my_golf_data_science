"""pathroute_v2 on the unmapped tiers (perception scene as the golf layer): dev out-of-fold, test once.

    python course_data/zero_tap/unmapped/run_u.py --cu CU --c1 C1 --c2 C2 --train mix [--out DIR] [--test]

--train: osm  = pair / walk / complex models fitted on the OSM (nocard) dev caches only
         unm  = fitted on the unmapped dev caches only
         mix  = both (default)
Dev is 5-fold over the unmapped dev courses; in every fold the held-out courses are removed from BOTH training
pools (their OSM version too), and the per-hole confidence calibration is out-of-fold on the same folds.
Writes <out>/unmapped_nocard/<slug>.json and <out>/unmapped_card/<slug>.json (same pairs and numbering; the card
tier takes pars from the card when its hole count fits) + <out>/summary_unmapped.json.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ZT))
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute_v2"), os.path.join(ZT, "pathroute"), ZT]
import bench as B  # noqa: E402
import run2 as R2  # noqa: E402
import confidence as CF  # noqa: E402
import percfeat as PF  # noqa: E402

METHOD = "pathroute_v2_unmapped"


def load_cu(cu, split, perc=None):
    out = []
    for r in B.courses(split, tier="unmapped_card"):
        p = os.path.join(cu, r["slug"] + ".pkl")
        d = pickle.load(open(p, "rb")) if os.path.exists(p) else dict(slug=r["slug"], kind=r["kind"], error="no cache")
        if perc and not d.get("error"):
            d = PF.augment(d, PF._scene(r, ROOT), perc)
        out.append(d)
    return out


def folds(ds, k=5):
    good = sorted(d["slug"] for d in ds if not d.get("error"))
    return {s: i % k for i, s in enumerate(good)}


def pools(train, osm, unm, drop=()):
    drop = set(drop)
    p = []
    if train in ("osm", "mix"):
        p += [d for d in osm if not d.get("error") and d["slug"] not in drop]
    if train in ("unm", "mix"):
        p += [d for d in unm if not d.get("error") and d["slug"] not in drop]
    return p


def cards():
    return {r["slug"]: B.card_for(r) for r in B.courses(tier="unmapped_card")}


def to_results(d, holes, conf, hconf, card_kind):
    card, kind = card_kind or (None, "none")
    r = R2.to_result(d, holes, conf, hconf)
    r["method"] = METHOD
    out = {}
    out["unmapped_nocard"] = dict(r, tier="unmapped_nocard")
    rc = json.loads(json.dumps(r))
    rc["tier"] = "unmapped_card"
    rc["card_kind"] = kind
    par = (card or {}).get("par") or []
    n = len(par)
    per = 9 if d["kind"] in (9, 27) else 18
    for h in rc["holes"]:
        # 27 / 36: loop A / B / C numbered 1..9 (1..18); a card covering every loop is read loop by loop
        pos = h["number"] - 1 + ("ABCD".index(h["course"]) * per if h.get("course") and n > per else 0)
        if 0 <= pos < n and par[pos]:
            h["par"] = int(par[pos])
    out["unmapped_card"] = rc
    return out


def run_dev(osm, unm, train, cfg=R2.CFG, k=5, log=print):
    fi = folds(unm, k)
    dec = {}
    t0 = time.time()
    for f in range(k):
        held = [s for s, v in fi.items() if v == f]
        M = R2.Models2().fit(pools(train, osm, unm, drop=held))
        for d in unm:
            if fi.get(d["slug"], -1) == f:
                dec[d["slug"]] = R2.decode_course(d, M.predict(d), cfg)
        log(f"fold {f} {time.time() - t0:.0f}s")
    ys = {}
    for d in unm:
        if d["slug"] in dec:
            r = R2.to_result(d, dec[d["slug"]][0], dec[d["slug"]][1], np.zeros(len(dec[d["slug"]][0])))
            ys[d["slug"]] = R2.pair_correct(r, d["slug"])[0]
    hconf = {}
    for f in range(k):
        tr = [s for s in dec if fi[s] != f and len(dec[s][0])]
        cal = CF.Calib().fit(np.vstack([dec[s][2] for s in tr]), np.concatenate([ys[s] for s in tr]))
        for s in dec:
            if fi[s] == f and len(dec[s][0]):
                hconf[s] = cal.predict(dec[s][2])
    good = [s for s in dec if len(dec[s][0])]
    calib = CF.Calib().fit(np.vstack([dec[s][2] for s in good]), np.concatenate([ys[s] for s in good]))
    res = []
    for d in unm:
        s = d["slug"]
        if s in dec:
            res.append((d, dec[s][0], dec[s][1], hconf.get(s, np.zeros(0))))
        else:
            res.append((d, [], 0.0, []))
    return res, calib


def run_test(osm, unm_dev, unm_test, train, calib, cfg=R2.CFG):
    M = R2.Models2().fit(pools(train, osm, unm_dev))
    res = []
    for d in unm_test:
        if d.get("error"):
            res.append((d, [], 0.0, []))
            continue
        holes, conf, X = R2.decode_course(d, M.predict(d), cfg)
        res.append((d, holes, conf, calib.predict(X) if len(holes) else []))
    return res


def finish(res, cds):
    out = {"unmapped_nocard": [], "unmapped_card": []}
    for d, holes, conf, hc in res:
        if d.get("error"):
            r = R2.to_result(d, [], 0.0, [])
            r["method"] = METHOD
            rs = {"unmapped_nocard": dict(r, tier="unmapped_nocard"), "unmapped_card": dict(r, tier="unmapped_card")}
        else:
            rs = to_results(d, holes, conf, hc, cds.get(d["slug"]))
        for k, v in rs.items():
            out[k].append(v)
    return out


def summarize(out, split):
    s = {}
    for tier, rs in out.items():
        a = B.score(rs, split)[split]
        s[tier] = dict(formed=a["formed_acc"], number=a["hole_number_acc"], holes_right=a["courses_holes_right"],
                       fully=a["courses_fully_right"], fails=a["course_failures"],
                       pairs=R2.pair_summary(R2.course_rows(rs)))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cu", required=True)
    ap.add_argument("--c1", required=True)
    ap.add_argument("--c2", required=True)
    ap.add_argument("--train", default="mix")
    ap.add_argument("--out")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--perc", choices=sorted(PF.SETS), help="add perception evidence columns (percfeat.py)")
    a = ap.parse_args()
    osm = R2.load(a.c1, a.c2, "dev") if a.train != "unm" else []
    if a.perc:
        osm = [d if d.get("error") else PF.pad_osm(d, a.perc) for d in osm]
    unm = load_cu(a.cu, "dev", a.perc)
    cds = cards()
    res, calib = run_dev(osm, unm, a.train)
    outs = dict(dev=finish(res, cds))
    summ = dict(train=a.train, perc=a.perc, cu=os.path.basename(a.cu.rstrip("/")), dev=summarize(outs["dev"], "dev"))
    print(json.dumps(summ["dev"]), flush=True)
    if a.test:
        test = load_cu(a.cu, "test", a.perc)
        outs["test"] = finish(run_test(osm, unm, test, a.train, calib), cds)
        summ["test"] = summarize(outs["test"], "test")
        print(json.dumps(summ["test"]), flush=True)
    if a.out:
        for sp, o in outs.items():
            for tier, rs in o.items():
                for r in rs:
                    B.write_result(r, os.path.join(a.out, tier))
        json.dump(summ, open(os.path.join(a.out, "summary_unmapped.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
