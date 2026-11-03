"""S4f: a mown-fairway layer from NAIP + the hole line, for holes whose landing corridor has no mapped fairway.

    from fairway_fill import fill_package
    pkg2, report = fill_package(pkg, slug, osm_fc)      # new dict; the input is not mutated

    python3 course_data/vision_any/fairway_fill.py --package course_data/packages/<slug>/package.json [--out ...]

Why: vision_any/2 makes trees and water only; the segment U-Net (course_data/segment) runs only where the segment
workflow was requested; so a course whose OSM has no golf=fairway (Creekmoor: tees, greens, bunkers, holes, no
fairway) was built fairway-blind: every landing "fairway 0 %", aims steered by sand and trees alone.

How (per course, nothing trained on hand maps and no OSM fairway used, so it behaves the same whether OSM has
fairways or not):
  1. the vision_any/<slug>/raw stack (every NAIP year, 4 bands, 1 m grid; layers.Stack) + 3x3 local std of the
     green and NIR bands per year (mown turf is smooth);
  2. two self-supervised classes from the hole lines: "mown" = pixels <= SEED_M of each par-4/5 line between
     SEED_FROM_YD past the tee and SEED_TO_YD short of the green; "rough" = ROUGH_M lateral off the line, further
     than OTHER_LINE_M from every other hole line; both lidar HAG <= 1 m (no trees) and off the OSM green / tee /
     bunker / water / building / road;
  3. a Fisher (LDA) direction between them, scaled so rough = 0, mown = 1; REFINE passes re-take the classes from
     the score (mown = score >= THETA within CORRIDOR_M, rough = score < THETA past ROUGH_M[0]);
  4. per hole: score (3x3 mean) >= THETA, HAG <= 1, off those OSM features, within CORRIDOR_M of the line and from
     FROM_YD past the tee to the green; opened / closed; the parts that touch the line kept.

Quality gate (stage text + report say which): the course's class separation d' >= MIN_DPRIME, else no fill at all
(dormant Bermuda, mown rough that looks like fairway). Per hole the fill must cover >= MIN_LINE_COVER of the
mid-hole line, its mean width must be WIDTH_YD, and it may fill <= MAX_SHARE of the corridor (else the rough is
not separable there). A hole that fails keeps no fill (flag). Holes whose landing corridor (LZ) already has
>= HAVE_FAIRWAY_YD2 of fairway (OSM, segment, mapper) are never touched.

Added zones: {"lie": "fairway", "poly", "src": "fairway_fill:naip", "p", "gapfill": "fairway_fill"}; the yard-frame
zones are refreshed with platform/package.reframe by the caller. Calibration + error budget: platform/ERROR_BUDGET.md
"Fairway fill".
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
YD = 0.9144
SRC = "fairway_fill:naip"
VERSION = "fairway_fill/1 (NAIP multi-year LDA, hole-line self-supervised)"

SEED_M = 4.0
SEED_FROM_YD, SEED_TO_YD = 90.0, 50.0
ROUGH_M = (32.0, 55.0)
OTHER_LINE_M = 30.0
CORRIDOR_M = 50.0
FROM_YD = 40.0
THETA = 0.5
REFINE = 2
MIN_DPRIME = 1.0
MIN_LINE_COVER = 0.5
WIDTH_YD = (14.0, 75.0)
MAX_SHARE = 0.85
HAVE_FAIRWAY_YD2 = 400.0
LZ = (150.0, 330.0, 45.0)          # landing corridor: yds along the tee line, +/- half width


def log(*a):
    print(*a, flush=True)


def _vision():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import layers as L
    return L


# --------------------------------------------------------------------------- package side
def _xy(lon0, lat0):
    kx, ky = math.cos(math.radians(lat0)) * 111320.0 / YD, 110574.0 / YD

    def f(ll):
        a = np.asarray(ll, float)
        return np.c_[(a[:, 0] - lon0) * kx, (a[:, 1] - lat0) * ky]
    return f


def corridor_fairway_yd2(h, tee_set=None):
    """Sq yds of fairway (any src) in the hole's landing corridor (LZ along the tee -> aim line)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    t = (h.get("tees") or {}).get(tee_set) if tee_set else None
    tee, aim = (t or {}).get("tee_ll") or h.get("tee_ll"), (t or {}).get("aim_ll") or h.get("aim_ll")
    if not tee or not aim:
        return 0.0
    f = _xy(*tee)
    a = f([aim])[0]
    u = a / (np.linalg.norm(a) + 1e-9)
    r = np.array([u[1], -u[0]])
    a0, a1, half = LZ
    box = Polygon([u * s + r * v for s, v in ((a0, -half), (a1, -half), (a1, half), (a0, half))])
    fw = []
    for z in h.get("zones_ll") or []:
        if z.get("lie") in ("fairway", "first_cut") and len(z.get("poly") or []) >= 3:
            g = Polygon(f(z["poly"]))
            fw.append(g if g.is_valid else g.buffer(0))
    return float(unary_union(fw).intersection(box).area) if fw else 0.0


