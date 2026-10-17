"""Tiled inference of the ariadgolf/golf-course-segmentation U-Net on a NAIP RGBN raster (runs on Actions).

Model facts (course_data/segment/model_card/, read from the Hub by probe_model.py):
  U-Net / ResNet-34 (segmentation_models_pytorch, config.json), 4 input bands R,G,B,NIR uint8 at 0.6 m
  ground sample distance, 512 x 512 tiles, normalisation (x - mean) / std with the means/stds below (no /255),
  6 logits: 0 background, 1 green, 2 tee, 3 fairway, 4 bunker, 5 water. FP16 safetensors (49 MB).
  Licence: none specified ("No additional license grant for the model weights is specified"). Labels are
  OSM (ODbL). Research/evaluation use only until Ariad grants a licence (see README.md in this folder).

Large rasters: overlapping 512 px tiles (stride 384), sin^2 blending of softmax probabilities, flip TTA
(identity, horizontal, vertical; as the card's inference.py). Edge tiles are reflect-padded.
"""
from __future__ import annotations

import json
import os

import numpy as np

REPO = "ariadgolf/golf-course-segmentation"
CLASSES = ["background", "green", "tee", "fairway", "bunker", "water"]
MEAN = [108.314, 118.389, 97.68, 158.925]
STD = [42.693, 38.205, 33.022, 51.632]
TILE = 512
STRIDE = 384
GSD_M = 0.6


def load(repo=REPO, revision=None, threads=None):
    """(model, config, sha) on CPU in float32. repo: a Hub id or a local smp save_pretrained folder with
    preprocessor_config.json (our own model from train/train.py)."""
    import segmentation_models_pytorch as smp
    import torch
    if threads:
        torch.set_num_threads(threads)
    if os.path.isdir(repo):
        cfg = json.load(open(os.path.join(repo, "preprocessor_config.json")))
        model = smp.from_pretrained(repo).float().eval()
        import hashlib
        h = hashlib.sha1()
        for f in sorted(os.listdir(repo)):
            if f.endswith((".safetensors", ".json")):
                h.update(open(os.path.join(repo, f), "rb").read())
        return model, cfg, h.hexdigest()
    from huggingface_hub import HfApi, hf_hub_download
    cfg = json.load(open(hf_hub_download(repo, "preprocessor_config.json", revision=revision)))
    assert cfg["image_mean"] == MEAN and cfg["image_std"] == STD and cfg["tile_size"] == TILE, cfg
    model = smp.from_pretrained(repo, revision=revision).float().eval()
    try:
        sha = HfApi().model_info(repo, revision=revision).sha
    except Exception:  # noqa: BLE001  (offline cache)
        sha = revision or "cached"
    return model, cfg, sha


def _window(n=TILE):
    w = np.sin(np.pi * (np.arange(n) + 0.5) / n) ** 2
    return (np.outer(w, w) + 1e-3).astype(np.float32)


def _starts(size, tile=TILE, stride=STRIDE):
    if size <= tile:
        return [0]
    s = list(range(0, size - tile, stride))
    return s + [size - tile]


def predict_raster(model, img, tta=True, log=print, mean=MEAN, std=STD):
    """img: (4, H, W) uint8 R,G,B,NIR at 0.6 m -> (6, H, W) float32 probabilities (0 where no data)."""
    import torch
    _, H, W = img.shape
    valid = img.any(axis=0)
    ph, pw = max(0, TILE - H), max(0, TILE - W)
    x = np.pad(img, ((0, 0), (0, ph), (0, pw)), mode="reflect") if (ph or pw) else img
    Hp, Wp = x.shape[1:]
    mean = np.asarray(mean, np.float32)[:, None, None]
    std = np.asarray(std, np.float32)[:, None, None]
    acc = np.zeros((len(CLASSES), Hp, Wp), np.float32)
    wsum = np.zeros((Hp, Wp), np.float32)
    win = _window()
    tiles = [(r, c) for r in _starts(Hp) for c in _starts(Wp)]
    for i, (r, c) in enumerate(tiles):
        t = x[:, r:r + TILE, c:c + TILE]
        if not t.any():
            continue
        xt = torch.from_numpy(np.ascontiguousarray((t.astype(np.float32) - mean) / std))[None]
        with torch.inference_mode():
            ps = []
            for d in ((None, 3, 2) if tta else (None,)):
                a = xt if d is None else xt.flip(d)
                p = model(a).softmax(dim=1)
                ps.append(p if d is None else p.flip(d))
            p = torch.stack(ps).mean(0)[0].numpy()
        acc[:, r:r + TILE, c:c + TILE] += p * win
        wsum[r:r + TILE, c:c + TILE] += win
        if log and (i % 20 == 0 or i == len(tiles) - 1):
            log(f"  tile {i + 1}/{len(tiles)}")
    out = acc / np.maximum(wsum, 1e-6)
    out = out[:, :H, :W]
    out[:, ~valid] = 0.0
    return out


def nir_water(img, frac=0.55, sd_max=8.0):
    """Open water from NAIP: NIR-dark (< frac x the scene's median NIR) and smooth (7 px NIR std < sd_max).

    The U-Net's own class 5 "water" is not usable: on our courses it covers the whole course interior
    (pixel precision vs OSM water 0.05-0.07; its card reports val IoU 0.03). NDWI failed on algae-green ponds
    (Spirit Hollow 2023 IoU 0.00). This rule scored IoU 0.45-0.62, precision 0.74-0.89 vs OSM water on the
    three courses (evaluate.py). Returns (mask, score 0-1)."""
    from scipy import ndimage as ndi
    n = img[3].astype(np.float32)
    valid = img.any(axis=0)
    med = float(np.median(n[valid])) if valid.any() else 128.0
    sd = np.sqrt(np.maximum(ndi.uniform_filter(n * n, 7) - ndi.uniform_filter(n, 7) ** 2, 0))
    m = (n < frac * med) & (sd < sd_max) & valid
    m = ndi.binary_opening(m, iterations=1)
    score = np.clip((frac * med - n) / (0.3 * med), 0, 1) * 0.5 + 0.5
    return m, score


def drop_tree_shadows(mask, hag_m, res_m=0.6, ring_m=10.0, tall_m=3.0, frac_max=0.25, keep_m2=2000.0):
    """Remove NIR-water components whose ring_m surroundings are > frac_max tall canopy (HAG >= tall_m):
    tree shadows on grass are NIR-dark and smooth like water. hag_m: height above ground (m) on the NAIP
    grid, NaN = unknown. Components >= keep_m2 are kept (ponds; shadows are small). Returns (mask, n_dropped)."""
    from scipy import ndimage as ndi
    lab, n = ndi.label(mask)
    if n == 0:
        return mask, 0
    r = max(1, int(round(ring_m / res_m)))
    tall = np.nan_to_num(hag_m, nan=0.0) >= tall_m
    known = np.isfinite(hag_m)
    keep = np.ones(n + 1, bool)
    keep[0] = False
    objs = ndi.find_objects(lab)
    for i, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        y0, y1 = max(sl[0].start - r, 0), min(sl[0].stop + r, mask.shape[0])
        x0, x1 = max(sl[1].start - r, 0), min(sl[1].stop + r, mask.shape[1])
        m = lab[y0:y1, x0:x1] == i
        if m.sum() * res_m * res_m >= keep_m2:
            continue
        ring = ndi.binary_dilation(m, iterations=r) & ~m & known[y0:y1, x0:x1]
        if ring.sum() and tall[y0:y1, x0:x1][ring].mean() > frac_max:
            keep[i] = False
    return keep[lab], int((~keep[1:]).sum())
