"""Kernel timings, C vs the numpy reference, on Yorba Linda-sized arrays (the fast-path NAIP grid is 4 x 4607 x 1565
at 0.6 m; the year scoring runs at 2.4 m). python3 course_data/platform/fastc/imaging/bench.py"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "imagery")]
import fastimg  # noqa: E402
import naip_years as NY  # noqa: E402
from test_fastimg import _scene  # noqa: E402


def t(f, k=5):
    f()
    t0 = time.perf_counter()
    for _ in range(k):
        f()
    return 1000 * (time.perf_counter() - t0) / k


def row(name, fc, fp):
    c, p = t(fc), t(fp)
    print(f"{name:42s} C {c:8.2f} ms   numpy {p:8.2f} ms   x{p / c:5.1f}")


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    H, W = 4607, 1565
    src = (rng.random((4, H, 900)) < 0.9) * rng.integers(1, 256, (4, H, 900))
    src = src.astype(np.uint8)
    dst = np.zeros((4, H, W), np.uint8)
    row("paste first, 4 x 4607 x 900 into 4607 x 1565", lambda: fastimg.paste(dst.copy(), src, 0, 600),
        lambda: fastimg.paste_py(dst.copy(), src, 0, 600))
    for name, (h, w) in (("metrics 2.4 m (1152 x 392, 18 greens)", (1152, 392)),
                         ("metrics 0.6 m (4607 x 1565, 18 greens)", (4607, 1565))):
        a, v, tu, lab, n = _scene(1, H=h, W=w, n_greens=18)
        row(name, lambda: fastimg.metrics(a, v, tu, lab, n), lambda: NY.metrics(a, v, tu, lab, n))
    acc = (rng.random((2900, 1000)) * 30).astype(np.float32)
    acc[rng.random(acc.shape) < 0.3] = np.nan
    tmp = (rng.random(acc.shape) * 30).astype(np.float32)
    row("canopy merge, 2900 x 1000", lambda: fastimg.chm_merge(acc.copy(), tmp), lambda: fastimg.chm_merge_py(acc.copy(), tmp))
    row("canopy quantize, 2900 x 1000", lambda: fastimg.chm_quantize(acc), lambda: fastimg.chm_quantize_py(acc))
