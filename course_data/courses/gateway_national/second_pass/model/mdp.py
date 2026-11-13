"""Second-shot rollout (a 2- / 3-stage approximate MDP) used to CHECK the engine's one-shot value table.

The engine scores a tee ball by a table V(lie, distance to the hole): generic strokes gained. That table knows
nothing about THIS hole beyond the tee shot: water beside the green, a green that is shallow from one side, a lay-up
zone pinched by a creek, a par 5 that is / is not reachable. Here the next shot is played explicitly from every
playable cell of the landing area with the engine's own swing model (same mishits, same per-club widths, the club an
ideal one for the distance or the 4-wood off the deck), aimed and clubbed optimally (min expected strokes), and its
finish is scored on the engine's own per-cell strokes (putts on the green, short game by lie, penalties). Cells further
than GO yds from the hole are solved after the nearer ones, on the improved values (backward induction), so a par-5
second shot chooses between going for the green and laying up to the best number.

    S2 = S + interp(V2 - S0)     on fairway / first cut / rough / sand cells; hazards and trees keep the engine's S.

`kappa` scales the second shot's spread; it is calibrated on a featureless hole (calibrate()) so that the rollout
reproduces the table at 150 yds from the fairway: what is left on a real hole is the hole's own geometry.
"""
import numpy as np
from scipy.interpolate import RegularGridInterpolator

CARRY = np.array([60.0, 100.0, 162.0, 185.0, 210.0, 255.0])
W95 = np.array([13.0, 20.6, 32.3, 36.6, 43.1, 53.8])        # engine central 95 % widths (x 70/65) by carry
D95 = np.array([9.0, 12.0, 16.0, 18.0, 20.0, 24.0]) * 1.25
ROLL = np.array([1.0, 2.0, 5.0, 7.0, 10.0, 15.0])
LIE_SPREAD = {"fairway": 1.0, "first_cut": 1.05, "rough": 1.25, "sand": 1.5}
LIE_CARRY = {"fairway": 1.0, "first_cut": 1.0, "rough": 0.96, "sand": 0.93}
LIE_MAXC = {"fairway": 250.0, "first_cut": 250.0, "rough": 225.0, "sand": 190.0}   # longest carry playable from the lie
GO = 235.0
STEP = 5.0


def club(carry):
    return (np.interp(carry, CARRY, ROLL), np.interp(carry, CARRY, W95) / 4.0, np.interp(carry, CARRY, D95) / 4.0)


def swing(P, z, carry, lie, kappa, tf):
    """along-shot carry and lateral miss (yds) of the swings z for a stock carry (array over options)."""
    roll, sl, sc = club(carry)
    k = kappa * LIE_SPREAD[lie]
    z_lat, z_car, u_m, u_f, u_r = [x[:, None] for x in z]
    c0 = carry[None, :] * LIE_CARRY[lie] * tf
    car = c0 + k * sc[None, :] * z_car
    lo, hi = P["mis_slight_carry"]
    slight = u_m < P["mis_slight"]
    heavy = (u_m >= P["mis_slight"]) & (u_m < P["mis_slight"] + P["mis_heavy"])
    car = np.where(slight, c0 * (lo + (hi - lo) * u_f), car)
    lo, hi = P["mis_heavy_carry"]
    car = np.where(heavy, c0 * (lo + (hi - lo) * u_f), car)
    dev = k * sl[None, :] * z_lat * (c0 / np.maximum(carry[None, :], 1.0))
    dev = np.where(slight, dev * P["mis_slight_lat"], dev)
    dev = np.where(heavy, dev * P["mis_heavy_lat"], dev)
    rl = roll[None, :] * (1 + P["roll_noise"] * (2 * u_r - 1))
    return car, dev, rl


def options(d, lie):
    """(stock carry, lateral offset) options from distance d: approach totals around d, lay-ups, lateral aims."""
    tot = [d + x for x in (-15, -10, -5, 0, 5)]
    if d > 200:
        tot += list(np.arange(100.0, d - 35.0, 20.0))
    car = []
    for t in tot:
        c = np.interp(t, CARRY + ROLL, CARRY)               # stock carry whose total is t
        if c > LIE_MAXC[lie]:
            c = LIE_MAXC[lie]
        if c >= 55:
            car.append(float(c))
    car = sorted(set(np.round(car, 1)))
    offs = (-15.0, -10.0, -5.0, 0.0, 5.0, 10.0, 15.0)
    C, O = np.meshgrid(car, offs, indexing="ij")
    return C.ravel(), O.ravel()


