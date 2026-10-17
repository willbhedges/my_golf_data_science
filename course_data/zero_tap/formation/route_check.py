"""How far the pair model carries once a sequence solver uses it: the structure solver's route CRF (exact DP over
the playing order, clubhouse anchors, card position terms) with its formation scores replaced by the pair model's
logits. A stand-in for workstream C's solver, to measure formation after sequencing, with and without a card.

    python course_data/zero_tap/formation/route_check.py --split train [--limit 20]    # OOF logits (cache/_oof.pkl)
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D                                                     # noqa: E402
import formation as F                                                # noqa: E402
import solver as V                                                   # noqa: E402
import eval as E                                                     # noqa: E402  (structure/eval.py)

TOPK = 8
SCORE = os.environ.get("ROUTE_SCORE", "logp")                   # logp | logit
CAL = dict(b0=-6.0, b1=0.0, temp=1.0)


def hyps_from_logits(sc, geo, pairs, z, topk=TOPK):
    per = [[] for _ in range(len(geo.G))]
    for p, zz in zip(pairs, z):
        f = {k: 0.0 for k in V.FEATS}
        f["length"] = float(zz)
        Dm = p["D"]
        _, pp = V.length_loglik(np.array([Dm]))
        per[p["gi"]].append(dict(gi=p["gi"], k=p["k"], tee=np.asarray(p["tee"]), D=Dm, ppar=pp[:, 0], cover=p["cover"],
                                 f=f, score=float(zz)))
    for i in range(len(per)):
        per[i].sort(key=lambda h: -h["score"])
        per[i] = per[i][:topk]
    return per


def route(e, mode, card_mode, z):
    I = D.build(e, mode, card_mode)
    if I is None or len(I.pairs) != len(z):
        return None
    if SCORE == "logp":
        # calibrated pair marginals (Sinkhorn), as log-probabilities: what hole_pairs/1 hands a sequence solver
        r = dict(nG=len(I.geo.G), nC=len(I.geo.C), gi=np.array([p["gi"] for p in I.pairs]),
                 k=np.array([p["k"] for p in I.pairs]), greens=[dict(p=float(g.get("p_hole", g.get("conf", 1.0))))
                                                                for g in I.sc.greens])
        S, P, ps, _ = F.solve(r, z, CAL)
        z = np.log(np.maximum(P[r["gi"], r["k"]], 1e-4))
    hyps = hyps_from_logits(I.sc, I.geo, I.pairs, z)
    old_h, old_w = V.hypotheses, dict(V.FORM_W)
    V.hypotheses = lambda sc, geo=None, topk=None, w=None, clubs=None: (hyps, I.geo)
    V.FORM_W.clear()
    V.FORM_W.update({k: 0.0 for k in V.FEATS})
    V.FORM_W["length"] = 1.0
    card = F.card_of(dict(slug=e["slug"], card=card_mode, truth=[dict(par=t["par"], length=t["length"]) for t in I.truth]))
    try:
        res = V.solve(I.sc, card=card, n_holes=I.N)
    finally:
        V.hypotheses = old_h
        V.FORM_W.clear()
        V.FORM_W.update(old_w)
    # structure eval's matcher keys tees by scene tee ids; virtual tees have no boxes -> match by tee_xy only
    G = I.geo.G
    R = I.geo.gr_r
    gid = {g["id"]: i for i, g in enumerate(I.sc.greens)}
    tg = [E.true_green(G, R, t["green"]) for t in I.truth]
    used, formed, number = set(), 0, 0
    for h in res.get("holes", []):
        gi = gid.get(h["green"])
        for j, t in enumerate(I.truth):
            if j in used or tg[j] is None or tg[j] != gi:
                continue
            boxes = [np.asarray(b) for b in (h.get("boxes_xy") or [])] or [np.asarray(h["tee_xy"])]
            if E.tee_ok(np.asarray(h["tee_xy"]), boxes, t):
                used.add(j)
                formed += 1
                number += int(h["number"] == t["ref"])
                break
    return dict(slug=e["slug"], mode=mode, card=card_mode, N=I.N, formed=formed, number=number,
                full=int(number == I.N))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--modes", default="osm")
    ap.add_argument("--cards", default="none,web,truth")
    ap.add_argument("--oof", default=os.path.join(F.CACHE, "_oof.pkl"))
    ap.add_argument("--out")
    a = ap.parse_args()
    oof = dict(pickle.load(open(a.oof, "rb")))
    es = {e["slug"]: e for e in D.courses() if e["split"] == a.split}
    out = []
    n = 0
    for slug in sorted(es):
        if a.limit and n >= a.limit:
            break
        n += 1
        for mode in a.modes.split(","):
            for cm in a.cards.split(","):
                z = oof.get((slug, mode, cm))
                if z is None:
                    continue
                t = time.time()
                try:
                    r = route(es[slug], mode, cm, z)
                except Exception as ex:                              # noqa: BLE001
                    print(slug, mode, cm, "error", repr(ex)[:200], flush=True)
                    continue
                if r:
                    r["sec"] = round(time.time() - t, 1)
                    out.append(r)
                    print(json.dumps(r), flush=True)
    agg = {}
    for r in out:
        k = f"{r['mode']}/{r['card']}"
        a_ = agg.setdefault(k, dict(courses=0, holes=0, formed=0, number=0, full=0))
        a_["courses"] += 1
        a_["holes"] += r["N"]
        a_["formed"] += r["formed"]
        a_["number"] += r["number"]
        a_["full"] += r["full"]
    for k, v in agg.items():
        v["formed_pct"] = round(100 * v["formed"] / v["holes"], 1)
        v["number_pct"] = round(100 * v["number"] / v["holes"], 1)
        v["full_pct"] = round(100 * v["full"] / v["courses"], 1)
    print(json.dumps(agg, indent=1))
    if a.out:
        json.dump(dict(rows=out, agg=agg), open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
