"""The segment U-Net (segmentation_models_pytorch Unet, ResNet-34 encoder, 4 bands in, 6 classes out) without torch.

The fast path has no torch (download.pytorch.org is not reachable and the PyPI wheel pulls GBs of CUDA wheels), so
the forward pass is written out here: BatchNorm folded into the convolutions, every convolution an im2col + one
SGEMM (numpy's OpenBLAS: ~300 GFLOP/s on this 4-CPU box), ReLU / residual / max-pool / nearest up-sampling as
plain array code. impl="c" runs im2col, the epilogues, the pool and the up-sampling in kernel.c (fp_im2col,
fp_bias_act, fp_maxpool3s2, fp_up2); the GEMMs stay in OpenBLAS in both paths (C buys nothing over it).

    W = load_safetensors(path)                      # state dict (smp / torchvision key names), fp16 or fp32
    net = UNet(W)                                   # folds BN
    logits = net(x)                                 # x (4, H, W) float32, already (x - mean) / std; H, W % 32 == 0
    P = predict_raster(net, img)                    # (6, H, W) softmax probabilities, 512 px tiles, sin^2 blending

Weights: course_data/segment/model_card (ariadgolf/golf-course-segmentation, Hugging Face) or our own
segment_train.yml artifact "golfseg-own-model". Neither is reachable from this container yet (NOTES_PERCEPTION.md);
test_fastperc.py checks the C path against this numpy path on random weights.
"""
from __future__ import annotations

import json
import struct

import numpy as np

CLASSES = ["background", "green", "tee", "fairway", "bunker", "water"]
MEAN = [108.314, 118.389, 97.68, 158.925]
STD = [42.693, 38.205, 33.022, 51.632]
TILE, STRIDE = 512, 384
BLOCKS = (3, 4, 6, 3)                      # resnet34 BasicBlocks per stage
WIDTH = (64, 128, 256, 512)
DECODER = (256, 128, 64, 32, 16)
EPS = 1e-5


def load_safetensors(path):
    """safetensors file -> {name: float32 array} (the format: u64 header length, JSON header, raw little-endian)."""
    dt = {"F16": np.float16, "F32": np.float32, "BF16": None, "F64": np.float64, "I64": np.int64}
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        head = json.loads(fh.read(n))
        buf = fh.read()
    out = {}
    for k, v in head.items():
        if k == "__metadata__":
            continue
        a, b = v["data_offsets"]
        if v["dtype"] == "BF16":
            raw = np.frombuffer(buf[a:b], np.uint16).astype(np.uint32) << 16
            arr = raw.view(np.float32)
        else:
            arr = np.frombuffer(buf[a:b], dt[v["dtype"]])
        out[k] = arr.reshape(v["shape"]).astype(np.float32)
    return out


def random_weights(seed=0, in_ch=4, classes=6):
    """A full state dict with the real shapes (tests)."""
    rng = np.random.default_rng(seed)
    W = {}

    def conv(name, o, i, k, bias=False):
        W[name + ".weight"] = (rng.normal(0, 1, (o, i, k, k)) * np.sqrt(2.0 / (i * k * k))).astype(np.float32)
        if bias:
            W[name + ".bias"] = rng.normal(0, 0.1, o).astype(np.float32)

    def bn(name, c):
        W[name + ".weight"] = rng.uniform(0.5, 1.5, c).astype(np.float32)
        W[name + ".bias"] = rng.normal(0, 0.1, c).astype(np.float32)
        W[name + ".running_mean"] = rng.normal(0, 0.1, c).astype(np.float32)
        W[name + ".running_var"] = rng.uniform(0.5, 1.5, c).astype(np.float32)
    conv("encoder.conv1", 64, in_ch, 7)
    bn("encoder.bn1", 64)
    cin = 64
    for s, (nb, w) in enumerate(zip(BLOCKS, WIDTH)):
        for b in range(nb):
            p = f"encoder.layer{s + 1}.{b}"
            conv(p + ".conv1", w, cin, 3)
            bn(p + ".bn1", w)
            conv(p + ".conv2", w, w, 3)
            bn(p + ".bn2", w)
            if b == 0 and s > 0:
                conv(p + ".downsample.0", w, cin, 1)
                bn(p + ".downsample.1", w)
            cin = w
    skips = (256, 128, 64, 64, 0)
    cin = 512
    for i, (o, sk) in enumerate(zip(DECODER, skips)):
        p = f"decoder.blocks.{i}"
        conv(p + ".conv1.0", o, cin + sk, 3)
        bn(p + ".conv1.1", o)
        conv(p + ".conv2.0", o, o, 3)
        bn(p + ".conv2.1", o)
        cin = o
    conv("segmentation_head.0", classes, 16, 3, bias=True)
    return W