def rollout(M, R, Scont, P, z, a0, l0, lie, kappa, tf):
    """min over options of E[1 + Scont(finish)] for a ball at (a0, l0) with lie name `lie`."""
    g = R.green
    d = float(np.hypot(g[0] - a0, g[1] - l0))
    carry, off = options(d, lie)
    u = np.array([g[0] - a0, g[1] - l0]) / max(d, 1e-9)
    v = np.array([-u[1], u[0]])                              # to the right of the shot line (a along, l right)
    car, dev, rl = swing(P, z, carry, lie, kappa, tf)
    lat = dev + off[None, :]
    a, l = a0 + car * u[0] + lat * v[0], l0 + car * u[1] + lat * v[1]
    land = R.lie_at(a, l)
    rr = np.where(M.HAZ[land], 0.0, np.where(land == M.CODE["rough"], rl * P["rough_roll"], rl))
    a, l = a + rr * u[0], l + rr * u[1]
    ev = 1.0 + Scont[R.idx(a, l)].mean(0)
    j = int(np.argmin(ev))
    return float(ev[j]), float(carry[j]), float(off[j]), d


BANDS = (235.0, 300.0, 380.0, 470.0, 1e9)


def big_raster(M, hd):
    """The hole's lie raster out to 700 yds / +-160 (par-5 greens lie beyond the engine's 430-yd raster), untraced
    ground = rough (the engine's 'unverified' half-trees rule is for wide tee balls, not for ground by a green)."""
    keep = (M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH)
    try:
        M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH = 700, -160, 160, 1e9
        Rb = M.Raster(hd)
        Rb._ext = (M.A0, M.L0)
    finally:
        M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH = keep
    A0, L0 = Rb._ext
    na, nl = len(Rb.a), len(Rb.l)

    def idx(a, l):
        ia = np.clip(np.rint((a - A0) / M.RES).astype(np.int32), 0, na - 1)
        il = np.clip(np.rint((l - L0) / M.RES).astype(np.int32), 0, nl - 1)
        return ia, il
    Rb.idx = idx
    Rb.lie_at = lambda a, l: Rb.lie[idx(a, l)]
    return Rb


def flat_raster(M, length=560.0, radius=14.0, half_fw=18.0):
    """A featureless hole in the engine's raster format: a straight fairway +-half_fw, rough elsewhere, a round
    green of `radius` at `length` on the line. No hazards, no trees."""
    keep = (M.A1, M.L0, M.L1)
    try:
        M.A1, M.L0, M.L1 = 700, -160, 160
        a = np.arange(M.A0, M.A1 + M.RES / 2, M.RES)
        l = np.arange(M.L0, M.L1 + M.RES / 2, M.RES)
        A0, L0 = M.A0, M.L0
    finally:
        M.A1, M.L0, M.L1 = keep
    R = object.__new__(M.Raster)
    R.a, R.l = a, l
    R.AA, R.LL = np.meshgrid(a, l, indexing="ij")
    R.green = np.array([length, 0.0])
    R.dist = np.hypot(R.AA - length, R.LL)
    lie = np.zeros(R.AA.shape, np.int8)                                   # rough
    lie[(np.abs(R.LL) <= half_fw) & (R.AA < length + radius + 5)] = M.CODE["fairway"]
    R.lie = lie
    R.native_depth = np.zeros(lie.shape)
    R.entry_dist = R.dist.copy()
    R.blocked = np.zeros(lie.shape, bool)
    th = np.linspace(0, 2 * np.pi, 60)
    R.hd = dict(green_poly=np.column_stack([length + radius * np.cos(th), radius * np.sin(th)]))
    na, nl = len(a), len(l)

    def idx(aa, ll):
        ia = np.clip(np.rint((aa - A0) / M.RES).astype(np.int32), 0, na - 1)
        il = np.clip(np.rint((ll - L0) / M.RES).astype(np.int32), 0, nl - 1)
        return ia, il
    R.idx = idx
    R.lie_at = lambda aa, ll: R.lie[idx(aa, ll)]
    return R


_FLAT = {}


def flat_delta(M, P, kappa, z, tf):
    """{lie: (d grid, rollout - table)} on the featureless hole: what the rollout says about a position that has
    nothing but distance and lie. Subtracted from the real hole's rollout, so only the hole's own geometry is left
    (the table keeps its level and its value of distance)."""
    key = (kappa, round(tf, 5), z.shape[1], P["table"], P["am_off"], P["am_slope"], P["m_rough"], P["m_sand"],
           P["first_cut"], P["mis_slight"], P["mis_heavy"], P["roll_noise"], P["rough_roll"])
    if key in _FLAT:
        return _FLAT[key]
    R = flat_raster(M)
    S0 = R.strokes(dict(P, block_sev=0.0), 560.0)
    ds = np.arange(25.0, 560.0, 5.0)
    out = {}
    for lie in LIE_SPREAD:
        vals = []
        for d in ds:
            v, c, o, _ = rollout(M, R, S0, P, z, 560.0 - d, 0.0, lie, kappa, tf)
            if lie == "first_cut":
                tb = M.table("fairway", d, P) + P["first_cut"] * (M.table("rough", d, P) - M.table("fairway", d, P))
            else:
                tb = M.table(lie, d, P)
            vals.append(v - float(tb))
        out[lie] = (ds, np.array(vals))
    _FLAT[key] = out
    return out


