"""Validation of the reference model against published numbers, launch-assumption sensitivity, gust scatter.
`python3 validate.py` -> results/validate.json (PHYSICS.md section 7)."""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refmodel as R                    # noqa: E402
import will as WL                       # noqa: E402

out = {}
# ---- 1. published checks, Tour launch conditions, sea level 77 F unless stated
rho, nu = R.air(77.0, 0.0)
DRV, I6 = (167, 10.9, 2686), (127, 14.1, 6231)


def carry(v, la, sp, model="fit", **kw):
    a = dict(rho=rho, nu=nu, model=model)
    a.update(kw)
    return R.fly(v, la, sp, **a)["carry"]


pub = {}
for m in ("fit", "linear", "smits"):
    d = {}
    c6 = carry(*I6, model=m)
    d["6-iron 20 mph head / tail, uniform (TrackMan -39 / +23)"] = [
        round(carry(*I6, model=m, wind=R.Wind(20, 0, False)) - c6, 1), round(carry(*I6, model=m, wind=R.Wind(-20, 0, False)) - c6, 1)]
    cd_ = carry(*DRV, model=m)
    d["driver 10 mph head / tail, uniform (published -12..-18 / +9..+11)"] = [
        round(carry(*DRV, model=m, wind=R.Wind(10, 0, False)) - cd_, 1), round(carry(*DRV, model=m, wind=R.Wind(-10, 0, False)) - cd_, 1)]
    d["driver 20 mph head / tail, uniform (Golf.com tour 300: -41 / +33)"] = [
        round(carry(*DRV, model=m, wind=R.Wind(20, 0, False)) - cd_, 1), round(carry(*DRV, model=m, wind=R.Wind(-20, 0, False)) - cd_, 1)]
    r40, n40 = R.air(40.0, 0.0)
    r100, n100 = R.air(100.0, 0.0)
    d["driver 40 F -> 100 F (TrackMan +9; Rice ~+12)"] = round(carry(*DRV, model=m, rho=r100, nu=n100) - carry(*DRV, model=m, rho=r40, nu=n40), 1)
    d["6-iron 40 F -> 100 F (TrackMan ~+8)"] = round(carry(*I6, model=m, rho=r100, nu=n100) - carry(*I6, model=m, rho=r40, nu=n40), 1)
    rd, nd = R.air(77.0, 5280.0)
    d["driver at 5280 ft, % (Titleist +6.1 %)"] = round(100 * (carry(*DRV, model=m, rho=rd, nu=nd) / cd_ - 1), 1)
    d["6-iron at 5280 ft, %"] = round(100 * (carry(*I6, model=m, rho=rd, nu=nd) / c6 - 1), 1)
    x = R.fly(*DRV, rho=rho, nu=nu, model=m, wind=R.Wind(0, 10, False))
    d["driver 10 mph crosswind drift, uniform, yds (rules of thumb 10-15 on a 250 drive)"] = round(abs(x["right"]), 1)
    t = R.fly(*DRV, rho=rho, nu=nu, model=m)
    d["driver lag-time formula w (T - R / v0x), yds"] = round(4.4704 * (t["time"] - t["carry"] * R.YD / (167 * R.MPH * math.cos(math.radians(10.9)))) / R.YD, 1)
    x6 = R.fly(*I6, rho=rho, nu=nu, model=m, wind=R.Wind(0, 10, False))
    d["6-iron 10 mph crosswind drift, uniform, yds"] = round(abs(x6["right"]), 1)
    # ball speed -> carry
    d["driver yds per mph of ball speed"] = round(carry(168, 10.9, 2686, model=m) - cd_, 2)
    d["6-iron yds per mph of ball speed"] = round(carry(128, 14.1, 6231, model=m) - c6, 2)
    pub[m] = d
out["published"] = pub

# ---- 2. launch-assumption sensitivity for Will's driver and mid iron (fit model): the corrections under other launches
sens = {}
for club, variants in (("Driver", [(11.5, 2550), (13.5, 2200), (10.0, 2900), (12.5, 2400)]),
                       ("Mid iron", [(14.3, 6200), (16.0, 5400), (13.0, 6800)])):
    rows = []
    for la, sp in variants:
        kw = dict(launch=la, spin=sp)
        b = WL.shot(club, **kw)
        rows.append(dict(launch=la, spin=sp, ball_mph=round(WL.speed(club, "fit", la, sp)[0], 1), land=round(b["land_deg"], 1),
                         time=round(b["time"], 2),
                         air45=round(WL.shot(club, 45.0, **kw)["carry"] - b["carry"], 1),
                         air_ball45=round(WL.shot(club, 45.0, ball_f=45.0, **kw)["carry"] - b["carry"], 1),
                         head10=round(WL.shot(club, head=10, **kw)["carry"] - b["carry"], 1),
                         tail10=round(WL.shot(club, head=-10, **kw)["carry"] - b["carry"], 1),
                         drift10=round(abs(WL.shot(club, cross=10, **kw)["right"]), 1),
                         drop10=round(WL.shot(club, drop_ft=10, **kw)["carry"] - b["carry"], 1)))
    sens[club] = rows
