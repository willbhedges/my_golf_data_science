"""Spirit Hollow tee-shot model, version 2 (raster engine).

Same course map as v1 (spirit_hollow/course.py: audited zones, OSM first cut, Black tees, DEM carry
per club), but a different engine and several model changes, each switchable so v1 can be
reproduced (see V1 below and validate.py):

  * Lie raster: each hole's zones are rasterised once per map draw on a 1-yd grid in the tee frame
    (along the app line, yds right of it). A shot is then an array lookup, so the expected strokes
    for every aim on a 0.5-yd grid come from one gather (common random numbers across aims and
    clubs by construction). Aim is then optimised continuously (Brent on the smoothed curve).
  * Soft course: the ball moves ~1-2 yds after landing (golfer, 2026-10-17). v1 kept the full
    calm-day roll (total - carry, ~25 yds for driver) and only capped the slope factor.
  * Temperature: carry x (1 - k (70 - T)), k ~ 0.0005-0.0009 per F (TrackMan/Rice ~2-2.5 yd per
    10 F for driver; TrackMan secondhand 1.3-1.7; Titleist 1.5% per 20 F).
  * Shot pattern: angular lateral (sigma = width/4) with an unknown common bias; carry depth with
    (a) push-slice / pull-hook correlation rho and (b) two-way curvature carry loss kappa*|offline|
    (centred, so the stated carry stays the mean); slight mishits 5-8% short (heel strikes cost
    12-15 yds on modern drivers in robot tests) with 15% wider lateral; heavy mishits 15-35% short.
  * Penalties by the Rules: ball lost (long grass) or OB = stroke and distance, i.e. 1 + the hole's
    tee value (v1: 2 + rough at the landing distance); water: 1 + rough measured from where the
    ball crossed into the penalty area (the reference point for both red and yellow relief), not
    where it landed. Lost-ball chance grows with depth into the long grass.
  * Trees: a ball in the trees is a punch-out (1 + next shot from ~adv yds further on, + a chance of
    hitting the trees again) with prob. = tree severity, otherwise a restricted shot from rough. A
    ball in the open whose line to the green is blocked by trees 10-60 yds ahead pays part of that.
  * Scoring tables: PGA Tour (Broadie) or a scratch-5 amateur table built from Tour + published
    offsets (research.md: Stagner/Arccos, Shot Scope): fairway + off + slope*(d - 150), rough gap
    x m_rough (amateur rough costs less than tour rough), sand gap x m_sand.
"""
import os
import sys

import numpy as np
from matplotlib.path import Path
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(SH, "..", "mozingo"), SH]

import course                                   # noqa: E402
import tee_strategy as t                        # noqa: E402

LIES = ["rough", "fairway", "first_cut", "sand", "recovery", "native", "water", "ob", "unverified"]
CODE = {k: i for i, k in enumerate(LIES)}
HAZ = np.array([False, False, False, True, True, True, True, True, True])   # ball stops where it lands
OPEN = np.array([True, True, True, True, False, False, False, False, False])  # lies a tree line can block
# The map was hand-checked within +/-55 yds of the line (course.py landing-zone QA). Untraced ground
# beyond that defaults to "rough" in v1; v2 calls it "unverified" and scores it half rough, half
# trees (the photos show both open grass and tree lines / back yards out there).
CHECKED_HALF_WIDTH = 55.0
UNVERIFIED_TREES = 0.5

A0, A1 = -10, 430          # raster: yds along the line
L0, L1 = -150, 150         # raster: yds right of the line
RES = 0.5

# golfer's numbers (carry, total on a normal day, lateral 95% width, carry-depth 95% window)
CLUBS = {
    "Driver": (275, 300, 65, 28),
    "2-wood": (265, 280, 60, 26),
    "4-wood": (255, 270, 50, 24),
    "Long iron": (210, 220, 40, 20),
    "Mid iron": (185, 192, 34, 18),
    "Hybrid ~235 (not in bag)": (235, 248, 45, 22),
}
WOODS = ["Driver", "2-wood", "4-wood"]
HYBRID = "Hybrid ~235 (not in bag)"     # hypothetical gap club (golfer's request): reported, never the pick
HYPOTHETICAL = {HYBRID}
ALL_CLUBS = list(CLUBS)
REAL_CLUBS = [c for c in ALL_CLUBS if c not in HYPOTHETICAL]


