"""Fit the pair-confidence calibrator on CONSTRAINED re-solves (confirm-and-resolve), so a hole's confidence stays
calibrated after the golfer has confirmed other holes.

    python course_data/zero_tap/pathroute_v2/calib_resolve.py --c1 C1 --c2 C2 --states STATES.pkl \
        [--model course_data/zero_tap/pathroute_v2/model_v2.pkl.gz] [--out MODEL_OUT.pkl.gz] [--jobs 3]

1. dev, out-of-fold: per fold, the hole / walk / tee-pair models are fit on the other 4 folds; each held-out course is
   played by the simulated golfer of sim2.py (ask the lowest-confidence unconfirmed hole under the CURRENT calibrator,
   answer from truth, re-solve), up to MAX_TAPS taps. Every state's unconfirmed holes give a row of
   confidence.CONF_F2 features (route / min-marginal / margins of the constrained decode + fix-aware extras) and the
   label "pair right" -> STATES.pkl.
2. confidence.Calib2 (logistic, plain coefficients) on all rows; course-level 5-fold OOF log-loss / reliability on
   dev is printed against the old calibrator on the same rows.
3. --out: model_v2 + calib_fix = Calib2 (models and the free-decode calibrator `calib` unchanged): resolve2.Session
   uses calib_fix once any golfer fact is set (Calib2 is worse than the old calibrator on free decodes: dev OOF
   log-loss 0.230 vs 0.195, the latter in-sample).
"""
from __future__ import annotations

import argparse
import gzip
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
import sim2 as SIM  # noqa: E402

MAX_TAPS = 18
_G = {}


def _read(p):
    with (gzip.open if p.endswith(".gz") else open)(p, "rb") as fh:
        return pickle.load(fh)


def _fit_fold(args):
    f, c1, c2 = args
    dev = R2.load(c1, c2, "dev")
    fi = R1.folds(dev, 5)
    return f, R2.Models2().fit([d for d in dev if fi.get(d["slug"], -1) not in (-1, f)])


def _init(c1, c2, folds_path, model):
    _G["d"] = {d["slug"]: d for d in R2.load(c1, c2, "dev") if not d.get("error")}
    _G["fi"] = R1.folds(list(_G["d"].values()), 5)
    _G["M"] = _read(folds_path)
    _G["cal"] = _read(model)["calib"]


def collect(slug):
    """Simulated golfer on one dev course with its fold's models -> rows of (X, y, step) of unconfirmed holes."""
    d = _G["d"][slug]
    Mo = _G["M"][_G["fi"][slug]]
    cal = _G["cal"]
    Mt = B.Matcher(B.truth(slug))
    single = d["kind"] in (9, 18)
    pr = Mo.predict(d)
    s = RS.Session(d, pr, cal)
    s.solve()
    hand, done, rows = {}, set(), []

    def snap(step):
        if not s.holes:
            return
        y, N, miss, num = SIM.state(d, s, hand)
        fp = s.fixed_pairs()
        for i, h in enumerate(s.holes):
            if (h["t"], h["g"]) not in fp:
                rows.append((s.X[i].tolist(), int(y[i]), step, float(s.conf[i])))
    snap(0)
    taps = 0
    while taps < MAX_TAPS:
        i = s.ask(SIM.CAP)
        if i is None:
            break
        h = s.holes[i]
        j, tees = SIM.answer(d, Mt, h["g"], done)
        taps += 1
        if j is None:
            s.not_a_hole(h["g"])
        else:
            done.add(j)
            num = Mt.holes[j]["ref"] if single else None
            tees = [t for t in tees if t not in {p[1] for p in s.fix["pairs"]}]
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
    return slug, rows


def _collect(slug):
    try:
        return collect(slug)
    except Exception as e:                                    # noqa: BLE001
        return slug, f"{type(e).__name__}: {e}"


def logloss(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def reliability(p, y, bins=(0, .5, .7, .8, .9, .95, .98, 1.01)):
    out = []
    for a, b in zip(bins[:-1], bins[1:]):
        m = (p >= a) & (p < b)
        if m.any():
            out.append((f"{a:.2f}-{min(b, 1):.2f}", int(m.sum()), round(float(p[m].mean()), 3), round(float(y[m].mean()), 3)))
    return out


def evaluate(states, C=1.0):
    """Course-level 5-fold OOF: Calib2 vs the old calibrator's stored confidence, on all rows / fixed-state rows."""
    slugs = sorted(states)
    fo = {s: i % 5 for i, s in enumerate(slugs)}
    X = np.array([r[0] for s in slugs for r in states[s]], float)
    y = np.array([r[1] for s in slugs for r in states[s]], int)
    step = np.array([r[2] for s in slugs for r in states[s]], int)
    old = np.array([r[3] for s in slugs for r in states[s]], float)
    f = np.array([fo[s] for s in slugs for _ in states[s]], int)
    p = np.zeros(len(y))
    for k in range(5):
        cal = CF.Calib2().fit(X[f != k], y[f != k], C=C)
        p[f == k] = cal.predict(X[f == k])
    out = {}
    for name, m in (("all", np.ones(len(y), bool)), ("step0", step == 0), ("after_fix", step > 0)):
        out[name] = dict(n=int(m.sum()), acc=round(float(y[m].mean()), 4), ll_old=round(logloss(old[m], y[m]), 4),
                         ll_new=round(logloss(p[m], y[m]), 4), rel_old=reliability(old[m], y[m]),
                         rel_new=reliability(p[m], y[m]))
    return out, X, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c1", required=True)
    ap.add_argument("--c2", required=True)
    ap.add_argument("--states", required=True)
    ap.add_argument("--model", default=os.path.join(HERE, "model_v2.pkl.gz"))
    ap.add_argument("--folds", help="fold models pickle (cached)")
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--C", type=float, default=1.0)
    a = ap.parse_args()
    t0 = time.time()
    if not os.path.exists(a.states):
        fp = a.folds or a.states + ".folds.pkl"
        if not os.path.exists(fp):
            with Pool(a.jobs) as p:
                M = dict(p.map(_fit_fold, [(f, a.c1, a.c2) for f in range(5)]))
            pickle.dump(M, open(fp, "wb"))
            print(f"fold models {time.time() - t0:.0f}s", flush=True)
        dev = [d["slug"] for d in R2.load(a.c1, a.c2, "dev") if not d.get("error")]
        states = {}
        with Pool(a.jobs, initializer=_init, initargs=(a.c1, a.c2, fp, a.model)) as p:
            for slug, rows in p.imap_unordered(_collect, dev):
                if isinstance(rows, str):
                    print(slug, "ERR", rows, flush=True)
                    continue
                states[slug] = rows
                print(slug, len(rows), f"{time.time() - t0:.0f}s", flush=True)
                if len(states) % 10 == 0:
                    pickle.dump(states, open(a.states + ".part", "wb"))
        pickle.dump(states, open(a.states, "wb"))
    states = pickle.load(open(a.states, "rb"))
    ev, X, y = evaluate(states, a.C)
    print(json.dumps(ev, indent=1))
    if a.out:
        m = _read(a.model)
        cal = CF.Calib2().fit(X, y, C=a.C)
        m = dict(m, calib_fix=cal, calib_info=dict(
            fit="calib_resolve.py: dev OOF constrained re-solves (simulated golfer, max %d taps)" % MAX_TAPS,
            rows=int(len(y)), courses=len(states), dev_oof=ev))
        with gzip.open(a.out, "wb") as fh:
            pickle.dump(m, fh)
        print("wrote", a.out, json.dumps(cal.export())[:400])


if __name__ == "__main__":
    main()