def _fold(W, conv, bn):
    w = W[conv + ".weight"]
    if bn is None:
        return w.reshape(w.shape[0], -1).copy(), W.get(conv + ".bias", np.zeros(w.shape[0], np.float32)).copy(), w.shape
    g, b, m, v = (W[bn + "." + k] for k in ("weight", "bias", "running_mean", "running_var"))
    sc = (g / np.sqrt(v + EPS)).astype(np.float32)
    bias = (b - m * sc + sc * W.get(conv + ".bias", 0.0)).astype(np.float32)
    return (w.reshape(w.shape[0], -1) * sc[:, None]).astype(np.float32), bias, w.shape


class UNet:
    def __init__(self, W, impl="py"):
        self.impl = impl
        self.L = {}
        self.L["stem"] = _fold(W, "encoder.conv1", "encoder.bn1")
        for s, nb in enumerate(BLOCKS):
            for b in range(nb):
                p = f"encoder.layer{s + 1}.{b}"
                self.L[p + ".1"] = _fold(W, p + ".conv1", p + ".bn1")
                self.L[p + ".2"] = _fold(W, p + ".conv2", p + ".bn2")
                if p + ".downsample.0.weight" in W:
                    self.L[p + ".ds"] = _fold(W, p + ".downsample.0", p + ".downsample.1")
        for i in range(len(DECODER)):
            p = f"decoder.blocks.{i}"
            self.L[p + ".1"] = _fold(W, p + ".conv1.0", p + ".conv1.1")
            self.L[p + ".2"] = _fold(W, p + ".conv2.0", p + ".conv2.1")
        self.L["head"] = _fold(W, "segmentation_head.0", None)
        self.flops = 0.0

    # ---- primitives (numpy reference / C)
    def conv(self, x, name, stride=1, relu=True, residual=None):
        wm, b, shp = self.L[name]
        k = shp[2]
        pad = k // 2
        C, H, Wd = x.shape
        Ho, Wo = (H + 2 * pad - k) // stride + 1, (Wd + 2 * pad - k) // stride + 1
        cols = im2col(x, k, stride, pad, self.impl) if k > 1 or stride > 1 else x.reshape(C, -1)
        y = wm @ cols                                               # OpenBLAS SGEMM (both paths)
        self.flops += 2.0 * wm.shape[0] * wm.shape[1] * cols.shape[1]
        y = bias_act(y, b, relu, None if residual is None else residual.reshape(residual.shape[0], -1), self.impl)
        return y.reshape(wm.shape[0], Ho, Wo)

    def block(self, x, p, stride):
        idn = self.conv(x, p + ".ds", stride, relu=False) if p + ".ds" in self.L else x
        h = self.conv(x, p + ".1", stride)
        return self.conv(h, p + ".2", 1, relu=True, residual=idn)

    def __call__(self, x):
        x = np.ascontiguousarray(x, np.float32)
        f1 = self.conv(x, "stem", 2)
        h = maxpool3s2(f1, self.impl)
        feats = [f1]
        for s, nb in enumerate(BLOCKS):
            for b in range(nb):
                h = self.block(h, f"encoder.layer{s + 1}.{b}", 2 if (b == 0 and s > 0) else 1)
            feats.append(h)
        skips = [feats[3], feats[2], feats[1], feats[0], None]
        x = feats[4]
        for i, sk in enumerate(skips):
            x = up2(x, self.impl)
            if sk is not None:
                x = np.concatenate([x, sk], 0)
            x = self.conv(x, f"decoder.blocks.{i}.1")
            x = self.conv(x, f"decoder.blocks.{i}.2")
        return self.conv(x, "head", relu=False)


