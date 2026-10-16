"""Long grass / native areas from NAIP, self-supervised from the course's own OSM map (no hand-traced labels).

Physics: mown turf (fairway, green, tee, and the mown rough beside them) is bright in NIR, green, smooth;
unmown native grass is darker in NIR, straw-coloured (higher red-blue chroma), coarser in texture, at every
course and season we have (Spirit Hollow Sept 2021/2023, Mozingo Jun 2020/Jul 2022). Features are expressed
in units of the course's own mown-turf spread (layers.features), so the same rule works across courses.

  1. negatives  = OSM fairway / green / tee (eroded 2 m) + the 2-8 m ring outside OSM fairways (first cut /
                  mown rough), minus tree canopy.
  2. anomaly    = robust z-score vs the negatives of (-NIR, +chroma, +NIR texture, -NDVI), averaged over
                  the NAIP years; seeds = cells >= 25 m from OSM mown turf, not canopy / water / sand /
                  building / road, with anomaly >= SEED_Z; plus any OSM grassland / scrub / meadow polygons.
  3. classifier = gradient boosting on all spectral + texture (+ lidar low-vegetation) features, trained
                  seeds vs negatives (d_mown is NOT a feature, so it cannot just learn "far from fairway"),
                  predicted on every eligible cell; p >= P_MIN, opened 2 m, >= 150 yd2.
"""
import numpy as np
from scipy import ndimage

import layers as L

SEED_Z = 3.0
SEED_DIST_M = 25.0
P_MIN = 0.7
ANOM = [("nir_s3", -1), ("chroma_s3", +1), ("std_nir_7", +1), ("ndvi_s3", -1)]


def _robust(v, ref):
    r = v[ref]
    r = r[np.isfinite(r)]
    med = np.median(r)
    s = 1.4826 * np.median(np.abs(r - med)) + 1e-3
    return (v - med) / s


def eligible(S, osm_m, trees, water):
    bad = trees | water | osm_m["bunker"] | osm_m["building"] | osm_m["green"] | osm_m["tee"] | osm_m["fairway"]
    bad |= ndimage.binary_dilation(osm_m["road"], L.disk(4))
    if S.naip:
        b = S.naip[0][1]
        bad |= b[..., :3].mean(-1) > 0.75                   # paths, roofs, sand
        bad |= ~np.isfinite(b).all(-1) | (b.sum(-1) == 0)
    return ~bad


def negatives(osm_m, trees):
    fw = osm_m["fairway"]
    core = ndimage.binary_erosion(osm_m["mown"], L.disk(2))
    d_out = ndimage.distance_transform_edt(~fw)
    ring = (d_out >= 2) & (d_out <= 8) & ~osm_m["mown"]
    return (core | ring) & ~ndimage.binary_dilation(trees, L.disk(2))


def anomaly(X, names, neg):
    parts = []
    for yi in range(2):
        cols = [(f"y{yi}_{n}", s) for n, s in ANOM]
        if not all(c in names for c, _ in cols):
            continue
        z = [s * _robust(X[..., names.index(c)], neg) for c, s in cols]
        parts.append(np.mean(z, 0))
    return np.mean(parts, 0)


def predict(S, osm_m, osm_layers, trees, water, X=None, names=None, seed_z=SEED_Z, p_min=P_MIN,
            n_max=60000, rng=0, return_parts=False):
    """-> (native bool mask, p grid, info)."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    if X is None:
        X, names = L.features(S, osm_m, trees)
    elig = eligible(S, osm_m, trees, water)
    neg = negatives(osm_m, trees) & np.isfinite(X).all(-1) if False else negatives(osm_m, trees)
    an = anomaly(X, names, neg)
    dmown = ndimage.distance_transform_edt(~osm_m["mown"]) * S.res
    course = osm_m["course"] if osm_m["course"].any() else np.ones_like(elig)
    course = ndimage.binary_dilation(course, L.disk(30))
    seeds = elig & course & (dmown >= SEED_DIST_M) & (an >= seed_z)
    seeds = ndimage.binary_opening(seeds, L.disk(1))
    osm_nat = osm_m.get("native")
    if osm_nat is not None and osm_nat.any():
        seeds |= ndimage.binary_erosion(osm_nat, L.disk(2)) & elig
    info = dict(seed_px=int(seeds.sum()), neg_px=int(neg.sum()), seed_z=seed_z)
    feat_idx = [i for i, n in enumerate(names) if n not in ("d_mown", "d_trees")]
    R = np.random.default_rng(rng)

    def pick(m, n):
        idx = np.flatnonzero(m.ravel())
        return R.choice(idx, min(n, len(idx)), replace=False) if len(idx) else idx
    Xf = X.reshape(-1, X.shape[-1])[:, feat_idx]
    if seeds.sum() < 200:
        info["note"] = "too few seeds: no native predicted"
        p = np.zeros(seeds.shape, np.float32)
    else:
        ip, ineg = pick(seeds, n_max), pick(neg & ~seeds, n_max)
        y = np.r_[np.ones(len(ip)), np.zeros(len(ineg))]
        clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=31,
                                             l2_regularization=1.0, random_state=0)
        clf.fit(Xf[np.r_[ip, ineg]], y)
        p = np.zeros(seeds.size, np.float32)
        ev = np.flatnonzero((elig & course).ravel())
        for i in range(0, len(ev), 400000):
            j = ev[i:i + 400000]
            p[j] = clf.predict_proba(Xf[j])[:, 1]
        p = p.reshape(seeds.shape)
        info["features"] = [names[i] for i in feat_idx]
    m = (ndimage.uniform_filter(p, 3) >= p_min) & elig
    m = ndimage.binary_opening(m, L.disk(2))
    m = ndimage.binary_closing(m, L.disk(2)) & elig
    m = L.remove_small(m, 150 * L.YD * L.YD / S.res ** 2)
    info["native_frac_course"] = float(m[course].mean())
    if return_parts:
        return m, p, info, dict(seeds=seeds, neg=neg, anomaly=an, elig=elig)
    return m, p, info
