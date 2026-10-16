"""tee_strategy: expected-strokes baselines, the shot simulator and the model switches."""
import copy

import numpy as np
import pytest

import course as course_mod
import tee_strategy as tmod

D = np.arange(0.0, 601.0, 1.0)          # 0-600 yds in 1-yd steps (covers clip + >300 tail)
MOZ_HOLES = list(tmod.HOLES)            # captured at import, before any patching
SH_HOLES = list(course_mod.HOLES)
HUGE = [(-1e5, -1e5), (1e5, -1e5), (1e5, 1e5), (-1e5, 1e5)]


# ---------------------------------------------------------------- expected_strokes
@pytest.mark.parametrize("lie", ["fairway", "rough", "water", "ob"])
def test_expected_strokes_monotone(t, lie):
    e = t.expected_strokes(lie, D)
    assert np.all(np.diff(e) >= -1e-12), f"{lie} decreases somewhere"


# Regression test (bug found by this suite, fixed in tee_strategy.py)
def test_expected_strokes_recovery_monotone(t):
    e = t.expected_strokes("recovery", D)
    assert np.all(np.diff(e) >= -1e-12)


@pytest.mark.parametrize("lie", ["fairway", "rough", "water", "ob"])
def test_hcp_baseline_monotone(t, monkeypatch, lie):
    monkeypatch.setattr(t, "HCP_BASELINE", True)
    assert np.all(np.diff(t.expected_strokes(lie, D)) >= -1e-12)


def test_rough_at_least_fairway(t):
    assert np.all(t.expected_strokes("rough", D) >= t.expected_strokes("fairway", D))


def test_water_is_rough_plus_one(t):
    np.testing.assert_allclose(t.expected_strokes("water", D), t.expected_strokes("rough", D) + 1.0,
                               rtol=0, atol=1e-12)


def test_ob_is_water_plus_one(t):
    np.testing.assert_allclose(t.expected_strokes("ob", D), t.expected_strokes("water", D) + 1.0,
                               rtol=0, atol=1e-12)


@pytest.mark.parametrize("lie", ["fairway", "rough", "sand", "recovery", "native", "water", "ob"])
def test_values_beyond_300_keep_rising(t, lie):
    d = np.array([300.0, 320.0, 350.0, 400.0, 500.0])
    e = t.expected_strokes(lie, d)
    assert np.all(np.diff(e) > 0)
    np.testing.assert_allclose(e - e[0], (d - 300) * t.LONG_SLOPE, atol=1e-12)


def test_expected_strokes_matches_table_at_knots(t):
    for lie in ("fairway", "rough", "sand", "recovery"):
        np.testing.assert_allclose(t.expected_strokes(lie, t.DIST), t.BASELINE[lie], atol=1e-12)


def test_scalar_input(t):
    assert float(t.expected_strokes("fairway", 150)) == pytest.approx(
        np.interp(150, t.DIST, t.BASELINE["fairway"]))


def test_hcp_baseline_raises_fairway_and_resets_exactly(t):
    orig = {lie: t.expected_strokes(lie, D).copy()
            for lie in ("fairway", "rough", "sand", "recovery", "native", "water", "ob")}
    t.HCP_BASELINE = True
    try:
        hcp = t.expected_strokes("fairway", D)
        assert np.all(hcp > orig["fairway"])
        # every bad lie costs 1.3x the tour gap over the fairway
        for lie in ("rough", "water", "ob"):
            np.testing.assert_allclose(
                t.expected_strokes(lie, D) - hcp, 1.3 * (orig[lie] - orig["fairway"]), atol=1e-12)
    finally:
        t.HCP_BASELINE = False
    for lie, v in orig.items():
        assert np.array_equal(t.expected_strokes(lie, D), v)


# ---------------------------------------------------------------- simulate
def test_simulate_shapes(t, z):
    pts, lie, to_green, strokes = t.simulate(1, "Driver", 0.0, z=z)
    n = z.shape[1]
    assert pts.shape == (n, 2) and lie.shape == (n,) and to_green.shape == (n,)
    assert strokes.shape == (n,)
    assert np.all(np.isfinite(strokes)) and np.all(strokes > 1.0)
    assert set(lie) <= {"fairway", "rough", "sand", "recovery", "native", "water", "ob"}


@pytest.mark.parametrize("hole", MOZ_HOLES)
def test_simulate_deterministic_with_fixed_z(t, z, hole):
    for club in t.clubs_for(hole):
        a = t.simulate(hole, club, 2.5, z=z)
        b = t.simulate(hole, club, 2.5, z=z)
        assert np.array_equal(a[0], b[0])
        assert np.array_equal(a[1], b[1])
        assert np.array_equal(a[2], b[2])
        assert np.array_equal(a[3], b[3])


