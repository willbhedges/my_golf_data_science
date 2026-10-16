"""Checks for build_holes.py on the committed Spirit Hollow OSM extract (offline)."""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
GEOJSON = os.path.join(HERE, "..", "spirit_hollow", "osm.geojson")
sys.path[:0] = [HERE, os.path.join(HERE, "..", "..", "mozingo")]

pytest.importorskip("shapely")
pytest.importorskip("pyproj")
pytestmark = pytest.mark.skipif(not os.path.exists(GEOJSON), reason="no osm.geojson")

import build_holes as bh  # noqa: E402

LIES = {"fairway", "recovery", "native", "water", "sand", "ob"}


@pytest.fixture(scope="module")
def built():
    with open(GEOJSON) as fh:
        fc = json.load(fh)
    world = bh.World(fc)
    return fc, world, bh.build(fc, world=world)[0], bh.build(fc, world=world, frame="yard")[0]


def test_all_holes_with_pars(built):
    _, _, holes, _ = built
    assert sorted(holes, key=int) == [str(i) for i in range(1, 19)]
    assert sum(h["par"] for h in holes.values()) == 72
    assert all(h["par"] == 3 for k, h in holes.items() if "par3" in h)


def test_frame_contract(built):
    _, _, holes, yard = built
    for k, h in holes.items():
        tee, d = np.array(h["tee"]), np.array(h["dot270"])
        assert d[0] == pytest.approx(tee[0]) and d[1] < tee[1]              # tee line points up
        assert np.linalg.norm(d - tee) / 270 == pytest.approx(h["px_per_yd"], rel=1e-3)
        assert 0 <= h["tee"][0] <= bh.W and 0 <= h["tee"][1] <= bh.H
        assert 0 <= h["green"][0] <= bh.W and 0 <= h["green"][1] <= bh.H
        # pixel and yard frames agree on where the green is (yds right, yds along)
        g_px = (np.array(h["green"]) - tee) / h["px_per_yd"]
        assert np.allclose(g_px, yard[k]["green"], atol=0.3)
        assert yard[k]["tee"] == (0.0, 0.0) and yard[k]["dot270"] == (0.0, -270.0)


def test_zones_are_simple_named_polygons(built):
    _, _, holes, _ = built
    for h in holes.values():
        assert h["zones"], "every hole has some mapped zone"
        for name, poly in h["zones"]:
            assert name in LIES and len(poly) >= 3
        names = [n for n, _ in h["zones"]]
        order = [bh.ORDER.index(n) for n in names if n != "ob"]
        assert order == sorted(order)                                         # later zones win


def test_lengths_match_the_line(built):
    fc, world, holes, _ = built
    # hand-traced app yardages (spirit_hollow/course.py); the length-matched tee lands within 25 yds
    hand = {"1": 413, "4": 520, "5": 397, "6": 421, "8": 375, "10": 521, "11": 348, "13": 407,
            "14": 418, "16": 388, "18": 516, "12": 177, "15": 134}
    alt = bh.build(fc, lengths={k: float(v) for k, v in hand.items()}, world=world)[0]
    for k, v in hand.items():
        L = alt[k]["par3"]["center"] if "par3" in alt[k] else alt[k]["length"]
        assert abs(L - v) <= 25, (k, L, v)


def test_model_runs_on_it(built):
    import tee_strategy as t
    _, _, holes, _ = built
    h = holes["1"]
    tee, f, r, ppy = t.hole_frame(h)
    pts = tee + np.outer([250.0, 280.0], f) * ppy
    lies = t.lie_at(h, pts)
    assert set(lies) <= LIES | {"rough"}


def test_holefree_splits_rings():
    from shapely.geometry import Polygon
    donut = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)], [[(40, 40), (60, 40), (60, 60), (40, 60)]])
    parts = bh._holefree(donut)
    assert all(not p.interiors for p in parts)
    assert sum(p.area for p in parts) == pytest.approx(donut.area)
