"""Hot Springs Country Club, Arlington Course (Hot Springs, AR), Gold tees: hand-checked landing corridors
(course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Gold tee -> its aim point). Order = precedence (later wins); unzoned = rough.
Classic parkland course (1932, renovated by Coore & Crenshaw): wide mown rough under scattered mature oaks and pines,
tree belts between holes, one pond (hole 9 area), houses / roads along the edges (hole 1 along Malvern Ave).
Start polygons: OSM fairway / bunker / water and the 3DEP lidar canopy (assist.py), checked on NAIP + CIR, the
other NAIP years and the lidar render; private lots (house footprints + 25 yds of yard) where houses back onto a hole.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401
import assist as A  # noqa: E402

S = "hot_springs_arlington"
H = {}


def auto(ref, trees=True, fairway=True, sand=True, water=True, lots=True):
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


EXTRA = {
    "1": [Z("ob", poly((44, 140), (75, 140), (75, 352), (70, 345), (60, 280), (52, 220), (44, 150)),
            "Malvern Ave (US-270B) right of the cart path: beyond the road edge is off the property")],
}
NOTE = {
    "1": ("Wide open par 4 along Malvern Ave: road / OB right beyond the cart path (+42 at 150 to +70 at 340); oaks "
          "left; fairway not separable from the rough on NAIP (dormant Bermuda), so unzoned = rough.", "high"),
}
TEE_SHOTS = ("1", "3", "4", "5", "6", "7", "9", "10", "12", "13", "14", "15", "16", "18")
for _r in TEE_SHOTS:
    _n, _c = NOTE.get(_r, ("Parkland: lidar crowns, OSM fairway / sand / water, house lots; checked on the review render.",
                           "medium"))
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r), note=_n, confidence=_c)

TRACE = dict(holes=H, missing=[])
