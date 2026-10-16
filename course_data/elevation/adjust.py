"""Elevation adjustments for the tee-shot strategy model (mozingo/tee_strategy.py club tuples).

    from course_data.elevation.adjust import adjustments
    adjustments("2F")  ->  {"clubs": {"Driver": {"carry_delta_yds": ..., "roll_factor": ...,
                                                  "lateral_kick_yds": ..., ...}, ...},
                            "extra_roll_yds": ..., "landing_drop_ft": ..., ...}

Inputs come from spirit_hollow_holes.json (holes_elevation.py on the USGS 3DEP 1 m DEM): the +-10 yd
lateral-mean profile along the tee line, and the least-squares plane of the 240-320 yd landing box.

1. Carry -- fly the ball onto the terrain
   A 2-D point-mass trajectory with drag and Magnus lift, spin decaying exponentially, is integrated
   until it comes down through the actual ground profile (not the tee height). The carry delta is the
   along-line distance of that intersection minus the flat-ground carry.
   * Aerodynamics: Cd = CD0 + CD1*S, Cl = CL0 + CL1*S (S = spin ratio r*omega/v), spin decay time TAU.
     Linear-in-spin-ratio forms as in Bearman & Harvey (1976, Aeronautical Quarterly 27:112) and Smits &
     Smith (1994, Science and Golf II); the 5 coefficients were fitted here to the TrackMan PGA Tour
     averages (driver 167 mph / 10.9 deg / 2686 rpm -> carry 275, apex 32 yd, land angle 38 deg;
     3-wood 158/9.2/3655 -> 243, 30, 43 deg; 5-wood 152/9.4/4350 -> 230, 31, 47 deg; TrackMan
     "PGA Tour Averages" sheet, https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf).
     The fit reproduces the driver exactly and the fairway woods within ~3 yd and ~2 deg.
   * Each model club keeps its TrackMan-like launch angle / spin; ball speed is solved so the flat carry
     equals the model's carry (e.g. Driver 275).
   * Why not a fixed "yards per foot" rule: published rules disagree (1 yd per 10 ft calculators,
     "10 yds per 30 ft", Golf Digest's TrackMan-based "1-to-1" i.e. 1 yd per yd = 3 ft). The geometry
     says dCarry ~= dh / tan(descent angle): at the driver's 38 deg that is ~0.43 yd per ft (1 yd per
     2.3 ft), at a 5-wood's 47 deg ~0.31 yd/ft (1 yd per 3.2 ft -- the classic 1-to-1 rule is the steep
     iron/fairway-wood case). The integration also captures that a downhill ball keeps steepening
     (so a big drop gains a bit less than dh/tan) and an uphill ball meets the slope earlier at a
     shallower angle (so it loses a bit more). Uphill costs > downhill gains for the same |dh|.

2. Roll -- landing-area slope (along-line grade s, + = upslope). s is taken per club from the lateral-mean
   profile between its adjusted landing spot - 5 yds and the end of its run-out (>= 20 yds), so a
   driver that flies into the face of a rise (2B) is treated differently from a 4-wood that stops short;
   the cross grade comes from the 240-320 yd plane fit.
   Rolling with constant resistance: deceleration g*(MU + s) -> roll = v^2 / (2 g (MU + s)), so the
   roll scales by MU / (MU + s) (Penner, "The physics of golf", Rep. Prog. Phys. 66 (2003) 131, the
   rolling-ball model used for putting and run-out; MU from the stimpmeter relation
   MU = v0^2 / (2 g * stimp) with v0 = 1.83 m/s: fairway stimp ~4 ft -> MU ~0.14, so MU = 0.15).
   The first bounce: an upslope raises the impact angle relative to the surface (theta + alpha), so
   less forward speed survives the bounce (Penner's effective-angle rigid bounce; Haake 1991);
   modelled as (cos(theta+alpha)/cos(theta))^2 on the run-out energy. Upslope landings kill roll,
   downslope landings add it. roll_factor is clipped to [0.25, 3.0] (steeper downhill than MU runs
   to the bottom of the slope).

3. Lateral kick -- cross grade c = cross_pct/100 (+ = ground rises to the golfer's right)
   During the run-out the side slope accelerates the ball sideways at g*c while it decelerates at
   g*(MU+s), so it drifts lateral = roll * c / (MU + s) toward the low side (capped at 0.6 * roll,
   since the path bends down the fall line). Sign: + = kicks right.

The model's club tuple is (carry, total, width, depth). Apply: carry += carry_delta_yds,
total += carry_delta_yds + (total - carry) * (roll_factor - 1); or keep the tuple and put
extra_roll_yds (driver-based) into the hole's 'extra_roll' key, aim offset by -lateral_kick_yds.
"""
import functools
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HOLES_JSON = os.path.join(HERE, "spirit_hollow_holes.json")

