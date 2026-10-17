"""Hand-map labels for the v2 hazard model, on the vision_any 1 m grid, in one shape for every course.

  holes = load_holes("spirit_hollow")     # course_data/spirit_hollow/hand_zones_ll.json (GPS, hand-checked)
  holes = load_holes("mozingo")           # mozingo/tee_strategy.HOLES via vision_any/mozingo/traced_registration.json
  lab = rasterize_hole(S, holes[0])       # dict(cls int8 grid (-1 = outside footprint), foot, corridor geometry)

Each hole: dict(key, ref, zones=[(lie, [[lon, lat], ...]), ...] in priority order (later wins, unzoned = rough),
footprint_ll, tee_ll, dot270_ll). Lies: fairway, first_cut, rough, recovery (= trees), native, water, sand, ob.
LOHO groups are `ref` (2B / 2F are the same hole on the ground).
"""
import json
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
YD = 0.9144
CLASSES = ["rough", "first_cut", "fairway", "recovery", "native", "water", "sand", "ob"]
CI = {c: i for i, c in enumerate(CLASSES)}
CORRIDOR = dict(a0=190.0, a1=335.0, lat=55.0)          # landing corridors, yds from the tee
MOZ_MIN_DICE = 0.7
FOOT_Y_MOZ = (560, 1830)


def _ref(k):
    k = str(k)
    return k[:-1] if (not k.isdigit() and k[:-1].isdigit()) else k


def load_holes(slug):
    if slug == "spirit_hollow":
        d = json.load(open(os.path.join(ROOT, "course_data", "spirit_hollow", "hand_zones_ll.json")))
        out = []
        for k, h in d["holes"].items():
            out.append(dict(key=k, ref=_ref(k), zones=[(z["lie"], z["poly_ll"]) for z in h["zones"]],
                            footprint_ll=h["footprint_ll"], tee_ll=h["tee_ll"], dot270_ll=h["dot270_ll"],
                            src="hand_zones_ll.json"))
        return out
    if slug == "mozingo":
        for p in (os.path.join(ROOT, "mozingo"),):
            if p not in sys.path:
                sys.path.insert(0, p)
        import tee_strategy as t
        regs = json.load(open(os.path.join(HERE, "mozingo", "traced_registration.json")))
        out = []
        for k, h in t.HOLES.items():
            r = regs.get(str(k))
            if not r or r["dice"] < MOZ_MIN_DICE:
                continue
            A = np.array(r["affine_px_to_ll"])
            f = lambda p: (np.atleast_2d(np.asarray(p, float)) @ A[:, :2].T + A[:, 2]).tolist()  # noqa: E731
            y0, y1 = FOOT_Y_MOZ
            out.append(dict(key=str(k), ref=str(k), zones=[(lie, f(poly)) for lie, poly in h["zones"]],
                            footprint_ll=f([(0, y0), (920, y0), (920, y1), (0, y1)]), tee_ll=f([h["tee"]])[0],
                            dot270_ll=f([h["dot270"]])[0], src=f"tee_strategy.HOLES + register_mozingo (dice {r['dice']})"))
        return out
    return []


def _fill(S, poly_ll):
    m = np.zeros((S.H, S.W), np.uint8)
    pts = np.round(S.ll_to_rc(np.asarray(poly_ll, float)) * 8).astype(np.int32)
    cv2.fillPoly(m, [pts], 1, shift=3)
    return m > 0


def corridor_coords(S, h):
    """(along, lat) in yards of every grid cell centre for hole h (tee line = tee -> dot270)."""
    rc = S.ll_to_rc([h["tee_ll"], h["dot270_ll"]])
    t, d = rc[0], rc[1]
    f = (d - t) / np.linalg.norm(d - t)
    r = np.array([-f[1], f[0]])                    # grid (col, row) with row down: this is golfer's right
    cc, rr = np.meshgrid(np.arange(S.W) + 0.5, np.arange(S.H) + 0.5)
    dx, dy = cc - t[0], rr - t[1]
    along = (dx * f[0] + dy * f[1]) * S.res / YD
    lat = (dx * r[0] + dy * r[1]) * S.res / YD
    return along.astype(np.float32), lat.astype(np.float32)


def corridor_mask(along, lat, c=CORRIDOR):
    return (along >= c["a0"]) & (along <= c["a1"]) & (np.abs(lat) <= c["lat"])


def rasterize_hole(S, h):
    """-> dict(cls int8 (-1 outside footprint), foot bool, along, lat, corr bool (corridor & footprint))."""
    foot = _fill(S, h["footprint_ll"])
    cls = np.zeros((S.H, S.W), np.int8)
    for lie, poly in h["zones"]:
        if lie not in CI or len(poly) < 3:
            continue
        cls[_fill(S, poly)] = CI[lie]
    cls[~foot] = -1
    along, lat = corridor_coords(S, h)
    return dict(cls=cls, foot=foot, along=along, lat=lat, corr=corridor_mask(along, lat) & foot)


def train_mask(cls, erode=1, rough_within_m=60.0):
    """Cells usable for training: inside the footprint, >= `erode` cells from a class boundary (registration
    and tracing noise), not OB, and rough only within rough_within_m of a hand fairway / first cut."""
    keep = np.zeros(cls.shape, bool)
    for c in range(len(CLASSES)):
        m = cls == c
        if m.any():
            keep |= ndimage.binary_erosion(m, iterations=erode) if erode else m
    keep &= (cls >= 0) & (cls != CI["ob"])
    mown = (cls == CI["fairway"]) | (cls == CI["first_cut"])
    if mown.any():
        near = ndimage.distance_transform_edt(~mown) <= rough_within_m
        keep &= ~((cls == CI["rough"]) & ~near)
    return keep
