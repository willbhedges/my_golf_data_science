"""Hole formation v2: learned pair model P(tee complex -> green) + global assignment, trained and evaluated.

    python course_data/zero_tap/formation/formation.py build [--procs 4]     # feature cache (cache/, not committed)
    python course_data/zero_tap/formation/formation.py cv                    # grouped-by-state CV on dev training courses
    python course_data/zero_tap/formation/formation.py final                 # fit on all dev training courses -> model.pkl,
                                                                             # evaluate once on gtest + held-out states
                                                                             # -> results.json, RESULTS.md

Inputs per course: mode "osm" (OSM greens / tees / fairways / ..., hole ways hidden), "perc" (blind perception scene),
each without a card, with the web card (when one was found), and with a stand-in card from the hidden ways
("truth" card, back-tee set only). See README.md.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import assign as A                                                   # noqa: E402
import data as D                                                     # noqa: E402

CACHE = os.environ.get("ZT_FORMATION_CACHE", os.path.join(HERE, "cache"))
MODES = ("osm", "perc")
CARDS = ("none", "web", "truth")
MODEL = os.path.join(HERE, "model.pkl")


# ----------------------------------------------------------------------------------------------- cache
def light(I):
    """The picklable part of an instance."""
    geo = I.geo
    return dict(slug=I.slug, state=I.state, split=I.split, mode=I.mode, card=I.card_mode, N=I.N, has_aux=I.has_aux,
                n_virtual=I.n_virtual, X=I.X.astype(np.float32), y=I.y.astype(np.int8),
                gi=np.array([p["gi"] for p in I.pairs], int), k=np.array([p["k"] for p in I.pairs], int),
                D=np.array([p["D"] for p in I.pairs], float),
                cover=[p["cover"] for p in I.pairs], tee=np.array([p["tee"] for p in I.pairs], float).reshape(-1, 2),
                true_g=I.true_g, ok=sorted(I.ok), nG=len(geo.G), nC=len(geo.C),
                G=geo.G, C=geo.C, proj=(I.sc.proj.lon0, I.sc.proj.lat0),
                greens=[dict(id=g.get("id"), p=float(g.get("p_hole", g.get("conf", 1.0)))) for g in I.sc.greens],
                cands=[dict(id=c["id"], xy=np.asarray(c["xy"]), conf=float(c.get("conf", 1.0)), virtual=bool(c.get("virtual")))
                       for c in geo.cx],
                truth=[dict(ref=t["ref"], par=t["par"], length=t["length"]) for t in I.truth])


def _job(args):
    e, mode, card = args
    p = os.path.join(CACHE, f"{e['slug']}__{mode}__{card}.pkl")
    if os.path.exists(p):
        return p
    try:
        I = D.build(e, mode, card)
        obj = light(I) if I is not None else None
    except Exception as ex:                                          # noqa: BLE001
        obj = dict(error=repr(ex)[:300])
    pickle.dump(obj, open(p, "wb"))
    return p


def build_cache(procs=4, only=None):
    os.makedirs(CACHE, exist_ok=True)
    jobs = [(e, m, c) for e in D.courses() for m in MODES for c in CARDS if not only or e["slug"] in only]
    t = time.time()
    with Pool(procs) as pool:
        for i, _ in enumerate(pool.imap_unordered(_job, jobs, chunksize=2)):
            if i % 100 == 0:
                print(i, len(jobs), round(time.time() - t), flush=True)


def load_cache(mode=None, card=None):
    out = []
    for e in D.courses():
        for m in MODES:
            for c in CARDS:
                if (mode and m != mode) or (card and c != card):
                    continue
                p = os.path.join(CACHE, f"{e['slug']}__{m}__{c}.pkl")
                if not os.path.exists(p):
                    continue
                r = pickle.load(open(p, "rb"))
                if r and "error" not in r and len(r["X"]):
                    out.append(r)
    return out


# ----------------------------------------------------------------------------------------------- model
FEATS = D.FEATS
FIDX = {n: i for i, n in enumerate(FEATS)}


def design(r):
    X = r["X"].astype(np.float64)
    perc = np.full((len(X), 1), float(r["mode"] == "perc"))
    return np.hstack([X, perc])


def fit_model(rows, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    X = np.vstack([design(r) for r in rows])
    y = np.concatenate([r["y"] for r in rows])
    clf = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=40,
                                         l2_regularization=1.0, random_state=seed)
    clf.fit(X, y)
    return clf


def pair_logit(clf, r):
    p = clf.predict_proba(design(r))[:, 1]
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p) - np.log1p(-p)


def score_matrix(r, z):
    S = np.full((r["nG"], r["nC"]), -np.inf)
    S[r["gi"], r["k"]] = z
    return S


def slack_vec(r, b0, b1):
    """Log-score of 'this green has no candidate' (practice green / missed tee): b0 + b1 * logit(1 - p_hole)."""
    ph = np.array([g["p"] for g in r["greens"]])
    ph = np.clip(ph, 0.02, 0.999)
    return b0 + b1 * (np.log1p(-ph) - np.log(ph))


def extend_back(r, m, S, back=150.0, perp=20.0):
    """A green paired with a forward tee of its hole takes the complex behind it on the same line (tee boxes of
    one hole line up along the line of play; holes start at their back-most complex), when that complex is free."""
    used = {k for _, k in m if k is not None}
    G, C = r["G"], r["C"]
    out = []
    for gi, k in m:
        if k is None:
            out.append((gi, k))
            continue
        cur = k
        for _ in range(4):
            T = C[cur]
            v = G[gi] - T
            L = float(np.hypot(*v))
            u = v / max(L, 1e-6)
            rel = C - T
            s = rel @ u
            pp = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
            cand = [j for j in np.nonzero((s < -8) & (s > -back) & (pp < perp))[0]
                    if j not in used and np.isfinite(S[gi, j]) and not r["cands"][j]["virtual"]]
            if not cand:
                break
            j = max(cand, key=lambda j: s[j])          # the nearest one behind, then repeat
            used.discard(cur)
            used.add(j)
            cur = j
        out.append((gi, cur))
    return out


EXTEND = False                                       # measured: -2 points on dev CV (forward tees were not the issue)


def solve(r, z, cal):
    S = score_matrix(r, z)
    sl = slack_vec(r, cal["b0"], cal["b1"])
    P, ps = A.sinkhorn(S, sl, temp=cal["temp"])
    m = A.map_assign(S, sl)
    if EXTEND:
        m = extend_back(r, m, S)
    return S, P, ps, m


# ----------------------------------------------------------------------------------------------- metrics
def corridor_mass(G, C, prow, gi, kt, perp=20.0, back=150.0):
    """Confidence that green gi's hole starts at the corridor of candidate kt: its marginal plus that of every other
    candidate on the same line of play (forward / back tees of the same hole: within `perp` yds of the line, from
    `back` yds behind kt to 60 % of the way to the green)."""
    T = C[kt]
    v = G[gi] - T
    L = float(np.hypot(*v))
    u = v / max(L, 1e-6)
    rel = C - T
    s = rel @ u
    pp = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
    same = (s > -back) & (s < 0.6 * L) & (pp < perp)
    same[kt] = True
    return float(min(1.0, prow[same].sum()))


def evaluate(r, P, m, S):
    """Per true hole: formed (MAP), top-1 marginal correct, its top marginal; + green-level softmax baseline."""
    ok = set(map(tuple, r["ok"]))
    amap = dict(m)
    rows = []
    for j, gi in enumerate(r["true_g"]):
        if gi is None:
            rows.append(dict(formed=0, top1=0, conf=0.0, cand=0, base=0))
            continue
        cand = int(any(g == gi for g, _ in ok))
        k = amap.get(gi)
        formed = int(k is not None and (gi, k) in ok)
        pr = P[gi]
        kt = int(np.argmax(pr)) if pr.size and pr.max() > 0 else None
        top1 = int(kt is not None and (gi, kt) in ok)
        # mass on any acceptable candidate (calibration of the hole as formed)
        pm = float(sum(pr[k2] for g2, k2 in ok if g2 == gi))
        kb = int(np.nanargmax(np.where(np.isfinite(S[gi]), S[gi], -1e9))) if np.isfinite(S[gi]).any() else None
        conf = corridor_mass(r["G"], r["C"], pr, gi, kt) if kt is not None else 0.0
        rows.append(dict(formed=formed, top1=top1, conf=conf, p_ok=pm, cand=cand,
                         indep=int(kb is not None and (gi, kb) in ok)))
    return rows


def base_rows(r):
    """Structure solver's formation score (FORM_W linear, structure.params) argmax per green: the old baseline."""
    z = r["X"][:, FIDX["base"]].astype(float)
    S = score_matrix(r, z)
    ok = set(map(tuple, r["ok"]))
    out = []
    for gi in r["true_g"]:
        if gi is None or not np.isfinite(S[gi]).any():
            out.append(0)
            continue
        out.append(int((gi, int(np.argmax(np.where(np.isfinite(S[gi]), S[gi], -1e9)))) in ok))
    return out


