"""C beam (kernel.c fr_beam) == numpy beam2 (zero_tap/joint/solve2.py): identical routings and costs, plain and
Lagrange-priced, with forbids (margins), on synthetic courses and (when the routing bench's prepared inputs are
cached) real ones.   python3 -m pytest course_data/platform/fastc/routing/test_fastroute.py -q"""
import glob
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
J = os.path.join(CD, "zero_tap", "joint")
sys.path[:0] = [HERE, J, os.path.dirname(J), os.path.join(CD, "platform", "fastpath"), os.path.join(CD, "platform")]
import fastroute  # noqa: E402
import solve2 as S2  # noqa: E402


def _both(pr, **kw):
    os.environ["GOLF_FASTC"] = "0"
    a = S2.beam2(pr, keep=3, **kw)
    os.environ["GOLF_FASTC"] = "1"
    b = S2.beam2(pr, keep=3, **kw)
    return a, b


def synthetic(seed, ng=14, nt=20, N=9):
    """a random course in the Course / geometry shape solve2 reads"""
    from shapely.geometry import Polygon
    rng = np.random.default_rng(seed)
    G = rng.uniform(0, 1200, (ng, 2))
    T = [dict(c=rng.uniform(0, 1200, 2), pts=rng.uniform(0, 1200, (1, 2)), p=0.9, id="t%d" % k, ax=None)
         for k in range(nt)]
    for t in T:
        t["pts"] = t["c"][None, :] + rng.normal(0, 8, (2, 2))
    Tc = np.array([t["c"] for t in T])
    D = np.hypot(Tc[:, None, 0] - G[None, :, 0], Tc[:, None, 1] - G[None, :, 1])
    Pbox = [[np.hypot(*(t["pts"] - G[g]).T) for g in range(ng)] for t in T]
    hp = np.array([(t, g) for t in range(nt) for g in range(ng)])
    wp = np.array([(g, t) for g in range(ng) for t in range(nt)])
    fair = [dict(poly=Polygon([(100, 100), (500, 120), (480, 300), (90, 260)]), cl=np.array([[300, 200]]))]
    co = dict(G=G, Gr=np.full(ng, 12.0), Gp=np.full(ng, 0.9), T=T, fair=fair, obst=[Polygon([(600, 600), (700, 600),
              (700, 700), (600, 700)])], club=(600.0, 500.0))
    geo = dict(D=D, P=D.copy(), Pbox=Pbox, Tc=Tc)
    sc = dict(ph=rng.uniform(0, 1, len(hp)) ** 3, pw=rng.uniform(0, 1, len(wp)) ** 3, ps=rng.uniform(0, 1, nt),
              pe=rng.uniform(0, 1, ng))
    y = list(rng.integers(120, 560, N))
    card = dict(tee_sets=dict(a=dict(yards=y), b=dict(yards=[int(v * 0.93) for v in y])))
    return dict(co=co, geo=geo, sc=sc, hp=hp, wp=wp, kind=N), card


def test_synthetic_identical():
    assert fastroute.lib() is not None, fastroute._L[1]
    for seed in range(6):
        d, card = synthetic(seed, N=9 if seed % 2 else 18)
        for reuse in (1, 0):
            pr = S2.Problem2(d, card, dict(beam=150 + 70 * seed, tee_reuse=reuse))
            a, b = _both(pr)
            assert a == b, (seed, reuse)
            price = S2.lagrange(pr)
            a, b = _both(pr, price=price)
            assert a == b
            if a:
                c = a[0][1][3]
                k, t, g = pr.cand[c]
                fb = {(3, "g", int(g))} if g >= 0 else {(3, "t", int(t))}
                a, b = _both(pr, forbid=fb, beam_w=60)
                assert a == b


def test_bench_courses_identical():
    """prepared inputs of the routing bench (route_bench.py --prep), when this machine has them"""
    fs = sorted(glob.glob(os.path.join(CD, "platform", "fastpath", "cache", "val", "prep", "*", "v1", "*.pkl")))[:6]
    import route_scene as RS
    RS._mods()
    for f in fs:
        x, pd = pickle.load(open(f, "rb"))
        if pd is None:
            continue
        d, _ = pd
        pr = S2.Problem2(d, x["card"], dict(RS.V1_PARAMS, beam=400))
        a, b = _both(pr)
        assert a == b, f
        a, b = _both(pr, price=S2.lagrange(pr))
        assert a == b, f