def test_simulate_default_z_deterministic(t):
    a = t.simulate(4, "Driver", 0.0)
    b = t.simulate(4, "Driver", 0.0)
    assert a[0].shape == (t.N_SHOTS, 2)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[3], b[3])


def test_default_z_tails_use_cached_chi(t):
    t.set_tails(5)
    a = t.simulate(4, "Driver", 0.0)
    b = t.simulate(4, "Driver", 0.0)
    assert np.array_equal(a[0], b[0])


def test_simulate_does_not_mutate_z(t, z):
    z0 = z.copy()
    t.simulate(1, "Driver", 0.0, z=z)
    assert np.array_equal(z, z0)


def test_best_aim_deterministic(t, z):
    aims = np.arange(-10, 10.1, 5)
    a = t.best_aim(4, "Driver", aims=aims, z=z)
    b = t.best_aim(4, "Driver", aims=aims, z=z)
    assert a["aim"] == b["aim"] and a["ev"] == b["ev"]
    assert a["ev"] == pytest.approx(min(t.simulate(4, "Driver", x, z=z)[3].mean() for x in aims))


def _landing(t, monkeypatch, hole, club, aim, z):
    """Landing spots: same draws with all roll removed (total = carry, no extra_roll)."""
    clubs = {k: (c, c, w, d) for k, (c, _, w, d) in t.CLUBS.items()}
    irons = {k: (c, c, w, d) for k, (c, _, w, d) in t.IRONS.items()}
    holes = copy.deepcopy(t.HOLES)
    holes[hole].pop("extra_roll", None)
    with monkeypatch.context() as m:
        m.setattr(t, "CLUBS", clubs)
        m.setattr(t, "IRONS", irons)
        m.setattr(t, "HOLES", holes)
        pts, lie, *_ = t.simulate(hole, club, aim, z=z)
    return pts, lie


def _check_stop_dead(t, monkeypatch, hole, z):
    for club in t.clubs_for(hole):
        land, land_lie = _landing(t, monkeypatch, hole, club, 0.0, z)
        pts, lie, *_ = t.simulate(hole, club, 0.0, z=z)
        haz = np.isin(land_lie, t.HAZARDS)
        assert np.array_equal(pts[haz], land[haz]), f"hole {hole} {club}: a ball moved in a hazard"
        assert np.array_equal(lie[haz], land_lie[haz])
        # balls that rolled must have rolled forward (never backwards)
        assert np.all(np.linalg.norm(pts - np.array(t.HOLES[hole]["tee"]), axis=1)
                      >= np.linalg.norm(land - np.array(t.HOLES[hole]["tee"]), axis=1) - 1e-9)


@pytest.mark.parametrize("hole", MOZ_HOLES)
def test_balls_stop_dead_in_hazards_mozingo(t, monkeypatch, z, hole):
    _check_stop_dead(t, monkeypatch, hole, z)


@pytest.mark.parametrize("hole", SH_HOLES)
def test_balls_stop_dead_in_hazards_spirit(t, monkeypatch, z, spirit_holes, hole):
    _check_stop_dead(t, monkeypatch, hole, z)


def test_some_balls_actually_land_in_hazards(t, monkeypatch, z):
    # sanity: the stop-dead test is not vacuous (Mozingo 18 has trees, marsh, prairie)
    _, land_lie = _landing(t, monkeypatch, 18, "Driver", 0.0, z)
    assert np.isin(land_lie, t.HAZARDS).sum() > 50


@pytest.mark.parametrize("hole", SH_HOLES)
def test_driver_wins_with_no_hazards(t, monkeypatch, z, hole):
    holes = copy.deepcopy(course_mod.HOLES)
    for h in holes.values():
        h["zones"] = [("fairway", HUGE)]
    monkeypatch.setattr(t, "HOLES", holes)
    ev = {c: t.simulate(hole, c, 0.0, z=z)[3].mean() for c in t.CLUBS}
    assert np.all(t.simulate(hole, "Driver", 0.0, z=z)[1] == "fairway")
    assert ev["Driver"] < ev["2-wood"], ev
    assert ev["Driver"] < ev["4-wood"], ev


# ---------------------------------------------------------------- switches
def _snapshot(t, z):
    return {(h, c, a): t.simulate(h, c, a, z=z) for h in (1, 7, 17) for c in t.clubs_for(h)
            for a in (-5.0, 5.0)}


