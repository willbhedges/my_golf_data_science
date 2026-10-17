"""Zero-tap order of play for one course -> zero_tap_result/1 (workstream C's output).

    python course_data/zero_tap/sequence/solve.py --osm osm.geojson.gz [--course course.json] [--card scorecard.json]
        [--hole-pairs hole_pairs.json] [--hole-evidence hole_evidence.json] --out result.json

Every golf=hole way, pin and ref / name of golf features in the OSM file is ignored (hidden), so the result is the
zero-tap inference. Formation: the structure solver's hypotheses, re-scored by workstream A's hole_pairs/1 when
given; number evidence: workstream B's hole_evidence/1 as a position term; anchors: anchors.py; gate: gate.py.

zero_tap_result/1 (provisional until workstream D's course_data/zero_tap/BENCH.md fixes the contract):
{"schema": "zero_tap_result/1", "method": "sequence/1", "course": {...from course.json},
 "certain": false, "confidence": 0.42, "gate": {"score": -1.3, "threshold": 0.8, "version": "zero_tap_gate/1"},
 "n_holes": 18, "inputs": {"formation": "structure" | "hole_pairs/1", "evidence": false, "card": true},
 "clubhouse": {"ll": [lon, lat], "how": "named", "p": 0.9}, "p_front_nine": 0.8, "p_route": 0.3,
 "holes": [{"number": 1, "par": 4, "tee_ll": [lon, lat], "tee_boxes_ll": [[lon, lat]], "green_ll": [lon, lat],
            "length_yd": 402.5, "p_number": 0.9, "p_tee": 0.97, "confidence": 0.87}],
 "practice_greens_ll": [[lon, lat]]}
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anchors as A                                                  # noqa: E402
import gate as GT                                                    # noqa: E402
import joint as J                                                    # noqa: E402

V = A.V
import scene as S                                                    # noqa: E402

PAIR_W = 1.0          # weight of log P(pair) from hole_pairs/1 against the structure formation score (v1 offsets)
PAIR_MIN = 0.005      # hole_pairs/1 lists pairs with p >= 0.005
PAIR_K = 6            # hypotheses per green kept from hole_pairs/1 (by p)
STRUCT_W = 0.0        # weight of the structure formation score added to log P(pair) in pairs mode (A's model has it)
PAIRS_FORM_W = float(os.environ.get("ZT_PAIRS_FORM_W", "1.0"))   # weight of log P(pair) in pairs mode
PAIR_FLOOR = 1e-3
EV_W = 1.0


def _ll(obj, *keys):
    for k in keys:
        v = obj.get(k)
        if v is not None and len(v) >= 2:
            return [float(v[0]), float(v[1])]
    return None


def pair_offsets(sc, geo, hyps, keep, pairs_obj):
    """hole_pairs/1 -> pad_extra (len(keep), K): PAIR_W * log P(tee complex -> green) for the hypotheses matched by
    location (green within 25 yds, a box of the complex within 30 yds of the pair's tee); unmatched hypotheses get
    the floor when the green has any pair listed (A's model says it is not this tee), else 0."""
    pairs = pairs_obj.get("pairs") or []
    pj = sc.proj
    per = {}
    for p in pairs:
        g, t = _ll(p, "green_ll", "green"), _ll(p, "tee_ll", "tee")
        pr = p.get("p", p.get("prob"))
        if g is None or t is None or pr is None:
            continue
        gx, tx = np.array(pj.fwd(*g)), np.array(pj.fwd(*t))
        d = np.hypot(*(geo.G - gx).T) - geo.gr_r
        gi = int(np.argmin(d))
        if d[gi] > 25:
            continue
        per.setdefault(gi, []).append((tx, float(pr)))
    K = max(1, max(len(hyps[g]) for g in keep))
    off = np.zeros((len(keep), K))
    for b, g in enumerate(keep):
        if g not in per:
            continue
        for h, x in enumerate(hyps[g][:K]):
            xy = geo.cx[x["k"]]["xy"]
            best = PAIR_FLOOR
            for tx, pr in per[g]:
                if np.hypot(*(xy - tx).T).min() <= 30:
                    best = max(best, pr)
            off[b, h] = PAIR_W * math.log(best)
    return off


# ----------------------------------------------------------------------------- hole_pairs/1 as the formation (v2)
def _formation_data():
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "formation"))
    import data as FD                                                # noqa: E402  (workstream A)
    return FD


