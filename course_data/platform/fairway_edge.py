"""Where does the mown fairway really end? A NAIP profile outward from the OSM fairway edge.

    python3 course_data/platform/fairway_edge.py --out course_data/platform/fairway_edge.json [--courses a,b]

OSM mappers on some courses trace the mown stripe (or less), on others the full fairway + first cut. This measures,
per course, how far the fairway look continues past the mapped edge, from the course's own imagery only (no hand
map, nothing trained):

  1. the vision_any/<slug>/raw stack (every NAIP year, 4 bands, on the 1 m grid; vision_any/layers.Stack) plus the
     3x3 local std of the green and NIR bands per year (mown turf is smooth);
  2. two reference classes: "fairway" = OSM fairway pixels >= 4 m inside the edge; "rough" = pixels 25-40 m outside
     every OSM fairway, inside the OSM course outline when mapped, not in OSM native / green / tee / bunker / water /
     building / road, lidar HAG <= 1 m (no trees);
  3. the Fisher (LDA) direction between the two, scaled so rough = 0, fairway = 1;
  4. the median score in 1 m rings outward from the OSM edge (same exclusions; HAG <= 1 m so a tree line does not end
     the profile), per course and per hole (rings inside the hole's landing zone: 150-350 yds along the package
     tee line, +/-60 yds).

extension(profile, theta) = the first distance past the edge whose ring score is below theta (metres, linear between
rings). A course whose OSM edge is the real edge drops through 0.5 within 0-1 m (Blue Hills, Eagle Knoll, Veenker,
National KC); Spirit Hollow (8 m) and Ellis (6 m) fall slowly: the first cut is unmapped. The band the package gets
from it (platform/fairway_band.py) and the calibration of theta: ERROR_BUDGET.md "Fairway".
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
DISTS = list(range(-6, 30))
MIN_RING = 50
LZ = (150.0, 350.0, 60.0)


def _vision(slug):
    vd = os.path.join(CD, "vision_any")
    if vd not in sys.path:
        sys.path.insert(0, vd)
    import layers as L
    import run_any as RA
    return L, RA


def score_grid(S, M):
    """(score grid: rough 0 .. fairway 1, valid mask, outward distance from OSM fairway m, inward distance m)."""
    from scipy import ndimage as ndi
    fw = M["fairway"]
    X = [b for _, b in S.naip]
    for _, b in S.naip:
        for c in (1, 3):
            a = np.nan_to_num(b[..., c])
            m = ndi.uniform_filter(a, 3)
            m2 = ndi.uniform_filter(a * a, 3)
            X.append(np.sqrt(np.maximum(m2 - m * m, 0))[..., None])
    X = np.concatenate(X, -1)
    hag = np.nan_to_num(S.layers.get("hag", np.zeros(fw.shape)))
    other = M["green"] | M["tee"] | M["bunker"] | M["water"] | M["building"] | M["road"] | (hag > 1.0)
    other = ndi.binary_dilation(other, iterations=1)
    dout = ndi.distance_transform_edt(~fw)
    din = ndi.distance_transform_edt(fw)
    ok = np.isfinite(X).all(-1) & ~other
    inner = ok & fw & (din >= 4)
    rough = ok & ~fw & (dout >= 25) & (dout <= 40) & ~M["native"]
    if M["course"].any():
        rough &= M["course"]
    mu_f, mu_r = X[inner].mean(0), X[rough].mean(0)
    Sw = np.cov(X[inner].T) + np.cov(X[rough].T)
    w = np.linalg.solve(Sw + 1e-4 * np.eye(len(mu_f)), mu_f - mu_r)
    s = ((X - mu_r) @ w) / ((mu_f - mu_r) @ w)
    return s, ok, dout, din


def ring_profile(s, ok, dout, din, fw, sel=None):
    out = []
    for d in DISTS:
        ring = (fw & (din > -d - 1) & (din <= -d)) if d < 0 else (~fw & (dout > d) & (dout <= d + 1))
        ring &= ok
        if sel is not None:
            ring &= sel
        n = int(ring.sum())
        out.append([d, round(float(np.median(s[ring])), 3) if n >= MIN_RING else None, n])
    return out


def extension(profile, theta=0.5):
    """Metres past the OSM edge where the ring score first drops below theta (None: no profile)."""
    prev = None
    for d, v, _n in profile:
        if d < 0 or v is None:
            continue
        if v < theta:
            if prev is None:
                return float(d)
            (d0, v0) = prev
            return float(d0 + (v0 - theta) / (v0 - v) * (d - d0)) if v0 != v else float(d)
        prev = (d, v)
    return float(profile[-1][0]) if prev else None


def landing_mask(S, tee_ll, aim_ll):
    from shapely.geometry import Polygon
    a0, a1, half = LZ
    f = np.cos(np.radians(tee_ll[1])) * 111320.0 / 0.9144, 110574.0 / 0.9144
    t = np.array([tee_ll[0] * f[0], tee_ll[1] * f[1]])
    a = np.array([aim_ll[0] * f[0], aim_ll[1] * f[1]]) - t
    fwd = a / np.linalg.norm(a)
    r = np.array([fwd[1], -fwd[0]])
    pts = [t + fwd * u + r * v for u, v in ((a0, -half), (a1, -half), (a1, half), (a0, half))]
    return S.rasterize([Polygon([(x / f[0], y / f[1]) for x, y in pts])])


def course_profiles(slug, pkg=None):
    """{"course": profile, "holes": {ref: profile}} (None when the course has no raw stack / OSM fairway)."""
    L, RA = _vision(slug)
    vslug = "mozingo" if slug == "mozingo_lake" else slug
    if not os.path.exists(os.path.join(CD, "vision_any", vslug, "raw")):
        return None
    cdir = RA.course_dir_for(vslug)
    S = L.Stack.load(vslug, cdir)
    if not S.naip:
        return None
    M, _ = L.osm_masks(S, json.load(open(os.path.join(cdir, "osm.geojson"))))
    if M["fairway"].sum() < 2000:
        return None
    s, ok, dout, din = score_grid(S, M)
    res = dict(course=ring_profile(s, ok, dout, din, M["fairway"]), holes={})
    for ref, h in ((pkg or {}).get("holes") or {}).items():
        if h.get("par") in (3, "3") or not h.get("tee_ll") or not h.get("aim_ll"):
            continue
        sel = landing_mask(S, h["tee_ll"], h["aim_ll"])
        res["holes"][str(ref)] = ring_profile(s, ok, dout, din, M["fairway"], sel)
    return res


def main():
    sys.path.insert(0, HERE)
    import fairway_quality as FQ
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "fairway_edge.json"))
    ap.add_argument("--courses")
    a = ap.parse_args()
    want = set(a.courses.split(",")) if a.courses else None
    out = json.load(open(a.out)) if os.path.exists(a.out) else {}
    for cfg in FQ.all_courses():
        if want and cfg["slug"] not in want:
            continue
        pkg = json.load(open(FQ.pkg_path(cfg)))
        r = course_profiles(cfg["slug"], pkg)
        out[cfg["slug"]] = r
        print(cfg["slug"], None if r is None else extension(r["course"]), flush=True)
        json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
