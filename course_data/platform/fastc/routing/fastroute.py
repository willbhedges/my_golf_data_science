"""ctypes front end of kernel.c (the joint router's beam search, zero_tap/joint/solve2.py beam2).

    import fastroute
    fastroute.beam(pr, step, Tm, st, en, price, B, keep)   # == solve2.beam2's numpy loop, identical results

Built on first use: gcc -O3 -march=native -ffp-contract=off -shared -fPIC kernel.c -> _build/kernel_<hash>.so
(FASTROUTE_SO=<file> loads a prebuilt one). available() is False without a compiler; GOLF_FASTC=0 keeps the
numpy reference (solve2 checks both).
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
FLAGS = ["-O3", "-march=native", "-ffp-contract=off", "-shared", "-fPIC"]
_L = [None, None]


def lib():
    if _L[0] is not None or _L[1] is not None:
        return _L[0]
    try:
        so = os.environ.get("FASTROUTE_SO")
        if not so:
            h = hashlib.sha1(open(SRC, "rb").read() + " ".join(FLAGS).encode() + platform.machine().encode()).hexdigest()[:12]
            bdir = os.environ.get("FASTROUTE_BUILD") or os.path.join(HERE, "_build")
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
    P, i, d = ctypes.c_void_p, ctypes.c_int, ctypes.c_double
    L.fr_beam.argtypes = [i, i, i, i, i, P, P, P, P, P, P, P, P, P, d, d, i, P, P]
    L.fr_beam.restype = i
    _L[0] = L
    return L


def enabled():
    return os.environ.get("GOLF_FASTC", "1") != "0" and lib() is not None


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


def beam(N, C, E, B, loop, step, Tm, st, en, gbit, tbit, endi, X, price, reuse, wx, keep):
    """arrays as kernel.c fr_beam documents; reuse None = no tee reuse. -> [(cost, [cand per position])]"""
    L = lib()
    step = np.ascontiguousarray(step, np.float64)
    Tm = np.ascontiguousarray(Tm, np.float64)
    st = np.ascontiguousarray(st, np.float64)
    en = np.ascontiguousarray(en, np.float64)
    gbit = np.ascontiguousarray(gbit, np.uint64)
    tbit = np.ascontiguousarray(tbit, np.uint64)
    endi = np.ascontiguousarray(endi, np.int64)
    X = np.ascontiguousarray(X, np.uint8)
    pz = None if price is None else np.ascontiguousarray(price, np.float64)
    seqs = np.zeros((keep, N), np.int64)
    costs = np.zeros(keep, np.float64)
    n = L.fr_beam(N, C, E, B, loop, _p(step), _p(Tm), _p(st), _p(en), _p(gbit), _p(tbit), _p(endi), _p(X),
                  _p(pz) if pz is not None else None, -1.0 if reuse is None else float(reuse), float(wx), keep,
                  _p(seqs), _p(costs))
    return [(float(costs[q]), [int(v) for v in seqs[q]]) for q in range(n)]
