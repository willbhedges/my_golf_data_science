"""The segment U-Net forward pass on Intel AMX (amx.c): bf16 weights and activations, float32 accumulation.

    import unet, unet_amx
    net = unet.UNet(W, impl="c")                    # folds BN (the float32 reference)
    if unet_amx.available():
        fast = unet_amx.AmxUNet(net)                # packs the folded weights to bf16 tiles
        logits = fast(x)                            # x (4, H, W) float32; W % 512 == 0, H % 32 == 0, else net(x)

Not bit-exact: weights and activations are rounded to bf16 (8-bit mantissa) between layers; the sums are float32.
test_fastperc.py bounds the difference to the float32 pass (logits and softmax probabilities); the held-out
detection benchmark (fastpath/perc_bench.py) is the accuracy gate (NOTES_PERCEPTION.md). FASTPERC_AMX=0 turns it
off (GOLF_FASTC=0 too, in fastscene).
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "amx.c")
FLAGS = ["-O3", "-march=native", "-mamx-tile", "-mamx-bf16", "-mavx512bf16", "-mavx512bw", "-fopenmp", "-shared",
         "-fPIC"]
_L = [None, None]          # lib, error


def _cpu_has_amx():
    try:
        flags = open("/proc/cpuinfo").read()
    except OSError:
        return False
    return all(f in flags for f in ("amx_tile", "amx_bf16", "avx512_bf16", "avx512bw"))


def lib():
    """the compiled amx.c (None when this CPU / kernel has no usable AMX)"""
    if _L[0] is not None or _L[1] is not None:
        return _L[0]
    try:
        if platform.machine() != "x86_64" or not _cpu_has_amx():
            raise RuntimeError("no AMX on this CPU")
        h = hashlib.sha1(open(SRC, "rb").read() + " ".join(FLAGS).encode()).hexdigest()[:12]
        bdir = os.environ.get("FASTPERC_BUILD") or os.path.join(HERE, "_build")
        os.makedirs(bdir, exist_ok=True)
        so = os.path.join(bdir, f"amx_{h}.so")
        if not os.path.exists(so):
            tmp = so + f".{os.getpid()}.tmp"
            subprocess.run([os.environ.get("CC", "gcc"), *FLAGS, SRC, "-o", tmp], check=True, capture_output=True)
            os.replace(tmp, so)
        os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")
        L = ctypes.CDLL(so)
        P, l, i = ctypes.c_void_p, ctypes.c_long, ctypes.c_int
        L.fa_init.restype = i
        L.fa_conv.argtypes = [P, l, l, l, i, i, i, P, P, l, l, l, P, i, i, P, i]
        L.fa_stem_patch.argtypes = [P, l, l, l, l, P]
        L.fa_hwc_pad.argtypes = [P, l, l, l, i, P]
        L.fa_maxpool.argtypes = [P, l, l, l, P]
        L.fa_upcat.argtypes = [P, l, l, l, P, l, P]
        if L.fa_init() != 0:
            raise RuntimeError("AMX tile state not granted")
        _L[0] = L
    except Exception as ex:                                          # noqa: BLE001
        _L[1] = repr(ex)
    return _L[0]


def available():
    return os.environ.get("FASTPERC_AMX", "1") != "0" and lib() is not None


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


def to_bf16(a):
    """float32 -> bf16 bits (uint16), round to nearest even"""
    u = np.ascontiguousarray(a, np.float32).view(np.uint32).astype(np.uint64)
    return ((u + 0x7FFF + ((u >> 16) & 1)) >> 16).astype(np.uint16)


def from_bf16(b):
    return (b.astype(np.uint32) << 16).view(np.float32)


def cpad(c):
    return 16 if c <= 16 else -(-c // 32) * 32


def pack(w4, b):
    """w4 (O, C, k, k) float32 (BN folded), b (O,) -> (bf16 VNNI blocks [Op/16][k*k][Cp/kc][kc/2][16][2], bias Op)"""
    O, C, k, _ = w4.shape
    Op, Cp = cpad(O), cpad(C)
    kc = 32 if Cp >= 32 else 16
    W = np.zeros((Op, Cp, k * k), np.float32)
    W[:O, :C] = w4.reshape(O, C, k * k)
    W = W.reshape(Op // 16, 16, Cp // kc, kc // 2, 2, k * k).transpose(0, 5, 2, 3, 1, 4)
    bp = np.zeros(Op, np.float32)
    bp[:O] = b
    return np.ascontiguousarray(to_bf16(W)), bp, Op, Cp


class AmxUNet:
    STEM_K = 224                 # 7 x 7 x 4 = 196 patch values, padded to 7 chunks of 32

    def __init__(self, net):
        import unet
        self.ref = net
        self.P = {}
        for name, (wm, b, shp) in net.L.items():
            w4 = wm.reshape(shp)
            if name == "stem":                      # as a 1 x 1 conv over (ky, kx, c)-ordered patches
                O, C, k, _ = shp
                w = np.zeros((O, self.STEM_K), np.float32)
                w[:, :C * k * k] = w4.transpose(0, 2, 3, 1).reshape(O, -1)
                w4 = w.reshape(O, self.STEM_K, 1, 1)
            self.P[name] = pack(w4, b) + (shp,)
        self.blocks, self.width, self.decoder = unet.BLOCKS, unet.WIDTH, unet.DECODER
        self.L = lib()
        self._bufs = {}

    def buf(self, key, shape, dt=np.uint16):
        """a work buffer reused across calls (fresh large allocations cost page faults on every tile)"""
        b = self._bufs.get(key)
        if b is None or b.shape != tuple(shape) or b.dtype != dt:
            b = self._bufs[key] = np.empty(shape, dt)
        return b

    def supports(self, x):
        return x.ndim == 3 and x.shape[0] == 4 and x.shape[2] % 512 == 0 and x.shape[1] % 32 == 0

    def _conv(self, xb, H, W, name, stride=1, relu=True, res=None, out_f32=False, pad_in=1):
        """xb: padded (pad_in) bf16 (H + 2 pad_in, W + 2 pad_in, Cp) -> padded bf16 (Ho + 2, Wo + 2, Op)"""
        wp, bp, Op, Cp, shp = self.P[name]
        k = shp[2] if name != "stem" else 1
        p = k // 2
        assert xb.shape[2] == Cp, (name, xb.shape, Cp)
        Ho, Wo = (H + 2 * p - k) // stride + 1, (W + 2 * p - k) // stride + 1
        if out_f32:
            out = self.buf(name, (Ho, Wo, Op), np.float32)
        else:
            out = self.buf(name, (Ho + 2, Wo + 2, Op))
        r = self.L.fa_conv(_p(xb), xb.shape[0], xb.shape[1], Cp, k, stride, pad_in - p, _p(wp), _p(bp), Op, Ho, Wo,
                           _p(out), 0 if out_f32 else 1, int(out_f32), None if res is None else _p(res), int(relu))
        if r:
            raise RuntimeError(f"fa_conv {name}: {r}")
        return out, Ho, Wo

    def __call__(self, x):
        x = np.ascontiguousarray(x, np.float32)
        if not self.supports(x):
            return self.ref(x)
        L = self.L
        C, H, W = x.shape
        Hs, Ws = (H - 1) // 2 + 1, (W - 1) // 2 + 1
        patch = self.buf("patch", (Hs, Ws, self.STEM_K))
        xp = self.buf("xp", (H + 6, W + 6, C))
        L.fa_hwc_pad(_p(x), C, H, W, 3, _p(xp))
        L.fa_stem_patch(_p(xp), C, H, W, self.STEM_K, _p(patch))
        f1, h, w = self._conv(patch, Hs, Ws, "stem", 1, pad_in=0)
        Hm, Wm = (h - 1) // 2 + 1, (w - 1) // 2 + 1
        cur = self.buf("pool", (Hm + 2, Wm + 2, f1.shape[2]))
        L.fa_maxpool(_p(f1), h, w, f1.shape[2], _p(cur))
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
            L.fa_upcat(_p(cur), h, w, Cx, None if sk is None else _p(sk[0]), Cs, _p(up))
            h, w = 2 * h, 2 * w
            cur, h, w = self._conv(up, h, w, f"decoder.blocks.{i}.1")
            cur, h, w = self._conv(cur, h, w, f"decoder.blocks.{i}.2")
        y, h, w = self._conv(cur, h, w, "head", relu=False, out_f32=True)
        n = self.P["head"][4][0]
        return np.ascontiguousarray(y[:, :, :n].transpose(2, 0, 1))
