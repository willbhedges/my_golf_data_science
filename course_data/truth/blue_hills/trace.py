"""Blue Hills Country Club (Kansas City, MO), Black tees: hand-checked landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Black tee -> its aim point). Order = precedence (later wins); unzoned = rough.
Residential parkland course (1963, Bob Dunning; Korn Ferry Tour host): tree-lined holes with houses behind most of
them, the pond on 5 / 6, a creek on 17 / 18. Start polygons: OSM fairway / bunker / water (mapped on the current,
post-renovation layout: they match NAIP 2021 / 2023), 3DEP lidar canopy (KS_JacksonCo_2006, leaf-off April 2006:
20 years old) and OB beyond the OSM course outline (checked against the house lots), each checked on NAIP 2023 (1 m) and
NAIP 2021 (0.6 m) + CIR, NAIP 2018-2022, and the Meta / WRI 2024 canopy-height map (CHM from ~2018-2020 Maxar
imagery) as the recency check of the 2006 crowns; then corrected by hand (see notes).

The footprint is extended to 415 yds along (FOOT a1 345 -> 415) on this course: the Blue tees are up to 65 yds ahead
of Black (18), and Blue is also solved as a full base set, so its drives (to ~330 from Blue) stay on the hand map.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import corridor as C  # noqa: E402
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401

C.FOOT.update(a1=415.0)            # before any assist call: assist clips to C.FOOT; build writes the footprint
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
    "1": [Z("rough", rect(-8, 12, 322, 362), "2006 lidar crowns right of the fairway at 325-360 are gone: mown rough "
                                             "with a path in NAIP 2021 / 2023 and CIR")],
    "3": [Z("recovery", ell(24, 241, 7, 7), "tree grown since 2006 right of the fairway (NAIP 2021 / 2023, CIR)"),
          Z("recovery", ell(-25, 223, 5, 7), "tree crown left of the fairway past the 2006 lidar edge")],
    "6": [Z("recovery", ell(-35, 331, 8, 10), "tree grown since 2006 left of the fairway (NAIP 2021 / 2023, CIR)")],
    "9": [Z("recovery", ell(-19, 229, 5, 9), "left tree line: crowns 5-8 yds past the 2006 lidar edge")],
    "11": [Z("recovery", ell(9, 332, 7, 6), "trees grown since 2006 right of the fairway (2006 lidar < 2.5 m there)"),
           Z("recovery", ell(17, 317, 6, 6), "tree grown since 2006 right of the fairway"),
           Z("recovery", ell(9, 306, 5, 5), "tree grown since 2006 right of the fairway")],
    "18": [Z("recovery", ell(-42, 352, 10, 6), "left trees past the 2006 lidar edge (NAIP 2021 / 2023)")],
}
LOTS = {}           # ref -> False where the house-lot rule draws OB that is not OB on the ground
NOTE = {}
TEE_SHOTS = ("1", "2", "3", "4", "6", "7", "9", "10", "11", "13", "15", "16", "17", "18")
for _r in TEE_SHOTS:
    _n, _c = NOTE.get(_r, ("Auto start layers (lidar canopy, OSM fairway / water / sand, house lots) checked on the "
                           "review render.", "medium"))
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r, lots=LOTS.get(_r, True)) + LATE.get(_r, []), note=_n,
                 confidence=_c)

TRACE = dict(holes=H, missing=[])