def needs_fill(h, tee_set=None):
    return int(h.get("par") or 4) >= 4 and corridor_fairway_yd2(h, tee_set) < HAVE_FAIRWAY_YD2


def hole_line_ll(h):
    line = [list(p) for p in (h.get("hole_line_ll") or [])]
    if len(line) >= 2 and h.get("green_ll"):
        line[-1] = list(h["green_ll"])
    return line


# --------------------------------------------------------------------------- grid side
def features(S):
    from scipy import ndimage as ndi
    X = [b for _, b in S.naip]
    for _, b in S.naip:
        for c in (1, 3):
            a = np.nan_to_num(b[..., c])
            m = ndi.uniform_filter(a, 3)
            m2 = ndi.uniform_filter(a * a, 3)
            X.append(np.sqrt(np.maximum(m2 - m * m, 0))[..., None])
    return np.concatenate(X, -1).astype(np.float32)


WIN_M = 90.0                       # per-hole window: the line's bbox + this


def _line_masks(S, lines):
    """{ref: (window slices, dist to the line m, arc yds of the nearest line point, line length yds)}."""
    from scipy import ndimage as ndi
    from shapely.geometry import LineString, Point
    S.ll_to_rc([[0, 0]])
    out = {}
    pad = int(math.ceil(WIN_M / S.res))
    for ref, ll in lines.items():
        rc = S.ll_to_rc(ll)
        c0, c1 = int(max(0, np.floor(rc[:, 0].min()) - pad)), int(min(S.W, np.ceil(rc[:, 0].max()) + pad))
        r0, r1 = int(max(0, np.floor(rc[:, 1].min()) - pad)), int(min(S.H, np.ceil(rc[:, 1].max()) + pad))
        if c1 - c0 < 5 or r1 - r0 < 5:
            continue
        win = (slice(r0, r1), slice(c0, c1))
        m = S.rasterize([LineString(ll)])[win]
        if not m.any():
            continue
        d, (ri, ci) = ndi.distance_transform_edt(~m, return_indices=True)
        rr, cc = np.nonzero(m)
        x, y = S.transform * (cc + c0 + 0.5, rr + r0 + 0.5)
        lon, lat = S._inv.transform(np.asarray(x), np.asarray(y))
        f = _xy(*ll[0])
        line_xy = LineString(f(ll))
        arc = np.zeros(m.shape, np.float32)
        arc[rr, cc] = [line_xy.project(Point(q)) for q in f(np.c_[lon, lat])]
        out[ref] = (win, (d * S.res).astype(np.float32), arc[ri, ci], float(line_xy.length))
    return out


def fisher(X, a, b):
    mu_a, mu_b = X[a].mean(0), X[b].mean(0)
    Sw = np.cov(X[a].T) + np.cov(X[b].T)
    w = np.linalg.solve(Sw + 1e-4 * np.eye(len(mu_a)), mu_a - mu_b)
    return w, float(mu_b @ w), float((mu_a - mu_b) @ w)


def _dprime(sa, sb):
    return float((sa.mean() - sb.mean()) / math.sqrt(0.5 * (sa.var() + sb.var()) + 1e-12))


def course_model(S, M, D, refs):
    """-> (score grid rough 0 .. mown 1 (NaN off the valid cells), valid grid, d', n seeds, n rough)."""
    from scipy import ndimage as ndi
    X = features(S)
    hag = S.layers.get("hag")
    hag = np.nan_to_num(hag, nan=0.0) if hag is not None else np.zeros(X.shape[:2], np.float32)
    other = M["green"] | M["tee"] | M["bunker"] | M["water"] | M["building"] | M["road"] | (hag > 1.0)
    other = ndi.binary_dilation(other, iterations=1)
    ok = np.isfinite(X).all(-1) & ~other
    near = np.zeros(ok.shape, np.uint8)                   # how many hole lines within OTHER_LINE_M
    for win, d, _arc, _L in D.values():
        near[win] += (d <= OTHER_LINE_M).astype(np.uint8)
    seed = np.zeros(ok.shape, bool)
    rough = np.zeros(ok.shape, bool)
    corr = np.zeros(ok.shape, bool)
    for ref in refs:
        if ref not in D:
            continue
        win, d, arc, L = D[ref]
        mid = (arc >= SEED_FROM_YD) & (arc <= L - SEED_TO_YD)
        seed[win] |= mid & (d <= SEED_M)
        rough[win] |= mid & (d >= ROUGH_M[0]) & (d <= ROUGH_M[1])
        corr[win] |= mid & (d <= CORRIDOR_M)
    seed &= ok
    rough &= ok & (near == 0)
    if M.get("course") is not None and M["course"].any():
        rough &= M["course"]
    if seed.sum() < 500 or rough.sum() < 500:
        return None, ok, 0.0, int(seed.sum()), int(rough.sum())
    w, off, scale = fisher(X, seed, rough)
    s = (X @ w - off) / scale
    for _ in range(REFINE):
        sm = ndi.uniform_filter(np.nan_to_num(s), 3)
        a = ok & corr & (sm >= THETA) & (s >= THETA)
        b = ok & rough & (sm < THETA)
        if a.sum() < 500 or b.sum() < 500:
            break
        w, off, scale = fisher(X, a, b)
        s = (X @ w - off) / scale
    dp = _dprime(s[seed], s[rough])            # on the line seeds vs the rough band, not the self-selected classes
    return np.where(ok, s, np.nan).astype(np.float32), ok, dp, int(seed.sum()), int(rough.sum())


