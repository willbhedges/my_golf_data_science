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
                ys.append(int(E.tee_ok(h["tee"], list(geo.cx[h["k"]]["xy"]), t)))
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


def trans_dataset(entries, degrade=None, use_paths=True):
    """Every true move green n -> hole n+1 (not the turn): candidates = every hypothesis of every other green."""
    import random
    import scene as S
    out = []
    for e in entries:
        sc, truth, N, _ = E.load(e)
        if N not in (9, 18):
            continue
        if degrade:
            sc = S.degrade(sc, random.Random(f"fit-{e['slug']}"), level=degrade)
        hyps, geo = V.hypotheses(sc)
        if not len(geo.C) or not len(geo.G):
            continue
        keep = list(range(len(geo.G)))
        pb = V.Problem(sc, hyps, geo, keep, use_paths=use_paths)
        tg = [E.true_green(geo.G, geo.gr_r, t["green"]) for t in truth]
        for n in range(N - 1):
            if (N == 18 and n == 8) or tg[n] is None or tg[n + 1] is None:
                continue
            a = tg[n]
            X, off, y = [], [], []
            for b in range(len(keep)):
                if b == a:
                    continue
                for h, x in enumerate(pb.hk[b]):
                    X.append(pb.F[a, b, h])
                    off.append(x["score"])
                    y.append(int(b == tg[n + 1] and E.tee_ok(x["tee"], list(geo.cx[x["k"]]["xy"]), truth[n + 1])))
            if any(y):
                out.append((np.array(X), np.array(off), np.array(y)))
    return out


def fit_trans(data, w0, l2=0.01):
    from scipy.optimize import minimize

    def nll(w):
        s, g = 0.0, np.zeros_like(w)
        for x, off, y in data:
            z = x @ w + off
            p = np.exp(z - z.max())
            p /= p.sum()
            pc = p * y
            s -= np.log(pc.sum())
            g -= (pc / pc.sum()) @ x - p @ x
        return s + l2 * ((w - w0) ** 2).sum(), g + 2 * l2 * (w - w0)
    r = minimize(nll, w0, jac=True, method="L-BFGS-B")
    acc = np.mean([y[np.argmax(x @ r.x + off)] for x, off, y in data])
    acc0 = np.mean([y[np.argmax(x @ w0 + off)] for x, off, y in data])
    return r.x, r.fun, acc, acc0


def pos_par(entries):
    """P(par | hole number) / P(par) on the dev courses' OSM par tags (Dirichlet-smoothed, 18 x 3)."""
    cnt = np.ones((18, 3)) * 2.0
    for e in entries:
        _, truth, N, _ = E.load(e)
        if N != 18:
            continue
        for t in truth:
            if t["par"] in (3, 4, 5):
                cnt[t["ref"] - 1, t["par"] - 3] += 1
    p = cnt / cnt.sum(1, keepdims=True)
    base = cnt.sum(0) / cnt.sum()
    return np.round(p / base[None, :], 4).tolist()


def calibrate(results_path):
    """Platt scaling of the per-hole confidence on dev eval rows: P(correct) = sigmoid(a * logit(conf) + b)."""
    from scipy.optimize import minimize
    rows = [r for r in json.load(open(results_path))["rows"] if r.get("split") == "dev" and r.get("config") == "full"]
    c = np.clip(np.array([x for r in rows for x in r.get("conf_raw", r["conf"])]), 1e-4, 1 - 1e-4)
    y = np.array([x for r in rows for x in r["correct"]])
    z = np.log(c / (1 - c))

    def nll(p):
        q = 1 / (1 + np.exp(-(p[0] * z + p[1])))
        q = np.clip(q, 1e-6, 1 - 1e-6)
        return -(y * np.log(q) + (1 - y) * np.log(1 - q)).sum()
    r = minimize(nll, [1.0, 0.0])
    p = json.load(open(os.path.join(HERE, "params.json")))
    p["calib"] = [round(float(r.x[0]), 4), round(float(r.x[1]), 4)]
    json.dump(p, open(os.path.join(HERE, "params.json"), "w"), indent=1)
    print("calibration", p["calib"], "holes", len(y))


