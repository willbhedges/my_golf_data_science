"""Frozen pretrained deep features for the GPS-app screenshots (run on GitHub Actions).

  python spirit_hollow/deep/extract_features.py      -> spirit_hollow/deep/features/*.npz

Frame conventions match spirit_hollow/vision.py: each screenshot is resized to 920 x 2000
screen px and features are wanted on the 460 x 1000 grid (W=460, H=1000, SCALE=2).

Backbone
  Primary: DINOv2 ViT-S/14 (torch.hub facebookresearch/dinov2, dinov2_vits14), frozen.
  The 920x2000 image is upscaled by UPSCALE (1.5 -> 1380x3000) so one 14 px patch covers
  ~9.3 screen px, then processed in overlapping 518x518 tiles with stride 406 (= 29
  patches, so every tile's patches fall on one global 14 px lattice). Patch tokens from
  blocks 6, 9 and 12 (layer-normed) are concatenated (3 x 384 = 1152 dims) and averaged
  where tiles overlap.
  Fallback (if DINOv2 cannot be loaded): timm convnext_tiny (ImageNet) stages 1-3
  (strides 4/8/16, 96+192+384 dims) resized to a stride-8 lattice and concatenated.

Dimensionality: one PCA fitted jointly on a random sample of lattice cells from all
images, keeping C = 64 components (saved in features/pca.npz).

Storage: a (1000, 460, 64) float16 array is 59 MB per image (1.1 GB for 19 images), so
each .npz stores the features on the backbone's own lattice ('feat', float16,
(Hc, Wc, C), about 2.7 MB) together with 'cell' = lattice cell size in 920x2000 screen px.
load_grid(stem) returns the bilinearly upsampled (1000, 460, C) float16 array aligned to
the vision.py grid; it needs only numpy (no torch), so downstream code can do

    from deep.extract_features import load_grid
    F = load_grid("hole05")          # (1000, 460, 64) float16
"""
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "screenshots")
OUT = os.path.join(HERE, "features")
SCREEN_W, SCREEN_H = 920, 2000
SCALE = 2
W, H = SCREEN_W // SCALE, SCREEN_H // SCALE
C_OUT = 64
UPSCALE = 1.5
TILE, PATCH = 518, 14
STRIDE = 29 * PATCH                     # 406
MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)


# ----------------------------------------------------------------------------- loading
def upsample_to_grid(feat, cell):
    """Bilinear-resample lattice features (Hc, Wc, C) to the (H, W, C) vision grid.

    Lattice cell (i, j) covers screen px [cell*j, cell*(j+1)) x [cell*i, cell*(i+1)),
    so its centre is at screen ((j+0.5)*cell, (i+0.5)*cell). Grid px (x, y) has its
    centre at screen ((x+0.5)*SCALE, (y+0.5)*SCALE)."""
    Hc, Wc = feat.shape[:2]

    def axis(n_out, n_in):
        c = (np.arange(n_out) + 0.5) * SCALE / cell - 0.5
        c = np.clip(c, 0, n_in - 1)
        i0 = np.floor(c).astype(int)
        i1 = np.minimum(i0 + 1, n_in - 1)
        return i0, i1, (c - i0).astype(np.float32)

    y0, y1, wy = axis(H, Hc)
    x0, x1, wx = axis(W, Wc)
    f = feat.astype(np.float32)
    rows = f[y0] * (1 - wy)[:, None, None] + f[y1] * wy[:, None, None]          # (H, Wc, C)
    out = rows[:, x0] * (1 - wx)[None, :, None] + rows[:, x1] * wx[None, :, None]
    return out.astype(np.float16)


def load_grid(stem, features_dir=OUT):
    """(1000, 460, C) float16 features for screenshot <stem>, aligned to vision.py's grid."""
    z = np.load(os.path.join(features_dir, stem + ".npz"))
    return upsample_to_grid(z["feat"], float(z["cell"]))


# ----------------------------------------------------------------------------- extraction
def load_image(path):
    from PIL import Image
    im = Image.open(path).convert("RGB").resize((SCREEN_W, SCREEN_H), Image.BILINEAR)
    return im


def dinov2_lattice(model, im, torch):
    from PIL import Image
    sw, sh = round(SCREEN_W * UPSCALE), round(SCREEN_H * UPSCALE)
    a = np.asarray(im.resize((sw, sh), Image.BICUBIC)).astype(np.float32) / 255.0
    a = (a - MEAN) / STD
    nx = max(1, int(np.ceil((sw - TILE) / STRIDE)) + 1)
    ny = max(1, int(np.ceil((sh - TILE) / STRIDE)) + 1)
    pw, ph = STRIDE * (nx - 1) + TILE, STRIDE * (ny - 1) + TILE
    a = np.pad(a, ((0, ph - sh), (0, pw - sw), (0, 0)), mode="edge")
    x = torch.from_numpy(a).permute(2, 0, 1)
    gp = TILE // PATCH
    Hc, Wc = ph // PATCH, pw // PATCH
    acc = None
    cnt = np.zeros((Hc, Wc, 1), np.float32)
    coords = [(ty * STRIDE, tx * STRIDE) for ty in range(ny) for tx in range(nx)]
    for b in range(0, len(coords), 8):
        batch = coords[b:b + 8]
        t = torch.stack([x[:, y:y + TILE, xx:xx + TILE] for y, xx in batch])
        with torch.inference_mode():
            outs = model.get_intermediate_layers(t, n=[5, 8, 11], reshape=True, norm=True)
        f = torch.cat(outs, 1).permute(0, 2, 3, 1).numpy()                     # (B, gp, gp, D)
        if acc is None:
            acc = np.zeros((Hc, Wc, f.shape[-1]), np.float32)
        for (y, xx), fi in zip(batch, f):
            i, j = y // PATCH, xx // PATCH
            acc[i:i + gp, j:j + gp] += fi
            cnt[i:i + gp, j:j + gp] += 1
    acc /= np.maximum(cnt, 1)
    vh, vw = int(np.ceil(sh / PATCH)), int(np.ceil(sw / PATCH))
    return acc[:vh, :vw], PATCH / UPSCALE


