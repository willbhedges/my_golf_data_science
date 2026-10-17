"""Compact imagery / lidar layers for the hole-formation pair model (runs on GitHub Actions: zt_formation.yml).

    python course_data/zero_tap/formation/aux_build.py <perception stack dir> --out aux.npz [--res 4]

From a perception stack (course_data/perception/fetch_stack.py: NAIP 1 m, U-Net probabilities, 3DEP HAG / DTM)
it writes one small north-up grid (default 5 m) holding what the pair features read:

  dtm     int16   bare earth, decimetres above `dtm_base_m` (-32768 = none)
  fw, gr, te  uint8  U-Net p(fairway), p(green), p(tee) x 255 (block mean)
  tree    uint8   share of the cell with lidar height above ground >= 4 m (x 255; 255-coded none -> 0)
  sdeg    uint8   mowing-stripe orientation, undirected bearing in degrees (0..176, 4-degree bins; 255 = none / not
                  fairway), from the structure tensor of the high-passed NAIP green band smoothed over ~10 m
                  (detect.stripe_orientation, per cell)
  scoh    uint8   its coherence x 255 in 1/16 steps (0 = no stripes)
  (fw / gr / te / tree are quantised to 1/16)
  crs, transform, dtm_base_m   the grid (EPSG code string, [res, 0, x0, 0, -res, y1])
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(CD, "perception"))


def block(a, k, fn="mean"):
    H, W = a.shape
    h, w = H // k, W // k
    v = a[:h * k, :w * k].reshape(h, k, w, k)
    if fn == "mean":
        return np.nanmean(v, axis=(1, 3))
    return np.nanmax(v, axis=(1, 3))


def build(stack_dir, res=4):
    import stack as S
    from scipy import ndimage as ndi
    st = S.load(stack_dir)
    k = int(round(res / st.res))
    out = {}
    with np.errstate(all="ignore"):
        z = st.dtm()
        zb = block(z, k)
        base = float(st.meta.get("dtm_base_m") or 0.0)
        out["dtm"] = np.where(np.isfinite(zb), np.clip(np.round((zb - base) * 10), -32000, 32000), -32768).astype(np.int16)
        for name, key in (("fairway", "fw"), ("green", "gr"), ("tee", "te")):
            out[key] = np.clip(np.round(block(st.seg(name), k) * 255), 0, 255).astype(np.uint8)
        h = st.hag()
        tall = np.where(np.isfinite(h), (h >= 4.0).astype(np.float32), 0.0)
        out["tree"] = np.clip(np.round(block(tall, k) * 255), 0, 255).astype(np.uint8)
        g = st.naip()[1]
        hp = g - ndi.gaussian_filter(g, 4)
        gr = ndi.sobel(hp, axis=0)
        gc = ndi.sobel(hp, axis=1)
        e, nn = gc, -gr
        sig = 10.0 / st.res
        Jee = ndi.gaussian_filter(e * e, sig)
        Jnn = ndi.gaussian_filter(nn * nn, sig)
        Jen = ndi.gaussian_filter(e * nn, sig)
        Jee, Jnn, Jen = block(Jee, k), block(Jnn, k), block(Jen, k)
        tr = Jee + Jnn
        coh = np.sqrt((Jee - Jnn) ** 2 + 4 * Jen ** 2) / np.maximum(tr, 1e-9)
        phi = 0.5 * np.arctan2(2 * Jen, Jee - Jnn)
        stripe = ((90.0 - np.degrees(phi)) + 90.0) % 180
    # quantised for size: probabilities / shares to 1/16, stripes (4-degree bins) only where the U-Net sees fairway
    for key in ("fw", "gr", "te", "tree"):
        out[key] = (out[key] // 16 * 16 + 8 * (out[key] >= 16)).astype(np.uint8)
    coh = np.nan_to_num(coh)
    keep = (out["fw"] >= 64) & (coh >= 0.08)
    out["sdeg"] = np.where(keep, np.clip(np.round(stripe / 4) * 4, 0, 176), 255).astype(np.uint8)
    out["scoh"] = np.where(keep, np.clip(np.round(coh * 16), 0, 15) * 16, 0).astype(np.uint8)
    out["crs"] = np.array(st.crs)
    out["transform"] = np.array([float(res), 0.0, st.x0, 0.0, -float(res), st.y1])
    out["dtm_base_m"] = np.array(base)
    out["lidar"] = np.array(bool(st.has_lidar()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stack")
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", type=float, default=5.0)
    a = ap.parse_args()
    out = build(a.stack, a.res)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    np.savez_compressed(a.out, **out)
    print(json.dumps({k: list(v.shape) for k, v in out.items()}), os.path.getsize(a.out))


if __name__ == "__main__":
    main()
