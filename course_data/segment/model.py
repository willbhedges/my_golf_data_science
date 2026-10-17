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
    """(model, config, sha) on CPU in float32."""
    import segmentation_models_pytorch as smp
    import torch
    from huggingface_hub import HfApi, hf_hub_download
    if threads:
        torch.set_num_threads(threads)
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


def predict_raster(model, img, tta=True, log=print):
    """img: (4, H, W) uint8 R,G,B,NIR at 0.6 m -> (6, H, W) float32 probabilities (0 where no data)."""
    import torch
    _, H, W = img.shape
    valid = img.any(axis=0)
    ph, pw = max(0, TILE - H), max(0, TILE - W)
    x = np.pad(img, ((0, 0), (0, ph), (0, pw)), mode="reflect") if (ph or pw) else img
    Hp, Wp = x.shape[1:]
    mean = np.asarray(MEAN, np.float32)[:, None, None]
    std = np.asarray(STD, np.float32)[:, None, None]
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


def ndwi_water(img, thr=0.15):
    """Open water from NAIP: NDWI = (G - NIR) / (G + NIR) > thr (water is NIR-dark). Returns (mask, ndwi)."""
    g = img[1].astype(np.float32)
    n = img[3].astype(np.float32)
    ndwi = (g - n) / np.maximum(g + n, 1.0)
    return (ndwi > thr) & img.any(axis=0), ndwi
