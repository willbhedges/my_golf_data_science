"""Approach-shot layer for the tee-shot engine: club + aim point into any green, by expected strokes.

    from course_data.strategy import approach as A
    hole = A.Hole.from_package("blue_hills", "4")                 # read-only package.json
    r = A.solve(hole, start=(-20, -280), lie="fairway")           # yard frame of the package
    r["best"]   -> {"club": "8-iron", "target": [x, y], "ev": 3.02, "plays_like": 161, ...}
    r["centre"] -> the same model, aim fixed at the green centroid (best club for it)

Frame: the package's yard frame (x = yds right of the tee line, y = -yds along it; tee at (0, 0)), so tee-shot
finishing spots from mozingo/tee_strategy.simulate map in with (px - tee_px) / ppy.

Model (APPROACH.md has the evidence and the numbers):
  * Bag: the golfer's woods / 4-iron / 6-iron numbers exactly as the tee model (tee_strategy.CLUBS / IRONS:
    Driver 275/300, 2-wood 265/280, 4-wood 255/270, "Long iron" = 4-iron 210/220, "Mid iron" = 6-iron 185/192)
    plus 12-yd gapping down to a 100-yd lob wedge. Off the deck the woods lose ~10 yds (no tee). Each club
    covers [total - 12, total + 3] (smooth / choke-down; the 4-wood swung smooth down to 222 fills the gap
    to the 4-iron); under 100 yds a partial wedge.
  * Plays-like distance to an aim point = horizontal yds + elevation (green higher than the ball by dh ft ->
    dh*0.3048/tan(50 deg)/0.9144 yds, course_data/elevation/adjust.py's par-3 rule) / the wind + temperature
    carry factor of the club that plays that distance (spirit_hollow/wind.py adjust / temperature_adjust:
    same physics as the tee shots and the par-3 "plays like" box). The golfer clubs and aims so the MEAN ball
    finishes on the aim point (the drift is aimed off and reported); wind widens the pattern by wind.py's
    width / depth factors.
  * Dispersion: the repo's approach pattern (spirit_hollow/approach/shots.py, fitted to 5-hcp proximity:
    lateral sigma 7.0 yd at 100, 9.4 at 150, 13.4 at 200; depth sigma 1.5x lateral; first cut / rough / sand /
    trees widen it; reach capped by lie). Over 200 yds 15% mishits finish 75-92% of the distance. Off the
    tee the tee model's own club widths stay in force (this module never changes tee numbers).
  * Expected strokes after the shot (PGA Tour, Broadie, as the tee engine; hcp=True adds ~5-hcp offsets):
    on the green putts by feet to the pin; off the green within 40 yds the short-game table by lie to the pin,
    plus a SHORT-SIDE cost when little green lies between the ball and the pin; beyond 40 yds
    tee_strategy.expected_strokes; trees = recovery row; water = 1 + rough near where it finished;
    OB = stroke and distance (1 + expected strokes from where the shot was played).
  * Unknown pin: averaged over 12 pins spread on the green (>= 4 yds from the edge); or pass pin=(x, y).
  * Lay-ups: when the green is out of reach (or close to it) fairway spots within reach are candidate aims too,
    scored by the same after-shot table.

Common random numbers across all aims and clubs; n swings per evaluation (default 400).
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "mozingo"), os.path.join(ROOT, "spirit_hollow")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tee_strategy as t                       # noqa: E402  tour tables, tee clubs, tee simulate
import wind as W                               # noqa: E402  spirit_hollow/wind.py (physics only)

PACKAGES = os.path.join(ROOT, "course_data", "packages")
YD, FT = 0.9144, 0.3048
DESCENT_DEG = 50.0                              # elevation/adjust.py: iron landing angle for plays-like

# ------------------------------------------------------------------ bag
# name: (carry, total) in calm 70 F air, wind.py sensitivity key. Woods/4i/6i = tee_strategy numbers.
BAG = {
    "2-wood": ((265, 280), "2-wood"),
    "4-wood": ((255, 270), "4-wood"),
    "4-iron": (t.IRONS["Long iron"][:2], "Long iron"),      # 210 / 220
    "5-iron": ((198, 206), "Long iron"),
    "6-iron": (t.IRONS["Mid iron"][:2], "Mid iron"),        # 185 / 192
    "7-iron": ((174, 180), "Mid iron"),
    "8-iron": ((162, 167), "Mid iron"),
    "9-iron": ((150, 154), "Mid iron"),
    "PW": ((138, 141), "Mid iron"),
    "GW": ((126, 128), "Mid iron"),
    "SW": ((113, 114), "Mid iron"),
    "LW": ((100, 101), "Mid iron"),
}
DECK_LOSS = {"2-wood": 15.0, "4-wood": 10.0}     # off the turf, no tee (approach/shots.py: 265 / 258)
CLUB_LOW, CLUB_HIGH = 12.0, 3.0                  # a club covers [total - 12, total + 3]
# The golfer's bag has no club between the 4-iron (220) and the 4-wood off the deck (~260): the 4-wood is
# swung smooth down to the 4-iron (approach/shots.py CLUB_FOR: "4-wood (smooth)"); v2 lists a ~235 hybrid
# as a hypothetical gap club, never in the bag.
SMOOTH_LOW = {"2-wood": 20.0, "4-wood": 40.0}
MIN_SHOT = 5.0
REACH = {"fairway": 275.0, "first_cut": 268.0, "rough": 235.0, "sand": 190.0, "recovery": 140.0,
         "green": 275.0}
# (lateral, depth) multipliers on the fairway pattern (approach/shots.py; trees = punch / restricted swing)
LIE_MULT = {"fairway": (1.0, 1.0), "green": (1.0, 1.0), "first_cut": (1.08, 1.12), "rough": (1.2, 1.35),
            "sand": (1.4, 1.5), "recovery": (1.6, 1.8)}
SIG_D = np.array([30, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275], float)
SIG_LAT = np.array([3.5, 4.5, 5.8, 7.0, 8.2, 9.4, 11.2, 13.4, 15.8, 18.5, 21.0])
DEPTH_RATIO = 1.5
MISHIT_FROM, MISHIT_RATE, MISHIT_RANGE = 200.0, 0.15, (0.75, 0.92)

# ------------------------------------------------------------------ scoring tables (Tour; Broadie)
PUTT_FT = np.array([1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 90], float)
PUTTS = np.array([1.00, 1.01, 1.04, 1.13, 1.23, 1.34, 1.50, 1.61, 1.78, 1.87, 1.98, 2.06, 2.14, 2.21, 2.40])
SHORT_D = np.array([2, 5, 10, 15, 20, 30, 40], float)
SHORT = {"fairway": [1.95, 2.05, 2.18, 2.30, 2.40, 2.52, 2.60],
         "first_cut": [2.00, 2.10, 2.23, 2.36, 2.47, 2.58, 2.66],
         "rough": [2.10, 2.20, 2.34, 2.47, 2.59, 2.70, 2.78],
         "sand": [2.30, 2.37, 2.43, 2.48, 2.53, 2.66, 2.82],
         "recovery": [3.00, 3.10, 3.20, 3.30, 3.40, 3.48, 3.55]}
# Short-sided: little green between the ball and the pin. Extra strokes at zero green to work with, fading
# linearly to 0 at SHORT_SIDE_RUN yds of green (Broadie / Arccos: tour up-and-down ~60% normal vs ~40-45%
# short-sided from greenside rough; a 15-20 point drop ~ 0.15-0.2 strokes; amateurs lose about the same).
SHORT_SIDE = {"fairway": 0.08, "first_cut": 0.12, "rough": 0.18, "sand": 0.15}
SHORT_SIDE_RUN = 10.0
HCP_PUTT, HCP_SHORT = 0.06, 0.15                # 5-hcp offsets (approach/shots.py, research.md section 2)

LIES = ["rough", "fairway", "first_cut", "sand", "recovery", "native", "water", "ob", "green"]
CODE = {k: i for i, k in enumerate(LIES)}
RES = 1.0


def putts(ft, hcp=False):
    ft = np.asarray(ft, float)
    e = np.interp(np.clip(ft, 1, 90), PUTT_FT, PUTTS) + np.maximum(ft - 90, 0) * 0.005
    return e + (HCP_PUTT if hcp else 0.0)


def baseline(lie, dist, hcp=False):
    """Expected strokes to hole out from a lie at `dist` yds, no geometry (green: putts)."""
    dist = np.asarray(dist, float)
    if lie == "green":
        return putts(dist * 3.0, hcp)
    key = "fairway" if lie == "green" else lie
    saved = t.HCP_BASELINE
    t.HCP_BASELINE = hcp
    try:
        long = t.expected_strokes(key, np.maximum(dist, 20))
    finally:
        t.HCP_BASELINE = saved
    if key in SHORT:
        short = np.interp(np.clip(dist, 2, 40), SHORT_D, SHORT[key]) + (HCP_SHORT if hcp else 0.0)
        return np.where(dist < 40, short, long)
    return long


def sigma(dist, lie="fairway"):
    lat = np.interp(dist, SIG_D, SIG_LAT)
    ml, md = LIE_MULT.get(lie, (1.0, 1.0))
    return lat * ml, lat * DEPTH_RATIO * md


# ------------------------------------------------------------------ conditions
class Conditions:
    """Wind (mph, FROM degrees true), temperature (F), exposure scale (package 'exposure' -> wind_page)."""

    def __init__(self, wind_mph=0.0, wind_from=0.0, temp_f=W.TEMP_BASE_F, exposure=1.0, gust_mph=None):
        self.wind_mph, self.wind_from, self.temp_f = float(wind_mph), float(wind_from), float(temp_f)
        self.exposure, self.gust_mph = float(exposure), gust_mph

    def club(self, name, bearing_deg, lie="fairway"):
        """(carry, total, width factor, depth factor, drift yds +right) for a full swing on this bearing."""
        (carry, total), sens = BAG[name]
        if lie != "green" and name in DECK_LOSS:
            carry, total = carry - DECK_LOSS[name], total - DECK_LOSS[name]
        tup = W.temperature_adjust((carry, total, 40.0, 20.0), self.temp_f)
        if self.wind_mph <= 0 and self.gust_mph is None:
            return tup[0], tup[1], 1.0, 1.0, 0.0
        rel = W.hole_relative(self.wind_from, bearing_deg)
        c, tot, w, d, drift = W.adjust(tup, self.wind_mph, rel, club_name=sens, gust_mph=self.gust_mph,
                                       exposure=self.exposure)
        return c, tot, w / 40.0, d / 20.0, drift


CALM = Conditions()


# ------------------------------------------------------------------ hole geometry
class Hole:
    """Lie raster (1 yd) in the package yard frame, green polygon, elevation along the tee line."""

    def __init__(self, zones, green_poly, tee_bearing=0.0, profile=None, green_elev=None, key="?", par=4,
                 name="", pad=45.0):
        self.key, self.par, self.name = key, par, name
        self.green = np.asarray(green_poly, float)
        self.green_path = Path(self.green)
        self.green_c = _centroid(self.green)
        self.tee_bearing = float(tee_bearing)
        pts = [self.green, np.zeros((1, 2))] + [np.asarray(p, float) for _, p in zones]
        allp = np.vstack(pts)
        lo = np.maximum(allp.min(0) - pad, [-200, -800])
        hi = np.minimum(allp.max(0) + pad, [200, 60])
        lo = np.minimum(lo, self.green.min(0) - pad)
        hi = np.maximum(hi, self.green.max(0) + pad)
        self.x = np.arange(lo[0], hi[0] + RES / 2, RES)
        self.y = np.arange(lo[1], hi[1] + RES / 2, RES)
        XX, YY = np.meshgrid(self.x, self.y, indexing="ij")
        cells = np.c_[XX.ravel(), YY.ravel()]
        lie = np.zeros(len(cells), np.int8)
        for name_, poly in zones:                       # package order, later wins (as tee_strategy)
            if name_ in CODE:
                lie[Path(np.asarray(poly, float)).contains_points(cells)] = CODE[name_]
        lie[self.green_path.contains_points(cells)] = CODE["green"]
        self.lie = lie.reshape(XX.shape)
        self.XX, self.YY = XX, YY
        prof = sorted(profile or [(0.0, 0.0)])
        if green_elev is not None:
            prof = sorted([p for p in prof if p[0] < green_elev[0] - 5] + [tuple(green_elev)])
        self.prof_a = np.array([p[0] for p in prof], float)
        self.prof_h = np.array([p[1] for p in prof], float)
        self._pins = None

    # -- construction from a platform package (read-only)
    @classmethod
    def from_package(cls, slug, key, pkg=None):
        if pkg is None:
            pkg = load_package(slug)
        h = pkg["holes"][str(key)]
        e = h.get("elevation") or {}
        prof = [(p["yd"], p["band_ft_rel_tee"]) for p in e.get("profile") or []
                if p.get("band_ft_rel_tee") is not None]
        g = e.get("green") or {}
        ge = (g["along_yd"], g["delta_ft"]) if g.get("delta_ft") is not None else None
        return cls(h["zones"], h["green_polygon_yd"], h.get("bearing_deg", 0.0), prof, ge, key=str(key),
                   par=h["par"], name=pkg["course"]["name"])

    def idx(self, p):
        p = np.asarray(p, float)
        ix = np.clip(np.rint((p[..., 0] - self.x[0]) / RES).astype(np.int32), 0, len(self.x) - 1)
        iy = np.clip(np.rint((p[..., 1] - self.y[0]) / RES).astype(np.int32), 0, len(self.y) - 1)
        return ix, iy

    def lie_at(self, p):
        return self.lie[self.idx(p)]

    def lie_name(self, p):
        return LIES[int(self.lie_at(np.asarray(p, float)))]

    def elev_ft(self, p):
        """Ground height (ft rel. tee) from the tee-line profile, by distance along the line."""
        along = -np.asarray(p, float)[..., 1]
        return np.interp(along, self.prof_a, self.prof_h)

    def bearing(self, start, aim):
        v = np.asarray(aim, float) - np.asarray(start, float)
        return (self.tee_bearing + math.degrees(math.atan2(v[0], -v[1]))) % 360.0

    def pins(self, k=12, inset=4.0, seed=3):
        """k pin spots spread over the green, >= inset yds from its edge (fixed seed)."""
        if self._pins is not None and len(self._pins) == k:
            return self._pins
        m = self.lie == CODE["green"]
        cand = np.c_[self.XX[m], self.YY[m]]
        d = _edge_dist(cand, self.green)
        pool = cand[d >= inset]
        if len(pool) < k:
            pool = cand[np.argsort(-d)[:max(k, 1)]]
        # spread: farthest-point sampling from a random start (deterministic)
        rng = np.random.default_rng(seed)
        pick = [int(rng.integers(len(pool)))]
        dmin = np.hypot(*(pool - pool[pick[0]]).T)
        while len(pick) < min(k, len(pool)):
            j = int(np.argmax(dmin))
            pick.append(j)
            dmin = np.minimum(dmin, np.hypot(*(pool - pool[j]).T))
        self._pins = pool[pick]
        return self._pins


def _centroid(poly):
    x, y = poly[:, 0], poly[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    c = x * y1 - x1 * y
    a = c.sum() / 2
    if abs(a) < 1e-9:
        return poly.mean(0)
    return np.array([((x + x1) * c).sum() / (6 * a), ((y + y1) * c).sum() / (6 * a)])


def _edge_dist(pts, poly):
    d = np.full(len(pts), np.inf)
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        ab = b - a
        den = float(ab @ ab) or 1e-9
        u = np.clip(((pts - a) @ ab) / den, 0, 1)
        d = np.minimum(d, np.hypot(*(pts - (a + u[:, None] * ab)).T))
    return d


def load_package(slug):
    with open(os.path.join(PACKAGES, slug, "package.json")) as fh:
        return json.load(fh)


# ------------------------------------------------------------------ value after the shot
def value_map(hole, pins, hcp=False):
    """Expected strokes to hole out from every raster cell, averaged over `pins` (K x 2).
    OB cells are NaN (stroke and distance depends on where the shot was played from)."""
    pins = np.atleast_2d(np.asarray(pins, float))
    key = (pins.tobytes(), hcp)
    cache = hole.__dict__.setdefault("_vcache", {})
    if key in cache:
        return cache[key]
    lie = hole.lie
    S = np.full(lie.shape, np.nan)
    gc = hole.green_c
    dc = np.hypot(hole.XX - gc[0], hole.YY - gc[1])
    dmin = np.min([np.hypot(hole.XX - p[0], hole.YY - p[1]) for p in pins], axis=0)
    near = dmin < 45
    # green
    m = lie == CODE["green"]
    S[m] = np.mean([putts(np.hypot(hole.XX[m] - p[0], hole.YY[m] - p[1]) * 3.0, hcp) for p in pins], axis=0)
    green_mask = lie == CODE["green"]
    for name in ("fairway", "first_cut", "rough", "sand"):
        m = lie == CODE[name]
        if not m.any():
            continue
        far = m & ~near
        S[far] = baseline(name, dc[far], hcp)
        mn = m & near
        if mn.any():
            cx, cy = hole.XX[mn], hole.YY[mn]
            acc = np.zeros(mn.sum())
            for p in pins:
                dp = np.hypot(cx - p[0], cy - p[1])
                v = baseline(name, dp, hcp)
                if name in SHORT_SIDE:
                    run = _green_run(hole, green_mask, cx, cy, p)
                    v = v + SHORT_SIDE[name] * np.clip(1 - run / SHORT_SIDE_RUN, 0, 1) * (dp < 40)
                acc += v
            S[mn] = acc / len(pins)
    rough_d = lambda d: baseline("rough", np.maximum(d, 2), hcp)       # noqa: E731
    m = lie == CODE["recovery"]
    rec = baseline("recovery", np.maximum(dmin[m], 2), hcp)
    S[m] = t.TREE_SEVERITY * rec + (1 - t.TREE_SEVERITY) * rough_d(dmin[m])
    m = lie == CODE["native"]
    S[m] = t.NATIVE_LOST * (2.0 + rough_d(dmin[m])) + (1 - t.NATIVE_LOST) * baseline("recovery", np.maximum(dmin[m], 2), hcp)
    m = lie == CODE["water"]                                           # drop near where it went in
    S[m] = 1.0 + rough_d(np.maximum(dmin[m], 10))
    cache[key] = S
    return S


def _green_run(hole, green_mask, cx, cy, pin, steps=16):
    """Yds of green on the straight line from each cell to the pin (what a chip has to work with)."""
    L = np.hypot(pin[0] - cx, pin[1] - cy)
    run = np.zeros(len(cx))
    for s in (np.arange(steps) + 0.5) / steps:
        px, py = cx + (pin[0] - cx) * s, cy + (pin[1] - cy) * s
        run += green_mask[hole.idx(np.stack([px, py], -1))]
    return run / steps * L


# ------------------------------------------------------------------ the shot
def z_draws(n=400, seed=0):
    r = np.random.default_rng(seed)
    return np.vstack([r.standard_normal((2, n)), r.random((2, n))])


def club_for(dist_eff, lie, cond, bearing):
    """Club that plays `dist_eff` (calm-equivalent plays-like yds incl. elevation) with a stock or smooth swing
    -> (name, swing factor [carry-scale], width factor, depth factor, drift) or None when out of reach."""
    if dist_eff > REACH.get(lie, 0.0) + CLUB_HIGH:
        return None
    best = None
    for name in BAG:
        if lie in ("rough", "sand", "recovery") and name in DECK_LOSS:
            continue
        c, tot, wf, df, drift = cond.club(name, bearing, lie)
        lo, hi = tot - SMOOTH_LOW.get(name, CLUB_LOW), tot + CLUB_HIGH
        if name == "LW":
            lo = MIN_SHOT
        if lo <= dist_eff <= hi:
            gap = abs(tot - dist_eff)
            if best is None or gap < best[0]:
                best = (gap, name, dist_eff / tot, wf, df, drift * dist_eff / max(tot, 1e-9))
    return None if best is None else best[1:]


def plays_like(hole, start, aim, cond=CALM):
    """Horizontal yds and the elevation-adjusted yds (green above the ball -> longer)."""
    d = float(np.hypot(*(np.asarray(aim, float) - np.asarray(start, float))))
    dh = float(hole.elev_ft(np.asarray(aim, float)) - hole.elev_ft(np.asarray(start, float)))
    return d, d + dh * FT / math.tan(math.radians(DESCENT_DEG)) / YD


def evaluate(hole, start, lie, aims, S, z, cond=CALM, start_ev=None, hcp=False):
    """EV (incl. this stroke) of each aim (M x 2) from `start` with common swings z.
    Returns ev (M,), clubs (M,) [None = out of reach -> inf], info list."""
    start = np.asarray(start, float)
    aims = np.atleast_2d(np.asarray(aims, float))
    if start_ev is None:
        start_ev = float(baseline(lie if lie in ("fairway", "rough", "sand", "recovery", "green") else "rough",
                                  np.hypot(*(start - hole.green_c)), hcp))
    ev = np.full(len(aims), np.inf)
    info = [None] * len(aims)
    zl, zd, um, uf = z
    for i, a in enumerate(aims):
        v = a - start
        d = float(np.hypot(*v))
        if d < MIN_SHOT:
            continue
        brg = hole.bearing(start, a)
        _, d_eff = plays_like(hole, start, a, cond)
        # wind carry factor is per club; the elevation is in calm-equivalent yds via the club range check
        c = club_for(d_eff, lie, cond, brg)
        if c is None:
            continue
        name, swing, wf, df, drift = c
        u = v / d
        sl, sd = sigma(d_eff, lie)
        along = d + sd * df * zd
        if d_eff > MISHIT_FROM:
            mis = um < MISHIT_RATE
            lo, hi = MISHIT_RANGE
            along = np.where(mis, d * (lo + (hi - lo) * uf), along)
        lat = sl * wf * zl
        right = _right_of(u)
        fin = start + along[:, None] * u + lat[:, None] * right
        s = S[hole.idx(fin)]
        ob = np.isnan(s)
        s = np.where(ob, 1.0 + start_ev, s)
        ev[i] = 1.0 + float(s.mean())
        info[i] = dict(club=name, swing=round(float(swing), 3), dist=round(d, 1), plays_like=round(d_eff, 1),
                       aim_off_drift=round(-float(drift), 1), p_green=float(np.mean(hole.lie[hole.idx(fin)] == CODE["green"])),
                       p_ob=float(ob.mean()), p_water=float(np.mean(hole.lie[hole.idx(fin)] == CODE["water"])),
                       p_sand=float(np.mean(hole.lie[hole.idx(fin)] == CODE["sand"])))
    return ev, info


def _right_of(u):
    """Golfer's right of direction u in the yard frame (x right of the tee line, y = -along)."""
    # tee line direction is (0, -1) and its right is (+1, 0): rotate u by +90 deg in screen sense.
    return np.array([-u[1], u[0]])


