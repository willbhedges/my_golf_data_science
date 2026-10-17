"""Fit the formation weights (conditional logit: which complex is a green's tee) on the dev courses only.

    python course_data/structure/fit.py            -> params.json (form_w), prints top-1 formation accuracy

For every true hole of a dev course (eval.courses("dev"), hole hints hidden), the candidates are all of its green's
(complex) hypotheses; the label is eval's tee criterion. The weights maximise the log-probability of the correct
candidates under a softmax within each green (L2 0.01).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eval as E                                                     # noqa: E402
import solver as V                                                   # noqa: E402


def dataset(entries, degrade=None):
    import random
    import scene as S
    X, Y, meta = [], [], []
    for e in entries:
        sc, truth, N, _ = E.load(e)
        if N not in (9, 18):
            continue
        if degrade:
            sc = S.degrade(sc, random.Random(f"fit-{e['slug']}"), level=degrade)
        hyps, geo = V.hypotheses(sc, topk=200)
        R = geo.gr_r
        for t in truth:
            gi = E.true_green(geo.G, R, t["green"])
            if gi is None or not hyps[gi]:
                continue
            ys = []
            for h in hyps[gi]:
                xy = geo.cx[h["k"]]["xy"]
                dmin = float(np.hypot(*(xy - t["tee"]).T).min())
                ys.append(int(dmin <= 35 or E._seg_dist(h["tee"], E._first(t["line"])) <= 25))
            X.append(np.array([[h["f"][k] for k in V.FEATS] for h in hyps[gi]]))
            Y.append(np.array(ys))
            meta.append((e["slug"], t["ref"]))
    return X, Y, meta


def fit(X, Y, w0, l2=0.01):
    from scipy.optimize import minimize
    XY = [(x, y) for x, y in zip(X, Y) if y.any()]

    def nll(w):
        s, g = 0.0, np.zeros_like(w)
        for x, y in XY:
            z = x @ w
            p = np.exp(z - z.max())
            p /= p.sum()
            pc = p * y
            s -= np.log(pc.sum())
            g -= (pc / pc.sum()) @ x - p @ x
        return s + l2 * (w ** 2).sum(), g + 2 * l2 * w
    r = minimize(nll, w0, jac=True, method="L-BFGS-B")
    return r.x, r.fun


def top1(X, Y, w):
    ok = [int(y[np.argmax(x @ w)]) for x, y in zip(X, Y) if len(y)]
    return float(np.mean(ok)), int(sum(1 for y in Y if y.any())) / max(1, len(Y))


def main():
    ents = E.courses("dev")
    X, Y, _ = dataset(ents)
    Xd, Yd, _ = dataset(ents, degrade=1.0)
    w0 = np.array([V.FORM_W[k] for k in V.FEATS])
    print("init top1", top1(X, Y, w0), "degraded", top1(Xd, Yd, w0))
    w, f = fit(X + Xd, Y + Yd, w0)
    print("fit", dict(zip(V.FEATS, np.round(w, 3))), "nll", round(f, 1))
    print("top1", top1(X, Y, w), "degraded", top1(Xd, Yd, w))
    p = json.load(open(os.path.join(HERE, "params.json"))) if os.path.exists(os.path.join(HERE, "params.json")) else {}
    p["form_w"] = {k: round(float(v), 4) for k, v in zip(V.FEATS, w)}
    p["fit_note"] = f"conditional logit on dev ({len(X)} holes clean + degraded), fit.py"
    json.dump(p, open(os.path.join(HERE, "params.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
