"""Wind (and temperature) adjustments for the tee-shot club tuples.

A club in mozingo/tee_strategy.py is ``(carry, total, width, depth)``:
carry yds, total yds on a firm fairway, lateral 95% width (= 4 sigma, the
model treats lateral misses as normal with width = +-2 sigma) and the
carry-depth 95% window.  ``adjust`` turns that calm-air tuple into the tuple
for a given wind, plus ``drift``: the crosswind shift of the mean lateral
landing point (yds, + = right of the aim line).

Conventions
-----------
``rel_dir_deg`` is the direction the wind blows FROM, measured clockwise from
the target line:  0 = straight into the face (headwind), 90 = from the right
(pushes the ball left), 180 = tailwind, 270 = from the left.  Components:

    head  = speed * cos(rel)      (> 0 headwind, < 0 tailwind)
    cross = speed * sin(rel)      (> 0 from the right -> drift left, i.e. < 0)

``hole_relative(wind_from_true, hole_bearing_true)`` gives ``rel_dir_deg``
from a forecast direction (degrees true, FROM) and the tee->target bearing.

Wind speeds are the *reported* (10 m anemometer) speed, which is how every
rule of thumb below is quoted.  A driver apex is ~30 m, where wind over open
ground is ~15-25% stronger (power law, alpha ~0.14), but the ball spends the
first and last ~1.5 s below 10 m, so the trajectory-averaged wind is within a
few % of the 10 m value (our trajectory check below changed by <3% between
a uniform wind and alpha = 0.14).  Tree-lined holes sit in sheltered air:
pass ``exposure`` < 1 (e.g. 0.6-0.8) for those.

Physics and sources (P = published number, I = our inference/derivation)
------------------------------------------------------------------------
Drag ~ (airspeed)^2, so a headwind costs more than an equal tailwind gains,
and the asymmetry grows with speed; a tailwind also reduces Magnus lift, so
the ball falls out of the sky sooner (Tutelman, via Golf.com "How wind
affects drives"; GolfWRX "How the wind affects your golf ball").

Carry, as a fraction of calm carry (h = headwind mph, t = tailwind mph):

    head: -(0.0045 h + 0.00010 h^2)      10 mph -> -5.5%  (~-15 yd on 275)
                                          20 mph -> -13.0% (~-36 yd)
    tail: +(0.0040 t - 0.00001 t^2)      10 mph -> +3.9%  (~+11 yd)
                                          20 mph -> +7.6%  (~+21 yd)

  P  Frank Thomas (Golf Channel / Golf.com): 250-yd drive, 10 mph head -13 yd
     (-5.2%), tail +9 yd (+3.6%).
  P  Foresight Sports sim (via Golf.com): driver -12 yd into 10 mph, +9 down.
  P  Golf Australia fitting test (2020): 10 mph headwind -16.5 m (~18 yd)
     driver carry; tailwind never gained as much as the headwind cost.
  P  Golf.com tour example: 300 carry -> 259 into 20 mph (-13.7%), 333 with
     20 mph down (+11%).
  P  TrackMan 6-iron (Golf Performance Center): 20 mph head -39 yd, tail +23.
  P  Rule of thumb (Colorado Avid Golfer, TrackMan-derived tables): 1% per
     mph headwind, 0.5% per mph tailwind (playing yardage, mostly irons; it
     over-states the driver headwind loss at 10 mph).
  I  Our 3-D point-mass trajectory (Bearman & Harvey-type C_D, C_L vs spin
     ratio, 171 mph ball speed, 11.5 deg, 2600 rpm, calibrated to 275 carry):
     10 mph head -12.8 yd, tail +10.5; 20 mph head -27.8, tail +19.1.
  The coefficients sit in the middle of the published driver numbers.

Roll (total - carry).  Into the wind the ball lands steeper and slower, down
wind shallower and faster (P: GolfWRX/Stickney TrackMan test - wind does not
change launch or spin, but headwinds give steep landings and tailwinds
shallow ones; long-drive tailwind landings near 100 mph vs 65-70 mph calm).
  I  Trajectory check: landing angle 27 deg calm, 32 (10 head) / 38 (20 head),
     24 (10 tail) / 21 (20 tail); horizontal landing speed ratio
     ~1 - 0.0155 h (head) and ~1 + 0.015 t - 0.00004 t^2 (tail).
  I  Roll on a firm fairway taken ~ (horizontal landing speed)^1.5:
     10 mph head ~0.78x roll, 10 mph tail ~1.23x roll.

Lateral width.  Wind does not change the spin axis (P: TrackMan "Spin
axis"; Ping testing), but a headwind raises airspeed and therefore the
tilted lift that makes the hook/slice, so curvature and lateral dispersion
grow into the wind and shrink down wind.
  P  Ping testing (Golf.com): horizontal dispersion +7% per 10 mph headwind;
     front-to-back dispersion shrinks slightly.
  I  Trajectory check with a 5 deg spin-axis tilt: curvature +7.4% at 10 mph
     head, -8% at 10 mph tail (matches Ping).
  =>  width x (1 + 0.007 h)  into the wind;  x (1 - 0.006 t)  down wind
      (floored at 0.85).
  Depth: x (1 - 0.003 h) into the wind (Ping: "shrinks slightly"),
         x (1 + 0.004 t) down wind (I: tailwind flight is less damped).

Crosswind drift of the mean.
  I  Trajectory check: 275-yd carry drifts ~1.14 yd per mph of pure
     crosswind (10 mph -> 11.4 yd); scales ~carry^1.5 (carry x hang time).
  P  Hole19: ~5 yd per 10 mph for a mid-iron (our formula: ~6 yd at 185 yd).
  P  GolfClubAtlas forum: 2-3 deg aim correction for a 10-kt crosswind.
  Drift is applied to the carry; a few yards more accrue on the roll-out but
  are ignored.  Curvature riding/fighting the wind is not modelled.

Gusts (optional ``gust_mph``).  A forecast gust is a ~3-s peak; with a peak
factor of ~3 the turbulent std is sigma_w ~ (gust - mean)/3 (I, standard
boundary-layer meteorology).  Each shot samples one realisation, so the
along-line component adds to the depth window and the across-line component
(lateral turbulence ~0.8 sigma_w) adds to the lateral width, in quadrature
with the swing's own dispersion.

Temperature (``temperature_adjust``).
  P  Titleist: ~1.5% distance per 20 F  -> 0.75% per 10 F (~2 yd on 275).
  P  Andrew Rice / TrackMan (2018): driver ~2 yd carry per 10 F at 155 mph
     ball speed; humidity almost no effect.
  =>  carry and total x (1 + 0.00075 (T - 70)).
"""
import math