# ------------------------------------------------------------------ DECADE target (the aim chooser)
# Port of spirit_hollow/approach/plan.py (decade_base / side_hazards / decade_box) to the package yard frame,
# with the card numbers, edge modifiers and "lesser of evils" severities taken from mozingo/yardage_book.py
# (the par-3 blue box, yardage_book.par3_plan), and the wind modifier of the wind pages
# (wind_page_template.html windMod: under 5 mph -1, 5-10 0, 10-20 +1, 20-30 +2, 30+ +3 yds on every edge).
DECADE_CAT = {"water": "water", "ob": "ob", "recovery": "trees", "native": "native", "sand": "bunker"}
DECADE_BAND, DECADE_BAND_PENAL = 12.0, 20.0      # yds beyond each edge searched (water / OB further)
DECADE_ROWS, DECADE_ROW_HITS = 11, 2             # rays per side; rays that must hit for a category to count
# Cushion multipliers by lie (lateral, depth) = approach/shots.py LIE_MULT (plan.py: no entry for trees -> 1).
DECADE_LIE_MULT = {k: v for k, v in LIE_MULT.items() if k != "recovery"}


def _yb():
    import yardage_book as yb                    # mozingo/yardage_book.py (DECADE card + modifiers)
    return yb


def decade_base(dist):
    """DECADE baseline yds in from an edge: the card table 60-250 (yardage_book.TARGET), 3 inside 60,
    distance / 20 beyond 250 (plan.py decade_base)."""
    if dist > 250:
        return float(round(dist / 20.0))
    return _yb().baseline_target(max(dist, 60))


