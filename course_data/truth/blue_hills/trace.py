"""Blue Hills Country Club (Kansas City, MO), Black tees: hand-checked landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Black tee -> its aim point). Order = precedence (later wins); unzoned = rough.
Residential parkland course (1963, Bob Dunning; Korn Ferry Tour host): tree-lined holes with houses behind most of
them, the pond on 5 / 6, a creek on 17 / 18. Start polygons: OSM fairway / bunker / water (mapped on the current,
post-renovation layout: they match NAIP 2021 / 2023), 3DEP lidar canopy (KS_JacksonCo_2006, leaf-off April 2006:
20 years old) and OB beyond the OSM course outline (checked against the house lots), each checked on NAIP 2023 (1 m) and
NAIP 2021 (0.6 m) + CIR, NAIP 2018-2022, and the Meta / WRI 2024 canopy-height map (CHM from ~2018-2020 Maxar
imagery) as the recency check of the 2006 crowns; then corrected by hand (see notes).

The footprint is extended to 440 yds along (FOOT a1 345 -> 440) on this course: the Blue tees are up to 65 yds and Blue/White up to 99 yds ahead
of Black (18), and Blue and Blue/White are also solved as full base sets, so their drives stay on the hand map.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import corridor as C  # noqa: E402
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401

C.FOOT.update(a1=440.0)            # before any assist call: assist clips to C.FOOT; build writes the footprint
import assist as A  # noqa: E402

S = "blue_hills"
H = {}
OUTLINE = ("OB: beyond the OSM course outline (the property line: it follows the tree line / lot lines behind the "
           "houses; the house-lot rule, footprints + 25 yds, reaches 10-20 yds inside it on 2 / 18)")
LIDAR = "lidar canopy > 2.5 m (3DEP 2006 leaf-off), checked on NAIP 2023 / 2021 and the Meta 2024 CHM"


def auto(ref, trees=True, fairway=True, sand=True, water=True, lots=True):
    z = []
    if trees:
        z += A.canopy(S, ref, note=LIDAR)
    if lots:                       # after the trees: a ball in a back-yard tree is OB
        z += A.outside_outline(S, ref, OUTLINE)
    if fairway:
        z += A.osm(S, ref, "fairway")
    if water:
        z += A.osm(S, ref, "water")
    if sand:
        z += A.osm(S, ref, "sand")
    return z


EXTRA = {}          # added before the auto layers (they win over these)
LATE = {           # added after the auto layers (win over them): hand corrections (2nd pass, zoomed renders)
    "17": [Z("water", poly((-70, 349), (-50, 342), (-30, 338), (-10, 338), (10, 343), (30, 347), (50, 352), (70, 358),
                           (70, 366), (50, 361), (30, 358), (10, 356), (-10, 357), (-30, 359), (-50, 360), (-70, 363)),
             "creek across the hole: the channel (dark in CIR 2021 / NAIP 2023) is 15-20 yds wide at x -30..0, "
             "2-3x the OSM water strip"),
           Z("recovery", poly((-30, 359), (-20, 358), (0, 357), (12, 357), (12, 371), (0, 376), (-20, 374), (-30, 368)),
             "far bank of the creek: dense vegetation (dark in NAIP 2021 / 2023 and CIR, no 2006 lidar height); "
             "uncertain: shrubs / young trees or a wider pool")],
    "1": [Z("recovery", ell(-37, 295, 4, 5), "small tree left grown since 2006 (NAIP 2021 / 2023)"),
          Z("rough", rect(-8, 12, 322, 362), "2006 lidar crowns right of the fairway at 325-360 are gone: mown rough "
                                             "with a path in NAIP 2021 / 2023 and CIR")],
    "3": [Z("recovery", ell(24, 241, 7, 7), "tree grown since 2006 right of the fairway (NAIP 2021 / 2023, CIR)"),
          Z("recovery", ell(-25, 223, 5, 7), "tree crown left of the fairway past the 2006 lidar edge")],
    "13": [Z("recovery", ell(33, 372, 9, 10), "trees right at 360-385 grown since 2006 (NAIP 2021 / 2023)")],
    "6": [Z("recovery", ell(-35, 331, 8, 10), "tree grown since 2006 left of the fairway (NAIP 2021 / 2023, CIR)")],
    "9": [Z("recovery", ell(-19, 229, 5, 9), "left tree line: crowns 5-8 yds past the 2006 lidar edge")],
    "11": [Z("recovery", ell(9, 332, 7, 6), "trees grown since 2006 right of the fairway (2006 lidar < 2.5 m there)"),
           Z("recovery", ell(17, 317, 6, 6), "tree grown since 2006 right of the fairway"),
           Z("recovery", ell(9, 306, 5, 5), "tree grown since 2006 right of the fairway")],
    "18": [Z("recovery", ell(-42, 352, 10, 6), "left trees past the 2006 lidar edge (NAIP 2021 / 2023)"),
           Z("rough", poly((-12, 333), (24, 333), (28, 350), (26, 386), (-6, 386), (-12, 360)),
             "2006 lidar canopy right of the fairway at 333-386 is gone: uniform mown rough in NAIP 2021 / 2023 and "
             "CIR (cleared with the renovation; a few young trees only)")],
}
LOTS = {}           # ref -> False where the house-lot rule draws OB that is not OB on the ground
NOTE = {
    "1": ("Par 5 north from the clubhouse: fairway 150-480 bending right (corner ~290 yds, 35 right); trees left between "
          "the fairway and the houses, OB beyond the course outline 35-50 yds left; bunkers right 265-305; trees right "
          "beyond them. 2006 crowns right at 325-360 are gone (rough).", "high"),
    "2": ("Fairway 200-400; houses left behind a tree line (OB at the course outline 30-50 yds left); tree lines both "
          "sides; fairway bunker left 270-285.", "high"),
    "3": ("Narrow fairway (25-30 yds) bending left through trees, tree-lined both sides; a tree grown since 2006 right "
          "at 240.", "high"),
    "4": ("Fairway 160-400 bending left; houses left (OB 35+ yds left); trees both sides.", "high"),
    "6": ("Par 5 over the pond (carry ~110 from Black); fairway 190-440 bending right; houses / OB left along the "
          "course outline; scattered trees both sides, one grown since 2006 left at 330.", "high"),
    "7": ("Fairway to ~300, then a dogleg left around a clump of trees; bunkers left 260-280 and 300-320; houses far "
          "left.", "high"),
    "9": ("Straight fairway; bunkers left 265 and right 280-290; the right tree line 5-10 yds off the fairway; houses / "
          "OB left beyond the trees.", "high"),
    "10": ("Fairway bending left toward the green; clumps of trees right at 290-345; houses / OB left.", "high"),
    "11": ("Narrow fairway bending left; trees right at 300-340 grown since 2006 (2006 lidar < 2.5 m there); houses / OB "
           "left.", "medium (young trees right: crown size +/-3 yds)"),
    "13": ("Par 5: long fairway drifting left; tree lines both sides; creek and OB far left.", "high"),
    "15": ("Straight chute: tree lines both sides 12-18 yds off the fairway centre.", "high"),
    "16": ("Straight, narrow fairway (~25 yds); trees both sides 10-15 yds off the line.", "high"),
    "17": ("Dogleg right: fairway 160-325; the creek crosses at 338-360 from Black (300-325 from Blue): its channel is "
           "15-20 yds wide at the line, 2-3x the OSM strip; vegetation on the far bank; trees both sides at the corner.",
           "medium (creek width / far-bank vegetation +/-4 yds)"),
    "18": ("Par 5 home: fairway from 225 bending left; houses / OB left (outline 30-40 yds left); trees right; fairway "
           "bunker right at 320.", "high"),
}
TEE_SHOTS = ("1", "2", "3", "4", "6", "7", "9", "10", "11", "13", "15", "16", "17", "18")
for _r in TEE_SHOTS:
    _n, _c = NOTE.get(_r, ("Auto start layers (lidar canopy, OSM fairway / water / sand, house lots) checked on the "
                           "review render.", "medium"))
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r, lots=LOTS.get(_r, True)) + LATE.get(_r, []), note=_n,
                 confidence=_c)

TRACE = dict(holes=H, missing=[])