def _assert_same(a, b):
    assert a.keys() == b.keys()
    for k in a:
        for x, y in zip(a[k], b[k]):
            assert np.array_equal(x, y), k


def test_tails_switch_side_effect_free(t, z):
    before = _snapshot(t, z)
    t.set_tails(5)
    assert t.TAIL_NU == 5 and t.CHI is not None and t.CHI.shape == (t.N_SHOTS,)
    changed = t.simulate(1, "Driver", -5.0, z=z)
    assert not np.array_equal(changed[0], before[(1, "Driver", -5.0)][0])
    t.set_tails(None)
    assert t.TAIL_NU is None and t.CHI is None
    _assert_same(before, _snapshot(t, z))


def test_rho_switch_side_effect_free(t, z):
    before = _snapshot(t, z)
    t.RHO = 0.3
    assert not np.array_equal(t.simulate(1, "Driver", -5.0, z=z)[0], before[(1, "Driver", -5.0)][0])
    t.RHO = 0.0
    _assert_same(before, _snapshot(t, z))


def test_hcp_switch_side_effect_free_on_simulate(t, z):
    before = _snapshot(t, z)
    t.HCP_BASELINE = True
    hcp = t.simulate(1, "Driver", -5.0, z=z)
    assert hcp[3].mean() > before[(1, "Driver", -5.0)][3].mean()
    t.HCP_BASELINE = False
    _assert_same(before, _snapshot(t, z))


def test_all_switches_together_then_reset(t, z):
    before = _snapshot(t, z)
    t.set_tails(5)
    t.RHO = -0.3
    t.HCP_BASELINE = True
    _snapshot(t, z)
    t.set_tails(None)
    t.RHO = 0.0
    t.HCP_BASELINE = False
    _assert_same(before, _snapshot(t, z))


def test_tails_keep_95pct_width(t):
    # Student-t rescaled so its 97.5% quantile equals the normal's 1.96
    st = pytest.importorskip("scipy.stats")
    for nu, q in t.T975.items():
        assert q == pytest.approx(st.t.ppf(0.975, nu), abs=2e-3)


# Regression test (bug found by this suite, fixed in tee_strategy.py)
def test_tails_deterministic_with_custom_z(t, z):
    t.set_tails(5)
    a = t.simulate(1, "Driver", 0.0, z=z)
    b = t.simulate(1, "Driver", 0.0, z=z)
    assert np.array_equal(a[0], b[0])


# ---------------------------------------------------------------- hole_frame
@pytest.mark.parametrize("hole", SH_HOLES)
def test_hole_frame_270_dot_is_270_yds_spirit(t, hole):
    h = course_mod.HOLES[hole]
    tee, fwd, right, ppy = t.hole_frame(h)
    dot = np.array(h["dot270"], float)
    assert np.linalg.norm(dot - tee) / ppy == pytest.approx(270.0, abs=1e-9)
    np.testing.assert_allclose(tee + 270 * fwd * ppy, dot, atol=1e-9)
    assert np.dot(fwd, right) == pytest.approx(0.0, abs=1e-12)
    assert np.linalg.norm(fwd) == pytest.approx(1.0) and np.linalg.norm(right) == pytest.approx(1.0)
    # golfer's right: screen y points down, so right = rotate fwd by +90 deg in screen coords
    assert fwd[0] * right[1] - fwd[1] * right[0] > 0


@pytest.mark.parametrize("hole", MOZ_HOLES)
def test_hole_frame_270_dot_is_270_yds_mozingo(t, hole):
    h = t.HOLES[hole]
    tee, fwd, right, ppy = t.hole_frame(h)
    assert np.linalg.norm(np.array(h["dot270"], float) - tee) / ppy == pytest.approx(270.0, abs=1e-9)


def test_simulated_carry_scale(t, z):
    # with no mishits, no roll and no lateral spread, every ball lands at carry yds from the tee
    zz = z.copy()
    zz[0] = 0.0
    zz[1] = 0.0
    zz[2] = 1.0       # never a mishit
    clubs = {k: (c, c, w, d) for k, (c, _, w, d) in t.CLUBS.items()}
    t.CLUBS = clubs
    for hole in SH_HOLES:
        h = copy.deepcopy(course_mod.HOLES[hole])
        h.pop("extra_roll", None)
        t.HOLES = {hole: h}
        pts, *_ = t.simulate(hole, "Driver", 0.0, z=zz)
        tee, _, _, ppy = t.hole_frame(h)
        np.testing.assert_allclose(np.linalg.norm(pts - tee, axis=1) / ppy, clubs["Driver"][0])
