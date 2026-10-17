"""Register a website image (per-hole aerial, GPS-app screenshot, course map) to the course's NAIP mosaic.

Global RootSIFT matching over a whole course fails across sources (val1: 0 of 779 images; every high-inlier
"match" was a degenerate homography). This does it in two steps:

  1. coarse: exhaustive rotation x ground-resolution search with normalised cross-correlation at 2.4 m/px on
     two channels that survive sensor / season changes (CLAHE grey and excess-green 2G-R-B). The score is the
     best NCC peak; `peak_ratio` = best / best elsewhere (> 120 m away) measures uniqueness.
  2. refine: RootSIFT between the image and a NAIP window (0.6 m) around the coarse hypothesis, ratio test,
     MAGSAC similarity (4-DoF) then homography; accepted only when inliers are spread over the image and the
     refined transform agrees with the coarse one.

register(im, naip_bgr) -> dict(H=3x3 image px -> NAIP lo px, inliers, ncc, peak_ratio, ...) or None.
"""
import math

import cv2
import numpy as np

COARSE_M = 1.8
GROUND_RES = (0.2, 0.3, 0.42, 0.6, 0.85, 1.2, 1.7, 2.4, 3.4)     # m per image px hypotheses
ROT_STEP = 15


CHANNELS = ("grad", "exg")


