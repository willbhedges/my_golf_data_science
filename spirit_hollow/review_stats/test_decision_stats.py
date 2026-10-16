"""Tests for the review patch.  python3 -m pytest -q spirit_hollow/review_stats/test_decision_stats.py"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "..", "mozingo"), os.path.join(HERE, ".."), HERE]

import decision as D            # noqa: E402
import decision_stats as DS     # noqa: E402


def synthetic(S=4000, aims=5, sd_theta=0.03, sd_noise=0.04, gap=0.01, seed=0):
    """Two clubs; true EV(c, a | theta) = base_c + theta_c + 0.002 * (a - 2)^2; half-sample noise."""
    rng = np.random.default_rng(seed)
    a = np.arange(aims)
    curve = 0.002 * (a - 2) ** 2
    th = rng.normal(0, sd_theta, S)
    true = {"X": np.zeros(S)[:, None] + curve, "Y": (gap + th)[:, None] + curve}
    # half-sample noise: each half has sd sqrt(2) * sd_noise so the full mean has sd_noise
    MA = {c: v + rng.normal(0, np.sqrt(2) * sd_noise, (S, aims)) for c, v in true.items()}
    MB = {c: v + rng.normal(0, np.sqrt(2) * sd_noise, (S, aims)) for c, v in true.items()}
    return true, MA, MB


def test_error_budget_recovers_components():
    true, MA, MB = synthetic(sd_noise=0.04)
    dA, dB = MA["Y"][:, 2] - MA["X"][:, 2], MB["Y"][:, 2] - MB["X"][:, 2]
    b = DS.error_budget(dA, dB)
    # difference of two independent noises -> noise var 2 * 0.04^2
    assert b["sigma2_z"] == pytest.approx(2 * 0.04 ** 2, rel=0.08)
    assert b["sigma2_theta"] == pytest.approx(0.03 ** 2, rel=0.25)


def test_deconvolved_p_best_removes_noise_bias():
    true, MA, MB = synthetic(sd_theta=0.03, sd_noise=0.04, gap=0.02)
    clubs = ["X", "Y"]
    col = {"X": 2, "Y": 2}
    p_true = float(np.mean(true["X"][:, 2] < true["Y"][:, 2]))          # ~ Phi(0.02/0.03) = 0.75
    naive = DS.p_best_fixed_aims_naive(MA, MB, clubs, col)["X"]
    dec, pair = DS.p_best_deconvolved(MA, MB, clubs, col)
    assert abs(naive - p_true) > 0.08                                      # noise drags it to 50/50
    assert dec["X"] == pytest.approx(p_true, abs=0.03)
    assert pair["Y"] == pytest.approx(p_true, abs=0.03)


def test_evpi_bracket_contains_truth():
    true, MA, MB = synthetic(sd_theta=0.03, sd_noise=0.02, gap=0.005)
    clubs = ["X", "Y"]
    M = {c: (MA[c] + MB[c]) / 2 for c in clubs}
    pick, _, col, _ = DS.posterior_pick(M, clubs)
    v_pick = true[pick][:, col[pick]]
    evpi_true = float(np.mean(v_pick - np.minimum(true["X"].min(1), true["Y"].min(1))))
    naive, cf = DS.evpi_bracket(MA, MB, clubs, pick, col[pick])
    assert cf - 0.001 <= evpi_true <= naive + 0.001
    assert naive - evpi_true > 0.005                                       # naive is visibly high


def test_crossfit_margin_shows_optimism_under_pure_noise():
    # every (club, aim) identical in truth: any in-sample margin is pure selection
    rng = np.random.default_rng(3)
    S, A = 64, 21
    M = {c: rng.normal(0, 0.05, (S, A)) for c in ("X", "Y", "Z")}
    cf = DS.crossfit_margin(M, list(M), S)
    assert cf["optimism_ev"] > 0
    assert cf["margin_out"] < cf["margin_in"]


def test_summarize_smoke_on_real_hole():
    th = D.prior_draws(4)
    Eh = {}
    try:
        for i, x in enumerate(th):
            D.apply(x)
            r = np.random.default_rng(i)
            z = np.vstack([r.standard_normal((2, 400)), r.random((2, 400))])
            DS.accumulate(Eh, DS.ev_grid_halves(16, z))
    finally:
        D.reset()
    s = DS.summarize(Eh)
    assert s["pick"] in s["clubs"] and s["runner"] != s["pick"]
    assert s["evpi_naive"] >= s["evpi_crossfit"] - 1e-9
    assert abs(sum(s["p_best_crossfit"].values()) - 1) < 1e-9
