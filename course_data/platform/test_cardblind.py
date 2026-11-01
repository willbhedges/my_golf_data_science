"""card:none helpers in package.py (offline, synthetic OSM)."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import package as P  # noqa: E402

LAT0, LON0 = 39.0, -95.0
D = 0.9144 / 111320


def ll(x, y):
    return [LON0 + x * D / math.cos(math.radians(LAT0)), LAT0 + y * D]


def fc_two_holes():
    f = []
    for r, x0 in (("1", 0), ("2", 200)):
        f.append(dict(type="Feature", properties=dict(golf="hole", ref=r, par="4" if r == "1" else ""),
                      geometry=dict(type="LineString", coordinates=[ll(x0, 0), ll(x0, 400 if r == "1" else 180)])))
        gy = 400 if r == "1" else 180
        f.append(dict(type="Feature", properties=dict(golf="green", osm_id=int(r)),
                      geometry=dict(type="Polygon", coordinates=[[ll(x0 - 10, gy - 5), ll(x0 + 10, gy - 5),
                                                                  ll(x0 + 10, gy + 15), ll(x0 - 10, gy + 15),
                                                                  ll(x0 - 10, gy - 5)]])))
        f.append(dict(type="Feature", properties=dict(golf="tee", osm_id=10 + int(r)),
                      geometry=dict(type="Polygon", coordinates=[[ll(x0 - 4, -6), ll(x0 + 4, -6), ll(x0 + 4, 6),
                                                                  ll(x0 - 4, 6), ll(x0 - 4, -6)]])))
    return dict(type="FeatureCollection", features=f)


def test_strip_card_inputs():
    req = dict(course="X", card="none", yardages=[400], tees="Black", par_overrides={"1": 5}, scorecard="a.json")
    assert P.card_blind(req) and not P.card_blind(dict(course="X"))
    out = P.strip_card_inputs(req)
    assert not any(k in out for k in ("yardages", "tees", "par_overrides", "scorecard")) and out["local_scorecard"] is False


def test_fallback_card():
    c = P.cardless_fallback(fc_two_holes())
    assert c["tee_sets"]["Back"]["yards"][:2] == [400, 180]
    assert c["par"][:2] == [4, 3]                       # OSM tag, then par from length
    assert c["tee_sets"]["Second"]["yards"][0] == round(400 * P.CARDLESS_SET2_RATIO)


def test_cardless_inputs_green_centre():
    holes, boxes, pads = P.cardless_inputs(fc_two_holes(), pads=[dict(id="lidar:1", coords=[(1, 2), (1, 3), (2, 3)])])
    assert [h["ref"] for h in holes] == [1, 2] and len(boxes) == 2 and pads[0]["source"] == "lidar"
    g = holes[0]["green"]                                # (lat, lon) centroid, 5 yds beyond the line end
    assert abs((g[0] - LAT0) / D - 405) < 0.5 and abs(holes[0]["green_r_yd"] - math.sqrt(400 / math.pi)) < 0.1
    assert holes[0]["line"][0] == (LAT0, LON0)


def test_cardless_infer_shape():
    card, info = P.cardless_infer(fc_two_holes(), {}, "/nonexistent", "x")
    if card is None:                                     # tees/cardless.py absent: the reason is a string
        assert isinstance(info, str)
        return
    assert card["tee_sets"] and all(len(s["yards"]) == 9 for s in card["tee_sets"].values())
    assert info["kind"] == "cardless"
