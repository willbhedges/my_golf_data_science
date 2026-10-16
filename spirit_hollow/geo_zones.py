"""Hand-checked hazard maps (spirit_hollow/course.py) in real-world coordinates (WGS84).

  python3 spirit_hollow/geo_zones.py            # -> course_data/spirit_hollow/hand_zones_ll.json
  python3 spirit_hollow/geo_zones.py --qa       # + validation table + check images in spirit_hollow/qa_geo/

course.py traces every tee-shot hole in the app screenshot's 920 x 2000 pixel frame. Those zones are the
source of truth; this module only moves them onto the ground, so any tee box can use them.

Screenshot px -> WGS84
  course_data/imagery/traced_align.py registered each screenshot onto NAIP 2023. Its record per hole
  (course_data/imagery/spirit_hollow/traced_registration.json) is
    frame : a render.Frame (a padded 1440 x 2520 NAIP render about a guessed tee), and
    warp  : 2x3 affine, SCREENSHOT px -> RENDER px (the matrix cv2.warpAffine(render, warp, ...,
            WARP_INVERSE_MAP) uses to pull the render into the screenshot grid), units = pixels.
  So  ll = frame.px_to_ll(warp @ [x, y, 1]).  Checked numerically (check_warp_direction): the
  render pulled through `warp` correlates with the screenshot (r 0.34-0.45), through its inverse it
  does not (r < 0).

  2B (the Gold tee on hole 2) did not register onto NAIP (corr 0.19, scale 0.89, tee moved 87 yds).
  It is the same hole, same app imagery and season as 2F (the Black tee), which registered well, so
  we match the two screenshots directly (SIFT + RANSAC similarity, hundreds of inliers) and chain
  2B px -> 2F px -> NAIP. 9B/9F are matched the same way as a cross-check of the two registrations.

Refinement (refine_transform)
  The NAIP registration is one global affine fitted on whole-image features; on some holes it is a
  few yards off in the landing area. Patches of the NAIP photo pulled into the screenshot grid are
  matched against the screenshot (edges and traced_align's brightness + top-hat images, +/-12 yds).
  A RANSAC affine correction is fitted on half the patches (checkerboard) and kept only if the other
  half's median offset drops by >= 0.3 yd, neither feature image gets worse, and no visible point
  moves more than 20 yds. Applied on 12 of 16 holes; methods end in "+refined".

Validation (validate / --qa) -> spirit_hollow/qa_geo/validation.json + check images
  * photo: the same patch matching after the final transform (median / p75 / max yds, n patches).
  * OSM: every OSM green, bunker, water shore and cart-path piece in view is drawn as an outline
    template and matched against the edges of (a) the screenshot and (b) the NAIP pull:
      osm_shot = |a|  (OSM vs the photo features of the screenshot), reg = |a - b| (the same with
      OSM's own misplacement on NAIP removed = the screenshot -> ground error at that feature).
  * traced: OSM green centroid vs course.py's app-trilaterated green; OSM bunkers vs the nearest
    traced sand box (<= 25 yds); water: share of each traced water zone on OSM water (+6 yds).
  * 9B / 9F (two independent NAIP registrations of the same hole) are matched screenshot to
    screenshot as a consistency check.
  gate(): photo median <= 4 yds over >= 20 patches, and OSM reg median <= 4 yds if >= 3 features.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
IMG_DIR = os.path.join(ROOT, "course_data", "imagery")
for _p in (HERE, IMG_DIR, os.path.join(ROOT, "mozingo")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import render as R                                          # noqa: E402

COURSE_DIR = os.path.join(ROOT, "course_data", "spirit_hollow")
NAIP_DIR = os.path.join(IMG_DIR, "spirit_hollow")
REG_PATH = os.path.join(NAIP_DIR, "traced_registration.json")
SHOTS = os.path.join(HERE, "screenshots_clean")
OUT_PATH = os.path.join(COURSE_DIR, "hand_zones_ll.json")
QA_DIR = os.path.join(HERE, "qa_geo")
Y0, Y1 = 560, 1980                                          # visible map rows of a screenshot
PAIRS = {"2B": "2F", "9B": "9F"}                            # same hole, two tees, same app imagery
USE_PAIR = {"2B"}                                           # holes whose NAIP registration failed


def ref_of(k):
    return str(k)[:-1] if isinstance(k, str) and not str(k).isdigit() else str(k)


def _key(k):
    return int(k) if str(k).isdigit() else str(k)


def screenshot_ppy(h):
    return float(np.linalg.norm(np.subtract(h["dot270"], h["tee"])) / 270.0)


# --------------------------------------------------------------------------- transforms
class ShotGeo:
    """Screenshot px (920 x 2000 frame) <-> WGS84 [lon, lat] for one traced hole."""

    def __init__(self, frame, warp, method, info=None):
        self.frame = frame
        self.warp = np.asarray(warp, float)                 # 2x3: screenshot px -> frame px
        self.inv = np.linalg.inv(np.vstack([self.warp, [0, 0, 1]]))[:2]
        self.method = method
        self.info = info or {}

    def px_to_ll(self, px):
        p = np.atleast_2d(np.asarray(px, float))
        return self.frame.px_to_ll(p @ self.warp[:, :2].T + self.warp[:, 2])

    def ll_to_px(self, ll):
        q = self.frame.ll_to_px(np.atleast_2d(np.asarray(ll, float)))
        return q @ self.inv[:, :2].T + self.inv[:, 2]

    def yd_per_px(self):
        """Ground yards per screenshot px (geometric mean of the affine's scale)."""
        return math.sqrt(abs(np.linalg.det(self.warp[:, :2]))) / self.frame.ppy


def load_registration(path=REG_PATH):
    return json.load(open(path))


def _gray_shot(name):
    import cv2
    from PIL import Image
    im = Image.open(os.path.join(SHOTS, name)).convert("RGB").resize((920, 2000), Image.LANCZOS)
    g = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY)
    return g


