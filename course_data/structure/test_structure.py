"""Unit tests (light, offline): python -m pytest -q course_data/structure/test_structure.py"""
from __future__ import annotations

import itertools
import math
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import crf  # noqa: E402
import scene as S  # noqa: E402
import solver as V  # noqa: E402


def brute(trans, start, end, N, turn=None):
    M = trans.shape[0]
    scores = {}
    for seq in itertools.permutations(range(M), N):
        s = start[seq[0]] + end[seq[-1]]
        for k in range(1, N):
            tr = turn if (turn is not None and k == 9) else trans
            s += tr[seq[k - 1], seq[k]]
        scores[seq] = s
    return scores


@pytest.mark.parametrize("M,N", [(5, 4), (6, 6), (7, 5)])
def test_route_dp_matches_brute_force(M, N):
    rng = np.random.default_rng(M * 10 + N)
    trans = rng.normal(0, 2, (M, M))
    np.fill_diagonal(trans, -1e4)
    start, end = rng.normal(0, 1, M), rng.normal(0, 1, M)
    sc = brute(trans, start, end, N)
    vals = np.array(list(sc.values()))
    logZ = math.log(np.exp(vals - vals.max()).sum()) + vals.max()
    r = V.route_dp(trans, start, end, N)
    assert abs(r["logZ"] - logZ) < 1e-3
    best = max(sc, key=sc.get)
    assert tuple(r["best"]) == best
    # exact marginals
    marg = np.zeros((M, N))
    for seq, s in sc.items():
        for k, j in enumerate(seq):
            marg[j, k] += math.exp(s - logZ)
    assert np.allclose(r["marg"], marg, atol=1e-4)


def test_route_dp_turn_matrix():
    rng = np.random.default_rng(3)
    M = N = 10
    trans = rng.normal(0, 1, (M, M))
    turn = rng.normal(0, 1, (M, M))
    start, end = rng.normal(0, 1, M), rng.normal(0, 1, M)
    r = V.route_dp(trans, start, end, N, turn=turn)
    best = V.route_score((trans, turn, start, end), r["best"])
    assert abs(best - r["best_score"]) < 1e-3


def test_crf_pairwise_marginals_sum():
    rng = np.random.default_rng(5)
    M, N = 6, 5
    trans = rng.normal(0, 1, (M, M))
    np.fill_diagonal(trans, -1e4)
    start, end = rng.normal(0, 1, M), rng.normal(0, 1, M)
    logZ, marg, xi, xi_t = crf.fb(trans, None, start, end, N)
    assert abs(xi.sum() - (N - 1)) < 1e-6                 # N - 1 moves per route
    assert np.allclose(marg.sum(0), 1.0, atol=1e-6)
    assert np.allclose(xi.sum(1), marg[:, :N - 1].sum(1), atol=1e-6)


def synthetic_course(n=9, seed=0):
    """A loop of n parallel holes going out and back (classic returning nine), clubhouse at the origin."""
    rng = np.random.default_rng(seed)
    feats = []
    holes = []
    lon0, lat0 = -90.0, 40.0
    pj = S.Proj(lon0, lat0)
    x = 0.0
    lengths = [380, 160, 520, 400, 350, 190, 480, 420, 390][:n]
    for i, L in enumerate(lengths):
        up = i % 2 == 0
        tee = np.array([x, 30.0 if up else 30.0 + L])
        green = np.array([x, 30.0 + L if up else 30.0])
        holes.append((tee, green))
        x += 70.0
    out = []
    for i, (t, g) in enumerate(holes):
        r = 12
        ring = [g + r * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 13)]
        out.append(dict(type="Feature", properties=dict(golf="green"),
                        geometry=dict(type="Polygon", coordinates=[[pj.ll(p) for p in ring]])))
        d = (g - t) / np.linalg.norm(g - t)
        n_ = np.array([-d[1], d[0]])
        box = [t + 8 * d + 4 * n_, t + 8 * d - 4 * n_, t - 8 * d - 4 * n_, t - 8 * d + 4 * n_, t + 8 * d + 4 * n_]
        out.append(dict(type="Feature", properties=dict(golf="tee"),
                        geometry=dict(type="Polygon", coordinates=[[pj.ll(p) for p in box]])))
        out.append(dict(type="Feature", properties=dict(golf="hole", ref=str(i + 1)),
                        geometry=dict(type="LineString", coordinates=[pj.ll(t), pj.ll(g)])))
    ch = np.array([-40.0, 10.0])
    sq = [ch + np.array(v) for v in ((-15, -15), (15, -15), (15, 15), (-15, 15), (-15, -15))]
    out.append(dict(type="Feature", properties=dict(building="yes", name="Clubhouse"),
                    geometry=dict(type="Polygon", coordinates=[[pj.ll(p) for p in sq]])))
    return dict(type="FeatureCollection", features=out)


def test_synthetic_loop_is_solved():
    fc = synthetic_course(9)
    sc = S.scene_from_osm(fc)
    assert len(sc.greens) == 9 and not any(f["properties"].get("golf") == "hole" for f in [])
    truth = S.truth_from_osm(fc, sc.proj)
    res = V.solve(sc, n_holes=9)
    import eval as E
    r = E.score_course(res, sc, truth, 9)
    assert r["formation"] == 9
    assert r["number"] >= 8


def test_scene_hides_holes_and_refs():
    fc = synthetic_course(9)
    sc = S.scene_from_osm(fc)
    assert all("ref" not in g for g in sc.greens)
    assert len(sc.clubhouse) == 1 and sc.clubhouse[0]["how"] == "named"


def test_contract_shape():
    import structure as ST
    fc = synthetic_course(9)
    res, sc = ST.run(fc, None, None, n_holes=9)
    assert res["schema"] == "course_structure/1"
    assert set(res["holes"]) == {str(i) for i in range(1, 10)}
    h = res["holes"]["1"]
    for k in ("tee_ll", "green_ll", "par", "confidence", "status", "bearing_deg"):
        assert k in h
    fc2 = ST.to_hole_features(res, {"type": "FeatureCollection", "features": []})
    assert len(fc2["features"]) == 9


def test_infer_pars_prior():
    pp = [[0.9, 0.1, 0.0]] * 4 + [[0.05, 0.9, 0.05]] * 10 + [[0.0, 0.2, 0.8]] * 4
    assert sum(V.infer_pars(pp, 18)) == 72
