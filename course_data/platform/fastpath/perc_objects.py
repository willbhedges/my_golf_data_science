"""Second-stage object models for the fast-path perception scene, trained on OUR U-Net's candidates.

perception/models/*.pkl (green / tee box / tee complex) were trained on the ariadgolf U-Net's candidates and see
only the candidate's own seg / DEM statistics plus context. Here each candidate also gets features the U-Net does
not see as such: its surroundings (fairway / bunker / tree / green probability in a 3-25 m ring: greens sit at
fairway ends, ringed by bunkers), NAIP texture (NIR / green-band std inside, NDVI / brightness contrast with the
ring: greens are smooth, mown short), DEM flatness (residual of a plane fit inside, relief against the ring:
greens and tees are smooth pads, often raised), canopy (Meta height inside / in the ring) and the other classes'
U-Net probability inside the candidate.

    install(DT, models)          inside fastscene.perception_ns: wraps detect.greens / tee_boxes / complex_features
                                 so every candidate carries the extra features; `models` then holds ours
    python3 perc_objects.py rows  train|val COMBO          # labelled rows from the cached U-Net probabilities
    python3 perc_objects.py fit   [--out fastscene_model/objects_unet]

Training courses: heldout.py TRAIN (perception pool courses, not VAL / TEST, not in the U-Net's training index).
"""
from __future__ import annotations

import json
import math
import os
import pickle
import sys

import numpy as np
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "fastscene_model", "objects_unet")
ROWS = os.environ.get("PERC_ROWS_DIR") or os.path.join(HERE, "cache", "heldout", "rows")   # per U-Net model
RING_IN, RING_OUT = 3.0, 25.0


def _plane_resid(z, m):
    rr, cc = np.nonzero(m)
    v = z[rr, cc]
    ok = np.isfinite(v)
    if ok.sum() < 8:
        return np.nan, np.nan
    A = np.c_[rr[ok], cc[ok], np.ones(ok.sum())].astype(np.float64)
    coef, *_ = np.linalg.lstsq(A, v[ok].astype(np.float64), rcond=None)
    res = v[ok] - A @ coef
    slope = math.hypot(coef[0], coef[1])
    return float(np.std(res)), float(slope)


def object_features(st, L, lab, objs, prefix=""):
    """extra features for every object (o["lab"] its label in `lab`) -> updates o["feat"] in place"""
    if not objs:
        return
    res = st.res
    seg = {k: st.seg(k) for k in ("green", "tee", "fairway", "bunker", "water")}
    n = st.naip()
    nir, gb = n[3], n[1]
    ndvi = L["ndvi"]
    bright = (n[0] + n[1] + n[2]) / 3.0
    hag = np.nan_to_num(L["hag"], nan=0.0)
    z = L["dtm"]
    sl_all = ndi.find_objects(lab)
    pad = int(math.ceil(RING_OUT / res)) + 1
    for o in objs:
        i = o.get("lab") or 0
        if i <= 0 or i - 1 >= len(sl_all) or sl_all[i - 1] is None:
            continue
        sl = sl_all[i - 1]
        r0, r1 = max(sl[0].start - pad, 0), min(sl[0].stop + pad, lab.shape[0])
        c0, c1 = max(sl[1].start - pad, 0), min(sl[1].stop + pad, lab.shape[1])
        w = (slice(r0, r1), slice(c0, c1))
        m = lab[w] == i
        d = ndi.distance_transform_edt(~m) * res
        ring = (d >= RING_IN) & (d <= RING_OUT)
        near = (d > 0) & (d <= 8.0)
        f = o.setdefault("feat", {})
        for k, a in seg.items():
            aw = a[w]
            f[prefix + "in_" + k] = float(aw[m].mean())
            f[prefix + "ring_" + k] = float(aw[ring].mean()) if ring.any() else 0.0
            f[prefix + "ringmax_" + k] = float(aw[ring].max()) if ring.any() else 0.0
        f[prefix + "near_fairway"] = float(seg["fairway"][w][near].mean()) if near.any() else 0.0
        f[prefix + "nir_sd"] = float(nir[w][m].std())
        f[prefix + "g_sd"] = float(gb[w][m].std())
        nd_in = float(np.nanmean(ndvi[w][m]))
        f[prefix + "ndvi_contrast"] = nd_in - (float(np.nanmean(ndvi[w][ring])) if ring.any() else nd_in)
        b_in = float(bright[w][m].mean())
        f[prefix + "bright_in"] = b_in
        f[prefix + "bright_contrast"] = b_in - (float(bright[w][ring].mean()) if ring.any() else b_in)
        f[prefix + "nir_contrast"] = float(nir[w][m].mean()) - (float(nir[w][ring].mean()) if ring.any() else 0.0)
        f[prefix + "hag_max"] = float(hag[w][m].max())
        f[prefix + "tree_ring"] = float((hag[w][ring] > 2.5).mean()) if ring.any() else 0.0
        zr, zs = _plane_resid(z[w], m)
        f[prefix + "z_resid"] = zr
        f[prefix + "z_plane_slope"] = zs
        zz = z[w]
        if np.isfinite(zz[m]).any() and ring.any() and np.isfinite(zz[ring]).any():
            f[prefix + "z_relief"] = float(np.nanmean(zz[m]) - np.nanmedian(zz[ring]))
            f[prefix + "z_ring_sd"] = float(np.nanstd(zz[ring]))
        else:
            f[prefix + "z_relief"] = f[prefix + "z_ring_sd"] = np.nan


