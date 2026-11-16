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


def test_comp_stats_exact():
    from scipy import ndimage as ndi
    with FS.perception_ns():
        import geo
    rng = np.random.default_rng(4)
    m = ndi.gaussian_filter(rng.normal(size=(400, 300)), 2) > 0.3
    lab, n = ndi.label(m)
    arr = {k: ndi.gaussian_filter(rng.normal(size=m.shape), 1).astype(np.float32) for k in "abc"}
    arr["a"][rng.random(m.shape) < 0.05] = np.nan
    A, B = geo.comp_stats(lab, n, arr), fastperc.comp_stats(lab, n, arr)
    assert set(A) == set(B) and all(np.array_equal(A[k], B[k], equal_nan=True) for k in A)


def test_scene_c_equals_numpy():
    """the whole perception pass on a stack: C hooks on == GOLF_FASTC=0 (same scene)."""
    import subprocess
    code = ("import sys, json; sys.path[:0] = [%r]; import fastscene as FS, test_fastperc as T; st = T.synthetic_stack(); "
            "import numpy as np; st.a['seg'][0][100:130, 100:140] = 230; st.a['seg'][1][50:60, 200:215] = 200; "
            "sc, D = FS.perceive(st, models={}); print(json.dumps([sc['summary'], [g['centroid'] for g in sc['greens']], "
            "[t['centroid'] for t in sc['tee_complexes']]]))") % FP
    env = dict(os.environ, PYTHONPATH=HERE)
    a = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=dict(env, GOLF_FASTC="1"))
    b = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=dict(env, GOLF_FASTC="0"))
    assert a.returncode == 0, a.stderr[-800:]
    assert a.stdout.strip().splitlines()[-1] == b.stdout.strip().splitlines()[-1]


def test_unet_c_equals_numpy_random_weights():
    import unet
    W = unet.random_weights(3)
    x = np.random.default_rng(1).normal(size=(4, 64, 96)).astype(np.float32)
    a = unet.UNet(W, "py")(x)
    b = unet.UNet(W, "c")(x)
    assert a.shape == (6, 64, 96) and np.abs(a - b).max() <= 1e-4 * np.abs(a).max()   # direct 3x3 convs: float32 order


def test_unet_tiles_and_safetensors(tmp_path):
    """predict_raster blends tiles into probabilities; a fp16 safetensors file round-trips through the loader."""
    import json as _json
    import struct
    import unet
    W = unet.random_weights(4)
    hdr, blobs, off = {}, [], 0
    for k, v in W.items():
        b = v.astype(np.float16).tobytes()
        hdr[k] = dict(dtype="F16", shape=list(v.shape), data_offsets=[off, off + len(b)])
        blobs.append(b)
        off += len(b)
    h = _json.dumps(hdr).encode()
    p = tmp_path / "m.safetensors"
    p.write_bytes(struct.pack("<Q", len(h)) + h + b"".join(blobs))
    W2 = unet.load_safetensors(str(p))
    assert set(W2) == set(W) and all(np.array_equal(W2[k], W[k].astype(np.float16).astype(np.float32)) for k in W)
    img = np.random.default_rng(0).integers(0, 255, (4, 300, 520), dtype=np.uint8)
    net = unet.UNet(W2, "c")
    P = unet.predict_raster(net, img)
    assert P.shape == (6, 300, 520) and np.allclose(P.sum(0), 1.0, atol=1e-4)


def test_unet_dihedral_tta():
    """dihedral() round-trips all 8 symmetries; augs=[0] is the plain prediction (bit-identical); an 8-view TTA of a
    symmetric image is a probability field"""
    import unet
    a = np.random.default_rng(1).random((3, 5, 7))
    for d in range(8):
        assert np.array_equal(unet.dihedral(unet.dihedral(a, d), d, inverse=True), a)
    net = unet.UNet(unet.random_weights(5), "c")
    img = np.random.default_rng(2).integers(0, 255, (4, 200, 260), dtype=np.uint8)
    assert np.array_equal(unet.predict_raster(net, img), unet.predict_raster(net, img, augs=[0]))
    P = unet.predict_raster(net, img, augs=[0, 1, 4, 6])
    assert P.shape == (6, 200, 260) and np.allclose(P.sum(0), 1.0, atol=1e-4)


def test_conv3x3_direct_close_to_gemm():
    rng = np.random.default_rng(6)
    x = rng.normal(size=(20, 70, 90)).astype(np.float32)
    w = rng.normal(size=(11, 20, 3, 3)).astype(np.float32)
    b = rng.normal(size=11).astype(np.float32)
    ref = fastperc.bias_act(w.reshape(11, -1) @ fastperc.im2col(x, 3, 1, 1), b, True).reshape(11, 70, 90)
    out = fastperc.conv3x3(x, w, b, True)
    assert np.abs(out - ref).max() <= 1e-4 * np.abs(ref).max()