def _hybrid_elevation():
    """DEM carry/roll for the hypothetical hybrid: interpolated by carry between 4-wood and long iron."""
    w = (235 - 210) / (255 - 210)
    for hd in course.HOLES.values():
        e = hd.get("elev")
        if e and "4-wood" in e and "Long iron" in e and HYBRID not in e:
            a, b = e["Long iron"], e["4-wood"]
            e[HYBRID] = tuple(float(x + w * (y - x)) for x, y in zip(a, b))


_hybrid_elevation()

# ------------------------------------------------------------------------------- scoring tables
DIST = np.array(t.DIST, float)
TOUR = {k: np.array(v, float) for k, v in t.BASELINE.items()}
TEE_DIST, TEE_BASE = np.array(t.TEE_DIST, float), np.array(t.TEE_BASE, float)
LONG_SLOPE = t.LONG_SLOPE


def _tour(kind, d):
    d = np.asarray(d, float)
    beyond = np.maximum(d - DIST[-1], 0) * LONG_SLOPE
    return np.interp(np.clip(d, DIST[0], DIST[-1]), DIST, TOUR[kind]) + beyond


def tee_value(length, P):
    v = float(np.interp(length, TEE_DIST, TEE_BASE))
    return v + (P["am_tee_off"] if P["table"] == "am" else 0.0)


def table(kind, d, P):
    """Expected strokes to hole out from a lie (fairway / rough / sand) at distance d."""
    fw = _tour("fairway", d)
    if P["table"] == "tour":
        return fw if kind == "fairway" else _tour(kind, d)
    off = P["am_off"] + P["am_slope"] * (np.clip(d, 20, 450) - 150)
    if kind == "fairway":
        return fw + off
    mult = P["m_rough"] if kind == "rough" else P["m_sand"]
    return fw + off + mult * (_tour(kind, d) - fw)


def punch_out(d, P):
    """Ball in the trees, chip out: one stroke, the next from ~adv yds closer (fairway/rough mix),
    plus a chance of a second recovery. v1 used Broadie's tour 'recovery' row instead."""
    if P.get("broadie_recovery"):
        e = _tour("recovery", d)
        if P["table"] == "am":
            fw = _tour("fairway", d)
            e = table("fairway", d, P) + 1.3 * (e - fw)
        return e
    d2 = np.maximum(d - P["punch_adv"], 20.0)
    return 1.0 + 0.5 * (table("fairway", d2, P) + table("rough", d2, P)) + P["punch_fail"]


# ------------------------------------------------------------------------------- the map
def frame(hd):
    """Tee, unit vectors, px per yard. With geom.py's 'scale' correction the yard is a ground yard."""
    tee, fwd, right, ppy = t.hole_frame(hd)
    return np.asarray(tee, float), fwd, right, ppy / hd.get("ground_scale", 1.0)


