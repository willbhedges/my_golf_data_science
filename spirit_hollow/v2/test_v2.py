"""Unit tests for the v2 engine (light: python3 -m pytest -q spirit_hollow/v2)."""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decide as D                               # noqa: E402
import model as M                                # noqa: E402
import tee_strategy as t                         # noqa: E402


@pytest.fixture(scope="module")
def v1_globals():
    import course
    save = (t.HOLES, t.CLUBS, t.IRONS, t.TREE_SEVERITY, t.NATIVE_LOST, t.MISHIT_RATE)
    w = 70 / 65
    t.HOLES = course.HOLES
    t.CLUBS = {k: (c, tot, wd * w, d * 1.25) for k, (c, tot, wd, d) in M.CLUBS.items() if k in M.WOODS}
    t.IRONS = {k: (c, tot, wd * w, d * 1.25) for k, (c, tot, wd, d) in M.CLUBS.items() if k not in M.WOODS}
    t.TREE_SEVERITY, t.NATIVE_LOST = 0.8, 0.5
    t.MISHIT_RATE = {k: 0.15 for k in M.CLUBS}
    yield
    t.HOLES, t.CLUBS, t.IRONS, t.TREE_SEVERITY, t.NATIVE_LOST, t.MISHIT_RATE = save


@pytest.mark.parametrize("h", [1, 11])
def test_engine_reproduces_v1(v1_globals, h):
    """In v1's world the raster engine matches tee_strategy.simulate (same swings) to < 0.01."""
    P = M.v1_world()
    z = M.draws_z(3000, 3)
    zv1 = np.vstack([z[1], z[0], z[2], z[3]])
    hd = M.HOLES[h]
    R = M.Raster(hd)
    S = R.strokes(P, hd["length"])
    aims = np.array([-10.0, 0.0, 10.0])
    for c in M.WOODS:
        ev2, _ = M.ev_curve(R, S, hd, c, P, z, aims)
        ev1 = np.array([t.simulate(h, c, a, z=zv1)[3].mean() for a in aims])
        assert np.abs(ev2 - ev1).max() < 0.01, (h, c, ev1, ev2)


def test_robust_aim_quadratic():
    aims = np.arange(-60, 60.001, 0.5)
    curve = 4.0 + 0.0004 * (aims - 7.3) ** 2
    r = D.robust_aim(aims, curve)
    assert abs(r["aim"] - 7.5) < 1e-9
    half = np.sqrt(0.005 / 0.0004)                 # +/- 3.54 yds within 0.005
    assert abs(r["window"][0] - (7.3 - half)) <= 1.0 and abs(r["window"][1] - (7.3 + half)) <= 1.0
    assert not r["at_bound"]
    r2 = D.robust_aim(aims, 4.0 + 0.001 * aims)     # minimum at the left bound
    assert r2["at_bound"]


def test_soft_roll_and_temperature():
    hd = M.HOLES[1]
    c_warm, roll_warm, *_ = M.club_numbers(hd, "Driver", M.central(temp_f=70.0))
    c_cold, roll_cold, *_ = M.club_numbers(hd, "Driver", M.central(temp_f=48.0))
    assert 3.5 < c_warm - c_cold < 5.5            # ~2 yds per 10 F on a ~290 carry
    assert roll_cold < 3.0                        # soft: a couple of yards
    _, roll_v1, *_ = M.club_numbers(hd, "Driver", M.v1_world())
    assert roll_v1 > 20


def test_mishit_shares_and_mean_carry():
    hd = M.HOLES[1]
    P = M.central(rho=0.0, kappa=0.0)
    z = M.draws_z(200000, 1)
    car, dev, roll = M.shots(hd, "Driver", P, z)
    carry = M.club_numbers(hd, "Driver", P)[0]
    short = np.mean(car < carry * 0.86)
    assert abs(short - P["mis_heavy"]) < 0.004
    # curvature loss is centred: the mean carry of good swings is unchanged
    P2 = M.central(kappa=0.2, rho=0.0, mis_slight=0.0, mis_heavy=0.0)
    car2, *_ = M.shots(hd, "Driver", P2, z)
    assert abs(car2.mean() - carry) < 0.2


def test_penalties():
    hd = M.HOLES["9F"]
    R = M.Raster(hd)
    P = M.central()
    S = R.strokes(P, hd["length"])
    water = (R.lie == M.CODE["water"]) & (R.AA < R.green[0] - 40) & (R.AA < 330)  # reachable, short of the green
    assert water.any()
    # relief from where it went in: never nearer the hole than the landing spot
    assert np.all(R.entry_dist[water] >= R.dist[water] - 1.0)
    # stroke and distance = 1 + tee value; in v1 world a lost ball was 2 + rough
    ob_like = 1.0 + M.tee_value(hd["length"], P)
    native = R.lie == M.CODE["native"]
    assert np.all(S[native] <= ob_like + 1e-9)


def test_prior_draws_shape():
    d = D.prior_draws(8)
    assert len(d) == 8
    w = np.array([p["width"]["Driver"] for p in d])
    assert 55 < w.min() and w.max() < 95
    r4 = np.array([p["width"]["4-wood"] / p["width"]["Driver"] for p in d])
    assert 0.65 < r4.mean() < 0.9
