"""Independent reference ball-flight model for the Gateway National second pass (PHYSICS.md).

3-D point-mass golf ball with drag and lift, spin decay, real-air density / viscosity, a logarithmic wind profile,
landing on ground above / below the tee, and a Haake / Penner bounce-and-roll model. Pure Python (math only), ~2 ms a
flight. Nothing here is imported by the engine; it is a yardstick to compare the engine's rules against.

Axes: x down the target line, y LEFT of it, z up (right-handed). Results report `right` = -y (the engine's sign).

Aerodynamics (three interchangeable coefficient sets, so the spread between them is a measure of model error):
  "fit"    Cd = cd0 + cd1 (1 - exp(-S / sd)),  Cl = cl1 (1 - exp(-S / sl)),  S = r omega / V_air.
           Fitted in fit_aero.py to the TrackMan PGA Tour + LPGA Tour average tables (23 clubs: ball speed, launch,
           spin -> carry, apex height, landing angle; rms 2.8 yds / 1.7 yds / 4.1 deg). Both coefficients rise with
           spin ratio and saturate (Bearman & Harvey 1976; Smits & Smith 1994); no Reynolds-number dependence
           (Bearman & Harvey: Cd of a dimpled ball is flat above the critical Re ~ 6e4, where all of these flights
           are). Not fitted to it, but it reproduces Titleist's altitude rule (carry +1.16 % per 1000 ft, i.e. a
           density elasticity of ~0.40 for a driver): this model 0.39.
  "fit_re" the same with a Reynolds term, Cd += cd2 (1e5 / Re): fits the tables a little better (2.4 yds / 2.1 yds /
           2.6 deg: steeper iron landings) but the Tour tables cannot tell speed from Reynolds number, and it
           predicts almost NO carry change with air density (elasticity 0.07 for a driver), which the altitude rule
           and every temperature test contradict. Kept only as the low end of the sensitivity bracket.
  "smits"  Smits & Smith 1994 (Science and Golf II, 340-347), as published: Cd = 0.24 + 0.18 S + 0.06 sin(pi (Re -
           9e4) / 2e5), Cl = 0.54 S^0.4. (A 1990s ball: more drag than a modern ball; Will's clubs are re-calibrated
           to his carries, so it still gives a second opinion on the SENSITIVITIES.)
  "linear" the repo's elevation/adjust.py set: Cd = 0.137 + 0.860 S, Cl = 0.0469 + 1.114 S (fitted there to the three
           Tour woods).
Spin decay: d omega / dt = -c omega V / r, c = 2.0e-5 (Smits & Smith; ~4 % per second at 60 m/s, as TrackMan quotes).
"""
import math

G = 9.80665
MASS, RAD = 0.04593, 0.021335
AREA = math.pi * RAD * RAD
YD, FT, MPH = 0.9144, 0.3048, 0.44704
SPIN_C = 2.0e-5

# ---------------------------------------------------------------------------------------------------------- air


def air(temp_f=70.0, alt_ft=410.0, rh=0.5, slp_hpa=1013.25):
    """(density kg/m3, kinematic viscosity m2/s) for a temperature, site altitude, relative humidity and sea-level
    pressure (station pressure by the standard barometric formula)."""
    T = (temp_f - 32.0) / 1.8 + 273.15
    p = slp_hpa * 100.0 * (1.0 - 2.25577e-5 * alt_ft * FT) ** 5.25588
    es = 610.94 * math.exp(17.625 * (T - 273.15) / (T - 30.11))        # Magnus, Pa
    pv = rh * es
    rho = (p - pv) / (287.058 * T) + pv / (461.495 * T)
    mu = 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)
    return rho, mu / rho


# ---------------------------------------------------------------------------------------------------------- aero
FIT = dict(cd0=0.1365, cd1=0.2830, sd=0.2193, cl1=0.4160, sl=0.1874)            # fit_aero.py (aero_fit.json wins)
FIT_RE = dict(cd0=0.0396, cd1=0.2059, sd=0.1359, cl1=0.3918, sl=0.1740, cd2=0.1204)
_FITFILE = __file__.replace("refmodel.py", "aero_fit.json")
try:
    import json as _json
    _d = _json.load(open(_FITFILE))
    FIT.update(_d["params"])
    FIT_RE.update(_d.get("params_re", {}))
