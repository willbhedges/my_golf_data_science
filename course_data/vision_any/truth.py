"""Hand-traced truth for validation and training: spirit_hollow/course.py zones georeferenced onto NAIP by
course_data/imagery/traced_align.py (traced_registration.json), put on the vision_any grid.

    T = SpiritHollowTruth(S)          # S = layers.Stack for spirit_hollow
    T.keys                             # traced holes with a usable registration
    T.label_raster(k)                  # int8 grid: class index (CLASSES) or -1 outside the footprint
    T.landing(k)                       # landing-zone points: ll, traced lie, along/lat
"""
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "course_data", "imagery"), os.path.join(ROOT, "spirit_hollow"),
          os.path.join(ROOT, "mozingo"), os.path.join(ROOT, "course_data")):
    if p not in sys.path:
        sys.path.append(p)

REG = os.path.join(ROOT, "course_data", "imagery", "spirit_hollow", "traced_registration.json")
FOOT_Y = (560, 1830)                  # screenshot rows that show ground
BAD_REG = {"2B"}                      # registration failed (scale at the search bound, tee moved 87 yds)
MIN_CORR = 0.18
CLASSES = ["rough", "fairway", "recovery", "native", "water", "sand", "ob"]
LANDING = dict(a0=220, a1=340, lat=45, step=5)


def landing_grid():
    a, l = np.meshgrid(np.arange(LANDING["a0"], LANDING["a1"] + 1, LANDING["step"]),
                       np.arange(-LANDING["lat"], LANDING["lat"] + 1, LANDING["step"]))
    return a.ravel().astype(float), l.ravel().astype(float)


def frame(h):
    tee = np.array(h["tee"], float)
    v = np.array(h["dot270"], float) - tee
    ppy = np.linalg.norm(v) / 270.0
    f = v / np.linalg.norm(v)
    return tee, f, np.array([-f[1], f[0]]), ppy


def to_px(h, along, lat):
    tee, f, r, ppy = frame(h)
    return tee + (np.asarray(along)[:, None] * f + np.asarray(lat)[:, None] * r) * ppy


def norm_lie(x):
    return "rough" if x == "first_cut" else x


class Truth:
    """Common part: self.HOLES (course.py-style, screenshot px), self.keys, px_to_ll / ll_to_px."""
    name = "?"

    def _poly_rc(self, k, pts):
        return np.round(self.S.ll_to_rc(self.px_to_ll(k, pts)) * 8).astype(np.int32)

    def reg_quality(self, k):
        return None


class MozingoTruth(Truth):
    """mozingo/tee_strategy.HOLES registered by register_mozingo.py (rigid fit on fairway/water/sand)."""
    name = "mozingo"
    MIN_DICE = 0.7

    def __init__(self, S):
        import tee_strategy as t
        self.t, self.S = t, S
        self.HOLES = dict(t.HOLES)
        self.regs = json.load(open(os.path.join(HERE, "mozingo", "traced_registration.json")))
        self.keys = [k for k in self.HOLES if str(k) in self.regs and self.regs[str(k)]["dice"] >= self.MIN_DICE]

    def px_to_ll(self, k, px):
        A = np.array(self.regs[str(k)]["affine_px_to_ll"])
        p = np.atleast_2d(np.asarray(px, float))
        return p @ A[:, :2].T + A[:, 2]

    def ll_to_px(self, k, ll):
        A = np.array(self.regs[str(k)]["affine_px_to_ll"])
        return (np.atleast_2d(np.asarray(ll, float)) - A[:, 2]) @ np.linalg.inv(A[:, :2]).T

    def reg_quality(self, k):
        return dict(method="lie_raster_fit", dice=self.regs[str(k)]["dice"])


class SpiritHollowTruth(Truth):
    name = "spirit_hollow"

    def __init__(self, S):
        import course
        import tee_strategy as t
        import traced_align as TA
        self.course, self.t, self.TA, self.S = course, t, TA, S
        self.HOLES = course.HOLES
        self.regs = json.load(open(REG))
        self.keys = [k for k in course.HOLES if str(k) in self.regs and str(k) not in BAD_REG
                     and (self.regs[str(k)].get("corr") or 0) >= MIN_CORR]

    def reg_quality(self, k):
        r = self.regs[str(k)]
        return dict(method="naip_ecc", ecc=r.get("ecc"), corr=round(r["corr"], 3))

    def px_to_ll(self, k, px):
        return self.TA.screenshot_px_to_ll(self.regs[str(k)], np.asarray(px, float))

    def ll_to_px(self, k, ll):
        """Inverse of px_to_ll (WGS84 -> traced screenshot px)."""
        import render as R
        reg = self.regs[str(k)]
        fr = R.Frame.from_json(reg["frame"])
        W2 = np.array(reg["warp"])
        q = fr.ll_to_px(np.asarray(ll, float))
        A, b = W2[:, :2], W2[:, 2]
        return (q - b) @ np.linalg.inv(A).T


class _Methods:
    def label_raster(self, k, rough_within_yd=25):
        """Grid of class indices from the traced zones (later zones win, as lie_at); -1 = ignore: outside
        the screenshot footprint, OB, rough farther than rough_within_yd from a traced fairway, and a 2 m
        band along every class boundary."""
        from scipy import ndimage
        S = self.S
        h = self.HOLES[k]
        cls = np.zeros((S.H, S.W), np.int8)
        for name, pts in h["zones"]:
            name = norm_lie(name)
            if name not in CLASSES:
                continue
            m = np.zeros((S.H, S.W), np.uint8)
            cv2.fillPoly(m, [self._poly_rc(k, pts)], 1, shift=3)
            cls[m > 0] = CLASSES.index(name)
        foot = np.zeros((S.H, S.W), np.uint8)
        cv2.fillPoly(foot, [self._poly_rc(k, [(0, FOOT_Y[0]), (920, FOOT_Y[0]), (920, FOOT_Y[1]), (0, FOOT_Y[1])])],
                     1, shift=3)
        lab = cls.copy()
        fw = cls == CLASSES.index("fairway")
        near = ndimage.distance_transform_edt(~fw) * S.res <= rough_within_yd * 0.9144
        lab[(cls == 0) & ~near] = -1
        keep = np.zeros((S.H, S.W), bool)
        for c in range(len(CLASSES)):
            keep |= ndimage.binary_erosion(cls == c, iterations=2)
        lab[~keep | (foot == 0) | (cls == CLASSES.index("ob"))] = -1
        return lab, foot > 0

    def landing(self, k):
        h = self.HOLES[k]
        al, la = landing_grid()
        px = to_px(h, al, la)
        lie = np.array([norm_lie(x) for x in self.t.lie_at(h, px)], dtype=object)
        return dict(along=al, lat=la, px=px, ll=self.px_to_ll(k, px), lie=lie)


Truth.label_raster = _Methods.label_raster
Truth.landing = _Methods.landing


def for_course(slug, S):
    return {"spirit_hollow": SpiritHollowTruth, "mozingo": MozingoTruth}[slug](S)
