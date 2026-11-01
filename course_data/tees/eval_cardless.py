"""Evaluate / fit tees/cardless.py on the zero_tap benchmark (courses with a fitting web card AND OSM tees).

    python3 course_data/tees/eval_cardless.py --fit        # fit cardless_model.json on the DEV split only
    python3 course_data/tees/eval_cardless.py              # dev + test numbers -> eval_cardless.json

Inputs per course (what a cardless run sees): the routed holes (truth hole lines tee -> green, OSM green centre and
radius; refs only for ordering), all OSM golf=tee boxes, lidar pads where the bench has them. Never the card, the
hole ways' par / dist tags or tee colour tags. Truth: the web card, cleaned (clean_sets): sets with missing holes
dropped, duplicates and combo sets (every hole equal to some other set's yardage) dropped, sets shorter than
MIN_FRAC of the back total dropped (junior / family tees).
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAIN = os.environ.get("GOLF_DATA_ROOT", "/home/user/my_golf_data_science")
sys.path[:0] = [HERE]
import cardless as CL  # noqa: E402

MIN_FRAC = 0.55


def _p(rel):
    for base in (ROOT, MAIN):
        p = os.path.join(base, rel)
        if os.path.exists(p):
            return p
    return None


def rd(rel):
    p = _p(rel) if rel else None
    if not p:
        return None
    raw = open(p, "rb").read()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def clean_sets(card, n):
    sets = []
    for name, s in (card.get("tee_sets") or {}).items():
        ys = s.get("yards") or []
        if len(ys) != n or any(not isinstance(y, (int, float)) or y <= 0 for y in ys):
            continue
        sets.append((name, [float(y) for y in ys]))
    sets.sort(key=lambda t: -sum(t[1]))
    keep = []
    for name, ys in sets:
        if any(all(abs(a - b) <= 2 for a, b in zip(ys, k[1])) for k in keep):
            continue                                       # duplicate
        keep.append((name, ys))
    out = []
    for i, (name, ys) in enumerate(keep):
        others = [k[1] for j, k in enumerate(keep) if j != i]
        if len(others) >= 2 and all(any(abs(y - o[h]) <= 2 for o in others) for h, y in enumerate(ys)):
            continue                                       # combo set
        out.append((name, ys))
    if out:
        top = sum(out[0][1])
        out = [s for s in out if sum(s[1]) >= MIN_FRAC * top]
    return out


def course_inputs(row):
    t = rd(row["files"]["truth"])
    card_doc = rd(row["files"]["card"])
    fc = rd(row["files"]["osm"])
    if not t or not card_doc or not fc:
        return None
    holes = sorted(t["holes"], key=lambda h: h["ref"])
    n = len(holes)
    if n not in (9, 18) or [h["ref"] for h in holes] != list(range(1, n + 1)):
        return None
    card = None
    for c in card_doc.get("cards") or []:
        cc = c.get("card") or {}
        if len(cc.get("par") or []) == n:
            card = cc
            break
    if not card:
        return None
    sets = clean_sets(card, n)
    if not sets:
        return None
    H = [dict(ref=h["ref"], line=[(p[1], p[0]) for p in h["line"]], green=(h["green_ll"][1], h["green_ll"][0]),
              green_r_yd=h.get("green_r_yd")) for h in holes]
    # truth alignment: a card whose nines are listed the other way round from the OSM refs (checked on the
    # line lengths; the method never sees this)
    L = [CL.hole_geometry(h)[2]["line_yd"] for h in H]
    par = [int(x) for x in card["par"]]
    swapped = False
    if n == 18:
        sw = lambda v: list(v[9:]) + list(v[:9])  # noqa: E731
        e0 = sorted(abs(a - b) for a, b in zip(L, sets[0][1]))[9]
        e1 = sorted(abs(a - b) for a, b in zip(L, sw(sets[0][1])))[9]
        if e1 < 0.5 * e0 and e0 > 25:
            sets = [(nm, sw(ys)) for nm, ys in sets]
            par, swapped = sw(par), True
    card_fit = sorted(abs(a - b) for a, b in zip(L, sets[0][1]))[n // 2]
    tees, tagged = [], {}
    for f in fc["features"]:
        p, g = f.get("properties") or {}, f.get("geometry") or {}
        if p.get("golf") == "tee" and g.get("type") in ("Polygon", "Point"):
            cs = g["coordinates"][0] if g["type"] == "Polygon" else [g["coordinates"]]
            tees.append(dict(id=f"{p.get('osm_type')}/{p.get('osm_id')}", coords=[(c[1], c[0]) for c in cs]))
        if p.get("golf") == "hole":
            for k in ("dist", "distance"):
                try:
                    tagged[str(p.get("ref"))] = float(str(p[k]).split()[0])
                except (KeyError, ValueError, IndexError):
                    pass
    pads = []
    pp = rd(row["files"].get("pads")) if row["files"].get("pads") else None
    for q in pp or []:
        pads.append(dict(id=q.get("id"), coords=[tuple(c) for c in q["coords"]], source="lidar"))
    return dict(slug=row["slug"], split=row["split"], n=n, holes=H, tees=tees, pads=pads,
                par=par, sets=sets, tagged=tagged, swapped=swapped,
                card_fit_yd=card_fit)


def load(split=None):
    man = json.load(open(_p("course_data/zero_tap/benchmark.json")))["courses"]
    out = []
    for r in man:
        if not r["in_bench"] or not (r.get("card") or {}).get("fits") or (split and r["split"] != split):
            continue
        x = course_inputs(r)
        if x:
            out.append(x)
    return out


def q(xs, f):
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(f * (len(xs) - 1) + 0.5))], 1) if xs else None


# ----------------------------------------------------------------------------- fitting (dev only)
def fit(courses, params=None):
    model = CL.load_model()
    # ratios per S from truth totals
    rat = defaultdict(list)
    for c in courses:
        S = len(c["sets"])
        tot = [sum(s[1]) for s in c["sets"]]
        rat[S].append([t / tot[0] for t in tot])
    for S in range(1, 7):
        if len(rat[S]) >= 3:
            model["ratios"][str(S)] = [round(sorted(v[i] for v in rat[S])[len(rat[S]) // 2], 4) for i in range(S)]
    # par prior
    pp = {}
    for n in (9, 18):
        cs = [c for c in courses if c["n"] == n]
        pp[str(n)] = dict(N=len(cs), total=dict(Counter(str(sum(c["par"])) for c in cs)),
                          n3=dict(Counter(str(c["par"].count(3)) for c in cs)),
                          n5=dict(Counter(str(c["par"].count(5)) for c in cs)))
    model["par_prior"] = pp
    # S table: slot-count quantile -> modal true S
    by = defaultdict(Counter)
    for c in courses:
        boxes = CL.tee_complexes(c["holes"], c["tees"], c["pads"])
        sl = [CL.slots(b, params) for b in boxes]
        if CL.PARAMS["line_start"]:
            geo = [CL.hole_geometry(h)[2] for h in c["holes"]]
            sl = [CL.with_line_start(s, g["line_yd"], params) for s, g in zip(sl, geo)]
        cs = sorted(len(s) for s in sl)
        qv = cs[int(round(CL.PARAMS["s_quantile"] * (len(cs) - 1)))]
        by[min(qv, 7)][min(max(len(c["sets"]), 2), 6)] += 1
        c["_sl"] = sl
    tab = {}
    allS = sum(by.values(), Counter())
    for k in range(0, 8):
        cnt = by.get(k, Counter()) + Counter({s: 0.5 * v / max(1, sum(allS.values())) for s, v in allS.items()})
        tab[str(k)] = int(max(cnt, key=cnt.get))
    model["s_table"] = tab
    # par softmax on predicted back / 2nd
    model["par"] = None
    X, Yp = [], []
    for c in courses:
        geo = [CL.hole_geometry(h)[2] for h in c["holes"]]
        S = len(c["sets"])
        Y, _ = CL.assign_sets(c["_sl"], max(S, 2), model, [g["line_yd"] for g in geo], params)
        for y, h, g, par in zip(Y, c["holes"], geo, c["par"]):
            if par in (3, 4, 5):
                X.append(CL.par_features(y[0], y[1], h.get("green_r_yd"), g["dogleg_deg"], g["line_yd"]))
                Yp.append(par - 3)
    model["par"] = softmax_fit(X, Yp)
    return model


def softmax_fit(X, Y, l2=1e-3, iters=3000, lr=0.5):
    import numpy as np
    X = np.array(X)
    Y = np.array(Y)
    mu, sd = X.mean(0), X.std(0)
    sd[0], mu[0] = 1.0, 0.0
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    W = np.zeros((3, X.shape[1]))
    T = np.eye(3)[Y]
    for _ in range(iters):
        L = Z @ W.T
        L -= L.max(1, keepdims=True)
        Pm = np.exp(L)
        Pm /= Pm.sum(1, keepdims=True)
        G = (Pm - T).T @ Z / len(Z) + l2 * W
        W -= lr * G
    # fold the standardisation into W (so the model takes raw features)
    Wr = W / sd
    Wr[:, 0] = W[:, 0] - (W[:, 1:] * mu[1:] / sd[1:]).sum(1)
    return Wr.round(5).tolist()


# ----------------------------------------------------------------------------- evaluation
def match_sets(pred, truth):
    """Monotone matching (by rank) of predicted to true sets minimising |total| differences (DP). Returns pairs."""
    P_, T_ = [sum(p) for p in pred], [sum(t) for t in truth]
    n, m = len(P_), len(T_)
    INF = float("inf")
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    B = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][0] = 400.0 * i
    for j in range(m + 1):
        D[0][j] = 400.0 * j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            opts = [(D[i - 1][j - 1] + abs(P_[i - 1] - T_[j - 1]), "m"), (D[i - 1][j] + 400, "p"), (D[i][j - 1] + 400, "t")]
            D[i][j], B[i][j] = min(opts)
    pairs, i, j = [], n, m
    while i > 0 and j > 0:
        b = B[i][j]
        if b == "m":
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif b == "p":
            i -= 1
        else:
            j -= 1
    return pairs[::-1]


def evaluate(courses, model, params=None, S_override=None):
    R = dict(n_courses=len(courses), holes=0, par_right=0, courses_all_par=0, S_right=0, S_pm1=0,
             err=defaultdict(list), tot_err=defaultdict(list), base=defaultdict(list), par_base_right=0,
             tagged_cov=0, per_course=[])
    for c in courses:
        S_true = len(c["sets"])
        card = CL.infer_card(c["holes"], c["tees"], c["pads"], model=model, params=params,
                             S=(S_true if S_override == "true" else None))
        S = card["diagnostics"]["S"]
        pred = [v["yards"] for v in card["tee_sets"].values()]
        truth = [s[1] for s in c["sets"]]
        R["S_right"] += S == S_true
        R["S_pm1"] += abs(S - S_true) <= 1
        pr = sum(a == b for a, b in zip(card["par"], c["par"]))
        R["holes"] += c["n"]
        R["par_right"] += pr
        R["courses_all_par"] += pr == c["n"]
        # back / 2nd by rank
        for k, nm in ((0, "back"), (1, "2nd")):
            if k < len(pred) and k < len(truth):
                R["err"][nm] += [abs(a - b) for a, b in zip(pred[k], truth[k])]
                R["tot_err"][nm].append(abs(sum(pred[k]) - sum(truth[k])))
        for i, j in match_sets(pred, truth):
            R["err"]["matched"] += [abs(a - b) for a, b in zip(pred[i], truth[j])]
            R["tot_err"]["matched"].append(abs(sum(pred[i]) - sum(truth[j])))
        # baselines: routed line length as the back set; OSM hole dist tags where present
        geo = [CL.hole_geometry(h)[2] for h in c["holes"]]
        R["base"]["line_back"] += [abs(g["line_yd"] - b) for g, b in zip(geo, truth[0])]
        if len(truth) > 1:
            R["base"]["line_2nd"] += [abs(g["line_yd"] - b) for g, b in zip(geo, truth[1])]
        for i, b in enumerate(truth[0]):
            tg = c["tagged"].get(str(i + 1))
            if tg:
                R["tagged_cov"] += 1
                R["base"]["tag_back"].append(abs(tg - b))
                R["base"]["tag_best"].append(min(abs(tg - t[i]) for t in truth))
        bpar = [3 if g["line_yd"] <= 250 else 5 if g["line_yd"] >= 470 else 4 for g in geo]
        R["par_base_right"] += sum(a == b for a, b in zip(bpar, c["par"]))
        R["per_course"].append(dict(slug=c["slug"], n=c["n"], S=S, S_true=S_true, par_right=pr,
                                    back_tot=sum(pred[0]), true_back_tot=sum(truth[0]),
                                    back_med=q([abs(a - b) for a, b in zip(pred[0], truth[0])], 0.5),
                                    slots=card["diagnostics"]["slots_per_hole"]))
    nC, nH = max(1, R["n_courses"]), max(1, R["holes"])
    out = dict(courses=R["n_courses"], holes=R["holes"],
               par_hole_acc=round(R["par_right"] / nH, 3), par_course_all_right=round(R["courses_all_par"] / nC, 3),
               par_baseline_line_thresholds=round(R["par_base_right"] / nH, 3),
               S_exact=round(R["S_right"] / nC, 3), S_within1=round(R["S_pm1"] / nC, 3),
               hole_yd_err={k: dict(n=len(v), median=q(v, .5), p90=q(v, .9), within10=round(sum(x <= 10 for x in v) / max(1, len(v)), 3))
                            for k, v in R["err"].items()},
               total_yd_err={k: dict(median=q(v, .5), p90=q(v, .9)) for k, v in R["tot_err"].items()},
               baselines={k: dict(n=len(v), median=q(v, .5), p90=q(v, .9)) for k, v in R["base"].items()},
               tagged_hole_coverage=round(R["tagged_cov"] / nH, 3))
    return out, R["per_course"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "eval_cardless.json"))
    a = ap.parse_args()
    dev = load("dev")
    if a.fit:
        model = fit(dev)
        json.dump(model, open(CL.MODEL_PATH, "w"), indent=1)
        print("wrote", CL.MODEL_PATH)
    model = CL.load_model()
    test = load("test")
    res = {}
    for name, cs in (("dev", dev), ("test", test)):
        o, pc = evaluate(cs, model)
        ot, _ = evaluate(cs, model, S_override="true")
        res[name] = dict(estimated_S=o, oracle_S=ot)
        res[name + "_per_course"] = pc
        print(name, json.dumps(o, indent=1))
        print(name, "oracle S", json.dumps({k: ot[k] for k in ("hole_yd_err", "total_yd_err", "par_hole_acc")}))
    res["version"] = CL.VERSION
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
