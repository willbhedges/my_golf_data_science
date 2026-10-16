"""spirit_hollow/qa_landing/disagree.py: edge-disagreement logic, patch loader, proposed patches (offline, fast)."""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "spirit_hollow", "qa_landing"))
import disagree as Q          # noqa: E402

LIES = {"fairway", "first_cut", "rough", "recovery", "native", "water", "sand", "ob"}


def _grid():
    a = np.arange(180.0, 346.0)
    l = np.arange(-65.0, 66.0)
    return a, l


def _ev(shape, **strong):
    """{class: (strong, weak, absent)} with weak = strong and absent = ~strong."""
    out = {}
    for c in Q.HAZ:
        s = strong.get(c, np.zeros(shape, bool))
        out[c] = (s, s.copy(), ~s)
    return out


def _hand(l, shape, tree_from):
    hand = np.full(shape, "rough", dtype=object)
    hand[:, np.abs(l) <= 15] = "fairway"
    hand[:, l >= tree_from] = "recovery"
    return hand


def _find(res, kind, cls):
    return [m for k, c, m, d in res if k == kind and c == cls]


def test_edge_within_tolerance_is_not_flagged():
    a, l = _grid()
    shp = (len(a), len(l))
    hand = _hand(l, shp, 25.0)
    ev = _ev(shp, recovery=np.broadcast_to(l >= 22.0, shp).copy())     # evidence edge 3 yds closer
    res = Q.classify_cells(hand, ev, Q.core_mask(a, l))
    assert not _find(res, "missing", "recovery")[0].any()


def test_missing_trees_edge_shift_measured():
    a, l = _grid()
    shp = (len(a), len(l))
    hand = _hand(l, shp, 30.0)
    ev = _ev(shp, recovery=np.broadcast_to(l >= 20.0, shp).copy())     # canopy 10 yds closer
    dens = np.full(shp, 1.0 / (shp[0] * shp[1]))
    w = np.ones(shp)
    for kind, cls, m, dist in Q.classify_cells(hand, ev, Q.core_mask(a, l)):
        if kind == "missing" and cls == "recovery":
            comps = Q.components(kind, cls, m, dist, a, l, dens, w)
    assert len(comps) == 1
    c = comps[0]
    assert c["lat"][0] == 20.0 and c["lat"][1] == 25.0                # > TOL from the hand edge only
    assert c["edge_shift_max"] == pytest.approx(10.0)
    assert c["along"] == (Q.ALONG[0], Q.ALONG[1])                      # clipped to the corridor
    assert c["score"] > 0


def test_phantom_and_swap():
    a, l = _grid()
    shp = (len(a), len(l))
    hand = _hand(l, shp, 20.0)                                        # trees drawn from +20
    ev = _ev(shp, recovery=np.broadcast_to(l >= 35.0, shp).copy())    # canopy really from +35
    res = Q.classify_cells(hand, ev, Q.core_mask(a, l))
    ph = _find(res, "phantom", "recovery")[0]
    assert ph[:, (l >= 20) & (l < 30)].any() and not ph[:, l >= 31].any()
    hand2 = _hand(l, shp, 20.0)
    hand2[:, l >= 20] = "native"
    ev2 = _ev(shp, recovery=np.broadcast_to(l >= 20.0, shp).copy())
    sw = _find(Q.classify_cells(hand2, ev2, Q.core_mask(a, l)), "swap", "native>recovery")[0]
    assert sw[:, l >= 25].any()


def test_duplicate_keys():
    src = "AUDIT_FIXES = {4: [], 5: [], '9B': [], 5: [], 8: [], 8: []}\n"
    assert sorted(Q.duplicate_keys(src)) == [5, 8]
    assert Q.duplicate_keys("AUDIT_FIXES = {1: []}\n") == []


def test_course_with_patches_applies_and_isolates():
    k = 14
    h = Q.course.HOLES[k]
    p = Q.to_px(h, 250.0, 0.0)
    sq = [(int(p[0]) - 6, int(p[1]) - 6), (int(p[0]) + 6, int(p[1]) - 6),
          (int(p[0]) + 6, int(p[1]) + 6), (int(p[0]) - 6, int(p[1]) + 6)]
    before = Q.t.lie_at(h, np.array([p]))[0]
    mod = Q.course_with_patches({k: [("sand", sq)]})
    assert Q.t.lie_at(mod.HOLES[k], np.array([p]))[0] == "sand"
    assert Q.t.lie_at(Q.course.HOLES[k], np.array([p]))[0] == before   # the real course is untouched


def test_proposed_patches_well_formed():
    P = Q.load_proposed()
    assert P.PROPOSED
    for fid, f in P.PROPOSED.items():
        assert f["verdict"] in ("map wrong", "evidence wrong", "unclear"), fid
        assert f["hole"] in Q.course.HOLES, fid
        if f["verdict"] != "map wrong":
            assert not f["patches"], fid
        for lie, poly in f["patches"]:
            assert lie in LIES, fid
            q = np.asarray(poly, float)
            assert q.shape[0] >= 3 and q.shape[1] == 2, fid
            assert (q[:, 0] > -50).all() and (q[:, 0] < 970).all() and (q[:, 1] > 400).all() and (q[:, 1] < 2100).all(), fid
    for k, plist in P.PATCHES.items():
        assert k in Q.course.HOLES
        assert all(isinstance(z, tuple) and len(z) == 2 for z in plist)
