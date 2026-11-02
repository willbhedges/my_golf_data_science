"""library/v2_adaptive.py: the adaptive aim bound around spirit_hollow/v2's robust_aim (synthetic curves).
python3 -m pytest -q course_data/library/test_v2_adaptive.py"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2_adaptive as A  # noqa: E402


def base(aims, curve, lo=-40.0, hi=40.0):
    """spirit_hollow/v2 robust_aim's contract on a grid: argmin inside [lo, hi], at_bound within 1 yd."""
    m = (aims >= lo - 1e-9) & (aims <= hi + 1e-9)
    i = int(np.argmin(np.where(m, curve, np.inf)))
    a = float(aims[i])
    return dict(aim=a, ev=float(curve[i]), ev_smooth=float(curve[i]), window=[a, a],
                at_bound=bool(a <= lo + 1 or a >= hi - 1), window_width=0.0)


@pytest.fixture
def ra(monkeypatch):
    monkeypatch.setattr(A, "_play_line_yds", lambda hd: hd.get("line"))
    ok = {"fn": lambda a: True}
    monkeypatch.setattr(A, "aim_ok", lambda M, R, hd, a, line=None: ok["fn"](a))
    A.CTX.clear()
    A.CTX.update(hd={"line": np.array([[0.0, 0.0], [400.0, 60.0]])}, R=None)
    return A.adaptive_robust_aim(base, None, 40.0), ok


def test_widens_where_the_curve_still_falls(ra):
    f, _ = ra
    aims = A.AIMS
    curve = 4.0 + 0.0005 * (aims - 52.0) ** 2                      # optimum 52 yds right
    r = f(aims, curve)
    assert r["aim"] == 52.0 and r["aim_bound"] == [-40.0, 60.0] and not r["at_bound"]
    curve = 4.0 + 0.0005 * (aims + 75.0) ** 2                      # 75 left: capped at one step (MAX_EXTRA 20)
    r = f(aims, curve)
    assert r["aim"] == -60.0 and r["aim_bound"] == [-60.0, 40.0] and r["at_bound"]


def test_keeps_the_bound_when_not_better_or_guarded(ra):
    f, ok = ra
    aims = A.AIMS
    flat = 4.0 + 0.0005 * (aims - 40.0) ** 2                       # optimum exactly on the bound
    assert f(aims, flat)["aim"] == 40.0 and "aim_bound" not in f(aims, flat)
    curve = 4.0 + 0.0005 * (aims - 52.0) ** 2
    ok["fn"] = lambda a: a <= 45                                    # 52 right is another hole / a hazard
    r = f(aims, curve)
    assert r["aim"] == 40.0 and r["at_bound"]
    A.CTX["hd"] = {}                                               # no line of play: fixed bound
    ok["fn"] = lambda a: True
    assert f(aims, curve)["aim"] == 40.0


def test_wind_drift_shifted_bound(ra):
    f, _ = ra
    aims = A.AIMS
    curve = 4.0 + 0.0005 * (aims - 50.0) ** 2
    r = f(aims, curve, -40.0 - 6.0, 40.0 - 6.0)                     # drift 6 yds right: bound -46..34
    assert r["aim"] == 50.0 and r["aim_bound"] == [-46.0, 54.0]


def test_off_switch(ra, monkeypatch):
    f, _ = ra
    monkeypatch.setenv("V2_ADAPTIVE_AIM", "0")
    curve = 4.0 + 0.0005 * (A.AIMS - 52.0) ** 2
    assert f(A.AIMS, curve)["aim"] == 40.0


def test_crop_widens_only_the_wide_side():
    # build_wind_page.tee_hole crops +/-75 off the tee line; a wide aim's landing oval (Gustin Gold 6 4-wood -60,
    # half width 27 + pad) needs more on its own side only
    assert A.crop_lateral(None) == (A.CROP_LAT, A.CROP_LAT)
    assert A.crop_lateral((97.0, 10.0)) == (97.0, A.CROP_LAT)
    assert A.crop_lateral((40.0, 103.5)) == (A.CROP_LAT, 103.5)


def test_page_stage_runs_through_the_wrapper():
    # course_page.py finish builds the page through v2_adaptive.py, and v2_course's alt-base page subprocesses
    # (os.path.abspath(__file__)) come back through it, so every solved set gets the wide crop
    import course_page as cp
    src = open(cp.__file__).read()
    assert '[sys.executable, VC_ADAPT_PY, "page"' in src and 'vc(q, "page"' not in src
    vc = A.load_v2_course()
    assert os.path.abspath(vc.__file__) == os.path.abspath(A.__file__)
