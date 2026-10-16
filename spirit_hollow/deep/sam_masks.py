"""Segment Anything (SAM) automatic region masks for the GPS-app screenshots (run on GitHub Actions).

  python spirit_hollow/deep/sam_masks.py        -> spirit_hollow/deep/sam/<stem>.npz + manifest.json

Frame conventions match spirit_hollow/vision.py: each screenshot is resized to 920 x 2000
screen px (same PIL call as vision.load_rgb); rows above TOP=545 and from BOTTOM=1830 down
are app UI. SamAutomaticMaskGenerator (ViT-B, official segment-anything package) is run on
the ground crop rows [545, 1830) of the 920x2000 image (offset recorded as 'offset_y').

Each mask is mapped to the 460 x 1000 vision grid (SCALE=2) by 2x2 area averaging
(>= 0.5 covered). Masks are painted largest-first so every grid pixel belongs to the
smallest-area mask covering it (finer regions win). Unassigned ground pixels take the
nearest region if it is within FILL_PX grid px, else stay -1. UI rows are -1.

Each <stem>.npz holds
  regions      int32 (1000, 460): -1 = no region / UI, else region id 0..N-1
  areas        int32 (N,): grid px per region in the final label image
  mask_area    int32 (N,): grid px of the original SAM mask (before overlap resolution)
  pred_iou, stability  float32 (N,): SAM scores
  offset_y     int: screen-px row of the crop passed to SAM

    from deep.sam_masks import load_regions
    R = load_regions("hole05")          # (1000, 460) int32
"""
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "screenshots")
OUT = os.path.join(HERE, "sam")
SCREEN_W, SCREEN_H = 920, 2000
SCALE = 2
W, H = SCREEN_W // SCALE, SCREEN_H // SCALE
TOP, BOTTOM = 545, 1830
FILL_PX = 3
CKPT_URL = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
CKPT = os.path.join(os.environ.get("SAM_CKPT_DIR", "/tmp"), "sam_vit_b_01ec64.pth")
PARAMS = dict(points_per_side=32, pred_iou_thresh=0.86, stability_score_thresh=0.9,
              min_mask_region_area=200, crop_n_layers=1, crop_n_points_downscale_factor=2,
              points_per_batch=64)
BUDGET_S = 70 * 60          # drop crop_n_layers to 0 if the projected total exceeds this


def load_regions(stem, out_dir=OUT):
    """(1000, 460) int32 region labels for screenshot <stem>, aligned to vision.py's grid."""
    return np.load(os.path.join(out_dir, stem + ".npz"))["regions"]


def load_image(path):
    from PIL import Image
    return np.asarray(Image.open(path).convert("RGB").resize((SCREEN_W, SCREEN_H)))


def masks_to_labels(masks, offset_y=TOP):
    """SAM mask dicts (crop frame) -> (labels (H, W) int32, kept mask indices)."""
    from scipy import ndimage
    g0, g1 = TOP // SCALE, -(-BOTTOM // SCALE)           # grid rows touching ground
    grids = []
    for m in masks:
        seg = m["segmentation"]
        full = np.zeros((SCREEN_H, SCREEN_W), np.float32)
        full[offset_y:offset_y + seg.shape[0], :seg.shape[1]] = seg
        full[:TOP] = 0
        full[BOTTOM:] = 0
        gm = full.reshape(H, SCALE, W, SCALE).mean((1, 3)) >= 0.5
        grids.append(gm)
    areas = np.array([g.sum() for g in grids], np.int64)
    labels = np.full((H, W), -1, np.int32)
    for i in np.argsort(-areas, kind="stable"):          # largest first; smaller overwrite
        if areas[i] > 0:
            labels[grids[i]] = i
    # renumber surviving regions 0..N-1
    kept = np.unique(labels[labels >= 0])
    remap = np.full(len(masks) + 1, -1, np.int32)
    remap[kept] = np.arange(len(kept), dtype=np.int32)
    labels = np.where(labels >= 0, remap[labels], -1).astype(np.int32)
    # fill small gaps in the ground band by nearest region
    unassigned = labels < 0
    if (~unassigned).any():
        dist, (iy, ix) = ndimage.distance_transform_edt(unassigned, return_indices=True)
        ground = np.zeros((H, W), bool)
        ground[g0:g1] = True
        fill = unassigned & ground & (dist <= FILL_PX)
        labels[fill] = labels[iy[fill], ix[fill]]
    labels[:g0] = -1
    labels[g1:] = -1
    return labels, kept, areas


