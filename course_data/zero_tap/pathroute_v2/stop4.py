"""Course-level stop rule for confirm taps: stop asking when P(every pair right) >= target.

    python course_data/zero_tap/pathroute_v2/stop4.py fit DEV.json [--policy P] --out STOP.json
    python course_data/zero_tap/pathroute_v2/stop4.py eval SIM.json [--stop STOP.json] [--split test] [--targets 0.9,0.95]

A sim3.py trajectory holds, per state (after each answer), the per-hole confidences (confirmed = 1), y (pair right),
N / miss (true holes, golfer-added holes) and nfix / nh. Two estimates of P(all pairs right) of a state:
  prod   product of the unconfirmed holes' calibrated confidences (independence);
  learn  logistic regression on [sum log conf, min log conf, holes < 0.9, holes < 0.99, confirmed fraction, holes
         missing vs the course kind] fit on dev states (out-of-fold over courses for the dev numbers), label = every
         decoded pair right (golfer-added missing holes count as right: the golfer places them, one tap each).
The stop is the first state with P >= target (else the end of the trajectory: every unconfirmed hole >= 0.999 or 30
taps). Taps at the stop = answers + golfer-added holes. The same features are computed by pathroute_engine.js
(Session.pAll) for the app.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute"), ZT]

FEATS = ["slog", "mlog", "n90", "n99", "ffix", "deficit"]
EPS = 1e-4


def feats(conf, nfix, nh, kind):
    """conf: per decoded hole (confirmed holes = 1.0, nfix of them); -> feature vector (FEATS order)."""
    c = np.sort(np.asarray(conf, float))
    un = c[:max(0, len(c) - int(nfix))] if nfix else c         # confirmed holes have conf 1.0 (sorted last)
    lg = np.log(np.clip(un, EPS, 1.0))
    return np.array([lg.sum(), lg.min() if len(lg) else 0.0, float(np.sum(un < 0.9)), float(np.sum(un < 0.99)),
                     nfix / max(nh, 1), float(max(0, int(kind) - int(nh)))])


def p_prod(conf, nfix):
    c = np.sort(np.asarray(conf, float))
    un = c[:max(0, len(c) - int(nfix))] if nfix else c
    return float(np.prod(np.clip(un, 0, 1)))


class Learn:
    def __init__(self, C=1.0):
        self.C = C

    def fit(self, X, y):
        from sklearn.linear_model import LogisticRegression
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
        self.m = LogisticRegression(C=self.C, max_iter=2000).fit((X - self.mu) / self.sd, y)
        return self

    def predict(self, X):
        return self.m.predict_proba((np.atleast_2d(X) - self.mu) / self.sd)[:, 1]

    def to_json(self):
        """Raw-feature logistic: p = sigmoid(b + sum w_k x_k)."""
        w = self.m.coef_[0] / self.sd
        return dict(feats=FEATS, w=[round(float(x), 8) for x in w],
                    b=round(float(self.m.intercept_[0] - np.sum(self.m.coef_[0] * self.mu / self.sd)), 8), eps=EPS)


def p_learn_json(js, f):
    z = js["b"] + float(np.dot(js["w"], f))
    return 1.0 / (1.0 + np.exp(-z))


def rows(sim):
    """-> list per course of per-state dicts (features, P_prod, label, taps)."""
    out = []
    for r in sim:
        if r.get("error") or not r.get("traj"):
            continue
        st = []
        for s in r["traj"]:
            nfix = s.get("nfix")
            if nfix is None:
                nfix = sum(1 for c in s["conf"] if c >= 1.0)
            nh = s.get("nh", len(s["conf"]))
            y = np.asarray(s["y"])
            st.append(dict(f=feats(s["conf"], nfix, nh, r["kind"]), pp=p_prod(s["conf"], nfix),
                           ok=int(len(y) > 0 and y.sum() == len(y)), strict=int(y.sum() == s["N"] and s["miss"] == 0),
                           taps=s["taps"] + s["miss"], right=int(y.sum()) + s["miss"], total=len(y) + s["miss"],
                           num=s.get("num", 0), N=s["N"]))
        out.append(dict(slug=r["slug"], kind=r["kind"], st=st, hole1=r.get("hole1") or {}))
    return out


def course_folds(R, k=5):
    return {c["slug"]: i % k for i, c in enumerate(sorted(R, key=lambda c: c["slug"]))}


def fit_learn(R, C=1.0):
    X = np.array([s["f"] for c in R for s in c["st"]])
    y = np.array([s["ok"] for c in R for s in c["st"]])
    return Learn(C).fit(X, y)


def score_oof(R, C=1.0):
    """Dev: P_learn of each state from a model fit on the other folds' courses."""
    fo = course_folds(R)
    for f in range(5):
        m = fit_learn([c for c in R if fo[c["slug"]] != f], C)
        for c in R:
            if fo[c["slug"]] == f:
                P = m.predict(np.array([s["f"] for s in c["st"]]))
                for s, p in zip(c["st"], P):
                    s["pl"] = float(p)