def match_screenshots(img_a, img_b):
    """Similarity a px -> b px between two app screenshots of the same hole (SIFT + RANSAC).
    -> (2x3 matrix, n inliers, median inlier residual px)."""
    import cv2
    a, b = _gray_shot(img_a), _gray_shot(img_b)
    mask = np.zeros_like(a)
    mask[Y0:Y1] = 255
    sift = cv2.SIFT_create(nfeatures=6000)
    ka, da = sift.detectAndCompute(a, mask)
    kb, db = sift.detectAndCompute(b, mask)
    m = cv2.BFMatcher(cv2.NORM_L2).knnMatch(da, db, k=2)
    good = [x for x, y in m if x.distance < 0.75 * y.distance]
    pa = np.float32([ka[g.queryIdx].pt for g in good])
    pb = np.float32([kb[g.trainIdx].pt for g in good])
    M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=4.0,
                                         maxIters=5000, confidence=0.999)
    inl = inl.ravel().astype(bool)
    res = np.linalg.norm(pa[inl] @ M[:, :2].T + M[:, 2] - pb[inl], axis=1)
    return M.astype(float), int(inl.sum()), float(np.median(res))


def check_warp_direction(key, reg=None, img=None):
    """Correlation of the screenshot with the NAIP render pulled through `warp` and through its
    inverse. The first must win if warp = screenshot px -> render px."""
    import cv2
    import course
    import traced_align as TA
    reg = reg or load_registration()
    r = reg[str(key)]
    fr = R.Frame.from_json(r["frame"])
    ren, _ = R.render(fr, img or R.Imagery(NAIP_DIR))
    W = np.array(r["warp"], np.float32)
    A0 = TA.feat(TA.screenshot(course.HOLES[_key(key)]))
    out = {}
    for name, M in (("forward", W), ("inverse", cv2.invertAffineTransform(W))):
        x = cv2.warpAffine(ren, M, (920, 2000), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        m = np.zeros((2000, 920), bool)
        m[Y0:Y1] = True
        m &= x.sum(axis=2) > 0
        out[name] = float(np.corrcoef(A0[m], TA.feat(x)[m])[0, 1])
    return out


def _compose(base_warp, M):
    """warp(M(x)): screenshot px -M-> px' -base-> frame px."""
    W = np.asarray(base_warp, float)
    return np.c_[W[:, :2] @ M[:, :2], W[:, :2] @ M[:, 2] + W[:, 2]]


def transforms(reg=None, holes=None, refine=True, img=None, log=print):
    """{key: ShotGeo} for every traced tee-shot hole: the NAIP registration (2B: chained through the
    2F screenshot), then a cross-validated photo-to-photo refinement (refine_transform)."""
    if holes is None:
        import course
        holes = course.HOLES
    reg = reg or load_registration()
    img = img or (R.Imagery(NAIP_DIR) if refine else None)
    out = {}
    order = [k for k in holes if str(k) not in USE_PAIR] + [k for k in holes if str(k) in USE_PAIR]
    for k in order:
        if str(k) in USE_PAIR:
            partner = _key(PAIRS[str(k)])
            base = out[partner]
            M, n, res = match_screenshots(holes[k]["image"], holes[partner]["image"])
            g = ShotGeo(base.frame, _compose(base.warp, M), f"screenshot_match:{partner}",
                        dict(inliers=n, residual_px=res, partner=str(partner),
                             naip_corr_failed=reg.get(str(k), {}).get("corr")))
        else:
            r = reg.get(str(k))
            if r is None:
                continue
            g = ShotGeo(R.Frame.from_json(r["frame"]), r["warp"], "naip_registration",
                        dict(corr=r.get("corr"), ecc=r.get("ecc"), scale=r.get("scale"),
                             rot_deg=r.get("rot_deg")))
        if refine:
            g = refine_transform(holes[k], g, img)
            if log:
                rf = g.info["refine"]
                log(f"{str(k):>3} {g.method:<22} holdout median {rf['holdout_before_yd']:.1f} -> "
                    f"{rf['holdout_after_yd']:.1f} yd ({'applied' if rf['applied'] else 'kept'}, "
                    f"max move {rf['max_move_yd']:.1f} yd, n {rf['n']})")
        out[k] = g
    return out


def dense_matches(h, g, img, half=90, search_yd=12.0, min_peak=0.3, min_distinct=0.04):
    """Photo-to-photo correspondences: patches of the NAIP photo (pulled into the screenshot grid
    through g) matched against the screenshot, on two season-robust feature images (edges, and
    traced_align's brightness + top-hat). -> (q, d, which) arrays: patch centre q (px), shift d (px):
    the ground shown at q in the NAIP pull sits at q + d in the screenshot."""
    import traced_align as TA
    shot = TA.screenshot(h)
    naip = naip_in_shot(g, img)
    valid = naip.sum(axis=2) > 0
    ypp = g.yd_per_px()
    search = int(round(search_yd / ypp))
    Q, D, which = [], [], []
    for wi, (A, B) in enumerate(((edge_map(shot), edge_map(naip, valid)), (TA.feat(shot), TA.feat(naip, valid)))):
        for y in range(Y0 + half + search, Y1 - half - search + 1, half):
            for x in range(half + search, 920 - half - search + 1, half // 2):
                if not valid[y - half:y + half, x - half:x + half].all():
                    continue
                tpl = B[y - half:y + half, x - half:x + half]
                r = _match(A, tpl, (x - half, y - half), search)
                if r is None or r[2] < min_peak or r[3] < min_distinct:
                    continue
                Q.append((x, y))
                D.append((r[0], r[1]))
                which.append(wi)
    return np.array(Q, float).reshape(-1, 2), np.array(D, float).reshape(-1, 2), np.array(which, int)


def refine_transform(h, g, img, thr_yd=2.5, max_move_yd=20.0, min_gain_yd=0.3):
    """Robust affine correction of g from dense_matches, cross-validated: fit (RANSAC) on half the
    patches (checkerboard), score the median residual on the other half before/after, and keep the
    correction (refitted on all inliers) only if the held-out residual drops by >= min_gain_yd and
    no visible point moves more than max_move_yd."""
    import cv2
    Q, D, which = dense_matches(h, g, img)
    ypp = g.yd_per_px()
    info = dict(n=int(len(Q)), applied=False, max_move_yd=0.0)
    if len(Q) < 12:
        info.update(holdout_before_yd=float("nan"), holdout_after_yd=float("nan"))
        return ShotGeo(g.frame, g.warp, g.method, {**g.info, "refine": info})
    S = Q + D                                             # screenshot px of the same ground
    cell = ((Q[:, 0] // 90).astype(int) + (Q[:, 1] // 90).astype(int)) % 2 == 0
    thr = thr_yd / ypp

    def fit(m):
        C, inl = cv2.estimateAffine2D(S[m].astype(np.float32), Q[m].astype(np.float32), method=cv2.RANSAC,
                                      ransacReprojThreshold=thr, maxIters=4000, confidence=0.999)
        return C, inl

    def resid(C, m):
        return np.linalg.norm(S[m] @ C[:, :2].T + C[:, 2] - Q[m], axis=1) * ypp
    before = np.linalg.norm(D[~cell], axis=1) * ypp
    C, _ = fit(cell)
    after = resid(C, ~cell) if C is not None else before
    info.update(holdout_before_yd=float(np.median(before)), holdout_after_yd=float(np.median(after)),
                n_train=int(cell.sum()), n_holdout=int((~cell).sum()))
    # both feature images must agree: the correction may not make either one's held-out fit worse
    wh = which[~cell]
    per = [(float(np.median(before[wh == i])), float(np.median(after[wh == i]))) for i in (0, 1)
           if (wh == i).sum() >= 5]
    info["holdout_by_feature"] = per
    agree = all(a <= b + 0.3 for b, a in per)
    if C is None or info["holdout_before_yd"] - info["holdout_after_yd"] < min_gain_yd or not agree:
        return ShotGeo(g.frame, g.warp, g.method, {**g.info, "refine": info})
    C, inl = fit(np.ones(len(Q), bool))
    corners = np.array(footprint_px(), float)
    grid = np.array([(x, y) for x in np.linspace(0, 920, 5) for y in np.linspace(Y0, Y1, 8)])
    pts = np.r_[corners, grid]
    move = np.linalg.norm(pts @ C[:, :2].T + C[:, 2] - pts, axis=1) * ypp
    info["max_move_yd"] = float(move.max())
    info["correction"] = C.tolist()
    info["inliers"] = int(inl.sum())
    if move.max() > max_move_yd:
        return ShotGeo(g.frame, g.warp, g.method, {**g.info, "refine": info})
    info["applied"] = True
    return ShotGeo(g.frame, _compose(g.warp, C), g.method + "+refined", {**g.info, "refine": info})


def transforms_from_json(data=None):
    """{key: ShotGeo} rebuilt from hand_zones_ll.json (no imagery needed)."""
    data = data or load()
    return {_key(k): ShotGeo(R.Frame.from_json(v["frame"]), v["warp"], v["method"], v.get("info"))
            for k, v in data["holes"].items()}


# --------------------------------------------------------------------------- conversion
def footprint_px():
    return [(0.0, Y0), (920.0, Y0), (920.0, Y1), (0.0, Y1)]


def hole_ll(k, h, g):
    """One course.HOLES entry -> dict of WGS84 geometry."""
    ll = lambda pts: [[round(float(a), 8), round(float(b), 8)] for a, b in g.px_to_ll(pts)]  # noqa: E731
    return dict(
        key=str(k), ref=ref_of(k), par=h["par"], image=h["image"], method=g.method, info=g.info,
        screenshot_ppy=screenshot_ppy(h), yd_per_px=g.yd_per_px(),
        frame=g.frame.to_json(), warp=g.warp.tolist(),
        tee_ll=ll([h["tee"]])[0], dot270_ll=ll([h["dot270"]])[0], green_ll=ll([h["green"]])[0],
        footprint_ll=ll(footprint_px()),
        zones=[dict(lie=lie, poly_ll=ll(poly)) for lie, poly in h["zones"]],
    )


def build(reg=None, write=True, path=OUT_PATH, G=None, refine=True):
    import course
    G = G or transforms(reg, refine=refine)
    out = dict(
        doc=("Hand-checked zones of spirit_hollow/course.py (tee-shot holes) in WGS84 [lon, lat]. "
             "Zone order is kept: later zones override earlier ones (tee_strategy.lie_at); unzoned = "
             "rough. footprint_ll = the screenshot's visible map (rows 560-1980): the hand-checked "
             "map only covers that area. frame + warp: screenshot px -> frame px (render.Frame) -> "
             "WGS84 (geo_zones.ShotGeo). Built by spirit_hollow/geo_zones.py."),
        source="spirit_hollow/course.py HOLES (incl. AUDIT_FIXES, landing-zone fixes, first_cut)",
        registration="course_data/imagery/spirit_hollow/traced_registration.json",
        holes={str(k): hole_ll(k, h, G[k]) for k, h in course.HOLES.items() if k in G},
        missing=[str(k) for k in course.HOLES if k not in G],
    )
    if write:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(out, fh, indent=1)
    return out, G


def load(path=OUT_PATH):
    return json.load(open(path))


# --------------------------------------------------------------------------- OSM features
def osm_features(course_dir=COURSE_DIR):
    """{'green' | 'bunker' | 'water': [ring_ll], 'path': [line_ll]} from the raw OSM extract."""
    fc = json.load(open(os.path.join(course_dir, "osm.geojson")))
    out = {"green": [], "bunker": [], "water": [], "path": []}
    for f in fc["features"]:
        p, geom = f["properties"], f["geometry"]
        if geom["type"] == "LineString":
            if p.get("golf") in ("path", "cartpath"):
                out["path"].append(np.array(geom["coordinates"], float))
            continue
        polys = ([geom["coordinates"]] if geom["type"] == "Polygon" else
                 geom["coordinates"] if geom["type"] == "MultiPolygon" else [])
        kind = ("green" if p.get("golf") == "green" else "bunker" if p.get("golf") == "bunker" else
                "water" if p.get("natural") == "water" or "water_hazard" in str(p.get("golf")) else None)
        if kind:
            out[kind] += [np.array(pl[0], float) for pl in polys]
    return out


# --------------------------------------------------------------------------- validation
def naip_in_shot(g, img):
    """The NAIP photo pulled into the screenshot's 920 x 2000 grid through the transform."""
    import cv2
    ren, _ = R.render(g.frame, img)
    return cv2.warpAffine(ren, g.warp.astype(np.float32), (920, 2000),
                          flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)


def edge_map(rgb, valid=None):
    """Gradient magnitude (season-robust: outlines of bunkers, greens, water, cart paths)."""
    import traced_align as TA
    m = TA.grad_img(np.ascontiguousarray(rgb[..., :3]), sigma=1.5)
    if valid is not None:
        m[~valid] = 0
    return m.astype(np.float32)


def _segments(p, seg_px):
    """Split a projected line into pieces of about seg_px."""
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    n = max(1, int(round(d[-1] / seg_px)))
    edges = np.linspace(0, d[-1], n + 1)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        t = np.linspace(a, b, 40)
        out.append(np.c_[np.interp(t, d, p[:, 0]), np.interp(t, d, p[:, 1])])
    return out


def _match(E, tpl, org, search):
    """NCC of template tpl (top-left at org) against E within +/-search px.
    -> (dx, dy, peak, distinct) or None."""
    import cv2
    x0, y0 = org
    th, tw = tpl.shape
    if x0 - search < 0 or y0 - search < 0 or x0 + tw + search > E.shape[1] or y0 + th + search > E.shape[0]:
        return None
    win = E[y0 - search:y0 + th + search, x0 - search:x0 + tw + search]
    if win.std() < 1e-3:
        return None
    res = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(res)
    if loc[0] in (0, 2 * search) or loc[1] in (0, 2 * search):
        return None
    r2 = res.copy()
    cv2.circle(r2, loc, max(4, search // 3), -1.0, -1)
    i, j = loc[1], loc[0]
    dx, dy = float(j - search), float(i - search)
    l, m_, r = res[i, j - 1], res[i, j], res[i, j + 1]
    dx += 0.5 * (l - r) / (l - 2 * m_ + r - 1e-9) if (l - 2 * m_ + r) < 0 else 0.0
    u, d = res[i - 1, j], res[i + 1, j]
    dy += 0.5 * (u - d) / (u - 2 * m_ + d - 1e-9) if (u - 2 * m_ + d) < 0 else 0.0
    return dx, dy, float(mx), float(mx - r2.max())


def feature_templates(g, osm, pad=12, seg_yd=50):
    """OSM outlines (greens, bunkers, water, cart-path pieces) drawn into the screenshot grid.
    -> list of (kind, centre px, template, top-left)."""
    import cv2
    ppx = 1.0 / g.yd_per_px()
    out = []
    items = []
    for kind in ("green", "bunker", "water"):
        items += [(kind, g.ll_to_px(r)) for r in osm[kind]]
    for line in osm["path"]:
        items += [("path", s) for s in _segments(g.ll_to_px(line), seg_yd * ppx)]
    for kind, p in items:
        p = p.copy()
        if kind == "water":                               # only the part of the shore in view
            inside = (p[:, 0] > 0) & (p[:, 0] < 920) & (p[:, 1] > Y0) & (p[:, 1] < Y1)
            if inside.sum() < 3:
                continue
        lo = np.maximum(np.floor(p.min(axis=0)) - pad, [0, Y0]).astype(int)
        hi = np.minimum(np.ceil(p.max(axis=0)) + pad, [920, Y1]).astype(int)
        if (hi - lo).min() < 2 * pad + 4 or (hi - lo).max() > 700:
            continue
        if not (p.min(axis=0)[0] >= 0 and p.max(axis=0)[0] <= 920 and p.min(axis=0)[1] >= Y0
                and p.max(axis=0)[1] <= Y1) and kind != "water":
            continue                                      # partly off-screen: skip
        t = np.zeros((hi[1] - lo[1], hi[0] - lo[0]), np.float32)
        q = np.round((p - lo) * 4).astype(np.int32)
        closed = kind != "path"
        cv2.polylines(t, [q], closed, 1.0, thickness=8, shift=2)
        t = cv2.GaussianBlur(t, (0, 0), 2.0)
        out.append((kind, p.mean(axis=0), t, (int(lo[0]), int(lo[1]))))
    return out


def validate(k, h, g, osm, img, search_yd=12.0, min_peak=0.3, min_distinct=0.03, return_images=False):
    """Per-hole offsets in yds (see the module doc).

    For each OSM outline in view we find the shift that best lines it up with the edges of (a) the
    app screenshot and (b) the NAIP photo pulled into the screenshot grid through the transform.
      osm_shot  = |shift (a)|   : OSM vs the photo features of the screenshot (what was asked)
      reg       = |(a) - (b)|   : the same with OSM's own misplacement on NAIP removed, i.e. the
                                  error of the screenshot -> ground transform at that feature
    Traced: OSM green centroid vs course.py's green; OSM bunker centroids vs the nearest traced sand."""
    import traced_align as TA
    from matplotlib.path import Path
    shot = TA.screenshot(h)
    naip = naip_in_shot(g, img)
    valid = naip.sum(axis=2) > 0
    Es, En = edge_map(shot), edge_map(naip, valid)
    ypp = g.yd_per_px()
    search = int(round(search_yd / ypp))
    rec = dict(features=[], traced=[], water=[])
    for kind, c, tpl, org in feature_templates(g, osm):
        a = _match(Es, tpl, org, search)
        b = _match(En, tpl, org, search)
        if a is None or b is None or min(a[2], b[2]) < min_peak or min(a[3], b[3]) < min_distinct:
            continue
        rec["features"].append(dict(
            kind=kind, px=[float(c[0]), float(c[1])], shot_px=[a[0], a[1]], naip_px=[b[0], b[1]],
            osm_shot_yd=float(math.hypot(a[0], a[1]) * ypp),
            osm_naip_yd=float(math.hypot(b[0], b[1]) * ypp),
            reg_yd=float(math.hypot(a[0] - b[0], a[1] - b[1]) * ypp), peak=[a[2], b[2]]))
    sands = [np.array(z, float) for lie, z in h["zones"] if lie == "sand"]
    for kind in ("green", "bunker"):
        for poly in osm[kind]:
            c = g.ll_to_px(poly).mean(axis=0)
            if not (0 <= c[0] <= 920 and Y0 <= c[1] <= Y1):
                continue
            if kind == "green":
                d = float(np.linalg.norm(np.array(h["green"], float) - c) * ypp)
                if d < 40:
                    rec["traced"].append(("green", d))
            elif sands:
                d = float(min(np.linalg.norm(z.mean(axis=0) - c) for z in sands) * ypp)
                if d < 25:
                    rec["traced"].append(("bunker", d))
    # water: share of each traced water zone on OSM water or within 6 yds of it
    wpx = [g.ll_to_px(w) for w in osm["water"]]
    from scipy.ndimage import distance_transform_edt
    yy, xx = np.mgrid[0:2000:2, 0:920:2]
    pts = np.c_[xx.ravel(), yy.ravel()]
    mask = np.zeros(xx.shape, bool)
    for w in wpx:
        if w[:, 1].max() > -500 and w[:, 1].min() < 2500:
            mask |= Path(w).contains_points(pts).reshape(xx.shape)
    dist = distance_transform_edt(~mask) * 2 * ypp
    for lie, z in h["zones"]:
        if lie != "water":
            continue
        inside = Path(z).contains_points(pts).reshape(xx.shape)
        inside[:Y0 // 2] = False
        if inside.sum() >= 20:
            rec["water"].append(float((dist[inside] <= 6).mean()))

    def stats(v):
        v = np.asarray(v, float)
        return (float(np.median(v)), float(v.max()), len(v)) if len(v) else (float("nan"), float("nan"), 0)
    F = rec["features"]
    reg_m, reg_x, n = stats([f["reg_yd"] for f in F])
    os_m, os_x, _ = stats([f["osm_shot_yd"] for f in F])
    on_m, _, _ = stats([f["osm_naip_yd"] for f in F])
    tr_m, tr_x, n_tr = stats([d for _, d in rec["traced"]])
    by_kind = {kd: stats([f["reg_yd"] for f in F if f["kind"] == kd]) for kd in ("green", "bunker", "water",
                                                                                   "path")}
    Q, Dd, _ = dense_matches(h, g, img)
    dd = np.linalg.norm(Dd, axis=1) * ypp
    ph_m, ph_x, n_ph = stats(dd)
    summary = dict(
        key=str(k), method=g.method, n_features=n, by_kind=by_kind,
        photo_median_yd=ph_m, photo_p75_yd=float(np.percentile(dd, 75)) if len(dd) else float("nan"),
        photo_max_yd=ph_x, n_photo=n_ph, refine=g.info.get("refine"),
        reg_median_yd=reg_m, reg_max_yd=reg_x, osm_shot_median_yd=os_m, osm_shot_max_yd=os_x,
        osm_naip_median_yd=on_m, n_traced=n_tr, traced_median_yd=tr_m, traced_max_yd=tr_x,
        green_traced_yd=next((d for kd, d in rec["traced"] if kd == "green"), None),
        water_on_osm=[round(x, 2) for x in rec["water"]], features=F)
    if return_images:
        return summary, shot, naip
    return summary


def gate(s, limit=4.0, min_photo=20):
    """Median photo-to-photo offset <= limit over >= min_photo matched patches, and the OSM-feature
    registration error (when >= 3 features matched) also <= limit."""
    ok = np.isfinite(s["photo_median_yd"]) and s["photo_median_yd"] <= limit and s["n_photo"] >= min_photo
    if s["n_features"] >= 3:
        ok = ok and s["reg_median_yd"] <= limit
    return bool(ok)


# --------------------------------------------------------------------------- QA images
LIE_RGB = {"fairway": (40, 200, 60), "first_cut": (150, 230, 120), "rough": (230, 230, 230),
           "sand": (255, 235, 90), "recovery": (20, 90, 20), "native": (230, 150, 40),
           "water": (40, 120, 255), "ob": (255, 40, 40)}


def draw_zones(rgb, zones_px, alpha=0.30, width=2):
    """Zones (lie, polygon px) over an image: translucent fill + solid outline, in zone order."""
    from PIL import Image, ImageDraw
    base = Image.fromarray(np.ascontiguousarray(rgb[..., :3])).convert("RGBA")
    for lie, poly in zones_px:
        col = LIE_RGB.get(lie, (255, 0, 255))
        ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = [tuple(map(float, p)) for p in poly]
        d.polygon(pts, fill=col + (int(255 * alpha),))
        d.line(pts + [pts[0]], fill=col + (255,), width=width)
        base = Image.alpha_composite(base, ov)
    return np.asarray(base.convert("RGB"))


def qa_image(k, h, g, img, osm, out_dir=QA_DIR, summary=None):
    """screenshot + zones | NAIP (pulled into the screenshot grid) + zones + OSM outlines."""
    from PIL import Image, ImageDraw
    import traced_align as TA
    shot = TA.screenshot(h)
    naip = naip_in_shot(g, img)
    zones = list(h["zones"])
    left = draw_zones(shot, zones)
    right = draw_zones(naip, zones)
    im = Image.fromarray(right)
    d = ImageDraw.Draw(im)
    for kind, col in (("green", (255, 255, 255)), ("bunker", (255, 0, 255)), ("water", (0, 255, 255))):
        for poly in osm[kind]:
            p = g.ll_to_px(poly)
            if p[:, 1].max() < 0 or p[:, 1].min() > 2000 or p[:, 0].max() < 0 or p[:, 0].min() > 920:
                continue
            d.line([tuple(map(float, q)) for q in p] + [tuple(map(float, p[0]))], fill=col, width=3)
    t = np.array(h["tee"], float)
    d.ellipse([t[0] - 8, t[1] - 8, t[0] + 8, t[1] + 8], outline=(255, 0, 0), width=3)
    gr = np.array(h["green"], float)
    d.ellipse([gr[0] - 8, gr[1] - 8, gr[0] + 8, gr[1] + 8], outline=(255, 255, 0), width=3)
    raw = Image.fromarray(naip[..., :3].copy())
    side = np.concatenate([left, np.asarray(im), np.asarray(raw)], axis=1)[Y0 - 40:]
    out = Image.fromarray(side)
    d2 = ImageDraw.Draw(out)
    lab = f"{k}  {g.method}"
    if summary:
        lab += (f"  reg error median {summary['reg_median_yd']:.1f} / max {summary['reg_max_yd']:.1f} yd"
                f" (n={summary['n_features']})")
    d2.rectangle([0, 0, out.size[0], 36], fill=(0, 0, 0))
    d2.text((10, 10), lab + "   [app screenshot + hand zones | NAIP 2023 + hand zones + OSM green/bunker/water"
            " (white/magenta/cyan) | NAIP]", fill=(255, 255, 255))
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f"hole_{k}.jpg")
    out.resize((out.size[0] // 2, out.size[1] // 2), Image.LANCZOS).save(p, quality=85)
    # full-res crop of the landing area (150-350 yds) for close checks
    ppy = screenshot_ppy(h)
    y_hi = int(min(Y1, t[1] - 150 * ppy))
    y_lo = int(max(Y0, t[1] - 350 * ppy))
    crop = np.concatenate([np.asarray(im), np.asarray(raw)], axis=1)[y_lo:y_hi]
    Image.fromarray(crop).save(os.path.join(out_dir, f"hole_{k}_landing.jpg"), quality=85)
    return p


def pair_consistency(G, holes):
    """For 9B/9F (both NAIP-registered): the screenshot match vs the two registrations, in yds."""
    out = {}
    for a, b in PAIRS.items():
        ka, kb = _key(a), _key(b)
        if a in USE_PAIR or ka not in G or kb not in G:
            continue
        M, n, res = match_screenshots(holes[ka]["image"], holes[kb]["image"])
        ys, xs = np.mgrid[Y0:Y1:40, 0:920:40]
        pa = np.c_[xs.ravel(), ys.ravel()].astype(float)
        pb = pa @ M[:, :2].T + M[:, 2]
        inb = (pb[:, 0] >= 0) & (pb[:, 0] < 920) & (pb[:, 1] >= Y0) & (pb[:, 1] < Y1)
        fa, fb = G[ka].frame, G[kb].frame
        la, lb = G[ka].px_to_ll(pa[inb]), G[kb].px_to_ll(pb[inb])
        d = np.linalg.norm(fa._to_yd(la) - fa._to_yd(lb), axis=1)
        out[f"{a}~{b}"] = dict(inliers=n, residual_px=res, median_yd=float(np.median(d)),
                               max_yd=float(d.max()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qa", action="store_true", help="validate + render check images")
    ap.add_argument("--holes")
    a = ap.parse_args()
    import course
    out, G = build()
    print(f"wrote {OUT_PATH}: {len(out['holes'])} holes, missing {out['missing']}")
    if not a.qa:
        return
    img = R.Imagery(NAIP_DIR)
    osm = osm_features()
    keys = [k for k in G if a.holes is None or str(k) in a.holes.split(",")]
    rows = []
    for k in keys:
        h = course.HOLES[k]
        s = validate(k, h, G[k], osm, img)
        qa_image(k, h, G[k], img, osm, summary=s)
        s["pass"] = gate(s)
        rows.append(s)
        print(f"{str(k):>3} {G[k].method:<22} photo med {s['photo_median_yd']:4.1f} p75 {s['photo_p75_yd']:4.1f} "
              f"(n {s['n_photo']:3d}) | OSM reg med {s['reg_median_yd']:5.1f} max {s['reg_max_yd']:5.1f} "
              f"(n {s['n_features']:2d})  osm->shot med {s['osm_shot_median_yd']:5.1f} max "
              f"{s['osm_shot_max_yd']:5.1f}  osm->naip med {s['osm_naip_median_yd']:5.1f}  traced med "
              f"{s['traced_median_yd']:5.1f} max {s['traced_max_yd']:5.1f} (n {s['n_traced']:2d})  "
              f"water {s['water_on_osm']}  {'PASS' if s['pass'] else 'FAIL'}", flush=True)
    pc = pair_consistency(G, course.HOLES)
    print("pair consistency", pc)
    with open(os.path.join(QA_DIR, "validation.json"), "w") as fh:
        json.dump(dict(holes=rows, pairs=pc,
                       warp_direction={k: check_warp_direction(k) for k in ("5", "14")}), fh, indent=1,
                  default=float)


if __name__ == "__main__":
    main()
