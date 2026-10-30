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


def candidate_aims(hole, start, lie, step_green=2.0, ring=8.0, layup_step=6.0):
    """Aim points: a grid on the green and a ring around it (bail-outs), plus lay-up spots on fairway / first
    cut within reach when the green is far."""
    gx = np.arange(hole.green[:, 0].min() - ring, hole.green[:, 0].max() + ring + 0.1, step_green)
    gy = np.arange(hole.green[:, 1].min() - ring, hole.green[:, 1].max() + ring + 0.1, step_green)
    GX, GY = np.meshgrid(gx, gy, indexing="ij")
    pts = np.c_[GX.ravel(), GY.ravel()]
    inside = hole.green_path.contains_points(pts)
    near = _edge_dist(pts, hole.green) <= ring
    lies = hole.lie_at(pts)
    ok = (inside | near) & ~np.isin(lies, [CODE["water"], CODE["ob"], CODE["recovery"], CODE["native"]])
    aims = [pts[ok]]
    dg = float(np.hypot(*(np.asarray(start, float) - hole.green_c)))
    if dg > min(REACH.get(lie, 0) - 15, 200) or hole.par >= 5:
        lx = hole.x[::int(layup_step / RES)]
        ly = hole.y[::int(layup_step / RES)]
        LX, LY = np.meshgrid(lx, ly, indexing="ij")
        lp = np.c_[LX.ravel(), LY.ravel()]
        ll = hole.lie_at(lp)
        dist = np.hypot(*(lp - np.asarray(start, float)).T)
        closer = np.hypot(*(lp - hole.green_c).T) < dg - 20
        sel = np.isin(ll, [CODE["fairway"], CODE["first_cut"]]) & (dist <= REACH.get(lie, 0) + CLUB_HIGH) & closer
        aims.append(lp[sel])
    return np.vstack(aims)


def solve(hole, start, lie=None, pin=None, cond=CALM, n=400, seed=0, hcp=False, start_ev=None, top=5):
    """Best club + aim from `start` (yard frame). pin=None -> pin-averaged over hole.pins().
    Returns dict(best, centre, flag (if pin given), top, n_aims)."""
    start = np.asarray(start, float)
    lie = lie or hole.lie_name(start)
    if lie == "green":
        pins = np.atleast_2d(pin) if pin is not None else hole.pins()
        ev = float(np.mean(putts(np.hypot(*(pins - start).T) * 3.0, hcp)))
        return dict(best=dict(club="putter", target=[round(float(x), 1) for x in start], ev=ev), centre=None,
                    top=[], n_aims=0, lie=lie)
    pins = np.atleast_2d(np.asarray(pin, float)) if pin is not None else hole.pins()
    S = value_map(hole, pins, hcp)
    z = z_draws(n, seed)
    aims = candidate_aims(hole, start, lie)
    ev, info = evaluate(hole, start, lie, aims, S, z, cond, start_ev, hcp)
    order = np.argsort(ev)

    def pack(i, a=None, e=None, inf=None):
        a = aims[i] if a is None else a
        e = ev[i] if e is None else e
        inf = info[i] if inf is None else inf
        if not np.isfinite(e):
            return None
        out = dict(target=[round(float(a[0]), 1), round(float(a[1]), 1)], ev=round(float(e), 4),
                   lie_at_target=hole.lie_name(a), **(inf or {}))
        out.update(_offset(hole, start, a))
        return out

    res = dict(lie=lie, start=[round(float(x), 1) for x in start], n_aims=int(len(aims)),
               best=pack(order[0]) if np.isfinite(ev[order[0]]) else None,
               top=[pack(i) for i in order[:top] if np.isfinite(ev[i])])
    # reference aims: the green centroid (and the flag), same swings
    refs = {"centre": hole.green_c}
    if pin is not None:
        refs["flag"] = np.asarray(pin, float)
    for k, a in refs.items():
        e, inf = evaluate(hole, start, lie, a[None, :], S, z, cond, start_ev, hcp)
        res[k] = pack(0, a, e[0], inf[0])
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
        for lie in ("fairway", "rough", "sand", "recovery"):
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
