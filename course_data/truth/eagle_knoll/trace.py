"""Eagle Knoll Golf Club (Hartsburg, MO), Back (blue) tees: hand-checked landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Back tee -> its aim point). Order = precedence (later wins); unzoned = rough.
Wooded, hilly parkland course in the Missouri River bluffs: tree lines on almost every hole, ponds on 3/6/14,
creek beds in the woods. Start polygons: OSM fairway / bunker / water and the 2015 3DEP lidar canopy (assist.py),
each checked on NAIP 2022 0.6 m + CIR, NAIP 2012-2020 and the lidar render, then corrected by hand (see notes).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401
import assist as A  # noqa: E402

S = "eagle_knoll"
H = {}


def auto(ref, trees=True, fairway=True, sand=True, water=True):
    """The checked start layers for a hole: trees (lidar), fairway, water, bunkers (OSM)."""
    z = []
    if trees:
        z += A.canopy(S, ref)
    if fairway:
        z += A.osm(S, ref, "fairway")
    if water:
        z += A.osm(S, ref, "water")
    if sand:
        z += A.osm(S, ref, "sand")
    return z


NOTE = {
    "1": ("Fairway (OSM) 140-270 then the hole turns left between tree lines: trees right from 220 (lidar edge = "
          "2022 photo), trees left 240-300 (x < -45), one tree left at 150. Bunker left 225. The mounded rough left "
          "of the fairway (150-240) is mown in every year: rough.", "high"),
    "3": ("Forced carry over the ravine woods / pond to a fairway that starts ~185 and bends left; woods left all the "
          "way (rough strip 7-15 yds). The OSM course outline crosses the ravine: not OB on the ground (no fence, "
          "no houses; woods continue), so no OB in the corridor.", "high"),
    "4": ("Fairway (OSM) 180-345 x -15..+15; woods left 20-30 yds off; hole 8's fairway right (fairway lie). The "
          "tan band right of the cart path in NAIP 2020 is dry mown rough (2020 is a dry year everywhere).", "high"),
    "5": ("Tree-lined: woods right 0-10 yds off the fairway edge the whole corridor (lidar edge matches 2022), "
          "open rough + cart path left to the trees at x -35..-45. Bunker right 245.", "high"),
    "7": ("Woods right at the fairway edge (x +12..+25); hole 13's parallel fairway left beyond the cart path "
          "(fairway lie).", "high"),
    "8": ("Bunkers left 255 / right 205 (OSM = photo); trees left 140-220; hole 4's fairway right. The tan "
          "upper-left area in NAIP 2020 is dry rough (mown in 2012-2018 and 2022).", "high"),
    "9": ("Two overlapping OSM fairway polygons (= the mown fairway). Right beyond the cart path at 280+: unmown "
          "grass (dark green 2022, tan 2020, bright CIR, no lidar height) = long grass. Trees right 150-280.",
          "medium (long-grass extent right)"),
    "10": ("Chute: trees right at the fairway edge (x +8..+15) the whole corridor; trees left from 260, open rough "
           "with trees beyond left before that.", "high"),
    "11": ("Doglegs right. Left: a strip of unmown grass (x -70..-42, 175-305; dark in 2012-2022 NAIP, bright CIR, "
           "no lidar height) beyond mown rough; trees right 230-280 beyond the cart path.",
           "medium (long-grass strip edges +/-5)"),
    "13": ("Fairway drifts right of the tee line (x -15..+5 at 150 to +5..+45 at 340); hole 7's fairway left "
           "(fairway lie); trees right beyond the cart path.", "high"),
    "14": ("Short par 4: fairway to ~210, pond 200-260 across the line (OSM = CIR water), green surround beyond; "
           "woods both sides. Lay up or carry ~265.", "high"),
    "15": ("Chute bending left: woods both sides, the right tree line 5-12 yds off the fairway.", "high"),
    "17": ("Creek (OSM water hazard, a wooded / grassed drainage) left 140-240 then crossing diagonally 250-345 "
           "between the first fairway and the second; woods right beyond the cart path.",
           "medium (creek width where it is grassed)"),
    "18": ("Trees right 240-340 beyond the cart path, trees left 140-220; a row of houses left: their back yards "
           "(houses ~65-100 yds left, yards ~25 yds) end ~45-70 yds left of the line: OB there (the OSM course outline "
           "runs 10-20 yds inside the yards).",
           "medium (OB line +/-8: no stakes visible)"),
}
EXTRA = {
    "9": [Z("native", poly((38, 280), (45, 285), (50, 300), (52, 330), (55, 350), (75, 350), (75, 280)),
            "unmown grass right of the cart path")],
    "11": [Z("native", poly((-75, 175), (-58, 175), (-48, 190), (-43, 220), (-42, 260), (-45, 290), (-55, 305),
                            (-75, 305)), "unmown grass strip left")],
    "18": A.house_lots(S, "18", 25.0, 45.0, "house lots left: footprints + 25 yds of back yard (no fence / stakes "
                                            "visible; the OSM outline runs 10-20 yds inside the yards)"),
}
# second pass (zoomed photo / CIR / NAIP 2020 with the lidar edge): crowns that grew past the 2015 lidar edge
LATE = {
    "10": [Z("recovery", band([(145, 21), (165, 20), (175, 22), (185, 21), (200, 21), (230, 22), (262, 24)],
                              [(145, 42), (262, 42)]),
             "right tree line: 2020 / 2022 crowns reach x +20..+24 (2015 lidar edge +22..+37 at 170-180)")],
}
for _r, (_n, _c) in NOTE.items():
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r) + LATE.get(_r, []), note=_n, confidence=_c)

TRACE = dict(holes=H, missing=[])
