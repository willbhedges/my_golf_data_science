"""The National Golf Club of Kansas City (Parkville, MO), Black tees: hand-checked landing corridors
(course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Black tee -> its aim point; package rebuilt with the OpenGolfAPI card, routing
checked hole by hole on the whole-course map, course_data/truth/course_map.py). Order = precedence (later wins);
unzoned = rough. Residential course on wooded hills above the Missouri River: tree-lined creeks, ponds, a lake
(9), home lots behind several holes. Review (corridor.py review, all 14 tee shots): the start layers matched the
photo / lidar; no unmown long grass in any corridor; creeks are OSM water lines inside the tree belts.
Start polygons: OSM fairway / bunker / water and the 3DEP lidar canopy (assist.py), checked on NAIP 2020 0.6 m +
CIR, the NAIP years and the lidar render; private lots (house footprints + 25 yds of yard) where the photo shows a
row of houses with lawns running to the course; long grass by hand (tan / textured, unmown in every NAIP year).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401
import assist as A  # noqa: E402

S = "national_kc"
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


def N(left, right, note):
    """native (unmown grass) band between a left and right edge [(along, x)]."""
    return Z("native", band(left, right), note)


EXTRA = {}
NOTE = {}
LOTS = {}          # ref -> False where the house-lot rule draws OB that is not OB on the ground
for _r in ("1", "2", "3", "5", "7", "8", "9", "10", "11", "12", "13", "15", "17", "18"):
    _n, _c = NOTE.get(_r, ("Auto start layers (lidar canopy, OSM fairway / water / sand, house lots) checked on the "
                           "review render.", "medium"))
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r, lots=LOTS.get(_r, True)), note=_n, confidence=_c)

TRACE = dict(holes=H, missing=[])
