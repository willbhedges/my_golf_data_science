"""Confirm-tap policies for resolve2.Session (sticky re-solve, Yes-without-re-solve, ask order), simulated golfer.

    python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split dev --folds FOLDS.pkl \
        --policy sticky:alpha=5,keep=1 --json OUT.json [--jobs 3]
    python course_data/zero_tap/pathroute_v2/sim3.py --c1 C1 --c2 C2 --split test --policy ... --json OUT.json

dev: out-of-fold (each course decoded by the hole / walk / tee-pair models of the 4 other folds, calib_resolve.py's
fold pickle; the calibrators of model_v2.pkl.gz were fit on dev, so they are in-sample there). test: model_v2.
The golfer is sim2's (answer from truth: "hole N is this tee + green" or "not a hole"); the trajectory is written in
sim2's format, so sim2_report.summarise gives taps to 98 % pair precision (global stop threshold on the remaining
confidence), all pairs right at that stop and numbering with one hole-1 tap (decoded at every state).

Policy string: name:key=value,...
  resolve = all | no | fix | never   re-solve after every answer / not after a "yes" / only after a correction
                               (a different tee for the green; "not a hole" drops the hole) / never (= no resolve)
  alpha, pin, pin_w, keep      resolve2.STICKY (alpha=0, pin>1, keep=0 = the old plain re-solve)
  num = 1 | 0                  a confirmation carries its hole number (pinned position) or is pair-only
  ask = low | voi              lowest confidence, or (1 - conf) * (1 + nb) with nb = unconfirmed tour neighbours
"""
from __future__ import annotations

import argparse
import copy
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
import resolve2 as RS  # noqa: E402
import sim2 as SIM  # noqa: E402

MAX_TAPS = 30
_G = {}


def parse_policy(s):
    name, _, kv = s.partition(":")
    p = dict(name=name, resolve="all", ask="low", sticky=None, num=True)
    st = dict(RS.STICKY)
    for item in filter(None, kv.split(",")):
        k, v = item.split("=")
        if k in ("resolve", "ask"):
            p[k] = v
        elif k == "num":
            p["num"] = bool(int(v))
        elif k == "plain":
            p["sticky"] = None if v == "1" else p["sticky"]
        else:
            st[k] = float(v) if k != "keep" else bool(int(v))
            p["sticky"] = st
    if name == "plain":
        p["sticky"] = None
    elif p["sticky"] is None and name != "plain":
        p["sticky"] = st
    return p


def ask(s, pol, thr):
    fp = s.fixed_pairs()
    un = [i for i, h in enumerate(s.holes) if (h["t"], h["g"]) not in fp and s.conf[i] < thr]
    if not un:
        return None
    if pol["ask"] == "voi":
        def nb(i):
            h = s.holes[i]
            return sum(1 for j in (i - 1, i + 1) if 0 <= j < len(s.holes) and s.holes[j]["loop"] == h["loop"]
                       and (s.holes[j]["t"], s.holes[j]["g"]) not in fp)
        return max(un, key=lambda i: ((1 - s.conf[i]) * (1 + 0.5 * nb(i)), -i))
    return min(un, key=lambda i: (s.conf[i], i))


def numbering_h1(d, s, hand, tee1):
    """Hole-1 tap on top of the current state: pairing / numbering decode with the true hole-1 tee."""
    s2 = copy.copy(s)
    s2.fix = json.loads(json.dumps(s.fix))
    s2.fix["pairs"] = [tuple(p) for p in s2.fix["pairs"]]
    if s2.fix.get("reject"):
        s2.fix["reject"] = [tuple(p) for p in s2.fix["reject"]]
    s2.prev = dict(s.prev)
    s2.hole_one(tee1)
    s2.solve(conf=False)
    if not s2.holes:
        return None
    s2.conf = np.ones(len(s2.holes))
    y, N, miss, num = SIM.state(d, s2, hand)
    return dict(num=num, y=y.tolist(), N=N)


