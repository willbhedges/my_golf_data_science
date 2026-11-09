"""Gateway National Golf Links (Madison, IL) hand truth per hole -> holes_truth.json (read by
course_data/courses/score_auto.py).

  python3 course_data/truth/gateway_national/holes_truth.py

Checked on whole-hole sheets (course_data/truth/hole_sheet.py: NAIP 2023 0.6 m + CIR), tee-area zooms with the OSM tee
pads, the corridor renders and the scorecard (golfify + OpenGolfAPI agree: The Tips 7178, Champions 7092, Back 6623
(72.4/133), Middle 6154, Forward 5187; par 71). The NCCGA played 6623 here in 2024 (listed as "Blue" in April, "Back"
in October) and "Arch" 6377 in Nov 2025 (a combo set not on this card): Back is the base set.

Hole numbering: OSM golf=hole ways for all 18, a continuous routing on the ground (1 NW from the clubhouse, 2 back SW,
3 the long par 5 SW along the industrial park, 4 par 3, 5 E, 6 SW, 7 par 3, 8 N, 9 NE, 10 W, 11 SW, 12 par 3, 13 NE,
14 par 3, 15 SW, 16 NE, 17 par 3, 18 SE to the clubhouse); every Back length matches the card within 2%: correct.

Greens: OSM outlines on the visible greens (checked on the sheets). Tees: as Eagle Knoll (pad kept within 8 yds of
the card; else moved along the line to the card, 'estimated'): 7 / 12 Middle (the box ahead is the Middle box), 10
Champions / Tips (no pad mapped or visible 44 yds behind Back), 15 Champions / Tips.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(CD)
sys.path.insert(0, os.path.join(CD, "imagery"))
import render as R  # noqa: E402

SRC = os.path.join(CD, "courses", "gateway_national", "auto", "package_v0_no_vision.json")
TOL = 8.0
CARD_PAR = [4, 4, 5, 3, 4, 5, 3, 4, 4, 4, 4, 3, 5, 3, 4, 4, 3, 5]     # golfify = OpenGolfAPI card

NOTES = {}

# 2026-11-09 map eye check (courses/gateway_national/EYECHECK_{A,B,C}_1109.md, OPTIMIZE.md section 3)
# tees: {hole: {set: ("ll", [lon, lat], how) | ("frame", (x right, along), how)}}; "frame" = the hole's corridor frame
# (render/frames.json, Back tee -> aim)
TEE_FIX = {
    "2": {"Back": ("ll", [-90.1434917, 38.663402],
                   "pad: OSM tee way 719497753 (eye check A M1; was way 720212696, hole 18's rear pad, 54 yds left "
                   "behind a 8-20 m tree block); ~418 to the green along the dogleg vs card 422")},
    "13": {"The Tips": ("frame", (5.0, -29.0),
                        "estimated: back of the Champions pad (eye check C; was lidar pad 132, 50 yds right across "
                        "the ditch); card 562 = Champions + 5")},
}
# par-3 zones added to the package zones (score_auto.truth_package "extra_zones"; the par-3 package zones are drawn in
# product precedence, native lowest, so the package bunkers / trees / water / fairway still win over these)
EXTRA_ZONES = {
    "7": [dict(lie="native", note="fescue long-right of the green (eye check B, NIR/red 1.05-1.16)",
               poly_ll=[[-90.1486416, 38.6539565], [-90.1486196, 38.6538909], [-90.1486344, 38.6538094],
                        [-90.1485995, 38.6536741], [-90.148894, 38.6535472], [-90.1487878, 38.6533956],
                        [-90.1481436, 38.6536732], [-90.1484116, 38.6540557]])],
    "14": [dict(lie="native",
                note="unmown strip down the left of the tee-to-green corridor, 0-185 (eye check C, NIR 135-150)",
                poly_ll=[[-90.1454631, 38.6592946], [-90.1436005, 38.6597278], [-90.1435169, 38.6595068],
                         [-90.1441713, 38.6593546], [-90.1447694, 38.6591983], [-90.1453735, 38.6590578]])],
}


def main():
    pkg = json.load(open(SRC))
    sets = list(pkg["tee_sets"])
    card_par = CARD_PAR
    out = {}
    est = []
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: int(kv[0])):
        i = int(ref) - 1
        par = int(card_par[i]) if card_par else int(h["par"])
        card = {s: int(pkg["tee_sets"][s]["yards"][i]) for s in sets}
        tees, how = {}, {}
        for s in sets:
            t = (h.get("tees") or {}).get(s) or {}
            ll = t.get("tee_ll")
            meas = t.get("measured_yards")
            if not ll:
                continue
            d = (card[s] - meas) if meas else 0.0
            if abs(d) > TOL:
                aim = t.get("aim_ll") or h["green_ll"]
                fr = R.Frame(ll, aim, ppy=1.0, proj="utm")
                ll = [round(float(v), 7) for v in fr.yds_to_ll([[0.0, float(d)]])[0]]   # + d = further back
                how[s] = f"estimated: pad tee moved {d:+.0f} yds along the line to the card ({meas} measured)"
                est.append((ref, s, d))
            else:
                how[s] = f"pad ({t.get('method')}), measured {meas} vs card {card[s]}"
            tees[s] = [round(float(ll[0]), 7), round(float(ll[1]), 7)]
        for s, (kind, v, why) in TEE_FIX.get(ref, {}).items():
            if kind == "frame":
                fj = json.load(open(os.path.join(HERE, "render", "frames.json")))[ref]["frame"]
                fr = R.Frame(fj["tee_ll"], fj["aim_ll"], ppy=1.0, proj="utm")
                v = fr.yds_to_ll([[float(v[0]), -float(v[1])]])[0]
            tees[s] = [round(float(v[0]), 7), round(float(v[1]), 7)]
            how[s] = why
        out[ref] = dict(par=par, card=card, tees=tees, tee_how=how, green_ll=h["green_ll"],
                        green_poly_ll=h.get("green_polygon_ll"), hole_line_ll=h.get("hole_line_ll"),
                        note=NOTES.get(ref, ""))
        if ref in EXTRA_ZONES:
            out[ref]["extra_zones"] = EXTRA_ZONES[ref]
    doc = dict(schema="holes_truth/1", course="Gateway National Golf Links", slug="gateway_national", likely_set="Back",
               sets=sets, source=os.path.relpath(SRC, ROOT), method=__doc__.strip().split("\n\n", 1)[1],
               holes=out)
    json.dump(doc, open(os.path.join(HERE, "holes_truth.json"), "w"), indent=1)
    print("estimated tees:", est)


if __name__ == "__main__":
    main()