YD, FT = 0.9144, 0.3048
G = 9.81
RHO = 1.194              # kg/m^3, ~200 m elevation, 15 C (Burlington IA is ~180-210 m)
M, R = 0.04593, 0.02134  # ball mass (kg), radius (m)
AREA = math.pi * R * R
# fitted to the TrackMan PGA Tour averages (see module docstring)
CD0, CD1, CL0, CL1, TAU = 0.137, 0.860, 0.0469, 1.114, 36.9
MU = 0.15                # fairway rolling resistance (stimp ~4 ft)

# The strategy model's clubs (mozingo/tee_strategy.CLUBS / IRONS): (carry, total, width, depth),
# with TrackMan-tour-like launch (deg) and spin (rpm); ball speed is solved per club for the carry.
CLUBS = {
    "Driver": dict(carry=275, total=300, launch=10.9, spin=2686),
    "2-wood": dict(carry=265, total=280, launch=10.0, spin=3200),
    "4-wood": dict(carry=255, total=270, launch=9.3, spin=3900),
    "Long iron": dict(carry=210, total=220, launch=11.0, spin=4836),
    "Mid iron": dict(carry=185, total=192, launch=14.1, spin=6231),
}


def _trajectory(v_mps, launch_deg, rpm, dt=0.005):
    """Yield (x m, y m, vx, vy) along the flight until the ball is well below the tee."""
    vx = v_mps * math.cos(math.radians(launch_deg))
    vy = v_mps * math.sin(math.radians(launch_deg))
    x = y = t = 0.0
    w0 = rpm * 2 * math.pi / 60
    while y > -60.0:
        V = math.hypot(vx, vy)
        S = w0 * math.exp(-t / TAU) * R / V
        cd, cl = CD0 + CD1 * S, CL0 + CL1 * S
        k = 0.5 * RHO * AREA / M * V
        ax = -k * (cd * vx + cl * vy)
        ay = -k * (cd * vy - cl * vx) - G
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        yield x, y, vx, vy


def fly(v_mps, launch_deg, rpm, ground=None):
    """Carry (yd) and descent angle (deg) where the ball comes down through `ground`.

    ground(x_yd) -> height in metres relative to the tee (None = flat at tee height)."""
    g = ground or (lambda xd: 0.0)
    prev = None
    for x, y, vx, vy in _trajectory(v_mps, launch_deg, rpm):
        h = y - g(x / YD)
        if prev is not None and vy < 0 and h <= 0 < prev[2]:
            f = prev[2] / (prev[2] - h)
            xc = prev[0] + f * (x - prev[0])
            return xc / YD, math.degrees(math.atan2(-vy, vx))
        prev = (x, y, h)
    return x / YD, math.degrees(math.atan2(-vy, vx))


@functools.lru_cache(maxsize=None)
def ball_speed_for(carry_yd, launch_deg, rpm):
    """Ball speed (m/s) that gives this flat carry (bisection)."""
    lo, hi = 30.0, 110.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if fly(mid, launch_deg, rpm)[0] < carry_yd:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def carry_on_profile(club, ground):
    c = CLUBS[club]
    v = ball_speed_for(c["carry"], c["launch"], c["spin"])
    return fly(v, c["launch"], c["spin"], ground)


def descent_angle(club):
    c = CLUBS[club]
    return fly(ball_speed_for(c["carry"], c["launch"], c["spin"]), c["launch"], c["spin"])[1]


def carry_delta_for_drop(club, drop_ft):
    """Carry change (yd) for a landing area uniformly `drop_ft` below (+) / above (-) the tee."""
    dh = -drop_ft * FT
    return carry_on_profile(club, lambda xd: dh if xd > 100 else dh * xd / 100.0)[0] - CLUBS[club]["carry"]


def roll_factor(along_pct, land_angle_deg=38.0, mu=MU):
    s = along_pct / 100.0
    alpha = math.atan(s)
    th = math.radians(land_angle_deg)
    bounce = (math.cos(min(th + alpha, math.radians(89))) / math.cos(th)) ** 2
    rf = (mu / (mu + s) if mu + s > 1e-6 else 99.0) * bounce
    return max(0.25, min(3.0, rf))


def lateral_kick(roll_yd, along_pct, cross_pct, mu=MU):
    """Side drift (yd, + = right) during the run-out on a cross slope (+cross = rises to the right)."""
    den = max(mu + along_pct / 100.0, 0.03)
    k = -roll_yd * (cross_pct / 100.0) / den
    cap = 0.6 * abs(roll_yd)
    return max(-cap, min(cap, k))


