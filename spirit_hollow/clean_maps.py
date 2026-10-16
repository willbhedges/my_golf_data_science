"""Remove the GPS app's drawings from the screenshots so the book shows only our aim.

  python3 spirit_hollow/clean_maps.py      -> screenshots_clean/<same name>.png

What gets removed: the red tee line and yardage dots, the white dispersion bars, the black
hole outline, the "Abstract" button and scale bar, the +/-/3D buttons, and the header and
footer (cropped). Removed pixels are filled by OpenCV inpainting (Telea's fast-marching
method for thin lines; Navier-Stokes for the larger button patches), which continues the
surrounding texture inward. The cleaned images keep the 920x2000 coordinate frame (the
cropped header/footer rows are left as a flat colour and never shown), so every traced
coordinate in course.py still lines up.
"""
import glob
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "screenshots")
DST = os.path.join(HERE, "screenshots_clean")
K = 1206 / 920                            # screenshot px per frame px
TOP, BOTTOM = 540, 1832                   # frame rows of real map

# App buttons / labels, frame coords (x0, y0, x1, y1); identical on every screenshot.
BUTTONS = [(20, 550, 232, 660),           # "Abstract" + scale bar
           (0, 545, 480, 606),            # scale bar text + line
           (800, 556, 900, 660),          # +
           (800, 662, 900, 762),          # -
           (754, 768, 900, 866),          # 3D
           (0, 500, 40, 560)]             # clipped green marker in the corner


def overlay_mask(bgr):
    b, g, r = [bgr[..., i].astype(int) for i in range(3)]
    red = (r > 175) & (g < 90) & (b < 90) & (r - g > 110)
    white = (r > 225) & (g > 225) & (b > 225)
    black = ((r < 28) & (g < 28) & (b < 28)).astype(np.uint8)
    # the hole outline is a ~6 px line: keep only thin black, never solid dark areas (ponds).
    # A line crossing a dark pond is near-black too, so also take very dark pixels that sit
    # right on the thin-line skeleton's path.
    solid = cv2.morphologyEx(black, cv2.MORPH_OPEN, np.ones((13, 13), np.uint8))
    thin_black = (black > 0) & (solid == 0)
    near = cv2.dilate(thin_black.astype(np.uint8), np.ones((3, 41), np.uint8)) | \
        cv2.dilate(thin_black.astype(np.uint8), np.ones((41, 3), np.uint8))
    very_dark = (r < 14) & (g < 14) & (b < 14)
    black = thin_black | ((near > 0) & very_dark)
    m = (red | white | black).astype(np.uint8)
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))              # catch anti-aliased edges
    big = np.zeros_like(m)
    for x0, y0, x1, y1 in BUTTONS:
        big[int(y0 * K):int(y1 * K), int(x0 * K):int(x1 * K)] = 1
    return m, big


def clean(path):
    bgr = cv2.imread(path)
    thin, big = overlay_mask(bgr)
    top, bot = int(TOP * K), int(BOTTOM * K)
    work = bgr.copy()
    # fill in the map band only; lines first, then the button patches from the result
    band = work[top:bot]
    band = cv2.inpaint(band, thin[top:bot], 9, cv2.INPAINT_TELEA)
    work[top:bot] = band
    # buttons: mirror the real imagery just below each patch up into it, then blend the seam
    for x0, y0, x1, y1 in BUTTONS:
        X0, Y0, X1, Y1 = int(x0 * K), max(int(y0 * K), top), int(x1 * K), int(y1 * K)
        h = Y1 - Y0
        if h <= 0:
            continue
        w = X1 - X0
        if x0 >= 750:                      # right-hand button column: mirror from the left
            src = work[Y0:Y1, X0 - w:X0][:, ::-1].copy()
        else:
            src = work[Y1:Y1 + h, X0:X1][::-1].copy()
        if src.shape[:2] != (h, w):
            continue
        # Poisson (seamless) blending matches the patch's colour/brightness to its border
        X1c = min(X1, work.shape[1] - 2)
        src = src[:, :X1c - X0]
        mask = np.full(src.shape[:2], 255, np.uint8)
        centre = (X0 + (X1c - X0) // 2, Y0 + h // 2)
        try:
            work = cv2.seamlessClone(src, work, mask, centre, cv2.NORMAL_CLONE)
        except cv2.error:
            work[Y0:Y1, X0:X1c] = src
    seam = np.zeros(work.shape[:2], np.uint8)
    for x0, y0, x1, y1 in BUTTONS:
        X0, Y0, X1, Y1 = int(x0 * K), max(int(y0 * K), top), int(x1 * K), int(y1 * K)
        cv2.rectangle(seam, (X0, Y0), (X1, Y1), 1, 6)
    work[top:bot] = cv2.inpaint(work[top:bot], seam[top:bot], 5, cv2.INPAINT_TELEA)
    work[:top] = work[top]                                     # flat fill (never displayed)
    work[bot:] = work[bot - 1]
    out = cv2.resize(work, (bgr.shape[1], bgr.shape[0]))
    return out


def main():
    os.makedirs(DST, exist_ok=True)
    for p in sorted(glob.glob(os.path.join(SRC, "*.png"))):
        cv2.imwrite(os.path.join(DST, os.path.basename(p)), clean(p))
        print("cleaned", os.path.basename(p), flush=True)


if __name__ == "__main__":
    main()