def wind_mod(mph):
    """DECADE wind modifier (yds added to every edge), as the wind pages: windMod(mph)."""
    mph = float(mph or 0.0)
    return -1 if mph < 5 else 0 if mph < 10 else 1 if mph < 20 else 2 if mph < 30 else 3


def _ld_frame(hole, start):
    fwd = hole.green_c - np.asarray(start, float)
    fwd = fwd / max(np.hypot(*fwd), 1e-9)
    return fwd, _right_of(fwd)


def _to_ld(hole, xy, fwd, right):
    rel = np.atleast_2d(np.asarray(xy, float)) - hole.green_c
    return np.c_[rel @ right, rel @ fwd]


def _from_ld(hole, ld, fwd, right):
    ld = np.atleast_2d(np.asarray(ld, float))
    return hole.green_c + ld[:, :1] * right + ld[:, 1:2] * fwd


def side_hazards(hole, fwd, right, band=DECADE_BAND_PENAL, band_near=DECADE_BAND):
    """What sits off each edge of the green seen from this direction: left/right/short/long -> DECADE category
    (water, ob, trees, native, bunker, rough). Rays leave the edge from DECADE_ROWS lines across the green; a
    category counts for a side when hit within 12 yds of the edge (20 for water/OB) on >= 2 rays; the worst
    counting category wins (plan.py side_hazards). Also the share of rays hitting each category."""
    yb = _yb()
    g = _to_ld(hole, hole.green, fwd, right)
    path = Path(g)
    lo, hi = g.min(axis=0), g.max(axis=0)
    span = np.arange(-60, 60.01, 0.5)
    ks = np.arange(1.0, band + 0.01, 1.0)
    out = {}
    for side in ("left", "right", "short", "long"):
        ax = 0 if side in ("left", "right") else 1
        other = 1 - ax
        w = hi[other] - lo[other]
        rows = np.linspace(lo[other] + 0.1 * w, hi[other] - 0.1 * w, DECADE_ROWS)
        hits = []
        for r in rows:
            pts = np.zeros((len(span), 2))
            pts[:, ax], pts[:, other] = span, r
            ins = span[path.contains_points(pts)]
            if not len(ins):
                continue
            edge = ins.min() if side in ("left", "short") else ins.max()
            sgn = -1 if side in ("left", "short") else 1
            q = np.zeros((len(ks), 2))
            q[:, ax], q[:, other] = edge + sgn * ks, r
            names = [DECADE_CAT.get(LIES[int(i)], "rough") for i in hole.lie_at(_from_ld(hole, q, fwd, right))]
            hits.append({c for c, k in zip(names, ks) if c in ("water", "ob") or (k <= band_near and c != "rough")})
        share = {c: round(sum(c in h for h in hits) / len(hits), 2)
                 for c in ("water", "ob", "trees", "native", "bunker")} if hits else {}
        cats = [c for c in share if share[c] * len(hits) >= DECADE_ROW_HITS]
        worst = max(cats, key=lambda c: yb.SEVERITY[c]) if cats else "rough"
        out[side] = (worst, {c: v for c, v in share.items() if v})
    return out