def ece(conf, cor, bins=10):
    conf, cor = np.asarray(conf, float), np.asarray(cor, float)
    if not len(conf):
        return float("nan"), []
    e, table = 0.0, []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        m = (conf >= lo) & ((conf < hi) | (b == bins - 1))
        if m.any():
            e += m.mean() * abs(conf[m].mean() - cor[m].mean())
            table.append([round(lo, 1), round(hi, 1), int(m.sum()), round(float(conf[m].mean()), 3),
                          round(float(cor[m].mean()), 3)])
    return float(e), table


def summarise(res):
    """res: list of (r, rows, base) -> metrics dict."""
    holes = [h for _, rows, _ in res for h in rows]
    if not holes:
        return {}
    n = len(holes)
    conf = [h["conf"] for h in holes]
    cor = [h["top1"] for h in holes]
    e, tab = ece(conf, cor)
    pok = [h.get("p_ok", 0.0) for h in holes]
    fo = [h["formed"] for h in holes]
    brier = float(np.mean((np.array(pok) - np.array(fo)) ** 2))
    return dict(courses=len(res), holes=n,
                formed=round(100 * np.mean(fo), 1),
                top1=round(100 * np.mean(cor), 1),
                indep_top1=round(100 * np.mean([h.get("indep", 0) for h in holes]), 1),
                baseline_top1=round(100 * np.mean([b for _, _, bs in res for b in bs]), 1),
                ceiling=round(100 * np.mean([h["cand"] for h in holes]), 1),
                all_formed=round(100 * np.mean([all(h["formed"] for h in rows) for _, rows, _ in res]), 1),
                ece=round(e, 3), brier=round(brier, 3), reliability=tab)


