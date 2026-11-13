"""Will's clubs on the reference model: launch conditions calibrated to his 70 F calm carries at Gateway (410 ft),
then the sensitivities (temperature, wind, elevation, roll). `python3 will.py` writes results/reference.json.

Launch angle / spin are Tour-like values for the carry (TrackMan Tour averages; the woods are teed, so a little
higher launch / lower spin than off the deck); the ball speed is SOLVED so the carry is Will's number. What matters
for the corrections is the sensitivity, and the three aero sets and the launch variants below bracket it.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refmodel as R                    # noqa: E402

ALT_FT = 410.0
# club: (70 F carry, stated total or None, launch deg, spin rpm)
CLUBS = {
    "Driver": (275, 300, 11.5, 2550),
    "2-wood": (265, 280, 11.0, 3000),
    "4-wood": (255, 270, 10.5, 3500),
    "Hybrid ~235 (not in bag)": (235, 248, 11.0, 4200),
    "Long iron": (210, 220, 11.5, 4700),
    "5-iron": (198, None, 12.5, 5300),
    "Mid iron": (185, 192, 14.3, 6200),
    "7-iron": (174, None, 16.3, 7000),
    "8-iron": (162, 167, 18.2, 7900),
    "9-iron": (150, None, 20.5, 8600),
    "PW": (138, None, 24.0, 9300),
    "GW": (126, None, 26.5, 9800),
}
TEE = ["Driver", "2-wood", "4-wood", "Long iron", "Mid iron", "8-iron"]
RHO70, NU70 = R.air(70.0, ALT_FT)
_cache = {}


def speed(club, model="fit", launch=None, spin=None):
    c, _, la, sp = CLUBS[club]
    la, sp = launch or la, spin or sp
    k = (club, model, la, sp)
    if k not in _cache:
        _cache[k] = R.solve_speed(c, la, sp, RHO70, NU70, model)
    return _cache[k], la, sp


def shot(club, temp_f=70.0, head=0.0, cross=0.0, drop_ft=0.0, model="fit", profile=True, z0=0.03, ball_f=None,
         axis=0.0, rh=0.5, slp=1013.25, launch=None, spin=None, ball_k=None):
    """Fly one of Will's clubs. ball_f: ball (and face) temperature, default 70 (a warm ball); ball_k: ball-speed
    loss per F below 70 (BALL_K)."""
    v, la, sp = speed(club, model, launch, spin)
    if ball_f is not None:
        v *= 1.0 - (BALL_K if ball_k is None else ball_k) * (70.0 - ball_f)
    rho, nu = R.air(temp_f, ALT_FT, rh, slp)
    w = R.Wind(head, cross, profile, z0) if (head or cross) else R.CALM
    return R.fly(v, la, sp, axis_deg=axis, rho=rho, nu=nu, wind=w, drop_ft=drop_ft, model=model)


# Ball speed lost per F of BALL temperature below 70 F (resilience of the core / cover; the club face matters far
# less). Published: Titleist ("a 40 F ball vs 80 F loses ~1.5 % of its speed" class statements: 0.0004 / F);
# Golf Laboratories robot / MyGolfSpy and TrackMan-Rice ball-in-freezer tests give 2-5 mph on ~165 mph between ~35 F
# and ~80 F balls (0.0003-0.0007 / F); Cochran & Stobbs (1968) 1.5 %/10 F is for wound balls (not used).
BALL_K, BALL_K_LO, BALL_K_HI = 0.0004, 0.0002, 0.0007


def tables(model="fit"):
    out = dict(model=model, clubs={})
    for c in CLUBS:
        v, la, sp = speed(c, model)
        b = shot(c, model=model)
        d = dict(ball_mph=round(v, 1), launch=la, spin=sp, carry=round(b["carry"], 1), apex_yds=round(b["apex"], 1),
                 apex_m=round(b["apex"] * R.YD, 1), land_deg=round(b["land_deg"], 1), time=round(b["time"], 2),
                 v_land_mph=round(b["v_land"], 1), spin_land=round(b["spin_land"]))
        # temperature: air only (warm ball), and air + cold ball
        d["temp_air"] = {str(T): round(shot(c, T, model=model)["carry"] - b["carry"], 2) for T in (35, 40, 45, 50, 55, 60, 65)}
        d["temp_air_ball"] = {str(T): round(shot(c, T, ball_f=T, model=model)["carry"] - b["carry"], 2)
                              for T in (35, 40, 45, 50, 55, 60, 65)}
        d["k_air_per_F"] = round(-d["temp_air"]["45"] / 25.0 / b["carry"], 6)
        d["k_air_ball_per_F"] = round(-d["temp_air_ball"]["45"] / 25.0 / b["carry"], 6)
        # wind at 70 F: head / tail / cross, log profile (z0 0.03) vs uniform
        for nm, kw in (("wind_log", dict(profile=True)), ("wind_uniform", dict(profile=False))):
            w = {}
            for s in (5, 10, 15, 20):
                h = shot(c, head=s, model=model, **kw)
                t = shot(c, head=-s, model=model, **kw)
                x = shot(c, cross=s, model=model, **kw)
                w[str(s)] = dict(head=round(h["carry"] - b["carry"], 1), tail=round(t["carry"] - b["carry"], 1),
                                 drift=round(abs(x["right"]), 1), cross_carry=round(x["carry"] - b["carry"], 1),
                                 head_land=round(h["land_deg"], 1), tail_land=round(t["land_deg"], 1),
                                 head_vh=round(h["vh"], 1), tail_vh=round(t["vh"], 1))
            d[nm] = w
        # elevation: landing 10 ft below / above
        d["elev"] = {str(dz): round(shot(c, drop_ft=dz, model=model)["carry"] - b["carry"], 2) for dz in (-10, -5, 5, 10)}
        d["yd_per_ft_geom"] = round(R.FT / math.tan(math.radians(b["land_deg"])) / R.YD, 3)
        out["clubs"][c] = d
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    res = {m: tables(m) for m in ("fit", "fit_re", "linear", "smits")}
    json.dump(res, open(os.path.join(HERE, "results", "reference.json"), "w"), indent=1)
    for m, t in res.items():
        print("==", m)
        for c, d in t["clubs"].items():
            print(f"{c[:10]:10s} {d['ball_mph']:6.1f} mph {d['launch']:4.1f} deg {d['spin']:5d} rpm | apex {d['apex_yds']:4.1f} "
                  f"land {d['land_deg']:4.1f} t {d['time']:4.2f} vland {d['v_land_mph']:4.1f} spin {d['spin_land']:5d} | "
                  f"45F air {d['temp_air']['45']:+5.1f} +ball {d['temp_air_ball']['45']:+5.1f} | 10 mph: head "
                  f"{d['wind_log']['10']['head']:+5.1f} tail {d['wind_log']['10']['tail']:+5.1f} drift "
                  f"{d['wind_log']['10']['drift']:4.1f} (uniform {d['wind_uniform']['10']['head']:+5.1f} "
                  f"{d['wind_uniform']['10']['tail']:+5.1f} {d['wind_uniform']['10']['drift']:4.1f}) | +10 ft drop "
                  f"{d['elev']['10']:+4.1f} up {d['elev']['-10']:+4.1f}")