def channels(bgr):
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    g = cv2.createCLAHE(2.0, (8, 8)).apply(g).astype(np.float32)
    out = []
    for ch in CHANNELS:
        if ch == "grey":
            out.append(cv2.GaussianBlur(g, (0, 0), 1.0))
        elif ch == "grad":
            gb = cv2.GaussianBlur(g, (0, 0), 1.5)
            gx = cv2.Sobel(gb, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(gb, cv2.CV_32F, 0, 1, ksize=3)
            m = np.sqrt(gx * gx + gy * gy)
            out.append(cv2.normalize(cv2.GaussianBlur(np.sqrt(m), (0, 0), 1.0), None, 0, 255, cv2.NORM_MINMAX))
        elif ch == "exg":
            b, gg, r = [c.astype(np.float32) for c in cv2.split(bgr)]
            exg = cv2.normalize(2 * gg - r - b, None, 0, 255, cv2.NORM_MINMAX)
            out.append(cv2.GaussianBlur(exg, (0, 0), 1.0))
    return out


def rotate_pad(img, ang):
    """Rotate by ang degrees onto an expanded canvas; returns (rotated, valid mask, 2x3 M src->canvas)."""
    h, w = img.shape[:2]
    a = math.radians(ang)
    c, s = abs(math.cos(a)), abs(math.sin(a))
    W, H = int(math.ceil(w * c + h * s)), int(math.ceil(w * s + h * c))
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    M[0, 2] += W / 2 - w / 2
    M[1, 2] += H / 2 - h / 2
    r = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    m = cv2.warpAffine(np.ones((h, w), np.uint8), M, (W, H), flags=cv2.INTER_NEAREST, borderValue=0)
    return r, m, M


def coarse(im, naip, naip_res, top_k=12):
    """-> list of hypotheses (z, ncc, g, ang, H image px -> NAIP lo px), best first, one per location."""
    k = naip_res / COARSE_M
    N = cv2.resize(naip, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    nch = channels(N)
    hyps = []
    h0, w0 = im.shape[:2]
    for g in GROUND_RES:
        s = g / COARSE_M
        tw, th = int(round(w0 * s)), int(round(h0 * s))
        if min(tw, th) < 24 or max(tw, th) > min(N.shape[:2]) * 0.95:
            continue
        T = cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA)
        tch = channels(T)
        for ang in range(0, 360, ROT_STEP):
            score = None
            for tc, ncv in zip(tch, nch):
                tr, msk, M = rotate_pad(tc, ang)
                if tr.shape[0] >= ncv.shape[0] or tr.shape[1] >= ncv.shape[1] or tc.std() < 3:
                    score = None
                    break
                R = cv2.matchTemplate(ncv, tr, cv2.TM_CCOEFF_NORMED, mask=msk.astype(np.float32))
                R = np.nan_to_num(R, nan=0.0, posinf=0.0, neginf=0.0)
                score = R if score is None else score + R
            if score is None:
                continue
            score /= len(tch)
            mu, sd = float(score.mean()), float(score.std()) + 1e-6
            # up to 3 peaks per map (non-maximum suppression 60 m)
            sc = score.copy()
            rad = max(3, int(60 / COARSE_M))
            for _ in range(3):
                _, mx, _, loc = cv2.minMaxLoc(sc)
                z = (mx - mu) / sd
                Sm = np.diag([s, s, 1.0])
                Mr = np.vstack([M, [0, 0, 1]])
                Tl = np.array([[1, 0, loc[0]], [0, 1, loc[1]], [0, 0, 1]], float)
                U = np.diag([1 / k, 1 / k, 1.0])
                Hc = U @ Tl @ Mr @ Sm
                cx, cy = (Hc @ [w0 / 2, h0 / 2, 1])[:2]
                hyps.append((z, float(mx), g, ang, Hc, (cx, cy)))
                x0, y0 = max(0, loc[0] - rad), max(0, loc[1] - rad)
                sc[y0:loc[1] + rad, x0:loc[0] + rad] = -1
    hyps.sort(key=lambda h: -h[0])
    out = []

    def add(h):
        if all(math.hypot(h[5][0] - o[5][0], h[5][1] - o[5][1]) * naip_res > 80 or o[2] != h[2] for o in out):
            out.append(h)
            return True
        return False
    for g in GROUND_RES:                           # the best 2 locations at every scale ...
        n = 0
        for h in hyps:
            if h[2] == g and add(h):
                n += 1
                if n >= 2:
                    break
    n = 0
    for h in hyps:                                 # ... plus the global best few
        if h not in out and add(h):
            n += 1
            if n >= top_k // 2:
                break
    out.sort(key=lambda h: -h[0])
    return out


def rootsift(des):
    des = des / (np.abs(des).sum(axis=1, keepdims=True) + 1e-7)
    return np.sqrt(des).astype(np.float32)


def refine(im, naip, Hc, margin_px=250):
    """SIFT between image and NAIP window around the coarse footprint."""
    h0, w0 = im.shape[:2]
    corners = np.float32([[0, 0], [w0, 0], [w0, h0], [0, h0]]).reshape(-1, 1, 2)
    fp = cv2.perspectiveTransform(corners, Hc).reshape(-1, 2)
    x0, y0 = np.maximum(fp.min(0) - margin_px, 0).astype(int)
    x1, y1 = np.minimum(fp.max(0) + margin_px, [naip.shape[1], naip.shape[0]]).astype(int)
    if x1 - x0 < 50 or y1 - y0 < 50:
        return None
    W = naip[y0:y1, x0:x1]
    # warp the image into the window frame with the coarse transform so SIFT sees similar scale / rotation
    Tw = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]], float) @ Hc
    warped = cv2.warpPerspective(im, Tw, (x1 - x0, y1 - y0))
    valid = cv2.warpPerspective(np.full(im.shape[:2], 255, np.uint8), Tw, (x1 - x0, y1 - y0))
    sift = cv2.SIFT_create(nfeatures=8000, contrastThreshold=0.015)
    cl = cv2.createCLAHE(2.0, (8, 8))
    ga = cl.apply(cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY))
    gb = cl.apply(cv2.cvtColor(W, cv2.COLOR_BGR2GRAY))
    ka, da = sift.detectAndCompute(ga, cv2.erode(valid, np.ones((9, 9), np.uint8)))
    kb, db = sift.detectAndCompute(gb, None)
    if da is None or db is None or len(ka) < 10 or len(kb) < 10:
        return None
    da, db = rootsift(da), rootsift(db)
    mm = cv2.BFMatcher(cv2.NORM_L2).knnMatch(da, db, k=2)
    A, B = [], []
    for m in mm:
        if len(m) < 2 or m[0].distance > 0.85 * m[1].distance:
            continue
        pa = np.array(ka[m[0].queryIdx].pt)
        pb = np.array(kb[m[0].trainIdx].pt)
        if np.linalg.norm(pa - pb) < 80:                   # coarse prior: within ~50 m of the coarse guess
            A.append(pa)
            B.append(pb)
    if len(A) < 8:
        return dict(inliers=0, candidates=len(A))
    A, B = np.float32(A), np.float32(B)
    Ms, inl = cv2.estimateAffinePartial2D(A, B, method=cv2.RANSAC, ransacReprojThreshold=4.0, maxIters=5000)
    if Ms is None:
        return dict(inliers=0, candidates=len(A))
    inl = inl.ravel().astype(bool)
    ni = int(inl.sum())
    # spread of inliers in the (warped) image frame
    spread = 0.0
    if ni >= 4:
        hull = cv2.convexHull(A[inl])
        spread = float(cv2.contourArea(hull)) / max(1.0, float((valid > 0).sum()))
    scale = math.hypot(Ms[0, 0], Ms[1, 0])
    rot = math.degrees(math.atan2(Ms[1, 0], Ms[0, 0]))
    Hs = np.vstack([Ms, [0, 0, 1]])
    Hf = np.array([[1, 0, x0], [0, 1, y0], [0, 0, 1]], float) @ Hs @ Tw
    return dict(H=Hf, inliers=ni, candidates=len(A), spread=round(spread, 3), d_scale=round(scale, 3),
                d_rot=round(rot, 1))


def _ok(r):
    return (r.get("inliers", 0) >= 10 and r.get("spread", 0) >= 0.08 and r.get("d_scale") is not None
            and 0.75 <= r["d_scale"] <= 1.33 and abs(r["d_rot"]) <= 12)


