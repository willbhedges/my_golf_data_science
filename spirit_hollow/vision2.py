"""Hazard classifier v2: DINOv2 features, region classification, calibration, ensembles.

  python3 spirit_hollow/vision2.py --method all     # LOHO comparison of every method -> report
  python3 spirit_hollow/vision2.py --method best    # + train best on all holes, write prob maps
  python3 spirit_hollow/vision2.py --method c       # LOHO for one method (cached afterwards)
  options: --methods hand,a,b,c   restrict the comparison;  --calib  add nested calibration
  (2 inner group folds per held-out hole = 2 extra HGB fits per hole per method: slow)

Everything (screenshots, UI mask, handcrafted features, labels, landing zones, metrics)
is reused from vision.py so the numbers are directly comparable with its baseline
(handcrafted + HGB, 7x7 smoothing: landing zones 59.4% / 79.2%, whole hole 52.4% / 72.5%).

Methods (all leave-one-hole-out: the held-out hole's pixels are never used for
training, scaling, calibration or ensembling weights):
  hand  handcrafted features + HGB (vision.py baseline, re-run here with this sampler)
  a     DINOv2 (64 PCA ch.) linear probe: standardised multinomial logistic regression
  b     DINOv2 + handcrafted, HGB
  c     (b) with DINOv2 features made photo-relative: the photo's fairway-corridor median
        (same app-line corridor vision.py uses for colour) is subtracted (both raw and
        relative channels kept)
  cpool (c) pixel probabilities mean-pooled inside each region (SAM or SLIC)
  d     region classification: mean/std of (c)'s pixel features per region (SAM regions
        if present for every photo, else SLIC n~2500), trained on >=70%-pure regions
  e*    calibration (temperature / isotonic, fitted on inner group-folds of the TRAINING
        holes only) and the calibrated average of the best two methods
Pixel methods' probabilities are smoothed 7x7 like vision.py before scoring.
"""
import json
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np                                                    # noqa: E402
from PIL import Image                                                 # noqa: E402
from scipy import ndimage                                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "deep")]
import vision as v                                                    # noqa: E402
from vision import CLASSES, H, W, SCALE, TOP, BOTTOM                  # noqa: E402

course, t = v.course, v.t
OUT = os.path.join(HERE, "output", "vision2")
CACHE = os.path.join(OUT, "cache")
SAM_DIR = os.path.join(HERE, "deep", "sam")
NC = len(CLASSES)
PEN = [CLASSES.index(c) for c in ("trees", "native", "water", "sand")]
PLY = [CLASSES.index(c) for c in ("fairway", "rough")]
N_PER_HOLE = 15000
HOLES = list(course.HOLES)


# ----------------------------------------------------------------------------- data
def corridor(hole, msmall):
    """vision.fairway_reference's sample: 230-300 yds along the app line, 3-9 yds off it."""
    tee, fwd, right, ppy = t.hole_frame(course.HOLES[hole])
    yy, xx = np.mgrid[0:H, 0:W]
    p = np.stack([(xx + 0.5) * SCALE - tee[0], (yy + 0.5) * SCALE - tee[1]], -1) / ppy
    along, lat = p @ fwd, p @ right
    return (along > 230) & (along < 300) & (np.abs(lat) > 3) & (np.abs(lat) < 9) & ~msmall


