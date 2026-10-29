"""Eagle Knoll hand truth per hole -> holes_truth.json (format read by course_data/courses/score_auto.py).

  python3 course_data/truth/eagle_knoll/holes_truth.py

Checked on whole-hole sheets (course_data/truth/hole_sheet.py: NAIP 2022 0.6 m + CIR), tee-area zooms with the OSM
tee pads, the corridor renders (NAIP 2012-2022, 3DEP lidar 2015 HAG) and the scorecard (golfify + OpenGolfAPI, which
agree: Eagle/gold 6920, Back/blue 6667, Middle/white 6186, Forward/red 5174; par 72; NCCGA used the blue tees here in
2015 (6682) and 2025 (6512), so Back is the likely tournament set).

Hole numbering: the OSM golf=hole ways (17 of 18; hole 9's line is the package's own) give a routing that is
continuous on the ground (1 S from the clubhouse, 2 W par 3, 3 W over the woods, 4 N, 5 W, 6 par 3 over the pond,
7 SE, 8 S, 9 NE to the clubhouse, 10 NW, 11 S, 12 par 3 N, 13 NW, 14 E over the pond, 15 NW, 16 par 3 E, 17 SE,
18 SE to the clubhouse) and every hole's measured length matches the card within 2% for Back: numbering correct.

Greens: every OSM green outline sits on the visible green in NAIP 2022 / CIR (checked on all 18 sheets): kept.

Tees: the package's tee for a set is kept when it sits on a visible / OSM pad and its measured length (tee -> hole
line -> green centre) is within 8 yds of the card. Otherwise (no separate pad mapped or visible for that set: the
Eagle box shares the Back pad on 11, 17, 18; Forward on 8 and 18) the truth tee is the pad tee moved along the tee
line by (card - measured), flagged 'estimated' (the box is too small to see in 0.6 m NAIP under trees).
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

SRC = os.path.join(CD, "courses", "eagle_knoll", "auto", "package_v0_no_vision.json")
TOL = 8.0
CARD_PAR = [4, 3, 4, 4, 4, 3, 5, 4, 5, 4, 4, 3, 5, 4, 4, 3, 5, 4]     # golfify = OpenGolfAPI card

# Re-check on the sharper photo (course_data/truth/recheck.py renders, recheck/): hand-placed tees and hole-line bends,
# in each hole's reference frame (ref_frame: the first-pass Back tee -> its 250-yd hole-line point; par 3: -> green):
# (x yds right of that line, along yds from that tee toward the green).
TEE_AT = {          # ref -> {set: (x, along, note)}
    "4": {"Back": (-4.9, 7.6, "the Back box is the small OSM pad 7-20 yds ahead of the Eagle pad (x -10..0), at the "
                               "back of its centre line, which measures the card 399; the first pass had it on the "
                               "front edge of the Eagle pad (406, +7)")},
}
LINE_AT = {}        # ref -> ([(x, along), ...] new hole-line vertices from the tee end to before the green, note)

NOTES = {
    "1": "Par 4 downhill from the clubhouse; fairway 140-270 then turns left between tree lines (left 240-300, right "
         "from 220); bunker left at 225.",
    "2": "Par 3, open; green outline OSM. No water near the green.",
    "3": "Par 4 over a wooded ravine and the pond (forced carry ~200 from Back): fairway starts at ~185 and bends "
         "left; woods left all the way; the OSM course outline crosses the ravine woods (not OB on the ground).",
    "4": "Par 4 uphill; woods left 20-30 yds off the fairway; hole 8's fairway right (playable).",
    "5": "Par 4, tree-lined: woods right within 0-10 yds of the fairway edge the whole way; open rough + cart path left.",
    "6": "Par 3 over the pond: water short, left and right of the green; bunkers long.",
    "7": "Par 5: woods right hug the fairway; hole 13's fairway left (playable).",
    "8": "Par 4: bunkers left 255 and right 205; trees left 140-220; hole 4's fairway right (playable).",
    "9": "Par 5 up to the clubhouse; unmown grass right beyond the cart path at 280+ (NAIP 2020 tan, 2022 dark green / "
         "CIR bright, no lidar height); trees right 150-280.",
    "10": "Par 4 down a chute: trees right at the fairway edge (x +10..+15), trees left from 260.",
    "11": "Par 4 doglegging right: a strip of unmown grass left (x -70..-42, 180-300: dark in every NAIP year, bright "
          "CIR, no lidar height); trees right 230-280.",
    "12": "Par 3, bunkers right and long.",
    "13": "Par 5: hole 7's fairway left (playable), trees right beyond the cart path.",
    "14": "Short par 4 (265) with the pond between ~200 and ~260 in front of the green: lay up short of 200 or carry "
          "~265; woods both sides.",
    "15": "Par 4 down a chute: woods both sides within ~10 yds of the fairway; fairway bends left.",
    "16": "Par 3 through a chute of trees; drainage creek short-right of the green.",
    "17": "Par 5: creek (OSM penalty area) left 140-240, then crossing diagonally 250-345 between the two fairways; "
          "woods right.",
    "18": "Par 4 home: trees right 240-340 beyond the cart path, trees left 140-220; houses far left (x < -75).",
}


def ref_frame(h, tee_ll, par, length=None):
    sys.path.insert(0, os.path.join(CD, "platform"))
    import tee_line as TL
    aim, _ = TL.aim_point(tee_ll, h.get("hole_line_ll"), h["green_ll"], length, par)
    return dict(tee_ll=[round(float(v), 7) for v in tee_ll], aim_ll=[round(float(v), 7) for v in aim])


def at(rf, x, along):
    fr = R.Frame(rf["tee_ll"], rf["aim_ll"], ppy=1.0, proj="utm")
    return [round(float(v), 7) for v in fr.yds_to_ll([[float(x), -float(along)]])[0]]


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
        rf = ref_frame(h, tees.get("Back") or next(iter(tees.values())), par, card.get("Back"))
        for s, (x, al, note) in TEE_AT.get(ref, {}).items():
            tees[s] = at(rf, x, al)
            how[s] = f"recheck: {note}"
        line = h.get("hole_line_ll")
        if ref in LINE_AT:
            pts, note = LINE_AT[ref]
            line = [at(rf, x, al) for x, al in pts]
            how["line"] = f"hole line bent by hand: {note}"
        out[ref] = dict(par=par, card=card, tees=tees, tee_how=how, green_ll=h["green_ll"],
                        green_poly_ll=h.get("green_polygon_ll"), hole_line_ll=line, ref_frame=rf,
                        note=NOTES.get(ref, ""))
    doc = dict(schema="holes_truth/1", course="Eagle Knoll Golf Club", slug="eagle_knoll", likely_set="Back",
               sets=sets, source=os.path.relpath(SRC, ROOT), method=__doc__.strip().split("\n\n", 1)[1],
               holes=out)
    json.dump(doc, open(os.path.join(HERE, "holes_truth.json"), "w"), indent=1)
    print("estimated tees:", est)


if __name__ == "__main__":
    main()
