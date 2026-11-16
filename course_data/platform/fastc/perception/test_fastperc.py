"""C kernels of the fast-path perception (kernel.c) against their numpy / scipy / LightGBM references.

  python3 -m pytest -q course_data/platform/fastc/perception/test_fastperc.py

  features          fastperc.features == fastscene.features_py within FEATURE_TOL x the feature's range (the local
                    std uses E[x^2] - E[x]^2 in both; float32 rounding of the two summation orders differs)
  gbm               fp_gbm / fp_gbm_blocked == LightGBM Booster.predict: max |dp| <= 1e-9 (same tree order,
                    double sums); blocked == row-wise bit for bit
  grey opening      == scipy.ndimage.grey_opening(footprint=disk), exactly (float32 and float64)
  label8            == scipy.ndimage.label(structure 3 x 3), exactly
  predict           fastscene.predict(impl="c") == predict(impl="py") within 1e-6 (cascade on and off)
"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
FP = os.path.join(os.path.dirname(os.path.dirname(HERE)), "fastpath")
sys.path[:0] = [HERE, FP]
import fastperc  # noqa: E402
import fastscene as FS  # noqa: E402


def synthetic_stack(H=260, W=310, seed=3):
    from scipy import ndimage as ndi
    S = FS._perc()
    st = S.synthetic(H, W)
    rng = np.random.default_rng(seed)
    base = ndi.gaussian_filter(rng.normal(size=(H, W)), 6)
    base = (base - base.min()) / (np.ptp(base) + 1e-9)
    for b, (lo, hi) in enumerate(((40, 160), (60, 170), (30, 140), (90, 220))):
        st.a["naip"][b] = np.clip(lo + (hi - lo) * base + rng.normal(0, 8, (H, W)), 0, 255).astype(np.uint8)
    hag = np.clip(ndi.gaussian_filter(rng.normal(size=(H, W)), 3) * 60, 0, 120)
    st.a["hag"] = np.where(rng.random((H, W)) < 0.02, 255, hag).astype(np.uint8)
    z = ndi.gaussian_filter(rng.normal(size=(H, W)).cumsum(0), 4)
    st.a["dtm"] = np.round((z - z.min()) * 100 + 500).astype(np.uint16)
    st.a["dtm"][:5, :7] = 65535
    return st


def test_features_match_reference():
    st = synthetic_stack()
    A = FS.features_py(st)
    B = fastperc.features(st)
    assert A.shape == B.shape
    for k, name in enumerate(FS.FEATURES):
        rng = float(A[k].max() - A[k].min()) or 1.0
        d = float(np.abs(A[k] - B[k]).max())
        assert d <= fastperc.FEATURE_TOL * rng, (name, d, rng)


def _toy_model(tmp_path):
    import lightgbm as lgb
    rng = np.random.default_rng(0)
    X = rng.normal(size=(3000, len(FS.FEATURES))).astype(np.float32)
    y = (np.argmax(X[:, :6] + rng.normal(0, 0.5, (3000, 6)), axis=1)).astype(int)
    b = lgb.train(dict(objective="multiclass", num_class=6, num_leaves=15, verbose=-1, num_threads=1), lgb.Dataset(X, y), 20)
    p = str(tmp_path / "m.txt")
    b.save_model(p)
    return dict(booster=lgb.Booster(model_file=p), path=p), X


def test_gbm_matches_lightgbm(tmp_path):
    m, X = _toy_model(tmp_path)
    ref = m["booster"].predict(X)
    a = fastperc.gbm_predict(m, X, blocked=False)
    b = fastperc.gbm_predict(m, X, blocked=True)
    assert np.abs(a - ref).max() <= 1e-9
    assert np.array_equal(a, b)


def test_predict_c_equals_py(tmp_path):
    m, _ = _toy_model(tmp_path)
    st = synthetic_stack()
    F = FS.features_py(st)
    mask = np.zeros((st.H, st.W), bool)
    mask[20:200, 30:280] = True
    for cascade in (False, True):
        a = FS.predict(m, F, mask, impl="py", cascade=cascade)
        b = FS.predict(m, F, mask, impl="c", cascade=cascade)
        assert np.abs(a - b).max() <= 1e-6


@pytest.mark.parametrize("dt", [np.float32, np.float64])
def test_grey_opening_disk_exact(dt):
    from scipy import ndimage as ndi
    rng = np.random.default_rng(5)
    z = ndi.gaussian_filter(rng.normal(size=(140, 170)).cumsum(1), 2).astype(dt)
    for r in (1, 3, 15):
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        disk = (xx ** 2 + yy ** 2) <= r * r
        assert np.array_equal(ndi.grey_opening(z, footprint=disk), fastperc.grey_opening_disk(z, r))


def test_label8_exact():
    from scipy import ndimage as ndi
    rng = np.random.default_rng(2)
    m = ndi.gaussian_filter(rng.normal(size=(300, 280)), 2) > 0.1
    a, na = ndi.label(m, np.ones((3, 3)))
    b, nb = fastperc.label8(m)
    assert na == nb and np.array_equal(a, b)
