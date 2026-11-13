"""Engine vs reference model, club by club and at the Gateway forecast. `python3 compare.py` -> results/compare.json
and the markdown tables printed to stdout (pasted into ../PHYSICS.md).

Engine side: the functions the page is built from, called unchanged (spirit_hollow/wind.py adjust / carry_factor /
drift_per_mph, spirit_hollow/v2/model.py club_numbers / central / hole_temp, spirit_hollow/wind_grid.plays_like,
course_data/courses/v2_course.activate for Gateway's bearings, DEM adjustments and forecast).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "course_data", "courses")]
import refmodel as R                    # noqa: E402
import will as WL                       # noqa: E402
import v2_course as V                   # noqa: E402

course, meta, M, D = V.activate("gateway_national", "truth")
import wind as W                        # noqa: E402
import wind_grid as WG                  # noqa: E402

FC = V.forecast("gateway_national")["hourly"]
# Open-Meteo fetched 2026-11-13 02:27Z with pressure / humidity (the page's forecast file has neither); also the newer
# temperatures and winds, listed in PHYSICS.md section 6 (the comparison itself uses the page's Nov 12 forecast rows)
_OM = json.load(open(os.path.join(HERE, "results", "open_meteo_1113_0227Z.json")))["hourly"]
OM = {(t[:10], int(t[11:13])): {k: _OM[k][i] for k in _OM if k != "time"} for i, t in enumerate(_OM["time"])}
SLP_REF = 1015.0          # a typical sea-level pressure for the days Will's stock numbers were hit on
DAYS = [("Sat", "2026-11-14"), ("Sun", "2026-11-15")]
TEE_HOUR, MIN_PER_HOLE = 9.0, 14.0
TEE = ["Driver", "2-wood", "4-wood", "Long iron", "Mid iron", "8-iron"]
MODELS = ("fit", "linear", "smits")


def at(day, hole):
    """Forecast at the time you reach `hole` (the page's forecastAtTime: wind interpolated as a vector)."""
    t = TEE_HOUR + (int(hole) - 1) * MIN_PER_HOLE / 60.0
    rows = {r["hour"]: r for r in FC if r["date"] == day}
    h0 = int(math.floor(t))
    a, b = rows[h0], rows.get(h0 + 1, rows[h0])
    w = t - h0

    def vec(r):
        d = math.radians(r["wind_from_deg"])
        return r["wind_mph"] * math.sin(d), r["wind_mph"] * math.cos(d)
    (ax, ay), (bx, by) = vec(a), vec(b)
    x, y = ax + (bx - ax) * w, ay + (by - ay) * w
    o0, o1 = OM[(day, h0)], OM.get((day, h0 + 1), OM[(day, h0)])
    om = {k: o0[k] + (o1[k] - o0[k]) * w for k in ("pressure_msl", "relative_humidity_2m", "temperature_2m", "wind_speed_10m")}
    temp = a["temp_f"] + (b["temp_f"] - a["temp_f"]) * w
    slp, rh = om["pressure_msl"], om["relative_humidity_2m"] / 100.0
    # the temperature at standard pressure / 50 % RH that has the same air density as the forecast air
    rho = R.air(temp, WL.ALT_FT, rh, slp)[0]
    lo, hi = temp - 40.0, temp + 10.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if R.air(mid, WL.ALT_FT, 0.5, SLP_REF)[0] > rho:
            lo = mid
        else:
            hi = mid
    return dict(t=t, mph=math.hypot(x, y), dir=math.degrees(math.atan2(x, y)) % 360,
                gust=a["gust_mph"] + (b["gust_mph"] - a["gust_mph"]) * w, temp=temp, slp=slp, rh=rh,
                temp_eff=0.5 * (lo + hi), rho=rho, temp_new=om["temperature_2m"], mph_new=om["wind_speed_10m"])


# ------------------------------------------------------------------------------------------------ proposed patch
# The corrections of PHYSICS.md section 5 as values of the engine's own knobs (nothing is written to the engine here:
# they are swapped in for the "patched" columns and swapped back).
PATCH = dict(
    SENSITIVITY={"Driver": 1.0, "2-wood": 1.2, "4-wood": 1.3, "Hybrid ~235 (not in bag)": 1.4, "Long iron": 1.5,
                 "Mid iron": 1.65, "8-iron": 2.0},
    DRIFT_PER_MPH_275=1.5,
    temp_k_cold_ball=0.00115,        # 0.00075 (air) + 0.0004 (ball at air temperature)
)


class patched:
    def __enter__(self):
        self.s, self.d = dict(W.SENSITIVITY), W.DRIFT_PER_MPH_275
        W.SENSITIVITY.update(PATCH["SENSITIVITY"])
        W.DRIFT_PER_MPH_275 = PATCH["DRIFT_PER_MPH_275"]

    def __exit__(self, *a):
        W.SENSITIVITY.clear()
        W.SENSITIVITY.update(self.s)
        W.DRIFT_PER_MPH_275 = self.d


# ------------------------------------------------------------------------------------------------ turf calibration
def calibrate_turf():
    """Crater-tilt scale of the 'normal' fairway so the Driver runs Will's 25 yds at 70 F calm."""
    b = WL.shot("Driver")
    lo, hi = 0.5, 2.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if R.run_out(b["vh"], b["vz"], b["spin_land"], dict(R.TURF["fairway_normal"], firm=mid)) > 25.0:
            lo = mid
        else:
            hi = mid
    f = 0.5 * (lo + hi)
    R.TURF["fairway_normal"]["firm"] = f
    R.TURF["fairway_firm"]["firm"] = f * 0.85
    R.TURF["fairway_soft"]["firm"] = f * 1.2
    return f


FIRM = calibrate_turf()


def roll(b, turf="fairway_normal"):
    return R.run_out(b["vh"], b["vz"], b["spin_land"], turf)


# ------------------------------------------------------------------------------------------------ generic tables
def generic():
    out = {}
    P = M.central()
    for c in TEE:
        carry, total, width, depth = M.CLUBS[c]
        e = dict(carry=carry, total=total)
        r = {}
        b0 = WL.shot(c)
        r["calm70"] = dict(carry=b0["carry"], roll=roll(b0), land=b0["land_deg"], time=b0["time"], apex=b0["apex"],
                           ball_mph=WL.speed(c)[0], v_land=b0["v_land"], spin_land=b0["spin_land"])
        # temperature
        e["temp"], r["temp"] = {}, {}
        for T in (35, 40, 45, 50, 55, 60):
            e["temp"][T] = carry * (1 - P["temp_k"] * (70 - T)) - carry
            ba, bb = WL.shot(c, T), WL.shot(c, T, ball_f=T)
            r["temp"][T] = dict(air={m: WL.shot(c, T, model=m)["carry"] - carry for m in MODELS},
                                air_ball=bb["carry"] - carry,
                                ball_lo=WL.shot(c, T, ball_f=T, ball_k=WL.BALL_K_LO)["carry"] - carry,
                                ball_hi=WL.shot(c, T, ball_f=T, ball_k=WL.BALL_K_HI)["carry"] - carry,
                                roll_air=roll(ba), roll_air_ball=roll(bb))
        # wind (70 F)
        e["wind"], r["wind"] = {}, {}
        for s in (5, 10, 15):
            eh = W.adjust((carry, total, width, depth), s, 0, c)
            et = W.adjust((carry, total, width, depth), s, 180, c)
            ex = W.adjust((carry, total, width, depth), s, 90, c)
            e["wind"][s] = dict(head=eh[0] - carry, tail=et[0] - carry, drift=abs(ex[4]), head_roll=eh[1] - eh[0],
                                tail_roll=et[1] - et[0], head_width=eh[2] / width, tail_width=et[2] / width)
            rr = {}
            for m in MODELS:
                h, t, x = WL.shot(c, head=s, model=m), WL.shot(c, head=-s, model=m), WL.shot(c, cross=s, model=m)
                rr[m] = dict(head=h["carry"] - carry, tail=t["carry"] - carry, drift=abs(x["right"]))
            h, t = WL.shot(c, head=s), WL.shot(c, head=-s)
            hu, tu, xu = WL.shot(c, head=s, profile=False), WL.shot(c, head=-s, profile=False), WL.shot(c, cross=s, profile=False)
            hr, xr = WL.shot(c, head=s, z0=0.1), WL.shot(c, cross=s, z0=0.1)
            # curvature: a 3-deg fade axis, calm vs head / tail (lateral dispersion scaling)
            f0 = WL.shot(c, axis=3.0)["right"]
            rr.update(head_roll=roll(h), tail_roll=roll(t), head_land=h["land_deg"], tail_land=t["land_deg"],
                      uniform=dict(head=hu["carry"] - carry, tail=tu["carry"] - carry, drift=abs(xu["right"])),
                      z0_10cm=dict(head=hr["carry"] - carry, drift=abs(xr["right"])),
                      curve_head=WL.shot(c, head=s, axis=3.0)["right"] / f0, curve_tail=WL.shot(c, head=-s, axis=3.0)["right"] / f0)
            r["wind"][s] = rr
        # elevation
        e["elev"] = {}
        r["elev"] = {dz: WL.shot(c, drop_ft=dz)["carry"] - carry for dz in (-10, -5, 5, 10)}
        # turf
        r["turf"] = {t: roll(b0, t) for t in ("fairway_firm", "fairway_normal", "fairway_soft")}
        r["turf45"] = {t: roll(WL.shot(c, 45.0, ball_f=45.0), t) for t in ("fairway_firm", "fairway_normal", "fairway_soft")}
        out[c] = dict(engine=e, ref=r)
    return out


# ------------------------------------------------------------------------------------------------ par 3s
IRONS = ["GW", "PW", "9-iron", "8-iron", "7-iron", "Mid iron", "5-iron", "Long iron"]


def ideal(carry70):
    """Launch conditions of an 'ideal club' with this 70 F carry (launch / spin interpolated between Will's irons)."""
    xs = [WL.CLUBS[c][0] for c in IRONS]
    la = _interp(carry70, xs, [WL.CLUBS[c][2] for c in IRONS])
    sp = _interp(carry70, xs, [WL.CLUBS[c][3] for c in IRONS])
    return R.solve_speed(carry70, la, sp, WL.RHO70, WL.NU70), la, sp


def _interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    for (a, ya), (b, yb) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x <= b:
            return ya + (yb - ya) * (x - a) / (b - a)
    return ys[-1]


def ref_shot(carry70, temp, head, cross, drop_ft, ball_f=None, profile=True, rh=0.5, slp=SLP_REF):
    v, la, sp = ideal(carry70)
    if ball_f is not None:
        v *= 1.0 - WL.BALL_K * (70.0 - ball_f)
    rho, nu = R.air(temp, WL.ALT_FT, rh, slp)
    return R.fly(v, la, sp, rho=rho, nu=nu, wind=R.Wind(head, cross, profile), drop_ft=drop_ft)


def ref_plays_like(target, temp, head, cross, drop_ft, ball_f=None, **air):
    """The 70 F calm flat-ground stock carry whose shot lands `target` yds out in these conditions (secant)."""
    c0, c1 = target, target + 10.0
    f0 = ref_shot(c0, temp, head, cross, drop_ft, ball_f, **air)["carry"] - target
    for _ in range(6):
        f1 = ref_shot(c1, temp, head, cross, drop_ft, ball_f, **air)["carry"] - target
        if abs(f1) < 0.02 or f1 == f0:
            break
        c0, c1, f0 = c1, c1 - f1 * (c1 - c0) / (f1 - f0), f1
    b = ref_shot(c1, temp, head, cross, drop_ft, ball_f, **air)
    return c1, b


def page_plays_like(A, mph, rel, dz, temp, tk):
    """The template's solvePar3 on the stored 5-mph x 30-deg grid (bilinear), x temperature."""
    S = WG.SPEEDS
    mph = min(mph, S[-1])
    i = 0
    while i < len(S) - 2 and mph > S[i + 1]:
        i += 1
    s0, s1 = S[i], S[i + 1]
    ws = (mph - s0) / (s1 - s0)
    d0 = math.floor(rel / 30) * 30
    d1, wd = (d0 + 30) % 360, (rel - d0) / 30

    def g(sp, dd):
        return (WG.plays_like(A, 0, 0) if sp == 0 else WG.plays_like(A, sp, dd)) + dz
    plays = (1 - ws) * ((1 - wd) * g(s0, d0) + wd * g(s0, d1)) + ws * ((1 - wd) * g(s1, d0) + wd * g(s1, d1))
    return plays / (1 - tk * (70 - temp)), plays


def par3s():
    T = json.load(open(os.path.join(ROOT, "course_data", "courses", "gateway_national", "par3_targets.json")))
    tk = float(M.central()["temp_k"])
    yards = meta["holes"]
    out = {}
    for h in sorted(course.PAR3):
        p = course.PAR3[h]
        card = yards[str(h)]["yards"]["Back"]
        aim = T["sets"]["Back"][str(h)]["boxes"]["-1"]["aim"]
        A = card + aim[1]
        dz, drop = p.get("plays_like_delta", 0.0), p.get("green_drop_ft", 0.0)
        row = dict(card=card, aim_depth=aim[1], A=A, dz=dz, drop_ft=drop, bearing=p["bearing"], days={})
        for lab, day in DAYS:
            f = at(day, h)
            rel = W.hole_relative(f["dir"], p["bearing"])
            head, cross = W.components(f["mph"], rel)
            page, plays = page_plays_like(A, f["mph"], rel, dz, f["temp"], tk)
            e_drift = W.adjust((A, A + 5, 30, 15), f["mph"], rel, club_name="Mid iron")[4]
            with patched():
                pw, _ = page_plays_like(A, f["mph"], rel, dz, f["temp"], tk)
                pc, _ = page_plays_like(A, f["mph"], rel, dz, f["temp"], PATCH["temp_k_cold_ball"])
                # ball at air temperature: the ball term uses the real temperature, the air term the effective one
                pp = pc + (page_plays_like(A, f["mph"], rel, dz, f["temp_eff"], tk)[0] - pw)
                p_drift = W.adjust((A, A + 5, 30, 15), f["mph"], rel, club_name="Mid iron")[4]
            air = dict(rh=f["rh"], slp=f["slp"])
            full, bf = ref_plays_like(A, f["temp"], head, cross, drop, ball_f=f["temp"], **air)
            warm, bw = ref_plays_like(A, f["temp"], head, cross, drop)
            cold, bc = ref_plays_like(A, f["temp"], head, cross, drop, ball_f=f["temp"])
            # the parts, reference: elevation only, wind only, temperature only
            el = ref_plays_like(A, 70.0, 0, 0, drop)[0] - A
            wi = ref_plays_like(A, 70.0, head, cross, 0.0)[0] - A
            ta = ref_plays_like(A, f["temp"], 0, 0, 0.0)[0] - A
            tb = ref_plays_like(A, f["temp"], 0, 0, 0.0, ball_f=f["temp"])[0] - A
            row["days"][lab] = dict(time=f["t"], temp=f["temp"], mph=f["mph"], gust=f["gust"], wind_from=f["dir"], rel=rel,
                                    head=head, cross=cross,
                                    page=page, page_parts=dict(elev=dz, wind=plays - dz - A, temp=page - plays),
                                    page_drift=e_drift, patched_warm=pw, patched_cold=pc, patched_cold_pressure=pp,
                                    patched_drift=p_drift, ref_cold_pressure=full, slp=f["slp"], rh=f["rh"],
                                    temp_eff=f["temp_eff"], temp_new=f["temp_new"], mph_new=f["mph_new"],
                                    ref_warm=warm, ref_cold=cold,
                                    ref_parts=dict(elev=el, wind=wi, temp_air=ta, temp_air_ball=tb),
                                    ref_drift=bc["right"], land_deg=bc["land_deg"], v_land=bc["v_land"],
                                    spin_land=bc["spin_land"], time_flight=bc["time"],
                                    green_roll={g: R.run_out(bc["vh"], bc["vz"], bc["spin_land"], g)
                                                for g in ("green_firm", "green_normal", "green_soft")})
        out[str(h)] = row
    return out


# ------------------------------------------------------------------------------------------------ tee shots
def tee_shots():
    out = {}
    for h in sorted(course.HOLES):
        hd = course.HOLES[h]
        drops = (meta["holes"].get(str(h), {}).get("clubs") or {})
        row = dict(bearing=course.BEARINGS[h], days={})
        for lab, day in DAYS:
            f = at(day, h)
            rel = W.hole_relative(f["dir"], course.BEARINGS[h])
            head, cross = W.components(f["mph"], rel)
            P = M.central(temp_f=f["temp"])
            clubs = {}
            for c in TEE:
                carry, rl, sl, sc = M.club_numbers(hd, c, P)
                c2, t2, w2, d2, drift = W.adjust((carry, carry + rl, 4 * sl, 4 * sc), f["mph"], rel, club_name=c)
                with patched():
                    Pc = M.central(temp_f=f["temp"], temp_k=PATCH["temp_k_cold_ball"])
                    ww = W.adjust((carry, carry + rl, 4 * sl, 4 * sc), f["mph"], rel, club_name=c)
                    ca, ra, sa, sca = M.club_numbers(hd, c, Pc)
                    wc = W.adjust((ca, ca + ra, 4 * sa, 4 * sca), f["mph"], rel, club_name=c)
                    # + pressure: the air term at the effective temperature (ball term at the real one)
                    kb = PATCH["temp_k_cold_ball"] - P["temp_k"]
                    fac = (1 - P["temp_k"] * (70 - f["temp_eff"]) - kb * (70 - f["temp"])) / (1 - PATCH["temp_k_cold_ball"] * (70 - f["temp"]))
                    wp = W.adjust((ca * fac, ca * fac + ra, 4 * sa, 4 * sca), f["mph"], rel, club_name=c)
                bp = WL.shot(c, f["temp"], head, cross, drop_ft=(drops.get(c) or {}).get("drop", 0.0), ball_f=f["temp"],
                             rh=f["rh"], slp=f["slp"])
                dc, rf = hd["elev"][c][0], hd["elev"][c][1]
                drop = (drops.get(c) or {}).get("drop", 0.0)
                bw = WL.shot(c, f["temp"], head, cross, drop_ft=drop)
                bc = WL.shot(c, f["temp"], head, cross, drop_ft=drop, ball_f=f["temp"])
                # reference total = reference carry + the ENGINE's roll (the bounce model is too turf-sensitive to
                # correct a total with: section 4)
                clubs[c] = dict(engine=dict(carry=c2, total=t2, drift=drift, width=w2, dc=dc, rf=rf),
                                patched_warm=dict(carry=ww[0], total=ww[1], drift=ww[4]),
                                patched_cold=dict(carry=wc[0], total=wc[1], drift=wc[4]),
                                patched_cold_pressure=dict(carry=wp[0], total=wp[1], drift=wp[4]),
                                ref_cold_pressure=dict(carry=bp["carry"], total=bp["carry"] + t2 - c2, drift=bp["right"]),
                                ref_warm=dict(carry=bw["carry"], total=bw["carry"] + t2 - c2, drift=bw["right"]),
                                ref_cold=dict(carry=bc["carry"], total=bc["carry"] + t2 - c2, drift=bc["right"]),
                                drop_ft=drop)
            row["days"][lab] = dict(temp=f["temp"], mph=f["mph"], gust=f["gust"], wind_from=f["dir"], head=head,
                                    cross=cross, slp=f["slp"], temp_eff=f["temp_eff"], temp_new=f["temp_new"],
                                    mph_new=f["mph_new"], clubs=clubs)
        out[str(h)] = row
    return out


if __name__ == "__main__":
    res = dict(firm_calibrated=FIRM, patch=PATCH, generic=generic(), par3=par3s(), tee=tee_shots())
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "compare.json"), "w"), indent=1)
    print("turf tilt scale (driver rolls 25):", round(FIRM, 3))
