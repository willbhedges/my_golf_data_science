"""Self-calibrated unmown score: LDA between this side's mown reference (fairway + rough inside the line) and the
ground outside the line, refined EM-style with the line itself."""
import numpy as np, sys, os
sys.path.insert(0, "/home/user/my_golf_data_science/course_data/product"); sys.path.insert(0, "/home/user/my_golf_data_science/course_data/mapper")
import mowing_line as ML
KEYS = ("tex", "tex9", "ntex", "ndvi", "gray", "exg", "hag25")

def side_score(g, f, m, side, near=(1, 6), far=(22, 45), iters=2, params=None, keys=KEYS, ret_sep=False):
    sh = g["shape"]; d = m["d"]; X = np.tile(ML.XS, (sh[0], 1))
    sm = (X < 0) if side == "L" else (X > 0)
    V = np.stack([np.nan_to_num(f[k]) for k in keys], -1)
    open_ = m["open"] & sm & (d > 0) & (np.abs(X) <= ML.REACH)
    fw = (d <= 0) & ~m["tree"] & (np.abs(X) <= ML.REACH)
    mown = (open_ & (d >= near[0]) & (d < near[1]))
    unm = open_ & (d >= far[0]) & (d <= far[1])
    p = np.full(sh, np.nan, np.float32); sep = 0.0; ln = None
    for it in range(iters + 1):
        if mown.sum() < 50 or unm.sum() < 50: break
        A, B = V[mown], V[unm]
        mu0, mu1 = A.mean(0), B.mean(0)
        Sg = (np.cov(A.T) * len(A) + np.cov(B.T) * len(B)) / (len(A) + len(B))
        Sg = Sg + np.eye(len(keys)) * (1e-6 + 0.05 * np.trace(Sg) / len(keys))
        w = np.linalg.solve(Sg, mu1 - mu0)
        sep = float(w @ (mu1 - mu0))                      # squared Mahalanobis distance between the classes
        s = (V - (mu0 + mu1) / 2) @ w
        p = (1 / (1 + np.exp(-np.clip(s, -30, 30)))).astype(np.float32)
        p[~m["open"]] = np.nan
        if it == iters: break
        ln = ML.detect(g, p, side, m, params)
        band = ML.band_mask(g, ln, side)
        mown2 = open_ & ~band & (d < 45); unm2 = open_ & band
        if mown2.sum() < 50 or unm2.sum() < 50: break
        mown, unm = mown2, unm2
    return (p, sep) if ret_sep else p

def self_score(g, f, m, **kw):
    pl = side_score(g, f, m, "L", **kw); pr = side_score(g, f, m, "R", **kw)
    X = np.tile(ML.XS, (g["shape"][0], 1))
    return np.where(X < 0, pl, pr)


def _lda(A, B, shrink=0.05):
    mu0, mu1 = A.mean(0), B.mean(0)
    Sg = (np.cov(A.T) * len(A) + np.cov(B.T) * len(B)) / (len(A) + len(B))
    Sg = Sg + np.eye(A.shape[1]) * (1e-6 + shrink * np.trace(Sg) / A.shape[1])
    w = np.linalg.solve(Sg, mu1 - mu0)
    return w, (mu0 + mu1) / 2, float(w @ (mu1 - mu0))


def course_score(G, sides, near=(1, 6), far=(22, 45), iters=2, params=None, keys=KEYS, mix=0.0):
    """{ref: {side: p grid}} with ONE mown-vs-unmown direction for the whole course (pooled over the fired sides),
    refined with the detected lines. mix > 0: per-side LDA blended in (weight mix)."""
    prep = {}
    for ref, ss in sides.items():
        if ref not in G or not ss: continue
        g = G[ref]; f, m = ML.features(g); sh = g["shape"]; X = np.tile(ML.XS, (sh[0], 1)); d = m["d"]
        V = np.stack([np.nan_to_num(f[k]) for k in keys], -1)
        for s in ss:
            sm = (X < 0) if s == "L" else (X > 0)
            open_ = m["open"] & sm & (d > 0) & (np.abs(X) <= ML.REACH)
            prep[(ref, s)] = dict(g=g, m=m, V=V, open=open_, mown=open_ & (d >= near[0]) & (d < near[1]), unm=open_ & (d >= far[0]) & (d <= far[1]), d=d)
    out = {}; lines = {}
    rng = np.random.default_rng(0)
    for it in range(iters + 1):
        A = np.concatenate([q["V"][q["mown"]] for q in prep.values()]); B = np.concatenate([q["V"][q["unm"]] for q in prep.values()])
        if len(A) < 200 or len(B) < 200: break
        w, c, sep = _lda(A, B)
        for key, q in prep.items():
            s_ = (q["V"] - c) @ w
            if mix > 0 and q["mown"].sum() > 100 and q["unm"].sum() > 100:
                w2, c2, _ = _lda(q["V"][q["mown"]], q["V"][q["unm"]])
                s_ = (1 - mix) * s_ + mix * ((q["V"] - c2) @ w2)
            p = (1 / (1 + np.exp(-np.clip(s_, -30, 30)))).astype(np.float32); p[~q["m"]["open"]] = np.nan
            q["p"] = p
            ln = ML.detect(q["g"], p, key[1], q["m"], params); q["ln"] = ln
            if it < iters:
                band = ML.band_mask(q["g"], ln, key[1])
                mown2 = q["open"] & ~band & (q["d"] < 45); unm2 = q["open"] & band
                if mown2.sum() >= 50 and unm2.sum() >= 50: q["mown"], q["unm"] = mown2, unm2
    for (ref, s), q in prep.items():
        out.setdefault(ref, {})[s] = (q.get("p"), q.get("ln"))
    return out, sep