def decade_box(hole, start, lie="fairway", wind=0, dist=None, pin=None, step=0.5):
    """The DECADE edge rule (yardage_book.par3_plan) generalised to any approach and green shape (plan.py
    decade_box, unchanged apart from the frame).

    Cushion per side = card number for the distance x the lie's dispersion multiplier, + 3 water/OB,
    + 2 trees/native, + 1 bunker, + the wind modifier (`wind`, yds). The target region is every point of the
    green at least the left/right cushion from the edge sideways and the short/long cushion along the line of
    play (checked at the cushion and half of it, so a kidney's waist counts). If nothing qualifies the lesser
    trouble gives up room 0.5 yd at a time (the worst side keeps its full cushion; equal trouble gives up
    equally, ending in the middle). Aim = the region's centroid; with a known `pin`, the pin if it is inside
    the region, else the region point nearest it."""
    yb = _yb()
    start = np.asarray(start, float)
    fwd, right = _ld_frame(hole, start)
    dist = float(np.hypot(*(hole.green_c - start))) if dist is None else float(dist)
    g = _to_ld(hole, hole.green, fwd, right)
    path = Path(g)
    haz = side_hazards(hole, fwd, right)
    base = decade_base(dist)
    ml, md = DECADE_LIE_MULT.get(lie, (1.0, 1.0))
    mult = {"left": ml, "right": ml, "short": md, "long": md}
    off = {k: max(base * mult[k] + yb.ADD[v[0]] + wind, 0.0) for k, v in haz.items()}
    sev = {k: yb.SEVERITY[v[0]] for k, v in haz.items()}
    lo, hi = g.min(axis=0), g.max(axis=0)
    gx, gy = np.meshgrid(np.arange(lo[0], hi[0] + step, step), np.arange(lo[1], hi[1] + step, step))
    cand = np.c_[gx.ravel(), gy.ravel()]
    cand = cand[path.contains_points(cand)]
    vec = {"left": (-1, 0), "right": (1, 0), "short": (0, -1), "long": (0, 1)}
    ok_side = {}

    def side_ok(side, c):
        if c not in ok_side.setdefault(side, {}):
            v = np.array(vec[side], float)
            ok = np.ones(len(cand), bool)
            for f in (0.5, 1.0):
                ok &= path.contains_points(cand + v * c * f)
            ok_side[side][c] = ok
        return ok_side[side][c]

    cush = {k: round(v / step) * step for k, v in off.items()}
    given = {k: 0.0 for k in cush}
    for _ in range(400):
        m = np.ones(len(cand), bool)
        for side, c in cush.items():
            m &= side_ok(side, c)
        if m.any():
            break
        live = [k for k in cush if cush[k] > 0]
        if not live:
            m = np.ones(len(cand), bool)
            break
        low = min(sev[k] for k in live)
        for k in live:
            if sev[k] == low:
                cush[k] = max(cush[k] - step, 0.0)
                given[k] += step
    region = cand[m]
    lat_c, dep_c = region.mean(axis=0)
    aim_ld = np.array([lat_c, dep_c])
    if pin is not None:
        p = _to_ld(hole, pin, fwd, right)[0]
        aim_ld = region[int(np.argmin(np.hypot(*(region - p).T)))]
    l0, d0 = region.min(axis=0)
    l1, d1 = region.max(axis=0)

    def how(a, b):
        if not given[a] and not given[b]:
            return "fits"
        if given[a] and given[b]:
            return "split"
        return f"{b} keeps" if given[a] else f"{a} keeps"
    return dict(dist=round(dist, 1), lie=lie, wind=wind, base=float(base), haz={k: v[0] for k, v in haz.items()},
                haz_share={k: v[1] for k, v in haz.items()}, off={k: round(v, 1) for k, v in off.items()},
                used=cush, given=given, lat=(round(float(l0), 1), round(float(l1), 1)),
                dep=(round(float(d0), 1), round(float(d1), 1)), how_lat=how("left", "right"),
                how_dep=how("short", "long"), n_cells=int(len(region)),
                aim_ld=(round(float(aim_ld[0]), 1), round(float(aim_ld[1]), 1)),
                aim_xy=_from_ld(hole, aim_ld, fwd, right)[0])