class Raster:
    """Lie codes on a 1-yd grid in the tee frame, plus the per-cell geometry the scoring needs."""

    def __init__(self, hd, jitter_seed=None, jitter_yds=2.5):
        self.hd = hd
        tee, fwd, right, ppy = frame(hd)
        self.a = np.arange(A0, A1 + RES / 2, RES)
        self.l = np.arange(L0, L1 + RES / 2, RES)
        AA, LL = np.meshgrid(self.a, self.l, indexing="ij")
        pts = tee + (AA.ravel()[:, None] * fwd + LL.ravel()[:, None] * right) * ppy
        lie = np.zeros(len(pts), np.int8)
        rng = np.random.default_rng(jitter_seed) if jitter_seed is not None else None
        for name, poly in hd["zones"]:
            poly = np.asarray(poly, float)
            if rng is not None:
                poly = poly + rng.normal(0, jitter_yds * ppy / 1.414, 2)
            lie[Path(poly).contains_points(pts)] = CODE[name]
        lie = lie.reshape(AA.shape)
        lie[(lie == CODE["rough"]) & (np.abs(LL) > CHECKED_HALF_WIDTH)] = CODE["unverified"]
        self.lie = lie
        g = np.asarray(hd["green"], float) - tee
        self.green = np.array([g @ fwd / ppy, g @ right / ppy])
        self.dist = np.hypot(AA - self.green[0], LL - self.green[1])
        self.AA, self.LL = AA, LL
        # depth into long grass (yds to the nearest non-native cell)
        self.native_depth = ndimage.distance_transform_edt(self.lie == CODE["native"]) * RES
        self._water_entry()
        self._blocked()

    def idx(self, a, l):
        ia = np.clip(np.rint((a - A0) / RES).astype(np.int32), 0, len(self.a) - 1)
        il = np.clip(np.rint((l - L0) / RES).astype(np.int32), 0, len(self.l) - 1)
        return ia, il

    def lie_at(self, a, l):
        return self.lie[self.idx(a, l)]

    def _water_entry(self):
        """For water cells: distance to the green from where the ball crossed into the water,
        walking back along the line from the tee (the relief reference point)."""
        self.entry_dist = self.dist.copy()
        w = np.argwhere(self.lie == CODE["water"])
        if not len(w):
            return
        a, l = self.a[w[:, 0]], self.l[w[:, 1]]
        r = np.hypot(a, l)
        found = np.zeros(len(w), bool)
        ea, el = a.copy(), l.copy()
        for k in np.arange(1, 121, 1.0):
            s = np.maximum(r - k, 0) / np.maximum(r, 1e-9)
            pa, pl = a * s, l * s
            dry = self.lie_at(pa, pl) != CODE["water"]
            new = dry & ~found
            ea[new], el[new] = pa[new], pl[new]
            found |= new
            if found.all():
                break
        self.entry_dist[w[:, 0], w[:, 1]] = np.hypot(ea - self.green[0], el - self.green[1])

    def _blocked(self, near=10.0, far=60.0, step=5.0):
        """True where the straight line to the green meets trees 10-60 yds ahead of the ball."""
        blk = np.zeros(self.lie.shape, bool)
        cand = OPEN[self.lie] & (self.AA > 120)
        ia, il = np.nonzero(cand)
        a, l = self.a[ia], self.l[il]
        d = self.dist[ia, il]
        ua, ul = (self.green[0] - a) / np.maximum(d, 1e-9), (self.green[1] - l) / np.maximum(d, 1e-9)
        hit = np.zeros(len(ia), bool)
        for s in np.arange(near, far + 0.1, step):
            ok = s < d - 25                               # trees by the green: flown over
            pa, pl = a + ua * s, l + ul * s
            inside = (pa >= A0) & (pa <= A1) & (pl >= L0) & (pl <= L1)
            hit |= ok & inside & (self.lie_at(pa, pl) == CODE["recovery"])
        blk[ia[hit], il[hit]] = True
        self.blocked = blk

    def strokes(self, P, length):
        """Expected strokes to hole out after the tee shot, per cell, under parameters P."""
        d, lie = self.dist, self.lie
        fw, ro, sa = table("fairway", d, P), table("rough", d, P), table("sand", d, P)
        S = ro.copy()
        S[lie == CODE["fairway"]] = fw[lie == CODE["fairway"]]
        fc = lie == CODE["first_cut"]
        S[fc] = fw[fc] + P["first_cut"] * (ro[fc] - fw[fc])
        S[lie == CODE["sand"]] = sa[lie == CODE["sand"]]
        rec = punch_out(d, P)
        m = lie == CODE["recovery"]
        if P.get("v1_penalties"):
            S[m] = P["trees"] * rec[m] + (1 - P["trees"]) * ro[m]
        else:
            S[m] = P["trees"] * rec[m] + (1 - P["trees"]) * (ro[m] + P["tree_restricted"])
        if P.get("v1_penalties"):
            sd_cost = 2.0 + ro                                 # v1: 2 + rough at the landing distance
        else:
            sd_cost = 1.0 + tee_value(length, P) + 0 * d       # stroke and distance: replay the tee shot
        m = lie == CODE["native"]
        if P.get("v1_penalties"):
            pl = np.full(m.sum(), P["lost_deep"])
        else:
            depth = self.native_depth[m]
            pl = P["lost_edge"] + (P["lost_deep"] - P["lost_edge"]) * np.clip(depth / P["lost_ramp"], 0, 1)
        S[m] = pl * sd_cost[m] + (1 - pl) * rec[m]
        m = lie == CODE["water"]
        dw = d[m] if P.get("v1_penalties") else self.entry_dist[m]
        S[m] = 1.0 + table("rough", dw, P)
        m = lie == CODE["ob"]
        S[m] = sd_cost[m]
        m = lie == CODE["unverified"]
        u = 0.0 if P.get("v1_penalties") else UNVERIFIED_TREES
        S[m] = (1 - u) * ro[m] + u * (P["trees"] * rec[m] + (1 - P["trees"]) * (ro[m] + P["tree_restricted"]))
        if P.get("block_sev", 0) > 0:
            b = self.blocked
            S[b] = S[b] + P["block_sev"] * np.maximum(rec[b] - S[b], 0)
        return S