def stop_eval(R, key, target, n_missing=()):
    """Stop at the first state with s[key] >= target. n_missing: no-result courses (one tap per true hole)."""
    taps, ok, strict, right, total, num, numN, alln, ncrs, full = [], [], [], 0, 0, 0, 0, 0, 0, []
    for c in R:
        k = next((i for i, s in enumerate(c["st"]) if s[key] >= target), len(c["st"]) - 1)
        s = c["st"][k]
        taps.append(s["taps"])
        ok.append(s["ok"])
        strict.append(s["strict"])
        right += s["right"]
        total += s["total"]
        if c["kind"] in (9, 18):
            h = c["hole1"].get(str(k), c["hole1"].get(k))
            ncrs += 1
            numN += s["N"]
            nn = h["num"] if h else s["num"]
            num += nn
            alln += int(bool(h) and nn == s["N"])
            yh = np.asarray(h["y"]) if h else None           # after the hole-1 tap: the shown route = the h1 decode
            full.append(int(bool(h) and len(yh) > 0 and yh.sum() == len(yh) and nn == s["N"]))
        else:
            full.append(s["ok"])
    for N in n_missing:
        taps.append(N)
        ok.append(1)
        strict.append(1)
        full.append(1)
        right += N
        total += N
    t = np.array(taps, float)
    return dict(target=target, n=len(t), taps_mean=round(float(t.mean()), 2), median=float(np.median(t)),
                p90=round(float(np.percentile(t, 90)), 1), zero=round(float(np.mean(t == 0)), 3),
                all_right=round(float(np.mean(ok)), 3), all_right_strict=round(float(np.mean(strict)), 3),
                precision=round(right / max(total, 1), 4), fully_right=round(float(np.mean(full)), 3),
                **({"numbered_h1": round(num / numN, 4), "all_numbered_h1": round(alln / ncrs, 3)} if numN else {}))


def oracle(R, n_missing=()):
    t = [next((s["taps"] for s in c["st"] if s["ok"]), c["st"][-1]["taps"]) for c in R] + list(n_missing)
    t = np.array(t, float)
    return dict(mean=round(float(t.mean()), 2), median=float(np.median(t)), p90=round(float(np.percentile(t, 90)), 1))


def reliability(R, key, bins=(0, .5, .8, .9, .95, .98, 1.01)):
    P = np.array([s[key] for c in R for s in c["st"]])
    y = np.array([s["ok"] for c in R for s in c["st"]])
    out = []
    for a, b in zip(bins, bins[1:]):
        m = (P >= a) & (P < b)
        if m.any():
            out.append(dict(bin=f"{a:.2f}-{min(b, 1):.2f}", n=int(m.sum()), p=round(float(P[m].mean()), 3),
                            right=round(float(y[m].mean()), 3)))
    return out


def missing_courses(sim, split):
    import bench as B
    have = {r["slug"] for r in sim if not r.get("error") and r.get("traj")}
    return [B.truth(r["slug"])["n_holes"] for r in B.courses(split) if r["slug"] not in have]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["fit", "eval"])
    ap.add_argument("sim")
    ap.add_argument("--policy", action="append")
    ap.add_argument("--stop", help="eval: learned stop model (fit's --out); dev without it: out-of-fold")
    ap.add_argument("--out")
    ap.add_argument("--split", default="dev")
    ap.add_argument("--targets", default="0.9,0.95")
    ap.add_argument("--C", type=float, default=1.0)
    a = ap.parse_args()
    S = json.load(open(a.sim))
    if isinstance(S, list):
        S = {"sim": S}
    pols = a.policy or list(S)
    if a.mode == "fit":
        R = [c for p in pols for c in rows(S[p])]
        m = fit_learn(R, a.C)
        js = dict(m.to_json(), trained_on=f"{a.sim} {pols}", n_states=sum(len(c["st"]) for c in R))
        print(json.dumps(js))
        if a.out:
            json.dump(js, open(a.out, "w"), indent=1)
        return
    js = json.load(open(a.stop)) if a.stop else None
    report = {}
    for p in pols:
        R = rows(S[p])
        nm = missing_courses(S[p], a.split)
        if js:
            for c in R:
                for s in c["st"]:
                    s["pl"] = float(p_learn_json(js, s["f"]))
        else:
            score_oof(R, a.C)
        rep = dict(oracle_all_right=oracle(R, nm), n_missing=len(nm))
        for key in ("pp", "pl"):
            rep[key] = [stop_eval(R, key, float(t), nm) for t in a.targets.split(",")]
            rep[key + "_reliability"] = reliability(R, key)
        report[p] = rep
        print(p, json.dumps(rep["oracle_all_right"]))
        for key in ("pp", "pl"):
            for x in rep[key]:
                print(f"  {key} {x}")
    if a.out:
        json.dump(report, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