def pair_hypotheses(sc, pairs_obj, clubs=None):
    """hole_pairs/1 -> (hyps, geo, stats, p_paired): the structure solver's hypotheses over the candidates workstream
    A scored (its complexes + fairway-end virtual tees, formation/data.add_virtual_tees), restricted per green to A's
    listed pairs and sorted by A's marginal p; each carries p_pair, p_corridor, a_map (it is A's MAP tee for that
    green) and form_lp = log p (+ STRUCT_W x structure score). Pairs are joined by (green id, tee id) and checked by
    location (green <= 5 yds, tee point within 5 yds of the complex); a pair failing that is matched by location
    (green <= 25 yds, a box within 30 yds)."""
    FD = _formation_data()
    geo = V.Geo(sc)
    FD.add_virtual_tees(sc, geo)
    hyps, geo = V.hypotheses(sc, geo, topk=10 ** 6, clubs=list(sc.clubhouse) if clubs is None else clubs)
    pj = sc.proj
    gid = {g["id"]: i for i, g in enumerate(sc.greens)}
    cid = {c["id"]: k for k, c in enumerate(geo.cx)}
    amap = {g["id"]: g.get("map_tee") for g in pairs_obj.get("greens") or []}
    st = dict(n_pairs=0, id_join=0, loc_join=0, unmatched=0, no_hyp=0)
    P = {}
    for p in pairs_obj.get("pairs") or []:
        st["n_pairs"] += 1
        g, t = _ll(p, "green_ll"), _ll(p, "tee_ll")
        gx = np.array(pj.fwd(*g)) if g else None
        tx = np.array(pj.fwd(*t)) if t else None
        gi, k = gid.get(p.get("green")), cid.get(p.get("tee"))
        ok = gi is not None and k is not None
        if ok and gx is not None and tx is not None:
            ok = bool(np.hypot(*(geo.G[gi] - gx)) <= 5 and
                      np.hypot(*(np.asarray(geo.cx[k]["xy"]) - tx).T).min() <= 5)
        if ok:
            st["id_join"] += 1
        elif gx is not None and tx is not None and len(geo.cx):
            d = np.hypot(*(geo.G - gx).T) - geo.gr_r
            gi = int(np.argmin(d))
            dk = np.array([np.hypot(*(np.asarray(c["xy"]) - tx).T).min() for c in geo.cx])
            k = int(np.argmin(dk))
            if d[gi] > 25 or dk[k] > 30:
                st["unmatched"] += 1
                continue
            st["loc_join"] += 1
        else:
            st["unmatched"] += 1
            continue
        key = (gi, k)
        if key not in P or P[key]["p"] < p["p"]:
            P[key] = dict(p=float(p["p"]), pc=float(p.get("p_corridor", p["p"])),
                          a_map=amap.get(sc.greens[gi]["id"]) == geo.cx[k]["id"])
    out = [[] for _ in hyps]
    seen = set()
    for gi, hs in enumerate(hyps):
        for h in hs:
            q = P.get((gi, h["k"]))
            if q is None or q["p"] < PAIR_MIN:
                continue
            seen.add((gi, h["k"]))
            h = dict(h, p_pair=q["p"], p_corridor=q["pc"], a_map=q["a_map"], score_struct=h["score"])
            h["form_lp"] = PAIRS_FORM_W * math.log(q["p"]) + STRUCT_W * h["score_struct"]
            h["score"] = h["form_lp"]
            out[gi].append(h)
        out[gi].sort(key=lambda r: -r["p_pair"])
        out[gi] = out[gi][:PAIR_K]
    st["no_hyp"] = len([k for k in P if k not in seen and P[k]["p"] >= PAIR_MIN])
    p_paired = np.zeros(len(sc.greens))
    for (gi, k), q in P.items():
        p_paired[gi] += q["p"]
    return out, geo, st, np.clip(p_paired, 0, 1)


def n_from_pairs(pairs_obj, p_paired):
    """9 / 18 / 27 / 36 from A's expected number of holes (sum of the pair marginals)."""
    e = (pairs_obj.get("summary") or {}).get("expected_holes")
    n = int(round(float(e) if e is not None else float(p_paired.sum())))
    return 36 if n >= 34 else 27 if n >= 26 else 18 if n >= 14 else (9 if n >= 5 else max(1, n))