# ------------------------------------------------------------------------------- shots
def draws_z(n, seed):
    """Common random numbers: rows = z_lat, z_car, u_mishit, u_frac, u_roll."""
    r = np.random.default_rng(seed)
    return np.vstack([r.standard_normal((2, n)), r.random((3, n))])


def club_numbers(hd, club, P):
    """(mean carry, roll on fairway, lateral sigma, carry sigma) for this club, hole and draw."""
    carry, total, width, depth = CLUBS[club]
    carry = carry + P["c_common"] + P["c_club"].get(club, 0.0)
    roll_nominal = total - CLUBS[club][0]
    dc, rf = 0.0, 1.0
    if "elev" in hd and club in hd["elev"]:
        dc, rf = hd["elev"][club][0], hd["elev"][club][1]
    carry = carry + dc
    carry = carry * (1.0 - P["temp_k"] * (70.0 - P["temp_f"]))
    if P.get("soft_roll") is not None:
        roll = P["soft_roll"] * rf
    else:
        roll = roll_nominal * rf * P["roll_mult"]
    sig_lat = P["width"][club] / 4.0
    sig_car = depth * P["depth_mult"] / 4.0
    return carry, roll, sig_lat, sig_car


def shots(hd, club, P, z, wind=None):
    """Landing (along, lateral-at-aim-0) and roll per swing. wind = (carry, total, width, depth,
    drift) override from wind.adjust, applied on top of the calm numbers."""
    carry, roll, sig_lat, sig_car = club_numbers(hd, club, P)
    drift = 0.0
    if wind is not None:
        carry, roll, sig_lat, sig_car, drift = wind(carry, roll, sig_lat, sig_car)
    z_lat, z_car, u_m, u_f, u_r = z
    dev = sig_lat * z_lat
    rho = P["rho"]
    car = carry + sig_car * (np.sqrt(1 - rho ** 2) * z_car - rho * z_lat)
    if P["kappa"]:
        car = car - P["kappa"] * sig_lat * (np.abs(z_lat) - np.sqrt(2 / np.pi))
    if P.get("skew"):                      # one-way miss: one side's tail stretched (+ = right)
        s = P["skew"]
        dev = np.where(np.sign(z_lat) == np.sign(s), dev * (1 + abs(s)), dev * (1 - abs(s) / 2))
    slight = u_m < P["mis_slight"]
    heavy = (u_m >= P["mis_slight"]) & (u_m < P["mis_slight"] + P["mis_heavy"])
    lo, hi = P["mis_slight_carry"]
    car = np.where(slight, carry * (lo + (hi - lo) * u_f), car)
    lo, hi = P["mis_heavy_carry"]
    car = np.where(heavy, carry * (lo + (hi - lo) * u_f), car)
    dev = np.where(slight, dev * P["mis_slight_lat"], dev)
    dev = np.where(heavy, dev * P["mis_heavy_lat"], dev)
    dev = dev + P["bias"] + drift
    rl = roll * (1 + P["roll_noise"] * (2 * u_r - 1))
    return car, dev, np.maximum(rl, 0.0)


def finish(R, car, lat, roll, rough_roll, v1_roll=False):
    """Roll each ball out along its flight line (2-yd steps, slower once in rough, stops in hazards).
    car / lat / roll broadcast to a common shape (e.g. swings x aims). Returns final (a, l, lie)."""
    a = np.broadcast_to(car, np.broadcast(car, lat).shape).astype(float).copy()
    l = np.broadcast_to(lat, a.shape).astype(float).copy()
    lie = R.lie_at(a, l)
    left = np.broadcast_to(roll, a.shape).astype(float).copy()
    left = np.where(lie == CODE["rough"], left * rough_roll, left)
    left = np.where(HAZ[lie], 0.0, left)
    norm = np.hypot(a, l)
    ua, ul = a / np.maximum(norm, 1e-9), l / np.maximum(norm, 1e-9)
    while True:
        mv = left > 1e-9
        if not mv.any():
            break
        st = np.minimum(left, 2.0) * mv
        a, l = a + ua * st, l + ul * st
        left = left - st
        new = R.lie_at(a, l)
        was_fw = (lie == CODE["fairway"]) if v1_roll else ((lie == CODE["fairway"]) | (lie == CODE["first_cut"]))
        into_rough = mv & (new == CODE["rough"]) & was_fw
        left = np.where(into_rough, left * rough_roll, left)
        left = np.where(HAZ[new], 0.0, left)
        lie = np.where(mv, new, lie)
    return a, l, lie


