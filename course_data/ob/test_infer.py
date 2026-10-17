"""Offline unit tests for OB inference (synthetic course; no network).  python -m pytest -q course_data/ob"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evaluate  # noqa: E402
import fetch  # noqa: E402
import infer  # noqa: E402
from shapely.geometry import Point, Polygon  # noqa: E402

LON0, LAT0 = -91.14, 40.76


def P():
    return infer.Proj(LON0, LAT0)


def ll(pr, xy):
    o = pr.xy([[LON0, LAT0]])[0]
    return [[float(a), float(b)] for a, b in pr.ll(np.asarray(xy, float) + o)]


def square(pr, cx, cy, r):
    return ll(pr, [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)])


def synthetic():
    """A 420-yd hole due north (metric yards; x east), course outline x in [-150, 70], houses at x = 85."""
    pr = P()
    tee, green = ll(pr, [(0, 0)])[0], ll(pr, [(0, 420)])[0]
    fairway = ll(pr, [(-20, 150), (20, 150), (20, 400), (-20, 400)])
    water = ll(pr, [(30, 250), (55, 250), (55, 290), (30, 290)])
    course = ll(pr, [(-150, -50), (70, -50), (70, 480), (-150, 480)])
    hole = dict(ref="1", par=4, tee_ll=tee, aim_ll=ll(pr, [(0, 250)])[0], green_ll=green,
                hole_line_ll=[tee, green], tees={"Black": dict(tee_ll=tee, aim_ll=ll(pr, [(0, 250)])[0])},
                zones_ll=[dict(lie="fairway", poly=fairway, src="osm", p=1.0),
                          dict(lie="water", poly=water, src="osm", p=1.0),
                          dict(lie="ob", poly=ll(pr, [(70, -50), (300, -50), (300, 480), (70, 480)]),
                               src="osm:course_boundary", p=1.0)])
    pkg = dict(schema="course_package/1", slug="synthetic", tee_set="Black",
               course=dict(slug="synthetic", boundary=dict(type="MultiPolygon", coordinates=[[course]])),
               holes={"1": hole}, stages={})
    from shapely.geometry import MultiPolygon
    houses = [Polygon(square(pr, 85, y, 8)) for y in range(150, 420, 30)]
    L = dict(course=MultiPolygon([Polygon(course)]), buildings=houses, parcels=[], roads=[], landuse=[], tags=[],
             have=["test"])
    return pkg, L, pr


def ob_union(zs, pr):
    from shapely.ops import unary_union
    return unary_union([Polygon(pr.xy(z["poly"])) for z in zs])


def test_quadkey():
    assert fetch.quadkey(-90, 45, 1) == "0"
    assert fetch.quadkey(90, -45, 1) == "3"
    assert len(fetch.quadkey(LON0, LAT0, 9)) == 9
    assert fetch.quadkeys_for([LON0, LAT0, LON0 + 0.001, LAT0 + 0.001]) == [fetch.quadkey(LON0, LAT0, 9)]


def test_house_lots_right_only_and_protected():
    pkg, L, pr = synthetic()
    out = infer.apply_ob(pkg, layers=L, params=dict(house_d=20, house_close=20, road_margin=None, out_off=None,
                                                    parcel_off=None), use_reframe=False)
    zs = [z for z in out["holes"]["1"]["zones_ll"] if z["lie"] == "ob"]
    assert zs and all(z["src"] == "ob:house" and 0 < z["p"] <= 1 for z in zs)
    o = pr.xy([[LON0, LAT0]])[0]
    g = ob_union(zs, pr)
    gx0, gy0, gx1, gy1 = g.bounds
    assert gx0 - o[0] >= 85 - 8 - 20 - 1.5          # starts house_d in front of the houses
    assert gx1 - o[0] <= infer.CORRIDOR + 1.5         # never beyond the corridor
    # the geometry stage's outline OB is replaced (mode replace); fairway and water are kept
    lies = [(z["lie"], z["src"]) for z in out["holes"]["1"]["zones_ll"]]
    assert ("ob", "osm:course_boundary") not in lies and ("fairway", "osm") in lies and ("water", "osm") in lies
    # the row of houses (30 yds apart) gives one continuous strip
    assert g.geom_type == "Polygon"
    assert out["holes"]["1"]["ob_inferred"]["evidence"] == ["house"]
    assert out["stages"]["ob"].startswith("ok")


def test_never_overrides_water_or_fairway():
    pkg, L, pr = synthetic()
    out = infer.apply_ob(pkg, layers=L, params=dict(house_d=None, road_margin=None, out_off=-60, out_dev=None,
                                                    parcel_off=None), use_reframe=False)
    zs = [z for z in out["holes"]["1"]["zones_ll"] if z["lie"] == "ob"]
    g = ob_union(zs, pr)
    for z in pkg["holes"]["1"]["zones_ll"][:2]:
        assert g.intersection(Polygon(pr.xy(z["poly"]))).area < 1.0


def test_outside_offset_and_add_mode():
    pkg, L, pr = synthetic()
    prm = dict(house_d=None, road_margin=None, out_off=-20, out_dev=None, parcel_off=None)
    out = infer.apply_ob(pkg, layers=L, params=prm, mode="add", use_reframe=False)
    srcs = [z["src"] for z in out["holes"]["1"]["zones_ll"]]
    assert "osm:course_boundary" in srcs and "ob:outside" in srcs
    o = pr.xy([[LON0, LAT0]])[0]
    zs = [z for z in out["holes"]["1"]["zones_ll"] if z["src"] == "ob:outside"]
    from shapely.geometry import box
    band = ob_union(zs, pr).intersection(box(o[0] - 200, o[1] + 100, o[0] + 200, o[1] + 400))
    assert band.bounds[0] - o[0] >= 70 - 20 - 1.5        # the outline pulled 20 yds in; behind the tee may be OB too
    # re-running is idempotent
    again = infer.apply_ob(out, layers=L, params=prm, mode="add", use_reframe=False)
    assert len(again["holes"]["1"]["zones_ll"]) == len(out["holes"]["1"]["zones_ll"])


def test_parcels_beat_house_buffers():
    pkg, L, pr = synthetic()
    lot = Polygon(ll(pr, [(50, 100), (200, 100), (200, 440), (50, 440)]))
    L = dict(L, parcels=[lot, Polygon(pkg["course"]["boundary"]["coordinates"][0][0])])
    R = infer.Regions(L)
    assert len(R.private) == 1 and R.lots is not None              # the course's own parcel is dropped
    out = infer.apply_ob(pkg, layers=L, params=dict(house_d=20, house_close=20, parcel_off=0, road_margin=None,
                                                    out_off=None), use_reframe=False)
    zs = [z for z in out["holes"]["1"]["zones_ll"] if z["lie"] == "ob"]
    assert {z["src"] for z in zs} == {"ob:parcel"}                  # every house is inside the lot
    o = pr.xy([[LON0, LAT0]])[0]
    assert abs(ob_union(zs, pr).bounds[0] - o[0] - 50) < 2


def test_roads_and_golf_buildings():
    from shapely.geometry import LineString
    pkg, L, pr = synthetic()
    club = Polygon(square(pr, -40, 60, 10))                       # inside the outline: clubhouse, not OB
    road = LineString(ll(pr, [(-50, -100), (-50, 600)]))           # a public road through the course
    L = dict(L, buildings=[club], roads=[(road, 5.0)])
    R = infer.Regions(L)
    assert R.houses == []
    inside = infer.apply_ob(pkg, layers=L, params=dict(house_d=20, road_margin=5, road_inside=True, out_off=None,
                                                       parcel_off=None), use_reframe=False)
    out = infer.apply_ob(pkg, layers=L, params=dict(house_d=20, road_margin=5, road_inside=False, out_off=None,
                                                    parcel_off=None), use_reframe=False)
    assert any(z["src"] == "ob:road" for z in inside["holes"]["1"]["zones_ll"])
    assert not any(z["lie"] == "ob" for z in out["holes"]["1"]["zones_ll"])


def test_no_layers_leaves_package():
    pkg, L, pr = synthetic()
    pkg["course"]["boundary"] = None
    out = infer.apply_ob(pkg, layers=dict(course=None, buildings=[], parcels=[], roads=[], landuse=[], tags=[], have=[]),
                         use_reframe=False)
    assert out["stages"]["ob"].startswith("missing") and out["holes"] == pkg["holes"]


def test_search_or_and_loho_pick():
    cells = [dict(truth=np.array([1, 1, 0, 0], bool)), dict(truth=np.array([0, 0, 1, 0], bool))]
    grid = dict(a=[None, 1], b=[None, 2])
    M = dict(a=[np.zeros(8, bool), np.array([1, 1, 0, 0, 0, 0, 0, 0], bool)],
             b=[np.zeros(8, bool), np.array([0, 0, 0, 0, 0, 0, 1, 1], bool)])
    combos, I, U = evaluate.search(cells, M, grid)
    j, iou = evaluate.best(combos, I, U, np.array([True, True]))
    assert combos[j] == dict(a=1, b=2) and iou == pytest.approx(3 / 4)
    j, iou = evaluate.best(combos, I, U, np.array([True, False]))
    assert combos[j] == dict(a=1, b=None) and iou == 1.0          # the simplest of the ties


def test_ref_of():
    assert evaluate.ref_of("2F") == "2" and evaluate.ref_of("9B") == "9" and evaluate.ref_of("10") == "10"