def hole_data(hole):
    """Cached per-hole arrays: hand (H,W,42), deep (H,W,64), deep_rel, labels, masks."""
    path = os.path.join(CACHE, f"hole_{hole}")
    if os.path.exists(os.path.join(path, "done")):          # memory-mapped: processes share pages
        return {f[:-4]: np.load(os.path.join(path, f), mmap_mode="r")
                for f in os.listdir(path) if f.endswith(".npy")}
    if os.path.exists(path + ".npz"):                       # older single-file cache
        z = np.load(path + ".npz")
        d = {k: z[k] for k in z.files}
        save_hole(path, d)
        return hole_data(hole)
    hd = course.HOLES[hole]
    rgb = v.load_rgb(hd["image"])
    m = v.ui_mask(rgb)
    F = v.features(rgb, m)
    msmall = np.asarray(Image.fromarray(m).resize((W, H), Image.NEAREST))
    ref = v.fairway_reference(hole, F, msmall)
    hand = np.concatenate([F, F[..., :v.N_COLOUR] - ref], -1)
    deep = v.load_deep(hd["image"])
    dref = np.median(deep[corridor(hole, msmall)], axis=0)
    lab = v.label_map(hole)
    lab[msmall] = -1
    lz, ppy = v.landing_mask(hole)
    small = np.asarray(Image.fromarray((rgb * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR))
    d = dict(hand=hand.astype(np.float16), deep=deep.astype(np.float16),
             deep_rel=(deep - dref).astype(np.float16), lab=lab, msmall=msmall, lz=lz,
             full=v.label_map_full(hole), ppy=np.float32(ppy), photo=small)
    save_hole(path, d)
    return hole_data(hole)


def save_hole(path, d):
    os.makedirs(path, exist_ok=True)
    for k, a in d.items():
        np.save(os.path.join(path, k + ".npy"), np.asarray(a))
    open(os.path.join(path, "done"), "w").close()


def regions(hole, d, src):
    """src='sam': SAM regions (gaps split into SLIC cells so every ground pixel has a
    region); src='slic': SLIC superpixels. Returns (seg, src)."""
    stem = os.path.splitext(course.HOLES[hole]["image"])[0]
    sam = os.path.join(SAM_DIR, stem + ".npz")
    if src == "sam":
        r = np.load(sam)["regions"].astype(np.int32)
        r[d["msmall"]] = -1
        # SAM leaves gaps; split them into SLIC cells so every ground pixel has a region
        slic = regions_slic(hole, d)
        gap = (r < 0) & (slic >= 0)
        r[gap] = r.max() + 1 + slic[gap]
        _, r2 = np.unique(r, return_inverse=True)
        r2 = r2.reshape(r.shape) - (1 if (r < 0).any() else 0)
        return r2.astype(np.int32), "sam"
    return regions_slic(hole, d), "slic"


def regions_slic(hole, d):
    path = os.path.join(CACHE, f"slic_{hole}.npy")
    if os.path.exists(path):
        return np.load(path)
    from skimage.segmentation import slic
    seg = slic(d["photo"], n_segments=2500, compactness=12, start_label=0, mask=~d["msmall"])
    np.save(path, seg.astype(np.int32))
    return seg.astype(np.int32)


def sam_available():
    stems = [os.path.splitext(hd["image"])[0] for hd in course.HOLES.values()]
    return all(os.path.exists(os.path.join(SAM_DIR, s + ".npz")) for s in stems)


REGION_SRC = "sam" if sam_available() else "slic"
REGION = {"d": REGION_SRC, "dslic": "slic"}          # region classifiers -> region source
POOL = {"cpool": REGION_SRC, "cpool_slic": "slic"}   # (c) probabilities pooled per region


def feats(d, kind):
    if kind == "deep":
        return d["deep"]
    if kind == "hand":
        return d["hand"]
    if kind == "both":
        return np.concatenate([d["hand"], d["deep"]], -1)
    if kind == "both_rel":
        return np.concatenate([d["hand"], d["deep_rel"]], -1)
    raise ValueError(kind)


def feats_at(d, kind, ii):
    """Features of flat pixel indices ii without materialising the full stack."""
    parts = {"deep": ["deep"], "hand": ["hand"], "both": ["hand", "deep"],
             "both_rel": ["hand", "deep_rel"]}[kind]
    return np.concatenate([np.asarray(d[p]).reshape(-1, d[p].shape[-1])[ii] for p in parts],
                          -1).astype(np.float32)


def sample_idx(lab, n, seed):
    ii = np.flatnonzero(lab.ravel() >= 0)
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(ii, min(n, len(ii)), replace=False))


# ----------------------------------------------------------------------------- models
def fit_hgb(X, y, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    clf = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_leaf_nodes=48,
                                         l2_regularization=1.0, class_weight="balanced",
                                         early_stopping=True, validation_fraction=0.1,
                                         n_iter_no_change=10, random_state=seed)
    return clf.fit(X, y)


