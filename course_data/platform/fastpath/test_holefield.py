import gzip
import io
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import holefield as HF  # noqa: E402

REF = os.path.join(HERE, "..", "..", "research", "artifacts", "holefield_v1", "46096963743",
                   "research-holefield_export.py-0", "holefield_ref.npz.gz")


def test_numpy_forward_matches_the_trained_network():
    """holefield.forward (numpy, batch norms folded, float16 weights) against the torch fit's own output"""
    W = HF.weights(HF.WEIGHTS)
    R = np.load(io.BytesIO(gzip.open(REF).read()))
    o = HF.forward(R["x"].astype(np.float32), W)
    assert o.shape == R["y"].shape
    assert float(np.abs(o - R["y"]).mean()) < 0.01 and float(np.corrcoef(o.ravel(), R["y"].ravel())[0, 1]) > 0.9999


def test_up2_is_torch_bilinear():
    a = np.arange(8, dtype=np.float32).reshape(1, 2, 4)
    assert np.allclose(HF._up2(a)[0, 0], [0, 0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3])


def test_pair_features_prefer_the_pair_the_field_runs_along():
    F = np.zeros((2, 64, 64), np.float32)
    F[0, 30:34, 10:50] = 1.0                                   # a field running east along row ~32

    class PJ:
        pass
    d = dict(co=dict(pj=PJ(), G=[np.array([48.0, 32.0]), np.array([32.0, 60.0])],
                     T=[dict(pts=[np.array([12.0, 32.0])]), dict(pts=[np.array([32.0, 5.0])])]),
             geo=dict(Tc=[np.array([12.0, 32.0]), np.array([32.0, 5.0])]), hp=[(0, 0), (1, 0), (0, 1), (1, 1)])
    X = HF._pair_features(F, lambda xy: np.asarray(xy, float), d)
    assert X.shape == (4, len(HF.XF4))
    assert X[0, 0] > 0.9 and X[1, 0] < 0.3                     # tee 0 -> green 0 follows the field
    assert X[0, 3] == 0 and X[1, 3] == 1 and X[0, 2] == 0 and X[1, 2] < 0
