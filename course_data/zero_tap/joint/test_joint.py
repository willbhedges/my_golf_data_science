"""Self-checks of the joint routing solver on a synthetic course (no data files needed)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solve as S  # noqa: E402


def synth(n=9, seed=0):
    """n holes around a ring: tee i -> green i (300 + 20 i yd apart), green i is 50 yd from tee i+1.
    Local scores: the true hole / walk pairs get p = 0.6, everything else 0.05 (so the card must do the numbering)."""
    rng = np.random.default_rng(seed)
    L = np.array([300.0 + 20 * i for i in range(n)])
    T, G, x = [], [], 0.0
    for i in range(n):
        T.append((x, 0.0))
        G.append((x + L[i], 0.0))
        x += L[i] + 50.0
    perm = rng.permutation(n)                       # hide the order of the greens
    G = np.array(G)[perm]
    T = np.array(T)
    hp = np.array([(t, g) for t in range(n) for g in range(n)])
    true_g = {int(perm[k]): k for k in range(n)}    # hole index -> green index
    ph = np.array([0.6 if true_g[t] == g else 0.05 for t, g in hp])
    wp = np.array([(g, t) for g in range(n) for t in range(n)])
    pw = np.array([0.6 if true_g.get(t - 1) == g else 0.05 for g, t in wp])
    Pbox = [[np.array([abs(G[g][0] - T[t][0])]) for g in range(n)] for t in range(n)]
    d = dict(kind=n, hp=hp, wp=wp, co=dict(G=G, T=[dict(c=T[t], pts=T[t][None], p=0.9) for t in range(n)],
                                           Gp=np.full(n, 0.9)),
             geo=dict(Tc=T, Pbox=Pbox), sc=dict(ph=ph, pw=pw, ps=np.full(n, 0.2), pe=np.full(n, 0.2)))
    card = dict(tee_sets=dict(blue=dict(yards=[int(v) for v in L])))
    return d, card, true_g


def test_card_sets_and_llr():
    Y = S.card_sets(dict(tee_sets=dict(a=dict(yards=[100] * 9), b=dict(yards=[120] * 9), c=dict(yards=[0] * 9))), 9)
    assert Y.shape == (2, 9) and Y[0, 0] == 120
    assert S.card_sets(None, 9) is None
    assert S.card_llr(np.array([0.0]), S.DEF)[0] < 0 < S.card_llr(np.array([200.0]), S.DEF)[0]


def test_segs_cross():
    assert S.segs_cross((0, 0), (10, 10), (0, 10), (10, 0))
    assert not S.segs_cross((0, 0), (10, 0), (0, 5), (10, 5))


def test_card_numbers_the_course():
    d, card, true_g = synth()
    sol = S.solve(d, card)
    assert [(t, g) for t, g in sol["holes"]] == [(i, true_g[i]) for i in range(9)]
    assert min(S.margins(sol)) > 0


def test_each_green_and_tee_once_and_fix():
    d, card, true_g = synth()
    sol = S.solve(d, None, fix={0: 3})              # golfer: "the first tee is tee 3"
    hs = sol["holes"]
    assert hs[0][0] == 3
    gs = [g for t, g in hs if g >= 0]
    ts = [t for t, g in hs if t >= 0]
    assert len(set(gs)) == len(gs) and len(set(ts)) == len(ts)


def test_missing_green_keeps_the_numbering():
    d, card, true_g = synth()
    gone = true_g[4]                                # hole 5's green was not detected
    d["sc"]["ph"] = np.where(d["hp"][:, 1] == gone, 1e-6, d["sc"]["ph"])
    d["co"]["Gp"][gone] = 0.03
    sol = S.solve(d, card)
    hs = sol["holes"]
    assert all(hs[i] == (i, true_g[i]) for i in range(9) if i != 4)