def ensure_checkpoint():
    if not os.path.exists(CKPT):
        import urllib.request
        print("downloading", CKPT_URL, flush=True)
        urllib.request.urlretrieve(CKPT_URL, CKPT)
    return CKPT


def main():
    import torch
    from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
    torch.set_num_threads(os.cpu_count() or 2)
    os.makedirs(OUT, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(SHOTS, "*.png")))
    if not paths:
        sys.exit(f"no screenshots in {SHOTS}")
    sam = sam_model_registry["vit_b"](checkpoint=ensure_checkpoint())
    sam.eval()
    params = dict(PARAMS)
    gen = SamAutomaticMaskGenerator(sam, output_mode="binary_mask", **params)

    files = {}
    t_start = time.time()
    for k, p in enumerate(paths):
        stem = os.path.splitext(os.path.basename(p))[0]
        t0 = time.time()
        crop = np.ascontiguousarray(load_image(p)[TOP:BOTTOM])
        with torch.inference_mode():
            masks = gen.generate(crop)
        labels, kept, mask_area = masks_to_labels(masks)
        n = len(kept)
        areas = np.bincount(labels[labels >= 0], minlength=n).astype(np.int32)
        np.savez_compressed(
            os.path.join(OUT, stem + ".npz"), regions=labels, areas=areas,
            mask_area=mask_area[kept].astype(np.int32),
            pred_iou=np.array([masks[i]["predicted_iou"] for i in kept], np.float32),
            stability=np.array([masks[i]["stability_score"] for i in kept], np.float32),
            offset_y=np.int32(TOP))
        dt = time.time() - t0
        files[stem + ".npz"] = dict(
            sam_masks=len(masks), regions=int(n), crop_n_layers=params["crop_n_layers"],
            unassigned_ground_px=int((labels[TOP // SCALE:-(-BOTTOM // SCALE)] < 0).sum()),
            seconds=round(dt, 1), bytes=os.path.getsize(os.path.join(OUT, stem + ".npz")))
        print(f"{stem}: {len(masks)} masks -> {n} regions  {dt:.1f}s", flush=True)
        elapsed = time.time() - t_start
        if params["crop_n_layers"] > 0 and k + 1 < len(paths):
            projected = elapsed + dt * (len(paths) - k - 1)
            if projected > BUDGET_S:
                print(f"projected {projected / 60:.0f} min > budget; crop_n_layers -> 0", flush=True)
                params["crop_n_layers"] = 0
                gen = SamAutomaticMaskGenerator(sam, output_mode="binary_mask", **params)

    manifest = dict(
        model="SAM ViT-B (sam_vit_b_01ec64.pth, facebookresearch/segment-anything)",
        params=PARAMS, frame=dict(screen=[SCREEN_W, SCREEN_H], grid=[W, H], scale=SCALE,
                                  crop_rows=[TOP, BOTTOM], offset_y=TOP),
        labels=("regions int32 (1000,460): -1 = none/UI; each px = smallest SAM mask covering "
                f"it; gaps filled by nearest region within {FILL_PX} grid px"),
        torch=torch.__version__, total_seconds=round(time.time() - t_start, 1),
        region_counts={k[:-4]: v["regions"] for k, v in files.items()}, files=files)
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    print("done:", len(files), "files", flush=True)


if __name__ == "__main__":
    main()