# ----------------------------------------------------------------------------------------------- calibration
def fit_cal(pred):
    """pred: list of (r, z). Grid-search temperature + slack on the (OOF) predictions by the log-loss of the true
    green's acceptable-candidate mass (+ formed rate as tie-break)."""
    best = None
    for b0 in (-6.0, -4.0, -3.0, -2.0, -1.0, 0.0):
        for b1 in (0.0, 0.5, 1.0):
            for temp in (0.6, 0.8, 1.0, 1.25, 1.5, 2.0):
                cal = dict(b0=b0, b1=b1, temp=temp)
                ll, nf, nh = 0.0, 0, 0
                for r, z in pred:
                    S = score_matrix(r, z)
                    sl = slack_vec(r, b0, b1)
                    P, _ = A.sinkhorn(S, sl, temp=temp)
                    ok = set(map(tuple, r["ok"]))
                    for gi in r["true_g"]:
                        if gi is None:
                            continue
                        pm = sum(P[gi, k] for g, k in ok if g == gi)
                        ll -= math.log(min(max(pm, 1e-4), 1 - 1e-4)) if any(g == gi for g, _ in ok) else 0.0
                        nh += 1
                key = ll / max(nh, 1)
                if best is None or key < best[0]:
                    best = (key, cal)
    return best[1], best[0]


