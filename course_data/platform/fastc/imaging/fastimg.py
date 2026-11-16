"""ctypes front end of kernel.c (fast-path imagery kernels, the fetch stage). numpy references live beside each call.

    import fastimg
    fastimg.paste(dst, src, r0, c0, mode="first")   # == paste_py (rasterio.merge 'first' / naip_years 'last valid')
    m = fastimg.metrics(rgbn, valid, turf, labels, n_greens)   # == naip_years.metrics(...) exactly (same dict)
    fastimg.chm_merge(acc, tmp); q = fastimg.chm_quantize(acc)  # == canopy.fetch's numpy lines exactly

Built on first use: gcc -O3 -march=native -ffp-contract=off -fopenmp -shared -fPIC kernel.c -> _build/
kernel_<source hash>.so (FASTIMG_SO=<file> loads a prebuilt one). available() is False when no compiler / the build
fails: the callers (fastpath/fast_imagery.py, canopy.py) then run the numpy reference.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGERY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "imagery")   # naip_years.py
if IMAGERY not in sys.path:
    sys.path.insert(0, IMAGERY)
SRC = os.path.join(HERE, "kernel.c")
FLAGS = ["-O3", "-march=native", "-ffp-contract=off", "-fopenmp", "-shared", "-fPIC"]
_L = [None, None]          # library, build error


def lib():
    if _L[0] is not None or _L[1] is not None:
        return _L[0]
    try:
        so = os.environ.get("FASTIMG_SO")
        if not so:
            h = hashlib.sha1(open(SRC, "rb").read() + " ".join(FLAGS).encode() + platform.machine().encode()).hexdigest()[:12]
            bdir = os.environ.get("FASTIMG_BUILD") or os.path.join(HERE, "_build")
            os.makedirs(bdir, exist_ok=True)
            so = os.path.join(bdir, f"kernel_{h}.so")
            if not os.path.exists(so):
                tmp = so + f".{os.getpid()}.tmp"
                subprocess.run([os.environ.get("CC", "gcc"), *FLAGS, SRC, "-o", tmp, "-lm"], check=True,
                               capture_output=True)
                os.replace(tmp, so)
        L = ctypes.CDLL(so)
    except Exception as e:                                           # noqa: BLE001
        _L[1] = repr(e)[:300]
        return None
    P, lg, i = ctypes.c_void_p, ctypes.c_long, ctypes.c_int
    L.fi_paste_u8.argtypes = [P, lg, lg, P, lg, lg, i, lg, lg, i]
    L.fi_paste_u8.restype = None
    L.fi_metrics.argtypes = [P, P, P, P, P, P, P, lg, i, i, P, P]
    L.fi_metrics.restype = i
    L.fi_chm_merge.argtypes = [P, P, lg]
    L.fi_chm_merge.restype = None
    L.fi_chm_quantize.argtypes = [P, P, lg]
    L.fi_chm_quantize.restype = None
    _L[0] = L
    return L


def available():
    return lib() is not None


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


# ------------------------------------------------------------------------------------------------- paste
def paste_py(dst, src, r0, c0, mode="first"):
    """numpy reference: src (nb, h, w) into dst (nb, H, W) at (r0, c0). first: rasterio.merge(method='first',
    nodata=0) per element; last: np.where(src > 0, src, dst) (naip_years.read_year's item loop)."""
    nb, h, w = src.shape
    cur = dst[:nb, r0:r0 + h, c0:c0 + w]
    m = (cur == 0) & (src != 0) if mode == "first" else src > 0
    cur[m] = src[m]


def paste(dst, src, r0, c0, mode="first"):
    L = lib()
    nb, h, w = src.shape
    if not (dst.dtype == src.dtype == np.uint8 and dst.ndim == 3 and nb <= dst.shape[0] and r0 >= 0 and c0 >= 0
            and r0 + h <= dst.shape[1] and c0 + w <= dst.shape[2]):
        raise ValueError(f"paste: {src.shape} at ({r0}, {c0}) does not fit {dst.shape} (uint8 both)")
    if L is None or not dst.flags.c_contiguous:
        return paste_py(dst, src, r0, c0, mode)
    s = np.ascontiguousarray(src)
    L.fi_paste_u8(_p(dst), dst.shape[1], dst.shape[2], _p(s), h, w, nb, r0, c0, 0 if mode == "first" else 1)


# ------------------------------------------------------------------------------------------------- year metrics
def metrics(rgbn, valid, turf, green_labels, n_greens):
    """naip_years.metrics in C: the same dict, the same numbers (float32 NDVI / excess green, numpy's median and
    'linear' percentile). Falls back to naip_years.metrics without the library."""
    L = lib()
    import naip_years as NY
    if L is None:
        return NY.metrics(rgbn, valid, turf, green_labels, n_greens)
    H, W = rgbn.shape[1:]
    if valid.shape != (H, W) or turf.shape != (H, W) or green_labels.shape != (H, W):
        raise ValueError("metrics: band / mask shapes differ")
    bands = [np.ascontiguousarray(rgbn[k], dtype=np.uint8) for k in range(4)]
    v = np.ascontiguousarray(valid, dtype=np.uint8)
    t = np.ascontiguousarray(turf, dtype=np.uint8)
    lab = np.ascontiguousarray(green_labels, dtype=np.int32)
    out = np.empty(12, np.float64)
    gm = np.empty(max(n_greens, 1), np.float64)
    if L.fi_metrics(*(_p(b) for b in bands), _p(v), _p(t), _p(lab), H * W, int(n_greens), 8, _p(out), _p(gm)):
        raise MemoryError("fi_metrics")
    f = lambda x: None if np.isnan(x) else float(x)                  # noqa: E731
    meds = [f(x) for x in gm[:n_greens]]
    bare = NY.bare_greens(meds)
    known = [x for x in bare if x is not None]
    use_any = bool(out[11])
    tn, te, gn, bt, cl, hz = (f(x) for x in out[:6])
    return dict(
        turf_ndvi=round(tn, 4) if tn is not None else None,
        turf_exg=round(te, 1) if te is not None else None,
        green_ndvi=round(gn, 4) if gn is not None else None,
        bare_turf=round(bt, 4) if bt is not None else None,
        greens_bare=round(sum(known) / len(known), 4) if known else 0.0,
        greens_bare_n=int(sum(known)), greens_n=len(known),
        cloud=round(cl, 4) if use_any else None,
        haze=round(hz, 1) if hz is not None else None,
        turf_rgb=[round(float(x), 1) for x in out[6:9]] if use_any else None,
        turf_px=int(out[9]), turf_source="box (no OSM turf)" if out[10] else "osm")


def score_array(arr, crs, transform, polys, extra):
    """naip_years._score_array with the C metrics (the masks are still rasterised by GDAL)."""
    import naip_years as NY
    valid = arr[:3].astype(np.int32).sum(0) > 0
    turf = np.zeros(arr.shape[1:], bool)
    for tag in NY.TURF_TAGS:
        turf |= NY.rasterize_ll(polys[tag], crs, transform, arr.shape[1:])
    lab = NY.rasterize_ll(polys["green"], crs, transform, arr.shape[1:], labels=True)
    c = dict(extra, has_nir=arr.shape[0] >= 4)
    if c["has_nir"]:
        c.update(metrics(arr, valid, turf, lab, len(polys["green"])))
    return c


# ------------------------------------------------------------------------------------------------- canopy
def chm_merge_py(acc, tmp):
    f = np.isnan(acc) & np.isfinite(tmp)
    acc[f] = tmp[f]


def chm_quantize_py(acc):
    return np.where(np.isfinite(acc), np.clip(np.round(acc), 0, 254), 255).astype(np.uint8)


def chm_merge(acc, tmp):
    L = lib()
    if L is None or acc.dtype != np.float32 or tmp.dtype != np.float32 or acc.shape != tmp.shape \
            or not acc.flags.c_contiguous:
        return chm_merge_py(acc, tmp)
    t = np.ascontiguousarray(tmp)
    L.fi_chm_merge(_p(acc), _p(t), acc.size)


def chm_quantize(acc):
    L = lib()
    if L is None or acc.dtype != np.float32:
        return chm_quantize_py(acc)
    a = np.ascontiguousarray(acc)
    q = np.empty(a.shape, np.uint8)
    L.fi_chm_quantize(_p(a), _p(q), a.size)
    return q
