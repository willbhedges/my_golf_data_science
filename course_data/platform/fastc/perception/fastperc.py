"""ctypes front end of kernel.c (fast-path perception kernels). numpy / LightGBM references: fastpath/fastscene.py.

    import fastperc
    F = fastperc.features(st, ref=None)          # == fastscene.features_py(st) within FEATURE_TOL
    P = fastperc.gbm_predict(model, X)           # == model["booster"].predict(X) within GBM_TOL
    lab, n = fastperc.label8(mask)               # == scipy.ndimage.label(mask, np.ones((3, 3))) exactly

Built on first use: gcc -O3 -march=native -ffp-contract=off -fopenmp -shared -fPIC kernel.c -> _build/
kernel_<source hash>_<cpu>.so (FASTPERC_SO=<file> loads a prebuilt one).
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "kernel.c")
FLAGS = ["-O3", "-march=native", "-ffp-contract=off", "-fopenmp", "-shared", "-fPIC"]
FEATURE_TOL = 2e-4          # max abs difference vs the numpy reference, relative to the feature's range
GBM_TOL = 1e-9
_L = [None]


def lib():
    if _L[0] is not None:
        return _L[0]
    so = os.environ.get("FASTPERC_SO")
    if not so:
        h = hashlib.sha1(open(SRC, "rb").read() + " ".join(FLAGS).encode() + platform.machine().encode()).hexdigest()[:12]
        bdir = os.environ.get("FASTPERC_BUILD") or os.path.join(HERE, "_build")
        os.makedirs(bdir, exist_ok=True)
        so = os.path.join(bdir, f"kernel_{h}.so")
        if not os.path.exists(so):
            tmp = so + f".{os.getpid()}.tmp"
            subprocess.run([os.environ.get("CC", "gcc"), *FLAGS, SRC, "-o", tmp, "-lm"], check=True)
            os.replace(tmp, so)
    # libgomp threads spin after each parallel region by default and then steal the cores OpenBLAS's GEMM threads
    # need (U-Net: 0.9 s -> 1.6 s a tile); passive waiting costs nothing measurable in the other kernels
    os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")
    L = ctypes.CDLL(so)
    P = ctypes.c_void_p
    L.fp_features.argtypes = [P, P, P, ctypes.c_long, ctypes.c_long, ctypes.c_float, P, P]
    L.fp_gbm.argtypes = [P, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int, P, P, P, P, P, P, P, P, P]
    L.fp_gbm_blocked.argtypes = L.fp_gbm.argtypes
    L.fp_gather.argtypes = [P, ctypes.c_long, ctypes.c_int, P, ctypes.c_long, P]
    L.fp_label8.argtypes = [P, ctypes.c_long, ctypes.c_long, P]
    L.fp_label8.restype = ctypes.c_long
    L.fp_comp_stats.argtypes = [P, ctypes.c_long, ctypes.c_int, P, ctypes.c_int, P, P, P, P, P, ctypes.c_long]
    L.fp_im2col.argtypes = [P, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int, P]
    L.fp_bias_act.argtypes = [P, P, ctypes.c_long, ctypes.c_long, ctypes.c_int, P]
    L.fp_maxpool3s2.argtypes = [P, ctypes.c_long, ctypes.c_long, ctypes.c_long, P]
    L.fp_up2.argtypes = [P, ctypes.c_long, ctypes.c_long, ctypes.c_long, P]
    L.fp_grey_disk.argtypes = [P, P, ctypes.c_long, ctypes.c_long, ctypes.c_int, ctypes.c_int]
    _L[0] = L
    return L


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


def features(st, ref=None):
    import fastscene as FS
    a = st.a
    naip = np.ascontiguousarray(a["naip"], np.uint8)
    hag = np.ascontiguousarray(a["hag"], np.uint8)
    dtm = np.ascontiguousarray(a["dtm"], np.uint16)
    H, W = hag.shape
    if ref is None:
        n = naip.astype(np.float32)
        hh = hag.astype(np.float32) * 0.25
        hh[hag == 255] = np.nan
        ref = FS.turf_ref(n[0], n[1], n[2], n[3], hh, st.valid())
    r = np.array([ref["ndvi"][0], ref["ndvi"][1], ref["bright"][0], ref["bright"][1], ref["nir"][0], ref["nir"][1],
                  ref["exg"][0], ref["exg"][1]], np.float64)
    ok = dtm != 65535
    zfill = float(np.median(dtm[ok].astype(np.float32) / 100.0)) if ok.any() else 0.0
    if not ok.any():
        dtm = np.zeros_like(dtm)
    out = np.empty((len(FS.FEATURES), H, W), np.float32)
    rc = lib().fp_features(_p(naip), _p(hag), _p(dtm), H, W, ctypes.c_float(zfill), _p(r), _p(out))
    if rc:
        raise MemoryError("fp_features")
    return out


_FLAT = {}


def flatten(model):
    """LightGBM booster -> flat arrays (numerical splits only; refuses anything else)."""
    key = model.get("path") or id(model)
    if key in _FLAT:
        return _FLAT[key]
    d = model["booster"].dump_model()
    K = int(d.get("num_class", 1))
    node_off, leaf_off, feat, thr, left, right, dleft, leaf = [0], [0], [], [], [], [], [], []
    for t in d["tree_info"]:
        nodes, leaves = [], []

        def walk(n):                                  # preorder: internal nodes get indices, leaves their own
            if "leaf_value" in n:
                leaves.append(n["leaf_value"])
                return ~(len(leaves) - 1)
            if n.get("decision_type", "<=") != "<=":
                raise ValueError("non-numerical split")
            i = len(nodes)
            nodes.append(None)
            lch = walk(n["left_child"])
            rch = walk(n["right_child"])
            nodes[i] = (n["split_feature"], float(n["threshold"]), lch, rch, bool(n.get("default_left", True)))
            return i
        root = t["tree_structure"]
        walk(root)
        for f_, th, lc, rc, dl in nodes:
            feat.append(f_)
            thr.append(th)
            left.append(lc)
            right.append(rc)
            dleft.append(1 if dl else 0)
        leaf += leaves
        node_off.append(len(feat))
        leaf_off.append(len(leaf))
    fl = dict(K=K, ntree=len(d["tree_info"]), nf=int(d["max_feature_idx"]) + 1,
              node_off=np.array(node_off, np.int32), leaf_off=np.array(leaf_off, np.int32),
              feat=np.array(feat, np.int32), thr=np.array(thr, np.float64), left=np.array(left, np.int32),
              right=np.array(right, np.int32), dleft=np.array(dleft, np.int8), leaf=np.array(leaf, np.float64))
    if K > 64:
        raise ValueError("too many classes")
    _FLAT[key] = fl
    return fl


def gbm_predict(model, X, blocked=True):
    fl = flatten(model)
    X = np.ascontiguousarray(X, np.float32)
    n, nf = X.shape
    if nf != fl["nf"]:
        raise ValueError(f"{nf} features, model has {fl['nf']}")
    out = np.empty((n, fl["K"]), np.float64)
    fn = lib().fp_gbm_blocked if blocked else lib().fp_gbm
    fn(_p(X), n, nf, fl["ntree"], fl["K"], _p(fl["node_off"]), _p(fl["leaf_off"]), _p(fl["feat"]),
                 _p(fl["thr"]), _p(fl["left"]), _p(fl["right"]), _p(fl["dleft"]), _p(fl["leaf"]), _p(out))
    return out


def gather(F, idx):
    """F (nf, H, W) float32, idx flat pixel indices -> (len(idx), nf) float32 rows."""
    F = np.ascontiguousarray(F, np.float32)
    nf = F.shape[0]
    idx = np.ascontiguousarray(idx, np.int64)
    X = np.empty((len(idx), nf), np.float32)
    lib().fp_gather(_p(F), F[0].size, nf, _p(idx), len(idx), _p(X))
    return X


def label8(mask):
    """8-connected components of a boolean mask, numbered in raster order of first pixel (scipy.ndimage.label
    with a 3x3 structure numbers them the same way) -> (int32 labels, n)."""
    m = np.ascontiguousarray(mask, np.uint8)
    H, W = m.shape
    lab = np.empty((H, W), np.int32)
    n = lib().fp_label8(_p(m), H, W, _p(lab))
    return lab, int(n)


def grey_disk(a, r, op):
    a64 = np.ascontiguousarray(a, np.float64)
    out = np.empty_like(a64)
    lib().fp_grey_disk(_p(a64), _p(out), a64.shape[0], a64.shape[1], int(r), int(op))
    return out.astype(a.dtype, copy=False)


def grey_opening_disk(a, r):
    """== scipy.ndimage.grey_opening(a, footprint=disk(r)) (mode 'reflect'), exactly."""
    return grey_disk(grey_disk(a, r, 0), r, 1)


def comp_stats(lab, n, arrays):
    """== perception geo.comp_stats(lab, n, arrays) (per-label NaN-safe means, area, centroid), bit for bit."""
    lab = np.ascontiguousarray(lab, np.int32)
    H, W = lab.shape
    names = list(arrays)
    k = len(names)
    keep = []
    for nm in names:
        a = np.asarray(arrays[nm])
        if a.dtype != np.float32:
            if a.dtype.kind != "f" or a.dtype.itemsize > 4:
                raise TypeError("float32 planes only (float64 would round)")
            a = a.astype(np.float32)
        keep.append(np.ascontiguousarray(a))
    ptrs = (ctypes.c_void_p * max(k, 1))(*[a.ctypes.data for a in keep])
    cnt, rs, cs = (np.empty(n + 1) for _ in range(3))
    s, m = np.empty((max(k, 1), n + 1)), np.empty((max(k, 1), n + 1))
    lib().fp_comp_stats(_p(lab), H * W, int(n), ptrs, k, _p(cnt), _p(rs), _p(cs), _p(s), _p(m), W)
    out = dict(area_px=cnt[1:].copy())
    with np.errstate(invalid="ignore", divide="ignore"):
        out["r"] = rs[1:] / cnt[1:] if n else np.zeros(0)
        out["c"] = cs[1:] / cnt[1:] if n else np.zeros(0)
        for j, nm in enumerate(names):
            out[nm] = np.where(m[j, 1:] > 0, s[j, 1:] / np.maximum(m[j, 1:], 1), np.nan)
    return out


# ---- U-Net primitives (unet.py impl="c")
def im2col(x, k, s, p):
    x = np.ascontiguousarray(x, np.float32)
    C, H, W = x.shape
    Ho, Wo = (H + 2 * p - k) // s + 1, (W + 2 * p - k) // s + 1
    out = np.empty((C * k * k, Ho * Wo), np.float32)
    lib().fp_im2col(_p(x), C, H, W, k, s, p, _p(out))
    return out


def bias_act(y, b, relu, res=None):
    y = np.ascontiguousarray(y, np.float32)
    b = np.ascontiguousarray(b, np.float32)
    r = None if res is None else np.ascontiguousarray(res, np.float32)
    lib().fp_bias_act(_p(y), _p(b), y.shape[0], y.shape[1], int(bool(relu)), None if r is None else _p(r))
    return y


def maxpool3s2(x):
    x = np.ascontiguousarray(x, np.float32)
    C, H, W = x.shape
    out = np.empty((C, (H - 1) // 2 + 1, (W - 1) // 2 + 1), np.float32)
    lib().fp_maxpool3s2(_p(x), C, H, W, _p(out))
    return out


def up2(x):
    x = np.ascontiguousarray(x, np.float32)
    C, H, W = x.shape
    out = np.empty((C, 2 * H, 2 * W), np.float32)
    lib().fp_up2(_p(x), C, H, W, _p(out))
    return out