def simulate(d, pr, cal, calf, pol):
    slug = d["slug"]
    Mt = B.Matcher(B.truth(slug))
    single = d["kind"] in (9, 18)
    s = RS.Session(d, pr, cal, calib_fix=calf, sticky=pol["sticky"])
    s.solve()
    j1 = next((j for j, hh in enumerate(Mt.holes) if hh["ref"] == 1), None)
    tees1 = [tt for tt, x in enumerate(d["tees"]) if j1 is not None and Mt.tee_ok(j1, [SIM._scene_pos(Mt, x["ll"])])]
    hand, done, traj, h1 = {}, set(), [], {}
    flips = 0

    def snap(n_taps):
        y, N, miss, num = SIM.state(d, s, hand)
        fp = s.fixed_pairs()
        un = [c for h, c in zip(s.holes, s.conf) if (h["t"], h["g"]) not in fp]
        traj.append(dict(taps=n_taps, min_un=float(min(un)) if un else 1.0,
                         conf=[round(float(c), 4) for c in s.conf], y=y.tolist(), N=N, miss=miss, num=num,
                         kept=list(getattr(s, "kept", None) or [])))
        if single and tees1 and not _G.get("no_h1"):
            r = numbering_h1(d, s, hand, tees1[0])
            if r:
                h1[len(traj) - 1] = r
        return y
    y_prev = snap(0)
    right_prev = {(h["t"], h["g"]) for h, ok in zip(s.holes, y_prev) if ok}
    taps = 0
    while taps < MAX_TAPS:
        i = ask(s, pol, SIM.CAP)
        if i is None:
            break
        h = s.holes[i]
        j, tees = SIM.answer(d, Mt, h["g"], done)
        taps += 1
        yes = False
        if j is None:
            s.not_a_hole(h["g"])
        else:
            done.add(j)
            num = Mt.holes[j]["ref"] if single and pol["num"] else None
            tees = [t for t in tees if t not in {p[1] for p in s.fix["pairs"]}]
            if tees:
                t2 = min(tees, key=lambda t: (t not in [h["t"]] + list(h["boxes"]), t))
            else:
                t2 = h["t"]
                hand[(t2, h["g"])] = j
            yes = t2 == h["t"]
            s.confirm_pair(num, t2, h["g"])
        if j is None and pol["resolve"] == "fix":           # "not a hole": drop it, no re-solve (the golfer adds the
            s.drop_hole(i)                                  # true hole if it is missing: one tap, sim2's `miss`)
        elif yes and pol["resolve"] in ("no", "never", "fix"):
            s.fix["pairs"] = s.fix["pairs"][:-1]
            s.confirm_yes(i, num)                       # the shipped "yes" path (resolve2.Session.confirm_yes)
        elif pol["resolve"] == "never":
            s.conf = np.array(s.conf, float)
            s.conf[i] = 1.0
            s.prev.pop((h["t"], h["g"]), None)
            if not yes:          # no re-decode: the corrected hole is right
                h2 = dict(h, t=s.fix["pairs"][-1][1]) if j is not None else None
                if h2 is None:
                    s.holes = [x for k, x in enumerate(s.holes) if k != i]
                    s.conf = np.delete(s.conf, i)
                else:
                    s.holes = [h2 if k == i else x for k, x in enumerate(s.holes)]
        else:
            s.solve()
        if not s.holes:
            break
        y = snap(taps)
        now = {(hh["t"], hh["g"]) for hh, ok in zip(s.holes, y) if ok}
        flips += len(right_prev - now - {(hh["t"], hh["g"]) for hh in [h]})
        right_prev = now
    return dict(slug=slug, kind=d["kind"], traj=traj, hole1=h1, hole1_tee_found=bool(tees1), flips=flips)


def _read(p):
    with (gzip.open if p.endswith(".gz") else open)(p, "rb") as fh:
        return pickle.load(fh)


def _init(c1, c2, split, model, folds):
    _G["d"] = {d["slug"]: d for d in R2.load(c1, c2, split) if not d.get("error")}
    m = _read(model)
    _G["cal"], _G["calf"] = m["calib"], m.get("calib_fix")
    if folds:
        _G["fi"] = R1.folds(list(_G["d"].values()), 5)
        _G["F"] = _read(folds)
    else:
        _G["F"] = None
        _G["M"] = m["models"]


def _sim(args):
    slug, pol = args
    try:
        d = _G["d"][slug]
        Mo = _G["F"][_G["fi"][slug]] if _G["F"] is not None else _G["M"]
        return simulate(d, Mo.predict(d), _G["cal"], _G["calf"], pol)
    except Exception as e:                                    # noqa: BLE001
        import traceback
        return dict(slug=slug, error=f"{type(e).__name__}: {e} {traceback.format_exc()[-400:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c1", required=True)
    ap.add_argument("--c2", required=True)
    ap.add_argument("--split", default="dev")
    ap.add_argument("--model", default=os.path.join(HERE, "model_v2.pkl.gz"))
    ap.add_argument("--folds")
    ap.add_argument("--policy", action="append", required=True)
    ap.add_argument("--json", required=True, help="output; with several policies: a {policy: sim} dict")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--courses")
    ap.add_argument("--no-h1", action="store_true", help="skip the hole-1 numbering decode (faster tuning)")
    a = ap.parse_args()
    _G["no_h1"] = a.no_h1
    t0 = time.time()
    slugs = [d["slug"] for d in R2.load(a.c1, a.c2, a.split) if not d.get("error")]
    if a.courses:
        slugs = [s for s in slugs if s in a.courses.split(",")]
    pols = {p: parse_policy(p) for p in a.policy}
    res = {p: [] for p in pols}
    with Pool(a.jobs, initializer=_init, initargs=(a.c1, a.c2, a.split, a.model, a.folds)) as pool:
        for r, (slug, pol) in zip(pool.imap(_sim, [(s, pols[p]) for p in pols for s in slugs]),
                                  [(s, p) for p in pols for s in slugs]):
            res[pol].append(r)
            if r.get("error"):
                print(pol, slug, r["error"], flush=True)
    print(f"{len(slugs)} courses x {len(pols)} policies {time.time() - t0:.0f}s", flush=True)
    json.dump(res, open(a.json, "w"))


if __name__ == "__main__":
    main()