def register(im, naip, naip_res, top_k=12):
    """Coarse top-k hypotheses, each verified by local SIFT; the best verified one wins.
    `second_inliers` (best other verified location) gives a uniqueness check."""
    h0, w0 = im.shape[:2]
    sc = min(1.0, 1400 / max(h0, w0))
    if sc < 1:
        im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    hyps = coarse(im, naip, naip_res, top_k)
    if not hyps:
        return None
    tried = []
    for rank, (z, ncc, g, ang, Hc, ctr) in enumerate(hyps):
        r = refine(im, naip, Hc) or {}
        tried.append((r.get("inliers", 0) if _ok(r) else 0, rank, z, ncc, g, ang, Hc, r))
    tried.sort(key=lambda t: (-t[0], t[1]))
    ni, rank, z, ncc, g, ang, Hc, r = tried[0]
    second = tried[1][0] if len(tried) > 1 else 0
    ok = ni > 0
    out = dict(z=round(z, 2), ncc=round(ncc, 3), coarse_rank=rank, ground_res=g, rot=ang, inliers=ni,
               second_inliers=second, candidates=r.get("candidates", 0), spread=r.get("spread", 0.0),
               d_scale=r.get("d_scale"), d_rot=r.get("d_rot"), refined=bool(ok), n_hyp=len(hyps))
    H = r["H"] if ok else hyps[0][4]
    S = np.diag([sc, sc, 1.0])
    H = H @ S                                              # original image px -> NAIP lo px
    out["H"] = (H / H[2, 2]).tolist()
    corners = np.float32([[0, 0], [w0, 0], [w0, h0], [0, h0]]).reshape(-1, 1, 2)
    out["footprint_px"] = cv2.perspectiveTransform(corners, np.float64(H)).reshape(-1, 2).tolist()
    return out


# ----------------------------------------------------------------------------- corridor classification
def _sim_from_pairs(a0, a1, b0, b1):
    """2x3 similarity mapping points a0->b0, a1->b1."""
    a0, a1, b0, b1 = (np.array(p, float) for p in (a0, a1, b0, b1))
    va, vb = a1 - a0, b1 - b0
    s = np.linalg.norm(vb) / max(1e-9, np.linalg.norm(va))
    ang = math.atan2(vb[1], vb[0]) - math.atan2(va[1], va[0])
    c, si = s * math.cos(ang), s * math.sin(ang)
    R = np.array([[c, -si], [si, c]])
    t = b0 - R @ a0
    return np.hstack([R, t[:, None]])


def _ncc(a, b, m):
    x, y = a[m] - a[m].mean(), b[m] - b[m].mean()
    return float((x * y).sum() / (np.sqrt((x * x).sum() * (y * y).sum()) + 1e-6))


def corridor_framings(W, H, tee, green, naip_res, k, ground_res=None, tee_y=(0.8, 0.88, 0.95),
                      spans=(0.55, 0.7, 0.85, 1.0, 1.2), shifts=(-0.12, 0.0, 0.12)):
    """Image-frame anchor pairs (tee point, green point) for a corridor.
    ground_res given: fixed scale (m per original image px), tee near the bottom, hole pointing up.
    Otherwise: the tee-green span is a share of the image height (hole fitted to the frame)."""
    out = []
    if ground_res:
        for g in ground_res if isinstance(ground_res, (list, tuple)) else (ground_res,):
            L = math.hypot(green[0] - tee[0], green[1] - tee[1]) * naip_res / (g / k)
            for ty in tee_y:
                out.append(((W / 2, H * ty), (W / 2, H * ty - L)))
    else:
        for span in spans:
            for sh in shifts:
                cy = H * (0.5 + sh)
                out.append(((W / 2, cy + span * H / 2), (W / 2, cy - span * H / 2)))
    return out


def match_corridors(im, naip, corridors_px, naip_res=0.6, out_h=320, **framing):
    """Which candidate hole corridor does a per-hole image show?

    Per-hole images (GPS-app screenshots, course-site hole maps) are framed along the hole: tee near the
    bottom, green toward the top. For every candidate corridor (tee px, green px in NAIP lo) and a few
    framings (corridor_framings), NAIP is pulled into the image grid and compared (NCC on gradient +
    excess-green channels).
    corridors_px: {id: ((tee_x, tee_y), (green_x, green_y))} -> {id: best score}, best first."""
    h0, w0 = im.shape[:2]
    k = out_h / h0
    W = max(32, int(round(w0 * k)))
    I = cv2.resize(im, (W, out_h), interpolation=cv2.INTER_AREA)
    ich = channels(I)
    ones = np.full(naip.shape[:2], 255, np.uint8)
    scores = {}
    for cid, (tee, green) in corridors_px.items():
        best = -1.0
        for a_tee, a_green in corridor_framings(W, out_h, tee, green, naip_res, k, **framing):
            M = _sim_from_pairs(a_tee, a_green, tee, green)        # image -> NAIP
            Minv = cv2.invertAffineTransform(M)
            R = cv2.warpAffine(naip, Minv, (W, out_h), flags=cv2.INTER_AREA, borderValue=0)
            valid = cv2.warpAffine(ones, Minv, (W, out_h), borderValue=0) > 0
            if valid.mean() < 0.6:
                continue
            rch = channels(R)
            best = max(best, sum(_ncc(a, b, valid) for a, b in zip(ich, rch)) / len(ich))
        scores[cid] = round(best, 4)
    return dict(sorted(scores.items(), key=lambda kv: -kv[1]))