except Exception:                                    # noqa: BLE001
    pass


def coeff(model, Re, S):
    if model == "fit":
        p = FIT
        return p["cd0"] + p["cd1"] * (1.0 - math.exp(-S / p["sd"])), p["cl1"] * (1.0 - math.exp(-S / p["sl"]))
    if model == "fit_re":
        p = FIT_RE
        return (p["cd0"] + p["cd1"] * (1.0 - math.exp(-S / p["sd"])) + p["cd2"] * (1e5 / Re),
                p["cl1"] * (1.0 - math.exp(-S / p["sl"])))
    if model == "smits":
        return 0.24 + 0.18 * S + 0.06 * math.sin(math.pi * (Re - 9e4) / 2e5), min(0.54 * S ** 0.4, 0.45)
    if model == "linear":
        return 0.137 + 0.860 * S, 0.0469 + 1.114 * S
    raise KeyError(model)


# ---------------------------------------------------------------------------------------------------------- wind
def wind_profile(z, z0=0.03, zref=10.0, zmin=0.2):
    """Neutral log law: u(z) / u(10 m). z0 = 0.03 m: open flat terrain, mown grass, few isolated obstacles (WMO /
    Davenport class 'open'); 0.1 m: 'roughly open' (scattered trees, a links-style flood-plain course with tree lines).
    Below zmin (grass / displacement) the speed is held."""
    return math.log(max(z, zmin) / z0) / math.log(zref / z0)


class Wind:
    """Mean wind at 10 m: head (mph, + into the face), cross (mph, + blowing FROM the right, i.e. pushes left),
    as spirit_hollow/wind.components. profile=False -> uniform with height (the 'rule of thumb' wind)."""

    def __init__(self, head=0.0, cross=0.0, profile=True, z0=0.03):
        self.wx, self.wy = -head * MPH, cross * MPH
        self.profile, self.z0 = profile, z0

    def at(self, z):
        f = wind_profile(z, self.z0) if self.profile else 1.0
        return self.wx * f, self.wy * f


CALM = Wind()