def hole_mask(S, s, ok, entry):
    """(fill mask on the full grid, stats) for one hole."""
    import cv2
    from scipy import ndimage as ndi
    L_ = _vision()
    win, d, arc, L = entry
    sw, okw = s[win], ok[win]
    sm = ndi.uniform_filter(np.nan_to_num(sw, nan=-1.0), 3)
    band = (arc >= FROM_YD) & (arc <= L + 5) & (d <= CORRIDOR_M)
    m = okw & band & (sm >= THETA)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, L_.disk(2).astype(np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, L_.disk(3).astype(np.uint8)) > 0
    m &= band & okw
    lab, n = ndi.label(m)
    touch = set(np.unique(lab[(d <= SEED_M + 2) & m]).tolist()) - {0}
    m = np.isin(lab, list(touch)) if touch else np.zeros_like(m)
    midarc = (arc >= SEED_FROM_YD) & (arc <= L - SEED_TO_YD)
    mid = midarc & (d <= SEED_M) & okw
    cover = float(m[mid].mean()) if mid.any() else 0.0
    span = band & okw & midarc
    share = float(m[span].mean()) if span.any() else 0.0
    seg = max(L - SEED_TO_YD - SEED_FROM_YD, 1.0)
    width = float((m & midarc).sum() * S.res ** 2 / YD ** 2 / seg)
    full = np.zeros(ok.shape, bool)
    full[win] = m
    return full, dict(cover=round(cover, 3), share=round(share, 3), width_yd=round(width, 1))


def gate_hole(st):
    why = []
    if st["cover"] < MIN_LINE_COVER:
        why.append(f"covers {st['cover']:.0%} of the line")
    if not (WIDTH_YD[0] <= st["width_yd"] <= WIDTH_YD[1]):
        why.append(f"mean width {st['width_yd']:.0f} yds")
    if st["share"] > MAX_SHARE:
        why.append(f"fills {st['share']:.0%} of the corridor (rough not separable)")
    return why


