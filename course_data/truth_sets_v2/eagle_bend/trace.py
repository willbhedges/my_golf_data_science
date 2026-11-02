'''Eagle Bend Golf Course (Lawrence, KS): hand-checked landing corridors of the Gold tee shots (truth set v2, course_data/truth/corridor.py).

Coordinates: (x = yds right of the tee line, along = yds from the tee) in each hole's corridor frame
(course_data/truth/annbriar/render/frames.json: the package's Gold tee -> its aim point). Order = precedence (later
wins); unzoned = rough. The footprint is 130-420 yds along x +/-65 so the truth tee (which can sit up to ~40 yds from
the package tee) keeps its 180-330 yd landing zone on the map.

Start layers: OSM fairway / bunker / water, 3DEP lidar canopy > 2.5 m (vision_any raw/hag.tif; NAIP crowns where
no lidar) and OB (house lots from building footprints / beyond the course outline, only where the photo shows
lots / roads behind the line). Each hole was then checked on the corridor render (photo + zones | photo | lidar
HAG | CIR) and corrected in LATE; anything still unsure is in CHECK.md.
'''
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "truth"))
import corridor as C  # noqa: E402
from corridor import Z, band, ell, poly, rect  # noqa: E402,F401

C.FOOT.update(a0=130.0, a1=420.0)        # before any assist call (assist clips to C.FOOT; build writes it)
import assist as A  # noqa: E402

S = "eagle_bend"
H = {}
LIDAR = "lidar canopy > 2.5 m (3DEP), checked on NAIP"


def auto(ref, trees=True, ob=None, fairway=True, water=True, sand=True):
    z = []
    if trees:
        z += A.canopy(S, ref, note=LIDAR) or A.naip_canopy(S, ref)
    if ob == "lots":
        z += A.house_lots(S, ref)
    elif ob == "outline":
        z += A.outside_outline(S, ref)
    if fairway:
        z += A.osm(S, ref, "fairway")
    if water:
        z += A.osm(S, ref, "water")
    if sand:
        z += A.osm(S, ref, "sand")
    return z


def native_beyond(ref, w=10.0, x0=-65.0, x1=65.0, a0=130.0, a1=420.0, note=None):
    """Long grass (native prairie): the box (x0..x1, a0..a1) minus every OSM fairway in the footprint grown by the
    mown-rough width w (yds). Goes in EXTRA (lowest precedence): trees, water, sand, fairway, OB drawn over it."""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    fw = [Polygon(z["xy"]).buffer(0) for z in A.osm(S, ref, "fairway")]
    g = box(x0, a0, x1, a1)
    if fw:
        g = g.difference(unary_union(fw).buffer(w))
    out = []
    for q in ([g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))):
        if q.geom_type == "Polygon" and q.area >= 60:
            out.append(Z("native", [[round(float(x), 1), round(float(a), 1)] for x, a in list(q.exterior.coords)[:-1]],
                         note or f"native grass (mottled unmown, NAIP 2021) beyond ~{w:g} yds of mown rough"))
    return out


W = 10.0
OB = {}
G = "golfer (plays the course): native here; NAIP 2021 shows the mottled unmown grass"
EXTRA = {
    "2": native_beyond("2", w=W, x1=0.0, note=G + " (left)") + native_beyond("2", w=W, x0=18.0, note=G + " (right, beyond the path)"),
    "3": native_beyond("3", w=W, x1=0.0, note=G + " (left, before the pond)"),
    "5": native_beyond("5", w=W, x1=-5.0, note=G + " (left)"),
    "6": native_beyond("6", w=W, x1=0.0, note=G + " (left)"),
    "11": native_beyond("11", w=W, x0=12.0) + native_beyond("11", w=W, x1=-40.0),
    "13": native_beyond("13", w=W, x0=8.0) + native_beyond("13", w=W, x1=-35.0),
    "15": native_beyond("15", w=W, x1=-30.0),
    "16": native_beyond("16", w=W, x1=-20.0),
    "18": native_beyond("18", w=W, x1=-38.0),
}
LATE = {}           # after the auto layers (win over them): hand corrections from the corridor check
DROP = {}           # ref -> indices of auto zones removed (photo shows they are wrong)
FILTER = {}         # ref -> predicate on an auto zone: False drops it (photo shows it is wrong)
NOTE = {}           # ref -> (note, confidence)

for _r in C.frames(S):
    _a = auto(_r, ob=OB.get(_r))
    _a = [z for i, z in enumerate(_a) if i not in DROP.get(_r, ()) and FILTER.get(_r, lambda q: True)(z)]
    _n, _c = NOTE.get(_r, ("auto start layers checked on the corridor render", "medium"))
    H[_r] = dict(zones=EXTRA.get(_r, []) + _a + LATE.get(_r, []), note=_n, confidence=_c)

TRACE = dict(holes=H, missing=[])