def context_green(greens, fairways):
    """distance from each green to the nearest fairway centreline end, and that fairway's length"""
    ends = []
    for fw in fairways or []:
        cl = fw.get("centerline")
        if cl is not None and len(cl) >= 2:
            ends += [(np.asarray(cl[0], float), fw["length"]), (np.asarray(cl[-1], float), fw["length"])]
    for g in greens:
        p = np.asarray(g["xy"], float)
        if ends:
            dd = [float(np.hypot(*(e - p))) for e, _ in ends]
            k = int(np.argmin(dd))
            g["feat"]["d_fw_end"] = dd[k]
            g["feat"]["fw_end_len"] = float(ends[k][1])
        else:
            g["feat"]["d_fw_end"], g["feat"]["fw_end_len"] = 999.0, 0.0


def install(DT, PV=None):
    """wrap perception's detectors (inside perception_ns) so every green / tee box / complex carries the extra
    features. Idempotent."""
    if getattr(DT, "_perc_objects", False):
        return
    DT._perc_objects = True
    g0, t0, cf0, cg0 = DT.greens, DT.tee_boxes, DT.complex_features, DT.classify_greens

    def greens(st, L, models=None):
        out, lab = g0(st, L, models)
        object_features(st, L, lab, out)
        DT._last_greens = out
        return out, lab

    def tee_boxes(st, L, green_lab, models=None):
        md = (models or {}).get("tee_box")
        ours = bool(md and md.get("extra"))
        out, lab = t0(st, L, green_lab, None if ours else models)
        object_features(st, L, lab, out)
        if ours:
            res = DT._apply(md["clf"], [b["feat"] for b in out], md["features"], md.get("thr"))
            if res:
                pr, cl = res
                for b, row in zip(out, pr):
                    b["p"] = float(row[cl.index(1)])
        return out, lab

    def complex_features(c, greens_, others):
        f = cf0(c, greens_, others)
        bs = [b for b in c["boxes"] if b.get("feat")]
        for k in ("in_tee", "ring_fairway", "ringmax_fairway", "near_fairway", "z_resid", "z_relief", "hag_max",
                  "tree_ring", "in_green", "nir_sd"):
            v = [b["feat"].get(k) for b in bs if b["feat"].get(k) is not None and np.isfinite(b["feat"].get(k))]
            f["b_" + k] = float(np.mean(v)) if v else np.nan
        f["box_p_mean"] = float(np.mean([b["p"] for b in c["boxes"]]))
        return f

    def classify_greens(st, greens_, complexes, ch, models=None, parks=(), bld=()):
        context_green(greens_, getattr(DT, "_fairways_last", None))
        return cg0(st, greens_, complexes, ch, models, parks, bld)

    f0 = DT.fairways

    def fairways(st, L):
        out, lab = f0(st, L)
        DT._fairways_last = out
        return out, lab
    DT.greens, DT.tee_boxes, DT.complex_features, DT.classify_greens, DT.fairways = \
        greens, tee_boxes, complex_features, classify_greens, fairways