out["launch_sensitivity"] = sens

# ---- 3. spin axis x crosswind: does a fade / draw ride or fight the wind differently? (drift relative to the calm curve)
ax = {}
for club in ("Driver", "Mid iron"):
    rows = {}
    for a in (-4.0, 0.0, 4.0):
        calm = WL.shot(club, axis=a)["right"]
        rows[str(a)] = dict(calm_curve=round(calm, 1),
                            wind_from_right_10=round(WL.shot(club, cross=10, axis=a)["right"] - calm, 1),
                            wind_from_left_10=round(WL.shot(club, cross=-10, axis=a)["right"] - calm, 1))
    ax[club] = rows
out["spin_axis_crosswind"] = ax

# ---- 4. gusts: turbulence felt by one flight. Along-wind turbulence sigma_u ~ 2.4 u* (neutral surface layer), u* =
# 0.4 u10 / ln(10 / z0); the forecast gust is a 3-s peak ~ mean + 3 sigma_u (peak factor 2.5-3.5). The ball averages
# the gust field over its ~6.5 s flight and ~200 m path: with an integral length scale L ~ 100 m at 20-30 m height
# the variance of the flight-average is sigma^2 x 2 (L/D)(1 - (L/D)(1 - exp(-D/L))) for an exponential correlation.


def flight_avg_factor(D=230.0, L=100.0):
    r = L / D
    return math.sqrt(2 * r * (1 - r * (1 - math.exp(-1 / r))))


g = {}
for z0 in (0.03, 0.1):
    ustar_ratio = 0.4 / math.log(10 / z0)
    g[f"sigma_u / u10, z0 {z0}"] = round(2.4 * ustar_ratio, 3)
    g[f"3-s gust / mean, z0 {z0}"] = round(1 + 3 * 2.4 * ustar_ratio, 2)
g["flight-average factor (L 100 m)"] = round(flight_avg_factor(), 2)
g["flight-average factor (L 50 m)"] = round(flight_avg_factor(L=50.0), 2)
cases = {}
for lab, mean, gust in (("Sat forecast 4.5 g 8", 4.5, 8.0), ("Sun forecast 3.5 g 6", 3.5, 6.0), ("10 g 17", 10.0, 17.0), ("15 g 25", 15.0, 25.0)):
    sig = (gust - mean) / 3.0
    eff = sig * flight_avg_factor()
    row = dict(sigma_point_mph=round(sig, 2), sigma_flight_mph=round(eff, 2))
    for club, sl, sc in (("Driver", 70 / 4.0, 28 * 1.25 / 4), ("Mid iron", 36.6 / 4, 18 * 1.25 / 4)):
        b = WL.shot(club)
        dh = (WL.shot(club, head=mean + 1)["carry"] - WL.shot(club, head=mean - 1)["carry"]) / 2      # yds per mph, into
        dx = abs(WL.shot(club, cross=5)["right"]) / 5.0
        row[club] = dict(carry_yds_per_mph=round(abs(dh), 2), drift_yds_per_mph=round(dx, 2),
                         swing_sigma_lat=round(sl, 1), swing_sigma_carry=round(sc, 1),
                         lat_sigma_into_wind=round(math.hypot(sl, dx * 0.8 * eff), 2),
                         lat_sigma_cross_wind=round(math.hypot(sl, dx * eff), 2),
                         carry_sigma_into_wind=round(math.hypot(sc, abs(dh) * eff), 2),
                         engine_rule_lat_cross=round(math.hypot(sl, dx * sig), 2),
                         engine_rule_carry_into=round(math.hypot(sc, abs(dh) * sig), 2))
    cases[lab] = row
g["cases"] = cases
out["gusts"] = g

# ---- 5. how fast a ball cools: lumped conduction, sphere r = 21.3 mm, rubber k ~ 0.25 W/m/K, rho c ~ 1.9e6 J/m3/K,
# surface h ~ 12 (still air, in the hand / on a tee) to 30 W/m2/K (4-5 mph breeze, or lying on cold wet turf)
cool = {}
for h in (12.0, 30.0):
    r, k, rc = 0.0213, 0.25, 1.9e6
    Bi = h * r / k
    # first eigenvalue of the sphere: 1 - z cot z = Bi
    z = 1.0
    for _ in range(200):
        f = 1 - z / math.tan(z) - Bi
        df = -1 / math.tan(z) + z / math.sin(z) ** 2
        z = min(max(z - f / df, 0.05), 3.1)
    tau = r * r * rc / (k * z * z)
    cool[f"h {h:.0f} W/m2K"] = dict(biot=round(Bi, 2), tau_min=round(tau / 60, 1),
                                    core_mean_fraction_left_after_14_min=round(math.exp(-14 * 60 / tau), 2),
                                    after_4_min=round(math.exp(-4 * 60 / tau), 2))
out["ball_cooling"] = cool

json.dump(out, open(os.path.join(HERE, "results", "validate.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