@functools.lru_cache(maxsize=None)
def _holes():
    return json.load(open(HOLES_JSON))["holes"]


def profile_fn(hole):
    """Lateral-mean ground (+-10 yds) along the tee line, metres relative to the tee."""
    P = [(p["yd"], p["band_ft_rel_tee"] * FT) for p in hole["profile"]]

    def g(xd):
        if xd <= P[0][0]:
            return P[0][1]
        for (a, za), (b, zb) in zip(P, P[1:]):
            if xd <= b:
                return za + (zb - za) * (xd - a) / (b - a)
        return P[-1][1]
    return g


def adjustments(hole_key, holes=None):
    """Per-club elevation adjustments for one hole (keys as in spirit_hollow/course.py: 1, '2B', ...).

    Returns dict(clubs={club: dict(carry_delta_yds, roll_factor, roll_delta_yds, lateral_kick_yds,
    landing_drop_ft, descent_deg)}, extra_roll_yds (Driver), landing slope, ...). Par 3s return
    the tee->green drop and a 'plays_like_delta_yds' for the green distance instead of roll."""
    H = (holes or _holes())[str(hole_key)]
    g = profile_fn(H)
    out = dict(hole=str(hole_key), par=H["par"], bearing_deg_true=H["bearing_deg_true"], clubs={})
    if H["par"] == 3 or not H.get("landing_slope"):
        drop = -H["green"]["delta_ft"]
        dist = H["green"]["along_yd"]
        # plays-like: an iron shot to a green `drop` ft below lands that much later (steep ~50 deg)
        out.update(green_drop_ft=round(drop, 1), green_along_yd=dist,
                   plays_like_delta_yds=round(-drop * FT / math.tan(math.radians(50)) / YD, 1),
                   green_slope=H.get("green_slope"))
        return out
    sl = H["landing_slope"]
    out.update(landing_slope=dict(along_pct=sl["along_pct"], cross_pct=sl["cross_pct"],
                                  magnitude_pct=sl["magnitude_pct"],
                                  fall_line_deg_cw_from_line=sl["fall_line_deg_cw_from_line"]),
               landing_270_delta_ft=H["landing"]["270"]["delta_ft"])
    for club, c in CLUBS.items():
        carry, ang = carry_on_profile(club, g)
        dc = carry - c["carry"]
        roll = c["total"] - c["carry"]
        # along grade where this club actually lands and runs: carry-5 .. carry+roll (>= 20 yds)
        span = max(roll, 20.0)
        along = (g(carry + span) - g(carry - 5)) / ((span + 5) * YD) * 100
        rf = roll_factor(along, ang)
        new_roll = roll * rf
        out["clubs"][club] = dict(
            carry_delta_yds=round(dc, 1), roll_factor=round(rf, 2),
            roll_delta_yds=round(new_roll - roll, 1),
            total_delta_yds=round(dc + new_roll - roll, 1),
            lateral_kick_yds=round(lateral_kick(new_roll, along, sl["cross_pct"]), 1),
            local_along_pct=round(along, 1),
            landing_drop_ft=round(-g(carry) / FT, 1), descent_deg=round(ang, 1))
    d = out["clubs"]["Driver"]
    out["extra_roll_yds"] = d["roll_delta_yds"]
    out["roll_factor"] = d["roll_factor"]
    out["lateral_kick_per_pct_side_slope_yds"] = round(-(CLUBS["Driver"]["total"] - CLUBS["Driver"]["carry"])
                                                      * d["roll_factor"] / 100 / max(MU + d["local_along_pct"] / 100, 0.03), 2)
    return out


def apply_to_club(tup, adj):
    """(carry, total, width, depth) + one club's adjustment -> adjusted tuple."""
    carry, total, width, depth = tup
    roll = total - carry
    nc = carry + adj["carry_delta_yds"]
    return (round(nc, 1), round(nc + roll * adj["roll_factor"], 1), width, depth)


if __name__ == "__main__":
    for k in _holes():
        a = adjustments(k)
        if "clubs" in a and a["clubs"]:
            c = a["clubs"]
            print(f"{k:>3}  drop270 {-a['landing_270_delta_ft']:+6.1f} ft  "
                  + "  ".join(f"{n[:6]} {c[n]['carry_delta_yds']:+5.1f}" for n in ("Driver", "2-wood", "4-wood"))
                  + f"  roll x{a['roll_factor']:.2f} ({a['extra_roll_yds']:+.0f} yd)  kick {c['Driver']['lateral_kick_yds']:+.1f}")
        else:
            print(f"{k:>3}  par 3: green drop {a['green_drop_ft']:+.1f} ft  plays {a['plays_like_delta_yds']:+.1f} yd")
