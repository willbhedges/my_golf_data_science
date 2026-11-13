"""Fit the 'fit' aerodynamic coefficients of refmodel.py to the TrackMan Tour average tables.

    python3 fit_aero.py        -> aero_fit.json (params, residual table)

Data: TrackMan "PGA Tour averages" and "LPGA Tour averages" (ball speed mph, launch deg, spin rpm -> carry yds, max
height yds, landing angle deg). The tables are quoted from memory of the published sheets (the driver / 3-wood /
5-wood rows are the ones already cited in course_data/elevation/adjust.py); assumed air 77 F, sea level, 50 % RH
(TrackMan's normalisation). An error of a few yards in a row, or of ~2 % in the assumed density, moves the fitted
coefficients slightly but not the sensitivities, because Will's clubs are re-solved to HIS carries afterwards.
"""
import json
import os

import numpy as np
from scipy.optimize import least_squares

import refmodel as R

# club: (ball mph, launch deg, spin rpm, carry yds, apex yds, land deg)
PGA = {
    "Driver": (167, 10.9, 2686, 275, 32, 38), "3-wood": (158, 9.2, 3655, 243, 30, 43),
    "5-wood": (152, 9.4, 4350, 230, 31, 47), "Hybrid": (146, 10.2, 4437, 225, 29, 47),
    "3-iron": (142, 10.4, 4630, 212, 27, 46), "4-iron": (137, 11.0, 4836, 203, 28, 48),
    "5-iron": (132, 12.1, 5361, 194, 31, 49), "6-iron": (127, 14.1, 6231, 183, 30, 50),
    "7-iron": (120, 16.3, 7097, 172, 32, 50), "8-iron": (115, 18.1, 7998, 160, 31, 50),
    "9-iron": (109, 20.4, 8647, 148, 30, 51), "PW": (102, 24.2, 9304, 136, 29, 52),
}
LPGA = {
    "Driver": (140, 13.2, 2611, 218, 25, 37), "3-wood": (132, 11.2, 2704, 195, 23, 39),
    "5-wood": (128, 12.1, 4501, 185, 26, 43), "Hybrid": (123, 12.7, 4693, 174, 25, 43),
    "4-iron": (116, 14.3, 4801, 169, 24, 43), "5-iron": (112, 14.8, 5081, 161, 23, 45),
    "6-iron": (109, 17.1, 5943, 152, 25, 46), "7-iron": (104, 19.0, 6699, 141, 26, 47),
    "8-iron": (100, 20.8, 7494, 130, 25, 47), "9-iron": (93, 23.9, 7589, 119, 26, 47),
    "PW": (86, 25.6, 8403, 107, 23, 48),
}
RHO, NU = R.air(77.0, 0.0, 0.5)
KEYS = ["cd0", "cd1", "sd", "cl1", "sl"]


def resid(x, rows, weights=(1.0, 0.6, 0.5)):
    R.FIT.update(dict(zip(KEYS, x)))
    out = []
    for v, la, sp, c, ap, ld in rows:
        f = R.fly(v, la, sp, rho=RHO, nu=NU, dt=0.02)
        out += [(f["carry"] - c) * weights[0], (f["apex"] - ap) * weights[1], (f["land_deg"] - ld) * weights[2]]
    return np.array(out)


def main():
    rows = list(PGA.values()) + list(LPGA.values())
    x0 = [0.14, 0.25, 0.15, 0.35, 0.15]
    r = least_squares(resid, x0, args=(rows,), bounds=([0.02, 0, 0.01, 0.1, 0.01], [0.4, 2, 3, 1.5, 3]),
                      diff_step=1e-3)
    p = dict(zip(KEYS, [float(v) for v in r.x]))
    R.FIT.update(p)
    table = {}
    for name, D in (("PGA", PGA), ("LPGA", LPGA)):
        for c, (v, la, sp, cy, ap, ld) in D.items():
            f = R.fly(v, la, sp, rho=RHO, nu=NU)
            table[f"{name} {c}"] = dict(carry=round(f["carry"], 1), d_carry=round(f["carry"] - cy, 1),
                                        apex=round(f["apex"], 1), d_apex=round(f["apex"] - ap, 1),
                                        land=round(f["land_deg"], 1), d_land=round(f["land_deg"] - ld, 1),
                                        time=round(f["time"], 2))
    dc = np.array([t["d_carry"] for t in table.values()])
    da = np.array([t["d_apex"] for t in table.values()])
    dl = np.array([t["d_land"] for t in table.values()])
    a = R.fly(167, 10.9, 2686, rho=RHO, nu=NU)["carry"]
    b = R.fly(167, 10.9, 2686, rho=RHO * 0.95, nu=NU / 0.95)["carry"]
    print("driver density elasticity (altitude):", round((b / a - 1) / 0.05, 3), "(Titleist rule: 0.40)")
    out = dict(params=p, params_re=R.FIT_RE, driver_density_elasticity=round((b / a - 1) / 0.05, 3), rho=RHO, rms=dict(carry=float(np.sqrt((dc ** 2).mean())),
               apex=float(np.sqrt((da ** 2).mean())), land=float(np.sqrt((dl ** 2).mean()))), table=table)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "aero_fit.json"), "w"), indent=1)
    print(json.dumps(out["params"]), out["rms"])
    for k, t in table.items():
        print(f"{k:14s} carry {t['carry']:6.1f} ({t['d_carry']:+5.1f})  apex {t['apex']:5.1f} ({t['d_apex']:+5.1f})  "
              f"land {t['land']:5.1f} ({t['d_land']:+5.1f})  t {t['time']}")


if __name__ == "__main__":
    main()