def fit_logreg(X, y, seed=0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=500,
                                                             class_weight="balanced"))
    return clf.fit(X, y)


def proba(clf, X):
    """predict_proba with all NC columns even if a class was absent in training."""
    P = np.zeros((len(X), NC), np.float32)
    for s in range(0, len(X), 100000):
        p = clf.predict_proba(X[s:s + 100000])
        P[s:s + 100000][:, clf.classes_] = p
    return P


def smooth(P):
    return np.stack([ndimage.uniform_filter(P[..., c], 7) for c in range(NC)], -1)


PIXEL = {"hand": ("hand", fit_hgb), "a": ("deep", fit_logreg), "b": ("both", fit_hgb),
         "c": ("both_rel", fit_hgb)}
# (c) = handcrafted + photo-relative DINOv2 (deep minus this photo's fairway-corridor median)


def pixel_train(method, holes, data, n=N_PER_HOLE, seed=0):
    kind, fitter = PIXEL[method]
    X, y = [], []
    for k in holes:
        ii = sample_idx(data[k]["lab"], n, seed + HOLES.index(k))
        X.append(feats_at(data[k], kind, ii))
        y.append(data[k]["lab"].ravel()[ii])
    return fitter(np.concatenate(X), np.concatenate(y), seed)


def pixel_predict(method, clf, d):
    kind = PIXEL[method][0]
    F = feats(d, kind)
    P = proba(clf, F.reshape(-1, F.shape[-1]).astype(np.float32)).reshape(H, W, NC)
    return smooth(P)


def region_table(hole, d, src):
    """Region features (mean/std of method-c features + log size) and pure labels."""
    seg, _ = regions(hole, d, src)
    path = os.path.join(CACHE, f"rfeat_{src}_{hole}.npz")
    if os.path.exists(path):
        z = np.load(path)
        return seg, z["RF"], z["rl"]
    F = feats(d, "both_rel").astype(np.float32)
    RF = v.region_features(F, seg).astype(np.float32)
    rl = v.region_labels(d["lab"], seg)
    np.savez(path, RF=RF, rl=rl)
    return seg, RF, rl


def region_train(holes, data, src, seed=0):
    X, y = [], []
    for k in holes:
        _, RF, rl = region_table(k, data[k], src)
        X.append(RF[rl >= 0]); y.append(rl[rl >= 0])
    return fit_hgb(np.concatenate(X), np.concatenate(y), seed)


def region_predict(clf, hole, d, src):
    seg, RF, _ = region_table(hole, d, src)
    Pr = proba(clf, RF)
    P = Pr[np.maximum(seg, 0)]
    P[seg < 0] = np.eye(NC)[CLASSES.index("rough")]
    return P


def pool(P, seg):
    """Mean of pixel probabilities inside each region."""
    n = seg.max() + 1
    ok = seg >= 0
    cnt = np.bincount(seg[ok], minlength=n)[:, None] + 1e-6
    S = np.stack([np.bincount(seg[ok], P[..., c][ok], minlength=n) for c in range(NC)], -1)
    Q = P.copy()
    Q[ok] = (S / cnt)[seg[ok]]
    return Q


# ----------------------------------------------------------------------------- LOHO
def oof_path(method, hole):
    return os.path.join(CACHE, f"oof_{method}_{hole}.npy")


def loho(method, data):
    """Out-of-fold probability maps for a base method (cached as float16)."""
    out = {}
    for h in HOLES:
        p = oof_path(method, h)
        if os.path.exists(p):
            out[h] = np.load(p).astype(np.float32)
            continue
        t0 = time.time()
        train = [k for k in HOLES if k != h]
        if method in PIXEL:
            P = pixel_predict(method, pixel_train(method, train, data), data[h])
        elif method in POOL:
            seg, _ = regions(h, data[h], POOL[method])
            P = pool(loho_single("c", h, data), seg)
        elif method in REGION:
            P = region_predict(region_train(train, data, REGION[method]), h, data[h], REGION[method])
        else:
            raise ValueError(method)
        np.save(p, P.astype(np.float16))
        out[h] = P
        print(f"  {method} {h}: {time.time() - t0:.0f}s", flush=True)
    return out


