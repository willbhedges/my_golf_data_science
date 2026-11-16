"""C kernels == numpy references (exact). python3 -m pytest -q course_data/platform/fastc/imaging/test_fastimg.py"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "imagery")]
import fastimg  # noqa: E402
import naip_years as NY  # noqa: E402

pytestmark = pytest.mark.skipif(not fastimg.available(), reason="kernel.c did not build: " + str(fastimg._L[1]))


def _scene(seed, H=180, W=140, n_greens=6, nodata_frac=0.1, turf_frac=0.4):
    """a synthetic NAIP year: turf-ish and soil-ish pixels, a nodata margin, labelled greens of 0-60 px"""
    rng = np.random.default_rng(seed)
    a = np.empty((4, H, W), np.uint8)
    green = rng.random((H, W)) < 0.5
    a[0] = np.where(green, rng.integers(40, 120, (H, W)), rng.integers(90, 255, (H, W)))
    a[1] = np.where(green, rng.integers(70, 160, (H, W)), rng.integers(90, 255, (H, W)))
    a[2] = rng.integers(30, 256, (H, W))
    a[3] = np.where(green, rng.integers(120, 256, (H, W)), rng.integers(20, 140, (H, W)))
    a[:, : int(H * nodata_frac)] = 0                              # outside the flight
    a[:, :, -3:] = rng.integers(0, 2, (4, H, min(W, 3)))           # near-zero values at an edge
    valid = a[:3].astype(np.int32).sum(0) > 0
    turf = rng.random((H, W)) < turf_frac
    lab = np.zeros((H, W), np.int32)
    for i in range(n_greens):
        r, c = rng.integers(0, max(H - 10, 1)), rng.integers(0, max(W - 10, 1))
        h, w = rng.integers(0, 9), rng.integers(0, 9)
        lab[r:r + h, c:c + w] = i + 1
    return a, valid, turf, lab, n_greens


@pytest.mark.parametrize("seed", range(12))
def test_metrics_equal_numpy(seed):
    a, valid, turf, lab, n = _scene(seed, turf_frac=[0.4, 0.001, 0.0][seed % 3])   # every 3rd: the < 200 px fallback
    assert fastimg.metrics(a, valid, turf, lab, n) == NY.metrics(a, valid, turf, lab, n)


def test_metrics_edge_cases():
    a, valid, turf, lab, n = _scene(99, H=40, W=40)
    for v, t in ((np.zeros_like(valid), turf), (valid, np.zeros_like(turf)), (np.ones_like(valid), np.ones_like(turf))):
        assert fastimg.metrics(a, v, t, lab, n) == NY.metrics(a, v, t, lab, n)
    z = np.zeros_like(a)                                           # an empty year
    assert fastimg.metrics(z, z[0] > 0, turf, lab, n) == NY.metrics(z, z[0] > 0, turf, lab, n)
    assert fastimg.metrics(a, valid, turf, np.zeros_like(lab), 0) == NY.metrics(a, valid, turf, np.zeros_like(lab), 0)
    for H, W in ((1, 201), (2, 101), (1, 1)):                     # odd / even counts, one pixel
        b, vb, tb, lb, nb = _scene(7, H=H, W=W, nodata_frac=0.0, n_greens=1)
        tb[:] = True
        assert fastimg.metrics(b, vb, tb, lb, nb) == NY.metrics(b, vb, tb, lb, nb)


def test_metrics_real_naip():
    """the Yorba Linda / Chevy Chase NAIP products of the fast-path cache, when present (2.4 m and 0.6 m)"""
    import glob
    import rasterio
    paths = sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(HERE)), "fastpath", "cache", "packages",
                                          "*", "imagery", "naip_rgb.tif")))[:3]
    if not paths:
        pytest.skip("no cached NAIP")
    rng = np.random.default_rng(1)
    for p in paths:
        with rasterio.open(p) as s, rasterio.open(p.replace("naip_rgb", "naip_nir")) as sn:
            a = np.concatenate([s.read(), sn.read()])
        for k in (4, 1):
            x = np.ascontiguousarray(a[:, ::k, ::k])
            valid = x[:3].astype(np.int32).sum(0) > 0
            turf = (x[3].astype(np.int32) - x[0] > 30) & (rng.random(x.shape[1:]) < 0.7)
            lab = np.zeros(x.shape[1:], np.int32)
            for i in range(12):
                r, c = rng.integers(0, x.shape[1] - 40), rng.integers(0, x.shape[2] - 40)
                lab[r:r + rng.integers(3, 40), c:c + rng.integers(3, 40)] = i + 1
            assert fastimg.metrics(x, valid, turf, lab, 12) == NY.metrics(x, valid, turf, lab, 12)


@pytest.mark.parametrize("mode", ["first", "last"])
def test_paste_equal_numpy(mode):
    rng = np.random.default_rng(3)
    base = (rng.random((4, 300, 260)) < 0.5) * rng.integers(0, 256, (4, 300, 260))
    for r0, c0, h, w in ((0, 0, 300, 260), (17, 33, 100, 200), (299, 259, 1, 1), (5, 0, 0, 10)):
        src = rng.integers(0, 3, (4, h, w)).astype(np.uint8) * rng.integers(0, 256, (4, h, w)).astype(np.uint8)
        d1 = base.astype(np.uint8)
        d2 = d1.copy()
        fastimg.paste(d1, src, r0, c0, mode)
        fastimg.paste_py(d2, src, r0, c0, mode)
        assert np.array_equal(d1, d2)
    big = np.zeros((4, 1200, 1100), np.uint8)                      # the OpenMP path
    src = rng.integers(0, 256, (4, 1100, 1000)).astype(np.uint8)
    d2 = big.copy()
    fastimg.paste(big, src, 50, 60, mode)
    fastimg.paste_py(d2, src, 50, 60, mode)
    assert np.array_equal(big, d2)
    with pytest.raises(ValueError):
        fastimg.paste(big, src, 200, 200, mode)                    # does not fit


def test_chm_equal_numpy():
    rng = np.random.default_rng(5)
    for shape in ((300, 200), (1600, 1500)):
        acc = (rng.random(shape) * 40 - 2).astype(np.float32)
        acc[rng.random(shape) < 0.3] = np.nan
        acc.flat[:6] = [0.5, 1.5, 2.5, -0.5, 254.5, np.inf]       # round half to even, clip, inf
        tmp = (rng.random(shape) * 300).astype(np.float32)
        tmp[rng.random(shape) < 0.5] = np.nan
        a1, a2 = acc.copy(), acc.copy()
        fastimg.chm_merge(a1, tmp)
        fastimg.chm_merge_py(a2, tmp)
        assert np.array_equal(a1, a2, equal_nan=True)
        assert np.array_equal(fastimg.chm_quantize(a1), fastimg.chm_quantize_py(a2))
