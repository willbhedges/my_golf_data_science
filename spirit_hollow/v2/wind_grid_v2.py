"""v2 wind grid: best club + aim per wind cell with the v2 engine at the v2 central world.

  TEE_BACK=0 WIND_HOLES=1,2F WIND_OUT=parts/w.json python3 spirit_hollow/v2/wind_grid_v2.py

Same cells and output layout as spirit_hollow/wind_grid.py (so the page template reads it), with
the v2 differences: soft-course roll, 48 F, all five clubs on every hole, aims optimised to 0.5 yd
(Brent on the smoothed curve) and the stored 'zone' is the 0.005-stroke aim window (v1: 0.02).
Wind effects (carry, roll, width, depth, drift) come from spirit_hollow/wind.py as in v1.
Stored carry/total are WITHOUT the DEM elevation change (the page adds it, as for v1).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
sys.path[:0] = [HERE, SH]

import model as M                               # noqa: E402
import decide as D                              # noqa: E402
import wind as W                                # noqa: E402
import wind_grid as WG                          # noqa: E402  (v1: bearings, par-3 plays-like, tee shift)

SPEEDS = WG.SPEEDS
DIRS = WG.DIRS
N = int(os.environ.get("WIND_SWINGS", 4000))
TEMPS = [float(x) for x in os.environ.get("WIND_TEMPS", "35,45,55,65").split(",")]
W.SENSITIVITY.setdefault(M.HYBRID, 1.1)          # between the 4-wood (1.05) and long iron (1.15)
AIMS = np.arange(-75, 75.001, 0.5)      # wide enough for aim = landing line - crosswind drift


def wind_hook(club, speed, rel):
    def f(carry, roll, sig_lat, sig_car):
        c2, t2, w2, d2, drift = W.adjust((carry, carry + roll, 4 * sig_lat, 4 * sig_car), speed, rel, club_name=club)
        return c2, max(t2 - c2, 0.0), w2 / 4, d2 / 4, drift
    return f


def solve(h, P, R, S, z, speed, rel):
    hd = M.HOLES[h]
    res = {}
    for c in M.ALL_CLUBS:
        hook = wind_hook(c, speed, rel) if speed else None
        ev, _ = M.ev_curve(R, S, hd, c, P, z, AIMS, wind=hook)
        dr = hook(*M.club_numbers(hd, c, P))[4] if hook else 0.0
        # the checked-map limit applies to where the ball is aimed to LAND (aim + drift), not the aim
        r = D.robust_aim(AIMS, ev, lo=-D.AIM_LIMIT - dr, hi=D.AIM_LIMIT - dr)
        # page numbers: calm club (temperature, carry offsets) with wind, no elevation
        base = dict(P)
        carry0, total0, width0, depth0 = M.CLUBS[c]
        carry = carry0 * (1.0 - P["temp_k"] * (70.0 - P["temp_f"]))
        roll = P["soft_roll"] if P.get("soft_roll") is not None else (total0 - carry0) * P["roll_mult"]
        tup = (carry, carry + roll, P["width"][c], depth0 * P["depth_mult"])
        c2, t2, w2, d2, drift = W.adjust(tup, speed, rel, club_name=c) if speed else tup + (0.0,)
        del base
        res[c] = dict(aim=r["aim"], ev=r["ev"], zone=r["window"], carry=float(c2), total=float(t2),
                      width=float(w2), drift=float(drift), at_bound=r["at_bound"])
    real = [c for c in res if c not in M.HYPOTHETICAL]
    best = min(real, key=lambda c: res[c]["ev"])
    runner = min((c for c in real if c != best), key=lambda c: res[c]["ev"])
    return dict(pick=best, margin=res[runner]["ev"] - res[best]["ev"], runner=runner, clubs=res)


def main():
    import geom
    geom.set_geometry(os.environ.get("V2_GEOM", "scale,elev,green"))   # before any tee shift
    back = float(os.environ.get("TEE_BACK", 0) or 0)
    if back:
        WG.shift_tees(back)                      # moves course.HOLES (= M.HOLES) tees in place
    bearings = WG.osm_bearings()
    z = M.draws_z(N, 31)
    only = [x.strip() for x in os.environ.get("WIND_HOLES", "").split(",") if x.strip()]
    out = dict(speeds=SPEEDS, dirs=DIRS, temps=TEMPS, bearings={}, holes={}, par3={}, tee_back=back, model="v2")
    for h in M.HOLES:
        if only and str(h) not in only:
            continue
        hd = M.HOLES[h]
        out["bearings"][str(h)] = (hd.get("elev_info") or {}).get("bearing") or bearings[WG.ref(h)]
        R = M.Raster(hd)
        byT = {}
        for T in TEMPS:
            P = M.central(temp_f=T)
            S = R.strokes(P, hd["length"])
            grid = {}
            for sp in SPEEDS:
                for rel in ([0] if sp == 0 else DIRS):
                    grid[f"{sp}_{rel}"] = solve(h, P, R, S, z, sp, rel)
            byT[f"{T:g}"] = grid
            print(h, T, "done", grid["0_0"]["pick"], grid["0_0"]["clubs"][grid["0_0"]["pick"]]["aim"], flush=True)
        out["holes"][str(h)] = byT
    import course
    for h, p in course.PAR3.items():
        out["bearings"][str(h)] = p.get("bearing") or bearings[WG.ref(h)]
        dz = p.get("plays_like_delta", 0.0)
        out["par3"][str(h)] = {f"{sp}_{rel}": WG.plays_like(p["center"], sp, rel) + dz
                               for sp in SPEEDS for rel in ([0] if sp == 0 else DIRS)}
    path = os.environ.get("WIND_OUT") or os.path.join(
        HERE, "output", "wind_grid.json" if not back else f"wind_grid_back{back:+.0f}.json")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(dict(out, back=back), f)
    print("wrote", path)


if __name__ == "__main__":
    main()