# Club sensitivity multipliers on the carry/roll/drift effects (I: higher
# spin/apex clubs are moved more by the same wind - Golf Australia: 10 mph
# headwind cost 16.5 m with driver but 15.8 m with a much shorter 7-iron).
SENSITIVITY = {"Driver": 1.0, "2-wood": 1.0, "4-wood": 1.05,
               "Long iron": 1.15, "Mid iron": 1.25}

HEAD_LIN, HEAD_QUAD = 0.0045, 0.00010
TAIL_LIN, TAIL_QUAD = 0.0040, 0.00001
DRIFT_PER_MPH_275 = 1.14     # yds of drift per crosswind mph at 275 carry
WIDTH_HEAD, WIDTH_TAIL, WIDTH_FLOOR = 0.007, 0.006, 0.85
DEPTH_HEAD, DEPTH_TAIL = 0.003, 0.004
TEMP_PER_F, TEMP_BASE_F = 0.00075, 70.0
MAX_WIND = 40.0


def components(speed_mph, rel_dir_deg):
    """(head, cross) mph; head > 0 into the face, cross > 0 blowing from the right."""
    r = math.radians(rel_dir_deg)
    head = speed_mph * math.cos(r)
    cross = speed_mph * math.sin(r)
    return (0.0 if abs(head) < 1e-9 else head), (0.0 if abs(cross) < 1e-9 else cross)


def hole_relative(wind_from_deg_true, hole_bearing_deg_true):
    """rel_dir_deg in [0, 360) for a wind FROM ``wind_from_deg_true`` on a hole
    played toward ``hole_bearing_deg_true`` (both degrees true).
    E.g. wind from 180 (south) on a hole played due south (180) -> 0 (headwind);
    on a hole played north (0) -> 180 (tailwind); played east (90) -> 90
    (from the right)."""
    return (wind_from_deg_true - hole_bearing_deg_true) % 360.0