# ----------------------------------------------------------------------------------------------- CV / final
def folds(states, k=6, seed=0):
    st = sorted(states)
    rng = np.random.default_rng(seed)
    rng.shuffle(st)
    return [set(st[i::k]) for i in range(k)]


def train_rows(rows):
    """Training rows: dev training courses, inputs without card and with the web card (truth cards are an eval
    stand-in only)."""
    return [r for r in rows if r["split"] == "train" and r["card"] in ("none", "web")]


CTX = ("z1", "P1", "row_z_other", "row_P_other", "row_rank", "col_z_other", "col_P_other", "col_rank",
       "comp_alt_gap", "own_alt_col_P", "row_soft", "p_slack", "card_ll", "card_post", "card_hole_p")


def card_of(r):
    if r["card"] == "web":
        return D.load_card(r["slug"])
    if r["card"] == "truth":
        return D.card_from_truth(r["truth"])
    return None


YD_SD, YD_TAIL, YD_BROAD = 6.0, 25.0, 0.001            # sharp is best (dev CV, oracle hole numbers)


def _yd_ll(res):
    """log density of (card yardage - straight distance): a core that is rarely short (sd YD_SD) and longer on
    dog-legs (exponential tail YD_TAIL), mixed with a broad N(0, 60) (card for other tees / unmapped tips)."""
    core = np.where(res < 0, -0.5 * (res / YD_SD) ** 2, -res / YD_TAIL) - math.log(YD_SD * 1.2533 + YD_TAIL)
    broad = -0.5 * (res / 60.0) ** 2 - math.log(60.0 * 2.5066)
    return np.logaddexp(math.log(1 - YD_BROAD) + core, math.log(YD_BROAD) + broad)


def card_match(r, card):
    """L (n_pairs x n_holes): log-likelihood ratio that pair i is card hole h, from every tee set's yardage vs the
    distances of the pair's boxes (its complex + forward complexes on its corridor) to the green, plus the par
    posterior of the length."""
    pars, Y, _ = D.card_sets(card)
    if Y is None:
        return None
    G, n = r["G"], len(r["gi"])
    H, Sn = Y.shape
    L = np.zeros((n, H))
    bg = math.log(1.0 / 250.0)
    for i in range(n):
        g = G[r["gi"][i]]
        boxes = [r["cands"][r["k"][i]]["xy"]] + [r["cands"][c]["xy"] for c in r["cover"][i] if c != r["k"][i]]
        d = np.hypot(*(np.vstack(boxes) - g).T)
        ll = _yd_ll(Y[:, 0] - r["D"][i])
        tot = np.logaddexp(math.log(0.85) + ll, math.log(0.15) + bg) - bg
        for s in range(1, Sn):
            l2 = _yd_ll(Y[:, s][:, None] - d[None, :]).max(1)
            tot = tot + 0.5 * (np.logaddexp(math.log(0.6) + l2, math.log(0.4) + bg) - bg)
        if pars is not None:
            p3, p5 = r["X"][i, FIDX["pp3"]], r["X"][i, FIDX["pp5"]]
            pp = {3: p3, 4: 1 - p3 - p5, 5: p5}
            pr = np.array([pp.get(p, 0.33) for p in pars], float)
            tot = tot + np.log(np.clip(pr, 0.02, 1.0)) - math.log(0.33)
        L[i] = tot
    return L


