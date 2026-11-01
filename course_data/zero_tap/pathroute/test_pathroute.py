"""pathroute self-checks on a synthetic 4-hole loop (no benchmark data needed)."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import decode as DC  # noqa: E402


def _toy(n=4):
    # holes laid out on a ring: tee k at angle k, green k at angle k + 0.8; green k is right beside tee k+1
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    R = 300.0
    tc = np.c_[R * np.cos(ang), R * np.sin(ang)]
    gc = np.c_[R * np.cos(ang + 0.8 * 2 * np.pi / n), R * np.sin(ang + 0.8 * 2 * np.pi / n)]
    hp, ph, tp, pt = [], [], [], []
    for t in range(n):
        for g in range(n):
            hp.append((t, g))
            ph.append(0.9 if g == t else 0.02)
            tp.append((g, t))
            pt.append(0.9 if t == (g + 1) % n else 0.02)
    d = dict(kind=9, hp=hp, tp=tp, tees=[{}] * n, greens=[{}] * n, tc=tc, gc=gc)
    pr = dict(hole=np.array(ph), trans=np.array(pt), start=np.where(np.arange(n) == 0, 0.9, 0.05),
              end=np.where(np.arange(n) == n - 1, 0.9, 0.05))
    return d, pr


def test_beam_recovers_loop():
    d, pr = _toy(4)
    H, T, S, E = DC.cost_mats(d, pr, dict(trans=1.0, club=1.0))
    gs, ts, cost, conf = DC.beam_loop(H, T, S, E, 4, np.ones(4, bool), np.ones(4, bool))
    assert gs == [0, 1, 2, 3] and ts == [0, 1, 2, 3]
    assert 0.5 < conf <= 1.0


def test_par_from_len():
    assert DC.par_from_len(180) == 3 and DC.par_from_len(400) == 4 and DC.par_from_len(540) == 5
