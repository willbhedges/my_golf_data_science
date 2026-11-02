"""pathroute v2 self-checks on synthetic data (no benchmark data needed)."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "pathroute"), os.path.dirname(HERE)]
import decode as DC  # noqa: E402
import decode2 as D2  # noqa: E402
import complexes as CX  # noqa: E402
import confidence as CF  # noqa: E402


def test_seg_cross():
    A = np.array([[0.0, 0.0], [0.0, 10.0]])
    B = np.array([[10.0, 10.0], [10.0, 20.0]])
    X = D2._seg_cross(A, B, np.array([[0.0, 10.0]]), np.array([[10.0, 0.0]]))
    assert X[0, 0] and not X[1, 0]


def _two_holes(swap_bias):
    # two parallel holes: tees at x=0 / x=100 (y=0), greens straight ahead (y=400). The local model slightly
    # prefers the crossed pairing (t0 -> g1, t1 -> g0) by swap_bias nats.
    tc = np.array([[0.0, 0.0], [100.0, 0.0]])
    gc = np.array([[0.0, 400.0], [100.0, 400.0]])
    hp, ph = [], []
    for t in range(2):
        for g in range(2):
            hp.append((t, g))
            ph.append(0.5 if t == g else 0.5 * np.exp(swap_bias))
    tp = [(g, t) for g in range(2) for t in range(2)]
    pt = [0.5] * 4
    d = dict(kind=9, hp=hp, tp=tp, tees=[{}] * 2, greens=[{}] * 2, tc=tc, gc=gc)
    pr = dict(hole=np.clip(ph, 0, 1), trans=np.array(pt), start=np.full(2, 0.5), end=np.full(2, 0.5))
    return d, pr


def test_crossing_penalty_uncrosses():
    d, pr = _two_holes(0.3)
    H, T, S, E = DC.cost_mats(d, pr, dict(trans=1.0, club=1.0))
    args = (H, T, S, E, 2, np.ones(2, bool), np.ones(2, bool), d["tc"], d["gc"], np.arange(2))
    gs, ts, _, _ = D2.beam_loop2(*args, cross=0.0, reuse=0.0)
    assert sorted(zip(ts, gs)) == [(0, 1), (1, 0)]            # crossed without the penalty
    gs, ts, _, _ = D2.beam_loop2(*args, cross=2.0, reuse=2.0)
    assert sorted(zip(ts, gs)) == [(0, 0), (1, 1)]


def test_cluster_average_linkage():
    pairs = [(0, 1), (1, 2), (0, 2), (2, 3)]
    p = [0.9, 0.9, 0.8, 0.6]
    c = CX.cluster(4, pairs, p, thr=0.5)
    assert c[0] == c[1] == c[2] and c[3] != c[0]            # 3 joins only if mean link to {0,1,2} > thr


def test_taps():
    courses = [(np.array([0.99, 0.99, 0.4]), np.array([1, 1, 0])), (np.array([0.99, 0.6]), np.array([1, 1]))]
    thr, taps, prec, zero = CF.taps_to_precision(courses, 0.98)
    assert prec >= 0.98 and taps == 0.5 and zero == 0.5


def _course(swap_bias):
    d, pr = _two_holes(swap_bias)
    d = dict(d, tees=[dict(id="t0"), dict(id="t1")], greens=[dict(id="g0"), dict(id="g1")])
    return d, pr


def _args(d, pr, H=None):
    H0, T, S, E = DC.cost_mats(d, pr, dict(trans=1.0, club=1.0))
    return (H0 if H is None else H, T, S, E, 2, np.ones(2, bool), np.ones(2, bool), d["tc"], d["gc"], np.arange(2))


def test_fix_pair_resolves():
    d, pr = _course(0.3)                                       # the model prefers the crossed pairing
    gs, ts, _, _ = D2.beam_loop2(*_args(d, pr), cross=0.0, reuse=0.0)
    assert sorted(zip(ts, gs)) == [(0, 1), (1, 0)]
    # golfer: "hole 2 is tee 0 -> green 0" -> the other pair follows, and the pinned pair is hole 2
    H = D2.apply_fix(DC.cost_mats(d, pr, dict(trans=1.0, club=1.0))[0], np.arange(2), dict(pairs=[(2, 0, 0)]))
    gs, ts, _, _ = D2.beam_loop2(*_args(d, pr, H), cross=0.0, reuse=0.0, pins={2: (0, 0)})
    assert list(zip(ts, gs)) == [(1, 1), (0, 0)]


def test_hole_one_fixes_start():
    d, pr = _course(-0.3)
    for first in (0, 1):
        gs, ts, _, _ = D2.beam_loop2(*_args(d, pr), first={first}, first_force=first)
        assert ts[0] == first and gs[0] == first


def test_not_a_hole_and_session_ids():
    import resolve2 as RS
    d, pr = _course(-0.3)
    H = D2.apply_fix(np.zeros((2, 2)), np.arange(2), dict(not_green=[1], pairs=[(None, 0, 0)]))
    assert np.isinf(H[:, 1]).all() and H[0, 0] < 0 and np.isinf(H[1, 0])
    f = dict(pairs=[(1, 0, 0)], not_green=[1], first_tee=0)
    s = RS.Session.__new__(RS.Session)
    s.d, s.fix = d, f
    assert RS.Session.from_ids(d, s.to_ids()) == dict(pairs=[(1, 0, 0)], not_green=[1], first_tee=0)


def test_live_route_bench_course():
    """live2.route (the stage_select "pathroute_v2" method) on a benchmark course: OSM hole ways become fixed
    pairs, the hidden-holes route has per-hole confidence and an ask order. Skips without the data / model."""
    import pytest
    import live2
    import bench as B
    rows = [r for r in B.courses("test") if r["kind"] == 18]
    if not rows or not os.path.exists(live2.MODEL) or B._rd(rows[0]["files"]["osm"]) is None:
        pytest.skip("benchmark data or model_v2.pkl.gz not checked out")
    r = rows[0]
    x = B.inputs(r, "nocard")
    res = live2.route(B._rd(r["files"]["osm"]), x["course"], n_holes=18)
    assert res["n_holes"] == 18 and res["confirm"]["osm_fixed"] >= 9
    assert all(h["confidence"] == 1.0 for h in res["holes"].values() if h["fixed"])
    hid = live2.route(x["fc"], x["course"], n_holes=18)
    assert hid["confirm"]["osm_fixed"] == 0 and all(0 <= h["confidence"] <= 1 for h in hid["holes"].values())
    ask = hid["confirm"]["ask_order"]
    if ask:                                        # confirm the first asked hole -> it comes back fixed
        h = hid["holes"][ask[0]]
        f = dict(pairs=[[int(ask[0]), h["tee_id"], h["green_id"]]], not_green=[], first_tee=None)
        again = live2.route(x["fc"], x["course"], n_holes=18, fix=f)
        assert again["holes"][ask[0]]["green_id"] == h["green_id"] and again["holes"][ask[0]]["confidence"] == 1.0


def test_reject_pair_forbids_complex():
    H = D2.apply_fix(np.zeros((3, 2)), np.array([0, 0, 1]), dict(reject=[(0, 1)]))
    assert np.isinf(H[0, 1]) and np.isinf(H[1, 1]) and H[2, 1] == 0 and H[0, 0] == 0
    # a reject of a pair the golfer also confirmed is ignored
    H = D2.apply_fix(np.zeros((3, 2)), np.arange(3), dict(pairs=[(1, 0, 1)], reject=[(0, 1)]))
    assert H[0, 1] < 0


def test_calib2_export_matches_predict():
    rng = np.random.default_rng(0)
    X = np.c_[rng.uniform(0, 1, (400, 6)), rng.uniform(0, 30, 400), rng.integers(0, 2, 400), rng.uniform(100, 500, 400),
              np.zeros(400), rng.uniform(0, 1, 400), rng.integers(0, 3, 400), rng.integers(0, 2, 400),
              rng.uniform(0, 14, (400, 2))]
    y = (X[:, 0] + 0.1 * rng.normal(size=400) > 0.5).astype(int)
    cal = CF.Calib2().fit(X, y)
    e = cal.export()
    z = CF.Calib2.transform(X) @ np.array(e["coef"]) + e["intercept"]
    assert np.allclose(1 / (1 + np.exp(-z)), cal.predict(X)) and len(e["coef"]) == 16
    assert np.allclose(cal.predict(X), cal.m.predict_proba((CF.Calib2.transform(X) - cal.mu) / cal.sd)[:, 1])


def test_sticky_bonus_and_weights():
    import resolve2 as RS
    H = D2.apply_fix(np.zeros((3, 2)), np.arange(3), dict(pairs=[(1, 0, 0)], sticky=[(1, 1, 2.5), (2, 0, 9.0)]))
    assert H[1, 1] == -2.5 and np.isinf(H[2, 0])          # a sticky pair on a blanked column stays forbidden
    st = dict(alpha=4.0, pin=0.9, pin_w=30.0, keep=True)
    assert RS.sticky_w(0.5, st) == 2.0 and RS.sticky_w(0.95, st) == 30.0


def test_policy_p_all_need_answer():
    """resolve2.POLICY: P(all right) = product of unconfirmed confidences; need() asks lowest first until the target;
    shipped: every answer re-solves; yes="keep" / not_hole="drop": "yes" / "not a hole" apply without a re-solve."""
    import resolve2 as RS
    assert RS.POLICY["yes"] == "solve" and RS.POLICY["not_hole"] == "solve" and RS.POLICY["sticky"] is None
    s = RS.Session.__new__(RS.Session)
    s.policy = dict(RS.POLICY, target=0.9)
    s.holes = [dict(t=i, g=i, boxes=[], loop=0, number=i + 1) for i in range(2)]
    s.conf = np.array([0.6, 0.8])
    s.fix = dict(pairs=[], not_green=[], first_tee=None)
    s.prev, s.sticky = {}, None
    called = []
    s.solve = lambda: called.append(1)
    assert s.answer(0, tee=None, number=1) is True and called == [1] and (1, 0, 0) in s.fix["pairs"]
    assert s.answer(1, not_hole=True) is True and called == [1, 1] and 1 in s.fix["not_green"]
    s = RS.Session.__new__(RS.Session)
    s.policy = dict(RS.POLICY, target=0.9, yes="keep", not_hole="drop")
    s.holes = [dict(t=i, g=i, boxes=[], loop=0, number=i + 1) for i in range(4)]
    s.conf = np.array([0.99, 0.6, 1.0, 0.8])
    s.fix = dict(pairs=[(3, 2, 2)], not_green=[], first_tee=None)
    s.prev, s.sticky = {}, None
    assert abs(s.p_all() - 0.99 * 0.6 * 0.8) < 1e-12
    assert s.need() == [1, 3] and s.ask_all() == 1 and s.need(0.5) == [1] and s.need(0.4) == []
    s.solve = lambda: (_ for _ in ()).throw(AssertionError("no re-solve expected"))
    assert s.answer(1, tee=None, number=2) is False and s.conf[1] == 1.0 and (2, 1, 1) in s.fix["pairs"]
    assert s.answer(2, not_hole=True) is False and len(s.holes) == 3 and 2 in s.fix["not_green"]
    called = []
    s.solve = lambda: called.append(1)
    assert s.answer(0, tee=7, number=1) is True and called and (1, 7, 0) in s.fix["pairs"]
    assert RS.p_all([0.5, 1.0], [False, True]) == 0.5


def test_policy_hole1_first():
    """POLICY h1 "first": a 9 / 18-hole course asks the hole-1 tee until one is set; other kinds never."""
    import resolve2 as RS
    s = RS.Session.__new__(RS.Session)
    s.policy = dict(RS.POLICY)
    s.fix = dict(pairs=[], not_green=[], first_tee=None)
    for kind, want in ((9, True), (18, True), (27, False), (36, False)):
        s.d = dict(kind=kind)
        assert s.need_hole1() is want
    s.d = dict(kind=18)
    s.hole_one(3)
    assert s.need_hole1() is False
    s.fix["first_tee"], s.policy["h1"] = None, "last"
    assert s.need_hole1() is False
