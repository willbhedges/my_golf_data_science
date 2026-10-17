"""Pre-compute the best club and aim for every wind on every hole (feeds the interactive page).

  python3 spirit_hollow/wind_grid.py     -> output/wind_grid.json

For each tee hole, each wind speed (0, 5, 10, 15, 20, 25 mph) and each direction the wind blows
FROM relative to the hole (every 30 deg; 0 = straight into you), the clubs are adjusted with
spirit_hollow/wind.py (carry, roll, dispersion width and depth, crosswind drift) and the strategy
model finds the best aim per club. Drift is applied to where the ball goes, so the stored aim is
where you aim. Settings are the prior means of the final Bayesian run (driver width 70 yds, tree
penalty 0.8, half of long-grass balls lost, 15% slight mishits, carry depth x1.25). Elevation
(DEM) is applied inside tee_strategy.simulate via each hole's 'elev' table.

Par 3s get the DECADE wind modifier (+1 yd per edge at 10-20 mph, +2 at 20-30, -1 under 5)
and a plays-like distance.
"""
import copy
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [os.path.join(ROOT, "mozingo"), HERE]

import course                                  # noqa: E402
import tee_strategy as t                       # noqa: E402
import wind as W                               # noqa: E402

t.HOLES = course.HOLES
SPEEDS = [0, 5, 10, 15, 20, 25]
DIRS = list(range(0, 360, 30))
N = 4000
AIMS = np.arange(-30, 30.01, 2.5)
ZONE_TOL = 0.02
BASE_CLUBS = copy.deepcopy(t.CLUBS)
BASE_IRONS = copy.deepcopy(t.IRONS)


def osm_bearings():
    d = json.load(open(os.path.join(ROOT, "course_data", "spirit_hollow", "holes_osm.json")))["holes"]

    def brg(a, b):
        lon1, lat1 = map(math.radians, a)
        lon2, lat2 = map(math.radians, b)
        y = math.sin(lon2 - lon1) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        return (math.degrees(math.atan2(y, x)) + 360) % 360
    return {int(k): brg(h["tee_ll"], h["aim_ll"]) for k, h in d.items()}


def elevation_adjust():
    try:
        sys.path.insert(0, os.path.join(ROOT, "course_data", "elevation"))
        import adjust as E
        return E
    except Exception:
        return None


def ref(k):
    return int(k) if isinstance(k, int) else int(str(k)[:-1])


def set_prior_means():
    s = 70.0 / 65.0
    t.CLUBS = {k: (c, tot, w * s, d * 1.25) for k, (c, tot, w, d) in BASE_CLUBS.items()}
    t.IRONS = {k: (c, tot, w * s, d * 1.25) for k, (c, tot, w, d) in BASE_IRONS.items()}
    t.TREE_SEVERITY, t.NATIVE_LOST = 0.8, 0.5
    t.MISHIT_RATE = {k: 0.15 for k in t.MISHIT_RATE}


def clubs_for(h):
    return list(BASE_CLUBS) + (list(BASE_IRONS) if course.HOLES[h].get("irons") else [])


def solve(h, speed, rel, z, elev):
    calm = {**t.CLUBS, **t.IRONS}
    res = {}
    for c in clubs_for(h):
        carry, total, width, depth, drift = W.adjust(calm[c], speed, rel, club_name=c)
        table = t.IRONS if c in t.IRONS else t.CLUBS
        saved = table[c]
        table[c] = (carry, total, width, depth)
        aims = AIMS if c not in t.IRONS else np.arange(-30, 45.01, 2.5)
        ev = np.array([t.simulate(h, c, a + drift, z=z)[3].mean() for a in aims])
        table[c] = saved
        i = int(ev.argmin())
        ok = aims[ev <= ev[i] + ZONE_TOL]
        res[c] = dict(aim=float(aims[i]), ev=float(ev[i]), zone=[float(ok.min()), float(ok.max())],
                      carry=float(carry), total=float(total), width=float(width), drift=float(drift))
    best = min(res, key=lambda c: res[c]["ev"])
    runner = min((c for c in res if c != best), key=lambda c: res[c]["ev"])
    return dict(pick=best, margin=res[runner]["ev"] - res[best]["ev"], runner=runner, clubs=res)


def plays_like(dist, speed, rel):
    """Par-3 plays-like yardage: distance scaled by how much a mid-iron's carry changes."""
    carry = W.adjust((dist, dist + 5, 30, 15), speed, rel, club_name="Mid iron")[0]
    return dist * dist / carry


def shift_tees(back):
    """Move every tee-shot tee `back` yds straight back along its line (negative = forward), the
    way most tee sets differ. Zones stay where they are on the ground; length grows by `back`."""
    for h, hd in course.HOLES.items():
        tee, d = np.array(hd["tee"], float), np.array(hd["dot270"], float)
        f = (d - tee) / np.linalg.norm(d - tee)
        ppy = np.linalg.norm(d - tee) / 270
        hd["tee"] = tuple(tee - f * back * ppy)
        hd["dot270"] = tuple(np.array(hd["tee"]) + f * 270 * ppy)
        hd["length"] = hd["length"] + back
        # elevation per club was measured from the original tee; keep it (small vs a 20-yd move)


def main():
    back = float(os.environ.get("TEE_BACK", 0) or 0)
    if back:
        shift_tees(back)
    set_prior_means()
    bearings = osm_bearings()
    E = elevation_adjust()
    rng = np.random.default_rng(31)
    z = np.vstack([rng.standard_normal((2, N)), rng.random((2, N))])
    only = [x.strip() for x in os.environ.get("WIND_HOLES", "").split(",") if x.strip()]
    path = os.path.join(HERE, "output", "wind_grid.json" if not back else f"wind_grid_back{back:+.0f}.json")
    out = dict(speeds=SPEEDS, dirs=DIRS, bearings={}, holes={}, par3={}, tee_back=back)
    if only and os.path.exists(path):                      # update just those tee holes
        out = json.load(open(path))
    for h in course.HOLES:
        if only and str(h) not in only:
            continue
        # elevation is applied inside tee_strategy.simulate via the hole's "elev" table
        b = (course.HOLES[h].get("elev_info") or {}).get("bearing") or bearings[ref(h)]
        out["bearings"][str(h)] = b
        elev = None
        grid = {}
        for sp in SPEEDS:
            for rel in ([0] if sp == 0 else DIRS):
                grid[f"{sp}_{rel}"] = solve(h, sp, rel, z, elev)
        out["holes"][str(h)] = grid
        print(h, "done", grid["0_0"]["pick"], flush=True)
    for h, p in course.PAR3.items():
        out["bearings"][str(h)] = p.get("bearing") or bearings[ref(h)]
        dz = p.get("plays_like_delta", 0.0)                      # elevation
        out["par3"][str(h)] = {f"{sp}_{rel}": plays_like(p["center"], sp, rel) + dz
                               for sp in SPEEDS for rel in ([0] if sp == 0 else DIRS)}
    part = os.environ.get("WIND_OUT")               # Actions matrix: write just these holes
    if part:
        with open(part, "w") as f:
            json.dump(dict(back=back, holes={k: out["holes"][k] for k in out["holes"] if not only or k in only},
                           bearings=out["bearings"], par3=out["par3"]), f)
        return
    with open(path, "w") as f:
        json.dump(out, f)
    print("wrote wind_grid.json")


if __name__ == "__main__":
    main()