# ---------------------------------------------------------------------------------------------------------- flight
def fly(v_mph, launch_deg, spin_rpm, axis_deg=0.0, az_deg=0.0, rho=1.2, nu=1.5e-5, wind=CALM, drop_ft=0.0,
        model="fit", dt=0.01, path=False):
    """One flight. axis_deg: spin-axis tilt (+ = fade / curves right). az_deg: start direction (+ = right).
    drop_ft: landing ground below (+) / above (-) the tee. Returns dict(carry yds along x, right yds, time s, apex yds,
    land_deg (below horizontal), v_land mph, vx, vz (m/s at landing), spin_land rpm, [path])."""
    v0 = v_mph * MPH
    la, az, ax_ = math.radians(launch_deg), math.radians(az_deg), math.radians(axis_deg)
    vx, vy, vz = v0 * math.cos(la) * math.cos(az), -v0 * math.cos(la) * math.sin(az), v0 * math.sin(la)
    # spin axis: backspin = -y; tilt about x so the lift leans right (-y) for axis_deg > 0; fixed in space
    sx, sy, sz = 0.0, -math.cos(ax_), -math.sin(ax_)
    if az:
        ca, sa = math.cos(-az), math.sin(-az)       # rotate about z with the start line (y left => right = -az)
        sx, sy = ca * sx - sa * sy, sa * sx + ca * sy
    om = spin_rpm * 2 * math.pi / 60.0
    x = y = z = t = 0.0
    k = 0.5 * rho * AREA / MASS
    zg = -drop_ft * FT
    apex = 0.0
    pts = []

    def acc(z_, vx_, vy_, vz_, om_):
        wx, wy = wind.at(z_)
        ux, uy, uz = vx_ - wx, vy_ - wy, vz_
        U = math.sqrt(ux * ux + uy * uy + uz * uz)
        S = RAD * om_ / U
        cd, cl = coeff(model, U * 2 * RAD / nu, S)
        # lift along s x u, normalised (s is a unit vector; |s x u| = U sin(angle) ~ U)
        lx, ly, lz = sy * uz - sz * uy, sz * ux - sx * uz, sx * uy - sy * ux
        ln = math.sqrt(lx * lx + ly * ly + lz * lz) or 1.0
        q = k * U
        return (-q * cd * ux + q * U * cl * lx / ln, -q * cd * uy + q * U * cl * ly / ln,
                -q * cd * uz + q * U * cl * lz / ln - G, -SPIN_C * om_ * U / RAD)

    while True:
        a1 = acc(z, vx, vy, vz, om)
        hx, hy, hz, ho = vx + 0.5 * dt * a1[0], vy + 0.5 * dt * a1[1], vz + 0.5 * dt * a1[2], om + 0.5 * dt * a1[3]
        a2 = acc(z + 0.5 * dt * vz, hx, hy, hz, ho)
        nx, ny, nz = x + dt * hx, y + dt * hy, z + dt * hz
        nvx, nvy, nvz, nom = vx + dt * a2[0], vy + dt * a2[1], vz + dt * a2[2], om + dt * a2[3]
        if nz > apex:
            apex = nz
        if nvz < 0 and nz <= zg:
            f = (z - zg) / (z - nz) if z != nz else 1.0
            x, y, z, t = x + f * (nx - x), y + f * (ny - y), zg, t + f * dt
            vx, vy, vz, om = vx + f * (nvx - vx), vy + f * (nvy - vy), vz + f * (nvz - vz), om + f * (nom - om)
            break
        x, y, z, vx, vy, vz, om = nx, ny, nz, nvx, nvy, nvz, nom
        t += dt
        if path:
            pts.append((t, x / YD, -y / YD, z / YD))
        if t > 20:
            break
    vh = math.hypot(vx, vy)
    out = dict(carry=x / YD, right=-y / YD, time=t, apex=apex / YD, land_deg=math.degrees(math.atan2(-vz, vh)),
               v_land=math.sqrt(vh * vh + vz * vz) / MPH, vh=vh, vz=vz, spin_land=om * 60 / (2 * math.pi))
    if path:
        out["path"] = pts
    return out


def solve_speed(carry, launch_deg, spin_rpm, rho, nu, model="fit", lo=60.0, hi=200.0):
    """Ball speed (mph) that carries `carry` yds on level ground in calm air of (rho, nu)."""
    for _ in range(34):
        mid = 0.5 * (lo + hi)
        if fly(mid, launch_deg, spin_rpm, rho=rho, nu=nu, model=model)["carry"] < carry:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------------------------------------- bounce / roll
# Penner, "The run of a golf ball", Can. J. Phys. 80 (2002) 931-940, after Haake (1989, 1991): the ball digs a
# shallow crater, so it rebounds from a surface tilted back toward it by theta_c = 15.4 deg x (v / 18.6 m/s) x
# (theta / 44.4 deg) (theta = impact angle from the horizontal); in that frame a rigid-body bounce with normal
# restitution e(v_n) = 0.510 - 0.0375 v_n + 0.000903 v_n^2 (0.120 above 20 m/s) and Coulomb friction mu = 0.40 that
# either slides throughout or grips (then v_t' = (5 v_t - 2 r omega) / 7, omega = backspin). Bounces repeat until the
# hop is under ~1 cm; then the ball rolls with deceleration a_roll (stimpmeter relation a = 1.83^2 / (2 stimp)).
# Turf enters three ways: `firm` scales the crater tilt (firm ground: shallower crater; soft: deeper), `e_scale` the
# rebound, `a_roll` the rolling resistance. The engine does not compute roll: it takes Will's stated totals. Here the
# 'normal' fairway is CALIBRATED so the driver runs Will's 25 yds at 70 F; everything else is then a prediction.
TURF = {
    # fairway: tilt scale, restitution scale, rolling deceleration (m/s2), friction
    "fairway_normal": dict(firm=1.00, e_scale=1.0, a_roll=1.25, mu=0.40),      # tilt re-calibrated in compare.py
    "fairway_firm": dict(firm=0.80, e_scale=1.1, a_roll=1.00, mu=0.40),        # dry, dormant, tight
    "fairway_soft": dict(firm=1.30, e_scale=0.85, a_roll=1.70, mu=0.40),       # damp / dew / thawed
    # greens: stimp ~9.5 ft -> a = 1.83^2 / (2 x 2.9) = 0.58
    "green_normal": dict(firm=1.00, e_scale=1.0, a_roll=0.58, mu=0.40),
    "green_firm": dict(firm=0.80, e_scale=1.1, a_roll=0.55, mu=0.40),
    "green_soft": dict(firm=1.30, e_scale=0.85, a_roll=0.65, mu=0.40),
}


