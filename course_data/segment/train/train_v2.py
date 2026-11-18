"""Fine-tune our NAIP golf-feature U-Net (golfseg_own) on the national v2 set (build_dataset.py --courses), CPU,
GitHub Actions, resumable across jobs (each job < 6 h).

    python course_data/segment/train/train_v2.py --data D --out OUT --init course_data/segment/models/golfseg_own \
        --ckpt CK.pt --minutes 300 --total-minutes 600 [--resume]

What is kept from v1 (so fastc/perception/unet.py runs the result unchanged): smp Unet / ResNet-34, 4 bands R, G, B,
NIR uint8 at 0.6 m, 6 classes, the v1 normalisation (image_mean / image_std copied from --init's
preprocessor_config.json, not re-estimated), tile 512 at inference. The state-dict names are checked against
--init's safetensors.

What changes:
  * data: ~1000+ courses from all lower-48 states, too many to hold decoded: a resident pool of --pool courses,
    one course swapped every --swap-s seconds by a background thread (JPEG GeoTIFF image + lab npz);
  * class-balanced crops: 40 % random crops as v1, 60 % centred on a pixel of a class drawn with --class-p
    (green / tee / fairway / bunker / water), so tees and water are seen more often;
  * loss: cross-entropy with weights ~ 1 / sqrt(class frequency) (from the index pixel counts) x --boost
    (tee, water), + 0.5 x soft Dice over the five feature classes, as v1;
  * schedule: AdamW, warm-up then cosine over the planned steps of ALL jobs (--total-minutes, sized on the first
    job's step time), fine-tuned from --init (lr --lr, default 2e-4);
  * validation: ~4 % of the courses (by osm id hash), fixed 512 px tiles; IoU per class of --init (step 0) and
    every --eval-every steps; the checkpoint with the best mean IoU over the five classes is exported.
Checkpoint (--ckpt: weights fp32, optimiser, step, plan, best) every --ckpt-min minutes and at the end; --resume
continues from it. Export at the end of every job: smp save_pretrained (fp16 safetensors) + preprocessor_config.json
+ train_log.json in --out.
Labels: OpenStreetMap contributors (ODbL 1.0). Imagery: USDA NAIP (public domain) via Microsoft Planetary Computer.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import random
import threading
import time

import numpy as np

CLASSES = ["background", "green", "tee", "fairway", "bunker", "water"]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def is_val(osm, share=0.04):
    return int(hashlib.sha1(osm.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF < share


def read_index(data):
    """merged index rows of every index*.json under data (one per shard) -> list of dict(osm, file, image, pixels..)"""
    rows = {}
    for p in sorted(glob.glob(os.path.join(data, "**", "index*.json"), recursive=True)):
        d = json.load(open(p))
        base = os.path.dirname(p)
        for k, c in d["courses"].items():
            if "file" not in c:
                continue
            c = dict(c, osm=k, dir=base)
            if os.path.exists(os.path.join(base, c["file"])):
                rows[k] = c
    return list(rows.values())


def load_course(c):
    z = np.load(os.path.join(c["dir"], c["file"]))
    lab = z["lab"]
    if "img" in z.files:
        img = z["img"]
    else:
        import rasterio
        with rasterio.open(os.path.join(c["dir"], c["image"])) as src:
            img = src.read()
    if img.shape[1:] != lab.shape:
        raise ValueError(f"shape mismatch {img.shape} {lab.shape}")
    pts = {}
    rng = np.random.default_rng(abs(hash(c["osm"])) % 2**32)
    for k in range(1, len(CLASSES)):
        idx = np.flatnonzero(lab.ravel() == k)
        if len(idx) >= 50:
            pts[k] = rng.choice(idx, min(len(idx), 4000), replace=False)
    return dict(osm=c["osm"], img=img, lab=lab, pts=pts)


class Pool:
    """resident decoded courses; a thread swaps one every swap_s seconds"""

    def __init__(self, rows, n, swap_s, seed):
        self.rows, self.n, self.swap_s = rows, min(n, len(rows)), swap_s
        self.rng = random.Random(seed)
        self.order = list(range(len(rows)))
        self.rng.shuffle(self.order)
        self.next = 0
        self.items = []
        self.lock = threading.Lock()
        self.loaded = 0
        tries = 0
        while len(self.items) < self.n and tries < 3 * len(rows):
            tries += 1
            c = self._load_next()
            if c is not None:
                self.items.append(c)
        self.stop = False
        threading.Thread(target=self._run, daemon=True).start()

    def _load_next(self):
        r = self.rows[self.order[self.next % len(self.order)]]
        self.next += 1
        if self.next % len(self.order) == 0:
            self.rng.shuffle(self.order)
        try:
            c = load_course(r)
            self.loaded += 1
            H, W = c["lab"].shape
            if H < 400 or W < 400 or (c["lab"] != 255).sum() < 10000:
                return None
            return c
        except Exception as e:                                  # noqa: BLE001
            log("load failed", r["osm"], repr(e)[:200])
            return None

    def _run(self):
        while not self.stop:
            time.sleep(self.swap_s)
            c = self._load_next()
            if c is not None:
                with self.lock:
                    self.items[self.rng.randrange(len(self.items))] = c

    def pick(self, rng):
        with self.lock:
            return self.items[rng.integers(len(self.items))]


def sampler(pool, size, rng, class_p):
    c = pool.pick(rng)
    H, W = c["lab"].shape
    y = x = 0
    centred = rng.random() < 0.6 and c["pts"]
    for _ in range(10):
        if centred:
            ks = [k for k in c["pts"]]
            p = np.array([class_p[k - 1] for k in ks], np.float64)
            k = ks[rng.choice(len(ks), p=p / p.sum())]
            i = c["pts"][k][rng.integers(len(c["pts"][k]))]
            cy, cx = divmod(int(i), W)
            cy += int(rng.integers(-size // 3, size // 3 + 1))
            cx += int(rng.integers(-size // 3, size // 3 + 1))
            y = int(np.clip(cy - size // 2, 0, H - size))
            x = int(np.clip(cx - size // 2, 0, W - size))
        else:
            y, x = int(rng.integers(0, H - size)), int(rng.integers(0, W - size))
        lab = c["lab"][y:y + size, x:x + size]
        if (lab != 255).mean() > 0.3 and (centred or rng.random() < 0.2 or (lab > 0).mean() * (lab != 255).mean() > 0.01):
            break
    img = c["img"][:, y:y + size, x:x + size].astype(np.float32)
    lab = c["lab"][y:y + size, x:x + size]
    k = rng.integers(4)
    img, lab = np.rot90(img, k, (1, 2)), np.rot90(lab, k)
    if rng.random() < 0.5:
        img, lab = img[:, :, ::-1], lab[:, ::-1]
    img = img * rng.uniform(0.9, 1.1, size=(4, 1, 1)) + rng.uniform(-8, 8, size=(4, 1, 1))
    return np.ascontiguousarray(img), np.ascontiguousarray(lab)


def batch(pool, size, n, rng, mean, std, class_p):
    xs, ys = zip(*(sampler(pool, size, rng, class_p) for _ in range(n)))
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


def val_tiles(rows, size=512, per_course=3, seed=0):
    """fixed validation tiles (img uint8, lab) from the validation courses: the tiles with most labelled feature px"""
    out = []
    for r in rows:
        try:
            c = load_course(r)
        except Exception as e:                                  # noqa: BLE001
            log("val load failed", r["osm"], repr(e)[:120])
            continue
        H, W = c["lab"].shape
        cand = []
        for y in range(0, H - size + 1, size):
            for x in range(0, W - size + 1, size):
                lab = c["lab"][y:y + size, x:x + size]
                if (lab != 255).mean() >= 0.3:
                    cand.append(((lab > 0).sum() - (lab == 255).sum() * 0, y, x))
        cand.sort(reverse=True)
        for _, y, x in cand[:per_course]:
            out.append((c["img"][:, y:y + size, x:x + size].copy(), c["lab"][y:y + size, x:x + size].copy()))
    return out


def evaluate(model, tiles, mean, std):
    import torch
    inter = np.zeros(len(CLASSES))
    union = np.zeros(len(CLASSES))
    m = np.asarray(mean, np.float32)[:, None, None]
    s = np.asarray(std, np.float32)[:, None, None]
    model.eval()
    with torch.inference_mode():
        for i in range(0, len(tiles), 4):
            chunk = tiles[i:i + 4]
            x = np.stack([(t[0].astype(np.float32) - m) / s for t in chunk])
            pred = model(torch.from_numpy(x)).argmax(1).numpy()
            for p, (_, lab) in zip(pred, chunk):
                v = lab != 255
                for k in range(1, len(CLASSES)):
                    a, t = (p == k) & v, (lab == k) & v
                    inter[k] += (a & t).sum()
                    union[k] += (a | t).sum()
    model.train()
    iou = {CLASSES[k]: round(float(inter[k] / union[k]), 4) if union[k] else None for k in range(1, len(CLASSES))}
    iou["mean"] = round(float(np.mean([v for v in iou.values() if v is not None])), 4)
    return iou


def build_model(init):
    import segmentation_models_pytorch as smp
    import torch
    from safetensors.torch import load_file
    cfg = json.load(open(os.path.join(init, "config.json")))
    model = smp.Unet(cfg.get("encoder_name", "resnet34"), encoder_weights=None, in_channels=cfg.get("in_channels", 4),
                     classes=cfg.get("classes", 6))
    sd = load_file(os.path.join(init, "model.safetensors"))
    own = model.state_dict()
    if set(sd) != set(own):
        raise SystemExit(f"state-dict names differ from --init: missing {sorted(set(own) - set(sd))[:5]} "
                         f"extra {sorted(set(sd) - set(own))[:5]}")
    model.load_state_dict({k: v.float() for k, v in sd.items()})
    return model.float(), sorted(sd)


def export(model, out, pre, log_d, names):
    import copy
    os.makedirs(out, exist_ok=True)
    m = copy.deepcopy(model).eval().half()
    m.save_pretrained(out)
    from safetensors.torch import load_file
    got = sorted(load_file(os.path.join(out, "model.safetensors")))
    if got != names:
        raise SystemExit("exported state-dict names differ from --init's")
    json.dump(pre, open(os.path.join(out, "preprocessor_config.json"), "w"), indent=1)
    json.dump(log_d, open(os.path.join(out, "train_log.json"), "w"), indent=1)
    log("exported", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--init", required=True, help="v1 model dir (config.json, model.safetensors, preprocessor_config)")
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--minutes", type=float, default=300.0, help="training time of this job")
    ap.add_argument("--total-minutes", type=float, default=600.0, help="training time of all jobs (the schedule)")
    ap.add_argument("--size", type=int, default=320)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--pool", type=int, default=96)
    ap.add_argument("--swap-s", type=float, default=5.0)
    ap.add_argument("--class-p", default="0.2,0.3,0.1,0.15,0.25", help="green,tee,fairway,bunker,water crop centres")
    ap.add_argument("--boost", default="1,1.25,1,1,1.25", help="CE weight factor green,tee,fairway,bunker,water")
    ap.add_argument("--eval-every", type=int, default=1500)
    ap.add_argument("--ckpt-min", type=float, default=25.0)
    ap.add_argument("--max-val", type=int, default=60, help="validation courses")
    ap.add_argument("--val-share", type=float, default=0.04)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    pre = json.load(open(os.path.join(a.init, "preprocessor_config.json")))
    mean, std = pre["image_mean"], pre["image_std"]
    rows = read_index(a.data)
    val_rows = sorted([r for r in rows if is_val(r["osm"], a.val_share)], key=lambda r: r["osm"])[:a.max_val]
    vset = {r["osm"] for r in val_rows}
    tr_rows = [r for r in rows if r["osm"] not in vset and not is_val(r["osm"], a.val_share)]
    freq = np.zeros(len(CLASSES))
    for r in tr_rows:
        px = r.get("pixels") or {}
        feat = sum(px.get(c, 0) for c in CLASSES[1:])
        freq[0] += max(0, r.get("inside", 0) - feat)
        for k, c in enumerate(CLASSES[1:], 1):
            freq[k] += px.get(c, 0)
    w = 1 / np.sqrt(np.maximum(freq / freq.sum(), 1e-4))
    w = w / w.mean()
    boost = [1.0] + [float(v) for v in a.boost.split(",")]
    w = w * np.asarray(boost)
    class_p = [float(v) for v in a.class_p.split(",")]
    states = sorted({r.get("state") for r in tr_rows if r.get("state")})
    log(f"{len(rows)} courses: {len(tr_rows)} train ({len(states)} states) / {len(val_rows)} val; "
        f"class freq {np.round(freq / freq.sum(), 4)} -> CE weights {np.round(w, 3)}")
    rng = np.random.default_rng(a.seed + (int(time.time()) if a.resume else 0))
    model, names = build_model(a.init)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    ce = torch.nn.CrossEntropyLoss(weight=torch.tensor(w, dtype=torch.float32), ignore_index=255)
    state = dict(step=0, total=None, best=None, best_iou=-1.0, val=[], steps=[], jobs=[])
    best_sd = None
    if a.resume and os.path.exists(a.ckpt):
        ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
        model.load_state_dict(ck["model"])
        opt.load_state_dict(ck["opt"])
        state, best_sd = ck["state"], ck.get("best_sd")
        del ck
        log("resumed at step", state["step"], "of", state["total"])
    tiles = val_tiles(val_rows)
    log(len(tiles), "validation tiles")
    if state["step"] == 0:
        v0 = evaluate(model, tiles, mean, std)
        state["val"].append(dict(step=0, iou=v0, note="init (v1 weights)"))
        log("val init", v0)
    pool = Pool(tr_rows, a.pool, a.swap_s, a.seed + state["step"])
    log("pool ready", len(pool.items), "courses")

    def lr_at(step):
        T = state["total"]
        wu = max(1, int(0.03 * T))
        if step < wu:
            return a.lr * (0.1 + 0.9 * step / wu)
        return a.lr * (0.02 + 0.98 * 0.5 * (1 + math.cos(math.pi * min(1.0, (step - wu) / max(1, T - wu)))))

    model.train()
    t0 = time.time()
    if state["total"] is None:
        x, y = batch(pool, a.size, a.bs, rng, mean, std, class_p)
        t1 = time.time()
        out = model(torch.from_numpy(x))
        (ce(out, torch.from_numpy(y)) + 0.5 * dice_loss(out, torch.from_numpy(y))).backward()
        opt.zero_grad()
        step_s = time.time() - t1 + 0.05
        state["total"] = max(100, int(a.total_minutes * 60 * 0.97 / (step_s * 1.08)))
        log(f"step {step_s:.2f}s -> {state['total']} steps planned over {a.total_minutes:.0f} min")
    job = dict(start_step=state["step"], started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    last_ck = time.time()
    run = None

    def save_ckpt():
        torch.save(dict(model=model.state_dict(), opt=opt.state_dict(), state=state, best_sd=best_sd), a.ckpt + ".tmp")
        os.replace(a.ckpt + ".tmp", a.ckpt)

    while state["step"] < state["total"]:
        step = state["step"] + 1
        for g in opt.param_groups:
            g["lr"] = lr_at(step)
        x, y = batch(pool, a.size, a.bs, rng, mean, std, class_p)
        xt, yt = torch.from_numpy(x), torch.from_numpy(y)
        out = model(xt)
        loss = ce(out, yt) + 0.5 * dice_loss(out, yt)
        opt.zero_grad()
        loss.backward()
        opt.step()
        state["step"] = step
        run = float(loss) if run is None else 0.98 * run + 0.02 * float(loss)
        if step % 50 == 0:
            state["steps"].append([step, round(run, 4), round(time.time() - t0)])
            log(f"step {step}/{state['total']} loss {run:.4f} lr {lr_at(step):.2e} {time.time() - t0:.0f}s "
                f"(pool loads {pool.loaded})")
        if step % a.eval_every == 0 or step == state["total"]:
            v = evaluate(model, tiles, mean, std)
            state["val"].append(dict(step=step, iou=v))
            log("val", step, v)
            if v["mean"] > state["best_iou"]:
                state["best_iou"], state["best"] = v["mean"], step
                best_sd = {k: t.detach().clone() for k, t in model.state_dict().items()}
        if time.time() - last_ck > a.ckpt_min * 60:
            save_ckpt()
            last_ck = time.time()
        if time.time() - t0 > a.minutes * 60:
            log("job time budget reached at step", step)
            break
    pool.stop = True
    if not state["val"] or state["val"][-1]["step"] != state["step"]:
        v = evaluate(model, tiles, mean, std)
        state["val"].append(dict(step=state["step"], iou=v))
        log("val", state["step"], v)
        if v["mean"] > state["best_iou"]:
            state["best_iou"], state["best"] = v["mean"], state["step"]
            best_sd = {k: t.detach().clone() for k, t in model.state_dict().items()}
    job.update(end_step=state["step"], minutes=round((time.time() - t0) / 60, 1))
    state["jobs"].append(job)
    save_ckpt()
    final = state["step"] >= state["total"]
    exp = model
    if best_sd is not None:
        exp, _ = build_model(a.init)
        exp.load_state_dict(best_sd)
    pre2 = dict(pre)
    pre2["licence"] = ("ours (course_data/segment/train, v2 fine-tune of golfseg_own); labels OpenStreetMap contributors "
                       "ODbL 1.0; imagery USDA NAIP; encoder init torchvision ImageNet ResNet weights (BSD-3)")
    log_d = dict(state=dict((k, v) for k, v in state.items()), final=final, exported_step=state["best"] or state["step"],
                 exported_val=next((v for v in state["val"] if v["step"] == state["best"]), None),
                 init_val=state["val"][0] if state["val"] else None, mean=mean, std=std, class_weights=w.tolist(),
                 class_p=class_p, size=a.size, bs=a.bs, lr=a.lr, pool=a.pool, courses_train=len(tr_rows),
                 courses_val=sorted(vset), states_train=states, init=os.path.basename(os.path.normpath(a.init)))
    export(exp, a.out, pre2, log_d, names)


if __name__ == "__main__":
    main()