def convnext_lattice(model, im, torch):
    a = (np.asarray(im).astype(np.float32) / 255.0 - MEAN) / STD
    t = torch.from_numpy(a).permute(2, 0, 1)[None]
    with torch.inference_mode():
        feats = model(t)
        size = (SCREEN_H // 8, SCREEN_W // 8)
        feats = [torch.nn.functional.interpolate(f, size=size, mode="bilinear",
                                                 align_corners=False) for f in feats]
        f = torch.cat(feats, 1)[0].permute(1, 2, 0).numpy()
    return f, 8.0


def get_backbone(torch):
    try:
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14", trust_repo=True)
        model.eval()
        # smoke test
        with torch.inference_mode():
            model.get_intermediate_layers(torch.zeros(1, 3, TILE, TILE), n=[5, 8, 11],
                                          reshape=True, norm=True)
        return "dinov2_vits14 (blocks 6,9,12; tiles 518/406 at 1.5x)", model, dinov2_lattice
    except Exception as e:                                                    # noqa: BLE001
        print(f"DINOv2 unavailable ({type(e).__name__}: {e}); falling back to convnext_tiny",
              flush=True)
    import timm
    model = timm.create_model("convnext_tiny", pretrained=True, features_only=True,
                              out_indices=(0, 1, 2))
    model.eval()
    return "timm convnext_tiny ImageNet (stages 1-3 @ stride 8)", model, convnext_lattice


def main():
    import torch
    torch.set_num_threads(os.cpu_count() or 2)
    os.makedirs(OUT, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(SHOTS, "*.png")))
    if not paths:
        sys.exit(f"no screenshots in {SHOTS}")
    name, model, fn = get_backbone(torch)
    print("backbone:", name, flush=True)

    lattices = {}
    for p in paths:
        t0 = time.time()
        f, cell = fn(model, load_image(p), torch)
        stem = os.path.splitext(os.path.basename(p))[0]
        lattices[stem] = (f.astype(np.float16), cell)
        print(f"{stem}: lattice {f.shape} cell {cell:.3f}px  {time.time() - t0:.1f}s", flush=True)

    rng = np.random.default_rng(0)
    sample = []
    for f, _ in lattices.values():
        v = f.reshape(-1, f.shape[-1])
        sample.append(v[rng.choice(len(v), min(len(v), 6000), replace=False)].astype(np.float64))
    S = np.concatenate(sample)
    mean = S.mean(0)
    cov = np.cov(S - mean, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]
    comps = evecs[:, :C_OUT].T                                                # (C, D)
    explained = float(evals[:C_OUT].sum() / evals.sum())
    np.savez(os.path.join(OUT, "pca.npz"), mean=mean.astype(np.float32),
             components=comps.astype(np.float32), eigenvalues=evals[:C_OUT].astype(np.float32),
             explained_ratio=np.float32(explained))
    print(f"PCA {S.shape[1]} -> {C_OUT}: {explained:.1%} variance", flush=True)

    files = {}
    for stem, (f, cell) in lattices.items():
        z = ((f.astype(np.float32) - mean.astype(np.float32)) @ comps.T.astype(np.float32))
        z = z.astype(np.float16)
        np.savez_compressed(os.path.join(OUT, stem + ".npz"), feat=z, cell=np.float32(cell))
        g = load_grid(stem)
        assert g.shape == (H, W, C_OUT), g.shape
        files[stem + ".npz"] = dict(lattice_shape=list(z.shape), grid_shape=list(g.shape),
                                    cell_screen_px=cell,
                                    bytes=os.path.getsize(os.path.join(OUT, stem + ".npz")))

    manifest = dict(
        backbone=name, channels=C_OUT, raw_dim=int(S.shape[1]),
        pca_explained_ratio=explained, dtype="float16",
        frame=dict(screen=[SCREEN_W, SCREEN_H], grid=[W, H], scale=SCALE),
        storage=("npz key 'feat' = PCA features on the backbone lattice; 'cell' = lattice "
                 "cell size in 920x2000 screen px. extract_features.load_grid(stem) gives the "
                 "bilinearly upsampled (1000, 460, C) float16 grid array."),
        torch=torch.__version__, files=files)
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    print("done:", len(files), "files", flush=True)


if __name__ == "__main__":
    main()
