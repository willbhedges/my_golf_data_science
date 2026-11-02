"""Fairway band (fairway_band.py), edge profile extension (fairway_edge.py), corridor quality (fairway_quality.py)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fairway_band as FB  # noqa: E402
import fairway_edge as FE  # noqa: E402

LON0, LAT0 = -93.6, 42.0
KX = 111320.0 * 0.7431448   # cos(42 deg)
KY = 110574.0


def ll(x_m, y_m):
    return [LON0 + x_m / KX, LAT0 + y_m / KY]


def rect(x0, y0, x1, y1):
    return [ll(x0, y0), ll(x1, y0), ll(x1, y1), ll(x0, y1)]


def _area_m2(poly):
    from shapely.geometry import Polygon
    return Polygon([((p[0] - LON0) * KX, (p[1] - LAT0) * KY) for p in poly]).area


def _geom(poly):
    from shapely.geometry import Polygon
    return Polygon([((p[0] - LON0) * KX, (p[1] - LAT0) * KY) for p in poly])


def test_band_only_turns_rough_into_fairway():
    fw = dict(lie="fairway", poly=rect(0, 0, 30, 200), src="osm")
    trees = dict(lie="recovery", poly=rect(-20, 50, -2, 100), src="vision2")
    sand = dict(lie="sand", poly=rect(30, 120, 40, 140), src="osm")
    add = FB.band_zones([fw, trees, sand], 5.0)
    assert add and all(z["lie"] == "fairway" and z["src"] == "fairway_band+5yd" for z in add)
    from shapely.ops import unary_union
    band = unary_union([_geom(z["poly"]) for z in add])
    assert band.intersection(_geom(trees["poly"])).area < 0.5
    assert band.intersection(_geom(sand["poly"])).area < 0.5
    assert band.intersection(_geom(fw["poly"])).area < 2.0          # 1e-7 deg rounding slivers only
    # about 5 yds (4.57 m) on every side, minus the hazards
    full = (30 + 2 * 4.572) * (200 + 2 * 4.572) - 30 * 200
    assert 0.8 * full < band.area < 1.01 * full


def test_band_zero_and_no_fairway_are_noops():
    zs = [dict(lie="recovery", poly=rect(0, 0, 10, 10))]
    assert FB.band_zones(zs, 5.0) == []
    pkg = dict(holes={"1": dict(zones_ll=[dict(lie="fairway", poly=rect(0, 0, 30, 200))])})
    out, n = FB.widen_package(pkg, 0.0)
    assert n == 0 and out["holes"]["1"]["zones_ll"] == pkg["holes"]["1"]["zones_ll"]
    out, n = FB.widen_package(pkg, 4.0, lie="first_cut")
    assert n >= 1 and len(pkg["holes"]["1"]["zones_ll"]) == 1           # input not mutated
    assert {z["lie"] for z in out["holes"]["1"]["zones_ll"][1:]} == {"first_cut"}


def test_band_rings_are_hole_free():
    # a fairway with a bunker inside the band area on both sides: the band is cut, parts are simple rings
    fw = dict(lie="fairway", poly=rect(0, 0, 30, 200))
    pond = dict(lie="water", poly=rect(-3, 90, 33, 110))       # crosses the fairway and the band on both sides
    add = FB.band_zones([fw, pond], 6.0)
    from shapely.geometry import Polygon
    for z in add:
        assert Polygon(z["poly"]).is_valid or Polygon(z["poly"]).buffer(0).area > 0
    assert sum(_area_m2(z["poly"]) for z in add) > 0


def test_extension_crossing():
    prof = [[-2, 0.95, 100], [-1, 0.9, 100], [0, 0.8, 100], [1, 0.7, 100], [2, 0.6, 100], [3, 0.4, 100], [4, 0.2, 100]]
    assert abs(FE.extension(prof, 0.5) - 2.5) < 1e-9
    assert FE.extension(prof, 0.9) == 0.0                      # the first outside ring is already below
    sharp = [[-1, 0.9, 100], [0, 0.3, 100], [1, 0.1, 100]]
    assert FE.extension(sharp, 0.5) == 0.0
    assert FE.extension([[0, None, 0], [1, None, 0]], 0.5) is None


def test_corridor_measure():
    import fairway_quality as FQ
    import numpy as np
    from shapely.geometry import box
    corr = box(-50, 180, 50, 330)
    right = np.array([1.0, 0.0])
    t = box(-20, 150, 20, 350)              # truth 40 yds wide
    a = box(-15, 150, 15, 350)              # auto 30 wide
    r = FQ.measure_corridor(a, t, corr, right)
    assert r["width_err"] == -10.0 and r["missing"] == 1500 and r["extra"] == 0
    assert r["best_buf"] == 5 and r["best_iou"] > 0.99


def test_par3_haz_accepts_first_cut():
    import importlib.util
    spec = importlib.util.spec_from_file_location("tf_platform_package", os.path.join(HERE, "package.py"))
    PP = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PP)
    green = [[-10, -160], [10, -160], [10, -180], [-10, -180]]
    h = dict(par3=dict(tee=[0, 0], flag=[0, -170], green=green),
             zones=[("first_cut", [[-40, -140], [40, -140], [40, -200], [-40, -200]]), ("fairway", green)])
    assert set(PP.par3_haz(h).values()) <= {"rough"}
