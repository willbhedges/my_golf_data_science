"""Tests for course_data/elevation/adjust.py (ballistics, roll, side kick) and the per-hole JSON."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adjust as A  # noqa: E402

TEE_KEYS = ["1", "2B", "2F", "4", "5", "6", "8", "9B", "9F", "10", "11", "13", "14", "16", "17", "18"]
PAR3_KEYS = ["7", "12", "15"]


def test_model_matches_trackman_driver():
    # TrackMan PGA Tour average driver: 167 mph, 10.9 deg, 2686 rpm -> 275 carry, 38 deg landing
    carry, ang = A.fly(167 * 0.44704, 10.9, 2686)
    assert carry == pytest.approx(275, abs=3)
    assert ang == pytest.approx(38, abs=1.5)


def test_fairway_woods_land_steeper():
    # 3-wood 158 mph / 9.2 / 3655 -> 243 yds, 43 deg; 5-wood 152 / 9.4 / 4350 -> 230 yds, 47 deg
    c3, a3 = A.fly(158 * 0.44704, 9.2, 3655)
    c5, a5 = A.fly(152 * 0.44704, 9.4, 4350)
    assert c3 == pytest.approx(243, abs=6) and c5 == pytest.approx(230, abs=6)
    assert A.descent_angle("Driver") < A.descent_angle("2-wood") < A.descent_angle("4-wood")


@pytest.mark.parametrize("club", ["Driver", "2-wood", "4-wood"])
def test_flat_carry_calibrated(club):
    assert A.carry_on_profile(club, None)[0] == pytest.approx(A.CLUBS[club]["carry"], abs=0.5)


def test_downhill_gains_uphill_loses_asymmetric():
    down = A.carry_delta_for_drop("Driver", 30)
    up = A.carry_delta_for_drop("Driver", -30)
    assert down > 0 > up
    assert abs(up) > down                     # uphill costs more than downhill gives
    # ~ dh / tan(descent): 30 ft at 38 deg -> ~12.8 yds; integration a bit less (ball steepens)
    assert 9 < down < 14


def test_rate_near_one_yard_per_2_to_3_feet():
    per_ft = A.carry_delta_for_drop("Driver", 10) / 10
    assert 0.33 < per_ft < 0.5               # 1 yd per 2-3 ft for a driver
    assert A.carry_delta_for_drop("4-wood", 10) < A.carry_delta_for_drop("Driver", 10)


def test_roll_factor_slope_direction():
    assert A.roll_factor(0.0) == pytest.approx(1.0)
    assert A.roll_factor(5.0) < 0.8           # upslope kills roll
    assert A.roll_factor(-5.0) > 1.3          # downslope adds it
    assert A.roll_factor(-40.0) == 3.0 and A.roll_factor(80.0) >= 0.25


def test_lateral_kick_toward_low_side():
    assert A.lateral_kick(25, 0, 5) < 0       # ground rises to the right -> kicks left
    assert A.lateral_kick(25, 0, -5) > 0
    assert A.lateral_kick(25, 0, 0) == 0
    assert abs(A.lateral_kick(25, 0, 50)) <= 0.6 * 25


def synthetic(drop_ft, along, cross):
    prof = [dict(yd=y, band_ft_rel_tee=-drop_ft * min(y, 200) / 200.0) for y in range(0, 401, 10)]
    return {"X": dict(par=4, bearing_deg_true=0.0, profile=prof,
                      landing={"270": dict(delta_ft=-drop_ft)},
                      landing_slope=dict(along_pct=along, cross_pct=cross, magnitude_pct=math.hypot(along, cross),
                                         fall_line_deg_cw_from_line=0.0))}


def test_adjustments_synthetic():
    flat = A.adjustments("X", synthetic(0, 0, 0))
    assert flat["clubs"]["Driver"]["carry_delta_yds"] == pytest.approx(0, abs=0.6)
    assert flat["roll_factor"] == pytest.approx(1.0) and flat["extra_roll_yds"] == pytest.approx(0)
    down = A.adjustments("X", synthetic(40, -4, 3))
    d = down["clubs"]["Driver"]
    assert d["carry_delta_yds"] > 10 and d["roll_factor"] > 1 and d["lateral_kick_yds"] < 0
    t = A.apply_to_club((275, 300, 65, 28), d)
    assert t[0] > 275 and t[1] - t[0] > 25 and t[2:] == (65, 28)


@pytest.mark.parametrize("k", TEE_KEYS)
def test_every_tee_hole_has_adjustments(k):
    a = A.adjustments(k)
    assert set(a["clubs"]) >= {"Driver", "2-wood", "4-wood"}
    for c in a["clubs"].values():
        assert -40 < c["carry_delta_yds"] < 40
        assert 0.25 <= c["roll_factor"] <= 3.0
    # sign consistency: a lower landing area gains carry
    drop = -a["landing_270_delta_ft"]
    if abs(drop) > 8:
        assert math.copysign(1, a["clubs"]["Driver"]["carry_delta_yds"]) == math.copysign(1, drop)


@pytest.mark.parametrize("k", PAR3_KEYS)
def test_par3(k):
    a = A.adjustments(k)
    assert a["par"] == 3 and "green_drop_ft" in a and abs(a["plays_like_delta_yds"]) < 15


def test_holes_json_complete():
    H = A._holes()
    assert set(TEE_KEYS + PAR3_KEYS) <= set(H)
    for k in TEE_KEYS:
        h = H[k]
        assert 0 <= h["bearing_deg_true"] < 360
        assert {"240", "270", "300"} <= set(h["landing"])
        assert h["profile"][0]["yd"] == 0 and h["profile"][0]["ft_rel_tee"] == pytest.approx(0, abs=3)
        assert all(b["yd"] - a["yd"] == 10 for a, b in zip(h["profile"], h["profile"][1:]))
        assert 500 < h["tee_elev"]["ft"] < 700           # Burlington IA, ~550-690 ft
