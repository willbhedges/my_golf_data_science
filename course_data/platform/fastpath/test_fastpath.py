"""Fast path: the extra publish gate and the lie raster."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast
import solve


def hole(green, card, meas):
    return dict(green_ll=green, yards={"Blue": card}, tees={"Blue": dict(measured_yards=meas)})


def test_gate_blocks_a_shared_green_and_a_card_that_does_not_fit():
    ok = {str(i + 1): hole([-100 + i * 0.005, 40.0], 400, 398) for i in range(18)}
    assert fast.extra_gate(dict(tee_set="Blue", holes=ok)) == []
    dup = dict(ok, **{"12": hole([-100.00002, 40.0], 395, 395)})
    assert any("1 and 12 share a green" in r for r in fast.extra_gate(dict(tee_set="Blue", holes=dup)))
    one = dict(ok, **{"5": hole(ok["5"]["green_ll"], 350, 265)})          # one card error: shown, flagged elsewhere
    assert fast.extra_gate(dict(tee_set="Blue", holes=one)) == []
    three = dict(ok, **{k: hole(ok[k]["green_ll"], 400, 300) for k in ("9", "10", "11")})
    assert any("does not fit the map on 3 holes" in r for r in fast.extra_gate(dict(tee_set="Blue", holes=three)))


def test_lie_raster_matches_the_polygon_order():
    h = dict(zones=[("fairway", [(0, 0), (100, 0), (100, 300), (0, 300)]), ("water", [(40, 100), (60, 100), (60, 140), (40, 140)])])
    pts = np.array([[50, 50], [50, 120], [150, 50], [-5, 10], [99, 299]], float)
    assert list(solve.raster_lie_at(h, pts)) == ["fairway", "water", "rough", "rough", "fairway"]