def card_context(r, z, card):
    """Card evidence through a soft green <-> card-hole assignment: Q[g, h] = logsumexp_k (z[g, k] + L[(g, k), h]),
    Sinkhorn over holes x greens (each card hole ends on one green) -> P(g is h); per pair: log sum_h P(g, h) exp(L)
    (normalised), its share of the green's card-weighted posterior, and P(g is some card hole)."""
    n = len(z)
    out = np.zeros((n, 3))
    L = card_match(r, card) if card else None
    if L is None:
        return out
    nG, H = r["nG"], L.shape[1]
    Q = np.full((nG, H), -np.inf)
    for i in range(n):
        g = r["gi"][i]
        Q[g] = np.logaddexp(Q[g], z[i] + L[i])
    P_hg, _ = A.sinkhorn(Q.T.copy(), np.full(H, -8.0), temp=1.0)
    Pgh = P_hg.T
    for i in range(n):
        w = Pgh[r["gi"][i]]
        if w.sum() < 1e-9:
            continue
        out[i, 0] = float(np.log(max((w * np.exp(np.clip(L[i], -30, 30))).sum() / w.sum(), 1e-12)))
        out[i, 2] = float(w.sum())
    for g in range(nG):
        idx = np.nonzero(r["gi"] == g)[0]
        if len(idx):
            a = z[idx] + out[idx, 0]
            a = np.exp(a - a.max())
            out[idx, 1] = a / a.sum()
    return out


def ctx_features(r, z, card="auto"):
    """Stage-2 context of each pair from the stage-1 logits: how it competes in its row (the green's other tees) and
    its column (other greens wanting this tee), whether the competing green has an alternative, and the stage-1
    Sinkhorn marginals."""
    S = score_matrix(r, z)
    sl = slack_vec(r, -6.0, 0.5)
    P, ps = A.sinkhorn(S, sl, temp=1.0)
    Sf = np.where(np.isfinite(S), S, -30.0)
    gi, k = r["gi"], r["k"]
    n = len(gi)
    out = np.zeros((n, len(CTX)))
    order_r = (-Sf).argsort(1).argsort(1)
    order_c = (-Sf).argsort(0).argsort(0)
    rowsm = np.exp(Sf - Sf.max(1, keepdims=True))
    rowsm = rowsm / rowsm.sum(1, keepdims=True)
    for i in range(n):
        g, c = gi[i], k[i]
        rz = Sf[g].copy(); rz[c] = -30.0
        rp = P[g].copy(); rp[c] = 0.0
        cz = Sf[:, c].copy(); cz[g] = -30.0
        cp = P[:, c].copy(); cp[g] = 0.0
        gs = int(np.argmax(cz))
        alt = Sf[gs].copy(); alt[c] = -30.0
        comp_gap = float(alt.max() - Sf[gs, c]) if cz.max() > -30 else 5.0
        ka = int(np.argmax(rz))
        oc = P[:, ka].copy(); oc[g] = 0.0
        out[i] = [z[i], P[g, c], rz.max(), rp.max(), min(order_r[g, c], 10), cz.max(), cp.max(), min(order_c[g, c], 10),
                  np.clip(comp_gap, -10, 10), oc.max(), rowsm[g, c], ps[g], 0.0, 0.0, 0.0]
    card = card_of(r) if card == "auto" else card
    if card:
        out[:, -3:] = card_context(r, z, card)
    return out


def fit_stage2(pairs, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    X = np.vstack([np.hstack([design(r), ctx_features(r, z)]) for r, z in pairs])
    y = np.concatenate([r["y"] for r, _ in pairs])
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=40,
                                         l2_regularization=1.0, random_state=seed)
    clf.fit(X, y)
    return clf


def stage2_logit(clf2, r, z, card="auto"):
    p = clf2.predict_proba(np.hstack([design(r), ctx_features(r, z, card)]))[:, 1]
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p) - np.log1p(-p)


STAGES = 2