WATER_P = 0.5               # U-Net water probability for a water pixel (chosen on VAL, NOTES_PERCEPTION.md)
WATER_NIR_P = 0.25          # ... or the NIR-dark rule's pixel where the U-Net gives at least this
WATER_MIN_M2 = 150


WATER_NIR_RATIO = 9.0       # a component is kept when its mean NIR <= this x the course's median NIR (open water is
                            # NIR-dark; the U-Net's bright false ponds are not)


WATER_SEEDED = 1            # 1: a U-Net water component is kept only when it holds NIR-rule pixels (seed fraction
                            # >= this x 0.01); the rule's own components are always kept


WATER_VETO = 0.05           # seeded mode: a rule component whose mean U-Net water probability is below this is dropped


def install_water(DT, p=None, nir_p=None, nir_ratio=None, seeded=None, veto=None):
    """detect.water from our U-Net's water class (its validation IoU 0.79; perception's rule was written for the
    ariadgolf model, whose water class was unusable): pixels with p_water >= WATER_P, plus the NIR-dark rule's
    pixels where p_water >= WATER_NIR_P (pond edges), opened once, components >= WATER_MIN_M2. Idempotent."""
    p = WATER_P if p is None else p
    nir_p = WATER_NIR_P if nir_p is None else nir_p
    nir_ratio = WATER_NIR_RATIO if nir_ratio is None else nir_ratio
    seeded = WATER_SEEDED if seeded is None else seeded
    veto = WATER_VETO if veto is None else veto
    w0 = getattr(DT, "_water_rule", None) or DT.water
    DT._water_rule = w0
    import geo

    def water(st, L):
        import os as _o
        import sys as _s
        _s.path.append(_o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(DT.__file__))), "segment"))
        from model import nir_water
        pw = st.seg("water")
        m = pw >= p
        rule = None
        if nir_p < 1 or seeded:
            rule, _ = nir_water(st.a["naip"])
        if nir_p < 1:
            m |= rule & (pw >= nir_p)
        m = ndi.binary_opening(m, iterations=1)
        m = ndi.binary_fill_holes(m)
        if seeded:
            ru = w0(st, L)[1] > 0                # the rule detector's own water (its shadow filter included)
            if veto > 0:
                lr, nr = ndi.label(ru, structure=np.ones((3, 3)))
                if nr:
                    mp = np.asarray(ndi.mean(pw, lr, np.arange(1, nr + 1)))
                    ru = np.r_[False, mp >= veto][lr]
            lab0, n0 = ndi.label(m, structure=np.ones((3, 3)))
            if n0:
                fr = np.asarray(ndi.mean(ru.astype(np.float32), lab0, np.arange(1, n0 + 1)))
                ok = np.r_[False, fr >= seeded * 0.01]
                m = ok[lab0]
            m |= ru
        nir = st.a["naip"][3].astype(np.float32)
        med = float(np.median(nir[st.valid()])) if st.valid().any() else 128.0
        lab, n, s = DT._components(st, m, WATER_MIN_M2 / st.res ** 2, dict(pw=pw, nir=nir))
        bad = [i + 1 for i in range(n) if s["nir"][i] > nir_ratio * med]
        if bad:
            lab, n, s = DT._components(st, (lab > 0) & ~np.isin(lab, bad), 1, dict(pw=pw, nir=nir))
        ax, ln, wd, comp = geo.shape_stats(lab, n, st.res) if n else ([], [], [], [])
        rings = geo.rings_from_labels(st, lab, simplify_m=1.0)
        out = []
        for i in range(n):
            out.append(dict(id=f"w{i + 1}", lab=i + 1, xy=DT._xy(st, s["r"][i], s["c"][i]),
                            area=s["area_px"][i] * st.res ** 2, ring=rings.get(i + 1),
                            p=float(np.clip(s["pw"][i], 0, 0.99)),
                            kind="stream" if (wd[i] < 15 and ln[i] > 4 * wd[i]) else "pond"))
        return out, lab
    DT.water = water


GREEN_SPLIT_M2 = 0           # > 0: green blobs larger than this are split at distance-transform saddles (two greens,
GREEN_SPLIT_MIN_M2 = 150     # or a green and a practice / approach blob, that touch) into parts >= GREEN_SPLIT_MIN_M2


