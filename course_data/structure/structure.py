"""Course structure CLI and the JSON contract (`course_structure/1`) for course_data/platform/package.py and the app.

    python course_data/structure/structure.py --osm osm.geojson[.gz] [--course course.json] [--card scorecard.json]
                                              [--hide-holes] [--out structure.json]
    python course_data/structure/structure.py --scene course_data/perception/scenes/<slug>/scene.json --out ...

`course_structure/1` (WGS84 [lon, lat]; yards):

    {"schema": "course_structure/1", "method": "structure/1 (scene -> CRF route, exact posterior)",
     "n_holes": 18, "status": "ok", "card_used": false, "input": "osm" | "perception" | ...,
     "clubhouse": {"ll": [lon, lat], "how": "named|building|parking|perception|hub", "p": 0.8},
     "total_par": 72, "p_route": 0.31,                 # posterior probability of the whole MAP route
     "practice_greens": [{"id": "g19", "ll": [lon, lat]}],
     "holes": {"1": {"ref": "1", "par": 4, "p_par": [0.02, 0.9, 0.08],
                     "tee_ll": [lon, lat],             # back tee of the hole's complex (start of play)
                     "green_ll": [lon, lat], "tee_boxes_ll": [[lon, lat], ...],
                     "length_yd": 402.5, "bearing_deg": 81.2,       # straight tee -> green; direction of play
                     "p_number": 0.93,                 # P(this green is hole 1) (exact marginal)
                     "p_tee": 0.97,                    # P(this complex is its tee | route)
                     "confidence": 0.90,               # p_number * p_tee (calibrated on dev, see REPORT.md)
                     "p_green": 0.90,                  # = confidence (routing.py field name)
                     "walk_in_yd": 55.0, "status": "ok" | "check", "flags": [...],
                     "green_id": "g3", "tee_id": "t12", "tee_complex": "c4"}}}

`to_hole_features(res, fc)` adds golf=hole LineStrings (ref, par, `structure_conf`) to a FeatureCollection the
way routing.to_hole_features does, so the package builder can use either. `for_package(fc, course, card)` is the
drop-in for package.route_missing_holes (holes OSM already maps are kept; only missing refs are filled).
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
import scene as S                                                    # noqa: E402
import solver as V                                                   # noqa: E402

CHECK_BELOW = 0.8


def bearing(p, q):
    return (math.degrees(math.atan2(q[0] - p[0], q[1] - p[1])) + 360) % 360


def contract(res, sc, source="osm"):
    """Solver result (local yards) -> course_structure/1 (WGS84)."""
    pj = sc.proj
    tid = {t["id"]: t for t in sc.tees}
    gid = {g["id"]: g for g in sc.greens}
    holes = {}
    for h in res.get("holes", []):
        flags = []
        if h["confidence"] < CHECK_BELOW:
            flags.append(f"uncertain ({h['confidence']:.0%}): P(number) {h['p_number']:.0%}, P(tee) {h['p_tee']:.0%}")
        if h.get("walk_in_yd") and h["walk_in_yd"] > 250:
            flags.append(f"long walk from the previous green ({h['walk_in_yd']:.0f} yds)")
        holes[str(h["number"])] = dict(
            ref=str(h["number"]), par=h.get("par"), p_par=h.get("p_par"),
            tee_ll=pj.ll(h["tee_xy"]), green_ll=pj.ll(h["green_xy"]),
            tee_boxes_ll=[pj.ll(tid[b]["c"]) for b in h.get("boxes", []) if b in tid],
            length_yd=h["length_yd"], bearing_deg=round(bearing(h["tee_xy"], h["green_xy"]), 1),
            p_number=h["p_number"], p_tee=h["p_tee"], confidence=h["confidence"], p_green=h["confidence"],
            walk_in_yd=h.get("walk_in_yd"), status="ok" if not flags else "check", flags=flags,
            green_id=h["green"], tee_id=h.get("tee"), tee_complex=h.get("tee_complex"))
    ch = res.get("clubhouse") or {}
    return dict(schema="course_structure/1", method="structure/1 (scene -> CRF route, exact posterior)",
                status=res.get("status"), n_holes=res.get("n_holes"), card_used=res.get("card_used", False),
                input=source, total_par=res.get("total_par"), p_route=res.get("p_route"),
                clubhouse=dict(ll=pj.ll(ch["xy"]), how=ch.get("how"), p=ch.get("p")) if ch.get("xy") is not None else None,
                practice_greens=[dict(id=g, ll=pj.ll(gid[g]["c"])) for g in res.get("practice_greens", []) if g in gid],
                holes=holes)


def to_hole_features(res, fc, only=None):
    """fc + golf=hole LineStrings tee -> green for the holes of a course_structure/1 result (refs in `only`)."""
    feats = list(fc.get("features", []))
    for ref, h in res["holes"].items():
        if only is not None and ref not in only:
            continue
        feats.append(dict(type="Feature", geometry=dict(type="LineString", coordinates=[h["tee_ll"], h["green_ll"]]),
                          properties=dict(golf="hole", ref=ref, par=str(h["par"]) if h.get("par") else None,
                                          source="structure", structure_conf=h["confidence"],
                                          structure_status=h["status"])))
    return dict(fc, features=feats)


def run(fc=None, course=None, card=None, scene_obj=None, hide_holes=True, **kw):
    if scene_obj is not None:
        sc = S.scene_from_perception(scene_obj)
        src = "perception"
    else:
        sc = S.scene_from_osm(fc, (course or {}).get("boundary"))
        src = "osm"
    res = V.solve(sc, card=card, **kw)
    return contract(res, sc, src), sc


def for_package(fc, course, card=None):
    """Drop-in for package.route_missing_holes: -> (fc with golf=hole lines for the refs OSM lacks, {ref: info})."""
    have = {str(f["properties"].get("ref")) for f in fc.get("features", []) if f["properties"].get("golf") == "hole"}
    res, _ = run(fc, course, card)
    missing = [r for r in res["holes"] if r not in have]
    fc2 = to_hole_features(res, fc, only=set(missing))
    info = {r: {k: res["holes"][r].get(k) for k in ("status", "flags", "p_green", "confidence", "par")} for r in missing}
    return fc2, info, res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--osm")
    ap.add_argument("--scene")
    ap.add_argument("--course")
    ap.add_argument("--card")
    ap.add_argument("--n-holes", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    card = json.load(open(a.card)) if a.card else None
    if card and "cards" in card:                                 # generalize scorecard.json wrapper
        card = card["cards"][0]["card"] if card["cards"] else None
    if a.scene:
        res, _ = run(scene_obj=json.load(open(a.scene)), card=card, n_holes=a.n_holes)
    else:
        fc = S.load_fc(a.osm)
        course = json.load(open(a.course)) if a.course else None
        res, _ = run(fc, course, card, n_holes=a.n_holes)
    txt = json.dumps(res, indent=1, default=float)
    if a.out:
        open(a.out, "w").write(txt)
    for r, h in res["holes"].items():
        print(f"{r:>2} par {h['par']} {h['length_yd']:5.0f} yds  conf {h['confidence']:.2f}  {h['status']}")


if __name__ == "__main__":
    main()
