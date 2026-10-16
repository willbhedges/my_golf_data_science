"""Georeference the hand-traced Spirit Hollow screenshots (spirit_hollow/course.py) onto NAIP.

  python3 course_data/imagery/traced_align.py [--holes 17,5] [--plots DIR]

For each traced hole the screenshot frame (tee px, 270-dot px) has no georeference. We get it in two steps:
  1. initial guess: the green is at (along, lat) of the tee from the app's three "Center" numbers
     (course.green_from_app); the OSM hole line's last node is the green; the tee is the point on the
     OSM hole line at that distance from the green. Scale = the screenshot's px/yd.
  2. refine: render NAIP into the screenshot pixel grid with that guess, then cv2.findTransformECC
     (affine) between the cleaned screenshot and the render, on gradient-magnitude images (the
     screenshots are winter, NAIP is September, so edges match better than colours).
Writes course_data/imagery/spirit_hollow/traced_registration.json: per hole, the Frame (screen px of the
NAIP render) plus the 2x3 warp `screenshot px -> render px`, ECC score, and the fitted scale/rotation.
"""
import argparse
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "spirit_hollow"), os.path.join(ROOT, "mozingo")]

import render as R                                     # noqa: E402

COURSE = os.path.join(ROOT, "course_data", "spirit_hollow")
IMG_DIR = os.path.join(HERE, "spirit_hollow")
SHOTS = os.path.join(ROOT, "spirit_hollow", "screenshots_clean")
Y0 = 560                                               # screenshot rows above this are app chrome


def ref_of(k):
    return str(k)[:-1] if isinstance(k, str) else str(k)


def load_course():
    import course
    return course


def initial_frame(k, course, lines):
    h = course.HOLES[k]
    tee_s = np.array(h["tee"], float)
    v = np.array(h["dot270"], float) - tee_s
    ppy = np.linalg.norm(v) / 270.0
    fwd_s = v / np.linalg.norm(v)
    right_s = np.array([-fwd_s[1], fwd_s[0]])
    along, lat = course.green_from_app(*course.APP[k], course.GREEN_SIDE[k])
    d = math.hypot(along, lat)

    line = np.array(lines[ref_of(k)], float)
    g_ll = line[-1]
    fr0 = R.Frame(g_ll, line[0], proj="enu")           # planar yards about the green
    P = fr0._to_yd(line) - fr0.t0
    # walk back from the green to the first point at Euclidean distance d
    tee_xy = None
    for i in range(len(P) - 1, 0, -1):
        a, b = P[i], P[i - 1]
        if np.linalg.norm(b) >= d:
            # solve |a + t (b - a)| = d
            u = b - a
            A, B, C = u @ u, 2 * a @ u, a @ a - d * d
            t = (-B + math.sqrt(max(B * B - 4 * A * C, 0))) / (2 * A)
            tee_xy = a + t * u
            break
    if tee_xy is None:                                  # tee behind the line start: extrapolate
        u = P[0] - P[1]
        u /= np.linalg.norm(u)
        a = P[0]
        B, C = 2 * a @ u, a @ a - d * d
        t = (-B + math.sqrt(max(B * B - 4 * C, 0))) / 2
        tee_xy = a + t * u
    tee_ll = fr0._from_yd(fr0.t0 + tee_xy)[0]
    # world direction of the tee line: the green is at angle atan2(lat, along) right of it
    g_dir = -tee_xy / np.linalg.norm(tee_xy)            # tee -> green, (east, north)
    phi = math.atan2(lat, along)                        # clockwise from the line
    c, s = math.cos(phi), math.sin(phi)
    # rotate g_dir anticlockwise by phi -> line direction (east/north are anticlockwise-positive)
    u = np.array([c * g_dir[0] - s * g_dir[1], s * g_dir[0] + c * g_dir[1]])
    r = np.array([u[1], -u[0]])
    # screen up (0,-1) in (along, lat) components of the screenshot's frame
    up = np.array([0.0, -1.0])
    up_world = (up @ fwd_s) * u + (up @ right_s) * r
    aim_xy = tee_xy + 100 * up_world
    aim_ll = fr0._from_yd(fr0.t0 + aim_xy)[0]
    return R.Frame(tee_ll, aim_ll, ppy=ppy, tee_px=tee_s, proj="enu"), dict(along=along, lat=lat, ppy=ppy)


