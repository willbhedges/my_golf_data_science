"""Fit cardgeo.py's parameters on DEV courses only (zero-tap sequence v3).

    python course_data/zero_tap/sequence/fit_cardgeo.py extract --tiers osm_card,unmapped_card --procs 4 --out cases.pkl.gz
    python course_data/zero_tap/sequence/fit_cardgeo.py fit cases.pkl.gz --out course_data/zero_tap/sequence/cardgeo_params.json

extract: for every dev course with a card and every true hole (truth: D's truth files, scored with D's matcher), the
         candidate tees of its green as the v2 solver sees them (workstream A's hole_pairs/1 joined to the structure
         hypotheses, top PAIR_K by A's p), each with its back length, box distances, A's log p, the structure score and
         whether D's matcher accepts it as the hole's tee. Card position k = true ref - 1 (oracle numbering: this
         measures how well the card tells the tees of one green apart, the route solver adds the order).
fit:     coordinate search over the card parameters maximising the dev log-likelihood of the true tee among each
         green's candidates under  W_A * log p_A + card_ll(h, k), and reports top-1 accuracy for: A alone, A + the
         v2 card term (longest set only), A + the joint card term. Test courses are never read.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import pickle
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import run_bench as RB                                                # noqa: E402  (loads D's bench as RB.DB)
import solve as SV                                                    # noqa: E402
import cardgeo as CG                                                  # noqa: E402

DB = RB.DB
V = SV.V
S = SV.S


def _course_cases(args):
    slug, tier, pairs_root = args
    row = next(r for r in DB.courses("dev") if r["slug"] == slug)
    assert row["split"] == "dev"
    try:
        x = DB.inputs(row, tier)
        hp, _ = RB._pairs_for(slug, tier, "test", pairs_root, None)      # A's committed file (dev: in-sample p)
        if hp is None or not x["card"]:
            return []
        scene = None
        if tier.startswith("unmapped"):
            scene = x.get("scene") or SV._formation_data().perception_scene_obj(slug)
            if scene is None:
                return []
        sc = S.scene_from_perception(scene) if scene else S.scene_from_osm(x["fc"], x["course"].get("boundary"))
        hyps, geo, _, _ = SV.pair_hypotheses(sc, hp)
        t = DB.truth(slug)
        if t["kind"] not in (9, 18):
            return []
        M = DB.Matcher(t)
        N = len(t["holes"])
        rows = CG.card_holes(x["card"], N)
        _, yards = V.card_info(x["card"])
        pj = sc.proj
        out = []
        for j, th in enumerate(M.holes):
            k = th["ref"] - 1
            gis = [gi for gi in range(len(sc.greens)) if M.green_ok(j, M.pj.fwd(*pj.ll(geo.G[gi])))]
            if not gis:
                continue
            gi = gis[0]
            hs = hyps[gi]
            if len(hs) < 2:
                continue
            cand = []
            for h in hs:
                pts = [M.pj.fwd(*pj.ll(h["tee"]))] + [M.pj.fwd(*pj.ll(q)) for q in np.asarray(geo.cx[h["k"]]["xy"]).reshape(-1, 2)]
                cand.append(dict(D=float(h["D"]), d=CG.box_dists(geo, gi, h).tolist(), lp=math.log(h["p_pair"]),
                                 s=float(h["score_struct"]), ok=bool(M.tee_ok(j, pts)), cover=len(h.get("cover") or [])))
            if not any(c["ok"] for c in cand):
                continue
            out.append(dict(slug=slug, tier=tier, k=k, hk=rows[k], rows=rows, Y_old=(yards[k] if yards and k < len(yards) else None),
                            cand=cand))
        return out
    except Exception as e:                                            # noqa: BLE001
        print("ERR", slug, tier, repr(e)[:200], flush=True)
        return []


def extract(tiers, procs, out, pairs_root):
    jobs = []
    for tier in tiers:
        slugs = {c["slug"] for c in DB.courses("dev", tier)}
        for r in DB.courses("dev"):
            if r["slug"] in slugs and os.path.exists(os.path.join(pairs_root, tier, r["slug"] + ".json")):
                jobs.append((r["slug"], tier, pairs_root))
    print(len(jobs), "dev course x tier jobs", flush=True)
    cases = []
    with Pool(procs) as pool:
        for i, cs in enumerate(pool.imap_unordered(_course_cases, jobs)):
            cases.extend(cs)
            if i % 20 == 0:
                print(i, len(cases), flush=True)
    with gzip.open(out, "wb") as fh:
        pickle.dump(cases, fh)
    print(len(cases), "cases ->", out)


def _old_ll(c, Y):
    """v2's card term for one hypothesis (structure/solver._card_pos without the marginalisation)."""
    if not Y:
        return 0.0
    D = c["D"]
    base = float(V.length_loglik(np.array([D]))[0][0])
    sd = 0.05 * Y + 12
    z = (D - Y) / sd if D > Y else (D - Y) / (2.0 * sd)
    return math.log(0.9 * math.exp(-0.5 * z * z) / (sd * 2.5) + 0.1 / 600) + math.log(600) - base


