"""Pixel-level hazard detection for the GPS-app screenshots.

  python3 spirit_hollow/vision.py            -> output/vision_report.md + output/vision/*.png

Pipeline
  1. Mask the app's own drawings (red line/dots, white yardage bars, black hole outline,
     buttons, header and footer) so they are never learned or scored.
  2. Per-pixel features at half resolution (460 x 1000 frame = 2 screen px per feature px):
       colour  - CIE Lab and HSV, each Gaussian-smoothed at two scales
       index   - excess-green ExG = 2g - r - b (chromatic), a standard vegetation index
       texture - local std of L at 3 window sizes, mean gradient magnitude, Laplacian energy
                 and a difference-of-Gaussians band (canopy is speckled, mown turf is smooth)
       context - each texture measure averaged over a wider ring (woods are big and rough)
  3. Labels from the traced, full-zoom-reviewed outlines in course.py, eroded 3 px so that
     boundary mistakes don't become training labels. OB polygons are semantic (houses /
     roads) and are left out; untraced pixels are 'rough'.
  4. Gradient-boosted trees, evaluated leave-one-hole-out: train on every other hole,
     predict the held-out one. That is the honest accuracy number, since each hole's
     map was never seen in training.
  5. QA: in each hole's landing zone (220-340 yds out, +/-45 yds of the line), flag every
     region where the classifier confidently (p >= 0.8) disagrees with the traced map.

The traced map stays the source of truth for the strategy; the classifier is a second
pair of eyes that points at places worth re-checking.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE]

import course                                  # noqa: E402
import tee_strategy as t                       # noqa: E402

t.HOLES = course.HOLES
CLASSES = ["fairway", "rough", "trees", "native", "water", "sand"]
TRACE_TO_CLASS = {"fairway": "fairway", "recovery": "trees", "native": "native", "water": "water",
                  "sand": "sand"}
SCALE = 2                                      # feature px = 2 screen px
W, H = 920 // SCALE, 2000 // SCALE
TOP, BOTTOM = 545, 1830                        # app header / footer, in screen px


def load_rgb(image):
    im = Image.open(os.path.join(HERE, "screenshots", image)).convert("RGB").resize((920, 2000))
    return np.asarray(im).astype(np.float32) / 255.0


def ui_mask(rgb):
    """True where the pixel is app UI rather than ground."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    red = (r > 0.7) & (g < 0.3) & (b < 0.3)
    white = (r > 0.9) & (g > 0.9) & (b > 0.9)
    black = (r < 0.09) & (g < 0.09) & (b < 0.09)              # the hole outline is pure black
    m = red | white | black
    m = ndimage.binary_dilation(m, iterations=4)
    m[:TOP] = True
    m[BOTTOM:] = True
    m[540:660, 20:230] = True                                 # "Abstract" button + scale bar
    m[540:870, 750:900] = True                                # +, -, 3D buttons
    return m


def rgb_to_lab(rgb):
    def lin(c):
        return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    rl, gl, bl = lin(rgb[..., 0]), lin(rgb[..., 1]), lin(rgb[..., 2])
    x = (0.4124 * rl + 0.3576 * gl + 0.1805 * bl) / 0.9505
    y = 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
    z = (0.0193 * rl + 0.1192 * gl + 0.9505 * bl) / 1.089

    def f(u):
        return np.where(u > 0.008856, np.cbrt(u), 7.787 * u + 16 / 116)
    fx, fy, fz = f(x), f(y), f(z)
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], axis=-1)


def rgb_to_hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn + 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    return np.stack([np.cos(2 * np.pi * h), np.sin(2 * np.pi * h), d / (mx + 1e-6), mx], axis=-1)