def grad_img(rgb, sigma=2.0):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), sigma)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    m = np.sqrt(gx * gx + gy * gy)
    m = cv2.GaussianBlur(m, (0, 0), sigma * 2)
    return m / (np.percentile(m, 99) + 1e-6)


def screenshot(h):
    im = Image.open(os.path.join(SHOTS, h["image"])).convert("RGB").resize((920, 2000), Image.LANCZOS)
    return np.asarray(im)


def _z(x, m=None):
    v = x[m] if m is not None else x
    return (x - v.mean()) / (v.std() + 1e-6)


def feat(rgb, valid=None):
    """Season-robust-ish feature: blurred brightness + bright small things (bunkers, cart paths)."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    th = cv2.GaussianBlur(cv2.morphologyEx(g, cv2.MORPH_TOPHAT, k), (0, 0), 3)
    gb = cv2.GaussianBlur(g, (0, 0), 3)
    f = _z(gb, valid) + _z(th, valid)
    if valid is not None:
        f[~valid] = 0
    return f.astype(np.float32)


def register(k, course, lines, img, plots=None, pad=260, s=0.25):
    """-> registration dict. warp: screenshot px -> px of the NAIP render in `frame` (padded canvas)."""
    h = course.HOLES[k]
    fr0, g = initial_frame(k, course, lines)
    fr = R.Frame(fr0.tee_ll, fr0.aim_ll, ppy=fr0.ppy, tee_px=fr0.tee_px + pad, proj="enu",
                 size=(920 + 2 * pad, 2000 + 2 * pad))
    ren, info = R.render(fr, img)
    shot = screenshot(h)
    valid = ren.sum(axis=2) > 0
    A0 = feat(shot)
    B0 = feat(ren, valid)
    c = np.array(h["tee"], float) + pad
    # 1) exhaustive rotation x scale; translation by normalised cross-correlation (matchTemplate)
    a = cv2.resize(A0, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    b = cv2.resize(B0, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    tpl = a[int(Y0 * s):int(1980 * s)]
    best = None
    for sc in np.arange(0.90, 1.101, 0.025):
        for th in np.arange(-14, 14.01, 1.0):
            M = cv2.getRotationMatrix2D((c[0] * s, c[1] * s), float(th), float(sc))
            bw = cv2.warpAffine(b, M, (b.shape[1], b.shape[0]), flags=cv2.WARP_INVERSE_MAP)
            res = cv2.matchTemplate(bw, tpl, cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(res)
            if best is None or mx > best[0]:
                best = (mx, float(th), float(sc), loc)
    cc0, th, sc, (u, v) = best
    A = cv2.getRotationMatrix2D((c[0], c[1]), th, sc)            # full-res, inverse-map matrix
    d = np.array([u / s, v / s - Y0])
    W = A.copy()
    W[:, 2] = A[:, :2] @ d + A[:, 2]                              # W(x) = A(x + d)
    warp = W.astype(np.float32)
    # 2) ECC refinement (affine) at half resolution
    ecc = float("nan")
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6)
    s2 = 0.5
    a2 = cv2.resize(A0, None, fx=s2, fy=s2, interpolation=cv2.INTER_AREA)
    b2 = cv2.resize(B0, None, fx=s2, fy=s2, interpolation=cv2.INTER_AREA)
    mask = np.zeros(a2.shape, np.uint8)
    mask[int(Y0 * s2):int(1980 * s2), :] = 1
    w0 = warp.astype(np.float32).copy()
    w0[:, 2] *= s2
    # ECC wants equal-size images: pre-warp the render into the screenshot grid, refine a small delta
    bpre = cv2.warpAffine(b2, w0, (a2.shape[1], a2.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    try:
        e, dl = cv2.findTransformECC(a2, bpre, np.eye(2, 3, dtype=np.float32), cv2.MOTION_AFFINE,
                                     crit, mask, 5)
        D = np.vstack([dl, [0, 0, 1]]).astype(float)
        W0 = np.vstack([w0, [0, 0, 1]]).astype(float)
        w1 = (W0 @ D)[:2]                                         # x -> w0(dl(x))
        w1[:, 2] /= s2
        Ad = w1[:, :2]
        scl = math.sqrt(abs(np.linalg.det(Ad)))
        shear = abs(Ad[:, 0] @ Ad[:, 1]) / (np.linalg.norm(Ad[:, 0]) * np.linalg.norm(Ad[:, 1]))
        moved = np.abs(dl - np.eye(2, 3)).max(), np.abs(dl[:, 2]).max() / s2
        if 0.88 < scl < 1.12 and shear < 0.05 and moved[1] < 60:
            warp, ecc = w1, float(e)
        else:
            print(f"   ECC rejected: scale {scl:.3f} shear {shear:.3f} shift {moved[1]:.0f}px")
    except cv2.error as ex:
        print("   ECC failed:", str(ex).strip().splitlines()[-1][:120])
    W2 = warp.astype(float)
    Ad = W2[:, :2]
    scl = math.sqrt(abs(np.linalg.det(Ad)))
    rot = math.degrees(math.atan2(Ad[1, 0], Ad[0, 0]))
    t_ren = Ad @ np.array(h["tee"], float) + W2[:, 2]
    tee_shift_yd = float(np.linalg.norm(t_ren - c) / fr.ppy)
    aligned = cv2.warpAffine(ren, W2, (920, 2000), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    m = np.zeros((2000, 920), bool)
    m[Y0:1980] = True
    m &= aligned.sum(axis=2) > 0
    corr = float(np.corrcoef(A0[m], feat(aligned)[m])[0, 1])
    res = dict(key=str(k), frame=fr.to_json(), warp=W2.tolist(), ncc_coarse=float(cc0), ecc=ecc,
               corr=corr, coarse=dict(rot_deg=th, scale=sc), scale=scl, rot_deg=rot,
               tee_shift_yd=tee_shift_yd, green_app=g, imagery_date=info["imagery_date"])
    if plots:
        os.makedirs(plots, exist_ok=True)
        blend = (0.5 * shot + 0.5 * aligned).astype(np.uint8)
        side = np.concatenate([shot, aligned, blend], axis=1)[Y0:]
        Image.fromarray(side).resize((side.shape[1] // 3, side.shape[0] // 3)).save(
            os.path.join(plots, f"reg_{k}.png"))
    return res


def screenshot_px_to_ll(reg, pts):
    """Traced-polygon screenshot px -> WGS84 via the registration."""
    fr = R.Frame.from_json(reg["frame"])
    W2 = np.array(reg["warp"])
    p = np.atleast_2d(np.asarray(pts, float))
    q = p @ W2[:, :2].T + W2[:, 2]
    return fr.px_to_ll(q)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holes")
    ap.add_argument("--plots")
    a = ap.parse_args()
    course = load_course()
    lines = R._osm_holes(COURSE)
    img = R.Imagery(IMG_DIR)
    keys = [k for k in course.HOLES if (a.holes is None or str(k) in a.holes.split(","))]
    out_p = os.path.join(IMG_DIR, "traced_registration.json")
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    for k in keys:
        r = register(k, course, lines, img, plots=a.plots)
        out[str(k)] = r
        print(f"{str(k):>3}: ncc {r['ncc_coarse']:.3f} {r['coarse']}  ecc {r['ecc']:.3f}  corr {r['corr']:.3f}  "
              f"scale {r['scale']:.3f}  rot {r['rot_deg']:+.1f}  tee moved {r['tee_shift_yd']:.0f} yd")
    with open(out_p, "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
