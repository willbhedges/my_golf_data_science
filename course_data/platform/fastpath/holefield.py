"""The learned hole field as routing features (research/holefield_gate0.py / holefield_gate1.py, NOTES_ROUTING.md
2026-11-27): a per-course direction field (unit tee -> green vector along each hole, scaled by P(on a hole)) and the
line integral that scores a tee for a green. No torch here: the fields are read from files.

Bench: ROUTE_HOLEFIELD=<dir> holding the research runs' fields_fold<k>.npz (one [2, S, S] float16 array per course,
out of fold) and origins_fold<k>.json ({slug: [lon0, lat0, kx, ky]}; a fold without it gets the origin of the mapped
hole lines, as the research loader centred its canvas).
  pair_x(slug, d) -> [n pairs, len(XF4)] for d['hp'] (NaN rows when the course has no field)"""
import glob
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "research"))

XF4 = ["hf_line", "hf_far", "hf_rel_g", "hf_rank_g", "hf_rel_t"]
_Z = {}


def on():
    return bool(os.environ.get("ROUTE_HOLEFIELD"))


def _files():
    d = os.environ.get("ROUTE_HOLEFIELD")
    if d not in _Z:
        z = dict(npz=[np.load(f) for f in sorted(glob.glob(os.path.join(d, "**", "fields_fold*.npz"), recursive=True))],
                 org={})
        for f in glob.glob(os.path.join(d, "**", "origins_fold*.json"), recursive=True):
            z["org"].update(json.load(open(f)))
        _Z[d] = z
    return _Z[d]


def _origin(slug):
    """the research loader's canvas centre: the mean point of the course's numbered hole lines (first way per ref)"""
    import math
    p = os.path.join(HERE, "benchdata", "big", "courses", slug, "osm_golf.geojson.gz")
    hs = {}
    for f in json.load(gzip.open(p, "rt"))["features"]:
        pr = f.get("properties") or {}
        if pr.get("golf") == "hole" and f["geometry"]["type"] == "LineString" and str(pr.get("ref") or "").isdigit() \
                and 1 <= int(pr["ref"]) <= 18 and len(f["geometry"]["coordinates"]) >= 2:
            hs.setdefault(int(pr["ref"]), np.asarray(f["geometry"]["coordinates"], float)[:, :2])
    lon0, lat0 = np.concatenate([hs[k] for k in sorted(hs)]).mean(0)
    return [float(lon0), float(lat0), math.cos(math.radians(lat0)) * 111320.0, 111320.0]


def field(slug):
    """-> (F [2, S, S] float32, origin) or None"""
    z = _files()
    for n in z["npz"]:
        if slug in n.files:
            return n[slug].astype(np.float32), z["org"].get(slug) or _origin(slug)
    return None


def pair_x(slug, d):
    import holefield_gate0 as G0
    co, geo = d["co"], d["geo"]
    hp = np.asarray(d["hp"], int).reshape(-1, 2)
    out = np.full((len(hp), len(XF4)), np.nan)
    fo = field(slug) if on() else None
    if fo is None or not len(hp):
        return out
    F, (lon0, lat0, kx, ky) = fo
    S = F.shape[-1]
    pj = co["pj"]

    def px(xy):
        lon, lat = pj.inv(np.asarray(xy, float)[..., 0], np.asarray(xy, float)[..., 1])
        return np.stack([(lon - lon0) * kx / G0.RES + S / 2, S / 2 - (lat - lat0) * ky / G0.RES], -1)
    G = px(np.asarray(co["G"], float))
    Tc = px(np.asarray(geo["Tc"], float))
    Gy = np.asarray(co["G"], float)
    far = px(np.array([np.asarray(co["T"][t]["pts"])[int(np.argmax(np.hypot(*(np.asarray(co["T"][t]["pts"]) - Gy[g]).T)))]
                       for t, g in hp]))
    line = np.array([G0.line_score(F, Tc[t], G[g]) for t, g in hp])
    out[:, 0] = line
    out[:, 1] = [G0.line_score(F, far[i], G[g]) for i, (t, g) in enumerate(hp)]
    for col, key in ((2, 1), (4, 0)):                           # the pair against the best of its green / of its tee
        best = {}
        for v, k in zip(line, hp[:, key]):
            best[k] = max(best.get(k, -9.0), v)
        out[:, col] = line - np.array([best[k] for k in hp[:, key]])
    order = np.argsort(-line)
    seen = {}
    for i in order:                                             # rank among the green's tees (0 = best)
        g = hp[i, 1]
        out[i, 3] = seen.get(g, 0)
        seen[g] = seen.get(g, 0) + 1
    return out


# ----------------------------------------------------------------------------- the network, numpy only
def _conv3(x, w, b):
    """3x3 convolution, padding 1, + ReLU. x [C, H, W], w [O, C, 3, 3] (batch norm folded in), b [O]"""
    C, H, W = x.shape
    xp = np.zeros((C, H + 2, W + 2), np.float32)
    xp[:, 1:-1, 1:-1] = x
    out = np.empty((w.shape[0], H * W), np.float32)
    out[:] = b[:, None]
    for ky in range(3):
        for kx in range(3):
            out += w[:, :, ky, kx] @ xp[:, ky:ky + H, kx:kx + W].reshape(C, H * W)
    np.maximum(out, 0, out=out)
    return out.reshape(-1, H, W)


def _up2(x):
    """bilinear x2 as torch's interpolate(align_corners=False)"""
    def one(a, axis):
        a = np.moveaxis(a, axis, -1)
        lo = np.concatenate([a[..., :1], a[..., :-1]], -1)
        hi = np.concatenate([a[..., 1:], a[..., -1:]], -1)
        o = np.empty(a.shape[:-1] + (a.shape[-1] * 2,), np.float32)
        o[..., 0::2] = 0.25 * lo + 0.75 * a
        o[..., 1::2] = 0.75 * a + 0.25 * hi
        return np.moveaxis(o, -1, axis)
    return one(one(x, 1), 2)


def forward(x, W):
    """the gate network (research/holefield_gate0.build_net) on x [C, S, S] float32 -> [3, S, S] (dx, dy, on-a-hole
    logit). W: holefield_weights.npz (research/holefield_export.py: batch norms folded)"""
    def block(v, name):
        for j in (0, 1):
            v = _conv3(v, W[f"{name}_{j}_w"].astype(np.float32), W[f"{name}_{j}_b"].astype(np.float32))
        return v
    sk = []
    v = np.asarray(x, np.float32)
    for i in range(5):
        if i:
            C, H, Wd = v.shape
            v = v.reshape(C, H // 2, 2, Wd // 2, 2).max((2, 4))
        v = block(v, "d%d" % i)
        sk.append(v)
    for i, s in enumerate(sk[-2::-1]):
        v = block(np.concatenate([_up2(v), s]), "u%d" % i)
    hw = W["head_w"].astype(np.float32)
    C, H, Wd = v.shape
    return (hw @ v.reshape(C, H * Wd) + W["head_b"].astype(np.float32)[:, None]).reshape(-1, H, Wd)


def field_of(x, W):
    """-> F [2, S, S]: the direction scaled by P(on a hole), as the research evaluation used it"""
    o = forward(x, W)
    return o[:2] * (1.0 / (1.0 + np.exp(-o[2])))[None]