def run_pairs(sc, fc, course, card, pairs, evidence, n_holes):
    """v2: A's pairs are the formation. -> (structure-style result, inputs, diag)."""
    hyps, geo, st, p_paired = pair_hypotheses(sc, pairs)
    pars, yards = V.card_info(card)
    N = n_holes or (len(pars) if pars else (len(yards) if yards else n_from_pairs(pairs, p_paired)))
    inputs = dict(formation="hole_pairs/1", evidence=bool(evidence), card=bool(card), join=st)
    if N > 18:
        res = V.solve(sc, card=card, n_holes=N)                     # 27 / 36: greedy, never certain
        return res, inputs, {}
    usable = [gi for gi, hs in enumerate(hyps) if hs]
    order = sorted(usable, key=lambda gi: -p_paired[gi])
    M = max(min(len(usable), 19, N + 3), min(len(usable), N))
    keep = sorted(order[:M])
    if len(keep) < 2:
        return dict(status="no_greens_or_tees", holes=[], n_holes=N, diag={}), inputs, {}
    K = max(len(hyps[g]) for g in keep)
    form_lp = np.full((len(keep), K), -1e4)
    for b, g in enumerate(keep):
        for h, x in enumerate(hyps[g]):
            form_lp[b, h] = x["form_lp"]
    roads, street = A.roads_from_fc(fc, sc.proj), A.addr_street(course)
    models = A.load_models()
    cands = A.clubhouse_candidates(sc, geo, hyps, roads=roads, street=street, model=models.get("club"))
    nine = models.get("nine")
    nine = nine.with_context(roads, street) if nine is not None else None
    Nk = min(N, len(keep))
    pos = evidence_pos(sc, geo, keep, Nk, evidence) if evidence else None
    res = J.solve(sc, card=card, n_holes=Nk, hyps=hyps, geo=geo, keep=keep, cands=cands, nine=nine,
                  pos_extra=pos, form_lp=form_lp, nothole_override=np.zeros(len(sc.greens)))
    dg = res.get("diag") or {}
    if dg:
        hs = res["holes"]
        used = set(dg["seq"])
        dg.update(pairs_mode=True, join=st, N_pairs=N,
                  p_pair=[h.get("p_pair") or 0.0 for h in hs], p_corridor=[h.get("p_corridor") or 0.0 for h in hs],
                  a_map=[bool(h.get("a_map")) for h in hs], p_tee_corr=[h.get("p_tee_corr") or 0.0 for h in hs],
                  p_paired_used=[float(p_paired[i]) for i in dg["seq"]],
                  p_paired_unused_max=float(max([p_paired[i] for i in range(len(sc.greens)) if i not in used],
                                                default=0.0)),
                  expected_holes=(pairs.get("summary") or {}).get("expected_holes"))
    return res, inputs, dg


def evidence_pos(sc, geo, keep, N, ev_obj):
    """hole_evidence/1 -> pos_extra (len(keep), N): EV_W * logit(confidence) at (green, number) for each piece of
    evidence located on a kept green (green within 30 yds), spread as -log(N-1) over the other numbers."""
    pos = np.zeros((len(keep), N))
    pj = sc.proj
    for e in ev_obj.get("holes") or ev_obj.get("evidence") or []:
        try:
            k = int(e.get("number", e.get("ref"))) - 1
        except (TypeError, ValueError):
            continue
        g = _ll(e, "green_ll", "green")
        c = float(e.get("confidence", e.get("p", 0.0)))
        if g is None or not (0 <= k < N) or c <= 0:
            continue
        gx = np.array(pj.fwd(*g))
        d = np.hypot(*(geo.G[keep] - gx).T) - geo.gr_r[keep]
        b = int(np.argmin(d))
        if d[b] > 30:
            continue
        c = min(max(c, 0.01), 0.99)
        lo = EV_W * math.log(c / (1 - c) * (N - 1))
        pos[b, k] += lo
    return np.clip(pos, -10, 10)