def loho_single(method, h, data):
    p = oof_path(method, h)
    if not os.path.exists(p):
        loho(method, data)
    return np.load(p).astype(np.float32)


# ----------------------------------------------------------------------------- calibration
INNER_FOLDS = 2
N_CAL = 4000                     # calibration pixels per inner-held-out hole


def inner_oof(method, h, data):
    """Out-of-fold probabilities for a sample of labelled pixels of every TRAINING hole
    (holes other than h), from 2 group folds over those holes. h is never touched."""
    path = os.path.join(CACHE, f"inner_{method}_{h}.npz")
    if os.path.exists(path):
        z = np.load(path)
        return z["P"], z["y"]
    train = [k for k in HOLES if k != h]
    folds = [train[i::INNER_FOLDS] for i in range(INNER_FOLDS)]
    Ps, ys = [], []
    for fold in folds:
        rest = [k for k in train if k not in fold]
        if method in PIXEL:
            clf = pixel_train(method, rest, data)
        elif method in REGION:
            clf = region_train(rest, data, REGION[method])
        for k in fold:
            if method in PIXEL:
                P = pixel_predict(method, clf, data[k])
            elif method in REGION:
                P = region_predict(clf, k, data[k], REGION[method])
            else:
                raise ValueError(method)
            ii = sample_idx(data[k]["lab"], N_CAL, 1000 + HOLES.index(k))
            Ps.append(P.reshape(-1, NC)[ii]); ys.append(data[k]["lab"].ravel()[ii])
    P, y = np.concatenate(Ps), np.concatenate(ys)
    np.savez(path, P=P, y=y)
    return P, y


def fit_temperature(P, y):
    from scipy.optimize import minimize_scalar
    L = np.log(np.clip(P, 1e-6, 1))
    def nll(T):
        z = L / T
        z = z - z.max(1, keepdims=True)
        lp = z - np.log(np.exp(z).sum(1, keepdims=True))
        return -lp[np.arange(len(y)), y].mean()
    return minimize_scalar(nll, bounds=(0.05, 20), method="bounded").x


def apply_temperature(P, T):
    z = np.log(np.clip(P, 1e-6, 1)) / T
    z -= z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


def fit_isotonic(P, y):
    from sklearn.isotonic import IsotonicRegression
    return [IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(P[:, c], y == c)
            for c in range(NC)]


def apply_isotonic(P, isos):
    shp = P.shape
    Q = np.stack([iso.predict(P.reshape(-1, NC)[:, c]) for c, iso in enumerate(isos)], -1)
    Q = np.maximum(Q, 1e-4)
    Q /= Q.sum(-1, keepdims=True)
    return Q.reshape(shp).astype(np.float32)


def calibrated(method, how, data):
    """LOHO maps of `method` calibrated with params fitted on inner folds of the training holes."""
    out = {}
    base = loho(method, data)
    for h in HOLES:
        P, y = inner_oof(method, h, data)
        if how == "temp":
            out[h] = apply_temperature(base[h], fit_temperature(P, y)).astype(np.float32)
        else:
            out[h] = apply_isotonic(base[h], fit_isotonic(P, y))
        print(f"  cal {method}/{how} {h}", flush=True)
    return out


# ----------------------------------------------------------------------------- metrics
def confusion(maps, data, zone):
    cm = np.zeros((NC, NC), np.int64)
    for h, P in maps.items():
        d = data[h]
        ok = d["lab"] >= 0
        if zone == "lz":
            ok &= d["lz"]
        np.add.at(cm, (d["lab"][ok], P.argmax(-1)[ok]), 1)
    return cm


def summary(cm):
    tp = cm[np.ix_(PEN, PEN)].sum(); fn = cm[np.ix_(PEN, PLY)].sum()
    fp = cm[np.ix_(PLY, PEN)].sum(); tn = cm[np.ix_(PLY, PLY)].sum()
    return dict(acc6=np.trace(cm) / cm.sum(), pp=(tp + tn) / (tp + tn + fp + fn),
                rec=tp / max(tp + fn, 1), prec=tp / max(tp + fp, 1),
                bal6=np.mean([cm[i, i] / max(cm[i].sum(), 1) for i in range(NC)]))


