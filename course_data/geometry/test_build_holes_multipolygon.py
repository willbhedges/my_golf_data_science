"""build_holes on a green / tee that is a MultiPolygon (synthetic, offline; no OSM extract needed)."""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "..", "mozingo")]
pytest.importorskip("shapely")
pytest.importorskip("pyproj")
import build_holes as bh  # noqa: E402
from shapely.geometry import MultiPolygon, Polygon  # noqa: E402

LAT0, LON0 = 39.0, -95.0
D = 0.9144 / 111320


def ll(x, y):
    """yards east / north of (LAT0, LON0) -> [lon, lat]"""
    return [LON0 + x * D / np.cos(np.radians(LAT0)), LAT0 + y * D]


def feat(props, gtype, coords):
    return {"type": "Feature", "properties": props, "geometry": {"type": gtype, "coordinates": coords}}


def test_largest_polygon():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1)]), Polygon([(5, 5), (9, 5), (9, 9)])])
    assert bh.largest_polygon(mp).area == 8.0
    p = Polygon([(0, 0), (1, 0), (1, 1)])
    assert bh.largest_polygon(p) is p


@pytest.mark.parametrize("kind", ["bowtie", "multipolygon"])
def test_multipart_green_builds(kind):
    """tomahawk_hills card-blind crash: 'MultiPolygon' object has no attribute 'exterior' in frame_for."""
    tee = [ll(-5, -5), ll(5, -5), ll(5, 5), ll(-5, 5), ll(-5, -5)]
    if kind == "bowtie":     # a self-intersecting ring: buffer(0) splits it into two triangles
        green = feat({"golf": "green"}, "Polygon", [[ll(-12, 390), ll(12, 410), ll(12, 390), ll(-12, 410), ll(-12, 390)]])
    else:                    # an OSM multipolygon relation with two parts
        a = [ll(-12, 390), ll(12, 390), ll(12, 410), ll(-12, 410), ll(-12, 390)]
        b = [ll(30, 395), ll(34, 395), ll(34, 399), ll(30, 399), ll(30, 395)]
        green = feat({"golf": "green"}, "MultiPolygon", [[a], [b]])
    fc = {"type": "FeatureCollection", "features": [
        feat({"golf": "hole", "ref": "1", "par": "4"}, "LineString", [ll(0, 0), ll(0, 400)]),
        green, feat({"golf": "tee"}, "Polygon", [tee])]}
    world = bh.World(fc)
    assert world.greens and all(g["geom"].geom_type == "Polygon" for g in world.greens)
    holes, _ = bh.build(fc, world=world, frame="yard")
    assert "1" in holes and holes["1"]["par"] == 4 and holes["1"].get("green_polygon")
