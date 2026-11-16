"""The segment U-Net forward pass in float32 without im2col (conv32.c): the fast path where AMX is missing.

    import unet, unet_fast
    net = unet.UNet(W, impl="c")                    # folds BN (the reference)
    if unet_fast.available():
        fast = unet_fast.FastUNet(net)              # packs the folded weights for the micro-kernel
        logits = fast(x)                            # x (4, H, W) float32, H, W % 32 == 0 (else net(x))

NHWC activations, implicit-GEMM convolutions with bias / residual / ReLU fused, no OpenBLAS and no im2col. Same
float32 maths as unet.py, summed in another order with FMA: test_fastperc.py bounds the difference.
FASTPERC_IMPL=fp32 forces it on an AMX machine (fastscene.unet_net).
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "conv32.c")
FLAGS = ["-O3", "-march=native", "-ffp-contract=fast", "-fopenmp", "-shared", "-fPIC"]
_L = [None, None]


def lib():
    if _L[0] is not None or _L[1] is not None:
        return _L[0]
    try:
        h = hashlib.sha1(open(SRC, "rb").read() + " ".join(FLAGS).encode() + platform.machine().encode()).hexdigest()[:12]
        bdir = os.environ.get("FASTPERC_BUILD") or os.path.join(HERE, "_build")
        os.makedirs(bdir, exist_ok=True)
        so = os.path.join(bdir, f"conv32_{h}.so")
        if not os.path.exists(so):
            tmp = so + f".{os.getpid()}.tmp"
            subprocess.run([os.environ.get("CC", "gcc"), *FLAGS, SRC, "-o", tmp], check=True, capture_output=True)
            os.replace(tmp, so)
        os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")
        L = ctypes.CDLL(so)
        P, l, i = ctypes.c_void_p, ctypes.c_long, ctypes.c_int
        L.fc_vl.restype = i
        L.fc_conv.argtypes = [P, l, l, l, i, i, i, P, P, l, l, l, P, i, P, i]
        L.fc_hwc_pad.argtypes = [P, l, l, l, i, P]
        L.fc_maxpool.argtypes = [P, l, l, l, P]
        L.fc_upcat.argtypes = [P, l, l, l, P, l, P]
        _L[0] = L
    except Exception as ex:                                          # noqa: BLE001
        _L[1] = repr(ex)
    return _L[0]


def available():
    return lib() is not None


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


class FastUNet:
    def __init__(self, net):
        import unet
        self.ref = net
        self.L = lib()
        self.VL = VL = self.L.fc_vl()
        rnd = lambda c: -(-c // VL) * VL                             # noqa: E731
        self.P = {}
        for name, (wm, b, shp) in net.L.items():
            O, C, k, _ = shp
            Op, Cp = rnd(O), (C if name == "stem" else rnd(C))
            nv = 2 if Op % (2 * VL) == 0 else 1
            W = np.zeros((Op, Cp, k * k), np.float32)
            W[:O, :C] = wm.reshape(O, C, k * k)
            W = np.ascontiguousarray(W.reshape(Op // (nv * VL), nv * VL, Cp, k * k).transpose(0, 3, 2, 1))
            bp = np.zeros(Op, np.float32)
            bp[:O] = b
            self.P[name] = (W, bp, Op, Cp, shp)
        self.blocks = unet.BLOCKS
        self._bufs = {}

    def buf(self, key, shape):
        b = self._bufs.get(key)
        if b is None or b.shape != tuple(shape):
            b = self._bufs[key] = np.empty(shape, np.float32)
        return b

    def supports(self, x):
        return x.ndim == 3 and x.shape[0] == 4 and x.shape[1] % 32 == 0 and x.shape[2] % 32 == 0

    def _conv(self, xb, H, W, name, stride=1, relu=True, res=None, pad_in=1, border=1):
        wp, bp, Op, Cp, shp = self.P[name]
        k = shp[2]
        p = k // 2
        assert xb.shape[2] == Cp, (name, xb.shape, Cp)
        Ho, Wo = (H + 2 * p - k) // stride + 1, (W + 2 * p - k) // stride + 1
        out = self.buf(name, (Ho + 2 * border, Wo + 2 * border, Op))
        r = self.L.fc_conv(_p(xb), xb.shape[0], xb.shape[1], Cp, k, stride, pad_in - p, _p(wp), _p(bp), Op, Ho, Wo,
                           _p(out), border, None if res is None else _p(res), int(relu))
        if r:
            raise RuntimeError(f"fc_conv {name}: {r}")
        return out, Ho, Wo

    def __call__(self, x):
        x = np.ascontiguousarray(x, np.float32)
        if not self.supports(x):
            return self.ref(x)
        L = self.L
        C, H, W = x.shape
        xp = self.buf("xp", (H + 6, W + 6, C))
        L.fc_hwc_pad(_p(x), C, H, W, 3, _p(xp))
        f1, h, w = self._conv(xp, H, W, "stem", 2, pad_in=3)
        Hm, Wm = (h - 1) // 2 + 1, (w - 1) // 2 + 1
        cur = self.buf("pool", (Hm + 2, Wm + 2, f1.shape[2]))
        L.fc_maxpool(_p(f1), h, w, f1.shape[2], _p(cur))
        feats = [(f1, h, w)]
        h, w = Hm, Wm
        for s, nb in enumerate(self.blocks):
            for b in range(nb):
                p = f"encoder.layer{s + 1}.{b}"
                st = 2 if (b == 0 and s > 0) else 1
                idn = self._conv(cur, h, w, p + ".ds", st, relu=False)[0] if p + ".ds" in self.P else cur
                t, h2, w2 = self._conv(cur, h, w, p + ".1", st)
                cur, h, w = self._conv(t, h2, w2, p + ".2", 1, relu=True, res=idn)
            feats.append((cur, h, w))
        skips = [feats[3], feats[2], feats[1], feats[0], None]
        for i, sk in enumerate(skips):
            Cx = cur.shape[2]
            Cs = 0 if sk is None else sk[0].shape[2]
            up = self.buf(f"up{i}", (2 * h + 2, 2 * w + 2, Cx + Cs))
            L.fc_upcat(_p(cur), h, w, Cx, None if sk is None else _p(sk[0]), Cs, _p(up))
            h, w = 2 * h, 2 * w
            cur, h, w = self._conv(up, h, w, f"decoder.blocks.{i}.1")
            cur, h, w = self._conv(cur, h, w, f"decoder.blocks.{i}.2")
        y, h, w = self._conv(cur, h, w, "head", relu=False, border=0)
        n = self.P["head"][4][0]
        return np.ascontiguousarray(y[:, :, :n].transpose(2, 0, 1))