def cv(rows, k=6, cal=None, stages=None):
    """Out-of-fold logits on the dev training courses (folds = groups of states). Stage 2 is fitted, per fold, on
    the stage-1 OOF logits of the other folds' courses."""
    stages = stages or STAGES
    tr = [r for r in rows if r["split"] == "train"]
    fs = folds({r["state"] for r in tr}, k)
    oof = {}
    for i, f in enumerate(fs):
        clf = fit_model(train_rows([r for r in tr if r["state"] not in f]))
        for r in tr:
            if r["state"] in f:
                oof[id(r)] = (r, pair_logit(clf, r))
        print("fold", i, sorted(f), flush=True)
    if stages >= 2:
        oof2 = {}
        for i, f in enumerate(fs):
            trp = [oof[id(r)] for r in tr if r["state"] not in f]          # every card variant (none, web, truth)
            c2 = fit_stage2(trp)
            for r in tr:
                if r["state"] in f:
                    oof2[id(r)] = (r, stage2_logit(c2, r, oof[id(r)][1]))
            print("stage 2 fold", i, flush=True)
        oof = oof2
    return list(oof.values())


def report(pred, cal, groups):
    out = {}
    for name, sel in groups.items():
        res = []
        for r, z in pred:
            if not sel(r):
                continue
            S, P, ps, m = solve(r, z, cal)
            res.append((r, evaluate(r, P, m, S), base_rows(r)))
        out[name] = summarise(res)
    return out


def groups_for(splits):
    g = {}
    for sp in splits:
        for mode in MODES:
            for card in CARDS:
                g[f"{sp}/{mode}/{card}"] = (lambda r, sp=sp, mode=mode, card=card:
                                            r["split"] == sp and r["mode"] == mode and r["card"] == card)
    return g


def md(results, title):
    lines = [f"### {title}", "",
             "| split / input / card | courses | holes | **formed** | top-1 per green | indep. top-1 | old baseline top-1 | candidate ceiling | all holes formed | ECE | Brier |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in results.items():
        if not v:
            continue
        lines.append(f"| {k} | {v['courses']} | {v['holes']} | **{v['formed']}%** | {v['top1']}% | {v['indep_top1']}% | "
                     f"{v['baseline_top1']}% | {v['ceiling']}% | {v['all_formed']}% | {v['ece']} | {v['brier']} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "cv", "final"])
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    if a.cmd == "build":
        build_cache(a.procs, set(a.only.split(",")) if a.only else None)
        return
    rows = load_cache()
    print(len(rows), "instances", flush=True)
    if a.cmd == "cv":
        oof = cv(rows)
        pickle.dump([((r["slug"], r["mode"], r["card"]), z) for r, z in oof], open(os.path.join(CACHE, "_oof.pkl"), "wb"))
        cal, ll = fit_cal([(r, z) for r, z in oof if r["card"] in ("none", "web")])
        print("cal", cal, round(ll, 4))
        res = report(oof, cal, groups_for(["train"]))
        json.dump(dict(cal=cal, results=res), open(os.path.join(HERE, "results_cv.json"), "w"), indent=1)
        print(md(res, "Dev training courses, cross-validated by state (6 folds)"))
        return
    # final: OOF calibration, one model on every dev training course, scored once on gtest + held-out
    oof = cv(rows)
    cal, ll = fit_cal([(r, z) for r, z in oof if r["card"] in ("none", "web")])
    res_cv = report(oof, cal, groups_for(["train"]))
    clf = fit_model(train_rows(rows))
    oof1 = cv(rows, stages=1)
    clf2 = fit_stage2(oof1) if STAGES >= 2 else None
    pickle.dump(dict(clf=clf, clf2=clf2, cal=cal, feats=list(FEATS) + ["is_perc"], trained_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     n_train=len(train_rows(rows))), open(MODEL, "wb"))
    test = []
    for r in rows:
        if r["split"] in ("gtest", "heldout"):
            z = pair_logit(clf, r)
            test.append((r, stage2_logit(clf2, r, z) if clf2 is not None else z))
    res_t = report(test, cal, groups_for(["heldout", "gtest"]))
    json.dump(dict(cal=cal, cv=res_cv, test=res_t), open(os.path.join(HERE, "results.json"), "w"), indent=1)
    txt = md(res_t, "Held-out states and generalize test courses (scored once)") + "\n" + \
        md(res_cv, "Dev training courses, cross-validated by state (6 folds)")
    open(os.path.join(HERE, "RESULTS.md"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