def split_blobs(mask, res, big_m2, min_m2, h_m=2.0):
    """watershed split of the components of `mask` larger than big_m2 on the distance transform, markers = its
    h-maxima (h_m metres: a neck at least h_m narrower than both lobes); parts < min_m2 are merged back."""
    from skimage.segmentation import watershed
    from skimage.morphology import h_maxima
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    if not n:
        return mask
    sizes = np.bincount(lab.ravel()) * res * res
    out = mask.copy()
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        if sl is None or sizes[i] <= big_m2:
            continue
        sl = tuple(slice(max(s.start - 2, 0), s.stop + 2) for s in sl)
        m = lab[sl] == i
        d = ndi.distance_transform_edt(m) * res
        pk, k = ndi.label(h_maxima(d, h_m) & m)
        if k < 2:
            continue
        ws = watershed(-d, pk, mask=m, watershed_line=True)
        part = np.bincount(ws.ravel()) * res * res
        if (part[1:] >= min_m2).sum() < 2:
            continue
        line = m & ndi.binary_dilation(ws == 0, structure=np.ones((3, 3)))   # cut for 8-connected labelling too
        out[sl] &= ~line
    return out


def install_green_split(DT, big_m2=None, min_m2=None, h_m=1.0):
    big = GREEN_SPLIT_M2 if big_m2 is None else big_m2
    mn = GREEN_SPLIT_MIN_M2 if min_m2 is None else min_m2
    if getattr(DT, "_green_split", None) == (big, mn, h_m):
        return
    first = getattr(DT, "_green_split", None) is None
    DT._green_split = (big, mn, h_m)
    real = getattr(DT, "_ndi_real", None) or DT.ndi
    DT._ndi_real = real

    class _NDI:                      # detect.greens: binary_fill_holes(binary_opening(p >= GREEN_P)) -> split
        def __getattr__(self, k):
            return getattr(real, k)

        @staticmethod
        def binary_fill_holes(m, *a, **kw):
            out = real.binary_fill_holes(m, *a, **kw)
            if getattr(DT, "_in_greens", False) and DT._green_split[0] > 0:
                out = split_blobs(out, DT._res, *DT._green_split)
            return out
    DT.ndi = _NDI()
    if not first:
        return
    g0 = DT.greens

    def greens(st, L, models=None):
        DT._in_greens, DT._res = True, st.res
        try:
            return g0(st, L, models)
        finally:
            DT._in_greens = False
    DT.greens = greens


def load(d=MODEL_DIR):
    out = {}
    if not os.path.isdir(d):
        return out
    for k in ("green", "tee_box", "tee_complex"):
        p = os.path.join(d, k + ".pkl")
        if os.path.exists(p):
            out[k] = pickle.load(open(p, "rb"))
    return out


# ----------------------------------------------------------------------------- training
def course_rows(D, ev):
    """labelled rows from one evaluated course (perception/evaluate.py set _truth on every candidate)"""
    import detect as DT
    rows = {}
    if (ev.get("greens_hole") or {}).get("eligible"):
        rows["green"] = [dict(g["feat"], y={None: 0, "hole": 1, "practice": 2, "unknown": 1}[g.get("_truth")])
                         for g in D["greens"]]
    if (ev.get("tee_boxes") or {}).get("eligible"):
        rows["tee_box"] = [dict(b["feat"], y=int(bool(b.get("_truth")))) for b in D["boxes"]]
    if (ev.get("tee_complexes") or {}).get("eligible"):
        rows["tee_complex"] = [dict(DT.complex_features(c, D["greens"], D["complexes"]), y=int(bool(c.get("_truth"))))
                               for c in D["complexes"]]
    return rows


def collect(which, combo, models_dir=None):
    """perception on every course of the set from the cached probabilities -> ROWS/<which>_<combo>/<slug>.json"""
    sys.path.insert(0, HERE)
    import evaluate_scene as ES
    import fastscene as FS
    import perc_bench as PB
    out = os.path.join(ROWS, f"{which}_{combo}")
    os.makedirs(out, exist_ok=True)
    os.environ["FASTSCENE_OBJECTS2"] = models_dir or "features"
    for e in PB.entries(which):
        p = os.path.join(out, e["slug"] + ".json")
        if os.path.exists(p):
            continue
        try:
            P = PB.load_combo(e["slug"], combo)
        except FileNotFoundError:
            continue
        r = ES.score_course(e["dir"], P=P, keep_D=True)
        with FS.perception_ns():
            rows = course_rows(r["_D"], r)
        rows["meta"] = dict(slug=e["slug"], state=e.get("state"))
        json.dump(rows, open(p, "w"), default=lambda x: None if x is None or not np.isfinite(x) else float(x))
        print(e["slug"], {k: len(v) for k, v in rows.items() if k != "meta"}, flush=True)


