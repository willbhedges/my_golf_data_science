"""Simulated golfer for confirm-and-resolve (resolve2.Session) on the zero-tap benchmark (nocard tier).

    python course_data/zero_tap/pathroute_v2/sim2.py --c1 C1 --c2 C2 --fit-out MODEL.pkl --json OUT.json [--jobs 4]

1. calibration as run2 (5-fold OOF on dev), models fit on all dev -> MODEL.pkl ({"models", "calib", ...}: the
   production model, see live2.py);
2. test courses (one run): the app asks about the lowest-confidence unconfirmed hole, the golfer answers from the
   truth ("hole N is this tee + green", or "not a hole"), the route is re-solved; repeat until every unconfirmed
   hole has confidence >= 0.999 or all holes are confirmed. The trajectory gives the taps for any threshold;
3. at the 98 %-precision stop (and with no pair taps at all) one extra "this tee is hole 1" tap -> numbering.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute"), ZT]
import bench as B  # noqa: E402
import run as R1  # noqa: E402
import run2 as R2  # noqa: E402
import confidence as CF  # noqa: E402
import resolve2 as RS  # noqa: E402

CAP = 0.999
_G = {}


# ----------------------------------------------------------------------------- fitting (parallel folds)
def _fold(args):
    f, c1, c2 = args
    dev = R2.load(c1, c2, "dev")
    fi = R1.folds(dev, 5)
    M = R2.Models2().fit([d for d in dev if fi.get(d["slug"], -1) not in (-1, f)])
    out = {}
    for d in dev:
        if fi.get(d["slug"], -1) == f:
            out[d["slug"]] = R2.decode_course(d, M.predict(d))
    return out


def fit(c1, c2, jobs):
    dev = R2.load(c1, c2, "dev")
    with Pool(jobs) as p:
        parts = p.map(_fold, [(f, c1, c2) for f in range(5)])
    dec = {k: v for part in parts for k, v in part.items()}
    X, y = [], []
    for d in dev:
        s = d["slug"]
        if s in dec and len(dec[s][0]):
            r = R2.to_result(d, dec[s][0], dec[s][1], np.zeros(len(dec[s][0])))
            X.append(dec[s][2])
            y.append(R2.pair_correct(r, s)[0])
    calib = CF.Calib().fit(np.vstack(X), np.concatenate(y))
    M = R2.Models2().fit([d for d in dev if not d.get("error")])
    return dict(models=M, calib=calib, cfg=R2.CFG, w=R2.W, trained_on="zero_tap benchmark dev split (nocard)",
                n_courses=sum(1 for d in dev if not d.get("error")))


# ----------------------------------------------------------------------------- golfer
def _scene_pos(M, ll):
    return M.pj.fwd(*ll[:2])


def answer(d, M, g):
    """-> (true hole index j or None, scene tees that are j's tee)."""
    p = _scene_pos(M, d["greens"][g]["ll"])
    js = [j for j in range(len(M.holes)) if M.green_ok(j, p)]
    if not js:
        return None, []
    j = min(js, key=lambda j: np.hypot(p[0] - M.holes[j]["g"][0], p[1] - M.holes[j]["g"][1]))
    tees = [t for t, tt in enumerate(d["tees"]) if M.tee_ok(j, [_scene_pos(M, tt["ll"])])]
    return j, tees


def state(d, s, hand):
    """Score the current solve: (y per predicted hole, N, miss, numbering right count)."""
    r = R2.to_result(d, s.holes, s.route_conf, s.conf)
    y, N = R2.pair_correct(r, d["slug"])
    for i, h in enumerate(s.holes):
        if (h["t"], h["g"]) in hand:
            y[i] = 1
    miss = max(0, N - int(y.sum()) - int((1 - y).sum()))
    t = B.truth(d["slug"])
    M = B.Matcher(t)
    num = 0
    used = set()
    for ph, h, ok in zip(r["holes"], s.holes, y):
        j, _ = M.match(ph)
        if (h["t"], h["g"]) in hand:
            j = hand[(h["t"], h["g"])]
        if ok and j is not None and j not in used:
            used.add(j)
            num += int(M.holes[j]["ref"] == ph["number"])
    return y, N, miss, num


def simulate(slug):
    d, Mo, cal = _G["d"][slug], _G["M"], _G["cal"]
    t = B.truth(slug)
    Mt = B.Matcher(t)
    single = d["kind"] in (9, 18)
    pr = Mo.predict(d)
    s = RS.Session(d, pr, cal)
    s.solve()
    hand = {}                                   # golfer-placed tee (no OSM tee matches the true hole)
    traj = []

    def snap(n_taps):
        y, N, miss, num = state(d, s, hand)
        fp = s.fixed_pairs()
        un = [c for h, c in zip(s.holes, s.conf) if (h["t"], h["g"]) not in fp]
        traj.append(dict(taps=n_taps, min_un=float(min(un)) if un else 1.0,
                         conf=[round(float(c), 4) for c in s.conf], y=y.tolist(), N=N, miss=miss, num=num,
                         fix=json.loads(json.dumps(s.fix))))
    snap(0)
    taps = 0
    while taps < 40:
        i = s.ask(CAP)
        if i is None:
            break
        h = s.holes[i]
        j, tees = answer(d, Mt, h["g"])
        taps += 1
        if j is None:
            s.not_a_hole(h["g"])
        else:
            num = Mt.holes[j]["ref"] if single else None
            if tees:
                t2 = min(tees, key=lambda t: (t not in [h["t"]] + list(h["boxes"]), t))
            else:
                t2 = h["t"]
                hand[(t2, h["g"])] = j
            s.confirm_pair(num, t2, h["g"])
        s.solve()
        if not s.holes:
            break
        snap(taps)
    out = dict(slug=slug, kind=d["kind"], traj=traj)
    # hole-1 tap on top of a state: re-solve with the true hole-1 tee
    j1 = next((j for j, hh in enumerate(Mt.holes) if hh["ref"] == 1), None)
    tees1 = [tt for tt, x in enumerate(d["tees"]) if j1 is not None and Mt.tee_ok(j1, [_scene_pos(Mt, x["ll"])])]
    out["hole1_tee_found"] = bool(tees1)
    if single and tees1:
        h1 = {}
        for k, st in enumerate(traj):
            s2 = RS.Session(d, pr, cal, fix=st["fix"])
            s2.fix["pairs"] = [tuple(p) for p in s2.fix["pairs"]]
            s2.hole_one(tees1[0])
            s2.solve()
            if not s2.holes:
                continue
            y, N, miss, num = state(d, s2, hand)
            h1[k] = dict(num=num, y=y.tolist(), N=N)
        out["hole1"] = h1
    return out


def _init(c1, c2, model):
    _G["d"] = {d["slug"]: d for d in R2.load(c1, c2, "test")}
    m = pickle.load(open(model, "rb"))
    _G["M"], _G["cal"] = m["models"], m["calib"]


def _sim(slug):
    try:
        return simulate(slug)
    except Exception as e:                                    # noqa: BLE001
        return dict(slug=slug, error=f"{type(e).__name__}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c1", required=True)
    ap.add_argument("--c2", required=True)
    ap.add_argument("--fit-out", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--courses")
    a = ap.parse_args()
    t0 = time.time()
    if not os.path.exists(a.fit_out):
        m = fit(a.c1, a.c2, a.jobs)
        pickle.dump(m, open(a.fit_out, "wb"))
        print(f"fit {time.time() - t0:.0f}s", flush=True)
    test = [d for d in R2.load(a.c1, a.c2, "test") if not d.get("error")]
    slugs = [d["slug"] for d in test]
    if a.courses:
        slugs = [s for s in slugs if s in a.courses.split(",")]
    res = []
    with Pool(a.jobs, initializer=_init, initargs=(a.c1, a.c2, a.fit_out)) as p:
        for r in p.imap_unordered(_sim, slugs):
            res.append(r)
            print(r["slug"], len(r.get("traj", [])) - 1, r.get("error", ""), f"{time.time() - t0:.0f}s", flush=True)
            json.dump(res, open(a.json, "w"))


if __name__ == "__main__":
    main()
