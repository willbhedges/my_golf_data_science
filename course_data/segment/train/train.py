"""Train our own NAIP golf-feature U-Net on the OSM-labelled set from build_dataset.py (CPU, GitHub Actions).

    python course_data/segment/train/train.py --data /tmp/golfseg_data --out /tmp/golfseg_model [--minutes 200]

Why: the ariadgolf weights carry no licence grant. This model is ours: U-Net / ResNet-34 (segmentation_models_pytorch,
encoder initialised from torchvision ImageNet weights, BSD-3), 4 bands R,G,B,NIR at 0.6 m, the same six classes
(0 background, 1 green, 2 tee, 3 fairway, 4 bunker, 5 water) and the same tiling at inference (model.py), so
run_segment.py runs it unchanged (--model <dir>). Labels OSM (ODbL): attribute "OpenStreetMap contributors".

Training: courses split 90/10 by course (validation IoU per class logged each epoch); random 320 px crops
centred on labelled pixels, flips / 90-degree rotations, brightness jitter; loss = cross-entropy (ignore 255,
class weights ~ 1/sqrt(frequency)) + 0.5 x soft Dice; AdamW + one-cycle LR; stops at --minutes. Saves the
smp save_pretrained folder (config.json + model.safetensors) + preprocessor_config.json + train_log.json.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import random
import time

import numpy as np

CLASSES = ["background", "green", "tee", "fairway", "bunker", "water"]


def load_courses(data):
    out = []
    for f in sorted(glob.glob(os.path.join(data, "*.npz"))):
        z = np.load(f)
        img, lab = z["img"], z["lab"]
        if img.shape[1] < 400 or img.shape[2] < 400 or (lab != 255).sum() < 10000:
            continue
        out.append(dict(name=os.path.basename(f), img=img, lab=lab))
    return out


def stats(courses):
    s = np.zeros(4)
    ss = np.zeros(4)
    n = 0
    for c in courses:
        m = c["lab"] != 255
        x = c["img"][:, m].astype(np.float64)
        s += x.sum(1)
        ss += (x * x).sum(1)
        n += x.shape[1]
    mean = s / n
    std = np.sqrt(ss / n - mean ** 2)
    freq = np.zeros(len(CLASSES))
    for c in courses:
        freq += np.bincount(c["lab"][c["lab"] != 255].ravel(), minlength=len(CLASSES))[:len(CLASSES)]
    return mean.tolist(), std.tolist(), freq


def sampler(courses, size, rng):
    c = courses[rng.integers(len(courses))]
    H, W = c["lab"].shape
    for _ in range(10):
        y, x = rng.integers(0, H - size), rng.integers(0, W - size)
        lab = c["lab"][y:y + size, x:x + size]
        if (lab != 255).mean() > 0.3 and (rng.random() < 0.2 or (lab > 0).mean() * (lab != 255).mean() > 0.01):
            break
    img = c["img"][:, y:y + size, x:x + size].astype(np.float32)
    k = rng.integers(4)
    img, lab = np.rot90(img, k, (1, 2)), np.rot90(lab, k)
    if rng.random() < 0.5:
        img, lab = img[:, :, ::-1], lab[:, ::-1]
    img = img * rng.uniform(0.9, 1.1, size=(4, 1, 1)) + rng.uniform(-8, 8, size=(4, 1, 1))
    return np.ascontiguousarray(img), np.ascontiguousarray(lab)


def batch(courses, size, n, rng, mean, std):
    xs, ys = zip(*(sampler(courses, size, rng) for _ in range(n)))
    x = (np.stack(xs) - np.asarray(mean, np.float32)[None, :, None, None]) / np.asarray(std, np.float32)[None, :, None, None]
    return x.astype(np.float32), np.stack(ys).astype(np.int64)


def dice_loss(logits, y, ignore=255):
    import torch
    p = logits.softmax(1)
    valid = (y != ignore)
    yy = torch.where(valid, y, torch.zeros_like(y))
    oh = torch.nn.functional.one_hot(yy, p.shape[1]).permute(0, 3, 1, 2).float() * valid[:, None]
    p = p * valid[:, None]
    inter = (p * oh).sum((0, 2, 3))
    den = p.sum((0, 2, 3)) + oh.sum((0, 2, 3))
    d = 1 - (2 * inter + 1) / (den + 1)
    return d[1:].mean()


def evaluate(model, courses, mean, std, size=512, max_tiles=60):
    import torch
    inter = np.zeros(len(CLASSES))
    union = np.zeros(len(CLASSES))
    model.eval()
    n = 0
    with torch.inference_mode():
        for c in courses:
            H, W = c["lab"].shape
            for y in range(0, H - size + 1, size):
                for x in range(0, W - size + 1, size):
                    lab = c["lab"][y:y + size, x:x + size]
                    if (lab != 255).mean() < 0.3 or n >= max_tiles:
                        continue
                    img = (c["img"][:, y:y + size, x:x + size].astype(np.float32)
                           - np.asarray(mean, np.float32)[:, None, None]) / np.asarray(std, np.float32)[:, None, None]
                    pred = model(torch.from_numpy(img)[None]).argmax(1)[0].numpy()
                    v = lab != 255
                    for k in range(1, len(CLASSES)):
                        p, t = (pred == k) & v, (lab == k) & v
                        inter[k] += (p & t).sum()
                        union[k] += (p | t).sum()
                    n += 1
    model.train()
    return {CLASSES[k]: round(float(inter[k] / union[k]), 3) if union[k] else None for k in range(1, len(CLASSES))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--minutes", type=float, default=200.0)
    ap.add_argument("--size", type=int, default=320)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=6e-4)
    ap.add_argument("--encoder", default="resnet34")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    import segmentation_models_pytorch as smp
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)
    courses = load_courses(a.data)
    random.Random(a.seed).shuffle(courses)
    nval = max(3, len(courses) // 10)
    val, tr = courses[:nval], courses[nval:]
    mean, std, freq = stats(tr)
    w = 1 / np.sqrt(np.maximum(freq / freq.sum(), 1e-4))
    w = w / w.mean()
    print(f"{len(tr)} train / {len(val)} val courses; mean {np.round(mean, 1)} std {np.round(std, 1)}; "
          f"class freq {np.round(freq / freq.sum(), 4)} -> weights {np.round(w, 2)}", flush=True)
    model = smp.Unet(a.encoder, encoder_weights="imagenet", in_channels=4, classes=len(CLASSES))
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    ce = torch.nn.CrossEntropyLoss(weight=torch.tensor(w, dtype=torch.float32), ignore_index=255)
    # time one step to size the schedule
    t0 = time.time()
    x, y = batch(tr, a.size, a.bs, rng, mean, std)
    loss = ce(model(torch.from_numpy(x)), torch.from_numpy(y))
    loss.backward()
    opt.zero_grad()
    step_s = time.time() - t0
    budget = a.minutes * 60 * 0.92
    eval_every = 300
    total = max(50, int(budget / (step_s * 1.05)))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=total, pct_start=0.1)
    print(f"step {step_s:.2f}s -> {total} steps", flush=True)
    log = dict(steps=[], val=[], courses_train=[c["name"] for c in tr], courses_val=[c["name"] for c in val],
               mean=mean, std=std, class_weights=w.tolist(), size=a.size, bs=a.bs, encoder=a.encoder)
    t0 = time.time()
    run = 0.0
    for step in range(1, total + 1):
        x, y = batch(tr, a.size, a.bs, rng, mean, std)
        xt, yt = torch.from_numpy(x), torch.from_numpy(y)
        out = model(xt)
        loss = ce(out, yt) + 0.5 * dice_loss(out, yt)
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()
        run = 0.98 * run + 0.02 * float(loss) if step > 1 else float(loss)
        if step % 25 == 0:
            log["steps"].append([step, round(run, 4), round(time.time() - t0)])
            print(f"step {step}/{total} loss {run:.4f} {time.time() - t0:.0f}s", flush=True)
        if step % eval_every == 0 or step == total:
            v = evaluate(model, val, mean, std)
            log["val"].append(dict(step=step, iou=v))
            print("val", v, flush=True)
        if time.time() - t0 > a.minutes * 60:
            print("time budget reached")
            break
    os.makedirs(a.out, exist_ok=True)
    model.eval()
    model.half().save_pretrained(a.out)
    pre = {"bands": ["red", "green", "blue", "near_infrared"], "input_dtype": "uint8", "do_rescale": False,
           "do_normalize": True, "image_mean": [round(m, 3) for m in mean], "image_std": [round(s, 3) for s in std],
           "tile_size": 512, "ground_sample_distance_m": 0.6,
           "id2label": {str(i): c for i, c in enumerate(CLASSES)},
           "licence": "ours (course_data/segment/train); labels OpenStreetMap contributors ODbL 1.0; imagery USDA NAIP; "
                      "encoder init torchvision ImageNet ResNet weights (BSD-3)"}
    json.dump(pre, open(os.path.join(a.out, "preprocessor_config.json"), "w"), indent=1)
    log["final_val"] = log["val"][-1] if log["val"] else None
    json.dump(log, open(os.path.join(a.out, "train_log.json"), "w"), indent=1)
    print("saved", a.out)


if __name__ == "__main__":
    main()
