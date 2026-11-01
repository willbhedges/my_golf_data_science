"""pathroute v2 on the zero-tap benchmark (nocard tier): v1 cache + v2 extras, OOF on dev, one run on test.

    python course_data/zero_tap/pathroute/prep.py --cache C1 --split all
    python course_data/zero_tap/pathroute_v2/prep2.py --cache C1 --out C2
    python course_data/zero_tap/pathroute_v2/run2.py --c1 C1 --c2 C2 --out course_data/zero_tap/results/pathroute_v2
        [--test]        # also fit on all dev and run test once

Writes <out>/nocard/<slug>.json (zero_tap_result/1, per-hole calibrated pair `confidence`), <out>/summary.json.
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
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute"), ZT]
import bench as B  # noqa: E402
import decode as DC  # noqa: E402
import run as R1  # noqa: E402
from model import Models  # noqa: E402
import complexes as CX  # noqa: E402
import confidence as CF  # noqa: E402
import decode2 as D2  # noqa: E402

METHOD = "pathroute_v2"
W = dict(trans=0.5, club=1.0)
CFG = dict(cross=1.5, reuse=2.0, comp_thr=0.5, K=6, beam=4000, box_mode="v1+comp", mm_beam=800)


def load(c1, c2, split):
    out = []
    for d in R1.load(c1, split):
        if not d.get("error"):
            p = os.path.join(c2, d["slug"] + ".pkl")
            e = pickle.load(open(p, "rb")) if os.path.exists(p) else dict(error="no v2 cache")
            if e.get("error"):
                d = dict(d, error=e["error"])
            else:
                d.update(e)
                d["hX"] = np.c_[d["hX"], e["hX2"]]
        out.append(d)
    return out


class Models2:
    def fit(self, ds):
        ds = [d for d in ds if not d.get("error")]
        self.h = Models().fit(ds)
        self.tp = CX.TeePairModel().fit(ds)
        return self

    def predict(self, d):
        pr = self.h.predict(d)
        pr["tpair"] = self.tp.predict(d)
        return pr


def decode_course(d, pr, cfg=CFG, conf_feats=True):
    """-> (holes, route conf, conf feature rows)."""
    comp = CX.cluster(len(d["tees"]), d["tpp"], pr["tpair"], thr=cfg["comp_thr"])
    kw = dict(K=cfg["K"], cross=cfg["cross"], reuse=cfg["reuse"], box_mode=cfg["box_mode"])
    holes, conf, cost = D2.decode2(d, pr, W, comp, beam=cfg["beam"], return_cost=True, **kw)
    H, T, S, E = DC.cost_mats(d, pr, W)
    if not conf_feats or not holes:
        return holes, conf, np.zeros((len(holes), len(CF.CONF_F)))
    mm = []
    for h in holes:
        H2 = H.copy()
        H2[comp == comp[h["t"]], h["g"]] = np.inf
        H2[h["t"], h["g"]] = np.inf
        _, _, c2 = D2.decode2(d, pr, W, comp, beam=cfg["mm_beam"], H=H2, return_cost=True, **kw)
        mm.append(c2 - cost if np.isfinite(c2) else 30.0)
    return holes, conf, CF.hole_conf_feats(d, H, T, holes, conf, mm)


def to_result(d, holes, conf, hconf, cuts=(225.0, 450.0)):
    base = dict(schema="zero_tap_result/1", method=METHOD, version=R1._version(), tier="nocard", slug=d["slug"],
                card_kind="none")
    if d.get("error"):
        return dict(base, certain=False, confidence=0.0, holes=[], error=d["error"])
    multi = d["kind"] in (27, 36)
    hs = []
    for h, c in zip(holes, hconf):
        hs.append(dict(number=h["number"], par=DC.par_from_len(h["L"], *cuts), green_ll=d["greens"][h["g"]]["ll"],
                       tee_ll=d["tees"][h["t"]]["ll"], tee_boxes_ll=[d["tees"][b]["ll"] for b in h["boxes"]],
                       green_id=d["greens"][h["g"]]["id"], tee_id=d["tees"][h["t"]]["id"],
                       confidence=round(float(c), 4), length_yd=round(h["L"], 1),
                       **({"course": "ABCD"[h["loop"]]} if multi else {})))
    return dict(base, certain=False, confidence=conf, holes=hs, error=None if hs else "decode failed")


def pair_correct(res, slug):
    """Per predicted hole: tee (or one of its boxes) + green of one true hole (bench's 'formed'), N true holes."""
    t = B.truth(slug)
    M = B.Matcher(t)
    used, out = set(), []
    for ph in res.get("holes") or []:
        j, _ = M.match(ph)
        ok = j is not None and j not in used
        if ok:
            used.add(j)
        out.append(int(ok))
    return np.array(out, int), t["n_holes"]


def primary_correct(res, slug):
    """Same as pair_correct but with the primary tee only (no box set) - the stricter pairing number."""
    r2 = dict(res, holes=[dict(h, tee_boxes_ll=[]) for h in res.get("holes") or []])
    return pair_correct(r2, slug)


def course_rows(res_list):
    rows = []
    for r in res_list:
        y, N = pair_correct(r, r["slug"])
        yp, _ = primary_correct(r, r["slug"])
        c = np.array([h.get("confidence") or 0.0 for h in r.get("holes") or []], float)
        miss = max(0, N - int(y.sum()) - int((1 - y).sum()))     # true holes with no predicted hole at all
        rows.append(dict(slug=r["slug"], N=N, y=y, yp=yp, c=c, miss=miss))
    return rows


def pair_summary(rows, target=0.98):
    tot = sum(r["N"] for r in rows)
    paired = sum(int(r["y"].sum()) for r in rows) / tot
    primary = sum(int(r["yp"].sum()) for r in rows) / tot
    allp = np.mean([int(r["y"].sum()) == r["N"] for r in rows])
    # taps: low-confidence holes asked; a course's missing holes must be placed by hand (one tap each)
    cs = [(np.r_[r["c"], np.zeros(r["miss"])], np.r_[r["y"], np.zeros(r["miss"], int)]) for r in rows]
    tp = CF.taps_to_precision(cs, target)
    return dict(paired=round(paired, 4), paired_primary_tee=round(primary, 4), all_pairs_right=round(float(allp), 4),
                taps98=dict(threshold=round(tp[0], 4), taps_per_course=round(tp[1], 2), precision=round(tp[2], 4),
                            courses_no_tap=round(tp[3], 4)) if tp else None)


def reliability(rows, bins=(0, .5, .7, .8, .9, .95, .98, 1.01)):
    c = np.concatenate([r["c"] for r in rows])
    y = np.concatenate([r["y"] for r in rows])
    out = []
    for a, b in zip(bins[:-1], bins[1:]):
        m = (c >= a) & (c < b)
        if m.any():
            out.append(dict(bin=f"{a:.2f}-{min(b, 1):.2f}", n=int(m.sum()), mean_conf=round(float(c[m].mean()), 3),
                            acc=round(float(y[m].mean()), 3)))
    return out


def run_dev(ds, k=5, cfg=CFG, log=print):
    fi = R1.folds(ds, k)
    dec = {}
    t0 = time.time()
    for f in range(k):
        M = Models2().fit([d for d in ds if fi.get(d["slug"], -1) not in (-1, f)])
        for d in ds:
            if fi.get(d["slug"], -1) == f:
                dec[d["slug"]] = decode_course(d, M.predict(d), cfg)
        log(f"fold {f} {time.time() - t0:.0f}s")
    # calibration: out-of-fold over the same folds
    ys = {}
    for d in ds:
        if d["slug"] in dec:
            r = to_result(d, dec[d["slug"]][0], dec[d["slug"]][1], np.zeros(len(dec[d["slug"]][0])))
            ys[d["slug"]] = pair_correct(r, d["slug"])[0]
    hconf = {}
    for f in range(k):
        tr = [s for s in dec if fi[s] != f and len(dec[s][0])]
        cal = CF.Calib().fit(np.vstack([dec[s][2] for s in tr]), np.concatenate([ys[s] for s in tr]))
        for s in dec:
            if fi[s] == f and len(dec[s][0]):
                hconf[s] = cal.predict(dec[s][2])
    res = []
    for d in ds:
        s = d["slug"]
        if s in dec:
            res.append(to_result(d, dec[s][0], dec[s][1], hconf.get(s, np.zeros(0))))
        else:
            res.append(to_result(d, [], 0.0, []))
    calib_all = CF.Calib().fit(np.vstack([dec[s][2] for s in dec if len(dec[s][0])]),
                               np.concatenate([ys[s] for s in dec if len(dec[s][0])]))
    return res, calib_all


def run_test(dev, test, calib, cfg=CFG):
    M = Models2().fit(dev)
    res = []
    for d in test:
        if d.get("error"):
            res.append(to_result(d, [], 0.0, []))
            continue
        holes, conf, X = decode_course(d, M.predict(d), cfg)
        res.append(to_result(d, holes, conf, calib.predict(X) if len(holes) else []))
    return res


def bench_summary(res, split):
    a = B.score(res, split)[split]
    return dict(formed=a["formed_acc"], number=a["hole_number_acc"], holes_right=a["courses_holes_right"],
                fully=a["courses_fully_right"], fails=a["course_failures"],
                by_kind={k: (v["formed_acc"], v["hole_number_acc"]) for k, v in a["by_kind"].items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c1", required=True)
    ap.add_argument("--c2", required=True)
    ap.add_argument("--out")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    dev = load(a.c1, a.c2, "dev")
    res, calib = run_dev(dev)
    summ = dict(config=CFG, dev=dict(bench=bench_summary(res, "dev"), pairs=pair_summary(course_rows(res)),
                                     reliability=reliability(course_rows(res))))
    print(json.dumps(summ["dev"]), flush=True)
    outs = dict(dev=res)
    if a.test:
        test = load(a.c1, a.c2, "test")
        tres = run_test([d for d in dev if not d.get("error")], test, calib)
        summ["test"] = dict(bench=bench_summary(tres, "test"), pairs=pair_summary(course_rows(tres)),
                            reliability=reliability(course_rows(tres)))
        print(json.dumps(summ["test"]), flush=True)
        outs["test"] = tres
    if a.out:
        for sp, rs in outs.items():
            for r in rs:
                B.write_result(r, os.path.join(a.out, "nocard"))
        prev = {}
        sp = os.path.join(a.out, "summary.json")
        if os.path.exists(sp):
            prev = json.load(open(sp))
        prev.update(summ)
        json.dump(prev, open(sp, "w"), indent=1)


if __name__ == "__main__":
    main()