# ------------------------------------------------------------------ lay-ups (out of reach, par 5s)
# DECADE lay-up: to a full-wedge number, on the widest fairway. The full-wedge window is the bag's full
# wedge totals, LW 101 .. PW 141 yds from the green centre. Inside it the spot with the most short grass
# around it (half-width capped at LAYUP_WIDE: past ~15 yds each side the fairway is "wide enough") wins,
# ties going to the shorter wedge in. No fairway in the window -> 60-160 yds, then any short grass >= 20 yds
# closer, then straight at the green as far as the lie allows.
LAYUP_WINDOWS = ((BAG["LW"][0][1] - 1.0, BAG["PW"][0][1]), (60.0, 160.0), (0.0, np.inf))
LAYUP_WIDE = 15.0


def _short_grass_width(hole):
    if "_sg_width" not in hole.__dict__:
        from scipy.ndimage import distance_transform_edt
        sg = np.isin(hole.lie, [CODE["fairway"], CODE["first_cut"]])
        hole._sg_width = distance_transform_edt(sg) * RES
    return hole._sg_width


def layup_target(hole, start, lie, cond=CALM):
    """DECADE lay-up spot from `start` -> (xy, how) or (None, why)."""
    start = np.asarray(start, float)
    dg = float(np.hypot(*(start - hole.green_c)))
    width = _short_grass_width(hole)
    dgc = np.hypot(hole.XX - hole.green_c[0], hole.YY - hole.green_c[1])
    dst = np.hypot(hole.XX - start[0], hole.YY - start[1])
    base = (width > 0) & (dst <= REACH.get(lie, 0.0)) & (dgc <= dg - 20) & (dst >= 30)
    for lo, hi in LAYUP_WINDOWS:
        sel = base & (dgc >= lo) & (dgc <= hi)
        if not sel.any():
            continue
        idx = np.flatnonzero(sel)
        score = np.minimum(width.ravel()[idx], LAYUP_WIDE)
        order = np.lexsort((dgc.ravel()[idx], -np.round(score)))
        for j in order[:200]:
            p = np.array([hole.XX.ravel()[idx[j]], hole.YY.ravel()[idx[j]]])
            _, d_eff = plays_like(hole, start, p, cond)
            if club_for(d_eff, lie, cond, hole.bearing(start, p)) is not None:
                return p, dict(window=[lo, hi], half_width=round(float(width.ravel()[idx[j]]), 1),
                               leaves=round(float(dgc.ravel()[idx[j]]), 1))
    u = (hole.green_c - start) / max(dg, 1e-9)
    d = min(REACH.get(lie, 0.0) - 5, dg - 20)
    if d < MIN_SHOT:
        return None, "no lay-up"
    return start + u * d, dict(window=None, half_width=0.0, leaves=round(dg - d, 1))


