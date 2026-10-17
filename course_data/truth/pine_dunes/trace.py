"""Pine Dunes Resort & Golf Club (Frankston, TX), Gold tees: hand-checked landing corridors
(course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Gold tee -> its aim point). Order = precedence (later wins); unzoned = rough.
Jay Morrish's pine-forest course in the East Texas sand hills: every hole cut through pine / hardwood forest,
sandy waste areas, ponds. Tree lines = 3DEP lidar canopy (HAG > 2.5 m from the point cloud; the package's bare
DEM is only the 10 m seamless one here), checked on NAIP 2020 / 2022 + CIR; fairways / bunkers / waste sand / water
from OSM, checked on the photo. Review (all 14 tee shots): no unmown long grass in the corridors (the forest floor
under the pines is trees), sandy waste areas are OSM sand.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401
import assist as A  # noqa: E402

S = "pine_dunes"
H = {}


def auto(ref, trees=True, fairway=True, sand=True, water=True, lots=False):
    z = []
    if lots:
        z += A.house_lots(S, ref)
    if trees:
        z += A.canopy(S, ref)
    if fairway:
        z += A.osm(S, ref, "fairway")
    if water:
        z += A.osm(S, ref, "water")
    if sand:
        z += A.osm(S, ref, "sand")
    return z


EXTRA = {}
NOTE = {}
TEE_SHOTS = ("1", "2", "4", "5", "7", "8", "9", "10", "11", "13", "14", "15", "17", "18")
for _r in TEE_SHOTS:
    _n, _c = NOTE.get(_r, ("Forest both sides (NAIP crowns), OSM fairway / sand / water; checked on the review render.",
                           "medium"))
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r), note=_n, confidence=_c)

TRACE = dict(holes=H, missing=[])