def fit_swap():
    """Front / back nine classifier on the dev courses' true routes: features of the true orientation (DP score
    difference under the fitted model + clubhouse / practice / range / parking / length cues), antisymmetric
    logistic regression without intercept."""
    from scipy.optimize import minimize
    X = []
    for e in E.courses("dev"):
        sc, truth, N, _ = E.load(e)
        if N != 18 or len(sc.greens) < 16 or len(sc.tees) < 16:
            continue
        try:
            res = V.solve(sc, n_holes=18, return_debug=True)
        except Exception:                                                 # noqa: BLE001
            continue
        d = res["debug"]
        geo, pb, br = d["geo"], d["pb"], d["br"]
        tg = [E.true_green(geo.G, geo.gr_r, t["green"]) for t in truth]
        if any(g is None or g not in pb.keep for g in tg):
            continue
        seq = [pb.keep.index(g) for g in tg]
        x = V.route_swap_x(sc, geo, pb, br, seq)
        x["dp"] = V.route_score(br["mats"], seq) - V.route_score(br["mats"], seq[9:] + seq[:9])
        X.append([x.get(k, 0.0) for k in V.SWAP_FEATS])
    X = np.array(X)

    def nll(w):
        z = X @ w
        return np.logaddexp(0, -z).sum() + 0.5 * (w ** 2).sum()
    r = minimize(nll, np.zeros(X.shape[1]))
    acc = float(((X @ r.x) > 0).mean())
    print("swap classifier", len(X), "routes, accuracy on dev", round(acc, 3), dict(zip(V.SWAP_FEATS, np.round(r.x, 3))))
    for j, k in enumerate(V.SWAP_FEATS):
        print("  alone", k, round(float((np.sign(X[:, j]) > 0).mean()), 3), "nonzero", int((X[:, j] != 0).sum()))
    p = json.load(open(os.path.join(HERE, "params.json")))
    p["swap_w"] = {k: round(float(v), 4) for k, v in zip(V.SWAP_FEATS, r.x)}
    json.dump(p, open(os.path.join(HERE, "params.json"), "w"), indent=1)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--swap":
        return fit_swap()
    if len(sys.argv) > 2 and sys.argv[1] == "--calibrate":
        return calibrate(sys.argv[2])
    ents = E.courses("dev")
    X, Y, _ = dataset(ents)
    Xd, Yd, _ = dataset(ents, degrade=1.0)
    w0 = np.array([V.FORM_W.get(k, 0.0) for k in V.FEATS])
    print("init top1", top1(X, Y, w0), "degraded", top1(Xd, Yd, w0))
    w, f = fit(X + Xd, Y + Yd, w0)
    print("fit", dict(zip(V.FEATS, np.round(w, 3))), "nll", round(f, 1))
    print("top1", top1(X, Y, w), "degraded", top1(Xd, Yd, w))
    p = json.load(open(os.path.join(HERE, "params.json"))) if os.path.exists(os.path.join(HERE, "params.json")) else {}
    p["form_w"] = {k: round(float(v), 4) for k, v in zip(V.FEATS, w)}
    p["pos_par"] = pos_par(ents)
    p["fit_note"] = f"conditional logit on dev ({len(X)} holes clean + degraded), fit.py"
    json.dump(p, open(os.path.join(HERE, "params.json"), "w"), indent=1)
    V.load_params()
    td = trans_dataset(ents) + trans_dataset(ents, degrade=1.0)
    t0 = np.array([V.TRANS_W.get(k, 0.0) for k in V.TFEATS])
    tw, tf, acc, acc0 = fit_trans(td, t0)
    print("transitions", len(td), "top1 next hole", round(acc0, 3), "->", round(acc, 3), dict(zip(V.TFEATS, np.round(tw, 3))))
    p["trans_w"] = {k: round(float(v), 4) for k, v in zip(V.TFEATS, tw)}
    json.dump(p, open(os.path.join(HERE, "params.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
