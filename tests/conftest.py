"""Shared fixtures for the golf strategy test suite.

The spirit_hollow scripts import the mozingo modules through sys.path inserts
(see spirit_hollow/build.py); replicate that here so `tee_strategy`,
`yardage_book`, `stats` and `course` all resolve as top-level modules and the
same module objects are shared by the code under test and by the tests.
"""
import copy
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOZINGO = os.path.join(ROOT, "mozingo")
SPIRIT = os.path.join(ROOT, "spirit_hollow")
for _p in (SPIRIT, MOZINGO):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tee_strategy as _t      # noqa: E402
import yardage_book as _yb     # noqa: E402
import course as _course       # noqa: E402

N_TEST = 2000

# Globals of tee_strategy that tests (or the code under test) may change.
_T_GLOBALS = ("HOLES", "CLUBS", "IRONS", "TAIL_NU", "CHI", "RHO", "HCP_BASELINE", "Z",
              "TREE_SEVERITY", "NATIVE_LOST", "MISHIT_RATE", "ROUGH_ROLL", "REFINE", "NATIVE_IS_PENALTY_AREA")
_YB_GLOBALS = ("NAME", "DIR", "PREFIX", "STRATEGY_NAME", "ORDER", "LABELS", "PAR3", "NOTES",
               "AIM_AT", "WIND_NOW")


@pytest.fixture(autouse=True)
def _restore_globals():
    """Snapshot module globals before every test and put them back afterwards."""
    t_saved = {k: getattr(_t, k) for k in _T_GLOBALS}
    yb_saved = {k: getattr(_yb, k) for k in _YB_GLOBALS}
    yield
    for k, v in t_saved.items():
        setattr(_t, k, v)
    for k, v in yb_saved.items():
        setattr(_yb, k, v)
    _yb.tee_plan.cache_clear()


@pytest.fixture
def t():
    return _t


@pytest.fixture
def yb():
    return _yb


@pytest.fixture
def course():
    return _course


@pytest.fixture(scope="session")
def z():
    """Fixed common-random-number draws (2 normals + 2 uniforms per shot)."""
    r = np.random.default_rng(12345)
    return np.vstack([r.standard_normal((2, N_TEST)), r.random((2, N_TEST))])


@pytest.fixture
def spirit_holes(t, monkeypatch):
    """Point tee_strategy at a private deep copy of the Spirit Hollow holes."""
    holes = copy.deepcopy(_course.HOLES)
    monkeypatch.setattr(t, "HOLES", holes)
    return holes