def candidate_aims(hole, start, lie, step_green=2.0, ring=8.0):
    """Diagnostic only (solve(opt=True)): the old expected-strokes search grid, green + an 8-yd ring."""
    gx = np.arange(hole.green[:, 0].min() - ring, hole.green[:, 0].max() + ring + 0.1, step_green)
    gy = np.arange(hole.green[:, 1].min() - ring, hole.green[:, 1].max() + ring + 0.1, step_green)
    GX, GY = np.meshgrid(gx, gy, indexing="ij")
    pts = np.c_[GX.ravel(), GY.ravel()]
    inside = hole.green_path.contains_points(pts)
    near = _edge_dist(pts, hole.green) <= ring
    lies = hole.lie_at(pts)
    ok = (inside | near) & ~np.isin(lies, [CODE["water"], CODE["ob"], CODE["recovery"], CODE["native"]])
    return pts[ok]


def solve(hole, start, lie=None, pin=None, cond=CALM, n=400, seed=0, hcp=False, start_ev=None, opt=False, top=None):
    """DECADE club + aim from `start` (yard frame). pin=None -> the box centre (pin-independent; EVs averaged
    over hole.pins()); a known pin -> the pin if inside the box, else the box point nearest it.

    The aim is never chosen by expected strokes. The club is the one whose plays-like total (elevation,
    wind, temperature) is nearest the distance to the aim. EVs are a check: best (the DECADE pick) vs centre
    (same logic aimed at the green centroid) and, with a pin, flag. Lay-ups: when the green is out of reach,
    or on a par 5 when the DECADE lay-up (full wedge, widest fairway) scores better than going.
    opt=True also reports the old EV-optimal aim (green + ring search) as `ev_opt`, for comparison."""
    start = np.asarray(start, float)
    lie = lie or hole.lie_name(start)
    if lie == "green":
        pins = np.atleast_2d(pin) if pin is not None else hole.pins()
        ev = float(np.mean(putts(np.hypot(*(pins - start).T) * 3.0, hcp)))
        return dict(best=dict(club="putter", target=[round(float(x), 1) for x in start], ev=ev, kind="putt"),
                    centre=None, n_aims=0, lie=lie)
    pins = np.atleast_2d(np.asarray(pin, float)) if pin is not None else hole.pins()
    S = value_map(hole, pins, hcp)
    z = z_draws(n, seed)
    box = decade_box(hole, start, lie, wind_mod(cond.wind_mph), pin=pin)

    def run(a, kind):
        a = np.asarray(a, float)
        e, inf = evaluate(hole, start, lie, a[None, :], S, z, cond, start_ev, hcp)
        if not np.isfinite(e[0]):
            return None
        out = dict(kind=kind, target=[round(float(a[0]), 1), round(float(a[1]), 1)], ev=round(float(e[0]), 4),
                   lie_at_target=hole.lie_name(a), **inf[0])
        out.update(_offset(hole, start, a))
        return out

    go = run(box["aim_xy"], "decade")
    res = dict(lie=lie, start=[round(float(x), 1) for x in start], n_aims=1, go=go,
               decade={k: v for k, v in box.items() if k != "aim_xy"})
    lay = None
    if go is None or hole.par >= 5:
        lp, how = layup_target(hole, start, lie, cond)
        if lp is not None:
            lay = run(lp, "layup")
            if lay is not None:
                lay["layup"] = how
    res["layup"] = lay
    if go is None:
        res["best"] = lay
    elif lay is not None and lay["ev"] < go["ev"]:
        res["best"] = lay
    else:
        res["best"] = go
    res["centre"] = run(hole.green_c, "centre")
    if pin is not None:
        res["flag"] = run(pin, "flag")
    if res["best"] and res["centre"]:
        res["ev_check"] = round(res["centre"]["ev"] - res["best"]["ev"], 4)   # + = DECADE beats the centre
    res["top"] = [res["best"]] if res["best"] else []
    if opt:
        aims = candidate_aims(hole, start, lie)
        ev, info = evaluate(hole, start, lie, aims, S, z, cond, start_ev, hcp)
        i = int(np.argmin(ev))
        if np.isfinite(ev[i]):
            o = dict(kind="ev_opt", target=[round(float(aims[i][0]), 1), round(float(aims[i][1]), 1)],
                     ev=round(float(ev[i]), 4), lie_at_target=hole.lie_name(aims[i]), **info[i])
            o.update(_offset(hole, start, aims[i]))
            res["ev_opt"] = o
    return res


