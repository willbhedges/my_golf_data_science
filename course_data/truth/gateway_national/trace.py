"""Gateway National Golf Links (Madison, IL), Back tees: hand-checked landing corridors (course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(render/frames.json: the package's Back tee -> its aim point). Order = precedence (later wins); unzoned = rough.
Links-style course on reclaimed flood-plain land (Keith Foster, 1998): native prairie / fescue framing almost
every hole, ponds and wetlands, few trees (lidar 2014 leaf-off), industrial park / interstate / race track around.
Start polygons: OSM fairway / bunker / water and the 3DEP lidar canopy (assist.py), checked on NAIP 2023 0.6 m + CIR,
NAIP 2012-2022 and the lidar render; long grass traced by hand (tan / textured, unmown in every NAIP year).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401
import assist as A  # noqa: E402

S = "gateway_national"
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



def N(left, right, note):
    """native (prairie / fescue) band between a left and right edge [(along, x)]."""
    return Z("native", band(left, right), note)


EXTRA = {
    "1": [N([(140, -70), (345, -70)], [(140, -42), (200, -56), (270, -50), (345, -40)], "prairie left of the cart path"),
          N([(140, 28), (200, 28), (260, 32), (345, 35)], [(140, 52), (345, 52)], "fescue right (tufted, tan / grey CIR)")],
    "2": [N([(265, -70), (345, -70)], [(265, -40), (300, -36), (345, -34)], "prairie left beyond the pond")],
    "3": [N([(140, -70), (345, -70)], [(140, -45), (345, -43)], "prairie left of the cart path"),
          N([(140, 18), (220, 20), (345, 22)], [(140, 30), (220, 30), (345, 32)], "fescue strip before the tree line right")],
    "5": [N([(140, -70), (345, -70)], [(140, -30), (200, -30), (250, -38), (300, -40), (345, -40)], "prairie left"),
          N([(140, 32), (345, 34)], [(140, 45), (345, 46)], "fescue between the rough and the cart path right"),
          N([(140, 56), (345, 58)], [(140, 70), (345, 70)], "prairie beyond the cart path right")],
    "6": [N([(255, -48), (345, -48)], [(255, -30), (345, -30)], "fescue between rough and trees left"),
          N([(140, 48), (345, 48)], [(140, 70), (345, 70)], "prairie beyond the cart path right")],
    "8": [N([(300, -40), (345, -40)], [(300, 25), (345, 25)], "prairie beyond the end of the fairway"),
          N([(220, 25), (345, 25)], [(220, 45), (345, 45)], "fescue before the trees right")],
    "9": [N([(140, -48), (300, -48)], [(140, -33), (300, -33)], "fescue strip left"),
          N([(140, 30), (340, 30)], [(140, 45), (340, 45)], "fescue before the tree line right")],
    "10": [N([(140, -70), (345, -70)], [(140, -45), (345, -45)], "prairie left"),
           N([(140, 52), (300, 30), (345, 30)], [(140, 70), (345, 70)], "prairie beyond the cart path right")],
    "11": [N([(160, -55), (260, -42), (345, -27)], [(160, -32), (260, -17), (345, -6)], "prairie strip between 11 and the parallel fairway"),
           N([(150, 18), (260, 30), (345, 55)], [(150, 70), (345, 70)], "fescue right of the fairway and beyond the path")],
    "13": [N([(140, 32), (345, 32)], [(140, 70), (345, 70)], "prairie right"),
           N([(140, -35), (260, -35)], [(140, -27), (260, -27)], "fescue strip between the path and the fairway left")],
    "15": [N([(140, -70), (345, -70)], [(140, -5), (200, -12), (260, -25), (300, -38), (345, -40)], "prairie left"),
           N([(140, 52), (260, 52)], [(140, 70), (260, 70)], "prairie right")],
    "16": [N([(140, -70), (300, -70)], [(140, -32), (220, -34), (300, -30)], "prairie left"),
           N([(140, 25), (300, 25)], [(140, 38), (300, 38)], "fescue between the fairway rough and the path right"),
           N([(140, 55), (300, 55)], [(140, 70), (300, 70)], "prairie beyond the path right")],
    "18": [N([(140, -45), (345, -45)], [(140, -25), (345, -27)], "fescue strip between the cart path and the fairway left")],
}
NOTE = {
    "1": ("Wide fairway (OSM) with fescue / prairie both sides: left beyond the cart path, right from x +28.", "medium-high"),
    "2": ("Pond left (OSM) 140-260; prairie beyond it; trees and the maintenance yard right.", "high"),
    "3": ("Prairie left of the cart path; a fescue strip then the tree line along the industrial park right.", "high"),
    "5": ("Fescue both sides beyond ~10 yds of mown rough; bunker left 245.", "medium (fescue edges +/-5)"),
    "6": ("Trees left (lidar), fescue between them and the rough at 255+; prairie right beyond the path.", "high"),
    "8": ("Dogleg left: fairway ends ~300, prairie beyond it; trees right; fescue before them.", "medium"),
    "9": ("Fescue strip left between the fairways; trees right at +45.", "medium"),
    "10": ("Short par 4: pond / ditch left (OSM water), prairie left and right beyond the path.", "medium"),
    "11": ("Prairie strip between 11 and the parallel fairway left; fescue right.", "medium"),
    "13": ("Water / ditch left (OSM), prairie right.", "medium-high"),
    "15": ("Prairie left (the fairway angles right), prairie right beyond the path.", "medium"),
    "16": ("Fescue both sides; pond beyond 300 left (OSM).", "medium"),
    "18": ("Fescue strip left between the path and the fairway; trees right (lidar).", "high"),
}
LATE = {}
for _r, (_n, _c) in NOTE.items():
    H[_r] = dict(zones=EXTRA.get(_r, []) + auto(_r) + LATE.get(_r, []), note=_n, confidence=_c)

TRACE = dict(holes=H, missing=[])
