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

PAIR_W = 1.0          # weight of log P(pair) from hole_pairs/1 against the structure formation score
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


def run(fc, course=None, card=None, pairs=None, evidence=None, gate_params=None, n_holes=None):
    course = course or {}
    sc = S.scene_from_osm(fc, course.get("boundary"))
    allh, geo = V.hypotheses(sc, topk=V.TOPK, clubs=list(sc.clubhouse))
    hyps = allh
    pars, yards = V.card_info(card)
    N = n_holes or (len(pars) if pars else (len(yards) if yards else V.n_holes_guess(hyps, len(geo.C))))
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
    return contract(res, sc, course, certain, conf, s, gp, dict(formation="hole_pairs/1" if pairs else "structure",
                                                                evidence=bool(evidence), card=bool(card)))


def contract(res, sc, course, certain, conf, s, gp, inputs):
    pj = sc.proj
    tid = {t["id"]: t for t in sc.tees}
    gid = {g["id"]: g for g in sc.greens}
    holes = []
    for h in res.get("holes", []):
        holes.append(dict(number=h["number"], par=h.get("par"), tee_ll=pj.ll(h["tee_xy"]),
                          tee_boxes_ll=[pj.ll(tid[b]["c"]) for b in h.get("boxes", []) if b in tid],
                          green_ll=pj.ll(h["green_xy"]), length_yd=h["length_yd"], p_number=h["p_number"],
                          p_tee=h["p_tee"], confidence=h["confidence"]))
    ch = res.get("clubhouse") or {}
    dg = res.get("diag", {})
    return {"schema": "zero_tap_result/1", "method": "sequence/1 (structure CRF + anchors v2 + gate)",
            "course": {k: course.get(k) for k in ("name", "slug", "state", "osm") if course.get(k) is not None},
            "status": res.get("status"), "certain": bool(certain),
            "confidence": None if conf is None else round(float(conf), 4),
            "gate": None if gp is None else dict(score=None if s is None else round(s, 4),
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
    ap.add_argument("--n-holes", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    fc = S.load_fc(a.osm)
    rd = (lambda p: json.load(open(p)) if p else None)
    card = rd(a.card)
    if card and "cards" in card:
        card = next((c.get("card", c) for c in card["cards"]), None)
    out = run(fc, rd(a.course), card, rd(a.hole_pairs), rd(a.hole_evidence), n_holes=a.n_holes)
    s = json.dumps(out, indent=1)
    if a.out:
        open(a.out, "w").write(s)
    else:
        print(s)


if __name__ == "__main__":
    main()