def test_dist_to_rings_exact():
    """== structure/scene.py _dist_to_rings (its own Python), points inside / outside / on vertices."""
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "structure", "scene.py")
    spec = importlib.util.spec_from_file_location("structure_scene_t", p)
    S = importlib.util.module_from_spec(spec)
    sys.modules["structure_scene_t"] = S
    spec.loader.exec_module(S)
    rng = np.random.default_rng(8)
    ang = np.sort(rng.uniform(0, 2 * np.pi, 40))
    r1 = np.c_[300 * np.cos(ang), 200 * np.sin(ang)]
    r1 = np.vstack([r1, r1[:1]])
    r2 = np.array([[500.0, 0], [600, 0], [600, 80], [500, 80], [500, 0]])
    rings = [r1, r2]
    pts = np.vstack([rng.uniform(-700, 800, (300, 2)), r1[:5], r2[:3]])
    os.environ["GOLF_FASTC"] = "0"
    ref = [S._dist_to_rings(q, rings) for q in pts]
    os.environ.pop("GOLF_FASTC")
    out = fastperc.dist_to_rings(pts, rings)
    assert np.array_equal(np.asarray(ref, float), out)


def _real_tiles():
    """two 512 px NAIP tiles of a cached package, normalised (None when the cache or the weights are missing)"""
    import unet
    wpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "segment", "models", "golfseg_own",
                         "model.safetensors")
    pk = os.path.join(FP, "cache", "packages", "b20_remsen", "imagery")
    if not (os.path.exists(wpath) and os.path.exists(os.path.join(pk, "naip_rgb.tif"))):
        return None, None
    import rasterio
    with rasterio.open(os.path.join(pk, "naip_rgb.tif")) as d:
        rgb = d.read(window=((0, 768), (0, 1024)))
    with rasterio.open(os.path.join(pk, "naip_nir.tif")) as d:
        nir = d.read(1, window=((0, 768), (0, 1024)))
    img = np.concatenate([rgb[:3], nir[None]], 0).astype(np.float32)
    m = np.asarray(unet.MEAN, np.float32)[:, None, None]
    s = np.asarray(unet.STD, np.float32)[:, None, None]
    x = (img - m) / s
    return unet.UNet(unet.load_safetensors(wpath), "c"), [x[:, :512, :512], x[:, 256:768, 512:1024]]


def _softmax(z):
    e = np.exp(z - z.max(0))
    return e / e.sum(0)


def test_unet_fast_fp32_close_to_numpy():
    """unet_fast (float32 implicit GEMM, FMA, (tap, c) order) == unet.py within float32 rounding: random weights on a
    small input and, when cached, the real weights on NAIP tiles"""
    import unet
    import unet_fast
    if not unet_fast.available():
        pytest.skip("conv32.c did not build: " + str(unet_fast._L[1]))
    W = unet.random_weights(3)
    x = np.random.default_rng(1).normal(size=(4, 64, 96)).astype(np.float32)
    ref = unet.UNet(W, "py")
    a, b = ref(x), unet_fast.FastUNet(ref)(x)
    assert b.shape == (6, 64, 96) and np.abs(a - b).max() <= 1e-4 * np.abs(a).max()
    net, tiles = _real_tiles()
    if net is None:
        return
    fast = unet_fast.FastUNet(net)
    for t in tiles:
        z0, z1 = net(t), fast(t)
        assert np.abs(z0 - z1).max() <= 1e-4 * np.abs(z0).max()
        assert np.abs(_softmax(z0) - _softmax(z1)).max() <= 1e-4


def test_unet_amx_bf16_close_to_float32():
    """unet_amx (bf16 weights / activations, float32 sums) against the float32 pass. Not exact; the bounds hold
    with margin on the real model (seen: mean |dp| 6e-4, max |dp| 0.04, argmax 99.9 %); the accuracy gate is the
    held-out detection benchmark (NOTES_PERCEPTION.md). Random weights: the layout and padding paths."""
    import unet
    import unet_amx
    if not unet_amx.available():
        pytest.skip("no usable AMX: " + str(unet_amx._L[1]))
    ref = unet.UNet(unet.random_weights(3), "c")
    x = np.random.default_rng(1).normal(size=(4, 64, 512)).astype(np.float32)
    z0, z1 = ref(x), unet_amx.AmxUNet(ref)(x)
    assert z1.shape == (6, 64, 512) and (z0.argmax(0) == z1.argmax(0)).mean() > 0.97
    assert np.abs(_softmax(z0) - _softmax(z1)).mean() < 0.01
    y = np.random.default_rng(2).normal(size=(4, 64, 96)).astype(np.float32)    # unsupported width: float32 pass
    assert np.array_equal(unet_amx.AmxUNet(ref)(y), ref(y))
    net, tiles = _real_tiles()
    if net is None:
        return
    amx = unet_amx.AmxUNet(net)
    for t in tiles:
        z0, z1 = net(t), amx(t)
        p0, p1 = _softmax(z0), _softmax(z1)
        assert np.abs(p0 - p1).mean() < 2e-3 and np.abs(p0 - p1).max() < 0.15
        assert (z0.argmax(0) == z1.argmax(0)).mean() > 0.995


def test_unet_net_selection(monkeypatch):
    """fastscene.unet_net: GOLF_FASTC=0 -> unet.py's numpy pass; FASTPERC_IMPL=fp32 -> unet_fast"""
    import unet
    import unet_fast
    wpath = FS.UNET_DEFAULT
    if not os.path.exists(wpath):
        pytest.skip("no U-Net weights")
    monkeypatch.setenv("GOLF_FASTC", "0")
    n = FS.unet_net(wpath)
    assert isinstance(n, unet.UNet) and n.impl == "py"
    monkeypatch.setenv("GOLF_FASTC", "1")
    monkeypatch.setenv("FASTPERC_IMPL", "fp32")
    if unet_fast.available():
        assert isinstance(FS.unet_net(wpath), unet_fast.FastUNet)