def improved_S(M, h, P, R, kappa, n=300, seed=11, raw=False):
    """Engine S on the engine raster R, and S2 = S + interp(delta), delta = (V2 - S0) on this hole minus the same on
    a featureless hole at the same distance and lie (raw=True: not subtracted). Backward induction in distance bands
    (BANDS): approach cells first, then the cells further out on the improved values."""
    hd = M.HOLES[h]
    S = R.strokes(P, hd["length"])
    Rb = big_raster(M, hd)
    S0 = Rb.strokes(dict(P, block_sev=0.0), hd["length"])
    z = M.draws_z(n, seed)
    tf = 1.0 - P["temp_k"] * (70.0 - P["temp_f"])
    FD = None if raw else flat_delta(M, P, kappa, z, tf)
    ga = np.arange(120.0, min(700.0, Rb.green[0] + 10) + 0.1, STEP)
    gl = np.arange(-160.0, 160.0 + 0.1, STEP)
    names = {M.CODE[k]: k for k in LIE_SPREAD}
    nodes = []
    for i, a0 in enumerate(ga):
        for j, l0 in enumerate(gl):
            code = int(Rb.lie_at(np.array([a0]), np.array([l0]))[0])
            dd = float(np.hypot(Rb.green[0] - a0, Rb.green[1] - l0))
            if code in names and dd > 25:
                nodes.append((dd, i, j, a0, l0, names[code]))
    D1 = np.zeros((len(ga), len(gl)))
    info = {}
    okb = np.isin(Rb.lie, list(names))

    def to_raster(Rx, ok):
        f = RegularGridInterpolator((ga, gl), D1, bounds_error=False, fill_value=0.0)
        dl = f(np.column_stack([Rx.AA.ravel(), Rx.LL.ravel()])).reshape(Rx.AA.shape)
        return np.where(ok, dl, 0.0)

    Scont = S0
    lo = 25.0
    for hi in BANDS:
        band = [x for x in nodes if lo < x[0] <= hi]
        for dd, i, j, a0, l0, lie in band:
            v, c, o, _ = rollout(M, Rb, Scont, P, z, a0, l0, lie, kappa, tf)
            dl = v - S0[Rb.idx(np.array([a0]), np.array([l0]))][0]
            if FD is not None:
                dl -= float(np.interp(dd, FD[lie][0], FD[lie][1]))
            D1[i, j] = dl
            info[(i, j)] = (v, c, o, dd, lie, a0, l0)
        if band:
            Scont = S0 + to_raster(Rb, okb)
        lo = hi
    S2 = S + to_raster(R, np.isin(R.lie, list(names)))
    return S, S2, dict(ga=ga, gl=gl, delta=D1, info=info)


# ---------------------------------------------------------------------------------------------- featureless hole
class Flat:
    """A featureless hole: fairway everywhere short of the green, a round green of radius r, rough around it."""

    def __init__(self, M, vc, P, radius=14.0):
        self.M, self.r = M, radius
        self.green = np.array([0.0, 0.0])
        self.P = P
        self.vc = vc

    def value(self, a, l):
        """strokes to hole out from (a, l) (the hole at the origin): putts on the green, rough short game near it,
        fairway table short of it (a < -radius-5 and |l| < 18), else rough."""
        M, P, vc = self.M, self.P, self.vc
        d = np.hypot(a, l)
        fw = (a < -(self.r + 5)) & (np.abs(l) < 18)
        kind_r = M.table("rough", d, P)
        kind_f = M.table("fairway", d, P)
        s = np.where(fw, kind_f, kind_r)
        near = d < 20
        fwd = np.interp(d, vc.SHORT_YDS, vc.SHORT_TOUR["fairway"]) - vc.SHORT_TOUR["fairway"][-1]
        gap = (np.interp(d, vc.SHORT_YDS, vc.SHORT_TOUR["rough"]) - np.interp(d, vc.SHORT_YDS, vc.SHORT_TOUR["fairway"])
               - (vc.SHORT_TOUR["rough"][-1] - vc.SHORT_TOUR["fairway"][-1]))
        s = np.where(near, s + fwd + np.where(fw, 0.0, P["m_rough"] * gap), s)
        s = np.where(d <= self.r, vc.putts(d, 0.10 if P["table"] == "am" else 0.0), s)
        return s


def flat_value(M, vc, P, d, lie, kappa, n=20000, seed=5, radius=14.0, tf=1.0):
    F = Flat(M, vc, P, radius)
    z = M.draws_z(n, seed)
    carry, off = options(d, lie)
    car, dev, rl = swing(P, z, carry, lie, kappa, tf)
    lat = dev + off[None, :]
    a = -d + car
    land_green = np.hypot(a, lat) <= radius
    land_fw = (a < -(radius + 5)) & (np.abs(lat) < 18)
    rr = np.where(land_green | land_fw, rl, rl * P["rough_roll"])
    ev = 1.0 + F.value(a + rr, lat).mean(0)
    j = int(np.argmin(ev))
    return float(ev[j]), float(carry[j]), float(off[j])
