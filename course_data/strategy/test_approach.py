"""Tests for course_data/strategy/approach.py (python3 -m pytest course_data/strategy/test_approach.py)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from course_data.strategy import approach as A      # noqa: E402

GREEN_C = np.array([0.0, -400.0])


def circle(c, r, k=48):
    a = np.linspace(0, 2 * np.pi, k, endpoint=False)
    return np.c_[c[0] + r * np.cos(a), c[1] + r * np.sin(a)].tolist()


def rect(x0, x1, y0, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def synth(extra=(), profile=None, green_elev=None, r=14.0, par=4):
    zones = [("fairway", rect(-18, 18, -385, -150))] + list(extra)
    return A.Hole(zones, circle(GREEN_C, r), 0.0, profile, green_elev, key="T", par=par)


START = np.array([0.0, -250.0])             # 150 yds short of the green centre, on the fairway


def test_tables_monotone():
    ft = np.array([2, 5, 10, 20, 40, 80])
    assert np.all(np.diff(A.putts(ft)) > 0)
    for lie in ("fairway", "rough", "sand"):
        d = np.array([5, 20, 60, 120, 200])
        assert np.all(np.diff(A.baseline(lie, d)) > 0)
    assert A.baseline("rough", 150) > A.baseline("fairway", 150)
    assert A.baseline("fairway", 150, hcp=True) > A.baseline("fairway", 150)


def test_bag_gapping_and_tee_consistency():
    tots = [A.BAG[c][0][1] for c in A.BAG]
    assert tots == sorted(tots, reverse=True)
    assert A.BAG["4-iron"][0] == A.t.IRONS["Long iron"][:2] == (210, 220)
    assert A.BAG["6-iron"][0] == A.t.IRONS["Mid iron"][:2]
    assert A.BAG["2-wood"][0] == A.t.CLUBS["2-wood"][:2]
    # every yardage 5..270 calm from the fairway has a club
    for d in range(5, 266, 3):
        assert A.club_for(float(d), "fairway", A.CALM, 0.0) is not None, d
    assert A.club_for(300.0, "fairway", A.CALM, 0.0) is None
    assert A.club_for(250.0, "rough", A.CALM, 0.0) is None


def test_open_green_aims_near_centre():
    h = synth()
    r = A.solve(h, START, "fairway", n=600)
    assert r["best"]["club"] in ("9-iron", "8-iron")
    assert abs(r["best"]["vs_centre_right"]) <= 4.0
    assert r["best"]["ev"] <= r["centre"]["ev"] + 1e-9


def test_water_right_moves_aim_left_and_costs_less_than_centre():
    water = ("water", rect(14, 60, -440, -360))
    h = synth([water])
    r = A.solve(h, START, "fairway", n=600)
    assert r["best"]["vs_centre_right"] <= -2.0
    assert r["best"]["ev"] < r["centre"]["ev"]
    assert r["best"]["p_water"] < r["centre"]["p_water"]


def test_ob_long_moves_aim_short():
    ob = ("ob", rect(-80, 80, -480, -412))
    h = synth([ob])
    r = A.solve(h, START, "fairway", n=600)
    assert r["best"]["vs_centre_long"] < -1.0
    assert r["best"]["p_ob"] <= r["centre"]["p_ob"]


def test_tucked_pin_behind_bunker_aims_inside_flag():
    bunker = ("sand", rect(-40, -13, -415, -385))
    h = synth([bunker])
    pin = GREEN_C + np.array([-10.0, 0.0])          # left pin, 4 yds from the edge, bunker short-side
    r = A.solve(h, START, "fairway", pin=pin, n=800)
    assert r["best"]["target"][0] > pin[0] + 1.0       # aim right of (inside) the flag
    assert r["best"]["ev"] <= r["flag"]["ev"]


def test_short_side_costs_more():
    h = synth()
    pin = GREEN_C + np.array([-10.0, 0.0])
    S = A.value_map(h, pin[None, :])
    left = S[h.idx(np.array([-17.0, -400.0]))]          # 3 yds off the edge, beside the pin
    right = S[h.idx(np.array([17.0, -400.0]))]          # 3 yds off the far edge (lots of green)
    # far side is 27 yds from the pin, short side 7: short-side costs despite being much closer
    assert left > A.baseline("rough", 7.0)
    assert right == pytest.approx(float(A.baseline("rough", 27.0)), abs=1e-6)


def test_elevation_plays_longer_uphill():
    up = synth(profile=[(0, 0.0), (250, 0.0), (400, 30.0)])
    d, d_eff = A.plays_like(up, START, GREEN_C)
    assert d == pytest.approx(150.0)
    assert d_eff == pytest.approx(150 + 30 * A.FT / np.tan(np.radians(50)) / A.YD, abs=0.5)
    r = A.solve(up, START, "fairway", n=300)
    assert r["centre"]["plays_like"] > 155


def test_wind_and_temperature_change_the_club():
    h = synth()
    calm = A.solve(h, START, "fairway", n=300)["centre"]["club"]
    head = A.solve(h, START, "fairway", n=300, cond=A.Conditions(15, 0.0))["centre"]  # hole plays north (0)
    cold = A.solve(h, START, "fairway", n=300, cond=A.Conditions(0, 0, temp_f=35))["centre"]
    order = list(A.BAG)
    assert order.index(head["club"]) < order.index(calm)
    assert order.index(cold["club"]) <= order.index(calm)
    # wind from the right pushes the ball left: aim off to the right (+)
    cross = A.solve(h, START, "fairway", n=300, cond=A.Conditions(15, 90.0))["centre"]
    assert cross["aim_off_drift"] > 2.0


def test_out_of_reach_lays_up_or_goes_short():
    h = synth(par=5)
    r = A.solve(h, np.array([0.0, -110.0]), "fairway", n=300)    # 290 yds: green out of reach
    assert r["best"] is not None and np.isfinite(r["best"]["ev"])
    assert r["centre"] is None
    assert r["best"]["dist"] <= A.REACH["fairway"] + A.CLUB_HIGH


def test_rough_worse_than_fairway():
    h = synth()
    f = A.solve(h, START, "fairway", n=400)["best"]["ev"]
    r = A.solve(h, START, "rough", n=400)["best"]["ev"]
    assert r > f


def test_proximity_matches_calibration():
    """Mean proximity on a huge green ~ the 5-hcp anchors the pattern was fitted to (~45 ft from 150)."""
    big = A.Hole([], circle(GREEN_C, 90), 0.0, key="B")
    z = A.z_draws(4000, 1)
    d = 150.0
    sl, sd = A.sigma(d)
    along, lat = d + sd * z[1], sl * z[0]
    ft = np.hypot(along - d, lat).mean() * 3
    assert 35 < ft < 55


def test_value_grid_penalties():
    h = synth()
    vg = A.ValueGrid(h, np.arange(-40, 41, 20.0), np.arange(-280, -219, 20.0), n=150)
    p = np.array([[0.0, -250.0]] * 3)
    v = vg.value(p, ["fairway", "water", "ob"])
    assert v[1] == pytest.approx(1 + vg.value(p[:1], ["rough"])[0])
    assert v[2] == pytest.approx(v[1] + 1)
    assert v[0] < v[1]


PKG = os.path.join(A.PACKAGES, "blue_hills", "package.json")


@pytest.mark.skipif(not os.path.exists(PKG), reason="blue_hills package not checked out")
def test_package_hole_solves():
    h = A.Hole.from_package("blue_hills", "4")
    assert (h.lie == A.CODE["green"]).sum() > 200
    start = h.green_c + np.array([0.0, 140.0])
    r = A.solve(h, start, "fairway", n=300)
    assert r["best"]["ev"] <= r["centre"]["ev"] + 1e-9
    assert 2.5 < r["best"]["ev"] < 4.5