def _offset(hole, start, a):
    """Aim point vs the green centre in the shot's frame: + long / + right (yds)."""
    v = hole.green_c - np.asarray(start, float)
    u = v / max(np.hypot(*v), 1e-9)
    d = np.asarray(a, float) - hole.green_c
    return dict(vs_centre_long=round(float(d @ u), 1), vs_centre_right=round(float(d @ _right_of(u)), 1))


# ------------------------------------------------------------------ value of a tee-shot finish
class ValueGrid:
    """V(x, y, lie) = expected strokes to hole out after the tee shot when the approach is played optimally,
    on a coarse grid of start spots (bilinear in between), for the open lies; penalty lies map onto them."""

    def __init__(self, hole, xs, ys, cond=CALM, n=250, hcp=False, tee_ev=None):
        self.hole, self.xs, self.ys = hole, np.asarray(xs, float), np.asarray(ys, float)
        self.tee_ev = tee_ev
        self.V = {}
        for lie in ("fairway", "rough", "sand"):
            g = np.empty((len(xs), len(ys)))
            for i, x in enumerate(xs):
                for j, y in enumerate(ys):
                    p = np.array([x, y])
                    if np.hypot(*(p - hole.green_c)) < 6:
                        g[i, j] = float(baseline("fairway", 6.0, hcp))
                        continue
                    r = solve(hole, p, lie, cond=cond, n=n, hcp=hcp, top=1)
                    g[i, j] = r["best"]["ev"] if r["best"] else np.nan
            if np.isnan(g).any():                       # out of reach everywhere it is NaN: fall back to table
                XX, YY = np.meshgrid(xs, ys, indexing="ij")
                fb = baseline(lie, np.hypot(XX - hole.green_c[0], YY - hole.green_c[1]), hcp)
                g = np.where(np.isnan(g), fb, g)
            self.V[lie] = g
        # Trees: the open-lie solve can't see a blocked line, so keep the tee model's Broadie gap over rough
        # (recovery row minus rough row, x TREE_SEVERITY) on top of the geometric rough value.
        XX, YY = np.meshgrid(xs, ys, indexing="ij")
        d = np.hypot(XX - hole.green_c[0], YY - hole.green_c[1])
        gap = baseline("recovery", d, hcp) - baseline("rough", d, hcp)
        self.V["recovery"] = self.V["rough"] + t.TREE_SEVERITY * gap
        self.hcp = hcp

    def _interp(self, lie, p):
        g = self.V[lie]
        fx = np.clip((p[:, 0] - self.xs[0]) / (self.xs[1] - self.xs[0]), 0, len(self.xs) - 1.000001)
        fy = np.clip((p[:, 1] - self.ys[0]) / (self.ys[1] - self.ys[0]), 0, len(self.ys) - 1.000001)
        i, j = fx.astype(int), fy.astype(int)
        tx, ty = fx - i, fy - j
        i1, j1 = np.minimum(i + 1, len(self.xs) - 1), np.minimum(j + 1, len(self.ys) - 1)
        return (g[i, j] * (1 - tx) * (1 - ty) + g[i1, j] * tx * (1 - ty) + g[i, j1] * (1 - tx) * ty +
                g[i1, j1] * tx * ty)

    def value(self, pts, lies):
        """Expected strokes after the tee shot for finishing spots (N x 2) with tee_strategy lie names."""
        pts = np.asarray(pts, float)
        lies = np.asarray(lies, dtype=object)
        out = np.empty(len(pts))
        for name in set(lies):
            m = lies == name
            p = pts[m]
            if name in ("fairway", "first_cut"):
                v = self._interp("fairway", p)
                if name == "first_cut":
                    v = v + t.FIRST_CUT_COST * (self._interp("rough", p) - v)
            elif name in ("rough", "sand", "recovery"):
                v = self._interp(name, p)
            elif name == "green":
                v = putts(np.hypot(*(p - self.hole.green_c).T) * 3.0, self.hcp)
            elif name == "water":                        # same as tee_strategy: 1 + rough at the spot
                v = 1.0 + self._interp("rough", p)
            elif name == "ob":                           # tee_strategy: 2 + rough (stroke and distance proxy)
                v = 2.0 + self._interp("rough", p)
            elif name == "native":
                v = t.NATIVE_LOST * (2.0 + self._interp("rough", p)) + (1 - t.NATIVE_LOST) * self._interp("recovery", p)
            else:
                v = self._interp("rough", p)
            out[m] = v
        return out