def _new(c, cs, P):
    v = CG.hole_ll(c["D"], np.array(c["d"]), cs["hk"], P, ppar=V.length_loglik(np.array([c["D"]]))[1][:, 0])
    return v + CG.hcp_node(c["D"], cs["hk"], P, cs.get("rows") or [])


def evaluate(cases, P, wa=3.0, mode="new", tiers=None):
    ll, top, n = 0.0, 0, 0
    for cs in cases:
        if tiers and cs["tier"] not in tiers:
            continue
        sc = []
        for c in cs["cand"]:
            v = wa * c["lp"]
            if mode == "new":
                v += _new(c, cs, P)
            elif mode == "old":
                v += _old_ll(c, cs["Y_old"])
            elif mode == "card_only":
                v = _new(c, cs, P)
            elif mode == "card_only_nonest":
                v = CG.hole_ll(c["D"], np.array(c["d"]), cs["hk"], P, nest=False,
                               ppar=V.length_loglik(np.array([c["D"]]))[1][:, 0])
            elif mode == "old_only":
                v = _old_ll(c, cs["Y_old"])
            elif mode == "struct":
                v = c["s"]
            elif mode == "struct_old":
                v = c["s"] + _old_ll(c, cs["Y_old"])
            elif mode == "struct_new":
                v = c["s"] + _new(c, cs, P)
            sc.append(v)
        sc = np.array(sc)
        okm = np.array([c["ok"] for c in cs["cand"]])
        lz = V._lse(sc)
        ll += float(V._lse(sc[okm]) - lz)
        top += int(okm[int(np.argmax(sc))])
        n += 1
    return ll, top, n


GRID = dict(sd_a=[0.015, 0.02, 0.03, 0.05, 0.07], sd_b=[4, 6, 9, 12, 16], dogleg=[1.5, 2.0, 3.0, 4.0, 6.0],
            back_out=[0.01, 0.03, 0.06, 0.1, 0.2], anchor_p0=[0.6, 0.75, 0.85, 0.95, 0.98],
            nest_sd=[2.5, 3, 4, 6, 8, 11], nest_pi=[0.1, 0.15, 0.2, 0.3, 0.45, 0.6], nest_R=[40, 80, 150, 300],
            par_w=[0.0, 0.25, 0.5, 1.0], hcp_w=[0.0, 0.1, 0.25, 0.5])


FIT_MODE = os.environ.get("CARDGEO_FIT_MODE", "card_only")
MODES = ("a_only", "old", "new", "old_only", "card_only", "card_only_nonest", "struct", "struct_old", "struct_new")


def fit(paths, out, wa=3.0):
    cases = []
    for p in paths:
        with gzip.open(p, "rb") as fh:
            cases.extend(pickle.load(fh))
    assert all(DB.courses_split(cs["slug"]) == "dev" for cs in cases) if hasattr(DB, "courses_split") else True
    dev_slugs = {r["slug"] for r in DB.courses("dev")}
    cases = [c for c in cases if c["slug"] in dev_slugs]
    # only greens where A's candidates disagree with the truth sometimes matter, but fit on all
    P = dict(CG.DEFAULT)
    rep = {}
    for mode in MODES:
        rep[mode + "_default"] = evaluate(cases, P, wa, mode)
    best = evaluate(cases, P, wa, FIT_MODE)[0]
    for sweep in range(3):
        changed = False
        for k, vals in GRID.items():
            for v in vals:
                Q = dict(P, **{k: v})
                s = evaluate(cases, Q, wa, FIT_MODE)[0]
                if s > best + 1e-6:
                    best, P, changed = s, Q, True
        print("sweep", sweep, round(best, 2), {k: P[k] for k in GRID}, flush=True)
        if not changed:
            break
    for mode in MODES:
        rep[mode] = evaluate(cases, P, wa, mode)
    for t in sorted({c["tier"] for c in cases}):
        for mode in ("old_only", "card_only", "struct_old", "struct_new"):
            rep[f"{t}/{mode}"] = evaluate(cases, P, wa, mode, tiers={t})
    for k_, v_ in rep.items():
        if v_:
            print(f"{k_:28s} ll {v_[0]:9.1f}  top-1 {v_[1]}/{v_[2]} = {v_[1] / max(v_[2], 1):.3f}")
    json.dump(dict(schema="cardgeo_params/1", fitted_on="dev only, oracle numbering, objective: " + FIT_MODE,
                   n_cases=len(cases), params={k: P[k] for k in CG.DEFAULT},
                   report={k: (None if v is None else dict(ll=v[0], top1=v[1], n=v[2])) for k, v in rep.items()}),
              open(out, "w"), indent=1)
    print("->", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["extract", "fit"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--tiers", default="osm_card,unmapped_card")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--pairs-root", default=os.path.join(ZT, "formation", "hole_pairs"))
    ap.add_argument("--wa", type=float, default=3.0)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.what == "extract":
        extract(a.tiers.split(","), a.procs, a.out, a.pairs_root)
    else:
        fit(a.paths, a.out or CG.PARAMS_PATH, a.wa)


if __name__ == "__main__":
    main()
