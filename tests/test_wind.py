"""Tests for spirit_hollow/wind.py (wind and temperature club adjustments)."""
import pytest

import wind

DRIVER = (275, 300, 65, 28)
TWO_WOOD = (265, 280, 60, 26)
FOUR_WOOD = (255, 270, 50, 24)
MID_IRON = (185, 192, 34, 18)


def test_zero_wind_identity():
    for rel in (0, 45, 90, 180, 270):
        c, t, w, d, drift = wind.adjust(DRIVER, 0, rel, "Driver")
        assert (c, t, w, d) == pytest.approx(DRIVER)
        assert drift == pytest.approx(0)


def test_zero_wind_with_gust_equal_speed_is_identity():
    assert wind.adjust(DRIVER, 0, 0, gust_mph=0)[:4] == pytest.approx(DRIVER)


def test_monotonic_in_speed():
    speeds = [0, 5, 10, 15, 20, 25, 30]
    head = [wind.adjust(DRIVER, s, 0, "Driver") for s in speeds]
    tail = [wind.adjust(DRIVER, s, 180, "Driver") for s in speeds]
    cross = [wind.adjust(DRIVER, s, 90, "Driver") for s in speeds]
    for a, b in zip(head, head[1:]):
        assert b[0] < a[0] and b[1] < a[1] and b[2] > a[2]
    for a, b in zip(tail, tail[1:]):
        assert b[0] > a[0] and b[1] > a[1] and b[2] <= a[2]
    for a, b in zip(cross, cross[1:]):
        assert b[4] < a[4]          # from the right -> further left


def test_head_vs_tail_asymmetry():
    for s in (5, 10, 20):
        c_h = wind.adjust(DRIVER, s, 0)[0]
        c_t = wind.adjust(DRIVER, s, 180)[0]
        loss, gain = 275 - c_h, c_t - 275
        assert loss > gain > 0
    # asymmetry grows with speed
    r10 = (275 - wind.adjust(DRIVER, 10, 0)[0]) / (wind.adjust(DRIVER, 10, 180)[0] - 275)
    r20 = (275 - wind.adjust(DRIVER, 20, 0)[0]) / (wind.adjust(DRIVER, 20, 180)[0] - 275)
    assert r20 > r10


def test_roll_shrinks_into_wind_grows_down_wind():
    c, t = wind.adjust(DRIVER, 10, 0)[:2]
    assert t - c < 25
    c, t = wind.adjust(DRIVER, 10, 180)[:2]
    assert t - c > 25


def test_crosswind_symmetry():
    r = wind.adjust(DRIVER, 12, 90, "Driver")
    l = wind.adjust(DRIVER, 12, 270, "Driver")
    assert r[:4] == pytest.approx(l[:4])
    assert r[4] == pytest.approx(-l[4])
    assert r[4] < 0                 # from the right pushes the ball left
    # pure crosswind leaves carry/total/width unchanged
    assert r[:3] == pytest.approx(DRIVER[:3])
    # quartering winds mirror too
    a = wind.adjust(DRIVER, 15, 45)
    b = wind.adjust(DRIVER, 15, 315)
    assert a[:4] == pytest.approx(b[:4]) and a[4] == pytest.approx(-b[4])


def test_sensible_magnitudes_driver():
    c, t, w, d, _ = wind.adjust(DRIVER, 10, 0, "Driver")
    assert 12 <= 275 - c <= 20          # published 12-18 yd; ours ~15
    assert 1.05 <= w / 65 <= 1.09       # Ping: +7% per 10 mph
    c = wind.adjust(DRIVER, 10, 180, "Driver")[0]
    assert 8 <= c - 275 <= 13           # published +9..+11
    c = wind.adjust(DRIVER, 20, 0, "Driver")[0]
    assert 28 <= 275 - c <= 42          # Golf.com tour example -13.7%
    drift = wind.adjust(DRIVER, 10, 90, "Driver")[4]
    assert -14 <= drift <= -8
    drift_iron = wind.adjust(MID_IRON, 10, 90, "Mid iron")[4]
    assert -9 <= drift_iron <= -4       # Hole19: ~5 yd per 10 mph mid-iron


def test_woods_ordering_preserved():
    adj = wind.adjust_clubs({"Driver": DRIVER, "2-wood": TWO_WOOD, "4-wood": FOUR_WOOD}, 15, 0)
    assert adj["Driver"][0] > adj["2-wood"][0] > adj["4-wood"][0]


def test_gusts_widen_only():
    base = wind.adjust(DRIVER, 10, 45)
    g = wind.adjust(DRIVER, 10, 45, gust_mph=22)
    assert g[0] == pytest.approx(base[0]) and g[4] == pytest.approx(base[4])
    assert g[2] > base[2] and g[3] > base[3]


def test_exposure_scales_speed():
    assert wind.adjust(DRIVER, 20, 0, exposure=0.5) == pytest.approx(wind.adjust(DRIVER, 10, 0))


def test_hole_relative():
    assert wind.hole_relative(180, 180) == 0          # wind from S, playing S: into
    assert wind.hole_relative(180, 0) == 180          # playing N: downwind
    assert wind.hole_relative(180, 90) == 90          # playing E: from the right
    assert wind.hole_relative(180, 270) == 270        # playing W: from the left
    assert wind.hole_relative(10, 350) == pytest.approx(20)


def test_temperature():
    assert wind.temperature_adjust(DRIVER, 70) == pytest.approx(DRIVER)
    c = wind.temperature_adjust(DRIVER, 50)[0]
    assert 3 <= 275 - c <= 5             # ~2 yd per 10 F
    assert wind.temperature_adjust(DRIVER, 50)[2:] == DRIVER[2:]