def load_course_module(slug):
    path = os.path.join(PACKAGES, slug, "course_auto.py")
    spec = importlib.util.spec_from_file_location(f"course_auto_{slug}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tee_compare(slug, key, clubs=None, aims=np.arange(-30, 30.1, 5.0), n_tee=1200, grid=8.0, n_app=200,
                cond=CALM, hcp=False, pkg=None, mod=None):
    """Offline: the tee engine's own swings (tee_strategy.simulate, same clubs / aims / lies) scored two ways:
    tee-only (1 + expected_strokes(lie, yds to the green centre), the published objective) and whole-hole
    (1 + V from the approach solver). Returns per (club, aim) both EVs and the two argmins."""
    mod = mod or load_course_module(slug)
    pkg = pkg or load_package(slug)
    hole = Hole.from_package(slug, key, pkg)
    saved = t.HOLES
    t.HOLES = mod.HOLES
    try:
        hd = mod.HOLES[int(key) if str(key).isdigit() else key]
        tee_px = np.array(hd["tee"], float)
        ppy = float(hd["px_per_yd"])
        clubs = clubs or list(t.CLUBS) + list(t.IRONS)
        z = z_draws(n_tee, seed=11)
        sims = {}
        for c in clubs:
            for a in aims:
                pts, lie, tg, s_tee = t.simulate(int(key) if str(key).isdigit() else key, c, float(a), z=z)
                sims[(c, float(a))] = ((pts - tee_px) / ppy, lie, float(s_tee.mean()))
    finally:
        t.HOLES = saved
    allp = np.vstack([v[0] for v in sims.values()])
    lo, hi = np.percentile(allp, 0.5, axis=0) - grid, np.percentile(allp, 99.5, axis=0) + grid
    xs = np.arange(lo[0], hi[0] + grid, grid)
    ys = np.arange(lo[1], hi[1] + grid, grid)
    vg = ValueGrid(hole, xs, ys, cond=cond, n=n_app, hcp=hcp)
    rows = []
    for (c, a), (p, lie, ev_tee) in sims.items():
        ev_whole = 1.0 + float(vg.value(p, lie).mean())
        rows.append(dict(club=c, aim=a, ev_tee=round(ev_tee, 4), ev_whole=round(ev_whole, 4)))
    bt = min(rows, key=lambda r: r["ev_tee"])
    bw = min(rows, key=lambda r: r["ev_whole"])
    # what the tee-only pick costs under the whole-hole objective
    bt_whole = next(r["ev_whole"] for r in rows if r["club"] == bt["club"] and r["aim"] == bt["aim"])
    return dict(hole=str(key), par=hole.par, tee_only=bt, whole_hole=bw,
                same_club=bt["club"] == bw["club"], aim_shift=bw["aim"] - bt["aim"],
                regret_whole=round(bt_whole - bw["ev_whole"], 4), rows=rows)
