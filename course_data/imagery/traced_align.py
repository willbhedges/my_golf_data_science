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


def feat(rgb, kind):
    if kind == "grad":
        return grad_img(rgb)
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 3.0)
    return (g - g.mean()) / (g.std() + 1e-6)


def _rot(cx, cy, th, sc, dx, dy):
    M = cv2.getRotationMatrix2D((cx, cy), th, sc)
    M[0, 2] += dx
    M[1, 2] += dy
    return M


def register(k, course, lines, img, plots=None, kind="gray"):
    """-> registration dict. warp: screenshot px -> px of the NAIP render in `frame`."""
    h = course.HOLES[k]
    fr, g = initial_frame(k, course, lines)
    ren, info = R.render(fr, img)
    shot = screenshot(h)
    A0, B0 = feat(shot, kind), feat(ren, kind)
    valid0 = (ren.sum(axis=2) > 0).astype(np.uint8)
    tx, ty = h["tee"]
    # 1) coarse exhaustive search at 1/8 scale (rotation about the tee, shift, scale)
    s = 0.125
    a = cv2.resize(A0, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    b = cv2.resize(B0, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    vb = cv2.resize(valid0, (b.shape[1], b.shape[0]), interpolation=cv2.INTER_NEAREST)
    rows = np.zeros(a.shape, bool)
    rows[int(Y0 * s):int(1980 * s), :] = True
    best = None
    for sc in (0.94, 1.0, 1.06):
        for th in range(-10, 11, 2):
            for dy in range(-100, 101, 10):
                for dx in range(-60, 61, 10):
                    # M maps screenshot px -> render px
                    M = _rot(tx * s, ty * s, th, sc, dx * s, dy * s)
                    w = cv2.warpAffine(b, M, (a.shape[1], a.shape[0]), flags=cv2.WARP_INVERSE_MAP)
                    vw = cv2.warpAffine(vb, M, (a.shape[1], a.shape[0]), flags=cv2.WARP_INVERSE_MAP)
                    m = rows & (vw > 0)
                    if m.sum() < 0.5 * rows.sum():
                        continue
                    cc = np.corrcoef(a[m], w[m])[0, 1]
                    if best is None or cc > best[0]:
                        best = (cc, th, sc, dx, dy)
    cc0, th, sc, dx, dy = best
    warp = _rot(tx, ty, th, sc, dx, dy).astype(np.float32)
    # 2) ECC refinement (affine), coarse to fine
    ecc = float("nan")
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6)
    for s in (0.25, 0.5):
        a = cv2.resize(A0, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        b = cv2.resize(B0, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        mask = np.zeros(a.shape, np.uint8)
        mask[int(Y0 * s):int(1980 * s), :] = 1
        w0 = warp.copy()
        w0[:, 2] *= s
        try:
            e, w1 = cv2.findTransformECC(a, b, w0, cv2.MOTION_AFFINE, crit, mask, 5)
            w1[:, 2] /= s
            # reject runaway solutions (shear / scale outside the plausible range)
            Ad = w1[:, :2]
            scl = math.sqrt(abs(np.linalg.det(Ad)))
            shear = abs(Ad[0] @ Ad[1]) / (np.linalg.norm(Ad[0]) * np.linalg.norm(Ad[1]))
            if 0.9 < scl < 1.1 and shear < 0.05:
                warp, ecc = w1, float(e)
        except cv2.error:
            pass
    W2 = warp.astype(float)
    Ad = W2[:, :2]
    scl = math.sqrt(abs(np.linalg.det(Ad)))
    rot = math.degrees(math.atan2(Ad[1, 0], Ad[0, 0]))
    t_ren = Ad @ np.array(h["tee"], float) + W2[:, 2]
    tee_shift_yd = float(np.linalg.norm(t_ren - np.array(h["tee"], float)) / fr.ppy)
    # final full-res correlation on both feature types (quality indicator)
    aligned = cv2.warpAffine(ren, W2, (920, 2000), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    m = np.zeros((2000, 920), bool)
    m[Y0:1980] = True
    m &= aligned.sum(axis=2) > 0
    qual = {kk: float(np.corrcoef(feat(shot, kk)[m], feat(aligned, kk)[m])[0, 1]) for kk in ("gray", "grad")}
    res = dict(key=str(k), frame=fr.to_json(), warp=W2.tolist(), ecc=ecc, coarse_cc=float(cc0),
               coarse=dict(rot_deg=th, scale=sc, dx=dx, dy=dy), scale=scl, rot_deg=rot,
               tee_shift_yd=tee_shift_yd, corr=qual, green_app=g, imagery_date=info["imagery_date"])
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
        print(f"{str(k):>3}: coarse cc {r['coarse_cc']:.3f} {r['coarse']}  ecc {r['ecc']:.3f}  "
              f"scale {r['scale']:.3f}  rot {r['rot_deg']:+.1f}  tee moved {r['tee_shift_yd']:.0f} yd  "
              f"corr gray {r['corr']['gray']:.2f} grad {r['corr']['grad']:.2f}")
    with open(out_p, "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
