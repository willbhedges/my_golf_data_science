import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "vision_any"))
import tree_edge_bias as TEB  # noqa: E402


def _grid():
    from affine import Affine
    import layers as L
    S = L.Stack()
    S.crs, S.res, S.W, S.H = "EPSG:32615", 1.0, 400, 400
    x0, y0 = 500000.0, 4500000.0
    S.transform = Affine(1.0, 0, x0, 0, -1.0, y0 + 400)
    S.ll_to_rc([[0, 0]])
    return S, x0, y0


def _ll(S, x, y):
    lon, lat = S._inv.transform(x, y)
    return [float(lon), float(lat)]


def _circle(S, cx, cy, r):
    from shapely.geometry import Point
    from shapely.ops import transform
    return transform(lambda x, y: S._inv.transform(x, y), Point(cx, cy).buffer(r, 64))


def test_short_auto_crown_gives_a_positive_edge_offset_and_a_missed_crown():
    S, x0, y0 = _grid()
    tee, aim = (x0 + 200, y0 + 10), (x0 + 200, y0 + 390)
    c1 = (x0 + 225, y0 + 10 + 200)            # 219 yds out, 27 yds right
    c2 = (x0 + 170, y0 + 10 + 250)            # a crown the auto layer does not have
    truth = _circle(S, *c1, 12.0).union(_circle(S, *c2, 8.0))
    auto = {"lidar HAG rule (vision_any/2)": [_circle(S, *c1, 9.0)]}
    foot = _circle(S, x0 + 200, y0 + 200, 190.0)
    z = np.zeros((S.H, S.W), np.float32)
    hm = z.copy()
    hm[:, :] = 0.0
    ctx = dict(hm=hm + 5.0, chm=z, ndvi=z, thr=2.5)
    m = TEB.measure_hole(S, auto, truth, foot, _ll(S, *tee), _ll(S, *aim), ctx)
    off = [o for o in m["edge_off_yd"] if abs(o) <= TEB.MATCH_YD]
    assert 2.5 < float(np.median(off)) < 4.0                     # 3 m short = 3.3 yds
    crowns = sorted(m["crowns"], key=lambda c: c["cover"])
    assert crowns[0]["cover"] == 0.0 and 200 < crowns[0]["area_yd2"] < 280      # pi 8^2 m2 = 240 yd2
    assert crowns[1]["cover"] > 0.5
    assert m["extra_yd2"] == 0
    assert m["missing_by_data"]["lidar over threshold"] == m["missing_yd2"] or \
        abs(m["missing_by_data"]["lidar over threshold"] - m["missing_yd2"]) <= 2
    S2 = TEB.summarise([dict(slug="x", lidar_year=2015, naip_years=[2021, 2023], meta_chm=False, holes={"1": m})])
    assert S2["crowns"]["missed"] == 1 and S2["edge_by_lidar_age"]["6+ yrs"]["median"] > 2.5


def test_auto_past_the_crown_is_negative():
    S, x0, y0 = _grid()
    tee, aim = (x0 + 200, y0 + 10), (x0 + 200, y0 + 390)
    c1 = (x0 + 225, y0 + 210)
    z = np.zeros((S.H, S.W), np.float32)
    m = TEB.measure_hole(S, {"OSM wood / tree row": [_circle(S, *c1, 12.0)]}, _circle(S, *c1, 9.0),
                         _circle(S, x0 + 200, y0 + 200, 190.0), _ll(S, *tee), _ll(S, *aim),
                         dict(hm=z, chm=z, ndvi=z, thr=2.5))
    off = [o for o in m["edge_off_yd"] if abs(o) <= TEB.MATCH_YD]
    assert -4.0 < float(np.median(off)) < -2.5