def ev_curve(R, S, hd, club, P, z, aims, wind=None):
    """Expected strokes (incl. the tee shot) at each aim, common swings z. Returns (ev, shots)."""
    car, dev, roll = shots(hd, club, P, z, wind)
    a, l, lie = finish(R, car[:, None], dev[:, None] + aims[None, :], roll[:, None], P["rough_roll"],
                       P.get("v1_roll", False))
    s = S[R.idx(a, l)]
    return 1.0 + s.mean(0), (a, l, lie, s)


def outcome_shares(R, lie, a, l):
    out = {k: float(np.mean(lie == CODE[k])) for k in LIES}
    out["blocked"] = float(np.mean(R.blocked[R.idx(a, l)] & OPEN[lie]))
    return out


# ------------------------------------------------------------------------------- parameters
def central(**over):
    """v2 central world (prior means / medians)."""
    w = 70.0 / 65.0
    P = dict(
        table="am", am_off=0.36, am_slope=0.0012, am_tee_off=0.40, m_rough=0.75, m_sand=1.1,
        first_cut=0.35, trees=0.8, tree_restricted=0.10, punch_adv=35.0, punch_fail=0.10,
        lost_edge=0.25, lost_deep=0.65, lost_ramp=10.0, block_sev=0.4,
        c_common=0.0, c_club={}, temp_f=48.0, temp_k=0.00075,
        soft_roll=2.0, roll_mult=1.0, roll_noise=0.5, rough_roll=0.3,
        width={c: CLUBS[c][2] * w for c in CLUBS}, depth_mult=1.25,
        rho=0.1, kappa=0.08, bias=0.0, skew=0.0,
        mis_slight=0.12, mis_slight_carry=(0.92, 0.95), mis_slight_lat=1.15,
        mis_heavy=0.025, mis_heavy_carry=(0.65, 0.85), mis_heavy_lat=1.5,
    )
    P.update(over)
    return P


def v1_world(**over):
    """v1's central world (wind_grid.set_prior_means + final_decision): tour table, full roll,
    15% slight mishits 92-97%, lost ball = 2 + rough, water at the landing distance, Broadie
    recovery row, no temperature, no line-of-sight, irons only on 11 and 13."""
    w = 70.0 / 65.0
    P = central(table="tour", broadie_recovery=True, v1_penalties=True, v1_roll=True, trees=0.8, lost_deep=0.5,
                block_sev=0.0, temp_k=0.0, soft_roll=None, roll_mult=1.0, roll_noise=0.0,
                width={c: CLUBS[c][2] * w for c in CLUBS}, rho=0.0, kappa=0.0,
                mis_slight=0.15, mis_slight_carry=(0.92, 0.97), mis_slight_lat=1.0, mis_heavy=0.0,
                first_cut=t.FIRST_CUT_COST, tree_restricted=0.0)
    P.update(over)
    return P


def clubs_for(h, P=None, all_clubs=True):
    if all_clubs:
        return list(ALL_CLUBS)
    return WOODS + (["Long iron", "Mid iron"] if course.HOLES[h].get("irons") else [])


HOLES = course.HOLES

# ------------------------------------------------------------------------------- temperature
# Carry x (1 - k (70 - T)). k = 0.00075 per F (prior 0.0005-0.0009): ~2.1 yds per 10 F on a 275 driver
# carry, ~1.6 on a 210 iron. Published: Andrew Rice/TrackMan 2-2.5 yds per 10 F (driver, 155 mph ball
# speed; air density), TrackMan as reported 1.3-1.7 by club, Titleist ~1.5% per 20 F. Reference 70 F:
# the golfer's carries are summer numbers. Each hole uses the forecast for when you reach it.
import json as _json                              # noqa: E402

_FC = os.path.join(SH, "..", "course_data", "weather", "forecast_spirit_hollow.json")
FORECAST = _json.load(open(_FC))["hourly"] if os.path.exists(_FC) else []
TEE_DAY, TEE_HOUR, MIN_PER_HOLE = "2026-10-17", 10.0, 14.0


def hole_number(h):
    return int(str(h).rstrip("FB"))


def hole_temp(h, day=TEE_DAY, tee_hour=TEE_HOUR):
    """Forecast temperature (F) when you reach hole h: tee time + 14 min per hole, linear in time."""
    rows = sorted((r["hour"], r["temp_f"]) for r in FORECAST if r["date"] == day)
    if not rows:
        return 48.0
    t = tee_hour + (hole_number(h) - 1) * MIN_PER_HOLE / 60
    hrs, temps = zip(*rows)
    return float(np.interp(t, hrs, temps))
