"""Raster <-> vector helpers on a stack grid (metric UTM; 1 px = res m)."""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage as ndi


def affine(st):
    from affine import Affine
    return Affine(st.res, 0, st.x0, 0, -st.res, st.y1)


def label(mask, min_px=1, structure8=True):
    s = np.ones((3, 3), bool) if structure8 else None
    lab, n = ndi.label(mask, structure=s)
    if n and min_px > 1:
        sizes = np.bincount(lab.ravel())
        small = sizes < min_px
        small[0] = False
        lab[small[lab]] = 0
        lab, n = ndi.label(lab > 0, structure=s)
    return lab, n


def rings_from_labels(st, lab, simplify_m=0.5):
    """{label id: outer ring [[x, y], ...] in grid CRS metres} (largest polygon of each label, holes dropped)."""
    from rasterio import features
    from shapely.geometry import shape
    out = {}
    if lab.max() == 0:
        return out
    for geom, v in features.shapes(lab.astype(np.int32), mask=lab > 0, transform=affine(st)):
        v = int(v)
        g = shape(geom)
        if simplify_m:
            g = g.simplify(simplify_m, preserve_topology=True)
        if g.is_empty:
            continue
        ring = list(g.exterior.coords)
        if v not in out or len(ring) > 0 and _area(ring) > _area(out[v]):
            out[v] = ring
    return out


def _area(ring):
    a = np.asarray(ring, float)
    if len(a) < 3:
        return 0.0
    x, y = a[:, 0], a[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


def ring_area(ring):
    return _area(ring)


def xy_to_ll_list(st, xy, nd=7):
    a = np.asarray(xy, float)
    if a.size == 0:
        return []
    lon, lat = st.xy_to_ll(a[:, 0], a[:, 1])
    return [[round(float(x), nd), round(float(y), nd)] for x, y in zip(np.atleast_1d(lon), np.atleast_1d(lat))]


def rc_to_xy(st, r, c):
    return st.rc_to_xy(r, c)


def pt_ll(st, x, y):
    lon, lat = st.xy_to_ll(float(x), float(y))
    return [round(float(lon), 7), round(float(lat), 7)]


def comp_stats(lab, n, arrays):
    """Per-label mean of each array in `arrays` ({name: (H, W)}) -> {name: (n,) array} (NaN-safe), + area px,
    centroid rows / cols."""
    idx = np.arange(1, n + 1)
    out = {}
    ones = np.ones(lab.shape, np.float32)
    cnt = ndi.sum(ones, lab, idx)
    out["area_px"] = np.asarray(cnt, float)
    rr, cc = np.indices(lab.shape)
    out["r"] = np.asarray(ndi.mean(rr, lab, idx), float) if n else np.zeros(0)
    out["c"] = np.asarray(ndi.mean(cc, lab, idx), float) if n else np.zeros(0)
    for k, a in arrays.items():
        v = np.isfinite(a)
        s = ndi.sum(np.where(v, a, 0.0), lab, idx)
        m = ndi.sum(v.astype(np.float32), lab, idx)
        out[k] = np.where(np.asarray(m) > 0, np.asarray(s) / np.maximum(np.asarray(m), 1), np.nan)
    return out


def comp_max(lab, n, a):
    idx = np.arange(1, n + 1)
    return np.asarray(ndi.maximum(np.nan_to_num(a, nan=-1e9), lab, idx), float)


def comp_percentile(lab, n, a, q):
    objs = ndi.find_objects(lab)
    out = np.full(n, np.nan)
    for i, sl in enumerate(objs):
        if sl is None:
            continue
        v = a[sl][lab[sl] == i + 1]
        v = v[np.isfinite(v)]
        if v.size:
            out[i] = np.percentile(v, q)
    return out


def shape_stats(lab, n, res=1.0):
    """Per label: long-axis bearing (deg, undirected [0,180) true north = up), length / width (m) from second
    moments, compactness 4 pi A / P^2 (perimeter from boundary pixels)."""
    objs = ndi.find_objects(lab)
    ax = np.full(n, np.nan)
    L = np.zeros(n)
    Wd = np.zeros(n)
    comp = np.zeros(n)
    for i, sl in enumerate(objs):
        if sl is None:
            continue
        m = lab[sl] == i + 1
        rr, cc = np.nonzero(m)
        if rr.size < 3:
            continue
        x, y = cc.astype(float), -rr.astype(float)
        x -= x.mean()
        y -= y.mean()
        cov = np.cov(np.vstack([x, y]))
        ev, evec = np.linalg.eigh(cov)
        v = evec[:, 1]
        ax[i] = (math.degrees(math.atan2(v[0], v[1])) + 360) % 180
        L[i] = 4 * math.sqrt(max(ev[1], 0)) * res
        Wd[i] = 4 * math.sqrt(max(ev[0], 0)) * res
        er = ndi.binary_erosion(m)
        per = float((m & ~er).sum()) * res
        comp[i] = 4 * math.pi * rr.size * res * res / max(per * per, 1e-6)
    return ax, L, Wd, np.clip(comp, 0, 1.5)


def angle_diff(a, b):
    """Undirected angle difference in degrees (0-90)."""
    d = abs((a - b) % 180)
    return min(d, 180 - d)


def bearing(p, q):
    """Bearing (deg true) from xy p to xy q in a north-up metric grid."""
    return (math.degrees(math.atan2(q[0] - p[0], q[1] - p[1])) + 360) % 360