def fill_holes(pkg, S, M, refs=None, tee_set=None):
    """-> (new package, report). refs: the holes to fill (default: needs_fill)."""
    from shapely.geometry import Polygon
    L_ = _vision()
    out = copy.deepcopy(pkg)
    ts = tee_set or out.get("tee_set")
    holes = out.get("holes") or {}
    lines = {str(r): hole_line_ll(h) for r, h in holes.items() if len(hole_line_ll(h)) >= 2}
    want = [str(r) for r, h in holes.items() if (refs is None and needs_fill(h, ts)) or (refs is not None and str(r) in refs)]
    want = [r for r in want if r in lines and int(holes[r].get("par") or 4) >= 4]
    rep = dict(version=VERSION, holes={}, wanted=want)
    if not want:
        rep["status"] = "not needed: every par-4/5 landing corridor has a fairway"
        return out, rep
    D = _line_masks(S, lines)
    model_refs = [r for r, h in holes.items() if str(r) in lines and int(h.get("par") or 4) >= 4]
    s, ok, dp, ns, nr = course_model(S, M, D, [str(r) for r in model_refs])
    rep.update(dprime=round(dp, 2), n_seed=ns, n_rough=nr)
    if s is None or dp < MIN_DPRIME:
        rep["status"] = (f"gated: mown / rough separation d' {dp:.2f} < {MIN_DPRIME} (seeds {ns}, rough {nr}); "
                         "no fairway filled")
        return out, rep
    n_ok = 0
    for r in want:
        if r not in D:
            continue
        m, st = hole_mask(S, s, ok, D[r])
        why = gate_hole(st)
        st["gate"] = why or "ok"
        rep["holes"][r] = st
        h = holes[r]
        if why:
            h.setdefault("flags", []).append("no fairway mapped; NAIP fairway fill gated: " + "; ".join(why))
            continue
        polys = L_.mask_to_polys(S, m, min_yd2=150, simplify_yd=1.5)
        add = []
        from shapely.ops import unary_union
        keep_out = []
        f = _xy(*h["tee_ll"])
        for z in h.get("zones_ll") or []:
            if z.get("lie") in ("green", "sand", "water", "recovery") and len(z.get("poly") or []) >= 3:
                g = Polygon(z["poly"])
                keep_out.append(g if g.is_valid else g.buffer(0))
        ko = unary_union(keep_out) if keep_out else None
        hf = _holefree()
        for p in polys:
            if ko is not None:
                p = p.difference(ko)
            for q in hf(p.buffer(0)):
                if q.is_empty or q.geom_type != "Polygon":
                    continue
                area = Polygon(f(np.asarray(q.exterior.coords))).area
                if area < 150:
                    continue
                add.append(dict(lie="fairway", poly=[[round(float(a), 7), round(float(b), 7)] for a, b in
                                                     np.asarray(q.exterior.coords)[:-1]],
                                src=SRC, p=round(min(0.95, 0.5 + 0.1 * dp), 2), gapfill="fairway_fill",
                                area_yd2=round(float(area))))
        if not add:
            st["gate"] = ["no polygon left after the hazards"]
            continue
        h["zones_ll"] = [z for z in (h.get("zones_ll") or []) if z.get("src") != SRC] + add
        h.setdefault("flags", []).append(f"fairway from NAIP (no fairway mapped): {len(add)} polygon(s), "
                                         f"width {st['width_yd']:.0f} yds, d' {dp:.1f}")
        prov = h.setdefault("provenance", {})
        pz = prov.get("zones") if isinstance(prov.get("zones"), dict) else {}
        pz["fairway"] = SRC
        prov["zones"] = pz
        n_ok += 1
    rep["status"] = (f"ok: {n_ok}/{len(want)} hole(s) without a mapped fairway filled from NAIP (d' {dp:.2f}; "
                     f"gated: {', '.join(r for r in want if rep['holes'].get(r, {}).get('gate') != 'ok') or 'none'})")
    return out, rep


def _holefree():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import gapfill as G
    return G.holefree


def strip_fairway(fc):
    """osm.geojson without golf=fairway (the classifier never uses it; for the 'OSM has no fairway' simulation)."""
    return dict(fc, features=[f for f in fc["features"] if (f.get("properties") or {}).get("golf") != "fairway"])


def load_stack(slug):
    L = _vision()
    raw = os.path.join(HERE, slug, "raw")
    if not os.path.exists(os.path.join(raw, "meta.json")):
        return None
    S = L.Stack.load(slug, os.path.join(HERE, slug))
    return S if S.naip else None


def fill_package(pkg, slug=None, osm_fc=None, refs=None, S=None):
    """course_package/1 + its osm.geojson -> (new package, report). Never fatal: a missing stack / failure leaves the
    package as it was and says so in report["status"]."""
    slug = slug or (pkg.get("course") or {}).get("slug") or pkg.get("slug")
    try:
        if not any(needs_fill(h, pkg.get("tee_set")) for h in (pkg.get("holes") or {}).values()) and refs is None:
            return copy.deepcopy(pkg), dict(status="not needed: every par-4/5 landing corridor has a fairway")
        L = _vision()
        if S is None:
            if HERE not in sys.path:
                sys.path.insert(0, HERE)
            import gapfill as G
            vslug = G.resolve_slug(slug, (pkg.get("course") or {}).get("center"))
            S = load_stack(vslug)
        if S is None:
            return copy.deepcopy(pkg), dict(status=f"not run: no vision_any/{slug}/raw NAIP stack")
        M, _ = L.osm_masks(S, strip_fairway(osm_fc or dict(features=[])))
        return fill_holes(pkg, S, M, refs)
    except Exception as e:                                       # noqa: BLE001
        return copy.deepcopy(pkg), dict(status=f"failed: {type(e).__name__}: {str(e)[:200]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True)
    ap.add_argument("--osm")
    ap.add_argument("--out")
    a = ap.parse_args()
    pkg = json.load(open(a.package))
    osm = a.osm or os.path.join(os.path.dirname(a.package), "raw", "osm.geojson")
    fc = json.load(open(osm)) if os.path.exists(osm) else None
    out, rep = fill_package(pkg, osm_fc=fc)
    log(json.dumps(rep, indent=1)[:4000])
    if a.out:
        json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