def carry_factor(head_mph, sens=1.0):
    """Multiplicative carry factor for a signed head component (mph)."""
    h = min(abs(head_mph), MAX_WIND)
    if head_mph >= 0:
        return 1.0 - sens * (HEAD_LIN * h + HEAD_QUAD * h * h)
    return 1.0 + sens * (TAIL_LIN * h - TAIL_QUAD * h * h)


def roll_factor(head_mph, sens=1.0):
    """Multiplicative factor on roll (total - carry)."""
    h = min(abs(head_mph), MAX_WIND) * sens
    v = 1.0 - 0.0155 * h if head_mph >= 0 else 1.0 + 0.015 * h - 0.00004 * h * h
    return max(v, 0.2) ** 1.5


def drift_per_mph(carry):
    return DRIFT_PER_MPH_275 * (max(carry, 0.0) / 275.0) ** 1.5


def adjust(club_tuple, speed_mph, rel_dir_deg, club_name=None, gust_mph=None, exposure=1.0):
    """Wind-adjusted ``(carry, total, width, depth, drift_yds)``.

    club_tuple : (carry, total, width, depth) in calm air.
    speed_mph  : reported (10 m) mean wind; scaled by ``exposure`` (1 = open).
    rel_dir_deg: wind FROM direction relative to the target line
                 (0 head, 90 from the right, 180 tail).
    club_name  : key of SENSITIVITY (default 1.0).
    gust_mph   : optional forecast gust; adds turbulent dispersion.
    drift_yds  : mean lateral shift, + = right.
    """
    carry, total, width, depth = club_tuple[:4]
    sens = SENSITIVITY.get(club_name, 1.0)
    speed = max(speed_mph, 0.0) * exposure
    head, cross = components(speed, rel_dir_deg)

    new_carry = carry * carry_factor(head, sens)
    new_roll = max(total - carry, 0.0) * roll_factor(head, sens)
    new_total = new_carry + new_roll

    dpm = drift_per_mph(new_carry) * sens
    drift = -dpm * cross + 0.0   # avoid -0.0

    h = abs(head)
    if head >= 0:
        wf, df = 1.0 + WIDTH_HEAD * h, 1.0 - DEPTH_HEAD * h
    else:
        wf, df = max(1.0 - WIDTH_TAIL * h, WIDTH_FLOOR), 1.0 + DEPTH_TAIL * h
    new_width, new_depth = width * wf, depth * df

    if gust_mph is not None and gust_mph * exposure > speed:
        sig_w = (gust_mph * exposure - speed) / 3.0
        r = math.radians(rel_dir_deg)
        # along-wind turbulence sigma_w, transverse ~0.8 sigma_w, projected
        sig_head = math.hypot(sig_w * math.cos(r), 0.8 * sig_w * math.sin(r))
        sig_cross = math.hypot(sig_w * math.sin(r), 0.8 * sig_w * math.cos(r))
        eps = 1.0
        dcarry = abs(carry * (carry_factor(head + eps, sens) - carry_factor(head - eps, sens)) / (2 * eps))
        new_width = math.hypot(new_width, 4.0 * dpm * sig_cross)
        new_depth = math.hypot(new_depth, 4.0 * dcarry * sig_head)

    return (new_carry, new_total, new_width, new_depth, drift)


def temperature_adjust(club_tuple, temp_f, base_f=TEMP_BASE_F):
    """Scale carry and total for air temperature (Titleist ~0.75%/10 F,
    TrackMan/Rice ~2 yd/10 F for driver).  Keeps any extra tuple fields."""
    f = 1.0 + TEMP_PER_F * (temp_f - base_f)
    carry, total = club_tuple[0] * f, club_tuple[1] * f
    return (carry, total) + tuple(club_tuple[2:])


def adjust_clubs(clubs, speed_mph, rel_dir_deg, gust_mph=None, temp_f=None, exposure=1.0):
    """Apply ``adjust`` (and optionally ``temperature_adjust``) to a dict of clubs."""
    out = {}
    for name, tup in clubs.items():
        if temp_f is not None:
            tup = temperature_adjust(tup, temp_f)
        out[name] = adjust(tup, speed_mph, rel_dir_deg, name, gust_mph=gust_mph, exposure=exposure)
    return out