def run(fc, course=None, card=None, pairs=None, evidence=None, gate_params=None, n_holes=None, return_raw=False,
        scene=None, legacy_pairs=False):
    """scene: a perception course_scene/1 object (unmapped tiers: the scene hole_pairs/1 was built on), else the
    scene comes from the OSM file. pairs: hole_pairs/1 -> v2 pairs mode (A's pairs ARE the formation); with
    legacy_pairs=True, v1's re-scoring of the structure hypotheses instead."""
    course = course or {}
    sc = S.scene_from_perception(scene) if scene else S.scene_from_osm(fc, course.get("boundary"))
    if pairs and not legacy_pairs:
        res, inputs, dg = run_pairs(sc, fc, course, card, pairs, evidence, n_holes)
        gp = gate_params if gate_params is not None else GT.load()
        certain, conf, s = GT.apply(gp, dg) if dg else (False, 0.0, None)
        out = contract(res, sc, course, certain, conf, s, gp, inputs)
        return (out, res) if return_raw else out
    allh, geo = V.hypotheses(sc, topk=V.TOPK, clubs=list(sc.clubhouse))
    hyps = allh
    pars, yards = V.card_info(card)
    N = n_holes or (len(pars) if pars else (len(yards) if yards else V.n_holes_guess(hyps, len(geo.C))))
    if N > 18:
        # 27 / 36 holes: the structure solver's greedy loop builder; never 'certain'
        res = V.solve(sc, card=card, n_holes=N)
        res["diag"] = {}
        out = contract(res, sc, course, False, 0.0, None, None, dict(formation="structure (greedy, 27/36)",
                                                                     evidence=False, card=bool(card)))
        return (out, res) if return_raw else out
    keep, _, _ = J.choose_keep(sc, hyps, geo, N)
    roads, street = A.roads_from_fc(fc, sc.proj), A.addr_street(course)
    models = A.load_models()
    cands = A.clubhouse_candidates(sc, geo, hyps, roads=roads, street=street, model=models.get("club"))
    nine = models.get("nine")
    nine = nine.with_context(roads, street) if nine is not None else None
    pad = pair_offsets(sc, geo, hyps, keep, pairs) if pairs else None
    pos = evidence_pos(sc, geo, keep, N, evidence) if evidence else None
    res = J.solve(sc, card=card, n_holes=N, hyps=hyps, geo=geo, keep=keep, cands=cands, nine=nine,
                  pad_extra=pad, pos_extra=pos)
    gp = gate_params if gate_params is not None else GT.load()
    certain, conf, s = GT.apply(gp, res.get("diag", {}))
    out = contract(res, sc, course, certain, conf, s, gp, dict(formation="hole_pairs/1" if pairs else "structure",
                                                               evidence=bool(evidence), card=bool(card)))
    return (out, res) if return_raw else out


def contract(res, sc, course, certain, conf, s, gp, inputs):
    pj = sc.proj
    tid = {t["id"]: t for t in sc.tees}
    gid = {g["id"]: g for g in sc.greens}
    holes = []
    for h in res.get("holes", []):
        holes.append(dict(number=h["number"], par=h.get("par"), tee_ll=pj.ll(h["tee_xy"]),
                          tee_boxes_ll=[pj.ll(tid[b]["c"]) for b in h.get("boxes", []) if b in tid],
                          green_ll=pj.ll(h["green_xy"]), length_yd=h["length_yd"], p_number=h["p_number"],
                          p_tee=h["p_tee"], confidence=h["confidence"],
                          **({"p_corridor": h["p_corridor"]} if h.get("p_corridor") is not None else {})))
    ch = res.get("clubhouse") or {}
    dg = res.get("diag", {})
    meth = ("sequence/2 (hole_pairs/1 formation + route CRF + anchors v2 + gate v2)"
            if inputs.get("formation") == "hole_pairs/1" else "sequence/1 (structure CRF + anchors v2 + gate)")
    return {"schema": "zero_tap_result/1", "method": meth,
            "course": {k: course.get(k) for k in ("name", "slug", "state", "osm") if course.get(k) is not None},
            "status": res.get("status"), "certain": bool(certain),
            "confidence": None if conf is None else round(float(conf), 4),
            "gate": None if not gp else dict(score=None if s is None else round(s, 4),
                                                 threshold=gp["threshold_score"], version=gp["schema"]),
            "n_holes": res.get("n_holes"), "inputs": inputs,
            "clubhouse": dict(ll=pj.ll(ch["xy"]), how=ch.get("how"), p=ch.get("p")) if ch.get("xy") is not None else None,
            "p_front_nine": res.get("p_front_nine"), "p_route": dg.get("p_route"),
            "holes": holes,
            "practice_greens_ll": [pj.ll(gid[g]["c"]) for g in res.get("practice_greens", []) if g in gid]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--osm", required=True)
    ap.add_argument("--course")
    ap.add_argument("--card")
    ap.add_argument("--hole-pairs")
    ap.add_argument("--hole-evidence")
    ap.add_argument("--scene", help="perception course_scene/1 (unmapped tiers: the scene hole_pairs/1 was built on)")
    ap.add_argument("--n-holes", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    fc = S.load_fc(a.osm)
    rd = (lambda p: json.load(open(p)) if p else None)
    card = rd(a.card)
    if card and "cards" in card:
        card = next((c.get("card", c) for c in card["cards"]), None)
    scene = None
    if a.scene:
        import gzip
        with (gzip.open if a.scene.endswith(".gz") else open)(a.scene, "rt") as fh:
            scene = json.load(fh)
    out = run(fc, rd(a.course), card, rd(a.hole_pairs), rd(a.hole_evidence), n_holes=a.n_holes, scene=scene)
    s = json.dumps(out, indent=1)
    if a.out:
        open(a.out, "w").write(s)
    else:
        print(s)


if __name__ == "__main__":
    main()
