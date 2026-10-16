"""python3 -m pytest -q spirit_hollow/review_stats/test_prior_patch.py"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "..", "mozingo"), os.path.join(HERE, ".."), HERE]

import tee_strategy as t        # noqa: E402
import prior_patch as PP        # noqa: E402


def test_prior_moments():
    th = PP.prior_draws(1024)
    w = np.array([x["width"] for x in th]) * 65
    assert 80 < np.median(w) < 84
    assert 70 < np.quantile(w, 0.05) < 74 and 92 < np.quantile(w, 0.95) < 96
    r4 = np.array([x["r4w"] for x in th])
    assert 0.83 < np.median(r4) < 0.87
    assert 0.70 < np.mean([x["hcp"] for x in th]) < 0.80


def test_apply_and_reset_roundtrip():
    clubs, irons, rr, hcp = dict(t.CLUBS), dict(t.IRONS), t.ROUGH_ROLL, t.HCP_BASELINE
    th = PP.prior_draws(8)[3]
    try:
        PP.apply(th)
        assert t.CLUBS["4-wood"][2] == np.float64(65 * th["width"] * th["r4w"])
        assert t.CLUBS["4-wood"][2] < t.CLUBS["Driver"][2]
        # carry gap driver - 4-wood keeps its base 20 yds +/- the club-specific parts only
        gap = t.CLUBS["Driver"][0] - t.CLUBS["4-wood"][0]
        assert abs(gap - 20 - (th["c_drv"] - th["c_4w"])) < 1e-9
        assert t.ROUGH_ROLL == th["rough_roll"] and t.HCP_BASELINE == th["hcp"]
        r = np.random.default_rng(0)
        z = np.vstack([r.standard_normal((2, 500)), r.random((2, 500))])
        assert np.isfinite(t.simulate(16, "Driver", 0.0, z=z)[3]).all()
    finally:
        PP.reset()
    assert t.CLUBS == clubs and t.IRONS == irons and t.ROUGH_ROLL == rr and t.HCP_BASELINE == hcp
