"""python3 -m pytest -q spirit_hollow/review_stats/test_baseline_patch.py"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "..", "mozingo"), os.path.join(HERE, ".."), HERE]

import tee_strategy as t        # noqa: E402
import baseline_patch as BP     # noqa: E402

D = np.array([30.0, 100, 150, 220, 350])


@pytest.fixture(autouse=True)
def _restore():
    saved = (t.HCP_BASELINE, t.NATIVE_LOST, t.TREE_SEVERITY, BP.NATIVE_IS_PENALTY_AREA)
    yield
    t.HCP_BASELINE, t.NATIVE_LOST, t.TREE_SEVERITY, BP.NATIVE_IS_PENALTY_AREA = saved
    BP.uninstall()


@pytest.mark.parametrize("lie", ["fairway", "rough", "sand", "recovery", "water", "ob"])
def test_tour_identical_to_original_except_native(lie):
    t.HCP_BASELINE = False
    assert np.allclose(BP.expected_strokes(lie, D), t.expected_strokes(lie, D))


def test_native_penalty_area_mode_matches_original():
    t.HCP_BASELINE, BP.NATIVE_IS_PENALTY_AREA = False, True
    assert np.allclose(BP.expected_strokes("native", D), t.expected_strokes("native", D))


def test_lost_ball_costs_like_ob():
    t.HCP_BASELINE, t.NATIVE_LOST = False, 1.0
    assert np.allclose(BP.expected_strokes("native", D), t.expected_strokes("ob", D))
    t.NATIVE_LOST = 0.5
    gap = BP.expected_strokes("native", D) - t.expected_strokes("native", D)
    assert np.allclose(gap, 0.5)                       # half the balls lost x 1 extra stroke


def test_hcp_penalty_strokes_not_scaled():
    t.HCP_BASELINE = True
    rough = BP.expected_strokes("rough", D)
    assert np.allclose(BP.expected_strokes("water", D) - rough, 1.0)
    assert np.allclose(BP.expected_strokes("ob", D) - rough, 2.0)
    t.NATIVE_LOST = 1.0
    assert np.allclose(BP.expected_strokes("native", D) - rough, 2.0)


def test_hcp_non_penalty_lies_match_original():
    t.HCP_BASELINE = True
    for lie in ("fairway", "rough", "sand", "recovery"):
        assert np.allclose(BP.expected_strokes(lie, D), t.expected_strokes(lie, D))


def test_install_roundtrip():
    orig = t.expected_strokes
    BP.install()
    assert t.expected_strokes is BP.expected_strokes
    BP.uninstall()
    assert t.expected_strokes is orig