def features(rgb, mask):
    """Stack of per-pixel features at half resolution. UI pixels are in-painted first
    (nearest valid pixel) so the app's lines don't bleed into the filters."""
    idx = ndimage.distance_transform_edt(mask, return_distances=False, return_indices=True)
    clean = rgb[tuple(idx)]
    small = np.asarray(Image.fromarray((clean * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                       np.float32) / 255.0
    lab, hsv = rgb_to_lab(small), rgb_to_hsv(small)
    s = small.sum(-1) + 1e-6
    exg = (2 * small[..., 1] - small[..., 0] - small[..., 2]) / s
    L = lab[..., 0]
    feats = []
    for sigma in (1.5, 5):
        feats += [ndimage.gaussian_filter(lab[..., c], sigma) for c in range(3)]
        feats += [ndimage.gaussian_filter(hsv[..., c], sigma) for c in range(4)]
        feats.append(ndimage.gaussian_filter(exg, sigma))
    tex = []
    for win in (3, 7, 15):
        m1 = ndimage.uniform_filter(L, win)
        m2 = ndimage.uniform_filter(L * L, win)
        tex.append(np.sqrt(np.maximum(m2 - m1 * m1, 0)))
    gm = np.hypot(ndimage.sobel(L, 0), ndimage.sobel(L, 1))
    tex.append(ndimage.uniform_filter(gm, 7))
    tex.append(ndimage.uniform_filter(np.abs(ndimage.laplace(ndimage.gaussian_filter(L, 1))), 7))
    tex.append(ndimage.gaussian_filter(L, 1) - ndimage.gaussian_filter(L, 4))
    feats += tex
    feats += [ndimage.uniform_filter(x, 31) for x in tex[:4]]          # context ring
    return np.stack(feats, axis=-1)


def label_map(hole):
    """Traced outlines -> class index per feature pixel (-1 = don't train on it)."""
    from matplotlib.path import Path
    yy, xx = np.mgrid[0:H, 0:W]
    pts = np.c_[(xx.ravel() + 0.5) * SCALE, (yy.ravel() + 0.5) * SCALE]
    lab = np.full(H * W, CLASSES.index("rough"), np.int16)
    ob = np.zeros(H * W, bool)
    for name, poly in course.HOLES[hole]["zones"]:
        inside = Path(poly).contains_points(pts)
        if name == "ob":
            ob |= inside
        elif name in TRACE_TO_CLASS:
            lab[inside] = CLASSES.index(TRACE_TO_CLASS[name])
            ob[inside] = False
    lab = lab.reshape(H, W)
    hd = course.HOLES[hole]
    ppy = t.hole_frame(hd)[3]
    near_fw = ndimage.binary_dilation(lab == CLASSES.index("fairway"),
                                      iterations=max(1, int(25 * ppy / SCALE)))
    lab[(lab == CLASSES.index("rough")) & ~near_fw] = -1        # untraced far away != rough
    keep = np.zeros((H, W), bool)
    for c in range(len(CLASSES)):                                 # erode each class 3 px
        keep |= ndimage.binary_erosion(lab == c, iterations=3)
    lab = np.where(keep & ~ob.reshape(H, W) & (lab >= 0), lab, -1)
    return lab


def landing_mask(hole):
    """Feature pixels within 220-340 yds of the tee and +/-45 yds of the line."""
    hd = course.HOLES[hole]
    tee, fwd, right, ppy = t.hole_frame(hd)
    yy, xx = np.mgrid[0:H, 0:W]
    p = np.stack([(xx + 0.5) * SCALE - tee[0], (yy + 0.5) * SCALE - tee[1]], -1) / ppy
    along, lat = p @ fwd, p @ right
    return (along > 220) & (along < 340) & (np.abs(lat) < 45), ppy


N_COLOUR = 16                                   # first 16 features are colour (2 scales x 8)


def fairway_reference(hole, F, msmall):
    """Median colour features of this photo's own fairway, from a robust sample: the
    corridor 230-300 yds along the app line, +/-6 yds, ignoring UI. The app line is drawn
    down the fairway on almost every hole, so the median is fairway even when a few
    samples fall in rough or a bunker."""
    hd = course.HOLES[hole]
    tee, fwd, right, ppy = t.hole_frame(hd)
    yy, xx = np.mgrid[0:H, 0:W]
    p = np.stack([(xx + 0.5) * SCALE - tee[0], (yy + 0.5) * SCALE - tee[1]], -1) / ppy
    along, lat = p @ fwd, p @ right
    sel = (along > 230) & (along < 300) & (np.abs(lat) > 3) & (np.abs(lat) < 9) & ~msmall
    return np.median(F[sel][:, :N_COLOUR], axis=0)


FEATS = os.environ.get("VISION_FEATS", "hand")   # hand | deep | both


def load_deep(image):
    """DINOv2 ViT-S/14 patch features (computed on GitHub Actions, see deep/), on our grid."""
    sys.path.insert(0, os.path.join(HERE, "deep"))
    from extract_features import load_grid
    return load_grid(os.path.splitext(image)[0]).astype(np.float32)


def build_dataset():
    data = {}
    for h, hd in course.HOLES.items():
        rgb = load_rgb(hd["image"])
        m = ui_mask(rgb)
        F = features(rgb, m)
        msmall0 = np.asarray(Image.fromarray(m).resize((W, H), Image.NEAREST))
        ref = fairway_reference(h, F, msmall0)
        F = np.concatenate([F, F[..., :N_COLOUR] - ref], axis=-1)   # absolute + relative colour
        if FEATS in ("deep", "both"):
            deep = load_deep(hd["image"])
            F = deep if FEATS == "deep" else np.concatenate([F, deep], axis=-1)
        msmall = np.asarray(Image.fromarray(m).resize((W, H), Image.NEAREST))
        lab = label_map(h)
        lab[msmall] = -1
        data[h] = (F, lab, msmall, rgb)
    return data


def fit(X, y, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    clf = HistGradientBoostingClassifier(max_iter=160, learning_rate=0.08, max_leaf_nodes=48,
                                         l2_regularization=1.0, class_weight="balanced",
                                         random_state=seed)
    clf.fit(X, y)
    return clf


def sample(F, lab, n, rng):
    ii = np.flatnonzero(lab.ravel() >= 0)
    ii = rng.choice(ii, min(n, len(ii)), replace=False)
    return F.reshape(-1, F.shape[-1])[ii], lab.ravel()[ii]


def superpixels(rgb, msmall, n=2500):
    """SLIC regions on the (UI-in-painted) half-res photo."""
    from skimage.segmentation import slic
    small = np.asarray(Image.fromarray((rgb * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR))
    seg = slic(small, n_segments=n, compactness=12, start_label=0, mask=~msmall)
    return seg


def region_features(F, seg):
    """Mean and std of every pixel feature inside each region, plus region size."""
    nseg = seg.max() + 1
    flat = F.reshape(-1, F.shape[-1]); sid = seg.ravel()
    ok = sid >= 0
    cnt = np.bincount(sid[ok], minlength=nseg).astype(np.float32)[:, None] + 1e-6
    s1 = np.zeros((nseg, F.shape[-1]), np.float32); s2 = np.zeros_like(s1)
    np.add.at(s1, sid[ok], flat[ok]); np.add.at(s2, sid[ok], flat[ok] ** 2)
    mu = s1 / cnt
    sd = np.sqrt(np.maximum(s2 / cnt - mu ** 2, 0))
    return np.c_[mu, sd, np.log(cnt)]


def region_labels(lab, seg):
    nseg = seg.max() + 1
    out = np.full(nseg, -1, np.int16)
    sid, l = seg.ravel(), lab.ravel()
    ok = (sid >= 0) & (l >= 0)
    votes = np.zeros((nseg, len(CLASSES)), int)
    np.add.at(votes, (sid[ok], l[ok]), 1)
    tot = votes.sum(1)
    good = (tot > 0) & (votes.max(1) >= 0.7 * tot)          # only clear-majority regions
    out[good] = votes[good].argmax(1)
    return out


def main_superpixel():
    """Leave-one-hole-out with region (superpixel) classification; prints the same metrics."""
    data = build_dataset()
    print("features built", flush=True)
    reg = {}
    for h, (F, lab, msmall, rgb) in data.items():
        seg = superpixels(rgb, msmall)
        reg[h] = (seg, region_features(F, seg), region_labels(lab, seg))
    conf = np.zeros((len(CLASSES), len(CLASSES)), int); conf_lz = np.zeros_like(conf)
    for h, (F, lab, msmall, rgb) in data.items():
        X = np.concatenate([reg[k][1][reg[k][2] >= 0] for k in data if k != h])
        y = np.concatenate([reg[k][2][reg[k][2] >= 0] for k in data if k != h])
        clf = fit(X, y)
        seg, RF, _ = reg[h]
        P = clf.predict_proba(RF)
        pred = np.where(seg >= 0, P.argmax(1)[np.maximum(seg, 0)], CLASSES.index("rough"))
        ok = lab >= 0
        lz, _ = landing_mask(h)
        np.add.at(conf, (lab[ok], pred[ok]), 1)
        np.add.at(conf_lz, (lab[ok & lz], pred[ok & lz]), 1)
        print(h, "done", flush=True)
    for cm, name in ((conf, "whole hole"), (conf_lz, "landing zones")):
        pen = [CLASSES.index(c) for c in ("trees", "native", "water", "sand")]
        ply = [CLASSES.index(c) for c in ("fairway", "rough")]
        tp = cm[np.ix_(pen, pen)].sum(); fn = cm[np.ix_(pen, ply)].sum()
        fp = cm[np.ix_(ply, pen)].sum(); tn = cm[np.ix_(ply, ply)].sum()
        print(f"SUPERPIXEL {name}: 6-class {np.trace(cm) / cm.sum():.1%}; penal-vs-playable "
              f"{(tp + tn) / (tp + tn + fp + fn):.1%} (recall {tp / max(tp + fn, 1):.0%}, precision {tp / max(tp + fp, 1):.0%})")


def main():
    rng = np.random.default_rng(0)
    out_dir = os.path.join(HERE, "output", "vision")
    os.makedirs(out_dir, exist_ok=True)
    data = build_dataset()
    print("features built", flush=True)
    per_hole = {h: sample(F, lab, 16000, rng) for h, (F, lab, _, _) in data.items()}
    conf = np.zeros((len(CLASSES), len(CLASSES)), int)
    conf_lz = np.zeros_like(conf)
    flags = {}
    for h, (F, lab, msmall, rgb) in data.items():
        X = np.concatenate([per_hole[k][0] for k in data if k != h])
        y = np.concatenate([per_hole[k][1] for k in data if k != h])
        clf = fit(X, y)
        P = clf.predict_proba(F.reshape(-1, F.shape[-1])).reshape(H, W, -1)
        P = np.stack([ndimage.uniform_filter(P[..., c], 7) for c in range(P.shape[-1])], -1)
        pred = P.argmax(-1)
        ok = lab >= 0
        lz, ppy = landing_mask(h)
        np.add.at(conf, (lab[ok], pred[ok]), 1)
        np.add.at(conf_lz, (lab[ok & lz], pred[ok & lz]), 1)
        # confident disagreements in the landing zone, using the un-eroded traced map
        full = label_map_full(h)
        dis = lz & ~msmall & (P.max(-1) >= 0.8) & (pred != full)
        dis = ndimage.binary_opening(dis, iterations=2)
        comp, n = ndimage.label(dis)
        yd2 = (SCALE / ppy) ** 2
        regions = []
        for i, sl in enumerate(ndimage.find_objects(comp), 1):
            area = (comp[sl] == i).sum() * yd2
            if area < 60:                                          # ignore < ~8x8 yds
                continue
            cy, cx = ndimage.center_of_mass(comp == i)
            tr = CLASSES[np.bincount(full[comp == i]).argmax()]
            pr = CLASSES[np.bincount(pred[comp == i]).argmax()]
            regions.append(dict(area=area, x=cx * SCALE, y=cy * SCALE, traced=tr, seen=pr))
        flags[h] = sorted(regions, key=lambda r: -r["area"])
        save_panel(h, rgb, pred, dis, os.path.join(out_dir, f"{h}.png"))
        print(h, "done", len(regions), "flags", flush=True)
    write_report(conf, conf_lz, flags)


def label_map_full(hole):
    """Un-eroded traced map (what the strategy model actually uses)."""
    from matplotlib.path import Path
    yy, xx = np.mgrid[0:H, 0:W]
    pts = np.c_[(xx.ravel() + 0.5) * SCALE, (yy.ravel() + 0.5) * SCALE]
    lab = np.full(H * W, CLASSES.index("rough"), np.int16)
    for name, poly in course.HOLES[hole]["zones"]:
        if name in TRACE_TO_CLASS:
            lab[Path(poly).contains_points(pts)] = CLASSES.index(TRACE_TO_CLASS[name])
        elif name == "ob":
            lab[Path(poly).contains_points(pts)] = CLASSES.index("rough")
    return lab.reshape(H, W)


PALETTE = np.array([[90, 210, 70], [170, 170, 170], [120, 60, 20], [235, 200, 60], [30, 140, 255],
                    [255, 255, 255]], np.uint8)


def save_panel(h, rgb, pred, dis, path):
    photo = np.asarray(Image.fromarray((rgb * 255).astype(np.uint8)).resize((W, H)))
    seg = PALETTE[pred]
    over = photo.copy()
    over[dis] = [255, 0, 255]
    panel = np.concatenate([photo, seg, over], axis=1)[TOP // SCALE: BOTTOM // SCALE]
    Image.fromarray(panel).save(path)


def write_report(conf, conf_lz, flags):
    def table(cm, title):
        rows = [f"### {title}", "", "| traced \\ seen | " + " | ".join(CLASSES) + " | recall |",
                "|---|" + "---|" * (len(CLASSES) + 1)]
        for i, c in enumerate(CLASSES):
            tot = cm[i].sum()
            rows.append(f"| **{c}** | " + " | ".join(f"{v / max(tot, 1):.0%}" for v in cm[i])
                        + f" | {cm[i, i] / max(tot, 1):.0%} |")
        prec = [cm[i, i] / max(cm[:, i].sum(), 1) for i in range(len(CLASSES))]
        rows.append("| precision | " + " | ".join(f"{p:.0%}" for p in prec) + " | |")
        acc = np.trace(cm) / max(cm.sum(), 1)
        pen = [CLASSES.index(c) for c in ("trees", "native", "water", "sand")]
        ply = [CLASSES.index(c) for c in ("fairway", "rough")]
        tp = cm[np.ix_(pen, pen)].sum(); fn = cm[np.ix_(pen, ply)].sum()
        fp = cm[np.ix_(ply, pen)].sum(); tn = cm[np.ix_(ply, ply)].sum()
        rows += ["", f"Overall pixel accuracy (6 classes): **{acc:.1%}**",
                 f"Penal (trees/long grass/water/sand) vs playable (fairway/rough): accuracy "
                 f"**{(tp + tn) / max(tp + tn + fp + fn, 1):.1%}**, penal recall {tp / max(tp + fn, 1):.0%}, "
                 f"penal precision {tp / max(tp + fp, 1):.0%}", ""]
        return rows

    md = ["# Spirit Hollow — hazard detection (leave-one-hole-out)", "",
          "Each hole is predicted by a model trained only on the *other* holes, so these are "
          "out-of-sample numbers. Rows are the traced (reviewed) label, columns what the "
          "classifier sees.", ""]
    md += table(conf, "Whole visible hole")
    md += table(conf_lz, "Landing zones only (220-340 yds, +/-45 yds)")
    md += ["## Confident disagreements in the landing zones", "",
           "Regions >= 60 sq yds where the classifier is >= 80% sure and disagrees with the map. "
           "Each was checked by eye at full zoom (see the strategy README for outcomes).", "",
           "| Hole | Where (screen x, y) | Size (sq yds) | Map says | Classifier sees |", "|---|---|---|---|---|"]
    for h, regs in flags.items():
        for r in regs[:6]:
            md.append(f"| {h} | {r['x']:.0f}, {r['y']:.0f} | {r['area']:.0f} | {r['traced']} | {r['seen']} |")
        if not regs:
            md.append(f"| {h} | — | — | agrees | — |")
    path = os.path.join(HERE, "output", "vision_report.md")
    with open(path, "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main_superpixel() if "--superpixel" in sys.argv else main()