def nll_ece(maps, data, zone="all", n=20000):
    """Pixel NLL and 15-bin top-label ECE on labelled pixels (a fixed sample per hole)."""
    Ps, ys = [], []
    for h, P in maps.items():
        d = data[h]
        ok = d["lab"] >= 0
        if zone == "lz":
            ok &= d["lz"]
        ii = np.flatnonzero(ok.ravel())
        ii = np.random.default_rng(7).choice(ii, min(n, len(ii)), replace=False)
        Ps.append(P.reshape(-1, NC)[ii]); ys.append(d["lab"].ravel()[ii])
    P, y = np.concatenate(Ps), np.concatenate(ys)
    nll = -np.log(np.clip(P[np.arange(len(y)), y], 1e-6, 1)).mean()
    conf, pred = P.max(1), P.argmax(1)
    bins = np.minimum((conf * 15).astype(int), 14)
    ece = sum(abs((pred[bins == b] == y[bins == b]).mean() - conf[bins == b].mean()) * (bins == b).mean()
              for b in range(15) if (bins == b).any())
    hi = conf >= 0.85
    return nll, ece, (pred[hi] == y[hi]).mean() if hi.any() else np.nan, hi.mean()


def flags_for(P, d, thr=0.85):
    """Confident (p>=thr) landing-zone disagreements with the un-eroded traced map."""
    pred = P.argmax(-1)
    full = d["full"]
    dis = d["lz"] & ~d["msmall"] & (P.max(-1) >= thr) & (pred != full)
    dis = ndimage.binary_opening(dis, iterations=2)
    comp, n = ndimage.label(dis)
    yd2 = (SCALE / float(d["ppy"])) ** 2
    regs = []
    for i in range(1, n + 1):
        r = comp == i
        area = r.sum() * yd2
        if area < 60:
            continue
        cy, cx = ndimage.center_of_mass(r)
        regs.append(dict(area=float(area), x=float(cx * SCALE), y=float(cy * SCALE),
                         traced=CLASSES[np.bincount(full[r], minlength=NC).argmax()],
                         seen=CLASSES[np.bincount(pred[r], minlength=NC).argmax()],
                         p=float(P.max(-1)[r].mean())))
    return sorted(regs, key=lambda r: -r["area"]), dis


# ----------------------------------------------------------------------------- report
DESC = {
    "hand": "Handcrafted + HGB (baseline features, this script's sampler)",
    "a": "(a) DINOv2 linear probe (std. multinomial logreg)",
    "b": "(b) DINOv2 + handcrafted, HGB",
    "c": "(c) handcrafted + photo-relative DINOv2 (fairway-corridor median subtracted), HGB",
    "cpool": f"(c) probabilities mean-pooled per {REGION_SRC.upper()} region",
    "cpool_slic": "(c) probabilities mean-pooled per SLIC superpixel",
    "d": f"(d) region classifier on {REGION_SRC.upper()} regions (mean/std per region, HGB)",
    "dslic": "(d') region classifier on SLIC superpixels (mean/std per region, HGB)",
}


def cm_table(cm, title):
    rows = [f"#### {title}", "", "| traced \\ seen | " + " | ".join(CLASSES) + " | recall |",
            "|---|" + "---|" * (NC + 1)]
    for i, c in enumerate(CLASSES):
        tot = max(cm[i].sum(), 1)
        rows.append(f"| **{c}** | " + " | ".join(f"{x / tot:.0%}" for x in cm[i])
                    + f" | {cm[i, i] / tot:.0%} |")
    prec = [cm[i, i] / max(cm[:, i].sum(), 1) for i in range(NC)]
    rows += ["| precision | " + " | ".join(f"{p:.0%}" for p in prec) + " | |", ""]
    return rows


