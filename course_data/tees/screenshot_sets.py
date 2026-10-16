"""Q1: which card tee set each hand-traced Spirit Hollow screenshot actually shows.

    python3 course_data/tees/screenshot_sets.py          # rewrite course_data/spirit_hollow/screenshot_tee_sets.json

The hand map (spirit_hollow/course.py) was traced from 18Birdies screenshots. 18Birdies places its tee
icon by hand, by default at the farthest-back set (auto_course_lookup.md, finding 2), so a traced hole
is NOT automatically the golfer's Black tee. Scoring our Black placement against a Gold screenshot
counts the reference's own tee as our error. This module labels every traced key with the set its
screenshot shows, so acceptance.py and qa/golden_spirit_hollow.py can score tee position and length
against the same set.

Evidence per traced key:
  length     the screenshot's measured length (course.HOLES[k]["length"] = 270 + the app's yards from
             the 270 dot; par 3s: PAR3[k]["center"]) against each card set (tees/scorecard.json).
  position   the screenshot tee georeferenced on NAIP (spirit_hollow/hand_zones_ll.json `tee_ll`, tee
             holes only) against each set's tee point in tees/tee_positions.json, and the nearest OSM
             tee box.
Rule: the set whose card yardage is nearest the measured length. Position is the cross-check: when it
points at another set by > 15 yds on a well-registered hole the label is marked `conflict` (none today).
Confidence: high = length margin >= 5 yds and position agrees; medium = one of the two is weak
(margin < 5, shared box, position > 25 yds from every set, or length only); low = margin < 3 and
no position evidence.

The output is committed and treated as fixed truth (re-running only refreshes the evidence numbers);
change a label only with new evidence (a screenshot re-check), and say so in `note`.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
OUT = os.path.join(CD, "spirit_hollow", "screenshot_tee_sets.json")
GOLFER_SET = "Black"

NOTES = {
    "1": "Gold box: 413 measured vs Gold 426 / Black 391, and the screenshot tee is 8 yds from the Gold box vs "
         "40 from Black (commit 55b3ae4).",
    "2B": "Gold: 609 vs the new 607 back tee, which has no OSM box (walk-back in tee_positions).",
    "9B": "Gold: 399 vs Gold 410 / Black 365.",
    "11": "Gold: 348 vs Gold 352 / Black 338; Gold and Black share one OSM box here, 6 yds apart on it.",
    "15": "Length only (par 3, no georeferenced tee): 134 is nearest White 132 (Black 145).",
    "7": "Length only: 159 sits between Black 154 and Gold 165; Black by 1 yd.",
}


def _key(k):
    return int(k) if str(k).isdigit() else k


def build(tee_positions=None):
    sys.path[:0] = [HERE, os.path.join(ROOT, "spirit_hollow")]
    import course                                                    # noqa: E402  (hand map; read only)
    from place_tee import centroid_ll, haversine_yd           # noqa: E402

    card = json.load(open(os.path.join(HERE, "scorecard.json")))
    tp = json.load(open(tee_positions or os.path.join(HERE, "tee_positions.json")))["holes"]
    hz = json.load(open(os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")))["holes"]
    fc = json.load(open(os.path.join(CD, "spirit_hollow", "osm.geojson")))
    boxes = []
    for f in fc["features"]:
        p, g = f["properties"], f["geometry"]
        if p.get("golf") == "tee" and g["type"] == "Polygon":
            boxes.append((p.get("osm_id"), centroid_ll([(c[1], c[0]) for c in g["coordinates"][0]])))
    sets = card["tee_sets"]
    keys = [str(k) for k in course.HOLES] + [str(k) for k in course.PAR3]
    out = {}
    for k in keys:
        ref = k.rstrip("BF")
        i = int(ref) - 1
        if _key(k) in course.HOLES:
            L = float(course.HOLES[_key(k)]["length"])
        else:
            L = float(course.PAR3[_key(k)]["center"])
        yards = {n: s["yards"][i] for n, s in sets.items()}
        gap = {n: round(L - y, 1) for n, y in yards.items()}
        by_len = sorted(yards, key=lambda n: abs(L - yards[n]))
        pick, margin = by_len[0], abs(L - yards[by_len[1]]) - abs(L - yards[by_len[0]])
        row = dict(set=pick, measured_length=L, card_yards=yards, length_gap=gap, length_margin=round(margin, 1),
                   par=course.HOLES[_key(k)]["par"] if _key(k) in course.HOLES else 3)
        conf, flags = "high", []
        if margin < 5:
            conf, flags = "medium", flags + ["length margin < 5 yds"]
        hk = hz.get(k)
        if hk and hk.get("tee_ll"):
            T = (hk["tee_ll"][1], hk["tee_ll"][0])
            dpos = {n: round(haversine_yd(T, (v["lat"], v["lon"])), 1) for n, v in tp[ref]["tees"].items()}
            near = min(dpos, key=dpos.get)
            nb = min(((haversine_yd(T, c), oid) for oid, c in boxes), default=(None, None))
            row.update(position_yd=dpos, position_nearest=near, registration=hk.get("method"),
                       nearest_osm_box=dict(osm_id=nb[1], yd=round(nb[0], 1)) if nb[0] is not None else None)
            shared = tp[ref]["tees"].get(pick, {}).get("shared_with") or []
            if near != pick and dpos[near] + 15 < dpos.get(pick, 1e9):
                conf, flags = "low", flags + [f"conflict: position says {near}"]
                row["conflict"] = True
            elif near != pick and near in shared:
                flags.append(f"position nearest {near} (same OSM box)")
            elif near != pick:
                conf, flags = "medium", flags + [f"position nearest {near} by < 15 yds"]
            if min(dpos.values()) > 25:
                conf = "medium" if conf == "high" else conf
                flags.append("screenshot tee > 25 yds from every placed set (registration or unmapped box)")
        else:
            row["position_yd"] = None
            flags.append("length only (no georeferenced tee)")
            conf = "low" if margin < 3 else "medium"
        row.update(confidence=conf, flags=flags, golfer_set=pick == GOLFER_SET)
        if k in NOTES:
            row["note"] = NOTES[k]
        out[k] = row
    return dict(
        schema="screenshot_tee_sets/1", course="Spirit Hollow Golf Course", app="18Birdies",
        golfer_set=GOLFER_SET,
        doc=__doc__.split("\n\n")[1].strip() if __doc__ else "",
        rule="set = card set nearest the screenshot's measured length; position (hand_zones_ll tee_ll vs "
             "tees/tee_positions.json) is the cross-check",
        sources=dict(measured="spirit_hollow/course.py HOLES[k]['length'] / PAR3[k]['center']",
                     card="course_data/tees/scorecard.json", position="course_data/spirit_hollow/hand_zones_ll.json",
                     placements=os.path.relpath(tee_positions or os.path.join(HERE, "tee_positions.json"), ROOT)),
        holes=out,
        summary={s: sorted((k for k, v in out.items() if v["set"] == s), key=lambda k: (int(k.rstrip("BF")), k))
                 for s in sets})


def load(path=OUT):
    """{traced key (str): set name} from the committed file; {} when it is absent."""
    if not os.path.exists(path):
        return {}
    return {k: v["set"] for k, v in json.load(open(path))["holes"].items()}


def main():
    d = build(sys.argv[1] if len(sys.argv) > 1 else None)
    with open(OUT, "w") as fh:
        json.dump(d, fh, indent=1)
    for k, v in d["holes"].items():
        print(f"{k:>3} {v['set']:<5} {v['confidence']:<6} len {v['measured_length']:.0f} gap {v['length_gap']} "
              f"pos {v.get('position_yd')} {'; '.join(v['flags'])}")
    print(json.dumps(d["summary"]))
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
