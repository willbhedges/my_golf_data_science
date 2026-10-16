"""Synthetic-geometry tests for place_tee (pytest course_data/tees)."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from place_tee import Frame, LineOfPlay, haversine_yd, place_tee, place_tee_sets  # noqa: E402

LAT0, LON0 = 40.76, -91.145
F = Frame(LAT0, LON0)


def ll(x, y):
    return F.inv(x, y)


def box(cx, cy, w=10, h=20, rot_deg=0.0, tid=None):
    """Rectangle tee (w across, h along the hole, in yards) centred at (cx, cy), rotated."""
    r = math.radians(rot_deg)
    out = []
    for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2), (-w / 2, -h / 2)]:
        out.append(ll(cx + dx * math.cos(r) - dy * math.sin(r), cy + dx * math.sin(r) + dy * math.cos(r)))
    return dict(id=tid, coords=out)


def straight_hole(length=400):
    """Hole due north: line from (0,0) to the green at (0, length)."""
    return [ll(0, 0), ll(0, length / 2), ll(0, length)]


def dist_from_green(res, green_xy):
    x, y = F.fwd(res["lat"], res["lon"])
    return math.hypot(x - green_xy[0], y - green_xy[1])


def test_frame_roundtrip_and_scale():
    lat, lon = ll(300, -200)
    x, y = F.fwd(lat, lon)
    assert abs(x - 300) < 1e-6 and abs(y + 200) < 1e-6
    assert abs(haversine_yd(ll(0, 0), ll(0, 400)) - 400) < 0.5
    assert abs(haversine_yd(ll(0, 0), ll(400, 0)) - 400) < 0.5


def test_picks_matching_box_among_three():
    line = straight_hole(400)
    tees = [box(0, -30, tid="back"), box(2, 0, tid="mid"), box(-3, 40, tid="fwd")]
    for want, yds in [("back", 430), ("mid", 400), ("fwd", 360)]:
        r = place_tee(line, tees, yds)
        assert r["tee_id"] == want, r
        assert r["method"] == "tee_centroid"
        assert abs(r["d_centroid"] - yds) < 1.0


def test_yardage_inside_box_extent_lands_on_the_box_axis():
    # one long box, 40 yds deep, centred 400 out; card says 412 -> 12 yds behind the centre
    line = straight_hole(400)
    r = place_tee(line, [box(0, 0, h=40, tid="long")], 412)
    assert r["tee_id"] == "long" and r["method"] == "tee_axis" and r["error_yd"] == 0
    assert abs(dist_from_green(r, (0, 400)) - 412) < 0.5
    x, y = F.fwd(r["lat"], r["lon"])
    assert abs(x) < 0.5 and abs(y + 12) < 0.5


def test_yardage_beyond_box_is_clamped_and_reports_error():
    line = straight_hole(400)
    r = place_tee(line, [box(0, 0, h=20, tid="only")], 420)   # box spans 390..410
    assert r["tee_id"] == "only" and abs(r["error_yd"] - 10) < 0.6
    assert abs(r["dist_yd"] - 410) < 0.6


def test_far_off_line_box_ignored_and_walkback_used():
    line = straight_hole(400)
    tees = [box(120, 0, tid="other_hole")]                     # 120 yds right of the line
    r = place_tee(line, tees, 400)
    assert r["method"] == "walkback" and r["tee_id"] is None
    assert abs(dist_from_green(r, (0, 400)) - 400) < 0.5


def test_walkback_extends_first_leg_behind_line_start():
    line = straight_hole(380)
    r = place_tee(line, [], 410)
    x, y = F.fwd(r["lat"], r["lon"])
    assert abs(x) < 0.5 and abs(y + 30) < 0.5


def test_walkback_on_dogleg_follows_line():
    # 250 north then 150 east (400 long): 300 from the green lands 100 up the first leg
    line = [ll(0, 0), ll(0, 250), ll(150, 250)]
    r = place_tee(line, [], 300)
    x, y = F.fwd(r["lat"], r["lon"])
    assert abs(x) < 0.5 and abs(y - 100) < 0.5


def test_dogleg_measures_through_turning_point():
    # tee box offset 15 yds left of the first leg; dist = |P - pivot| + 150
    line = [ll(0, 0), ll(0, 250), ll(150, 250)]
    yds = math.hypot(15, 250) + 150
    r = place_tee(line, [box(-15, 0, tid="left")], yds)
    assert r["tee_id"] == "left" and abs(r["d_centroid"] - yds) < 0.5


def test_tee_too_far_from_card_falls_back():
    line = straight_hole(400)
    r = place_tee(line, [box(0, 0, tid="t")], 470, max_err_yd=25)
    assert r["method"] == "walkback"
    assert r["candidates"][0]["tee_id"] == "t"


def test_point_tee_and_green_override():
    line = straight_hole(400)
    pt = dict(id="pt", coords=[ll(0, -10)])
    r = place_tee(line, [pt], 415, green=ll(0, 405))
    assert r["tee_id"] == "pt" and abs(r["d_centroid"] - 415) < 0.5


def test_rotated_hole_is_frame_independent():
    # same hole rotated 37 degrees: the tee chosen and distances must not change
    th = math.radians(37)
    rot = lambda x, y: (x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th))  # noqa
    line = [ll(*rot(0, 0)), ll(*rot(0, 400))]
    tees = [box(*rot(0, -25), rot_deg=37, tid="back"), box(*rot(0, 15), rot_deg=37, tid="fwd")]
    assert place_tee(line, tees, 425)["tee_id"] == "back"
    assert place_tee(line, tees, 385)["tee_id"] == "fwd"


def test_tee_sets_share_box():
    line = straight_hole(400)
    tees = [box(0, -20, h=30, tid="big"), box(0, 60, tid="red")]
    out = place_tee_sets(line, tees, {"Gold": 425, "Black": 410, "Red": 340})
    assert out["Gold"]["tee_id"] == out["Black"]["tee_id"] == "big"
    assert out["Gold"]["shared_with"] == ["Black"]
    assert out["Red"]["tee_id"] == "red" and out["Red"]["shared_with"] == []
    # Gold sits behind Black on the shared box
    assert out["Gold"]["dist_yd"] > out["Black"]["dist_yd"]


def test_line_of_play_distances():
    lop = LineOfPlay([(0, 0), (0, 200), (100, 200)])
    assert lop.length == pytest.approx(300)
    assert lop.dist_to_green((0, -50)) == pytest.approx(350)
    assert lop.point_at_distance(100) == pytest.approx((0, 200))


def test_assign_tees_to_holes_exclusive():
    from place_tee import assign_tees_to_holes
    # hole A runs north from (0,0); hole B runs north from (60,0): a box at x=50 belongs to B
    lines = {"A": [ll(0, 0), ll(0, 400)], "B": [ll(60, 0), ll(60, 350)]}
    tees = [box(0, -10, tid="a1"), box(50, -5, tid="b1"), box(300, 0, tid="nowhere")]
    got = assign_tees_to_holes(lines, tees)
    assert [t["id"] for t in got["A"]] == ["a1"]
    assert [t["id"] for t in got["B"]] == ["b1"]