def restitution(vn):
    return 0.120 if vn > 20.0 else 0.510 - 0.0375 * vn + 0.000903 * vn * vn


def run_out(vh, vz, spin_rpm, turf, slope_pct=0.0, detail=False):
    """Bounce + roll distance (yds) after landing with horizontal speed vh, vertical vz (< 0), backspin spin_rpm.
    slope_pct: along-line grade of the landing ground (+ = uphill)."""
    T = TURF[turf] if isinstance(turf, str) else turf
    om = spin_rpm * 2 * math.pi / 60.0          # backspin +
    x = 0.0
    alpha = math.atan(slope_pct / 100.0)
    nb = 0
    first = None
    for _ in range(12):
        v = math.hypot(vh, vz)
        th = math.atan2(-vz, vh) + alpha          # impact angle to the surface
        if th <= 0:
            break
        thc = math.radians(15.4) * (v / 18.6) * (math.degrees(th) / 44.4) * T["firm"]
        thc = min(thc, math.radians(60.0))
        a = th + thc                              # angle to the tilted surface
        vt, vn = v * math.cos(a), v * math.sin(a)
        e = min(restitution(vn) * T["e_scale"], 0.9)
        mu_c = 2.0 * (vt + RAD * om) / (7.0 * (1 + e) * vn)
        if T["mu"] < mu_c:                        # slides throughout
            vt2 = vt - T["mu"] * vn * (1 + e)
            om2 = om - 5.0 * T["mu"] * vn * (1 + e) / (2.0 * RAD)
        else:                                     # grips: leaves rolling
            vt2 = (5.0 * vt - 2.0 * RAD * om) / 7.0
            om2 = -vt2 / RAD
        vn2 = e * vn
        # back to the true surface frame (tilted surface leans back toward the ball by thc), then to the horizontal
        vs = vt2 * math.cos(thc) - vn2 * math.sin(thc)
        vp = vt2 * math.sin(thc) + vn2 * math.cos(thc)
        vh, vz = vs * math.cos(alpha) - vp * math.sin(alpha), vs * math.sin(alpha) + vp * math.cos(alpha)
        om = om2
        nb += 1
        if first is None:
            first = dict(thc=math.degrees(thc), e=e, vh=vh, vz=vz, grip=T["mu"] >= mu_c)
        if vz <= 0.45:                            # hop under ~1 cm: rolling from here
            break
        tf = 2 * vz / G                           # flight of the hop (no air; level ground approx.)
        x += vh * tf
        vz = -vz
    # roll: v^2 / (2 (a_roll + g sin(alpha))); a ball still carrying backspin checks first (om > 0 with vh > 0)
    if vh > 0:
        # sliding phase until rolling: v_roll = (5 v - 2 r om) / 7 (same as the grip result), negligible distance
        vr = (5.0 * vh - 2.0 * RAD * om) / 7.0 if abs(vh + RAD * om) > 1e-6 and om != -vh / RAD else vh
        dec = T["a_roll"] + G * math.sin(alpha)
        if dec > 0.05:
            x += math.copysign(vr * vr / (2 * dec), vr)
    else:
        dec = T["a_roll"] - G * math.sin(alpha)
        x -= vh * vh / (2 * max(dec, 0.05))
    if detail:
        return x / YD, dict(bounces=nb, first=first)
    return x / YD