def write_report(results, best, best_maps, data, extra):
    md = ["# Spirit Hollow — hazard classifier v2 (leave-one-hole-out)", "",
          "Every number is out-of-sample: each hole is scored with a model trained only on the "
          "other 15 holes. Calibration maps (when run, `--calib`) are fitted on inner "
          "2-group-fold predictions over those 15 training holes, so the held-out hole contributes nothing to training, "
          "feature scaling, calibration or ensemble weights (the ensemble is a fixed 50/50 "
          "average). Pixel methods are 7x7-smoothed before scoring, as in vision.py. "
          f"Regions for (d)/pooling: **{REGION_SRC.upper()}**"
          + (" (SAM masks for all photos; gaps filled with SLIC cells)." if REGION_SRC == "sam"
             else " superpixels (n~2500, compactness 12) — SAM masks were not available.") , "",
          "Penal = trees/native/water/sand, playable = fairway/rough. 'bal' = mean per-class "
          "recall. Landing zones = 220-340 yds, +/-45 yds of the line.", "",
          "| Method | LZ 6-class | LZ bal | LZ penal-vs-playable | LZ penal recall | LZ penal precision "
          "| Hole 6-class | Hole penal-vs-playable | Hole penal recall | Hole penal precision | NLL | ECE |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|",
          "| vision.py baseline (as reported) | 59.4% | | 79.2% | 69% | 55% | 52.4% | 72.5% | 72% | 75% | | |"]
    for name, r in results.items():
        L, A = r["lz"], r["all"]
        mark = "**" if name == best else ""
        md.append(f"| {mark}{r['desc']}{mark} | {L['acc6']:.1%} | {L['bal6']:.1%} | {L['pp']:.1%} | "
                  f"{L['rec']:.0%} | {L['prec']:.0%} | {A['acc6']:.1%} | {A['pp']:.1%} | {A['rec']:.0%} | "
                  f"{A['prec']:.0%} | {r['nll']:.2f} | {r['ece']:.3f} |")
    md += ["", f"Best (by landing-zone penal-vs-playable accuracy, then 6-class): **{results[best]['desc']}**.",
           "", "Reliability of confident pixels (p>=0.85, whole hole, labelled pixels):", "",
           "| Method | share of pixels with p>=0.85 | accuracy of those |", "|---|---|---|"]
    for name, r in results.items():
        md.append(f"| {r['desc']} | {r['hi_share']:.1%} | {r['hi_acc']:.1%} |")
    md += ["", "Per-hole landing-zone accuracy of the best method (6-class / penal-vs-playable):", "",
           "| Hole | " + " | ".join(str(h) for h in HOLES) + " |", "|---|" + "---|" * len(HOLES)]
    a6, ap = [], []
    for h in HOLES:
        s = summary(confusion({h: best_maps[h]}, data, "lz"))
        a6.append(f"{s['acc6']:.0%}"); ap.append(f"{s['pp']:.0%}")
    md += ["| 6-class | " + " | ".join(a6) + " |", "| penal | " + " | ".join(ap) + " |", ""]
    md += ["## Confusion matrices — best method (LOHO)", ""]
    md += cm_table(confusion(best_maps, data, "all"), "Whole visible hole")
    md += cm_table(confusion(best_maps, data, "lz"), "Landing zones")
    md += ["## Confident landing-zone disagreements with the traced map", "",
           "From the best method's LOHO maps (the hole's own map was never seen). Regions "
           ">= 60 sq yds where p >= 0.85 and the predicted class differs from the un-eroded "
           "traced map; x/y are screen px in the 920x2000 frame. Images with the regions in "
           "magenta: output/vision2/<hole>.png.", "",
           "| Hole | Screen x, y | Area (sq yds) | Map says | Classifier sees | mean p |",
           "|---|---|---|---|---|---|"]
    for h in HOLES:
        regs = extra["flags"][h]
        for r in regs:
            md.append(f"| {h} | {r['x']:.0f}, {r['y']:.0f} | {r['area']:.0f} | {r['traced']} | "
                      f"{r['seen']} | {r['p']:.2f} |")
        if not regs:
            md.append(f"| {h} | — | — | agrees | — | |")
    md += ["", "## Notes", ""] + extra.get("notes", [])
    with open(os.path.join(HERE, "output", "vision2_report.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[:30]))


def save_panel(h, d, P, dis):
    seg = v.PALETTE[P.argmax(-1)]
    over = d["photo"].copy()
    over[dis] = [255, 0, 255]
    panel = np.concatenate([d["photo"], seg, over], axis=1)[TOP // SCALE: BOTTOM // SCALE]
    Image.fromarray(panel).save(os.path.join(OUT, f"{h}.png"))


# ----------------------------------------------------------------------------- driver
def evaluate(maps, data, desc):
    nll, ece, hi_acc, hi_share = nll_ece(maps, data)
    return dict(desc=desc, lz=summary(confusion(maps, data, "lz")),
                all=summary(confusion(maps, data, "all")), nll=nll, ece=ece,
                hi_acc=hi_acc, hi_share=hi_share)


def score_key(r):
    return (round(r["lz"]["pp"], 3), r["lz"]["acc6"])


def run_all(data, methods, calib):
    results, maps = {}, {}
    for m in methods:
        print("method", m, flush=True)
        maps[m] = loho(m, data)
        results[m] = evaluate(maps[m], data, DESC[m])
        r = results[m]
        print(f"  -> LZ {r['lz']['acc6']:.1%} / {r['lz']['pp']:.1%}  hole {r['all']['acc6']:.1%} / "
              f"{r['all']['pp']:.1%}", flush=True)
    # top two base methods from different families (a method and its pooled self don't pair)
    family = lambda m: "c" if m in POOL else m                     # noqa: E731
    ranked = sorted(methods, key=lambda m: score_key(results[m]), reverse=True)
    top2 = [ranked[0]] + [m for m in ranked[1:] if family(m) != family(ranked[0])][:1]
    k = "ens_raw"
    maps[k] = {h: 0.5 * (maps[top2[0]][h] + maps[top2[1]][h]) for h in HOLES}
    results[k] = evaluate(maps[k], data, f"(e) ensemble 50/50 of {top2[0]} + {top2[1]}, uncalibrated")
    print(k, results[k]["lz"], flush=True)
    # (e) nested calibration (inner group folds of the training holes): expensive, opt-in
    if calib:
        for m in [m for m in top2 if m in PIXEL or m in REGION]:
            for how in ("temp", "iso"):
                k = f"{m}+{how}"
                maps[k] = calibrated(m, how, data)
                results[k] = evaluate(maps[k], data, f"(e) {m}, {how}-calibrated")
        for how in ("temp", "iso"):
            if all(f"{m}+{how}" in maps for m in top2):
                k = f"ens_{how}"
                maps[k] = {h: 0.5 * (maps[f"{top2[0]}+{how}"][h] + maps[f"{top2[1]}+{how}"][h])
                           for h in HOLES}
                results[k] = evaluate(maps[k], data, f"(e) ensemble 50/50 of {top2[0]} + {top2[1]}, {how}-calibrated")
    best = max(results, key=lambda m: score_key(results[m]))
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump({k: {kk: (vv if not isinstance(vv, dict) else {a: float(b) for a, b in vv.items()})
                       for kk, vv in r.items() if kk != "desc"} | {"desc": r["desc"]}
                   for k, r in results.items()} | {"best": best, "top2": top2,
                                                    "region_source": REGION_SRC},
                  f, indent=1, default=float)
    return results, maps, best, top2


def final_fit(best, top2, data):
    """Train the best configuration on all 16 holes and write probability maps."""
    pdir = os.path.join(OUT, "probs")
    os.makedirs(pdir, exist_ok=True)
    parts = [best]
    how = None
    if best.startswith("ens_"):
        how = None if best == "ens_raw" else best[4:]
        parts = top2
    elif "+" in best:
        parts, how = [best.split("+")[0]], best.split("+")[1]
    models = {}
    for m in parts:
        base = m
        if base in PIXEL:
            models[m] = pixel_train(base, HOLES, data)
        elif base in REGION:
            models[m] = region_train(HOLES, data, REGION[base])
        elif base in POOL:
            models[m] = pixel_train("c", HOLES, data)
    cal = {}
    if how:                    # calibration from all-holes inner folds (pool every hole's OOF)
        for m in parts:
            Ps, ys = [], []
            for h in HOLES:     # LOHO maps of this method are honest OOF for every hole
                P = loho_single(m, h, data)
                ii = sample_idx(data[h]["lab"], N_CAL, 2000 + HOLES.index(h))
                Ps.append(P.reshape(-1, NC)[ii]); ys.append(data[h]["lab"].ravel()[ii])
            P, y = np.concatenate(Ps), np.concatenate(ys)
            cal[m] = fit_temperature(P, y) if how == "temp" else fit_isotonic(P, y)
    for h in HOLES:
        maps = []
        for m in parts:
            if m in PIXEL:
                P = pixel_predict(m, models[m], data[h])
            elif m in REGION:
                P = region_predict(models[m], h, data[h], REGION[m])
            elif m in POOL:
                P = pool(pixel_predict("c", models[m], data[h]), regions(h, data[h], POOL[m])[0])
            if how == "temp":
                P = apply_temperature(P, cal[m])
            elif how == "iso":
                P = apply_isotonic(P, cal[m])
            maps.append(P)
        P = np.mean(maps, 0).astype(np.float16)
        np.savez_compressed(os.path.join(pdir, f"{h}.npz"), probs=P, classes=np.array(CLASSES))
        print("  wrote", h, flush=True)


def main():
    args = sys.argv[1:]
    method = args[args.index("--method") + 1] if "--method" in args else "best"
    os.makedirs(CACHE, exist_ok=True)
    t0 = time.time()
    data = {h: hole_data(h) for h in HOLES}
    print(f"data ready {time.time() - t0:.0f}s; regions = {REGION_SRC}", flush=True)
    if method not in ("all", "best"):
        maps = loho(method, data)
        r = evaluate(maps, data, DESC.get(method, method))
        print(json.dumps({k: r[k] for k in ("lz", "all")}, indent=1, default=float))
        return
    methods = (args[args.index("--methods") + 1].split(",") if "--methods" in args else
               ["hand", "a", "b", "c", "d", "dslic", "cpool", "cpool_slic"])
    results, maps, best, top2 = run_all(data, methods, "--calib" in args)
    flags = {}
    lohodir = os.path.join(OUT, "probs_loho")
    os.makedirs(lohodir, exist_ok=True)
    for h in HOLES:
        flags[h], dis = flags_for(maps[best][h], data[h])
        save_panel(h, data[h], maps[best][h], dis)
        np.savez_compressed(os.path.join(lohodir, f"{h}.npz"), probs=maps[best][h].astype(np.float16),
                            classes=np.array(CLASSES))
    notes = [f"- Best = `{best}`; top-2 base methods for calibration/ensembling: {top2}.",
             "- `output/vision2/probs/<hole>.npz` (key `probs`, float16 (1000,460,6), classes in "
             "`classes`) come from the best configuration trained on ALL 16 holes — in-sample for "
             "every hole, so use them as the deliverable map, not for accuracy claims. The honest "
             "out-of-sample maps behind this report are in `output/vision2/probs_loho/`.",
             "- For the all-holes model, calibration parameters are fitted on the LOHO "
             "(out-of-fold) predictions of all 16 holes.",
             f"- Training sample: {N_PER_HOLE} labelled pixels per hole (fixed seeds); HGB "
             "max_iter=150, lr 0.08, 48 leaves, balanced class weights."]
    if "--calib" not in args:
        notes.append("- (e) calibration: the nested temperature/isotonic calibration (inner "
                     "group folds over the 15 training holes) is implemented (`--calib`) but was "
                     "NOT run for this report — it costs 2 extra HGB fits per held-out hole per "
                     "method and the shared CPU was oversubscribed. Temperature scaling cannot "
                     "change any argmax, so it would not move the accuracy columns; it would "
                     "only change the p>=0.85 flag set. The ensemble row is an uncalibrated "
                     "fixed 50/50 average (no weights tuned).")
    missing = [m for m in ["hand", "a", "b", "c", "d", "dslic", "cpool", "cpool_slic"] if m not in methods]
    if missing:
        notes.append(f"- Not run for this report (CPU budget): {', '.join(missing)}.")
    if method == "best":
        final_fit(best, top2, data)
    write_report(results, best, maps[best], data, dict(flags=flags, notes=notes))
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
