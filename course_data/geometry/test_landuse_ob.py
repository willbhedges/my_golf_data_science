"""A landuse=residential area drawn round a whole subdivision (golf course inside it) is not OB inside the course
outline (Crow Canyon CC, blind loop 2026-11-09); houses and land use outside the outline still are."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_holes as bh
from shapely.geometry import Point


def sq(lon, lat, dx, dy):
    return {"type": "Polygon", "coordinates": [[[lon - dx, lat - dy], [lon + dx, lat - dy], [lon + dx, lat + dy],
                                                [lon - dx, lat + dy], [lon - dx, lat - dy]]]}


def feat(props, geom):
    return {"type": "Feature", "properties": props, "geometry": geom}


def world(with_course=True):
    fs = [feat({"landuse": "residential"}, sq(-100.0, 40.0, 0.01, 0.01)),
          feat({"building": "house"}, sq(-100.0005, 40.0, 0.0001, 0.0001)),
          feat({"golf": "hole", "ref": "1", "par": "4"}, {"type": "LineString", "coordinates": [[-100.0, 39.998], [-100.0, 40.001]]})]
    if with_course:
        fs.append(feat({"leisure": "golf_course"}, sq(-100.0, 40.0, 0.002, 0.004)))
    return bh.World({"type": "FeatureCollection", "features": fs})


def at(w, lon, lat):
    x, y = w.tr.transform(lon, lat) if hasattr(w, "tr") else (None, None)
    g = w.proj(Point(lon, lat))
    return w.union["ob"] is not None and w.union["ob"].contains(g)


def test_rough_inside_the_course_is_not_ob():
    w = world()
    assert w.landuse_ob_clipped == 1
    assert not at(w, -100.001, 40.0)          # rough beside the hole, inside the outline
    assert at(w, -100.0005, 40.0)             # the house inside the outline is still OB
    assert at(w, -100.006, 40.0)              # the residential area outside the outline is still OB


def test_without_an_outline_land_use_stays_ob():
    w = world(False)
    assert w.landuse_ob_clipped == 0 and at(w, -100.001, 40.0)
