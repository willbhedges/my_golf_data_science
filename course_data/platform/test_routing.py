"""Offline tests for routing.py on a synthetic 18-hole course (no network, no rasters)."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import routing as R  # noqa: E402

LON0, LAT0 = -93.0, 42.0
PR = R.Proj(LON0, LAT0)
PARS = [4, 4, 3, 5, 4, 4, 3, 4, 5, 4, 3, 4, 5, 4, 4, 3, 4, 5]
YDS = {3: 165, 4: 390, 5: 520}


def _ll(x, y):
    lo, la = PR.inv(x, y)
    return [float(lo), float(la)]


def _box(cx, cy, ang, half_len=12, half_w=5):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(-half_len, -half_w), (half_len, -half_w), (half_len, half_w), (-half_len, half_w), (-half_len, -half_w)]
    return [_ll(cx + c * u - s * v, cy + s * u + c * v) for u, v in pts]


def synthetic(seed=1):
    """Two 9-hole loops from a clubhouse at (0, 0): holes zig-zag outwards; 3 tee boxes per hole (card sets at
    100 / 92 / 82 % of the back yardage), round greens, a practice green by the clubhouse, a car park."""
    rnd = random.Random(seed)
    feats, truth = [], {}
    x, y, heading = 30.0, 0.0, 0.0
    yards = {"Back": [], "Middle": [], "Front": []}
    for i, par in enumerate(PARS):
        if i == 9:
            x, y, heading = -30.0, 0.0, math.pi
        L = YDS[par] + rnd.randint(-25, 25)
        heading += rnd.uniform(-1.0, 1.0) if i not in (0, 9) else 0.0
        if i in (4, 13):                                   # turn back towards the clubhouse
            heading = math.atan2(-y, -x) + rnd.uniform(-0.4, 0.4)
        tx, ty = x, y
        gx, gy = tx + L * math.cos(heading), ty + L * math.sin(heading)
        for frac, name in ((1.0, "Back"), (0.92, "Middle"), (0.82, "Front")):
            d = L * (1 - frac)
            bx, by = tx + d * math.cos(heading), ty + d * math.sin(heading)
            feats.append(dict(type="Feature", properties=dict(golf="tee", osm_id=1000 + 10 * i + len(yards[name]) % 9),
                              geometry=dict(type="Polygon", coordinates=[_box(bx, by, heading)])))
            yards[name].append(int(round(math.hypot(gx - bx, gy - by))))
        ring = [_ll(gx + 14 * math.cos(a / 8 * math.pi), gy + 14 * math.sin(a / 8 * math.pi)) for a in range(17)]
        feats.append(dict(type="Feature", properties=dict(golf="green", osm_id=2000 + i),
                          geometry=dict(type="Polygon", coordinates=[ring])))
        feats.append(dict(type="Feature", properties=dict(golf="hole", ref=str(i + 1), par=str(par), osm_id=3000 + i),
                          geometry=dict(type="LineString", coordinates=[_ll(tx, ty), _ll(gx, gy)])))
        truth[str(i + 1)] = (tx, ty, gx, gy)
        # next tee 40-70 yds beyond the green, sideways
        side = heading + rnd.choice([-1, 1]) * math.pi / 2
        x, y = gx + rnd.uniform(40, 70) * math.cos(side), gy + rnd.uniform(40, 70) * math.sin(side)
    ring = [_ll(14 * math.cos(a / 8 * math.pi), 60 + 14 * math.sin(a / 8 * math.pi)) for a in range(17)]
    feats.append(dict(type="Feature", properties=dict(golf="green", osm_id=2999), geometry=dict(type="Polygon", coordinates=[ring])))
    feats.append(dict(type="Feature", properties=dict(amenity="parking", osm_id=4000),
                      geometry=dict(type="Point", coordinates=_ll(0, -20))))
    feats.append(dict(type="Feature", properties=dict(golf="clubhouse", osm_id=4001),
                      geometry=dict(type="Point", coordinates=_ll(0, 0))))
    card = dict(par=PARS, tee_sets={k: dict(yards=v) for k, v in yards.items()})
    return dict(type="FeatureCollection", features=feats), card, truth


def test_card_holes():
    n, pars, yards = R.card_holes(dict(par=[4, 3], tee_sets={"A": dict(yards=[400, 150]), "B": dict(yards=[380, 140])}))
    assert n == 2 and pars == [4, 3] and yards == [[380, 400], [140, 150]]
    assert R.card_holes(None) == (None, None, None)


def test_route_recovers_synthetic_course():
    fc, card, truth = synthetic()
    inp = R.inputs_from_fc(fc, hide_holes=True)
    assert len(inp["greens"]) == 19 and len(inp["tees"]) == 54 and inp["clubhouse"]
    res = R.route(inp, card)
    sc = R.score(res, R.truth_from_fc(fc))
    assert sc["green_assign_acc"] >= 0.94, sc
    assert sc["hole_number_acc"] >= 0.89, sc
    assert res["n_holes"] == 18
    assert "osm:way/2999" in res["unused_greens"]                 # the practice green stays unused


def test_anchors_pin_mapped_holes():
    fc, card, truth = synthetic(seed=3)
    inp = R.inputs_from_fc(fc)                                   # hole ways visible -> anchors
    res = R.route(inp, card)
    assert all(h["anchored"] for h in res["holes"].values())
    assert R.score(res, R.truth_from_fc(fc))["green_assign_acc"] == 1.0


def test_to_hole_features_adds_lines():
    fc, card, _ = synthetic(seed=2)
    fc0 = dict(fc, features=[f for f in fc["features"] if f["properties"].get("golf") != "hole"])
    inp = R.inputs_from_fc(fc0)
    res = R.route(inp, card)
    fc2 = R.to_hole_features(res, fc0, inp)
    lines = [f for f in fc2["features"] if f["properties"].get("golf") == "hole"]
    assert len(lines) == sum(1 for h in res["holes"].values() if h.get("tee_ll") and h.get("green_ll"))
    assert all(f["properties"]["source"] == "routing" for f in lines)


def test_crossings():
    import numpy as np
    a = np.array([[0, 0], [0, 30], [100, 100]], float)
    b = np.array([[100, 100], [100, 30], [200, 200]], float)
    x = R._crossings(a, b)
    assert x[0, 1] == 1 and x[1, 0] == 1 and x[0, 2] == 0     # touching at an end is not a crossing