def _lib():
    import fastperc
    return fastperc


def im2col(x, k, stride, pad, impl="py"):
    if impl == "c":
        return _lib().im2col(x, k, stride, pad)
    C, H, W = x.shape
    xp = np.pad(x, ((0, 0), (pad, pad), (pad, pad)))
    v = np.lib.stride_tricks.sliding_window_view(xp, (k, k), axis=(1, 2))[:, ::stride, ::stride]
    Ho, Wo = v.shape[1], v.shape[2]
    return np.ascontiguousarray(v.transpose(0, 3, 4, 1, 2)).reshape(C * k * k, Ho * Wo)


def bias_act(y, b, relu, res, impl="py"):
    if impl == "c":
        return _lib().bias_act(y, b, relu, res)
    y = y + b[:, None]
    if res is not None:
        y = y + res
    return np.maximum(y, 0.0) if relu else y


def maxpool3s2(x, impl="py"):
    if impl == "c":
        return _lib().maxpool3s2(x)
    C, H, W = x.shape
    xp = np.pad(x, ((0, 0), (1, 1), (1, 1)), constant_values=-np.inf)
    v = np.lib.stride_tricks.sliding_window_view(xp, (3, 3), axis=(1, 2))[:, ::2, ::2]
    return v.max(axis=(3, 4)).astype(np.float32)


def up2(x, impl="py"):
    if impl == "c":
        return _lib().up2(x)
    return np.repeat(np.repeat(x, 2, axis=1), 2, axis=2)


def _window(n=TILE):
    w = np.sin(np.pi * (np.arange(n) + 0.5) / n) ** 2
    return (np.outer(w, w) + 1e-3).astype(np.float32)


def _starts(size, tile=TILE, stride=STRIDE):
    if size <= tile:
        return [0]
    s = list(range(0, size - tile, stride))
    return s + [size - tile]


def predict_raster(net, img, keep=None, tta=False, mean=MEAN, std=STD):
    """img (4, H, W) uint8 R,G,B,NIR at 0.6 m -> (6, H, W) float32 probabilities (segment/model.predict_raster
    without torch). keep (H, W) bool: tiles with no kept pixel are skipped (the course outline)."""
    _, H, W = img.shape
    valid = img.any(axis=0)
    ph, pw = max(0, TILE - H), max(0, TILE - W)
    x = np.pad(img, ((0, 0), (0, ph), (0, pw)), mode="reflect") if (ph or pw) else img
    kp = None if keep is None else np.pad(keep, ((0, ph), (0, pw)))
    Hp, Wp = x.shape[1:]
    m = np.asarray(mean, np.float32)[:, None, None]
    s = np.asarray(std, np.float32)[:, None, None]
    acc = np.zeros((len(CLASSES), Hp, Wp), np.float32)
    wsum = np.zeros((Hp, Wp), np.float32)
    win = _window()
    for r in _starts(Hp):
        for c in _starts(Wp):
            t = x[:, r:r + TILE, c:c + TILE]
            if not t.any() or (kp is not None and not kp[r:r + TILE, c:c + TILE].any()):
                continue
            xt = (t.astype(np.float32) - m) / s
            ps = []
            for flip in ((None, 2, 1) if tta else (None,)):
                a = xt if flip is None else np.flip(xt, flip)
                z = net(np.ascontiguousarray(a))
                z = np.exp(z - z.max(0, keepdims=True))
                p = z / z.sum(0, keepdims=True)
                ps.append(p if flip is None else np.flip(p, flip))
            acc[:, r:r + TILE, c:c + TILE] += np.mean(ps, 0) * win
            wsum[r:r + TILE, c:c + TILE] += win
    out = acc / np.maximum(wsum, 1e-6)
    out = out[:, :H, :W]
    out[:, ~valid] = 0.0
    return out
