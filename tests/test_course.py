"""spirit_hollow/course.py data integrity and yardage_book.use_course."""
import numpy as np
import pytest
from matplotlib.path import Path

import course as course_mod
import tee_strategy as tmod

SH = list(course_mod.HOLES)


def test_order_covers_holes(course):
    for h in course.ORDER:
        assert (h in course.HOLES) != (h in course.PAR3), h
    assert set(course.ORDER) == set(course.HOLES) | set(course.PAR3)
    assert len(course.ORDER) == len(set(course.ORDER))


def test_notes_and_aim_at(course):
    for h in course.HOLES:
        assert course.NOTES.get(h), h
        assert course.AIM_AT.get(h), h


def test_par3_entries_complete(course):
    for h, p in course.PAR3.items():
        assert set(p["haz"]) == {"left", "right", "short", "long"}
        assert p["front"] < p["center"] < p["back"]
        assert len(p["green"]) >= 3
        assert p["short"] and p["note"]


def test_app_tables_cover_holes(course):
    assert set(course.APP) == set(course.HOLES) == set(course.GREEN_SIDE)
    for k, (a, b, c) in course.APP.items():
        assert a < b < c, k


def test_zone_names_known(course, t):
    known = {"fairway", "rough", *t.HAZARDS}
    for h, hd in course.HOLES.items():
        for name, poly in hd["zones"]:
            assert name in known, (h, name)
            assert len(poly) >= 3


# hole 11's green is deliberately left on the line (see GREEN_SIDE); tested separately below
@pytest.mark.parametrize("hole", [h for h in SH if h != 11])
def test_green_reproduces_app_numbers(t, course, hole):
    hd = course.HOLES[hole]
    tee, fwd, right, ppy = t.hole_frame(hd)
    g = np.array(hd["green"], float)
    for along, app in zip((300, 270, 240), course.APP[hole]):
        d = np.linalg.norm(g - (tee + along * fwd * ppy)) / ppy
        assert d == pytest.approx(app, abs=1.5), (hole, along, d, app)


def test_hole11_on_the_line(t, course):
    hd = course.HOLES[11]
    tee, fwd, right, ppy = t.hole_frame(hd)
    rel = (np.array(hd["green"]) - tee) / ppy
    assert rel @ right == pytest.approx(0.0, abs=1e-6)
    assert rel @ fwd == pytest.approx(270 + course.APP[11][1])


@pytest.mark.parametrize("hole", SH)
def test_green_side_and_length(t, course, hole):
    hd = course.HOLES[hole]
    tee, fwd, right, ppy = t.hole_frame(hd)
    lat = (np.array(hd["green"]) - tee) @ right / ppy
    side = course.GREEN_SIDE[hole]
    if side == 0:
        assert lat == pytest.approx(0.0, abs=1e-6)
    else:
        assert np.sign(lat) == side or abs(lat) < 1e-6
    assert hd["length"] == 270 + course.APP[hole][1]


def test_green_from_app_roundtrip(course):
    # put a green at (along, lat), measure from the three dots, trilaterate back
    for along, lat in [(380, -20), (420, 15), (500, 0.0), (330, 40)]:
        d = [np.hypot(along - a, lat) for a in (300, 270, 240)]
        a2, l2 = course.green_from_app(*d, np.sign(lat) if lat else 1)
        assert a2 == pytest.approx(along) and l2 == pytest.approx(lat, abs=1e-6)


@pytest.mark.parametrize("hole", SH)
def test_tee_not_in_hazard(t, course, hole):
    hd = course.HOLES[hole]
    for name, poly in hd["zones"]:
        if name in t.HAZARDS:
            assert not Path(poly).contains_point(hd["tee"]), (hole, name)
    assert t.lie_at(hd, np.array([hd["tee"]], float))[0] not in t.HAZARDS


@pytest.mark.parametrize("hole", list(tmod.HOLES))
def test_mozingo_tee_not_in_hazard(t, hole):
    hd = t.HOLES[hole]
    assert t.lie_at(hd, np.array([hd["tee"]], float))[0] not in t.HAZARDS


def test_aim_bounds_set(course):
    for h, hd in course.HOLES.items():
        assert hd["aim_min"] < 0 < hd["aim_max"], h


def test_par3_flag_is_green_centroid(course):
    for h, p in course.PAR3.items():
        g = np.array(p["green"])
        np.testing.assert_allclose(g.mean(axis=0), 0.0, atol=1e-6)
        tee, flag = np.array(p["tee"]), np.array(p["flag"])
        assert flag[1] < tee[1]          # flag is up the screen from the tee


# ---------------------------------------------------------------- use_course
def test_use_course_swaps_globals(yb, t, course):
    assert yb.label("9B") == "9B"            # Mozingo has no such labels
    moz_holes = t.HOLES
    yb.use_course("Spirit Hollow GC", "/x", "Spirit_Hollow", course.HOLES, course.PAR3,
                  course.NOTES, course.AIM_AT, course.ORDER, course.LABELS)
    assert yb.label("9B") == "9 back tee"
    assert yb.label("2F") == "2 forward tee"
    assert yb.label(7) == "7"
    assert yb.NAME == "Spirit Hollow GC" and yb.DIR == "/x" and yb.PREFIX == "Spirit_Hollow"
    assert yb.STRATEGY_NAME == "Spirit_Hollow_Strategy.pdf"
    assert yb.ORDER is course.ORDER
    assert yb.PAR3 is course.PAR3 and yb.NOTES is course.NOTES and yb.AIM_AT is course.AIM_AT
    assert t.HOLES is course.HOLES and t.HOLES is not moz_holes
    assert yb.tee_plan.cache_info().currsize == 0
    # clubs_for reads the swapped holes (Spirit Hollow 11 and 13 offer irons)
    assert "Long iron" in t.clubs_for(13)


def test_use_course_labels_default_empty(yb, course):
    yb.use_course("X", "/x", "X", course.HOLES, course.PAR3, course.NOTES, course.AIM_AT,
                  course.ORDER)
    assert yb.LABELS == {} and yb.label("9B") == "9B"


def test_build_setup(yb, t, course):
    import build
    build.setup()
    assert yb.label("9B") == "9 back tee"
    assert t.HOLES is course.HOLES
    assert yb.NAME == "Spirit Hollow GC"


def test_use_course_clears_tee_plan_cache(yb, t, course, monkeypatch):
    calls = []
    # seed the cache with a cheap fake entry, then check use_course empties it
    monkeypatch.setattr(t, "best_aim", lambda h, c, aims=None, z=None: calls.append((h, c)) or
                        dict(ev=float(len(c)), aim=0.0))
    monkeypatch.setattr(t, "simulate", lambda h, c, a, **k: (None, None, None, np.array([abs(a)])))
    yb.tee_plan(1)
    assert yb.tee_plan.cache_info().currsize == 1
    yb.use_course("Spirit Hollow GC", "/x", "Spirit_Hollow", course.HOLES, course.PAR3,
                  course.NOTES, course.AIM_AT, course.ORDER, course.LABELS)
    assert yb.tee_plan.cache_info().currsize == 0


def test_par3_summary(yb):
    p = yb.PAR3[15]
    plan = yb.par3_plan(p)
    play, d0, d1 = yb.par3_summary(p, plan)
    assert play == pytest.approx(p["center"] + plan["aim"][1])
    assert d0 <= play <= d1 + 1e-9


def test_side_strings(yb):
    assert yb.side(0) == "on the app line"
    assert yb.side(1.2) == "on the app line"
    assert yb.side(5) == "5 yds right" and yb.side(-7.5) == "8 yds left"