def _xy(rows, feats):
    X = np.array([[np.nan if r.get(f) is None else r.get(f) for f in feats] for r in rows], float)
    return X, np.array([r["y"] for r in rows], int)


def fit(rows_dir, out=MODEL_DIR, exclude=(), drop=()):
    import glob
    from sklearn.ensemble import HistGradientBoostingClassifier
    dirs = [rows_dir] if isinstance(rows_dir, str) else list(rows_dir)
    tabs = [json.load(open(p)) for d in dirs for p in sorted(glob.glob(os.path.join(d, "*.json")))]
    tabs = [t for t in tabs if t["meta"]["slug"] not in exclude]
    os.makedirs(out, exist_ok=True)
    info = dict(rows_dir=rows_dir, courses=[t["meta"]["slug"] for t in tabs], models={})
    for name in ("green", "tee_box", "tee_complex"):
        rows = [r for t in tabs for r in t.get(name, [])]
        if not rows:
            continue
        feats = sorted({k for r in rows for k in r if k not in ("y", "g") and k not in drop})
        X, y = _xy(rows, feats)
        thr = None
        if name != "green":                     # course-grouped 4-fold OOF threshold (F1) on the train courses
            groups = np.concatenate([np.full(len(t.get(name, [])), i) for i, t in enumerate(tabs)])
            ps = np.zeros(len(y))
            for k in range(4):
                tr, te = groups % 4 != k, groups % 4 == k
                c = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=15,
                                                   min_samples_leaf=20, l2_regularization=1.0, random_state=0)
                c.fit(X[tr], y[tr])
                ps[te] = c.predict_proba(X[te])[:, 1]
            best = (-1, 0.5)
            for th in np.linspace(0.1, 0.9, 33):
                tp = ((ps >= th) & (y == 1)).sum()
                f1 = 2 * tp / max((ps >= th).sum() + (y == 1).sum(), 1)
                best = max(best, (f1, float(th)))
            thr = round(best[1], 3)
        clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=20,
                                             l2_regularization=1.0, random_state=0)
        clf.fit(X, y)
        pickle.dump(dict(clf=clf, features=feats, thr=thr, extra=True), open(os.path.join(out, name + ".pkl"), "wb"))
        info["models"][name] = dict(n=int(len(y)), pos=int((y >= 1).sum()), thr=thr, n_features=len(feats))
        print(name, info["models"][name], flush=True)
    json.dump(info, open(os.path.join(out, "models.json"), "w"), indent=1)
    return info


def crossfit(out, train_dirs, val_dir, k=2):
    """final model on train + all of VAL (out/final) and k fold models on train + VAL minus fold j (out/fold<j>);
    out/foldmap.json maps every VAL course to the fold model that never saw it (FASTSCENE_OBJECTS2=<foldmap>)"""
    import glob
    vs = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(val_dir, "*.json")))
    fm = {"*": os.path.join(out, "final")}
    fit(list(train_dirs) + [val_dir], os.path.join(out, "final"))
    for j in range(k):
        held = [s for i, s in enumerate(vs) if i % k == j]
        fit(list(train_dirs) + [val_dir], os.path.join(out, f"fold{j}"), exclude=held)
        fm.update({s: os.path.join(out, f"fold{j}") for s in held})
    json.dump(fm, open(os.path.join(out, "foldmap.json"), "w"), indent=1)
    return fm


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["rows", "fit", "crossfit"])
    ap.add_argument("which", nargs="?", default="train")
    ap.add_argument("combo", nargs="?", default="d0")
    ap.add_argument("--out", default=MODEL_DIR)
    a = ap.parse_args()
    if a.cmd == "rows":
        collect(a.which, a.combo)
    elif a.cmd == "crossfit":
        crossfit(a.out, [os.path.join(ROWS, f"train_{a.combo}")], os.path.join(ROWS, f"val_{a.combo}"))
    else:
        fit(os.path.join(ROWS, f"{a.which}_{a.combo}"), a.out)
